from pydantic import BaseModel, Field


class LinearDatasetConfig(BaseModel, frozen=True):
    num_points: int = 10
    slope: float = 0.5
    y_intercept: float = 0.5
    x_min: float = 0.0
    x_max: float = 1.0
    noise_type: str = ""
    noise_amplitude: float = Field(default=1.0, le=1.0, ge=0.0)
