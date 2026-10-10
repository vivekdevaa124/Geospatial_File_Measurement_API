from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
import tempfile
import os

from . import models, schemas, database, services

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Geospatial File Measurement API")

@app.post("/api/files/", response_model=schemas.FileResponse)
def upload_file(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    if not file.filename.lower().endswith(('.zip', '.kml')):
        raise HTTPException(status_code=400, detail="Only .zip (Shapefile) or .kml files are supported.")
    
    try:
        fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(file.filename)[1])
        with os.fdopen(fd, 'wb') as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    
    file_record = services.process_geospatial_file(temp_path, file.filename, db)
    
    os.remove(temp_path)
    
    if file_record.status == "ERROR":
        raise HTTPException(status_code=400, detail="Error processing geospatial file. Ensure it is a valid Shapefile (.zip) or KML.")
        
    return file_record

@app.get("/api/files/{id}/", response_model=schemas.FileResponse)
def get_file_info(id: str, db: Session = Depends(database.get_db)):
    file_record = db.query(models.FileRecord).filter(models.FileRecord.id == id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    return file_record

@app.get("/api/files/{id}/measurements/", response_model=list[schemas.FeatureMeasurementResponse])
def get_file_measurements(id: str, db: Session = Depends(database.get_db)):
    file_record = db.query(models.FileRecord).filter(models.FileRecord.id == id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    measurements = db.query(models.FeatureMeasurement).filter(models.FeatureMeasurement.file_id == id).all()
    return measurements
