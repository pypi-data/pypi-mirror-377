"""Runs DeepFrag2."""

import os
os.environ["NUMEXPR_MAX_THREADS"] = str(os.cpu_count())

import time
import torch
import logging
import pytorch_lightning as pl
from collagen.core.args import get_args
from collagen.apps.deepfrag.run import DeepFrag
from collagen.apps.deepfrag.model import DeepFragModel
from collagen.apps.deepfrag.run_multimodal_model import MultimodalDeepFrag
from collagen.apps.deepfrag.model_fusing_modalities import DeepFragModelESM2
from collagen.model_parents.moad_voxel.moad_voxel import VoxelModelParent
from collagen.apps.deepfrag.model_paired_data import DeepFragModelPairedDataFinetune
from collagen.external.common.datasets.fragment_dataset import FragmentDataset


class DeepFragFactory:

    @staticmethod
    def build_deepfrag_instance():
        """Build a DeepFrag instance according to the arguments."""

        df_args = get_args(
            parser_funcs=[
                VoxelModelParent.add_moad_args,
                DeepFragModel.add_model_args,
                DeepFragModelESM2.add_model_args,
                FragmentDataset.add_fragment_args,
            ],
            post_parse_args_funcs=[VoxelModelParent.fix_moad_args],
            is_pytorch_lightning=True,
        )

        if bool(df_args.run_mm_model):
            df_model = MultimodalDeepFrag(args=df_args)
        else:
            df_model = DeepFrag(
                args=df_args, 
                model_cls=DeepFragModelPairedDataFinetune if df_args.paired_data_csv else DeepFragModel,
            )

        return df_model, df_args

def main():
    numba_logger = logging.getLogger("numba")
    numba_logger.setLevel(logging.WARNING)

    thread_logger = logging.getLogger('thread_errors')
    thread_logger.setLevel(logging.ERROR)

    print("Hello DeepFrag")
    print("PyTorch", torch.__version__)
    print("PytorchLightning", pl.__version__)

    start_time = time.time()
    model, args = DeepFragFactory.build_deepfrag_instance()
    model.run(args)
    final_time = time.time()

    print(f"Successful DeepFrag execution in: {str(final_time - start_time)} seconds")

# if __name__ == "__main__":
