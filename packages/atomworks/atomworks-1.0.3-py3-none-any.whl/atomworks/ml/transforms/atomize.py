from typing import Any, ClassVar

import biotite.structure as struc
import numpy as np
from biotite.structure import AtomArray

from atomworks.ml.transforms._checks import (
    check_atom_array_annotation,
    check_contains_keys,
    check_is_instance,
    check_nonzero_length,
)
from atomworks.ml.transforms.base import Transform


class FlagNonPolymersForAtomization(Transform):
    """
    Flag all non-polymer residues for atomization.

    This is relevant for examples such as `6w12`, which have a protein residue
    outside of a polymer (e.g. an individual SER bonded to a sugar in `6w12`)
    """

    incompatible_previous_transforms: ClassVar[list[str | Transform]] = ["AtomizeByCCDName"]

    def check_input(self, data: dict[str, Any]) -> None:
        check_contains_keys(data, ["atom_array"])
        check_is_instance(data, "atom_array", AtomArray)
        check_nonzero_length(data, "atom_array")
        check_atom_array_annotation(data, required=["is_polymer"])

    def forward(self, data: dict[str, Any]) -> dict[str, Any]:
        atom_array = data["atom_array"]

        atomize = ~atom_array.is_polymer

        if "atomize" not in atom_array.get_annotation_categories():
            atom_array.set_annotation("atomize", atomize)
        else:
            atom_array.atomize |= atomize

        data["atom_array"] = atom_array
        return data


def _validate_atomize(atom_array: AtomArray, atomize: np.ndarray) -> None:
    """
    Validate that each residue is either atomized or not. Raises a ValueError if this is not the case.
    """
    _all = struc.apply_residue_wise(atom_array, atomize, np.all)
    _any = struc.apply_residue_wise(atom_array, atomize, np.any)
    if np.any(_all != _any):
        raise ValueError("For each residue, all atoms must be atomized or none must be atomized.")


def atomize_by_ccd_name(
    atom_array: AtomArray,
    atomize_by_default: bool = True,
    res_names_to_atomize: list[str] = [],
    res_names_to_ignore: list[str] = [],
    move_atomized_part_to_end: bool = False,
    validate_atomize: bool = False,
) -> AtomArray:
    """
    Atomize residues by breaking down the res_name field into the actual element names.

    Args:
        atom_array (AtomArray): The atom array to atomize.
        atomize_by_default (bool): Whether to atomize residues by default.
        res_names_to_atomize (list[str]): List of residue names to atomize. Defaults to [].
        res_names_to_ignore (list[str]): List of residue names to ignore. These residues
            will only be atomized, if their `atomize` flag is already explicitly set to `True`, e.g. from a
            previous transform to sample random residues for atomization for data augmentation. Defaults to [].
        move_atomized_part_to_end (bool, optional): Whether to move atomized parts to the end of the array. Defaults to False.
            This is relevant for RF2AA, which follows the convention that atomized parts are grouped together at the end of the
            input.
        validate_atomize (bool, optional): Whether to validate that a residue is either atomized or not. Defaults to False.

    Returns:
        AtomArray: The atomized atom array. The `atomize` flag is set for each atom in the array.
            NOTE: The returned array may be reordered if `move_atomized_part_to_end` is True.
    """
    atomize = np.full(len(atom_array), atomize_by_default, dtype=bool)

    # Exclude residues to ignore
    if len(res_names_to_ignore) > 0:
        atomize[np.isin(atom_array.res_name, res_names_to_ignore)] = False

    # Include residues to atomize
    if len(res_names_to_atomize) > 0:
        atomize[np.isin(atom_array.res_name, res_names_to_atomize)] = True

    # Include everything with the `atomize` flag from possible previous transforms
    #  this is used to manually define residues to atomize, e.g. as a data augmentation
    if "atomize" in atom_array.get_annotation_categories():
        atomize |= atom_array.atomize

    if validate_atomize:
        # ... validate that a residue is either atomized or not
        _validate_atomize(atom_array, atomize)

    # Perform atomization
    atom_array.set_annotation("atomize", atomize)

    if move_atomized_part_to_end:
        # as per RF2AA convention, the atomized parts are grouped together at the end
        #  of the input. This flag enables that.
        # NOTE: This needs to be done via `reshuffling` in order to preserve the correct
        #  bonding information.
        _idxs_pre_shuffling = np.arange(len(atom_array))
        reordered_idxs = np.concatenate(
            [_idxs_pre_shuffling[~atom_array.atomize], _idxs_pre_shuffling[atom_array.atomize]]
        )
        atom_array = atom_array[reordered_idxs]

    return atom_array


