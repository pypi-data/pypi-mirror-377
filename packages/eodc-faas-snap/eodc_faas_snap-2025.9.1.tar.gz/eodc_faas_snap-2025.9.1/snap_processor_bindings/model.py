import logging
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DEM(BaseModel):
    filepath: Path
    nodata: Any
    ellipsoid_height: bool


class SnapCorrectionCoefficient(Enum):
    SIGMA0 = "sigma0"
    GAMMA0 = "gamma0"
    BETA0 = "beta0"


class SnapCorrectionMethod(Enum):
    TERRAIN = "terrain-correction"
    ELLIPSOID = "ellipsoid-correction"


class SnapParameters(BaseModel):
    """Pydantic model of snap supported parameters."""

    input_files: list[str]
    user_workspace: Path
    correction_coefficient: SnapCorrectionCoefficient = Field(
        default=SnapCorrectionCoefficient.GAMMA0
    )
    correction_method: SnapCorrectionMethod = Field(
        default=SnapCorrectionMethod.TERRAIN
    )
    dem: Optional[DEM] = Field(default=None)
    save_incidence_angle: bool = Field(default=False)

    @property
    def root_path(self):
        return self.user_workspace / "SNAP"

    @property
    def outputs_path(self) -> Path:
        return self.root_path / "outputs"

    @property
    def stac_path(self) -> Path:
        return self.outputs_path / "STAC"

    @property
    def stac_items_path(self) -> Path:
        return self.stac_path / "items"
