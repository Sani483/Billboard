from supabase import create_client, Client
from config import (
    SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY,
    COMPLIANCE_TABLE, CITIZEN_REPORTS_TABLE, GEOLOCATION_TABLE,
    MIN_REPORTS_FOR_VALIDATION
)
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import uuid

class SupabaseDB:
    """Enhanced database layer with compliance monitoring, geolocation tracking, and citizen engagement"""
    
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.service_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # ============= IMAGE STORAGE =============
    async def upload_image(self, file_data: bytes, filename: str, bucket: str = "billboard-images"):
        """Upload image to Supabase Storage"""
        try:
            # Use service client for storage uploads to avoid RLS/permission issues
            response = self.service_client.storage.from_(bucket).upload(filename, file_data)
            return response
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None
    
    async def get_image_url(self, filename: str, bucket: str = "billboard-images"):
        """Get public URL of uploaded image"""
        try:
            url = self.client.storage.from_(bucket).get_public_url(filename)
            return url
        except Exception as e:
            print(f"Error getting image URL: {e}")
            return None
    
    # ============= VIOLATION REPORTS =============
    async def create_violation_report(self, report_data: dict):
        """Create a new violation report with full analysis data"""
        try:
            report_id = str(uuid.uuid4())
            report_data['id'] = report_id
            report_data['created_at'] = datetime.utcnow().isoformat()
            report_data['updated_at'] = datetime.utcnow().isoformat()
            # Ensure we only insert columns that exist in the schema to avoid cache/schema errors
            allowed_keys = {
                'id', 'image_url', 'image_filename', 'extracted_text', 'is_compliant',
                'status', 'violations_found', 'violation_count', 'violation_context',
                'ocr_confidence', 'severity_level', 'severity_score', 'text_regions',
                'latitude', 'longitude', 'zoning_compliance', 'detection_timestamp',
                'created_at', 'updated_at'
            }

            sanitized = {k: v for k, v in report_data.items() if k in allowed_keys}
            # Ensure status present
            sanitized.setdefault('status', 'pending')

            # Use service client for writes (bypass RLS where appropriate)
            response = self.service_client.table("violation_reports").insert(sanitized).execute()
            return response.data[0] if getattr(response, 'data', None) else None
        except Exception as e:
            print(f"Error creating report: {e}")
            return None
    
    async def get_violation_reports(self, limit: int = 50, offset: int = 0):
        """Get all violation reports with pagination"""
        try:
            response = (
                self.client.table("violation_reports")
                .select("*")
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching reports: {e}")
            return []
    
    async def get_report_by_id(self, report_id: str):
        """Get specific violation report by ID"""
        try:
            response = self.client.table("violation_reports").select("*").eq("id", report_id).single().execute()
            return response.data
        except Exception as e:
            print(f"Error fetching report: {e}")
            return None
    
    async def update_report_status(self, report_id: str, status: str):
        """Update report status (pending, approved, resolved, rejected)"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            response = self.client.table("violation_reports").update(update_data).eq("id", report_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating report: {e}")
            return None
    
    # ============= COMPLIANCE MONITORING =============
    async def check_zoning_compliance(self, location: Dict, violation_keywords: List[str]) -> Dict:
        """Check if location complies with zoning laws"""
        try:
            # Query zoning rules table for this location
            if 'latitude' in location and 'longitude' in location:
                lat, lon = location['latitude'], location['longitude']
                
                response = (
                    self.client.table(COMPLIANCE_TABLE)
                    .select("*")
                    .execute()
                )
                
                # Simple check: if any zoning rule matches
                zoning_violations = []
                for rule in response.data or []:
                    if self._check_location_in_zone(lat, lon, rule):
                        if any(kw in rule.get('restricted_keywords', '') for kw in violation_keywords):
                            zoning_violations.append(rule)
                
                return {
                    "compliant": len(zoning_violations) == 0,
                    "violations": zoning_violations,
                    "zone_info": response.data[0] if response.data else None
                }
            
            return {"compliant": True, "violations": [], "zone_info": None}
        except Exception as e:
            print(f"Error checking zoning compliance: {e}")
            return {"compliant": True, "violations": [], "zone_info": None}
    
    def _check_location_in_zone(self, lat: float, lon: float, zone: Dict) -> bool:
        """Simple location check (expand with actual geo-bounds logic)"""
        # Placeholder: check if location is within zone bounds
        return True
    
    async def log_compliance_check(self, report_id: str, check_data: Dict):
        """Log a compliance check result"""
        try:
            check_data['report_id'] = report_id
            check_data['check_timestamp'] = datetime.utcnow().isoformat()
            response = self.service_client.table(COMPLIANCE_TABLE).insert(check_data).execute()
            return response.data[0] if getattr(response, 'data', None) else None
        except Exception as e:
            print(f"Error logging compliance check: {e}")
            return None
    
    # ============= GEOLOCATION TRACKING =============
    async def save_billboard_location(self, location_data: Dict):
        """Save billboard location with geolocation data and timestamp"""
        try:
            location_data['id'] = str(uuid.uuid4())
            location_data['timestamp'] = datetime.utcnow().isoformat()
            location_data['created_at'] = datetime.utcnow().isoformat()
            response = self.service_client.table(GEOLOCATION_TABLE).insert(location_data).execute()
            return response.data[0] if getattr(response, 'data', None) else None
        except Exception as e:
            print(f"Error saving location: {e}")
            return None
    
    async def get_nearby_billboards(self, latitude: float, longitude: float, radius_km: float = 1.0) -> List[Dict]:
        """Get billboards within a specified radius (in kilometers)"""
        try:
            # Fetch all locations (in production, use PostGIS for efficient geo-queries)
            response = self.client.table(GEOLOCATION_TABLE).select("*").execute()
            
            nearby = []
            for location in response.data or []:
                if self._calculate_distance(
                    latitude, longitude,
                    location.get('latitude', 0),
                    location.get('longitude', 0)
                ) <= radius_km:
                    nearby.append(location)
            
            return nearby
        except Exception as e:
            print(f"Error fetching nearby billboards: {e}")
            return []
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers (Haversine formula)"""
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r
    
    # ============= CITIZEN ENGAGEMENT =============
    async def submit_citizen_report(self, citizen_report: Dict):
        """Submit a citizen violation report"""
        try:
            citizen_report['id'] = str(uuid.uuid4())
            citizen_report['submitted_at'] = datetime.utcnow().isoformat()
            citizen_report['status'] = 'pending'
            citizen_report['validated_by_count'] = 0
            citizen_report['reporter_reputation'] = citizen_report.get('reporter_reputation', 0)
            # Use service client to perform inserts (ensure permissions)
            response = self.service_client.table(CITIZEN_REPORTS_TABLE).insert(citizen_report).execute()
            
            # Auto-flag if multiple citizens report same location
            if response.data:
                await self._check_and_flag_violation(citizen_report.get('billboard_id'))
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error submitting citizen report: {e}")
            return None
    
    async def validate_citizen_report(self, citizen_report_id: str, validator_id: str) -> Dict:
        """Citizen validation of another's report (increases credibility)"""
        try:
            # Increment validation count
            response = (
                self.client.table(CITIZEN_REPORTS_TABLE)
                .select("validated_by_count")
                .eq("id", citizen_report_id)
                .single()
                .execute()
            )
            
            current_count = response.data.get('validated_by_count', 0) if response.data else 0
            
            update_response = (
                self.client.table(CITIZEN_REPORTS_TABLE)
                .update({"validated_by_count": current_count + 1})
                .eq("id", citizen_report_id)
                .execute()
            )
            
            return update_response.data[0] if update_response.data else None
        except Exception as e:
            print(f"Error validating citizen report: {e}")
            return None
    
    async def get_citizen_reports(self, billboard_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get citizen reports, optionally filtered by billboard"""
        try:
            query = self.client.table(CITIZEN_REPORTS_TABLE).select("*").order("submitted_at", desc=True)
            
            if billboard_id:
                query = query.eq("billboard_id", billboard_id)
            
            response = query.limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching citizen reports: {e}")
            return []
    
    async def _check_and_flag_violation(self, billboard_id: str):
        """Auto-flag violation if multiple citizen reports exist"""
        try:
            citizen_reports = await self.get_citizen_reports(billboard_id)
            
            if len(citizen_reports) >= MIN_REPORTS_FOR_VALIDATION:
                # Update original violation report status to "auto-flagged"
                await self.service_client.table("violation_reports").update({
                    "status": "flagged_by_citizens",
                    "citizen_validation_count": len(citizen_reports)
                }).eq("id", billboard_id).execute()
        except Exception as e:
            print(f"Error flagging violation: {e}")
    
    # ============= STATISTICS & DASHBOARD =============
    async def get_statistics(self) -> Dict:
        """Get comprehensive dashboard statistics"""
        try:
            reports = self.client.table("violation_reports").select("status, created_at").execute()
            citizen_reports = self.client.table(CITIZEN_REPORTS_TABLE).select("*").execute()
            locations = self.client.table(GEOLOCATION_TABLE).select("*").execute()
            
            data = reports.data or []
            total = len(data)
            pending = len([r for r in data if r.get("status") == "pending"])
            flagged = len([r for r in data if r.get("status") == "flagged_by_citizens"])
            resolved = len([r for r in data if r.get("status") == "resolved"])
            
            # This week
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            this_week = len([r for r in data if r.get("created_at", "") > week_ago])
            
            return {
                "total_reports": total,
                "pending": pending,
                "flagged_by_citizens": flagged,
                "resolved": resolved,
                "this_week": this_week,
                "citizen_reports_count": len(citizen_reports.data or []),
                "tracked_locations": len(locations.data or []),
                "avg_severity": self._calculate_avg_severity(data)
            }
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return {
                "total_reports": 0, "pending": 0, "flagged_by_citizens": 0,
                "resolved": 0, "this_week": 0, "citizen_reports_count": 0,
                "tracked_locations": 0, "avg_severity": 0
            }
    
    def _calculate_avg_severity(self, reports: List[Dict]) -> float:
        """Calculate average severity across reports"""
        if not reports:
            return 0.0
        
        severities = []
        severity_map = {"Critical": 9, "High": 6, "Medium": 4, "Low": 2, "None": 0}
        
        for report in reports:
            level = report.get("severity_level", "None")
            severities.append(severity_map.get(level, 0))
        
        return round(sum(severities) / len(severities), 2) if severities else 0.0

# Initialize database connection
db = SupabaseDB()
