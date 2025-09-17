import os
import sys
from copy import deepcopy
import numpy as np
import h5py
import yaml
from typing import cast
from importlib.resources import files

from .transcript_transformer import train, predict
from .argparser import Parser
from .util_functions import (
    find_optimal_folds,
    prtime,
    mv_ckpt_to_out_dir,
    merge_outputs,
    parse_fasta,
)
from .data import process_seq_data
from .processing import (
    construct_output_table,
    csv_to_gtf,
    create_multiqc_reports,
    process_seq_preds,
)


def parse_args():
    parser = Parser(
        description="Run TIS Transformer", stage="train", tool="tis_transformer"
    )
    parser.add_run_args()
    data_parser = parser.add_data_args()
    # Argument (model) to use pre-trained model, Can only be human or mouse
    data_parser.add_argument(
        "--model",
        choices=["human", "mouse"],
        default=None,
        type=str,
        help="Use a pre-trained model for predictions. Models are trained on Ensembl database."
        "Choices: 'human', 'mouse'.",
    )
    fa_parser = parser.add_argument_group(
        "fasta",
        "Use a fasta file with sequences to predict. Ignores --h5_path and --gtf_path.",
    )
    fa_parser.add_argument(
        "--fasta",
        type=str,
        default=None,
        help="Path to a fasta file with sequences to predict. Ignores --h5_path and --gtf_path.",
    )
    fa_parser.add_argument(
        "--fold",
        type=int,
        default=0,
        help="Determines the fold number to use for prediction. If not set, the first fold will be used",
    )

    parser.add_processing_args()
    parser.add_comp_args()
    parser.add_training_args()
    parser.add_train_loading_args()
    parser.add_evaluation_args()
    # Too advanced for now, not documented
    # parser.add_architecture_args()
    default_config = files("transcript_transformer.configs").joinpath("defaults.tt.yml")
    default_config = os.fspath(cast(os.PathLike, default_config))
    args = parser.parse_arguments(sys.argv[1:], [default_config])
    if args.out_prefix is None:
        print(args.conf[0])
        args.out_prefix = f"{os.path.splitext(args.h5_path)[0]}_"

    return args


def main():
    prtime("Running TIS Transformer tool\n")
    args = parse_args()

    if args.fasta:
        print(f"\t -- Using Pre-trained {args.model} TIS Transformer model parameters")
        args.__dict__.update(args.trained_model["folds"][args.fold])
        args.transfer_checkpoint = os.path.join(
            args.model_dir, args.transfer_checkpoint
        )
        # list test set contigs
        print(
            f"\t -- Using model trained on contigs: {args.train + args.val}. Parsed sequences are not supposed to be from these contigs. "
            f"Use different `--fold` (current: {args.fold}) to select a model trained on different data. See the user manual for more information."
        )
        predict(args)
        out = np.load(f"{args.out_prefix}.npy", allow_pickle=True)
        tr_ids = np.hstack([o[0] for o in out])
        pred_list = [o[1] for o in out]
        tr_ids, tr_seqs = parse_fasta(args.fasta, args.max_seq_len)
        mask = [np.where(pred > args.prob_cutoff)[0] for pred in pred_list]
        if len(np.hstack(mask)) > 0:
            df = process_seq_preds(tr_ids, pred_list, tr_seqs, args.prob_cutoff)
            print(df)
            df.write_csv(f"{args.out_prefix}.csv")
            print(f"\t -- Sites of interest saved to '{args.out_prefix}.csv'")
        else:
            print(
                f"\t !-> No sites of interest found (omitted creation of '{args.out_prefix}.csv')"
            )
        return

    # --- Data loading ---
    if not args.backup_path:
        args.backup_path = os.path.splitext(args.gtf_path)[0] + ".h5"
    process_seq_data(
        args.h5_path,
        args.gtf_path,
        args.fa_path,
        args.backup_path,
        not args.no_backup,
    )
    if args.data:
        prtime("End of pipeline (omit --data to run full pipeline)...", "\n")
        return 0

    # --- Determine folds and contigs if relevant ---
    if args.folds is None:
        prtime("Determining fold allocations...", "\n")
        f = h5py.File(args.h5_path, "r")["transcript"]
        contigs = np.array(f["seqname"])
        tr_lens = np.array(f["transcript_len"])
        f.file.close()
        contig_set = np.unique(contigs)
        if args.folds == None:
            contig_lens = {}
            # determine nt count per seqname
            for contig in contig_set:
                mask = contigs == contig
                contig_lens[contig] = sum(tr_lens[mask])
            args.folds = find_optimal_folds(contig_lens, args.test_frac, args.val_frac)

    # --- Training or Prediction ---
    prtime(f"Evaluating genome sequence data...", "\n\n")
    result_file = f"{args.out_prefix}.npy"
    keep_preds = os.path.isfile(result_file) and (not args.overwrite_preds)
    if ("trained_model" in args) and keep_preds:
        print(f"\t -- TIS Transformer output present: {result_file}")
        args.folds = {}  # Basically skip future steps
        req_train = False
    elif "trained_model" in args:
        # args.model > args.trained_model
        if args.model is not None:
            print(
                f"\t -- Using Pre-trained {args.model} TIS Transformer model parameters"
            )
        else:
            print(f"\t -- Using existing TIS Transformer model parameters")
        req_train = False
    else:
        print(f"\t -- Training TIS Transformer model parameters from scratch")
        req_train = True
    for i, fold in args.folds.items():
        args_set = deepcopy(args)
        args_set.__dict__.update(fold)
        # set output path
        args_set.out_prefix = "_".join([f"{args_set.out_prefix}", f"f{i}"])
        if req_train:
            prtime(f"Training model — Fold {i} ...", "\n")
            # train model
            trainer, model = train(
                args_set, test_model=False, enable_model_summary=False
            )
            mv_ckpt_to_out_dir(trainer, f"{args_set.out_prefix}.tt")
            rel_path = os.path.basename(args_set.out_prefix)
            args.folds[i]["transfer_checkpoint"] = f"{rel_path}.tt.ckpt"
            prtime(f"Predicting samples — Fold {i} ...", "\n")
            predict(args_set, trainer=trainer, model=model)
        else:
            print(args_set.transfer_checkpoint)
            args_set.transfer_checkpoint = os.path.join(
                args.model_dir, args_set.transfer_checkpoint
            )
            print(f"\t -- Loaded model: {args_set.transfer_checkpoint}...")
            prtime(f"Predicting samples — Fold {i} ...", "\n")
            predict(args_set)
    if len(args.folds) > 0:
        prtime(f"Merging predictions to {args.out_prefix}.npy...", "\n")
        merge_outputs(args.out_prefix, args.folds.keys())
        # remove independent fold outputs
        [os.remove(f"{args.out_prefix}_f{i}.npy") for i in args.folds.keys()]
        # Save params file
        if req_train:
            args.folds[0]["test"] = []
            save_dict = {"trained_model": {"folds": args.folds}}
            with open(f"{args.out_prefix}_params.tt.yml", "w+") as f:
                yaml.dump(save_dict, f, default_flow_style=False)

    # load predictions
    out = np.load(f"{args.out_prefix}.npy", allow_pickle=True)

    # --- Sort and transfer predictions to h5 file ---
    if not keep_preds:
        prtime(f"Saving predictions to {args.h5_path}...", "\n")
        tr_ids = np.hstack([o[0] for o in out])
        pred_list = [o[1] for o in out]
        aligned_pred_list = align_to_h5_ids(args.h5_path, tr_ids, pred_list)
        integrate_seq_predictions(args.h5_path, aligned_pred_list)
        if not args.no_backup:
            # check of existence of backup path file
            if os.path.exists(args.backup_path):
                integrate_seq_predictions(args.backup_path, aligned_pred_list)

    # --- Result Processing ---
    df, df_filt, df_novel = construct_output_table(
        h5_path=args.h5_path,
        out_prefix=args.out_prefix,
        prob_cutoff=args.prob_cutoff,
        start_codons=args.start_codons,
        min_ORF_len=args.min_ORF_len,
        exclude_invalid_TTS=not args.include_invalid_TTS,
        return_ORF_coords=args.return_ORF_coords,
    )
    if df is not None:
        names = ["TIS Transformer Redundant set", "TIS Transformer"]
        paths = [args.out_prefix + ".redundant", args.out_prefix]
        multiqc_path = os.path.join(os.path.dirname(args.out_prefix), "multiqc")
        os.makedirs(multiqc_path, exist_ok=True)
        for df, name, path in zip([df, df_filt], names, paths):
            csv_to_gtf(
                args.h5_path,
                df,
                path,
                "TIS_Transformer",
            )
            out = os.path.join(multiqc_path, os.path.basename(path))
            create_multiqc_reports(df, out, "tis_transformer", name)
        csv_to_gtf(
            args.h5_path, df_novel, args.out_prefix + ".novel", "TIS_Transformer"
        )


