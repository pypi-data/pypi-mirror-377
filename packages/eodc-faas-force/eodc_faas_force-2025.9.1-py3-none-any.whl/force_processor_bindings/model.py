import logging
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class ForceResMergeOptions(Enum):
    IMPROPHE = "IMPROPHE"
    REGRESSION = "REGRESSION"
    STARFM = "STARFM"
    NONE = "NONE"

    def __str__(self) -> str:
        """This is so that the template substitution puts in
        the value, without the enum name"""
        return str(self.value)


class ForceParameters(BaseModel):
    """Pydantic model of force supported parameters."""

    stac_url: Optional[str] = None
    collection_id: Optional[str] = None

    # Specify bounding box in Lon/Lat.
    bbox: Optional[Union[tuple[float, ...], list[float], str]] = None

    # datetime needs to be formatted as required by
    # https://pystac-client.readthedocs.io/en/latest/api.html#pystac_client.Client.search
    datetime: Optional[str] = None
    input_files: list[str] = Field(default_factory=list)
    user_workspace: Path
    dem_file: str
    dem_nodata: int = Field(default=-9999)
    do_atmo: bool = Field(default="TRUE")
    do_topo: bool = Field(default="TRUE")
    do_brdf: bool = Field(default="TRUE")
    adjacency_effect: bool = Field(default="TRUE")
    multi_scattering: bool = Field(default="TRUE")
    erase_clouds: bool = Field(default="TRUE")
    max_cloud_cover_frame: int = Field(default=90, ge=0, le=100)
    max_cloud_cover_tile: int = Field(default=90, ge=0, le=100)
    cloud_buffer: float = Field(default=300, ge=0, le=10000)
    cirrus_buffer: float = Field(default=0, ge=0, le=10000)
    shadow_buffer: float = Field(default=90, ge=0, le=10000)
    snow_buffer: float = Field(default=30, ge=0, le=10000)
    cloud_threshold: float = Field(default=0.225, ge=0, le=1)
    shadow_threshold: float = Field(default=0.02, ge=0, le=1)
    res_merge: ForceResMergeOptions = Field(default=ForceResMergeOptions.IMPROPHE)

    @field_validator(
        "adjacency_effect",
        "do_atmo",
        "do_brdf",
        "do_topo",
        "multi_scattering",
        "erase_clouds",
    )
    @classmethod
    def bool_to_force_string(cls, v: bool):
        # This is necessary, because the FORCE processor
        # actually needs to take in all-caps strings, not bools.
        return "TRUE" if v is True else "FALSE"

    @property
    def force_path(self) -> Path:
        return self.user_workspace / "FORCE"

    @property
    def temp_dir(self) -> Path:
        return self.force_path / "temp"

    @property
    def output_dir(self) -> Path:
        return self.force_path / "output"

    @property
    def logs_dir(self) -> Path:
        return self.force_path / "log"

    def node_log_dir(self, node_id) -> Path:
        return self.logs_dir / f"node_{node_id}"

    @property
    def configs_dir(self) -> Path:
        return self.temp_dir / "configs"

    def node_config_file(self, node_id) -> Path:
        return self.configs_dir / f"node_{node_id}.prm"

    def node_temp_dir(self, node_id) -> Path:
        return self.temp_dir / f"node_{node_id}"

    @property
    def dir_provenance(self) -> Path:
        return self.force_path / "provenance"

    @property
    def stac_output_dir(self) -> Path:
        return self.output_dir / "STAC"

    @property
    def stac_output_items_dir(self) -> Path:
        return self.stac_output_dir / "items"
