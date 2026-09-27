from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ultralytics import YOLO

from pathlib import Path
from PIL import Image
import piexif
import datetime
import json
import os
import shutil
import tempfile

import numpy as np
import rasterio
from rasterio.mask import mask as raster_mask
from rasterio.warp import transform_geom

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
yolo_model = YOLO(str(BASE_DIR / "yolov8n.pt"))

# ============================================================
# DHARA DRISHTI
# Geospatial Watershed Monitoring & Decision Support System
# ============================================================

app = FastAPI(
    title="DHARA DRISHTI API",
    description="Geospatial Watershed Monitoring & Decision Support System",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

RECORDS_FILE = DATA_DIR / "field_records.json"


# ============================================================
# INITIALIZE FIELD RECORD DATABASE
# ============================================================

if not RECORDS_FILE.exists():
    RECORDS_FILE.write_text("[]", encoding="utf-8")


def load_records():
    try:
        return json.loads(
            RECORDS_FILE.read_text(encoding="utf-8")
        )
    except Exception:
        return []


def save_records(records):
    RECORDS_FILE.write_text(
        json.dumps(records, indent=2),
        encoding="utf-8"
    )


# ============================================================
# GPS HELPERS
# ============================================================

def convert_to_decimal(coordinate, ref):

    degrees = coordinate[0][0] / coordinate[0][1]
    minutes = coordinate[1][0] / coordinate[1][1]
    seconds = coordinate[2][0] / coordinate[2][1]

    decimal = degrees + minutes / 60 + seconds / 3600

    if ref in [b"S", b"W"]:
        decimal = -decimal

    return decimal


def extract_gps(image_path):

    try:

        image = Image.open(image_path)

        exif_data = image.info.get("exif")

        if not exif_data:
            return None

        exif_dict = piexif.load(exif_data)

        gps = exif_dict.get("GPS", {})

        latitude = gps.get(
            piexif.GPSIFD.GPSLatitude
        )

        latitude_ref = gps.get(
            piexif.GPSIFD.GPSLatitudeRef
        )

        longitude = gps.get(
            piexif.GPSIFD.GPSLongitude
        )

        longitude_ref = gps.get(
            piexif.GPSIFD.GPSLongitudeRef
        )

        if not latitude or not longitude:
            return None

        if not latitude_ref or not longitude_ref:
            return None

        latitude = convert_to_decimal(
            latitude,
            latitude_ref
        )

        longitude = convert_to_decimal(
            longitude,
            longitude_ref
        )

        return {
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6)
        }

    except Exception as e:

        print("GPS extraction error:", e)

        return None


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "project": "DHARA DRISHTI",
        "status": "Backend is running",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "DHARA DRISHTI API"
    }


# ============================================================
# FIELD IMAGE UPLOAD
# ============================================================

@app.post("/upload-field-image")
async def upload_field_image(
    file: UploadFile = File(...)
):

    allowed_types = [
        "image/jpeg",
        "image/jpg",
        "image/png"
    ]

    if file.content_type not in allowed_types:

        return {
            "status": "error",
            "message": "Only JPG, JPEG and PNG images are allowed."
        }


    # Make filename safe enough for prototype use
    filename = Path(file.filename).name

    file_path = UPLOAD_DIR / filename


    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    gps = extract_gps(file_path)


    return {

        "status": "success",

        "filename": filename,

        "gps_available": gps is not None,

        "gps": gps,

        "image_url": f"/uploads/{filename}",

        "message":
            "Field image uploaded successfully."
            if gps
            else
            "Field image uploaded successfully, but no GPS metadata was found."
    }


# ============================================================
# CREATE FIELD OBSERVATION
# ============================================================

@app.post("/field-observation")
async def create_field_observation(

    file: UploadFile = File(...),

    description: str = Form(""),

    intervention_type: str = Form("")

):

    allowed_types = [
        "image/jpeg",
        "image/jpg",
        "image/png"
    ]

    if file.content_type not in allowed_types:

        return {
            "status": "error",
            "message": "Only JPG, JPEG and PNG images are allowed."
        }


    filename = Path(file.filename).name

    timestamp = datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    stored_filename = (
        f"{timestamp}_{filename}"
    )

    file_path = UPLOAD_DIR / stored_filename


    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    gps = extract_gps(file_path)


    records = load_records()


    record_id = len(records) + 1


    record = {

        "id": record_id,

        "filename": stored_filename,

        "description": description,

        "intervention_type": intervention_type,

        "gps": gps,

        "gps_available": gps is not None,

        "uploaded_at":
            datetime.datetime.now().isoformat(),

        "status": "verified"
        if gps
        else "gps_missing"
    }


    records.append(record)

    save_records(records)


    return {

        "status": "success",

        "message": "Field observation recorded successfully.",

        "record": record
    }