def align_to_h5_ids(h5_path, tr_ids, data_list, dtype=np.float32):
    f = h5py.File(h5_path, "r")
    grp = f["transcript"]
    f_tr_ids = grp["transcript_id"][:]
    f_tr_lens = grp["transcript_len"][:]
    f.close()
    unsorted_tr_ids = [s.split(b"|")[1] for s in tr_ids]
    # fast re-order predictions to hdf5 ids
    xsorted = np.argsort(f_tr_ids)
    idx_to_h5idx = xsorted[np.searchsorted(f_tr_ids[xsorted], unsorted_tr_ids)]
    # create emptry array
    pred_arr = np.empty(shape=(len(f_tr_ids),), dtype=object)
    pred_arr.fill(np.array([], dtype=dtype))
    for idx, pred in zip(idx_to_h5idx, data_list):
        pred_arr[idx] = pred
    # Idxs of missing predictions
    idxs_missing = [f for f in range(len(f_tr_ids)) if f not in idx_to_h5idx]
    for idx in idxs_missing:
        # If dtype is float32, float64, or float16, fill with NaN
        if np.issubdtype(dtype, np.floating):
            pred_arr[idx] = np.full(f_tr_lens[idx], np.nan, dtype=dtype)
        # If dtype is int subtype:
        elif np.issubdtype(dtype, np.integer):
            pred_arr[idx] = np.full(f_tr_lens[idx], -1, dtype=dtype)
        # Elif dtype is string subtype:
        elif np.issubdtype(dtype, np.string_):
            pred_arr[idx] = np.full(f_tr_lens[idx], b"", dtype=dtype)

    return pred_arr


def integrate_seq_predictions(h5_path, data_list, dtype=np.dtype("float32")):
    f = h5py.File(h5_path, "a")
    grp = f["transcript"]
    dtype = h5py.vlen_dtype(dtype)
    if "tis_transformer_score" in grp.keys():
        print(f"\t -- Overwriting results in {h5_path} database...")
        del grp["tis_transformer_score"]
    else:
        print(f"\t -- Writing results to {h5_path} database...")
    grp.create_dataset("tis_transformer_score", data=data_list, dtype=dtype)
    f.close()


if __name__ == "__main__":
    main()
