"""Parent class for all MOAD voxel models."""

from argparse import ArgumentParser, Namespace
import json
from typing import Sequence, Type, TypeVar, Union
from collagen.external.common.datasets.fragment_dataset import FragmentDataset
from collagen.model_parents.moad_voxel.inference_single_complex import InferenceSingleComplex
from collagen.model_parents.moad_voxel.inference_multiple_complexes import (
    InferenceMultipleComplex,
)
from collagen.model_parents.moad_voxel.inits import VoxelModelInits
from collagen.model_parents.moad_voxel.test import VoxelModelTest
from collagen.model_parents.moad_voxel.train import VoxelModelTrain
from collagen.model_parents.moad_voxel import arguments
import os
from collagen.model_parents.moad_voxel.utils import VoxelModelUtils
from collagen.core.molecules.fingerprints import download_molbert_ckpt
import pytorch_lightning as pl  # type: ignore
import torch  # type: ignore

# from ... import VoxelParams

ENTRY_T = TypeVar("ENTRY_T")
TMP_T = TypeVar("TMP_T")
OUT_T = TypeVar("OUT_T")

# ENTRY_T = Tuple[Mol, Mol, BackedMol, str, int]
# TMP_T = Tuple[DelayedMolVoxel, DelayedMolVoxel, torch.Tensor, StructureEntry]
# OUT_T = Tuple[torch.Tensor, torch.Tensor, List[str]]


