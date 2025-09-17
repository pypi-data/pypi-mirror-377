"""Functions required to split the MOAD into train, val, and test sets."""

import os
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple, Union

from collagen.external.common.parent_interface import ParentInterface
import numpy as np  # type: ignore
from collagen.util import sorted_list
import json
from collagen.external.common.butina_clustering_split import (
    generate_splits_using_butina_clustering,
)
from collagen.external.common.types import StructuresSplit


split_rand_num_gen: Union[np.random.Generator, None] = None


@dataclass
class SplitsPdbIds:

    """MOAD splits in terms of PDB IDs."""

    train: List
    val: List
    test: List


@dataclass
class SplitsSmiles:

    """Splits in terms of SMILES."""

    train: Set[str]
    val: Set[str]
    test: Set[str]


def _split_seq_per_probability(seq: List, p: float) -> Tuple[List, List]:
    """Divide a sequence according to a probability, p.

    Args:
        seq (List): Sequence to be divided.
        p (float): Probability of the first part.

    Returns:
        Tuple[List, List]: First and second parts of the sequence.
    """
    global split_rand_num_gen
    l = sorted_list(seq)
    size = len(l)

    if split_rand_num_gen is not None:
        split_rand_num_gen.shuffle(l)
    # np.random.shuffle(l)

    return l[: int(size * p)], l[int(size * p) :]


def _flatten(seq: List[List]) -> List:
    """Flatten a list of lists.

    Args:
        seq (List[List]): List of lists.

    Returns:
        List: Flattened list.
    """
    a = []
    for s in seq:
        a += s
    return a


def _random_divide_two_prts(
    seq: Union[Set[str], List[str]]
) -> Tuple[Set[str], Set[str]]:
    """Divide a sequence into two parts.

    Args:
        seq (Union[Set[str], List[str]]): Sequence to be divided.

    Returns:
        Tuple[List, List]: First and second parts of the sequence.
    """
    global split_rand_num_gen
    l = sorted_list(seq)  # To make deterministic is same seed used
    size = len(l)
    half_size = size // 2  # same as int(size / 2.0)

    if split_rand_num_gen is not None:
        split_rand_num_gen.shuffle(l)

    # np.random.shuffle(l)

    return (set(l[:half_size]), set(l[half_size:]))


def _random_divide_three_prts(
    seq: Union[Set[str], List[str]]
) -> Tuple[Set[str], Set[str], Set[str]]:
    """Divide a sequence into three parts.

    Args:
        seq (Union[Set[str], List[str]]): Sequence to be divided.

    Returns:
        Tuple[Set[str], Set[str], Set[str]]: First, second, and third parts of the sequence.
    """
    global split_rand_num_gen

    l = sorted_list(seq)
    size = len(l)

    if split_rand_num_gen is not None:
        split_rand_num_gen.shuffle(l)
    # np.random.shuffle(l)

    thid_size = size // 3
    return (
        set(l[:thid_size]),
        set(l[thid_size : thid_size * 2]),
        set(l[thid_size * 2 :]),
    )


def _smiles_for(data_interface: "ParentInterface", targets: List[str]) -> Set[str]:
    """Return all the SMILES strings contained in the selected targets.

    Args:
        data_interface (ParentInterface): ParentInterface object.
        targets (List[str]): List of targets.

    Returns:
        Set[str]: Set of SMILES strings.
    """
    smiles = set()

    for target in targets:
        for ligand in data_interface[target].ligands:
            smi = ligand.smiles
            if ligand.is_valid and smi not in ["n/a", "NULL"]:
                smiles.add(smi)

    return smiles


def _limit_split_size(
    max_pdbs_train: Optional[int],
    max_pdbs_val: Optional[int],
    max_pdbs_test: Optional[int],
    pdb_ids: SplitsPdbIds,
) -> SplitsPdbIds:
    # If the user has asked to limit the size of the train, test, or val set,
    # impose those limits here.

    if max_pdbs_train is not None and len(pdb_ids.train) > max_pdbs_train:
        pdb_ids.train = pdb_ids.train[:max_pdbs_train]

    if max_pdbs_val is not None and len(pdb_ids.val) > max_pdbs_val:
        pdb_ids.val = pdb_ids.val[:max_pdbs_val]

    if max_pdbs_test is not None and len(pdb_ids.test) > max_pdbs_test:
        pdb_ids.test = pdb_ids.test[:max_pdbs_test]

    return pdb_ids

# NOTE: Not used in the codebase
# def get_families_and_smiles(data_interface: "ParentInterface"):
#     families: List[List[str]] = []
#     for c in data_interface.classes:
#         families.extend(
#             [x.pdb_id for x in f.targets if x is not None] for f in c.families
#         )