class AtomizeByCCDName(Transform):
    """Atomize residues by breaking down the CCD res_name field into the actual element names.

    NOTE: Both polymers AND non-polymers are considered "residues" by the CCD, and have a corresponding res_name.

    This transform allows for the atomization of residues in an AtomArray by breaking down the residue names into their
    constituent atoms. It provides options to atomize residues by default, specify residues to atomize or ignore, and
    move atomized parts to the end of the array. It must be run before any transforms that rely on the tokens established
    during atomization, such as `AddTokenBondAdjacency`.

    Attributes:
        - atomize_by_default (bool): Whether to atomize residues by default.
        - res_names_to_atomize (list[str]): List of residue names to atomize.
        - res_names_to_ignore (list[str]): List of residue names to ignore.
        - move_atomized_part_to_end (bool): Whether to move atomized parts to the end of the array.
            This is done e.g. in RF2AA, when atomizing polymer residues covalently bound to a ligand.

    Raises:
        ValueError: If a residue name appears in both `res_names_to_atomize` and `res_names_to_ignore`.
        ValueError: If some atoms in a residue are atomized and some are not.
    """

    incompatible_previous_transforms: ClassVar[list[str | Transform]] = [
        "AddTokenBondAdjacency",  # atomization changes the bond adjacency as some tokens are expaded into atoms
        "AddRF2AAChiralFeatures",  # chiral features depend on the atomized components since we need to calculate chirals for those
        "AddGlobalTokenIdAnnotation",  # atomization changes the token IDs
        "AtomizeByCCDName",  # cannot apply this transform twice
        "EncodeAtomArray",  # cannot encode atom array before atomizing as encoding may depend on atomization
    ]

    def __init__(
        self,
        atomize_by_default: bool,
        res_names_to_atomize: list[str] | None = None,
        res_names_to_ignore: list[str] | None = None,
        move_atomized_part_to_end: bool = False,
        validate_atomize: bool = False,
    ):
        """Initialize the AtomizeByCCDName transform.

        NOTE:
            - Residues are atomized if they have the `atomize` flag set to True.
            - Atoms in a given residue must either all be atomized or none be atomized (enforced by the transform).
            - If the `atomize` flag is already set to `True` for a residue, it will be atomized regardless of the
                `res_names_to_atomize` or `res_names_to_ignore` settings. This allows for manual definition of residues
                to atomize, e.g. for data augmentation.

        Args:
            atomize_by_default (bool): Whether to atomize residues by default.
            res_names_to_atomize (list[str], optional): List of residue names to atomize. Defaults to None.
            res_names_to_ignore (list[str] | None, optional): List of residue names to ignore. These residues
                will only be atomized, if their `atomize` flag is already explicitly set to `True`, e.g. from a
                previous transform to sample random residues for atomization for data augmentation. Defaults to None.
            move_atomized_part_to_end (bool, optional): Whether to move atomized parts to the end of the array. Defaults to False.
             This is relevant for RF2AA, which follows the convention that atomized parts are grouped together at the end of the
             input.
            validate_atomize (bool, optional): Whether to validate that a residue is either atomized or not. Defaults to False.

        Raises:
            ValueError: If a residue name appears in both `res_names_to_atomize` and `res_names_to_ignore`.
            ValueError: If some atoms in a residue are atomized and some are not.
        """
        self.validate_atomize = validate_atomize
        self.res_names_to_atomize = (
            np.asarray(res_names_to_atomize) if res_names_to_atomize is not None else np.array([])
        )
        self.res_names_to_ignore = np.asarray(res_names_to_ignore) if res_names_to_ignore is not None else np.array([])
        # Ensure that we do not try to atomize and ignore a residue name at the same time
        if np.any(np.isin(self.res_names_to_ignore, self.res_names_to_atomize)):
            raise ValueError("Cannot atomize and ignore the same residue name at the same time.")

        self.atomize_by_default = atomize_by_default
        self.move_atomized_part_to_end = move_atomized_part_to_end

    def check_input(self, data: dict[str, Any]) -> None:
        check_contains_keys(data, ["atom_array"])
        check_is_instance(data, "atom_array", AtomArray)
        check_nonzero_length(data, "atom_array")

    def forward(self, data: dict[str, Any]) -> dict[str, Any]:
        atom_array = data["atom_array"]

        atom_array = atomize_by_ccd_name(
            atom_array,
            atomize_by_default=self.atomize_by_default,
            res_names_to_atomize=self.res_names_to_atomize,
            res_names_to_ignore=self.res_names_to_ignore,
            move_atomized_part_to_end=self.move_atomized_part_to_end,
            validate_atomize=self.validate_atomize,
        )

        data["atom_array"] = atom_array
        return data
