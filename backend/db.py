from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY
import json
from datetime import datetime

class SupabaseDB:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.service_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    async def upload_image(self, file_data: bytes, filename: str, bucket: str = "billboard-images"):
        """Upload image to Supabase Storage"""
        try:
            response = self.client.storage.from_(bucket).upload(filename, file_data)
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
    
    async def create_violation_report(self, report_data: dict):
        """Create a new violation report in database"""
        try:
            response = self.client.table("violation_reports").insert(report_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating report: {e}")
            return None
    
    async def get_violation_reports(self, limit: int = 50):
        """Get all violation reports"""
        try:
            response = self.client.table("violation_reports").select("*").limit(limit).order("created_at", desc=True).execute()
            return response.data
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
        """Update report status (pending, approved, rejected)"""
        try:
            response = self.client.table("violation_reports").update({"status": status, "updated_at": datetime.utcnow().isoformat()}).eq("id", report_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating report: {e}")
            return None
    
    async def get_statistics(self):
        """Get dashboard statistics"""
        try:
            reports = self.client.table("violation_reports").select("status").execute()
            total = len(reports.data)
            pending = len([r for r in reports.data if r["status"] == "pending"])
            resolved = len([r for r in reports.data if r["status"] == "resolved"])
            
            return {
                "total_reports": total,
                "pending": pending,
                "resolved": resolved,
                "this_week": pending  # Simplified for demo
            }
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return {"total_reports": 0, "pending": 0, "resolved": 0, "this_week": 0}

# Initialize database connection
db = SupabaseDB()
