"""It would be tedious to get the user args to some places in the code (e.g.,
MOAD_target). Let's just make some of the variables globally availble here.
There arguments are broadly applicable, so it makes sense to separate them
anyway.
"""

import argparse
import json
from ..args_defaults import get_default_args

verbose = False


def _add_generic_params(
    parent_parser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Add parameters (args) that are common to all collagen apps.

    Args:
        parent_parser (argparse.ArgumentParser): The argparser.

    Returns:
        argparse.ArgumentParser: The updated argparser with the generic
        parameters added.
    """
    # TODO: Some of these arguments are not common, but specific to deepfrag.
    # Good to refactor some of this.

    # For many of these, good to define default values in args_defaults.py

    parser = parent_parser.add_argument_group("Common")
    parser.add_argument(
        "--cpu",
        action="store_true",
    )
    parser.add_argument(
        "--wandb_project",
        required=False,
        # default=None
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["train_on_moad", "train_on_complexes", "warm_starting", "test_on_moad", "test_on_complexes", "inference_single_complex", "inference_multiple_complexes"],
        help="Can be train, warm_starting, test, inference_single_complex, or inference_multiple_complexes.\n"
        + "\tIf train_on_moad, trains the model on the Binding MOAD Database.\n"
        + "\tIf train_on_complexes, trains the model receiving as input a CSV file with PDB/SDF file pairs corresponding to receptor/ligand complexes.\n"
        + "\tIf warm_starting, runs an incremental learning on a new dataset. It is suitable for fine tuning.\n"
        + "\tIf test_on_moad, runs inference on the test set extracted from the Binding MOAD Database.\n"
        + "\tIf test_on_complexes, runs inference on the test set extracted from a CSV file with PDB/SDF file pairs corresponding to receptor/ligand complexes.\n"
        + "\tIf inference_single_complex, runs inference on an external set by specifying the fragment coordinates.\n"
        + "\tIf inference_multiple_complexes, runs inference on an external set comprised of protein-ligand pairs, that is, a SDF file per each ligand and a PDB file per each receptor.\n",
    )

    parser.add_argument(
        "--test_predictions_file",
        type=str,
        help="If specified, the numpy file where the full test-set predictions will be saved. Requires that the mode is set to test.",
        default=None,
    )

    parser.add_argument(
        "--receptor",
        type=str,
        help="The receptor (PDB file) to use when running in inference mode.",
        default=None,
    )
    parser.add_argument(
        "--ligand",
        type=str,
        help="The ligand (SDF file) to use when running in inference mode.",
        default=None,
    )
    parser.add_argument(
        "--branch_atm_loc_xyz",
        type=str,
        help="A comma-separated list of x,y,z coordinates to use when running in inference mode.",
        default=None,
    )

    parser.add_argument(
        "--num_inference_predictions",
        type=int,
        help="The number of top-k matching fragments (SMILES strings) to return when running DeepFrag in inference mode.",
        default=10,
    )

    parser.add_argument(
        "--load_checkpoint",
        type=str,
        default=None,
        help="If specified, the model will be loaded from this checkpoint. You can list multiple checkpoints (separated by commas) for testing/inference.",
    )
    parser.add_argument(
        "--load_newest_checkpoint",
        action="store_true",
        help="If set, the most recent checkpoint will be loaded.",
    )
    # TODO: JDD: Load from best validation checkpoint.
    parser.add_argument(
        "--verbose",
        type=bool,
        required=False,
        default=False,
        # action="store_true",
        help="If set, will output additional information during the run. Useful for debugging.",
    )
    parser.add_argument(
        "--json_params",
        required=False,
        default=None,
        help="Path to a json file with parameters that override those specified at the command line.",
    )
    parser.add_argument(
        "--save_params",
        required=False,
        # default=None,
        help="Path to a json file where all parameters will be saved. Useful for debugging.",
    )
    parser.add_argument(
        "--learning_rate",
        required=False,
        # default=1e-4,
        help="The learning rate.",
    )
    parser.add_argument(
        "--model_for_warm_starting",
        type=str,
        required=False,
        default=None,
        help="Path to .pt file where the model to be used for incremental learning is saved",
    )

    return parent_parser


def _get_arg_parser(
    parser_funcs: list, is_pytorch_lightning=False
) -> argparse.ArgumentParser:
    """Construct an arg parser.

    Args:
        parser_funcs (list): A list of functions that add arguments to a
            parser. They each accept a parser and return a parser.
        is_pytorch_lightning (bool, optional): Whether the app uses pytorch
            lightning. Defaults to False.

    Returns:
        argparse.ArgumentParser: A parser with all the arguments added.
    """
    # Create the parser
    parent_parser = argparse.ArgumentParser()

    # Add arguments to it per each input function
    for func in parser_funcs:
        parent_parser = func(parent_parser)

    # Add arguments that are common to all apps.
    parent_parser = _add_generic_params(parent_parser)

    # Add pytorch lighting parameters if appropriate.
    if is_pytorch_lightning:
        import pytorch_lightning as pl  # type: ignore

        pl.Trainer.add_argparse_args(parent_parser)

    return parent_parser


def get_args(
    parser_funcs=None, post_parse_args_funcs=None, is_pytorch_lightning=False
) -> argparse.Namespace:
    """Create a parser and gets the associated parameters.

    Args:
        parser_funcs (list, optional): A list of functions that add arguments to
            a parser. They each accept a parser and return a parser. Defaults to
            [].
        fix_args_funcs (list, optional): A list of functions that modify the
            parsed args. Each accepts args and returns args. Allows for
            modifying one argument based on the value of another. Defaults to
            [].
        is_pytorch_lightning (bool, optional): [description]. Defaults to False.

    Returns:
        argparse.Namespace: The parsed and updated args.
    """
    if parser_funcs is None:
        parser_funcs = []
    if post_parse_args_funcs is None:
        post_parse_args_funcs = []

    global verbose

    # Get the parser
    parser = _get_arg_parser(parser_funcs, is_pytorch_lightning)

    # Set any missing defaults. Use the set_defaults() function.
    d = get_default_args()
    for k, v in d.items():
        parser.set_defaults(**{k: v})

    # Parse the arguments
    args = parser.parse_args()

    # Make a few select arguments globally available.
    verbose = args.verbose

    # Add parameters from JSON file, which override any command-line parameters.
    if args.json_params:
        with open(args.json_params, "rt") as f:
            new_args = json.load(f)
        for k in new_args.keys():
            setattr(args, k, new_args[k])

    # Fix the arguments.
    for func in post_parse_args_funcs:
        args = func(args)

    # Save all arguments to a json file for debugging.
    if args.save_params is not None:
        with open(args.save_params, "w") as f:
            json.dump(vars(args), f, indent=4)

    # Always print out the arguments to the screen.
    print("\nPARAMETERS")
    print("-----------\n")
    for k, v in vars(args).items():
        print(f"{k.rjust(35)} : {str(v)}")
    print("")

    return args
