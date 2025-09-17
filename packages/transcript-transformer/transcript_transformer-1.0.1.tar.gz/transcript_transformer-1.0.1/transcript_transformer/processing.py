import numpy as np
from tqdm import tqdm
import h5py
import polars as pl
from scipy.stats import entropy
from scipy.sparse import csr_matrix
from transcript_transformer import (
    RIBOTIE_MQC_HEADER,
    START_CODON_MQC_HEADER,
    BIOTYPE_VARIANT_MQC_HEADER,
    ORF_TYPE_MQC_HEADER,
    ORF_TYPE_ORDER,
    IDX_PROT_DICT,
    IDX_DNA_DICT,
    STANDARD_HEADERS,
    RENAME_HEADERS,
    STANDARD_OUT_HEADERS,
    RIBO_OUT_HEADERS,
)
from .util_functions import (
    construct_prot,
    prtime,
    check_genomic_order,
    find_distant_exon_coord,
    transcript_region_to_exons,
    get_str2str_idx_map,
)


def eval_overlap(ORF_id, CDS_exon_start, CDS_exon_end, ORF_exon_start, ORF_exon_end):
    df = (
        pl.DataFrame(
            [ORF_id, CDS_exon_start, CDS_exon_end, ORF_exon_start, ORF_exon_end]
        )
        .with_columns(
            overlap=(pl.col("ORF_exon_start") - pl.col("ORF_exon_end")).abs()
            + 1
            - (pl.col("CDS_exon_start") - pl.col("ORF_exon_start")).clip(0)
            - (pl.col("ORF_exon_end") - pl.col("CDS_exon_end")).clip(0),
            ORF_exon_len=(pl.col("ORF_exon_end") - pl.col("ORF_exon_start")).abs() + 1,
        )
        .group_by("ORF_exon_start", "ORF_exon_end")
        .agg(pl.all().get(pl.col("overlap").arg_max()))
        .with_columns(
            ORF_coords_no_CDS=pl.when(
                (pl.col("overlap") > 0) & (pl.col("overlap") < pl.col("ORF_exon_len"))
            )
            .then(
                pl.concat_list(
                    pl.when(pl.col("ORF_exon_start") < pl.col("CDS_exon_start"))
                    .then(pl.col("ORF_exon_start"))
                    .otherwise(pl.col("CDS_exon_end")),
                    pl.when(pl.col("ORF_exon_start") < pl.col("CDS_exon_start"))
                    .then(pl.col("CDS_exon_start"))
                    .otherwise(pl.col("ORF_exon_end")),
                )
            )
            .otherwise(pl.lit([]))
        )
        .group_by("ORF_id")
        .agg(
            pl.col("overlap").sum(), pl.col("ORF_coords_no_CDS").flatten().drop_nulls()
        )
    )
    if len(df) > 0:
        non_CDS_coords = df[0, "ORF_coords_no_CDS"].to_list()
        overlap = df[0, "overlap"]
    else:
        non_CDS_coords = []
        overlap = 0
    return overlap, non_CDS_coords


