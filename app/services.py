import geopandas as gpd
import pyogrio
import os
import pandas as pd
from sqlalchemy.orm import Session
from . import models

def process_geospatial_file(file_path: str, original_filename: str, db: Session):
    try:
        engine = "pyogrio"
        if original_filename.lower().endswith('.zip'):
            gdf = gpd.read_file(f"zip://{file_path}", engine=engine)
        else:
            gdf = gpd.read_file(file_path, engine=engine)
        
        feature_count = len(gdf)
        crs = str(gdf.crs) if gdf.crs else "Unknown"

        file_record = models.FileRecord(
            filename=original_filename,
            feature_count=feature_count,
            crs=crs,
            status="COMPLETED"
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        projected_gdf = gdf
        if gdf.crs and gdf.crs.is_geographic:
            try:
                projected_gdf = gdf.to_crs(gdf.estimate_utm_crs())
            except Exception as e:
                print(f"Warning: Could not estimate UTM CRS: {e}")
        
        for index, row in gdf.iterrows():
            geom = row.geometry
            if geom is None or pd.isna(geom):
                continue

            geometry_type = geom.geom_type
            geometry_wkt = geom.wkt
            
            properties = {col: val for col, val in row.items() if col != 'geometry'}
            
            cleaned_properties = {}
            for k, v in properties.items():
                if pd.isna(v):
                    cleaned_properties[k] = None
                else:
                    if hasattr(v, "item"): 
                        cleaned_properties[k] = v.item()
                    else:
                        cleaned_properties[k] = v

            projected_geom = projected_gdf.loc[index, 'geometry']
            
            measurement_type = "None"
            measurement_value = None
            measurement_unit = None

            if geometry_type in ["Polygon", "MultiPolygon"]:
                measurement_type = "Area"
                measurement_value = projected_geom.area
                measurement_unit = "square meters"
            elif geometry_type in ["LineString", "MultiLineString"]:
                measurement_type = "Length"
                measurement_value = projected_geom.length
                measurement_unit = "meters"
            
            feature_record = models.FeatureMeasurement(
                file_id=file_record.id,
                feature_index=int(index) if not pd.isna(index) else 0,
                geometry_type=geometry_type,
                geometry=geometry_wkt,
                properties=cleaned_properties,
                measurement_type=measurement_type,
                measurement_value=measurement_value,
                measurement_unit=measurement_unit
            )
            db.add(feature_record)
        
        db.commit()
        return file_record
    
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        file_record = models.FileRecord(
            filename=original_filename,
            feature_count=0,
            crs="Unknown",
            status="ERROR"
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        return file_record
