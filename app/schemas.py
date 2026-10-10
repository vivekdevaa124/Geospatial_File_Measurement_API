from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class FileResponse(BaseModel):
    id: str
    filename: str
    feature_count: int
    crs: str
    status: str

    model_config = {"from_attributes": True}

class FeatureMeasurementResponse(BaseModel):
    feature_index: int
    geometry_type: str
    geometry: str
    properties: Dict[str, Any]
    measurement_type: str
    measurement_value: Optional[float]
    measurement_unit: Optional[str]

    model_config = {"from_attributes": True}