def parse_ribo_data(df, f, h5_path, ribo_ids, parallel):
    df_ribo = df.select("ORF_id", "h5_idx", "TIS_idx", "TTS_idx", "ORF_len")
    # multiple sets in case of merged data sets
    sys_path = f"{h5_path.split('.h5')[0]}_{{sample}}.h5"
    db_path = "transcript/riboseq/{sample}/5/"
    ribo_paths = [
        [sys_path.format(sample=sample), db_path.format(sample=sample)]
        for sample in ribo_ids
    ]
    # only data and indices of sparse object are required (all counts are summed over read lengths)
    csr_cols = ["data", "indices", "indptr", "shape"]
    for h in csr_cols:
        if parallel:
            count_matrix = [
                np.array(h5py.File(a)[f"{p}/{h}"])[df_ribo["h5_idx"]]
                for a, p in ribo_paths
            ]
        else:
            count_matrix = [
                np.array(f[f"{p}/{h}"])[df_ribo["h5_idx"]] for _, p in ribo_paths
            ]
        if h in ["data", "indices"]:
            # concatenate the individual entries by keeping transcript position and value
            exp_iter = range(len(count_matrix))
            tr_iter = range(len(count_matrix[0]))
            counts = [
                np.concatenate([count_matrix[i][j] for i in exp_iter]) for j in tr_iter
            ]
            total_reads = [len(c) for c in counts]
        elif h == "indptr":
            # row values are not important (read length info is discarded), replace last value
            # of indptr with total reads (normally indicating all reads are in the last row)
            counts = count_matrix[0]
            counts[:, -1] = total_reads
        else:
            # shape is the same for all samples, just take the first one
            counts = count_matrix[0]
        df_ribo = df_ribo.with_columns(
            pl.Series(name=h, values=list(counts), dtype=pl.List(pl.Int32))
        )
    # Filter out results with 0 reads (only happens when training on zero-read data)
    df_ribo = df_ribo.filter(pl.col("data").cast(pl.List(pl.Int32)).list.len() > 0)
    # Polars autoconverts empty list columns to array types...
    df_ribo = df_ribo.cast({"data": pl.List(pl.Int32), "indices": pl.List(pl.Int32)})
    # get in-ORF reads and properties that cannot be retrieved using polars API
    csr_f = (
        lambda x: csr_matrix((x["data"], x["indices"], x["indptr"]), shape=x["shape"])
        .sum(axis=0)
        .tolist()[0]
    )
    df_ribo = df_ribo.with_columns(
        pl.struct(*csr_cols)
        .map_elements(
            csr_f,
            return_dtype=pl.List(pl.Int32),
        )
        .alias("reads")
    )
    # get ribo properties supported by polars API
    df_ribo = df_ribo.with_columns(
        reads_in_ORF=(pl.col("reads").list.slice(pl.col("TIS_idx"), pl.col("ORF_len"))),
        reads_in_transcript=pl.col("data").list.sum(),
    ).with_columns(
        reads_in_ORF=pl.col("reads_in_ORF").list.sum(),
        reads_in_frame_frac=(
            pl.col("reads_in_ORF")
            .list.gather_every(3)
            .list.sum()
            .truediv(pl.col("reads_in_ORF").list.sum())
        ),
        reads_5UTR=(pl.col("reads").list.slice(0, pl.col("TIS_idx")).list.sum()),
        reads_3UTR=(
            pl.when(pl.col("TTS_idx") != -1)
            .then(pl.col("reads").list.slice(pl.col("TTS_idx")).list.sum())
            .otherwise(pl.lit(0))
        ),
        reads_skew=(
            pl.col("reads_in_ORF")
            .list.slice(offset=pl.col("reads_in_ORF").list.len().truediv(2))
            .list.sum()
            .truediv(pl.col("reads_in_ORF").list.sum())
            .sub(0.5)
            .mul(2)
        ),
        reads_coverage_frac=(
            pl.col("reads_in_ORF")
            .list.eval((pl.element() > 0))
            .list.sum()
            .truediv(pl.col("reads_in_ORF").list.len())
        ),
        reads_entropy=(
            pl.col("reads_in_ORF").map_elements(
                lambda x: entropy(x, np.full(len(x), 1) / len(x)),
                return_dtype=pl.Float32,
            )
        ),
    )
    return df_ribo.fill_nan(0)


def parse_CDS_overlap(df, df_CDS):
    # detect CDS variant information
    df = df.with_columns(
        has_CDS_TIS=(pl.col("TIS_coord").is_in(df_CDS["canonical_TIS_coord"])),
        has_CDS_TTS=(pl.col("LTS_coord").is_in(df_CDS["canonical_LTS_coord"])),
    )
    sel_cols = [
        "ORF_id",
        "CDS_exon_start",
        "CDS_exon_end",
        "ORF_exon_start",
        "ORF_exon_end",
    ]
    var_feats = {
        "ORF_id": [],
        "shared_in_frame_CDS_region": [],
        "shared_in_frame_CDS_frac": [],
        "ORF_coords_no_CDS": [],
        "has_CDS_clones": [],
    }
    for r in df.iter_rows(named=True):
        var_feats["ORF_id"].append(r["ORF_id"])
        df_CDS_row = df_CDS.filter(
            pl.when(pl.col("strand") == "+")
            .then(
                (pl.col("CDS_start_range") < r["ORF_exon_end"][-1])
                & (pl.col("CDS_end_range") > r["ORF_exon_start"][0])
            )
            .otherwise(
                (pl.col("CDS_start_range") < r["ORF_exon_end"][0])
                & (pl.col("CDS_end_range") > r["ORF_exon_start"][-1])
            )
        )
        if len(df_CDS_row) > 0:
            df_CDS_row = df_CDS_row.with_columns(
                ORF_id=pl.lit(r["ORF_id"]),
                ORF_exon_start=pl.lit(r["ORF_exon_start"]),
                ORF_exon_end=pl.lit(r["ORF_exon_end"]),
                ORF_exon_len=pl.lit(r["ORF_exon_len"]),
            )
            has_CDS_clones = (
                (df_CDS_row["CDS_exon_start"] == df_CDS_row["ORF_exon_start"])
                & (df_CDS_row["CDS_exon_end"] == df_CDS_row["ORF_exon_end"])
            ).any()
            # ORF start is within CDS exon boundaries
            cond_1 = (pl.col("ORF_exon_start") >= pl.col("CDS_exon_start")) & (
                pl.col("ORF_exon_start") < pl.col("CDS_exon_end")
            )
            # ORF end is within CDS exon boundaries
            cond_2 = (pl.col("ORF_exon_end") > pl.col("CDS_exon_start")) & (
                pl.col("ORF_exon_end") <= pl.col("CDS_exon_end")
            )
            cond_3 = (
                pl.when(pl.col("strand") == "+")
                .then((pl.col("ORF_exon_start") - pl.col("CDS_exon_start")) % 3 == 0)
                .otherwise((pl.col("ORF_exon_end") - pl.col("CDS_exon_end")) % 3 == 0)
            )
            # filter specific exon regions if they're not overlapping with CDS exon regions
            df_CDS_exons = (
                df_CDS_row.explode(["CDS_exon_start", "CDS_exon_end"])
                .explode(["ORF_exon_start", "ORF_exon_end", "ORF_exon_len"])
                .with_columns(shared_in_frame_CDS_region=(cond_1 | cond_2) & cond_3)
                .filter(pl.col("shared_in_frame_CDS_region"))
            )
            out = eval_overlap(*[df_CDS_exons[c] for c in sel_cols])
            in_frame_CDSs = (
                df_CDS_exons.group_by("transcript_id")
                .agg(pl.col("shared_in_frame_CDS_region").any())
                .select("transcript_id")
                .to_series()
                .to_list()
            )
        else:
            has_CDS_clones = False
            out = [0, []]
            in_frame_CDSs = []
        var_feats["has_CDS_clones"].append(has_CDS_clones)
        var_feats["shared_in_frame_CDS_frac"].append(out[0])
        var_feats["ORF_coords_no_CDS"].append(out[1])
        var_feats["shared_in_frame_CDS_region"].append(in_frame_CDSs)
    df_var_feats = pl.DataFrame(
        var_feats,
        schema={
            "ORF_id": pl.String,
            "shared_in_frame_CDS_region": pl.List(pl.String),
            "shared_in_frame_CDS_frac": pl.Int64,
            "ORF_coords_no_CDS": pl.List(pl.Int64),
            "has_CDS_clones": pl.Boolean,
        },
    )
    df = df.join(df_var_feats, on="ORF_id")

    return df


