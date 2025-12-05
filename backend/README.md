# Smart Billboard Compliance Backend

FastAPI backend for the Smart Billboard Compliance Detection System with Supabase integration.

## Features

- 🖼️ **Image Upload & Analysis**: Upload billboard images for violation detection
- 🔍 **OCR Text Extraction**: Extract text from images using Tesseract
- 🚨 **Violation Detection**: Detect prohibited keywords in billboard content
- 💾 **Supabase Integration**: Store images and reports in Supabase
- 📊 **Real-time Dashboard**: Track violations in real-time
- 🔐 **CORS Support**: Secure frontend integration

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- pip (Python package manager)
- Tesseract OCR installed on your system
- Supabase account

### 2. Install Tesseract OCR

**Windows:**
```bash
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 3. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Setup Supabase

1. Go to [Supabase](https://supabase.com) and create a new project
2. Create the following table structure:

**Table: `violation_reports`**
```sql
CREATE TABLE violation_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  image_url TEXT,
  image_filename TEXT,
  extracted_text TEXT,
  is_compliant BOOLEAN,
  status TEXT DEFAULT 'pending',
  violations_found TEXT[] DEFAULT '{}',
  violation_count INTEGER DEFAULT 0,
  violation_context TEXT[] DEFAULT '{}',
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);
```

3. Create a Storage bucket named `billboard-images`

### 6. Configure Environment

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Fill in your Supabase credentials:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
VIOLATION_KEYWORDS=nude,adult,gambling,alcohol,tobacco,drugs,weapons
FRONTEND_URL=http://localhost:5174
```

### 7. Run the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/api/docs`
- Health Check: `http://localhost:8000/api/health`

## API Endpoints

### Health Check
- **GET** `/api/health` - Check API status

### Image Analysis
- **POST** `/api/analyze` - Analyze billboard image
  - Upload image file
  - Returns analysis results and stores report

### Reports
- **GET** `/api/reports` - Get all violation reports
- **GET** `/api/reports/{report_id}` - Get specific report
- **PATCH** `/api/reports/{report_id}/status` - Update report status

### Statistics
- **GET** `/api/statistics` - Get dashboard statistics

## Example Usage

### Analyze Image
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "accept: application/json" \
  -F "file=@/path/to/billboard.jpg"
```

Response:
```json
{
  "success": true,
  "report_id": "uuid",
  "analysis": {
    "is_compliant": false,
    "status": "Unauthorized",
    "violations_found": ["adult", "gambling"],
    "violation_count": 2,
    "extracted_text": "..."
  }
}
```

### Get Reports
```bash
curl -X GET "http://localhost:8000/api/reports?limit=50"
```

### Update Report Status
```bash
curl -X PATCH "http://localhost:8000/api/reports/{report_id}/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'
```

## Project Structure

```
backend/
├── main.py              # FastAPI application & endpoints
├── config.py            # Configuration settings
├── db.py                # Supabase database integration
├── detector.py          # Violation detection logic
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── .env                 # Environment variables (git ignored)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Violation Keywords

Default keywords checked for violations:
- nude
- adult
- gambling
- alcohol
- tobacco
- drugs
- weapons

Customize in `.env` file:
```
VIOLATION_KEYWORDS=keyword1,keyword2,keyword3
```

## Frontend Integration

Connect from frontend using API:

```javascript
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  body: formData
});

const result = await response.json();
```

## Troubleshooting

### Tesseract not found
- Ensure Tesseract is installed and added to PATH
- Set environment variable: `PYTESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe` (Windows)

### Supabase connection errors
- Verify `.env` file has correct credentials
- Check Supabase project is active
- Ensure network connectivity

### CORS errors
- Verify `FRONTEND_URL` in `.env` matches frontend origin
- Check CORS middleware configuration in `main.py`

## Development

For development with auto-reload:

```bash
pip install uvicorn
uvicorn main:app --reload
```

## License

MIT License

## Support

For issues or questions, please create an issue in the repository.