#     smiles: List[List[str]] = [list(_smiles_for(data_interface, family)) for family in families]

#     return families, smiles


def _flatten_and_limit_pdb_ids(
    train_families,
    val_families,
    test_families,
    max_pdbs_train,
    max_pdbs_val,
    max_pdbs_test,
):
    # Now that they are divided, we can keep only the targets themselves (no
    # longer organized into families).
    pdb_ids = SplitsPdbIds(
        train=_flatten(train_families),
        val=_flatten(val_families),
        test=_flatten(test_families),
    )

    # If the user has asked to limit the size of the train, test, or val set,
    # impose those limits here.
    pdb_ids = _limit_split_size(
        max_pdbs_train,
        max_pdbs_val,
        max_pdbs_test,
        pdb_ids,
    )

    return pdb_ids

# NOTE: Note used
# def report_sizes(train_set, test_set, val_set):
#     print(f"Training set size: {len(train_set)}")
#     print(f"Testing set size: {len(test_set)}")
#     print(f"Validation set size: {len(val_set)}")

#     # Get the smiles in each of the sets
#     train_smiles = {complex["smiles"] for complex in train_set}
#     test_smiles = {complex["smiles"] for complex in test_set}
#     val_smiles = {complex["smiles"] for complex in val_set}

#     # Get the families in each of the sets
#     train_families = {complex["family_idx"] for complex in train_set}
#     test_families = {complex["family_idx"] for complex in test_set}
#     val_families = {complex["family_idx"] for complex in val_set}

#     # Verify that there is no overlap between the sets
#     print(f"Train and test overlap, SMILES: {len(train_smiles & test_smiles)}")
#     print(f"Train and val overlap: {len(train_smiles & val_smiles)}")
#     print(f"Test and val overlap, SMILES: {len(test_smiles & val_smiles)}")
#     print(f"Train and test overlap, families: {len(train_families & test_families)}")
#     print(f"Train and val overlap, families: {len(train_families & val_families)}")
#     print(f"Test and val overlap, families: {len(test_families & val_families)}")

#     # What is the number that were not assigned to any cluster?
#     # print(f"Number of complexes not assigned to any cluster: {len(data) - len(train_set) - len(test_set) - len(val_set)}")


def _generate_splits_from_scratch(
    data_interface: "ParentInterface",
    fraction_train: float = 0.6,
    fraction_val: float = 0.5,
    prevent_smiles_overlap: bool = True,
    max_pdbs_train: Optional[int] = None,
    max_pdbs_val: Optional[int] = None,
    max_pdbs_test: Optional[int] = None,
    split_method: str = "random",
    butina_cluster_cutoff: Optional[float] = 0.4,
):
    if split_method == "butina":
        # User must specify a butina_cluster_cutoff if using butina clustering.
        assert (
            butina_cluster_cutoff is not None
        ), "Must specify butina_cluster_cutoff if using butina split method."

        print("Building training/validation/test sets based on Butina clustering")
        (
            train_families,
            val_families,
            test_families,
        ) = generate_splits_using_butina_clustering(
            data_interface,
            split_rand_num_gen,
            fraction_train,
            fraction_val,
            butina_cluster_cutoff,
        )

        pdb_ids = _flatten_and_limit_pdb_ids(
            train_families,
            val_families,
            test_families,
            max_pdbs_train,
            max_pdbs_val,
            max_pdbs_test,
        )

        # Get all the ligand SMILES associated with the targets in each set.
        all_smis = SplitsSmiles(
            train=_smiles_for(data_interface, pdb_ids.train),
            val=_smiles_for(data_interface, pdb_ids.val),
            test=_smiles_for(data_interface, pdb_ids.test),
        )
    elif split_method in ["random", "random_default", "high_priority", "low_priority"]:
        print("Building training/validation/test sets")
        # Not loading previously determined splits from disk, so generate based
        # on random seed.

        # Make sure the user knows you can't use butina clustering with anything
        # but butina split method.
        assert (
            butina_cluster_cutoff is None
        ), "Butina clustering only works with butina split method. Either change the split method or remove the butina_cluster_cutoff argument."

        # First, get a flat list of all the families (not grouped by class).
        families: List[List[str]] = []
        for c in data_interface.classes:
            families.extend(
                [x.pdb_id for x in f.targets if x is not None] for f in c.families
            )

        # Note that we're working with families (not individual targets in those
        # families) so members of same family are not shared across train, val,
        # test sets.

        # Divide the families into train/val/test sets.
        train_families, other_families = _split_seq_per_probability(
            families, fraction_train
        )
        val_families, test_families = _split_seq_per_probability(
            other_families, fraction_val
        )

        pdb_ids = _flatten_and_limit_pdb_ids(
            train_families,
            val_families,
            test_families,
            max_pdbs_train,
            max_pdbs_val,
            max_pdbs_test,
        )

        # Get all the ligand SMILES associated with the targets in each set.
        all_smis = SplitsSmiles(
            train=_smiles_for(data_interface, pdb_ids.train),
            val=_smiles_for(data_interface, pdb_ids.val),
            test=_smiles_for(data_interface, pdb_ids.test),
        )

        if prevent_smiles_overlap:
            if split_method in ["random", "random_default"]:
                print("    Reassigning overlapping SMILES randomly")
                _randomly_reassign_overlapping_smiles(all_smis)
            elif split_method == "high_priority":
                print(
                    "    Reassigning overlapping SMILES by priority, favoring the training and validation sets"
                )
                _priority_reassign_overlapping_smiles(all_smis)
            else:  # it is low priority
                print(
                    "    Reassigning overlapping SMILES by priority, favoring the testing and validation sets"
                )
                _priority_reassign_overlapping_smiles(all_smis, False)
    else:
        # Throw error here.
        raise ValueError(f"Unknown split method: {split_method}")

    return pdb_ids, all_smis


