"""KDI Transformer with NaN."""

from __future__ import annotations

from typing import Any

import numpy as np
import torch
from sklearn.preprocessing import (
    PowerTransformer,
)

try:
    from kditransform import KDITransformer

    # This import fails on some systems, due to problems with numba
except ImportError:
    KDITransformer = PowerTransformer  # fallback to avoid error


ALPHAS = (
    0.05,
    0.1,
    0.2,
    0.25,
    0.3,
    0.4,
    0.5,
    0.6,
    0.8,
    1.0,
    1.2,
    1.5,
    1.8,
    2.0,
    2.5,
    3.0,
    5.0,
)


class KDITransformerWithNaN(KDITransformer):
    """KDI transformer that can handle NaN values. It performs KDI with NaNs replaced by
    mean values and then fills the NaN values with NaNs after the transformation.
    """

    def _more_tags(self) -> dict:
        return {"allow_nan": True}

    def fit(
        self,
        X: torch.Tensor | np.ndarray,
        y: Any | None = None,
    ) -> KDITransformerWithNaN:
        """Fit the transformer."""
        if isinstance(X, torch.Tensor):
            X = X.cpu().numpy()

        X = np.nan_to_num(X, nan=np.nanmean(X, axis=0))
        return super().fit(X, y)  # type: ignore

    def transform(self, X: torch.Tensor | np.ndarray) -> np.ndarray:
        """Transform the data."""
        # if tensor convert to numpy
        if isinstance(X, torch.Tensor):
            X = X.cpu().numpy()

        # Calculate the NaN mask for the current dataset
        nan_mask = np.isnan(X)

        # Replace NaNs with the mean of columns
        imputation = np.nanmean(X, axis=0)
        imputation = np.nan_to_num(imputation, nan=0)
        X = np.nan_to_num(X, nan=imputation)

        # Apply the transformation
        X = super().transform(X)

        # Reintroduce NaN values based on the current dataset's mask
        X[nan_mask] = np.nan

        return X  # type: ignore


def get_all_kdi_transformers() -> dict[str, KDITransformerWithNaN]:
    """Get all KDI transformers."""
    try:
        all_preprocessors = {
            "kdi": KDITransformerWithNaN(alpha=1.0, output_distribution="normal"),
            "kdi_uni": KDITransformerWithNaN(
                alpha=1.0,
                output_distribution="uniform",
            ),
        }
        for alpha in ALPHAS:
            all_preprocessors[f"kdi_alpha_{alpha}"] = KDITransformerWithNaN(
                alpha=alpha,
                output_distribution="normal",
            )
            all_preprocessors[f"kdi_alpha_{alpha}_uni"] = KDITransformerWithNaN(
                alpha=alpha,
                output_distribution="uniform",
            )
        return all_preprocessors
    except Exception:  # noqa: BLE001
        return {}


__all__ = [
    "KDITransformerWithNaN",
    "get_all_kdi_transformers",
]
