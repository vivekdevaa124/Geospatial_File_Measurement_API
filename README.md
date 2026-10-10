# Geospatial File Measurement API

This is a backend service built with **FastAPI** that accepts a geospatial file (Shapefile in `.zip` or `.kml`), processes the features within it, and returns measurement information. 

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repo_url>
   cd <repo_name>
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Run the application locally:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be accessible at `http://127.0.0.1:8000`. You can also view the interactive Swagger documentation at `http://127.0.0.1:8000/docs`.

## API

### 1. Upload File
- **Endpoint:** `POST /api/files/`
- **Description:** Uploads and processes a geospatial file (`.zip` or `.kml`).
- **Request Body:** `multipart/form-data` with a `file` field.
- **Example Request:**
  ```bash
  curl -X 'POST' \
    'http://127.0.0.1:8000/api/files/' \
    -H 'accept: application/json' \
    -H 'Content-Type: multipart/form-data' \
    -F 'file=@survey.kml'
  ```
- **Example Response:**
  ```json
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "filename": "survey.kml",
    "feature_count": 120,
    "crs": "EPSG:4326",
    "status": "COMPLETED"
  }
  ```

### 2. File Information
- **Endpoint:** `GET /api/files/{id}/`
- **Description:** Returns information about the uploaded file.
- **Example Response:**
  ```json
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "filename": "survey.kml",
    "feature_count": 120,
    "crs": "EPSG:4326",
    "status": "COMPLETED"
  }
  ```

### 3. Measurements
- **Endpoint:** `GET /api/files/{id}/measurements/`
- **Description:** Returns measurements for the features in the file.
- **Example Response:**
  ```json
  [
    {
      "feature_index": 0,
      "geometry_type": "Polygon",
      "geometry": "POLYGON ((...))",
      "properties": {"name": "Plot A"},
      "measurement_type": "Area",
      "measurement_value": 450.5,
      "measurement_unit": "square meters"
    }
  ]
  ```

## Architecture

- **Application Structure:** The application uses FastAPI for the API layer and SQLAlchemy as the ORM to interact with a SQLite database. Models, schemas, services, and API endpoints are logically separated into different modules within the `app` package.
- **File-processing Flow:** Uploaded files are temporarily saved to disk. `GeoPandas` (with the `pyogrio` engine) reads the `.zip` or `.kml` file. The features, geometry, and properties are extracted iteratively.
- **Measurement Calculation Flow:** For each feature, if the geometry is a Polygon/MultiPolygon, the area is calculated. If it's a LineString/MultiLineString, the length is calculated. Point geometries are skipped for measurements.
- **CRS Handling:** `GeoPandas` checks the coordinate reference system (CRS). If the coordinates are geographic (e.g., EPSG:4326), `estimate_utm_crs()` is used to reproject the data to an appropriate UTM coordinate system automatically before calculating the area or length to ensure accurate measurements in meters.

## Design Decisions

- **FastAPI:** Chosen for its performance, ease of use, automatic OpenAPI documentation, and modern Python type hinting support compared to Django.
- **GeoPandas & Pyogrio:** GeoPandas provides high-level geospatial operations. Pyogrio is used as the underlying I/O engine as it's faster and has more reliable installation across operating systems compared to Fiona, avoiding complex GDAL binary setup issues on Windows.
- **SQLite:** Used for data storage simplicity. Since this is an assignment, SQLite requires no extra setup and works perfectly for basic CRUD operations.
- **Synchronous Processing:** The current processing is handled synchronously. For production applications handling very large files, moving the file processing to a background task (using Celery or FastAPI BackgroundTasks) would prevent the upload request from timing out.
- **UTM CRS Estimation:** Used `estimate_utm_crs()` which calculates the centroid of the geometry and dynamically assigns the appropriate UTM Zone for highly accurate local distance/area calculations.

## Learning and Future Scope

- **Learnings:** Integrating `pyogrio` to gracefully handle KML and zipped Shapefiles without the heavy overhead of `fiona` on Windows was a key optimization.
- **Future Scope:** 
  - Offload geospatial processing to background workers (e.g., Celery, Redis).
  - Use PostGIS instead of SQLite for advanced geospatial querying capabilities.
  - Implement pagination for the `/measurements/` endpoint when returning large numbers of features.

  <img width="1907" height="872" alt="Screenshot 2026-10-10 225642" src="https://github.com/user-attachments/assets/82a0b3ac-3c95-4df2-9ed0-3edb9313f428" />
  <img width="1915" height="882" alt="Screenshot 2026-10-10 225656" src="https://github.com/user-attachments/assets/fc60a5d3-7bfe-457b-a057-985facd96e1c" />