def _randomly_reassign_overlapping_smiles(all_smis: SplitsSmiles):
    """
    Reassign overlapping SMILES randomly.

    Args:
        all_smis (SplitsSmiles): MOAD splits in terms of SMILES. Modified
            in place.
    """
    # Reassign overlapping SMILES.

    # Find the overlaps (intersections) between pairs of sets.
    train_val = all_smis.train & all_smis.val
    val_test = all_smis.val & all_smis.test
    train_test = all_smis.train & all_smis.test

    # Find the SMILES that are in two sets but not in the third one
    train_val_not_test = train_val - all_smis.test
    val_test_not_train = val_test - all_smis.train
    train_test_not_val = train_test - all_smis.val

    # Find SMILES that are present in all three sets
    train_test_val = all_smis.train & all_smis.val & all_smis.test

    # Overlapping SMILES are reassigned to temporary sets
    a_train, a_val = _random_divide_two_prts(train_val_not_test)
    b_val, b_test = _random_divide_two_prts(val_test_not_train)
    c_train, c_test = _random_divide_two_prts(train_test_not_val)
    d_train, d_val, d_test = _random_divide_three_prts(train_test_val)

    # Update SMILES sets to include the reassigned SMILES and exclude the
    # overlapping ones
    all_smis.train = (
        (all_smis.train - (all_smis.val | all_smis.test)) | a_train | c_train | d_train
    )
    all_smis.val = (
        (all_smis.val - (all_smis.train | all_smis.test)) | a_val | b_val | d_val
    )
    all_smis.test = (
        (all_smis.test - (all_smis.train | all_smis.val)) | b_test | c_test | d_test
    )


def _priority_reassign_overlapping_smiles(
    all_smis: SplitsSmiles, high_prior: bool = True
):
    """
    Reassign overlapping SMILES by priority.

    Args:
        all_smis (SplitsSmiles): MOAD splits in terms of SMILES. Modified
            in place.
        high_prior (bool, optional): If True, the training and validation sets
            will be favored. Otherwise, the testing and validation sets will be
            favored. Defaults to True.
    """
    # Reassign overlapping SMILES.

    # Find the overlaps (intersections) between pairs of sets.
    train_val = all_smis.train & all_smis.val
    train_test = all_smis.train & all_smis.test
    val_test = all_smis.val & all_smis.test

    # Calculated to verify reassignments
    size_overlap = len(all_smis.train) + len(all_smis.val) + len(all_smis.test)
    size_expected_non_overlap = len(all_smis.train | all_smis.val | all_smis.test)

    # Update SMILES sets
    if high_prior:
        # all_smis.train = all_smis.train
        all_smis.val = all_smis.val - train_val
        all_smis.test = all_smis.test - (train_test | val_test)
    else:
        all_smis.train = all_smis.train - (train_val | train_test)
        all_smis.val = all_smis.val - val_test
        # all_smis.test = all_smis.test

    size_non_overlap = len(all_smis.train) + len(all_smis.val) + len(all_smis.test)
    assert (size_non_overlap <= size_overlap) and (
        size_expected_non_overlap == size_non_overlap
    )
    print(f"Total number of SMILES with overlapping: {str(size_overlap)}")
    print(f"Total number of SMILES without overlapping: {str(size_non_overlap)}")


