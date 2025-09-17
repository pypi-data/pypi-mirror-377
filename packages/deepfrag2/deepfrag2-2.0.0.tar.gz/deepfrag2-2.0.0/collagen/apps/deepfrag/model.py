"""DeepFrag model."""

import argparse
from typing import List, Optional, Tuple

from collagen.external.common.types import StructureEntry
from collagen.metrics.metrics import mse_loss
from collagen.test.viz_debug import save_batch_first_item_channels
from torch import nn  # type: ignore
import pytorch_lightning as pl  # type: ignore
from collagen.apps.deepfrag.AggregationOperators import *
from collagen.metrics import cos_loss
import random


class DeepFragModel(pl.LightningModule):

    """DeepFrag model."""

    def __init__(self, num_voxel_features: int = 10, **kwargs):
        """Initialize the model.

        Args:
            num_voxel_features (int, optional): the number of features per
                voxel. Defaults to 10.
            **kwargs: additional keyword arguments.
        """
        super().__init__()

        self.fp_size = kwargs["fp_size"]

        # Need to keep track of whether it is a continuous fingerprint because
        # for continuous fingerprints better to use MSE (vs. cos sim) for loss
        # function.
        self.is_continuous_fingerprint = kwargs["fragment_representation"] in [
            "molbert",
            "molbert_shuffled",
        ]

        self.save_hyperparameters()
        self.aggregation = Aggregate1DTensor(operator=kwargs["aggregation_loss_vector"])
        self.learning_rate = float(kwargs["learning_rate"])
        self.predictions = None
        self.prediction_targets = None
        self.prediction_targets_entry_infos = None

        self.debug_voxels = kwargs["debug_voxels"] if "debug_voxels" in kwargs else False

        # Only record the examples used for the first epoch. After first epoch,
        # add to below to stop recording. Will eventually contain "train",
        # "val", and "test".
        self._examples_used_stop_recording = set([])
        self._examples_used = {"train": {}, "val": {}, "test": {}}

        # self.first_epoch = True

        self.encoder = nn.Sequential(
            # Rescale data (mean = 0, stdev = 1), per batch.
            nn.BatchNorm3d(num_voxel_features),
            # 3D convolution #1. Output has 64 channels. Each filter is 3x3.
            nn.Conv3d(num_voxel_features, 64, kernel_size=3),
            # Activation function. Output 0 if negative, same if positive.
            nn.ReLU(),
            # 3D convolution #2. Input/output: 64 channels. Each filter is 3x3.
            nn.Conv3d(64, 64, kernel_size=3),
            # Activation function. Output 0 if negative, same if positive.
            nn.ReLU(),
            # 3D convolution #3. Input/output: 64 channels. Each filter is 3x3.
            nn.Conv3d(64, 64, kernel_size=3),
            # Activation function. Output 0 if negative, same if positive.
            nn.ReLU(),
            # Takes max value for each 2x2 field.
            nn.MaxPool3d(kernel_size=2),
            # Rescale data (mean = 0, stdev = 1), per batch.
            nn.BatchNorm3d(64),
            # 3D convolution #4. Input/output: 64 channels. Each filter is 3x3.
            nn.Conv3d(64, 64, kernel_size=3),
            # Activation function. Output 0 if negative, same if positive.
            nn.ReLU(),
            # 3D convolution #5. Input/output: 64 channels. Each filter is 3x3.
            nn.Conv3d(64, 64, kernel_size=3),
            # Activation function. Output 0 if negative, same if positive.
            nn.ReLU(),
            # 3D convolution #6. Input/output: 64 channels. Each filter is 3x3.
            nn.Conv3d(64, 64, kernel_size=3),
            # Activation function. Output 0 if negative, same if positive.
            nn.ReLU(),
            # Calculate the average value of patches to get 1x1x1 output size.
            # nn.AdaptiveAvgPool3d((1, 1, 1)),
            Aggregate3x3Patches(
                operator=kwargs["aggregation_3x3_patches"], output_size=(1, 1, 1)
            ),
            # The dimension of the tensor here is (16, 64, 1, 1, 1)
            # Make the output a vector.
            nn.Flatten(),
            # Randomly zero some values
            nn.Dropout(),
            # Linear transform (fully connected). Increases features to 512.
            nn.Linear(64, 512),
            # Activation function. Output 0 if negative, same if positive.
            nn.ReLU(),
            # Here's your latent space?
        )

        # self.decoder = nn.Sequential(
        #     # Linear transform (fully connected). Increases features to 512.
        #     nn.Linear(512, 64),
        #
        #     # Activation function. Output 0 if negative, same if positive.
        #     nn.ReLU(),
        #
        #     # Reshapes vector to tensor.
        #     nn.Unflatten(1, (64, 1, 1, 1)),
        #
        #     # TODO: Linear layer somewhere here to get it into fragment space?
        #     # Or ReLU?
        #
        #     # Deconvolution #1
        #     nn.ConvTranspose3d(
        #         64, 64, kernel_size=3, stride=1, # padding=1, output_padding=1
        #     ),
        #     nn.ReLU(),
        #
        #     # Deconvolution #2
        #     nn.ConvTranspose3d(
        #         64, 64, kernel_size=3, stride=1, # padding=1, output_padding=1
        #     ),
        #     nn.ReLU(),
        #
        #     # Deconvolution #3
        #     nn.ConvTranspose3d(
        #         64, 64, kernel_size=3, stride=1, # padding=1, output_padding=1
        #     ),
        #     nn.ReLU(),
        #
        #     # Deconvolution #4
        #     nn.ConvTranspose3d(
        #         64, 64, kernel_size=3, stride=1, # padding=1, output_padding=1
        #     ),
        #     nn.ReLU(),
        #
        #     # nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
        #     nn.Upsample(scale_factor=2, mode='nearest'),
        #
        #     # Deconvolution #5
        #     nn.ConvTranspose3d(
        #         64, 64, kernel_size=3, stride=1, # padding=1, output_padding=1
        #     ),
        #     nn.ReLU(),
        #
        #     # Deconvolution #6
        #     nn.ConvTranspose3d(
        #         64, 64, kernel_size=3, stride=1, # padding=1, output_padding=1
        #     ),
        #     nn.ReLU(),
        #
        #     # Deconvolution #7
        #     nn.ConvTranspose3d(
        #         64, num_voxel_features, kernel_size=3, stride=1, # padding=1, output_padding=1
        #     ),
        #     nn.ReLU(),
        #
        #     # TODO: num_voxel_features includes receptor + ligand features. Not
        #     # the right one here. Needs to match however you calculate voxel
        #     # fragment.
        # )

        if self.is_continuous_fingerprint:
            self.deepfrag_after_encoder = nn.Sequential(
                # Randomly zero some values
                nn.Dropout(),
                # Linear transform (fully connected). Increases/Decreases
                # features to the --fp_size argument. It could generate negative
                # values
                # https://pytorch.org/docs/stable/generated/torch.nn.Linear.html
                nn.Linear(512, self.fp_size),
            )
        else:
            self.deepfrag_after_encoder = nn.Sequential(
                # Randomly zero some values
                nn.Dropout(),
                # Linear transform (fully connected). Increases/Decreases
                # features to the --fp_size argument. It could generate negative
                # values
                # https://pytorch.org/docs/stable/generated/torch.nn.Linear.html
                nn.Linear(512, self.fp_size),
                # Applies sigmoid activation function. See
                # https://pytorch.org/docs/stable/generated/torch.nn.Sigmoid.html
                # Values ranging between 0 and 1
                nn.Sigmoid(),
            )
        
        self.has_saved_some_debug_voxels = False

    def on_train_start(self):
        """Called when the actual training begins (after sanity check).
        This is a good place to reset the validation example tracking. The
        problem is the "Validation sanity check" step, which records only two
        batches worth of receptors. You want to record all the validation
        receptors for storage in the train_on_moad.actually_used.json file, so
        you must reset.
        """
        super().on_train_start()
        
        # Remove 'val' from the stop recording set if it was added during sanity check
        if 'val' in self._examples_used_stop_recording:
            self._examples_used_stop_recording.remove('val')
            # print("Reset validation example tracking after sanity check")
            
            # Also clear any validation examples recorded during sanity check
            if 'val' in self._examples_used:
                self._examples_used['val'] = {}

    @staticmethod
    def add_model_args(
        parent_parser: argparse.ArgumentParser,
    ) -> argparse.ArgumentParser:
        """Add model-specific arguments to the parser.
        
        Args:
            parent_parser (argparse.ArgumentParser): The parser to add to.
            
        Returns:
            argparse.ArgumentParser: The parser with model-specific arguments added.
        """
        # For many of these, good to define default values in args_defaults.py
        parser = parent_parser.add_argument_group("DeepFragModel")
        parser.add_argument(
            "--voxel_features",
            type=int,
            help="The number of voxel Features. Defaults to 10.",
            default=10,
        )
        parser.add_argument(
            "--fragment_representation",
            required=False,
            type=str,
            help="The type of fragment representations to be calculated: rdk10, rdk10_x_morgan, molbert",  # Intentionally leaving some off, like molbert_shuffled, which is for debugging.
        )  # , default="rdk10")
        parser.add_argument(
            "--aggregation_3x3_patches",
            required=False,
            type=str,
            help="The aggregation operator to be used to aggregate 3x3 patches. Defaults to Mean.",
        )  # , default=Operator.MEAN.value)
        parser.add_argument(
            "--aggregation_loss_vector",
            required=False,
            type=str,
            help="The aggregation operator to be used to aggregate loss values. Defaults to Mean.",
        )  # , default=Operator.MEAN.value)
        parser.add_argument(
            "--aggregation_rotations",
            required=False,
            type=str,
            help="The aggregation operator to be used to aggregate rotations. Defaults to Mean.",
        )  # , default=Operator.MEAN.value)
        parser.add_argument(
            "--save_fps",
            action="store_true",
            help="If given, predicted and calculated fingerprints will be saved in binary files during test mode.",
        )
        parser.add_argument(
            "--use_prevalence",
            action="store_true",
            help="If given, prevalence values are calculated and used during fine-tuning on paired data.",
        )
        return parent_parser

    def forward(self, voxel: torch.Tensor, entry_infos: Optional[List[StructureEntry]] = None) -> torch.Tensor:
        """Forward pass of the model.
        
        Args:
            voxel (torch.Tensor): The voxel grid.
            entry_infos: the information for each voxel
            
        Returns:
            torch.Tensor: The predicted fragment fingerprint.
        """
        latent_space = self.encoder(voxel)
        fps = self.deepfrag_after_encoder(latent_space)
        # frag_voxel = self.decoder(latent_space)
        return fps
        # return self.model(voxel)

    def configure_optimizers(self) -> torch.optim.Optimizer:
        """Configure the optimizer.

        Returns:
            torch.optim.Optimizer: The optimizer.
        """
        # https://stackoverflow.com/questions/42966393/is-it-good-learning-rate-for-adam-method
        # 3e-4 to 5e-4 are the best learning rates if you're learning the task
        # from scratch.

        return torch.optim.Adam(self.parameters(), lr=self.learning_rate)

    def loss(
        self,
        pred: torch.Tensor,
        fps: torch.Tensor,
        entry_infos: Optional[List[StructureEntry]],
        batch_size: Optional[int],
    ) -> torch.Tensor:
        """Calculate the loss.

        Args:
            pred (torch.Tensor): The predicted fragment fingerprint.
            fps (torch.Tensor): The ground truth fragment fingerprint.
            entry_infos (List[StructureEntry]): The entry information.
            batch_size (int): The batch size.

        Returns:
            torch.Tensor: The loss.
        """
        return (
            mse_loss(pred, fps)
            if self.is_continuous_fingerprint
            else self.aggregation.aggregate_on_pytorch_tensor(cos_loss(pred, fps))
        )

    def training_step(
        self, batch: Tuple[torch.Tensor, torch.Tensor, List[StructureEntry]], batch_idx: int
    ) -> torch.Tensor:
        """Training step.

        Args:
            batch (Tuple[torch.Tensor, torch.Tensor, List[StructureEntry]]): The
                batch to train on.
            batch_idx (int): The batch index.

        Returns:
            torch.Tensor: The loss.
        """
        voxels, fps, entry_infos = batch

        # if not os.path.exists("voxels_debug"):
        if self.debug_voxels and not self.has_saved_some_debug_voxels:
            for i in range(len(entry_infos)):
                save_batch_first_item_channels(
                    voxels[i],
                    entry_infos[i],
                    "voxels_debug_" + str(random.randint(0, 1000000)),
                )
            self.has_saved_some_debug_voxels = True

        pred = self(voxels, entry_infos)

        batch_size = voxels.shape[0]

        loss = self.loss(pred, fps, entry_infos, batch_size)

        # print("shape", cos_loss(pred, fps).shape)

        self._mark_example_as_used("train", entry_infos)

        # print("training_step")
        self.log("loss", loss, batch_size=batch_size)

        return loss

    # def on_train_epoch_end(self):
    #     if not self.first_epoch:
    #         return

    #     print("\nEnd first epoch. Saving fragment counts...\n")

    #     # Get the fragment counts from what's currently in self._examples_used
    #     for recep_name in self._examples_used["train"].keys():
    #         for frag in self._examples_used["train"][recep_name]:
    #             if frag not in self.fragment_counts_for_training:
    #                 self.fragment_counts_for_training[frag] = 0
    #             self.fragment_counts_for_training[frag] += 1

    #     # Convert self.fragment_counts_for_training to a list of tuples sorted
    #     # in descending order by second element
    #     fragment_counts_for_training_srted = sorted(
    #         self.fragment_counts_for_training.items(),
    #         key=lambda x: x[1],
    #         reverse=True
    #     )

    #     with open("fragment_counts_for_training.json", "w") as f:
    #         json.dump(fragment_counts_for_training_srted, f, indent=4)

    #     self.first_epoch = False

    def validation_step(
        self, batch: Tuple[torch.Tensor, torch.Tensor, List[StructureEntry]], batch_idx: int
    ):
        """Run validation step.

        Args:
            batch (Tuple[torch.Tensor, torch.Tensor, List[StructureEntry]]): The
                batch to validate on.
            batch_idx (int): The batch index.
        """
        voxels, fps, entry_infos = batch

        # print("::", voxels.shape, fps.shape, len(smis))

        pred = self(voxels, entry_infos)

        batch_size = voxels.shape[0]

        # loss = cos_loss(pred, fps).mean()
        loss = self.loss(pred, fps, entry_infos, batch_size)

        self._mark_example_as_used("val", entry_infos)

        # print("validation_step")
        self.log("val_loss", loss, batch_size=batch_size)

    def test_step(
        self, batch: Tuple[torch.Tensor, torch.Tensor, List[StructureEntry]], batch_idx: int
    ) -> Tuple[torch.Tensor, torch.Tensor, List[StructureEntry]]:
        """Run inferance on a given batch.

        Args:
            batch (Tuple[torch.Tensor, torch.Tensor, List[StructureEntry]]): The
                batch to run inference on.
            batch_idx (int): The batch index.

        Returns:
            Tuple[torch.Tensor, torch.Tensor, List[StructureEntry]]: The predicted
                and target fingerprints, and the entry infos.
        """
        voxels, fps, entry_infos = batch
        pred = self(voxels, entry_infos)

        batch_size = voxels.shape[0]

        # loss = cos_loss(pred, fps).mean()
        loss = self.loss(pred, fps, entry_infos, batch_size)

        self._mark_example_as_used("test", entry_infos)

        # print("test_step")
        self.log("test_loss", loss, batch_size=batch_size)

        # Drop (large) voxel input, return the predicted and target fingerprints.
        return pred, fps, entry_infos

    def training_epoch_end(self, outputs: List[dict]):
        """Run at the end of the training epoch with the outputs of all
            training steps. Logs the info.
        
        Args:
            outputs (List[dict]): List of outputs you defined in
                training_step(), or if there are multiple dataloaders, a list
                containing a list of outputs for each dataloader.
        """
        # with open("debug.txt", "a") as f: f.write(f"start training_epoch_end\n")

        self._examples_used_stop_recording.add("train")

        # See https://github.com/Lightning-AI/lightning/issues/2110
        try:
            # Sometimes x["loss"] is an empty TensorList. Not sure why. TODO:
            # Using try catch like this is bad practice.
            avg_loss = torch.stack([x["loss"] for x in outputs]).mean()
            self.log(
                "loss_per_epoch", {"avg_loss": avg_loss, "step": self.current_epoch + 1}
            )
        except Exception:
            self.log("loss_per_epoch", {"avg_loss": -1, "step": self.current_epoch + 1})

        # with open("debug.txt", "a") as f: f.write(f"end training_epoch_end\n")

    def validation_epoch_end(self, outputs: List[dict]):
        """Run at the end of the validation epoch with the outputs of all
            validation steps. Logs the info.
        
        Args:
            outputs (List[dict]): List of outputs you defined in
                validation_step(), or if there are multiple dataloaders, a
                list containing a list of outputs for each dataloader.
        """
        # with open("debug.txt", "a") as f: f.write(f"start validation_epoch_end\n")
        self._examples_used_stop_recording.add("val")

        # See https://github.com/Lightning-AI/lightning/issues/2110
        try:
            # Sometimes x["val_loss"] is an empty TensorList. Not sure why.
            # TODO: Using try catch like this is bad practice.
            avg_loss = torch.stack([x["val_loss"] for x in outputs]).mean()
            self.log(
                "val_loss_per_epoch",
                {"avg_loss": avg_loss, "step": self.current_epoch + 1},
            )
        except Exception:
            self.log(
                "val_loss_per_epoch", {"avg_loss": -1, "step": self.current_epoch + 1}
            )
        # with open("debug.txt", "a") as f: f.write(f"end validation_epoch_end\n")

    def test_epoch_end(
        self, results: List[Tuple[torch.Tensor, torch.Tensor, List[StructureEntry]]]
    ):
        """Run after inference has been run on all batches.

        Args:
            results (List[Tuple[torch.Tensor, torch.Tensor, List[StructureEntry]]]): The
                results from all batches.
        """
        # with open("debug.txt", "a") as f: f.write(f"start test_epoch_end\n")
        self._examples_used_stop_recording.add("test")

        predictions = torch.cat([x[0] for x in results])
        prediction_targets = torch.cat([x[1] for x in results])

        prediction_targets_entry_infos = []
        for x in results:
            prediction_targets_entry_infos.extend(x[2])

        # Sort so that order is always the same (for multiple rotations).
        keys_and_idxs_sorted = sorted(
            [
                (e.hashable_key(), i)
                for i, e in enumerate(prediction_targets_entry_infos)
            ],
            key=lambda x: x[0],
        )
        argsort_idx = [i for _, i in keys_and_idxs_sorted]

        prediction_targets_entry_infos = [
            prediction_targets_entry_infos[i] for i in argsort_idx
        ]

        argsort_idx_tnsr = torch.tensor(argsort_idx, device=predictions.device)

        torch.index_select(predictions.clone(), 0, argsort_idx_tnsr, out=predictions)

        torch.index_select(
            prediction_targets.clone(), 0, argsort_idx_tnsr, out=prediction_targets
        )

        # Save predictions, etc., so they can be accessed outside the model.
        self.predictions = predictions
        self.prediction_targets = prediction_targets
        self.prediction_targets_entry_infos = prediction_targets_entry_infos
        # with open("debug.txt", "a") as f: f.write(f"end test_epoch_end\n")

    def _mark_example_as_used(self, lbl: str, entry_infos: List[StructureEntry]):
        """Mark the example as used.

        Args:
            lbl (str): The label of the split.
            entry_infos (List[StructureEntry]): The entry infos.
        """
        if lbl in self._examples_used_stop_recording:
            # No longer recording for this label.
            return

        if entry_infos is not None:
            for entry_info in entry_infos:
                if entry_info.receptor_name not in self._examples_used[lbl]:
                    # Don't use set here. If one ligand has multiple identical
                    # fragments, I want them all listed.
                    self._examples_used[lbl][entry_info.receptor_name] = []
                self._examples_used[lbl][entry_info.receptor_name].append(
                    entry_info.fragment_smiles
                )

    def get_examples_actually_used(self) -> dict:
        """Get the examples used.

        Returns:
            dict: The examples used.
        """
        to_return = {"counts": {}}
        for split in self._examples_used:
            to_return[split] = {}
            frags_together = []
            for recep in self._examples_used[split].keys():
                frags = self._examples_used[split][recep]
                frags_together.extend(frags)
                to_return[split][recep] = list(frags)
            to_return["counts"][split] = {
                "receptors": len(self._examples_used[split].keys()),
                "fragments": {
                    "total": len(frags_together),
                    "unique": len(set(frags_together)),
                },
            }
        return to_return