class VoxelModelParent:
    """Parent class for all MOAD voxel models."""

    def __init__(
        self,
        args: Namespace,
        model_cls: Type[pl.LightningModule],
        dataset_cls: FragmentDataset,
    ):
        """Initialize the model parent.

        Args:
            args (Namespace): The arguments parsed by argparse.
            model_cls (Type[pl.LightningModule]): The model class. Soemthing
                like DeepFragModelSDFData or DeepFragModel.
            dataset_cls (FragmentDataset): The dataset class.
                Something like FragmentDataset.
        """
        self.inits = VoxelModelInits(self)

        self.voxel_params = self.inits.init_voxel_params(args)
        self.num_voxel_features = self.voxel_params.receptor_featurizer.size() + self.voxel_params.ligand_featurizer.size()

        self.train = VoxelModelTrain(self)
        self.test = VoxelModelTest(self)
        self.inference_single_complex = InferenceSingleComplex(self)
        self.inference_multiple_complexes = InferenceMultipleComplex(self)
        self.utils = VoxelModelUtils(self)

        self.model_cls = model_cls

        self.dataset_cls = dataset_cls

        self.utils.disable_warnings()

    @staticmethod
    def add_moad_args(parent_parser: ArgumentParser) -> ArgumentParser:
        """Add the MOAD arguments to the parser.

        Args:
            parent_parser (ArgumentParser): The parser to add the arguments to.

        Returns:
            ArgumentParser: The parser with the arguments added.
        """
        return arguments.add_moad_args(parent_parser)

    @staticmethod
    def fix_moad_args(args: Namespace) -> Namespace:
        """Only works after arguments have been parsed, so in a separate
        definition.

        Args:
            args (Namespace): The arguments parsed by argparse.

        Returns:
            Namespace: The arguments with the MOAD arguments fixed.
        """
        return arguments.fix_moad_args(args)

    def pre_voxelize(self, args: Namespace, entry: ENTRY_T) -> TMP_T:
        """Preprocess the entry before voxelization. Should be overwritten by
        child class.

        Args:
            args (Namespace): The arguments parsed by argparse.
            entry (ENTRY_T): The entry to preprocess.

        Returns:
            TMP_T: The preprocessed entry.
        """
        raise NotImplementedError()

    def voxelize(self, args: Namespace, device: torch.device,
                 batch: Sequence[TMP_T], ) -> OUT_T:
        """Voxelize the batch. Should be overwritten by child class.

        Args:
            args (Namespace): The arguments parsed by argparse.
            device (torch.device): The device to use.
            batch (List[TMP_T]): The batch to voxelize.

        Returns:
            OUT_T: The voxelized batch.
        """
        raise NotImplementedError()

    @staticmethod
    def batch_eval(args: Namespace, batch: OUT_T):
        """Evaluate the batch. Should be overwritten by child class.

        Args:
            args (Namespace): The arguments parsed by argparse.
            batch (OUT_T): The batch to evaluate.
        """
        pass

    @staticmethod
    def custom_test(args: Namespace, predictions):
        """Run custom test. Should be overwritten by child class.

        Args:
            args (Namespace): The arguments parsed by argparse.
            predictions: The predictions.
        """
        pass

    @staticmethod
    def setup_fingerprint_scheme(args: Namespace):
        """Set up the fingerprint scheme.

        Args:
            args (Namespace): The arguments parsed by argparse.
        """
        if args.fragment_representation in [
            "rdk10",
            "rdk10_x_morgan",
        ]:
            args.__setattr__("fp_size", 2048)
        elif args.fragment_representation in [
            "molbert",
        ]:
            args.__setattr__("fp_size", 1536)
            download_molbert_ckpt()
        else:
            raise Exception("The fragment representation is wrong.")

    def load_checkpoint(self, args: Namespace, validate_args=True) -> Union[str, None]:
        """Load the checkpoint.

        Args:
            args (Namespace): The arguments parsed by argparse.
            validate_args (bool): Whether to validate the arguments.

        Returns:
            Union[str, None]: The checkpoint filename to load.
        """
        ckpt_filename = self.utils.get_checkpoint_filename(args, validate_args)
        if ckpt_filename is not None:
            print(f"Restoring from checkpoint: {ckpt_filename}")

        return ckpt_filename

    def run(self, args: Namespace):
        """Run the model.

        Args:
            args (Namespace): The arguments parsed by argparse.
        """
        self.utils.disable_warnings()
        self.setup_fingerprint_scheme(args)
        ckpt_filename = self.load_checkpoint(args)

        if args.mode == "train_on_moad" or args.mode == "train_on_complexes":
            print("Starting 'training' process")
            self.train.run_train(args, ckpt_filename)
        elif args.mode == "warm_starting":
            print("Starting 'warm_starting' process")
            self.train.run_warm_starting(args)
        elif args.mode == "test_on_moad" or args.mode == "test_on_complexes":
            print("Starting 'test' process")
            assert ckpt_filename is not None, "Must specify a checkpoint to test"
            self.test.run_test(args, ckpt_filename)
        elif args.mode == "inference_single_complex":
            print("Starting 'inference_single_complex' process")
            assert (
                ckpt_filename is not None
            ), "Must specify a checkpoint to run inference"
            self.inference_single_complex.run_test(args, ckpt_filename)
        elif args.mode == "inference_multiple_complexes":
            print("Starting 'inference_multiple_complexes' process")
            assert (
                ckpt_filename is not None
            ), "Must specify a checkpoint to run inference"
            self.inference_multiple_complexes.run_test(args, ckpt_filename)
        else:
            raise ValueError(f"Invalid mode: {args.mode}")

    # def _get_train_frag_counts(self, args, moad, train, voxel_params, device):
    #     # Without calculating voxels and fingerprints...

    #     # NOTE: No longer used, but leaving here as an example of how to get
    #     # fragments without calculating voxels. Useful for testing?

    #     voxel_params_frag = copy.deepcopy(voxel_params)
    #     voxel_params_frag.calc_voxels = False
    #     voxel_params_frag.calc_fps = False
    #     train_data_to_get_frags = get_data_from_split(self,
    #         args, moad, train, voxel_params_frag, device
    #     )

    #     frag_counts = {}

    #     for payload in tqdm(train_data_to_get_frags, desc="Counting fragment SMILES..."):
    #         _, _, entry_infos = payload
    #         for entry_info in entry_infos:
    #             if entry_info.fragment_smiles not in frag_counts:
    #                 # Don't use set here. If one ligand has multiple identical
    #                 # fragments, I want them all listed.
    #                 frag_counts[entry_info.fragment_smiles] = 0
    #             frag_counts[entry_info.fragment_smiles] += 1
    #     return frag_counts

    def save_examples_used(self, model: pl.LightningModule, args: Namespace):
        """Save the examples used.

        Args:
            model (pl.LightningModule): The model.
            args (Namespace): The arguments parsed by argparse.
        """
        if args.default_root_dir is None:
            pth = os.getcwd() + os.sep
        else:
            pth = args.default_root_dir + os.sep

        if "train" in args.mode:
            torch.save(model.state_dict(), f"{pth}model_train_last.pt")
        elif args.mode == "warm_starting":
            torch.save(model.state_dict(), f"{pth}model_fine_tuned_last.pt")

        out_name = pth + os.sep + args.mode + ".actually_used.json"
        if not os.path.exists(out_name):
            examples_used = model.get_examples_actually_used()
            with open(out_name, "w") as f:
                json.dump(examples_used, f, indent=4)