def _load_splits_from_disk(
    data_interface: "ParentInterface",
    load_splits: str,
    max_pdbs_train: Optional[int] = None,
    max_pdbs_val: Optional[int] = None,
    max_pdbs_test: Optional[int] = None,
) -> Tuple[SplitsPdbIds, SplitsSmiles, int]:
    """
    Load splits from disk.

    Args:
        data_interface (ParentInterface): MOADInterface object.
        load_splits (str): Path to the file containing the splits.
        max_pdbs_train (int, optional): Maximum number of PDBs in the training set.
            Defaults to None.
        max_pdbs_val (int, optional): Maximum number of PDBs in the validation set.

    Returns:
        Tuple[SplitsPdbIds, SplitsSmiles, int]: PDB IDs, SMILES, and the
            seed used to generate the splits.
    """
    # User has asked to load splits from file on disk. Get from the file.
    with open(load_splits) as f:
        split_inf = json.load(f)

    pdb_ids = SplitsPdbIds(
        train=split_inf["train"]["pdbs"],
        val=split_inf["val"]["pdbs"],
        test=split_inf["test"]["pdbs"],
    )

    # Reset seed just in case you also use save_splits. Not used.
    seed = split_inf["test"]

    if max_pdbs_train is None and max_pdbs_val is None and max_pdbs_test is None:
        # Load from cache
        all_smis = SplitsSmiles(
            train=set(split_inf["train"]["smiles"]),
            val=set(split_inf["val"]["smiles"]),
            test=set(split_inf["test"]["smiles"]),
        )

        return pdb_ids, all_smis, seed

    # If you get here, the user has asked to limit the number of pdbs in the
    # train/test/val set(s), so also don't get the smiles from the cache as
    # above.
    pdb_ids = _limit_split_size(
        max_pdbs_train,
        max_pdbs_val,
        max_pdbs_test,
        pdb_ids,
    )

    all_smis = SplitsSmiles(
        train=_smiles_for(data_interface, pdb_ids.train),
        val=_smiles_for(data_interface, pdb_ids.val),
        test=_smiles_for(data_interface, pdb_ids.test),
    )

    return pdb_ids, all_smis, seed


def _save_split(
    save_splits: str,
    seed: Optional[int],
    pdb_ids: SplitsPdbIds,
    all_smis: SplitsSmiles,
):
    """
    Save splits to disk.

    Args:
        save_splits (str): Path to the file where the splits will be saved.
        seed (int): Seed used to generate the splits.
        pdb_ids (SplitsPdbIds): PDB IDs.
        all_smis (SplitsSmiles): SMILES.
    """
    # Save spits and seed to json (for record keeping).
    split_inf = {
        "seed": seed,
        "unique_counts": {
            "train": {
                "pdbs": len(set(pdb_ids.train)),
                "frags": len(set(all_smis.train)),
            },
            "val": {
                "pdbs": len(set(pdb_ids.val)),
                "frags": len(set(all_smis.val)),
            },
            "test": {
                "pdbs": len(set(pdb_ids.test)),
                "frags": len(set(all_smis.test)),
            },
        },
        "train": {
            "pdbs": pdb_ids.train,
            "smiles": [smi for smi in all_smis.train],
        },
        "val": {"pdbs": pdb_ids.val, "smiles": [smi for smi in all_smis.val]},
        "test": {"pdbs": pdb_ids.test, "smiles": [smi for smi in all_smis.test]},
    }
    if not os.path.exists(os.path.dirname(save_splits)):
        os.mkdir(os.path.dirname(save_splits))
    with open(save_splits, "w") as f:
        json.dump(split_inf, f, indent=4)