def construct_output_table(
    h5_path,
    out_prefix,
    prob_cutoff=0.15,
    correction=False,
    dist=9,
    start_codons=".*TG$",
    min_ORF_len=15,
    remove_duplicates=True,
    exclude_invalid_TTS=True,
    ribo_output=None,
    grouped_ribo_ids={},
    parallel=False,
    return_ORF_coords=False,
):
    f = h5py.File(h5_path, "r")
    f_tr_ids = np.array(f["transcript/transcript_id"])
    f_headers = pl.Series(f["transcript"].keys())
    f_headers = f_headers.filter(~f_headers.is_in(["riboseq", "tis"]))
    has_tt_output = "tis_transformer_score" in f_headers
    f_headers = f_headers.filter(f_headers != "tis_transformer_score")
    has_rt_output = ribo_output is not None
    assert has_tt_output or has_rt_output, "no model predictions found"
    tool_scores = np.array(["ribotie_score", "tis_transformer_score"])[
        [has_rt_output, has_tt_output]
    ].tolist()
    # Add whichever other column info provided when GTF was first parsed
    xtr_heads = (
        pl.Series(f_headers)
        .filter(~pl.Series(f_headers).is_in(STANDARD_HEADERS))
        .to_list()
    )
    prtime(f"Processing '{out_prefix}.npy'...", "\n")
    if has_rt_output:
        assert grouped_ribo_ids is not {}, "No grouped_ribo_id dictionary provided"
        prefix = "ribotie_"
        tool_headers = tool_scores + ["ribotie_rank"]
        tr_ids = np.array([o[0].split(b"|")[1] for o in ribo_output])
        group = ribo_output[0][0].split(b"|")[0].decode()
        pred_to_h5_args = get_str2str_idx_map(tr_ids, f_tr_ids)
        preds = [o[1] for o in ribo_output]
        if has_tt_output:
            tt_scores = f["transcript/tis_transformer_score"][:][pred_to_h5_args]
            df = pl.DataFrame(
                {
                    "transcript_id": tr_ids,
                    "h5_idx": pred_to_h5_args,
                    f"ribotie_score": preds,
                    f"tis_transformer_score": tt_scores,
                }
            ).with_columns(
                pl.col(f"tis_transformer_score").map_elements(list, pl.List(pl.Float32))
            )
        else:
            df = pl.DataFrame(
                {
                    "transcript_id": tr_ids,
                    "h5_idx": pred_to_h5_args,
                    f"ribotie_score": preds,
                },
                strict=False,
            )
        out_headers = tool_headers + STANDARD_OUT_HEADERS + RIBO_OUT_HEADERS + xtr_heads
    else:
        prefix = "tis_transformer_"
        # bring columns to forefront in final output table
        tool_headers = ["tis_transformer_score", "tis_transformer_rank"]
        df = pl.DataFrame(
            {
                "transcript_id": f["transcript/transcript_id"][:],
                "h5_idx": np.arange(len(f_tr_ids)),
                f"{prefix}score": f["transcript/tis_transformer_score"][:],
            }
        ).with_columns(
            pl.col(f"{prefix}score").map_elements(list, pl.List(pl.Float32)),
        )
        out_headers = tool_headers + STANDARD_OUT_HEADERS + xtr_heads
    if return_ORF_coords:
        out_headers += ["ORF_coords"]

    prtime(f"Parsing ORF information...", "\t")
    df = df.with_columns(
        TIS_idx=(
            pl.col(f"{prefix}score")
            .list.eval(
                ((pl.element() > prob_cutoff) & pl.element().is_not_nan()).arg_true()
            )
            .cast(pl.List(pl.Int32))
        ),
    ).sort("h5_idx")

    # filter transcripts with zero predictions
    tr_mask = df["TIS_idx"].list.len() > 0
    df = df.filter(tr_mask)

    # Select only the scores that are above the prob_cutoff
    for score in tool_scores:
        df = df.with_columns(pl.col(score).list.gather(pl.col("TIS_idx")).alias(score))

    # check for positive set size and winnow if necessary
    max_preds = 1000000
    if df["TIS_idx"].explode().shape[0] > max_preds:
        print(
            f"\t\t-- Too many predictions, filtering to top {max_preds}. Consider increasing prob_cutoff"
        )
        # explode -> sort -> head -> groupby
        df = df.explode(tool_scores + ["TIS_idx"]).sort(
            f"{prefix}score", descending=True
        )
        df = df.head(max_preds)
        df = df.group_by(["transcript_id", "h5_idx"]).agg(tool_scores + ["TIS_idx"])

    # add transcript/gene information before exploding df
    df = df.with_columns(
        [
            pl.Series(name=h, values=f[f"transcript/{h}"][:][df["h5_idx"]])
            for h in f_headers
        ]
    )

    # devectorize and Listify numpy arrays
    df = df.with_columns(
        (
            pl.col("canonical_protein_seq")
            .map_elements(list, pl.List(pl.Int8))
            .list.eval(pl.element().replace_strict(IDX_PROT_DICT))
            .list.join("")
        ),
        (
            pl.col("seq")
            .map_elements(list, pl.List(pl.Int8))
            .list.eval(pl.element().replace_strict(IDX_DNA_DICT))
            .list.join("")
        ),
    ).with_columns(
        pl.col("exon_idxs").map_elements(list, pl.List(pl.Int64)),
        pl.col("exon_coords").map_elements(list, pl.List(pl.Int64)),
        pl.col("CDS_coords").map_elements(list, pl.List(pl.Int64)),
        pl.col("CDS_idxs").map_elements(list, pl.List(pl.Int64)),
        pl.col(f"{prefix}score").map_elements(list, pl.List(pl.Float64)),
        pl.col(pl.Binary).cast(pl.String),
    )
    # Explode df to get ORF predictions per row
    df = df.explode(tool_scores + ["TIS_idx"]).sort("h5_idx")
    # if non-canonical ATG, find in-frame ATGs to 'correct' prediction to
    if correction:
        # Set corr_dist to max from which in-frame codons are derived
        df = df.with_columns(corr_dist=pl.lit(dist * 3))
        df = (
            # 1. Calc upstream cut as multiple of 3 and not lower than 0
            df.with_columns(
                upstr_cut=pl.col("corr_dist").clip(
                    0, pl.col("TIS_idx") - pl.col("TIS_idx").mod(3)
                )
            )
            # Create list of codons and check for in-frame ATG
            .with_columns(
                corrects=(
                    pl.col("seq")
                    .str.slice(
                        pl.col("TIS_idx") - pl.col("upstr_cut"),
                        pl.col("upstr_cut") + 3 + dist * 3,
                    )
                    .map_elements(
                        lambda x: [x[i : i + 3] for i in range(0, len(x), 3)],
                        return_dtype=pl.List(pl.String),
                    )
                    .list.eval(
                        pl.element().str.contains("ATG").arg_true().cast(pl.Int8)
                    )
                )
            )
            .explode("corrects")
            .with_columns(corrects=pl.col("corrects") * 3 - pl.col("upstr_cut"))
            .group_by(pl.exclude("corrects"))
            .all()
            # 2. From distances, select ATG closest to pred TIS
            .with_columns(
                correction=(
                    pl.col("corrects")
                    .list.get(
                        pl.col("corrects").list.eval(pl.element().abs()).list.arg_min()
                    )
                    .fill_null(0)
                )
            )
            # 3. Apply corrects and keep unique matches
            .with_columns(TIS_idx=pl.col("TIS_idx") + pl.col("correction"))
        )
        if remove_duplicates:
            df = df.sort("ribotie_score", descending=True).unique(
                ["transcript_id", "TIS_idx"], keep="first"
            )
    prot_f_dict = {
        "protein_seq": pl.String,
        "TTS_on_transcript": pl.Boolean,
        "stop_codon": pl.String,
    }
    df = (
        df.with_columns(
            (
                pl.col("seq")
                .str.slice(pl.col("TIS_idx"))
                .map_elements(
                    lambda x: dict(zip(list(prot_f_dict.keys()), construct_prot(x))),
                    return_dtype=pl.Struct(prot_f_dict),
                )
                .alias("prot_struct")
            ),
            strand=pl.col("strand"),
            TIS_pos=pl.col("TIS_idx") + 1,
            canonical_TTS_idx=pl.col("canonical_LTS_idx") + 1,
            start_codon=pl.col("seq").str.slice(pl.col("TIS_idx"), 3),
            dist_from_canonical_TIS=(
                pl.when(pl.col("canonical_TIS_idx") != 0)
                .then(pl.col("TIS_idx") - pl.col("canonical_TIS_idx"))
                .otherwise(pl.lit(None))
                .cast(pl.Int32)
            ),
            canonical_TIS_pos=pl.col("canonical_TIS_idx") + 1,
            canonical_TTS_pos=pl.col("canonical_TTS_idx") + 1,
            canonical_LTS_pos=pl.col("canonical_LTS_idx") + 1,
        )
        .unnest("prot_struct")
        .with_columns(
            frame_wrt_canonical_TIS=pl.col("dist_from_canonical_TIS") % 3,
            ORF_len=pl.col("protein_seq").str.len_chars() * 3,
            ORF_id=pl.col("transcript_id")
            + "_"
            + (pl.col("TIS_idx") + 1).cast(pl.String),
        )
        .with_columns(
            TTS_idx=(
                pl.when(pl.col("TTS_on_transcript"))
                .then(pl.col("TIS_idx") + pl.col("ORF_len"))
                .otherwise(pl.lit(-1))
            ),
            LTS_idx=(
                pl.when(pl.col("TTS_on_transcript"))
                .then(pl.col("TIS_idx") + pl.col("ORF_len") - 1)
                .otherwise(pl.col("transcript_len") - 1)
            ),
        )
        .with_columns(
            TTS_pos=pl.col("TTS_idx") + 1,
        )
    )
    # Filter out faulty ORFs (length 0)
    df = df.filter(pl.col("ORF_len") > 0)
    # Find exon id's and coordinates for start and stop sites
    sel_cols = [
        "ORF_id",
        "strand",
        "TTS_on_transcript",
        "TIS_idx",
        "LTS_idx",
        "TTS_idx",
        "exon_idxs",
        "exon_coords",
    ]
    df_tmp = df.select(sel_cols)
    for poi in ["TIS", "LTS", "TTS"]:
        exon_start_idx = (pl.col(f"{poi}_exon") - 1) * 2
        # polars cannot use pl.col in list.eval function, hence explode - groupby
        df_tmp = (
            df_tmp.join(
                (
                    df_tmp.explode("exon_idxs")
                    .with_columns(
                        (pl.col("exon_idxs") <= pl.col(f"{poi}_idx")).alias(
                            f"{poi}_exon"
                        )
                    )
                    .group_by("ORF_id")
                    .agg(pl.col(f"{poi}_exon").sum() // 2 + 1)
                ),
                on="ORF_id",
                how="left",
            )
            .with_columns(
                (
                    pl.when(pl.col(f"{poi}_idx") == -1)
                    .then(pl.lit(-1))
                    .otherwise(pl.col(f"{poi}_exon"))
                    .alias(f"{poi}_exon")
                ),
                (
                    pl.when(pl.col(f"{poi}_idx") == -1)
                    .then(pl.lit(-1))
                    .otherwise(
                        pl.col(f"{poi}_idx")
                        - pl.col("exon_idxs").list.get(exon_start_idx)
                    )
                    .alias(f"{poi}_idx_on_exon")
                ),
            )
            .with_columns(
                (pl.col(f"{poi}_idx_on_exon") + 1).alias(f"{poi}_pos_on_exon"),
                pl.when((pl.col(f"{poi}_idx") != -1) & (pl.col("strand") == "+"))
                .then(
                    pl.col("exon_coords").list.get(exon_start_idx, null_on_oob=True)
                    + pl.col(f"{poi}_idx_on_exon")
                )
                .when((pl.col(f"{poi}_idx") != -1) & (pl.col("strand") == "-"))
                .then(
                    pl.col("exon_coords").list.get(exon_start_idx + 1, null_on_oob=True)
                    - pl.col(f"{poi}_idx_on_exon")
                )
                .otherwise(pl.lit(-1))
                .alias(f"{poi}_coord"),
            )
        )
    df = df.join(df_tmp.drop(sel_cols[1:]), on="ORF_id", how="left")
    if has_rt_output:
        prtime("Parsing ribo-seq information...", "\t")
        df_ribo = parse_ribo_data(df, f, h5_path, grouped_ribo_ids[group], parallel)
        if len(df_ribo) > 0:
            df = df.join(df_ribo[:, [0, *range(10, 18)]], on="ORF_id", how="inner")
        else:
            if len(df) > 0:
                print(f"!-> No ribosome reads present amongst input samples.")
            df = df.join(df_ribo[:, [0]], on="ORF_id", how="inner")
    # stop early if df is empty
    if len(df) == 0:
        out_dicts = {n: pl.Series(n, []) for n in out_headers}
        df_out = pl.DataFrame(out_dicts).rename(RENAME_HEADERS)
        df_out.write_csv(f"{out_prefix}.redundant.csv")
        df_out.write_csv(f"{out_prefix}.csv")
        df_out.write_csv(f"{out_prefix}.novel.csv")
        print(f"\t !-> The positive set is empty!")
        return df_out, df_out, df_out

    # detect ORF biotypes, evaluate whether transcript biotype is given
    prtime("Parsing ORF type information...", "\t")
    if "transcript_biotype" in df.columns:
        biotype_expr = pl.col("transcript_biotype") == "lncRNA"
    else:
        biotype_expr = pl.lit(False)
    df = df.with_columns(
        ORF_type=pl.when(pl.col("canonical_TIS_idx") != -1)
        .then(
            pl.when(pl.col("canonical_TIS_idx") == pl.col("TIS_idx"))
            .then(
                pl.when(pl.col("canonical_LTS_idx") == pl.col("LTS_idx"))
                .then(pl.lit("annotated CDS"))
                .when(pl.col("canonical_TTS_idx") < pl.col("TTS_idx"))
                .then(pl.lit("C-terminal extension"))
                .otherwise(pl.lit("C-terminal truncation"))
            )
            .when(pl.col("canonical_TTS_idx") < pl.col("TIS_idx"))
            .then(pl.lit("dORF"))
            .when(pl.col("canonical_TIS_idx") >= pl.col("TTS_idx"))
            .then(pl.lit("uORF"))
            .when(pl.col("canonical_TIS_idx") > pl.col("TIS_idx"))
            .then(
                pl.when(pl.col("canonical_TTS_idx") == pl.col("TTS_idx"))
                .then(pl.lit("N-terminal extension"))
                .otherwise(pl.lit("uoORF"))
            )
            .when(pl.col("canonical_TTS_idx") < pl.col("TTS_idx"))
            .then(pl.lit("doORF"))
            .otherwise(
                pl.when(pl.col("canonical_TTS_idx") == pl.col("TTS_idx"))
                .then(pl.lit("N-terminal truncation"))
                .otherwise(pl.lit("intORF"))
            )
        )
        .otherwise(
            pl.when(biotype_expr)
            .then(pl.lit("lncRNA-ORF"))
            .otherwise(pl.lit("varRNA-ORF"))
        )
    )
    prtime("Detecting CDS variants...", "\t")
    out_cols = ["ORF_coords", "ORF_exons"]
    out_types = [pl.List(pl.Int64), pl.List(pl.Int64)]
    attrs = ["TIS_coord", "LTS_coord", "strand", "exon_coords"]
    df = (
        df.with_columns(
            pl.struct(set(attrs))
            .map_elements(
                lambda x: dict(
                    zip(out_cols, transcript_region_to_exons(*[x[a] for a in attrs]))
                ),
                return_dtype=pl.Struct(dict(zip(out_cols, out_types))),
            )
            .struct.unnest()
        )
        .with_columns(
            ORF_exon_start=pl.col("ORF_coords").list.gather_every(2, 0),
            ORF_exon_end=pl.col("ORF_coords").list.gather_every(2, 1),
        )
        .with_columns(
            ORF_exon_len=(
                (pl.col("ORF_exon_start") - pl.col("ORF_exon_end")).list.eval(
                    pl.element().abs() + 1
                )
            )
        )
    )
    # load in all CDS properties in h5 db
    h5_cols = [
        "transcript_id",
        "seqname",
        "strand",
        "CDS_coords",
        "canonical_TIS_coord",
        "canonical_LTS_coord",
    ]
    mask = pl.Series(list(f[f"transcript/canonical_TIS_idx"])) != -1
    df_CDS = (
        pl.DataFrame(
            {f"{h}": np.array(f[f"transcript/{h}"])[mask.arg_true()] for h in h5_cols}
        )
        .with_columns(
            pl.col("CDS_coords").map_elements(list, pl.List(pl.Int64)),
            pl.col(pl.Binary).cast(pl.String),
        )
        .with_columns(
            CDS_exon_start=pl.col("CDS_coords").list.gather_every(2, 0),
            CDS_exon_end=pl.col("CDS_coords").list.gather_every(2, 1),
            CDS_start_range=(
                pl.when(pl.col("strand") == "+")
                .then(pl.col("CDS_coords").list.get(0))
                .otherwise(pl.col("CDS_coords").list.get(-2))
            ),
            CDS_end_range=(
                pl.when(pl.col("strand") == "+")
                .then(pl.col("CDS_coords").list.get(-1))
                .otherwise(pl.col("CDS_coords").list.get(1))
            ),
        )
        .drop("CDS_coords")
    )
    # close h5 db handle
    f.file.close()
    # To evaluate CDS variants, group df and df_CDS by seqname (to prevent OOM)
    df_grps = []
    total = df["seqname"].unique().len()
    for seqname, df_grp in tqdm(df.group_by("seqname"), total=total, desc="seqname"):
        df_CDS_grp = df_CDS.filter(pl.col("seqname") == seqname[0])
        df_grp = parse_CDS_overlap(df_grp, df_CDS_grp)
        df_grps.append(df_grp)

    df = pl.concat(df_grps)
    df = df.with_columns(pl.col("shared_in_frame_CDS_frac").truediv(pl.col("ORF_len")))
    # Change ORF_coord delimiter to ";"
    if return_ORF_coords:
        df = df.with_columns(
            ORF_coords=pl.col("ORF_coords").cast(pl.List(pl.String)).list.join(";")
        )

    # --- Filter CDS variants and custom filters ---
    # Custom filters
    conds_xtr = [
        pl.col("TTS_on_transcript") if exclude_invalid_TTS else pl.lit(True),
        pl.col("start_codon").str.contains(start_codons),
        pl.col("ORF_len") >= min_ORF_len,
    ]
    c_xtr = pl.lit(True).and_(*conds_xtr)
    df = df.filter(c_xtr)
    # CDS variant filtering
    if len(df) > 0:
        df_filt = filter_CDS_variants(df)
    else:
        df_filt = df
    df_novel = df_filt.filter(pl.col("ORF_type") != "annotated CDS")

    # --- Save to csv ---
    for df_, label in zip([df, df_filt, df_novel], [".redundant", "", ".novel"]):
        save_output_table(df_, out_prefix, label, prefix, out_headers)

    return df, df_filt, df_novel


def save_output_table(df, out_prefix, label, prefix, out_headers):
    df = (
        df.with_columns(
            (pl.col(f"{prefix}score").rank(method="ordinal", descending=True)).alias(
                f"{prefix}rank"
            )
        )
        .select(out_headers)
        .sort(f"{prefix}rank")
        .rename(RENAME_HEADERS)
    )
    df.write_csv(f"{out_prefix}{label}.csv", float_precision=4)


def filter_CDS_variants(df):
    conds_cds_var = [
        pl.col("has_CDS_clones") == False,
        pl.col("shared_in_frame_CDS_frac") < 1,
    ]
    c_clone = pl.col("has_CDS_clones") == False
    c_cds_var = pl.lit(True).and_(*conds_cds_var)
    c_1 = pl.col("ORF_type") == "annotated CDS"
    c_2 = pl.col("ORF_type").is_in(
        [
            "N-terminal truncation",
            "N-terminal extension",
            "C-terminal truncation",
            "C-terminal extension",
        ]
    )
    c_3 = pl.col("ORF_type").is_in(
        ["uORF", "uoORF", "dORF", "doORF", "intORF", "lncRNA-ORF"]
    )
    if "transcript_biotype" in df.columns:
        c_bio = pl.col("transcript_biotype") == "protein_coding"
    else:
        c_bio = pl.lit(False)

    filter_suffix = ""
    df_filts = []
    for _, df_grp in df.group_by("TIS_coord"):
        df_filt = df_grp.filter(
            # If annotated CDS then annotated CDS
            pl.when(c_1.any()).then(c_1)
            # elif trunc/extension & not CDS clone
            .when((c_2 & c_clone).any()).then(c_2 & c_clone)
            # elif type 3 & not CDS variant
            .when((c_3 & c_cds_var).any()).then(c_3 & c_cds_var)
            # else OK if not CDS clones and in_frame_CDS_frac < 1
            .otherwise(c_cds_var)
            # if either annotated or protein coding present, select these otherwise OK
            & pl.when((c_1 | c_bio).any()).then(c_1 | c_bio).otherwise(pl.lit(True))
        )
        df_filts.append(df_filt)
    df_filt = pl.concat(df_filts)

    return df_filt


def process_seq_preds(ids, preds, seqs, min_prob):
    # Find indices above min_prob for each prediction
    mask = [np.where(pred > min_prob)[0] for pred in preds]

    rows = []
    for i, idxs in enumerate(mask):
        tr = seqs[i]
        for idx in idxs:
            prot_seq, has_stop, stop_codon = construct_prot(tr[idx:])
            TTS_pos = idx + len(prot_seq) * 3
            rows.append(
                {
                    "transcript_id": ids[i],
                    "transcript_length": len(tr),
                    "TIS_pos": idx + 1,
                    "output": preds[i][idx],
                    "start_codon": tr[idx : idx + 3],
                    "TTS_pos": TTS_pos,
                    "stop_codon": stop_codon,
                    "TTS_on_transcript": has_stop,
                    "protein_length": len(prot_seq),
                    "protein_sequence": prot_seq,
                }
            )
    return pl.DataFrame(rows)


def create_multiqc_reports(df, out_prefix, id, name):
    # Start codons
    output = out_prefix + ".start_codons_mqc.tsv"
    header = RIBOTIE_MQC_HEADER.format(id=id, name=name)
    with open(output, "w") as f:
        f.write(header)
        f.write(START_CODON_MQC_HEADER.format(id=id))
    start_codons = df["start_codon"].value_counts()
    with open(output, mode="a") as f:
        start_codons.write_csv(f, separator="\t", include_header=False)

    # Transcript biotypes
    if "transcript_biotype" in df.columns:
        output = out_prefix + ".biotypes_variant_mqc.tsv"
        with open(output, "w") as f:
            f.write(header)
            f.write(BIOTYPE_VARIANT_MQC_HEADER.format(id=id))
        orf_biotypes = (
            df.filter(pl.col("ORF_type") == "varRNA-ORF")["transcript_biotype"]
            .value_counts()
            .sort("count", descending=True)
        )
        with open(output, mode="a") as f:
            orf_biotypes.write_csv(f, separator="\t", include_header=False)

    # ORF types
    output = out_prefix + ".ORF_types_mqc.tsv"
    with open(output, "w") as f:
        f.write(header)
        f.write(ORF_TYPE_MQC_HEADER.format(id=id))
    orf_types = (
        df["ORF_type"]
        .value_counts()
        .sort(pl.col("ORF_type").cast(pl.Enum(ORF_TYPE_ORDER)))
    )
    with open(output, mode="a") as f:
        orf_types.write_csv(f, separator="\t", include_header=False)

    # ORF lengths
    # output = out_prefix + ".ORF_lens_mqc.tsv"
    # ax = df.ORF_len.apply(lambda x: np.log(x)).plot.kde()
    # x, y = np.exp(ax.lines[-1].get_xdata()), ax.lines[-1].get_ydata()
    # with open(output, "w") as f:
    #     f.write(RIBOTIE_MQC_HEADER)
    #     f.write(ORF_LEN_MQC_HEADER)
    #     for x_, y_ in zip(x, y):
    #         f.write(f"{x_}\t{y_}\n")

    return


def csv_to_gtf(h5_path, df, out_prefix, caller):
    """
    Converts a DataFrame of ORF predictions into a GTF file.
    !!! Creates a unique transcript entry for each ORF to ensure GTF compatibility. !!!
    """
    df = df.fill_null("NA").sort("transcript_id").cast({"seqname": pl.String})

    # Create a lookup map for original transcript_id to exon coordinates for efficiency.
    with h5py.File(h5_path, "r") as f:
        h5_ids = np.array(f["transcript/transcript_id"], dtype=str)
        h5_exons = np.array(f["transcript/exon_coords"])
        tr_id_to_exon_coords = dict(zip(h5_ids, h5_exons))

    gtf_lines = []

    # Iterate through each ORF (row) to create a separate transcript entry.
    for orf in df.iter_rows(named=True):
        original_transcript_id = orf["transcript_id"]
        exon_coord = tr_id_to_exon_coords.get(original_transcript_id)

        if exon_coord is None:
            # Optionally, log or handle cases where exon coordinates are not found.
            continue

        check_genomic_order(exon_coord, orf["strand"])

        # Use ORF_id as the new transcript_id for GTF compatibility.
        dummy_transcript_id = orf["ORF_id"]

        # --- Define base attributes for this new dummy transcript ---
        base_attrs = {
            "gene_id": orf["gene_id"],
            "transcript_id": dummy_transcript_id,
            "gene_name": orf["gene_name"],
        }

        # --- 1. Generate the 'transcript' feature line ---
        if orf["strand"] == "+":
            tr_start, tr_stop = exon_coord[0], exon_coord[-1]
        else:
            tr_start, tr_stop = exon_coord[-2], exon_coord[1]

        attr_str = "; ".join([f'{k} "{v}"' for k, v in base_attrs.items()]) + ";"
        gtf_lines.append(
            f'{orf["seqname"]}\t{caller}\ttranscript\t{tr_start}\t{tr_stop}\t.\t{orf["strand"]}\t.\t{attr_str}\n'
        )

        # --- 2. Generate 'exon' feature lines for the transcript ---
        exons = exon_coord.reshape(-1, 2)
        for i, (exon_start, exon_stop) in enumerate(exons):
            exon_attrs = base_attrs | {"exon_number": i + 1}
            attr_str = "; ".join([f'{k} "{v}"' for k, v in exon_attrs.items()]) + ";"
            gtf_lines.append(
                f'{orf["seqname"]}\t{caller}\texon\t{exon_start}\t{exon_stop}\t.\t{orf["strand"]}\t.\t{attr_str}\n'
            )

        # --- 3. Generate feature lines for this specific ORF ---
        TIS, LTS, TTS, strand = (
            orf["TIS_coord"],
            orf["LTS_coord"],
            orf["TTS_coord"],
            orf["strand"],
        )

        orf_fields = ["ORF_id", "ORF_type", "ribotie_score", "tis_transformer_score"]
        orf_attrs = {k: orf[k] for k in orf_fields if k in orf and orf[k] != "NA"}

        feature_definitions = []
        if TIS is not None:
            start_codon_stop = find_distant_exon_coord(TIS, 2, strand, exon_coord)
            feature_definitions.append(("start_codon", TIS, start_codon_stop))
        feature_definitions.append(("CDS", TIS, LTS))
        if TTS != -1:
            stop_codon_stop = find_distant_exon_coord(TTS, 2, strand, exon_coord)
            feature_definitions.append(("stop_codon", TTS, stop_codon_stop))

        for feature_type, start_coord, stop_coord in feature_definitions:
            if start_coord is None or stop_coord is None:
                continue

            parts, part_exons = transcript_region_to_exons(
                start_coord, stop_coord, strand, exon_coord
            )

            for i, (part_start, part_stop) in enumerate(np.array(parts).reshape(-1, 2)):
                feature_attrs = base_attrs | orf_attrs | {"exon_number": part_exons[i]}
                attr_str = (
                    "; ".join([f'{k} "{v}"' for k, v in feature_attrs.items()]) + ";"
                )
                gtf_lines.append(
                    f'{orf["seqname"]}\t{caller}\t{feature_type}\t{part_start}\t{part_stop}\t.\t{strand}\t.\t{attr_str}\n'
                )

    # --- Write all generated lines to the output GTF file ---
    with open(f"{out_prefix}.gtf", "w") as f:
        f.writelines(gtf_lines)