# ============================================================
# GET ALL FIELD OBSERVATIONS
# ============================================================

@app.get("/field-observations")
def get_field_observations():

    records = load_records()

    return {

        "status": "success",

        "count": len(records),

        "records": records
    }


# ============================================================
# GET SINGLE FIELD OBSERVATION
# ============================================================

@app.get("/field-observation/{record_id}")
def get_field_observation(record_id: int):

    records = load_records()

    for record in records:

        if record["id"] == record_id:

            return {
                "status": "success",
                "record": record
            }


    return {
        "status": "error",
        "message": "Field observation not found."
    }


# ============================================================
# WATERSHED ANALYSIS
# ============================================================

@app.get("/watershed-analysis")
def watershed_analysis():

    return {

        "watershed": "Murredu Watershed",

        "status": "analysis_available",

        "layers": {

            "ndvi": {
                "name": "Vegetation Health",
                "file": "ndvi.png"
            },

            "water": {
                "name": "Water Bodies",
                "file": "water.png"
            },

            "drainage": {
                "name": "Drainage Network",
                "file": "drainage.png"
            },

            "slope": {
                "name": "Slope",
                "file": "slope.png"
            },

            "erosion": {
                "name": "Erosion Susceptibility",
                "file": "erosion.png"
            },

            "lulc": {
                "name": "Land Use / Land Cover",
                "file": "lulc.png"
            },

            "health": {
                "name": "Watershed Health",
                "file": "health.png"
            },

            "intervention": {
                "name": "Intervention Priority",
                "file": "intervention.png"
            }
        }
    }


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

@app.get("/dashboard-stats")
def dashboard_stats():

    return {

        "watershed": "Murredu Watershed",

        "area_km2": 1593.33,

        "vegetation": {

            "dense_percent": 26.33,

            "moderate_percent": 54.18
        },

        "water": {

            "coverage_percent": 1.25,

            "estimated_area_km2": 49.30
        },

        "erosion": {

            "very_low_percent": 56.22,

            "low_percent": 35.55,

            "moderate_percent": 6.64,

            "high_percent": 1.59
        },

        "watershed_health": {

            "mean_score": 0.5794
        },

        "intervention_priority": {

            "vegetation_restoration_percent": 2.77,

            "erosion_control_percent": 3.16,

            "water_conservation_percent": 1.59,

            "high_priority_percent": 4.12
        },

        "change_detection": {

            "period": "2023 to 2026",

            "vegetation_gain_percent": 10.90,

            "vegetation_loss_percent": 64.11,

            "stable_percent": 24.99
        }
    }


# ============================================================
# PRIORITY AREAS
# ============================================================

@app.get("/priority-areas")
def priority_areas():

    return {

        "status": "success",

        "priorities": [

            {
                "priority": "Vegetation Restoration",

                "percentage": 2.77,

                "reason":
                    "Low vegetation condition combined with low watershed health."
            },

            {
                "priority": "Erosion Control",

                "percentage": 3.16,

                "reason":
                    "Higher erosion susceptibility and terrain conditions."
            },

            {
                "priority": "Water Conservation",

                "percentage": 1.59,

                "reason":
                    "Lower watershed health with relatively lower slope."
            },

            {
                "priority": "High Priority Multi-Factor",

                "percentage": 4.12,

                "reason":
                    "Combination of poor health, erosion susceptibility and higher slope."
            }
        ]
    }


# ============================================================
# CHANGE DETECTION
# ============================================================
# Stable SIH-demo implementation.
#
# The project already has a processed 2023 -> 2026 NDVI result.
# We intentionally do NOT call an external Sentinel-2/STAC service
# from the demo API, so Change Detection remains reliable offline.
# ============================================================

MURREDU_BOUNDARY_FILE = DATA_DIR / "Murredu_Watershed.geojson"


def _load_murredu_geometry():
    if not MURREDU_BOUNDARY_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Murredu watershed boundary is not generated yet.",
                "action": "Run generate_murredu_boundary.py once using the local Murredu DEM."
            }
        )

    data = json.loads(MURREDU_BOUNDARY_FILE.read_text(encoding="utf-8"))

    if data.get("type") == "FeatureCollection":
        return data["features"][0]["geometry"], data["features"][0].get("properties", {})

    if data.get("type") == "Feature":
        return data["geometry"], data.get("properties", {})

    return data, {}


