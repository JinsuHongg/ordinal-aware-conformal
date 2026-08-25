"""Dataset adapters and immutable split-assignment utilities."""

from .flare import (
    build_ocqr_flare_manifest_audit,
    filter_ocqr_flare_rows,
    ocqr_flare_row_exclusion_masks,
)
from .surya_zarr import discover_surya_year_groups, open_surya_year_dataset
from .utkface import UTKFaceDataset

__all__ = [
    "UTKFaceDataset",
    "build_ocqr_flare_manifest_audit",
    "discover_surya_year_groups",
    "filter_ocqr_flare_rows",
    "ocqr_flare_row_exclusion_masks",
    "open_surya_year_dataset",
]