def create_train_val_test_splits(
    dataset: ParentInterface,
    seed: Optional[int] = 0,
    fraction_train: float = 0.6,
    fraction_val: float = 0.5,
    prevent_smiles_overlap: bool = True,
    save_splits: Optional[str] = None,
    load_splits: Optional[str] = None,
    max_pdbs_train: Optional[int] = None,
    max_pdbs_val: Optional[int] = None,
    max_pdbs_test: Optional[int] = None,
    split_method: str = "random",  # random, butina
    butina_cluster_cutoff: Optional[float] = 0.4,
) -> Tuple["StructuresSplit", "StructuresSplit", "StructuresSplit"]:
    """Compute a TRAIN/VAL/TEST split.

    Targets are first assigned to a TRAIN set with `p_train` probability.
    The remaining targets are assigned to a VAL set with `p_val`
    probability. The unused targets are assigned to the TEST set.

    Args:
        seed (int, optional): If set to a nonzero number, compute_MOAD_split
            will always return the same split.
        fraction_train (float, optional): Fraction of training data. Defaults to 0.6.
        fraction_val (float, optional): Fraction of validation data. Defaults to 0.5.
        prevent_smiles_overlap (bool, optional): If True, overlapping SMILES
            between the sets will be reassigned. Defaults to True.
        save_splits (str, optional): If set, save the splits to this file.
            Defaults to None.
        load_splits (str, optional): If set, load the splits from this file.
            Defaults to None.
        max_pdbs_train (int, optional): Maximum number of PDBs in the training set.
            Defaults to None.
        max_pdbs_val (int, optional): Maximum number of PDBs in the validation set.
            Defaults to None.
        max_pdbs_test (int, optional): Maximum number of PDBs in the test set.
            Defaults to None.
        split_method (str, optional): Method to use for splitting the data into
            TRAIN/VAL/TEST sets. If 'random', the data will be partitioned randomly
            according to the specified fractions. If any fragments are present in
            more than one set, some will be randomly removed to ensure independence.
            If 'high_priority', duplicate fragments will be removed so as to favor
            the training set first, then the validation set (i.e., training and
            validation sets will be larger that user-specified fraction). If
            'low_priority', duplicate fragment will be removed so as to favor the
            test set, then the validation set (i.e., test and validation sets will
            be larger than the user-specified fraction). If 'butina', butina
            clustering will be used. Used only for finetuning. Defaults to 'random'.
        butina_cluster_cutoff (float, optional): Cutoff value to be applied for the
            Butina clustering method. Defaults to 0.4.

    Returns:
        Tuple[StructuresSplit, StructuresSplit, StructuresSplit]: train/val/test sets
    """
    if seed != 0 and seed is not None:
        global split_rand_num_gen
        split_rand_num_gen = np.random.default_rng(seed)

        # Note: Below also makes rotations and other randomly determined
        # aspects of the code deterministic. So using
        # np.random.default_rng(seed) instead.

        # np.random.seed(seed)

    # pdb_ids = SplitsPdbIds(None, None, None)
    # all_smis = SplitsSmiles(None, None, None)

    # train_pdb_ids = None
    # val_pdb_ids = None
    # test_pdb_ids = None
    # train_all_smis = None
    # val_all_smis = None
    # test_all_smis = None

    if load_splits is None:
        # Not loading previously determined splits from disk, so generate based
        # on random seed.
        pdb_ids, all_smis = _generate_splits_from_scratch(
            dataset,
            fraction_train,
            fraction_val,
            prevent_smiles_overlap,
            max_pdbs_train,
            max_pdbs_val,
            max_pdbs_test,
            split_method,
            butina_cluster_cutoff,
        )
    else:
        # User has asked to load splits from file on disk. Get from the file.
        pdb_ids, all_smis, seed = _load_splits_from_disk(
            dataset,
            load_splits,
            max_pdbs_train,
            max_pdbs_val,
            max_pdbs_test,
        )

    if save_splits is not None:
        # Save spits and seed to json (for record keeping).
        _save_split(save_splits, seed, pdb_ids, all_smis)

    print("\nSPLIT INFORMATION BEFORE FRAGMENTING/FILTERING")
    print(f"Training dataset size: {len(pdb_ids.train)}")
    print(f"Validation dataset size: {len(pdb_ids.val)}")
    print(f"Test dataset size: {len(pdb_ids.test)}")
    print("")

    return (
        StructuresSplit(name="TRAIN", targets=pdb_ids.train, smiles=all_smis.train),
        StructuresSplit(name="VAL", targets=pdb_ids.val, smiles=all_smis.val),
        StructuresSplit(name="TEST", targets=pdb_ids.test, smiles=all_smis.test),
    )


def create_full_dataset_as_single_split(data_interface: "ParentInterface") -> StructuresSplit:
    """
    Return a split containing all targets and smiles strings.

    Args:
        data_interface (ParentInterface): ParentInterface object.

    Returns:
        StructuresSplit: Split containing all targets and smiles strings.
    """
    pdb_ids, all_smis = _generate_splits_from_scratch(
        data_interface,
        fraction_train=1.0,
        fraction_val=0.0,
        prevent_smiles_overlap=True,
        max_pdbs_train=None,
        max_pdbs_val=None,
        max_pdbs_test=None,
        butina_cluster_cutoff=None,
    )

    return StructuresSplit(name="Full", targets=pdb_ids.train, smiles=all_smis.train)
