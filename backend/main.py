from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime
from config import API_TITLE, API_VERSION, API_DESCRIPTION, FRONTEND_URL
from db import db
from detector import detector
import os

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

# ============ Health Check ============
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Smart Billboard Compliance API"
    }

# ============ Image Analysis Endpoints ============
@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze billboard image for violations
    - Extracts text using OCR
    - Detects violation keywords
    - Stores result in database
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image file
        image_data = await file.read()
        
        # Analyze image
        analysis_result = detector.analyze_image(image_data)
        
        if not analysis_result["success"]:
            raise HTTPException(status_code=500, detail="Analysis failed")
        
        # Generate unique filename
        filename = f"billboards/{uuid.uuid4()}_{file.filename}"
        
        # Upload image to Supabase
        await db.upload_image(image_data, filename)
        image_url = await db.get_image_url(filename)
        
        # Prepare report data
        detection_data = analysis_result["data"]
        report_data = {
            "image_url": image_url,
            "image_filename": filename,
            "extracted_text": detection_data["extracted_text"],
            "is_compliant": detection_data["is_compliant"],
            "status": "pending",  # Will be reviewed by admin
            "violations_found": detection_data["violations_found"],
            "violation_count": detection_data["violation_count"],
            "violation_context": detection_data["violation_context"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Store in database
        stored_report = await db.create_violation_report(report_data)
        
        return {
            "success": True,
            "report_id": stored_report["id"] if stored_report else None,
            "analysis": detection_data,
            "message": "Image analyzed successfully"
        }
    
    except Exception as e:
        print(f"Error in analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

# ============ Dashboard Endpoints ============
@app.get("/api/reports")
async def get_reports(limit: int = 50):
    """Get all violation reports for dashboard"""
    reports = await db.get_violation_reports(limit)
    return {
        "success": True,
        "count": len(reports),
        "reports": reports
    }

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """Get specific report by ID"""
    report = await db.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "success": True,
        "report": report
    }

@app.patch("/api/reports/{report_id}/status")
async def update_report_status(report_id: str, status: str):
    """Update report status (pending, approved, rejected)"""
    valid_statuses = ["pending", "approved", "rejected", "resolved"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
    
    updated_report = await db.update_report_status(report_id, status)
    if not updated_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "success": True,
        "report": updated_report,
        "message": f"Report status updated to {status}"
    }

# ============ Statistics Endpoints ============
@app.get("/api/statistics")
async def get_statistics():
    """Get dashboard statistics"""
    stats = await db.get_statistics()
    return {
        "success": True,
        "statistics": stats
    }

# ============ Root Endpoint ============
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Smart Billboard Compliance API",
        "version": API_VERSION,
        "docs": "/api/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
