from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
from config import API_TITLE, API_VERSION, API_DESCRIPTION, FRONTEND_URL
from db import db
from detector import detector
import os

# ============ Pydantic Models =============
class CitizenReportCreate(BaseModel):
    billboard_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: str
    reporter_name: str
    reporter_email: str
    reporter_reputation: int = 0

class GeolocationData(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "US"

class ReportStatusUpdate(BaseModel):
    status: str  # pending, approved, resolved, flagged_by_citizens, rejected

# ============ FastAPI Setup =============
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ HEALTH & INFO =============
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Smart Billboard Compliance System",
        "version": API_VERSION
    }

@app.get("/api/info")
async def api_info():
    """Get API information and capabilities"""
    return {
        "title": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "features": [
            "Advanced Computer Vision for billboard text detection",
            "OCR-based violation keyword matching with confidence scoring",
            "Compliance monitoring against zoning laws",
            "Geolocation tracking with timestamp",
            "Citizen engagement and report validation",
            "Severity level assessment (Critical, High, Medium, Low)"
        ]
    }

# ============ IMAGE ANALYSIS =============
@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...), latitude: Optional[float] = None, longitude: Optional[float] = None):
    """
    Analyze billboard image for violations using advanced computer vision
    
    Features:
    - Text extraction via OCR with confidence scoring
    - Violation keyword detection
    - Severity level assessment
    - Text region localization
    - Geolocation tracking (optional)
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image
        image_data = await file.read()
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Advanced computer vision analysis
        analysis_result = detector.analyze_image(image_data)
        
        if not analysis_result.get("analysis_complete"):
            raise HTTPException(status_code=500, detail="Image analysis failed")
        
        # Upload image to storage
        filename = f"billboards/{uuid.uuid4()}_{file.filename}"
        await db.upload_image(image_data, filename)
        image_url = await db.get_image_url(filename)
        
        # Prepare comprehensive report
        report_data = {
            "image_url": image_url,
            "image_filename": filename,
            "extracted_text": analysis_result.get("extracted_text", ""),
            "is_compliant": analysis_result.get("is_compliant", True),
            "status": "pending",
            "violations_found": analysis_result.get("violations_found", []),
            "violation_count": analysis_result.get("violation_count", 0),
            "violation_context": analysis_result.get("violation_context", []),
            "ocr_confidence": analysis_result.get("ocr_confidence", 0.0),
            "severity_level": analysis_result.get("severity_level", "none"),
            "severity_score": analysis_result.get("severity_score", 0),
            "text_regions": analysis_result.get("text_regions", []),
            "detection_timestamp": analysis_result.get("detection_timestamp")
        }
        
        # Add geolocation if provided
        if latitude and longitude:
            report_data["latitude"] = latitude
            report_data["longitude"] = longitude
            
            # Check compliance with zoning laws
            location = {"latitude": latitude, "longitude": longitude}
            zoning_check = await db.check_zoning_compliance(location, report_data["violations_found"])
            report_data["zoning_compliance"] = zoning_check
        
        # Store report
        stored_report = await db.create_violation_report(report_data)
        
        return {
            "success": True,
            "report_id": stored_report.get("id") if stored_report else None,
            "image_url": image_url,
            "analysis": {
                "is_compliant": analysis_result.get("is_compliant"),
                "status": analysis_result.get("status"),
                "violations_found": analysis_result.get("violations_found"),
                "violation_count": analysis_result.get("violation_count"),
                "ocr_confidence": analysis_result.get("ocr_confidence"),
                "severity_level": analysis_result.get("severity_level"),
                "severity_score": analysis_result.get("severity_score"),
                "text_regions": analysis_result.get("text_regions"),
                "extracted_text": analysis_result.get("extracted_text")[:500] + "..." if len(analysis_result.get("extracted_text", "")) > 500 else analysis_result.get("extracted_text")
            },
            "message": f"{'Violation detected!' if not analysis_result.get('is_compliant') else 'No violations found.'}"
        }
    
    except Exception as e:
        print(f"Error analyzing image: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

# ============ REPORTS MANAGEMENT =============
@app.get("/api/reports")
async def get_reports(limit: int = Query(50, le=100), offset: int = Query(0)):
    """Get all violation reports with pagination"""
    try:
        reports = await db.get_violation_reports(limit, offset)
        return {
            "success": True,
            "data": reports,
            "count": len(reports),
            "message": f"Retrieved {len(reports)} reports"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """Get a specific violation report by ID"""
    try:
        report = await db.get_report_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return {
            "success": True,
            "data": report,
            "message": "Report retrieved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/reports/{report_id}/status")
async def update_report_status(report_id: str, status_update: ReportStatusUpdate):
    """Update report status (pending, approved, resolved, rejected)"""
    try:
        valid_statuses = ["pending", "approved", "resolved", "flagged_by_citizens", "rejected"]
        if status_update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        updated = await db.update_report_status(report_id, status_update.status)
        if not updated:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "success": True,
            "report_id": report_id,
            "new_status": status_update.status,
            "message": "Report status updated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ GEOLOCATION =============
@app.post("/api/geolocation/save")
async def save_billboard_location(location: GeolocationData, report_id: Optional[str] = None):
    """
    Save billboard location with GPS coordinates and metadata
    Enables spatial queries and nearby billboard detection
    """
    try:
        location_data = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "address": location.address,
            "city": location.city,
            "state": location.state,
            "country": location.country,
            "report_id": report_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        location_record = await db.save_billboard_location(location_data)
        
        return {
            "success": True,
            "location_id": location_record.get("id") if location_record else None,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "message": "Location saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/geolocation/nearby")
async def get_nearby_billboards(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(1.0, le=50.0)
):
    """
    Find billboards near a location within specified radius
    Uses Haversine formula for accurate distance calculation
    """
    try:
        billboards = await db.get_nearby_billboards(latitude, longitude, radius_km)
        return {
            "success": True,
            "query_location": {"latitude": latitude, "longitude": longitude},
            "radius_km": radius_km,
            "count": len(billboards),
            "billboards": billboards,
            "message": f"Found {len(billboards)} billboards within {radius_km}km"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ CITIZEN ENGAGEMENT =============
@app.post("/api/citizen-reports")
async def submit_citizen_report(citizen_report: CitizenReportCreate):
    """
    Submit a citizen violation report
    - Empowers citizens to report unauthorized billboards
    - Enables community validation and democratic compliance checking
    """
    try:
        report_data = {
            "billboard_id": citizen_report.billboard_id,
            "latitude": citizen_report.latitude,
            "longitude": citizen_report.longitude,
            "description": citizen_report.description,
            "reporter_name": citizen_report.reporter_name,
            "reporter_email": citizen_report.reporter_email,
            "reporter_reputation": citizen_report.reporter_reputation,
            "submitted_at": datetime.utcnow().isoformat(),
            "validated_by_count": 0,
            "status": "submitted"
        }
        
        submitted_report = await db.submit_citizen_report(report_data)
        
        return {
            "success": True,
            "report_id": submitted_report.get("id") if submitted_report else None,
            "billboard_id": citizen_report.billboard_id,
            "status": "submitted",
            "message": "Report submitted successfully. Other citizens can validate this report."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/citizen-reports")
async def get_citizen_reports(billboard_id: Optional[str] = None, limit: int = Query(50, le=100)):
    """
    Get citizen violation reports (optionally filtered by billboard)
    Shows community participation in compliance monitoring
    """
    try:
        reports = await db.get_citizen_reports(billboard_id, limit)
        return {
            "success": True,
            "count": len(reports),
            "reports": reports,
            "message": f"Retrieved {len(reports)} citizen reports"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/citizen-reports/{report_id}/validate")
async def validate_citizen_report(report_id: str, validator_id: str = Query(...)):
    """
    Validate a citizen report by voting for it
    Multiple validations auto-flag violation for faster admin review
    """
    try:
        validated = await db.validate_citizen_report(report_id, validator_id)
        
        if not validated:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "success": True,
            "report_id": report_id,
            "validator_id": validator_id,
            "message": "Report validation recorded. Community validation helps prioritize high-impact violations."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ COMPLIANCE MONITORING =============
@app.post("/api/compliance-check")
async def perform_compliance_check(location: GeolocationData, violations: List[str] = Query(...)):
    """
    Check billboard compliance with zoning laws at specific location
    Validates against permitted billboard database and city regulations
    """
    try:
        location_data = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "city": location.city,
            "state": location.state,
            "country": location.country
        }
        
        compliance = await db.check_zoning_compliance(location_data, violations)
        
        return {
            "success": True,
            "location": location_data,
            "violations_checked": violations,
            "is_compliant": compliance.get("is_compliant"),
            "zoning_info": compliance,
            "message": "Compliance check complete"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ DASHBOARD STATISTICS =============
@app.get("/api/statistics")
async def get_statistics():
    """
    Get comprehensive dashboard statistics
    Shows system health, violation trends, and citizen engagement metrics
    """
    try:
        stats = await db.get_statistics()
        return {
            "success": True,
            "statistics": {
                "total_reports": stats.get("total_reports", 0),
                "pending_reports": stats.get("pending", 0),
                "flagged_by_citizens": stats.get("flagged_by_citizens", 0),
                "resolved_reports": stats.get("resolved", 0),
                "reports_this_week": stats.get("this_week", 0),
                "citizen_reports_count": stats.get("citizen_reports_count", 0),
                "tracked_locations": stats.get("tracked_locations", 0),
                "average_severity": stats.get("avg_severity", 0)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Dashboard statistics retrieved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ ERROR HANDLING =============
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "message": str(exc.detail)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc)
        }
    )

# ============ ROOT ENDPOINT =============
@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "documentation": "/api/docs",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
