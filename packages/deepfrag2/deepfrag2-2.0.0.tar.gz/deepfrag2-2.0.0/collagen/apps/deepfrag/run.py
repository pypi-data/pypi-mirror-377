"""Run DeepFrag."""

import argparse
from collagen.core.molecules.mol import BackedMol
from collagen.external.common.datasets.fragment_dataset import FragmentDataset
from collagen.external.common.types import StructureEntry
import torch  # type: ignore
import pytorch_lightning as pl  # type: ignore
from typing import final, Type
from typing import List, Sequence, Tuple, Union
from collagen import Mol, DelayedMolVoxel # , VoxelParams
from collagen.util import rand_rot
from collagen.model_parents import VoxelModelParent
import numpy as np

ENTRY_T = Tuple[Mol, Mol, BackedMol, str, int]
TMP_T = Tuple[DelayedMolVoxel, DelayedMolVoxel, torch.Tensor, StructureEntry]
OUT_T = Tuple[torch.Tensor, torch.Tensor, List[str]]


def _fingerprint_fn(args: argparse.Namespace, mol: BackedMol):
    return torch.tensor(mol.fingerprint(args.fragment_representation, args.fp_size))


class DeepFrag(VoxelModelParent):

    """DeepFrag model."""

    def __init__(self, args: argparse.Namespace, model_cls: Type[pl.LightningModule], dataset_cls: FragmentDataset = FragmentDataset):
        """Initialize the DeepFrag model parent.

        Args:
            args (Namespace): The arguments parsed by argparse.
            model_cls (Type[pl.LightningModule]): The model class. Soemthing
                like DeepFragModelSDFData or DeepFragModel.
            dataset_cls (FragmentDataset): The dataset class.
                Something like FragmentDataset.
        """
        super().__init__(args, model_cls=model_cls, dataset_cls=dataset_cls)

    @final
    def pre_voxelize(self, args: argparse.Namespace, entry: ENTRY_T) -> TMP_T:
        """Preprocess the entry before voxelization.
        
        Args:
            args (argparse.Namespace): The arguments parsed by argparse.
            entry (ENTRY_T): The entry to preprocess.
            
        Returns:
            TMP_T: The preprocessed entry.
        """
        rec, parent, frag, ligand_id, fragment_idx = entry

        # Random rotations, unless debugging voxels
        rot = np.array([1, 0, 0, 0]) if args.debug_voxels else rand_rot()

        center = frag.connectors[0]

        payload = self._get_payload(rec, parent, frag, ligand_id, fragment_idx, center)

        return (
            rec.voxelize_delayed(self.voxel_params, center=center, rot=rot, is_receptor=True),
            parent.voxelize_delayed(self.voxel_params, center=center, rot=rot, is_receptor=False),
            _fingerprint_fn(args, frag),
            payload,
        )

    def _get_payload(self, rec, parent, frag, ligand_id, fragment_idx, center):
        frag_smiles = frag.smiles(True)
        parent_smiles = parent.smiles(True)

        assert (
                frag_smiles is not None and parent_smiles is not None
        ), f"Fragment ({frag_smiles}) or parent ({parent_smiles}) SMILES is None"

        return StructureEntry(
            fragment_smiles=frag_smiles,
            parent_smiles=parent_smiles,
            receptor_name=rec.meta["name"],
            connection_pt=center,
            ligand_id=ligand_id,
            fragment_idx=fragment_idx,
        )

    @final
    def voxelize(self, args: argparse.Namespace, device: torch.device,
                 batch: Sequence[TMP_T], ) -> OUT_T:
        """Voxelize the batch.
        
        Args:
            args (argparse.Namespace): The arguments parsed by argparse.
            device (torch.device): The device to use.
            batch (List[TMP_T]): The batch to voxelize.
            
        Returns:
            OUT_T: The voxels, fingerprints, and fragment SMILES.
        """
        voxels = (
            torch.zeros(
                size=self.voxel_params.tensor_size(batch=len(batch), feature_mult=1),
                device=device,
            )
            if self.voxel_params.calc_voxels
            else None
        )

        fingerprints: Union[torch.Tensor, None] = (
            torch.zeros(size=(len(batch), args.fp_size), device=device)
            if self.voxel_params.calc_fps
            else None
        )

        frag_smis = []

        for i in range(len(batch)):
            rec, parent, frag, smi = batch[i]

            if self.voxel_params.calc_voxels:
                rec.voxelize_into(
                    voxels, batch_idx=i, layer_offset=0, cpu=(device.type == "cpu")
                )

                # atom_featurizer must not be None
                assert (
                    self.voxel_params.receptor_featurizer is not None
                ), "Receptor featurizer is None"

                assert(
                    self.voxel_params.ligand_featurizer is not None
                ), "Ligand featurizer is None"

                parent.voxelize_into(
                    voxels,
                    batch_idx=i,
                    layer_offset=self.voxel_params.receptor_featurizer.size(),
                    cpu=(device.type == "cpu")
                )

            if self.voxel_params.calc_fps:
                # Make sure fingerprint is not None
                assert fingerprints is not None, "Fingerprint tensor is None"
                fingerprints[i] = frag

            frag_smis.append(smi)

        return voxels, fingerprints, frag_smis
