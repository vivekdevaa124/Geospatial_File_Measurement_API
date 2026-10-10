from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class FileRecord(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    filename = Column(String, index=True)
    feature_count = Column(Integer)
    crs = Column(String)
    status = Column(String)

    measurements = relationship("FeatureMeasurement", back_populates="file")


class FeatureMeasurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = Column(String, ForeignKey("files.id"))
    feature_index = Column(Integer)
    geometry_type = Column(String)
    geometry = Column(String)
    properties = Column(JSON)
    measurement_type = Column(String)
    measurement_value = Column(Float, nullable=True)
    measurement_unit = Column(String, nullable=True)

    file = relationship("FileRecord", back_populates="measurements")