@app.get("/change-detection")
def change_detection(before: str, after: str, threshold: float = 0.10):
    """
    Stable comparison of the project's processed Murredu watershed
    change-detection result.

    Supported processed dates:
      before = 2023-11-11
      after  = 2026-03-05

    The values are from the already processed project analysis and
    are deliberately not recomputed from an external online service.
    """

    try:
        before_dt = datetime.datetime.strptime(before, "%Y-%m-%d")
        after_dt = datetime.datetime.strptime(after, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Dates must use YYYY-MM-DD format."
        )

    if before_dt >= after_dt:
        raise HTTPException(
            status_code=400,
            detail="Before date must be earlier than after date."
        )

    if not (0.01 <= threshold <= 0.50):
        raise HTTPException(
            status_code=400,
            detail="Threshold must be between 0.01 and 0.50 NDVI."
        )

    # The project has one validated demo comparison currently available.
    if before != "2023-11-11" or after != "2026-03-05":
        raise HTTPException(
            status_code=400,
            detail={
                "message": "This demo currently supports the processed comparison "
                           "11 Nov 2023 to 5 Mar 2026.",
                "supported_before": "2023-11-11",
                "supported_after": "2026-03-05"
            }
        )

    # Verify that the exact Murredu boundary is available.
    _, boundary_props = _load_murredu_geometry()

    # These are the project's existing processed change-detection results.
    before_mean = 0.45495245
    after_mean = 0.30805

    gain_pct = 10.90
    loss_pct = 64.11
    stable_pct = 24.99

    return {
        "status": "success",
        "period": {
            "requested_before": before,
            "requested_after": after,
            "before_date": "2023-11-11",
            "after_date": "2026-03-05",
            "before_label": "11 Nov 2023",
            "after_label": "5 Mar 2026"
        },
        "scenes": {
            "before_id": "S2B_44QME_20231111_0_L2A",
            "after_id": "S2C_44QME_20260305_0_L2A",
            "before_cloud_percent": 0.008301,
            "after_cloud_percent": 0.000082
        },
        "boundary": {
            "name": "Murredu Watershed",
            "area_km2": boundary_props.get("area_km2", 1593.33),
            "source": boundary_props.get(
                "source",
                "DEM hydrological delineation"
            )
        },
        "ndvi": {
            "before_mean": round(before_mean, 4),
            "after_mean": round(after_mean, 4),
            "mean_change": round(after_mean - before_mean, 4)
        },
        "metrics": {
            "vegetation_gain_percent": gain_pct,
            "vegetation_loss_percent": loss_pct,
            "stable_percent": stable_pct,
            "total_changed_percent": round(gain_pct + loss_pct, 2),
            "net_change_percentage_points": round(gain_pct - loss_pct, 2),
            "ndvi_change_threshold": threshold,
            "valid_pixels": None
        },
        "note": (
            "Project prototype change detection for the Murredu watershed, "
            "based on the processed Sentinel-2 L2A comparison for "
            "11 Nov 2023 and 5 Mar 2026. Gain/loss percentages are "
            "pixel proportions from the project's existing analysis. "
            "The result is not recalculated from an external online service "
            "during the demo."
        )
    }


@app.get("/murredu-boundary")
def murredu_boundary():
    geometry, props = _load_murredu_geometry()
    return {
        "status": "success",
        "boundary": geometry,
        "properties": props
    }


# ============================================================
# WATERSHED HEALTH
# ============================================================

@app.get("/watershed-health")
def watershed_health():

    return {

        "status": "success",

        "mean_score": 0.5794,

        "components": {

            "vegetation": 0.40,

            "water": 0.20,

            "erosion": 0.25,

            "slope": 0.15
        },

        "interpretation":
            "Prototype composite watershed health indicator."
    }


# ============================================================
# API INFORMATION
# ============================================================

@app.get("/api-info")
def api_info():

    return {

        "project": "DHARA DRISHTI",

        "modules": [

            "Field Image Upload",

            "GPS Extraction",

            "Field Observation Management",

            "Watershed Analysis",

            "Dashboard Statistics",

            "Priority Area Identification",

            "Change Detection",

            "Watershed Health"
        ],

        "api_version": "1.0.0"
    }

@app.post("/ai-analyze")
async def ai_analyze(file: UploadFile = File(...)):
    """
    Run YOLOv8 inference on an uploaded field image.
    """

    temp_path = UPLOAD_DIR / f"ai_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        results = yolo_model.predict(
            source=str(temp_path),
            conf=0.25,
            verbose=False
        )

        detections = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                detections.append({
                    "class_id": class_id,
                    "class_name": yolo_model.names[class_id],
                    "confidence": round(confidence, 3)
                })

        return {
            "success": True,
            "model": "YOLOv8n",
            "detections": detections,
            "detection_count": len(detections)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if temp_path.exists():
            temp_path.unlink()
