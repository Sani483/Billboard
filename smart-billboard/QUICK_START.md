# Smart Billboard - Final Setup Steps

Now that you have created your Supabase project, follow these steps to get everything running:

## ⚡ Quick Summary of What You Need to Do

1. **Create database table in Supabase** (SQL)
2. **Create storage bucket in Supabase** (for images)
3. **Copy credentials to backend .env file**
4. **Install dependencies and test**
5. **Run backend and frontend servers**
6. **Test the system**

---

## Step 1: Create Database Table

### In Your Browser:

1. Open Supabase Dashboard: https://supabase.com
2. Click your **smart-billboard** project
3. In left sidebar, click **SQL Editor**
4. Click **New Query** (top right)
5. **Delete** any existing code
6. **Copy-paste** this entire SQL:

```sql
CREATE TABLE IF NOT EXISTS violation_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  image_url TEXT,
  image_filename TEXT,
  extracted_text TEXT,
  is_compliant BOOLEAN DEFAULT true,
  violations_found TEXT[] DEFAULT '{}',
  violation_count INTEGER DEFAULT 0,
  violation_context TEXT[] DEFAULT '{}',
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_created_at ON violation_reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_status ON violation_reports(status);
```

7. Click **Run** (top right)
8. You should see: ✅ "Success!"

---

## Step 2: Create Storage Bucket

### In Your Browser:

1. In left sidebar, click **Storage**
2. Click **Create a new bucket** (blue button)
3. **Bucket name**: `billboard-images`
4. Choose **Public** (so images can be shown)
5. Click **Create bucket**

---

## Step 3: Get Your API Credentials

### In Your Browser:

1. In left sidebar, click **Settings** → **API**
2. Look at the page - you'll see:
   - **Project URL** (under "URLs" section)
   - **Anon Key** (under "Project API keys")
   - **Service Role Key** (under "Project API keys")

Copy these three values. They look like:
- URL: `https://xxxxx.supabase.co`
- Keys: Long strings starting with `eyJ...`

---

## Step 4: Fill in Your .env File

### In File Explorer:

1. Navigate to: `C:\Users\Lenovo\Desktop\BillBoard av\smart-billboard\backend`
2. Right-click `.env.example` → **Open with Notepad**
3. You'll see:
```
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here
FRONTEND_URL=http://localhost:5174
```

4. Replace the values:
   - `SUPABASE_URL` → paste your Project URL
   - `SUPABASE_KEY` → paste your Anon Key
   - `SUPABASE_SERVICE_KEY` → paste your Service Role Key

5. **Save As** (Ctrl+Shift+S) as `.env` (same folder, change filename from `.env.example` to `.env`)
6. Close Notepad

**Example (with fake credentials):**
```
SUPABASE_URL=https://myproject123.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im15cHJvamVjdDEyMyIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNzAxNjAwMDAwLCJleHAiOjE4NjQzNjAwMDB9.ABC123...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im15cHJvamVjdDEyMyIsInJvbGUiOiJzZXJ2aWNlX3JvbGUiLCJpYXQiOjE3MDE2MDAwMDAsImV4cCI6MTg2NDM2MDAwMH0.XYZ789...
FRONTEND_URL=http://localhost:5174
```

---

## Step 5: Install Tesseract OCR

Open **PowerShell** and run:

### Option A: Using Chocolatey (Recommended)
```powershell
choco install tesseract
```

### Option B: Manual Download
1. Visit: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the installer
3. Run it and choose default installation path
4. Restart your computer

Verify installation:
```powershell
tesseract --version
```

---

## Step 6: Test Supabase Connection

### In PowerShell:

```powershell
# Navigate to backend folder
cd "C:\Users\Lenovo\Desktop\BillBoard av\smart-billboard\backend"

# Activate virtual environment
venv\Scripts\activate

# Run test script
python test_supabase.py
```

You should see:
```
✓ SUPABASE_URL: https://xxx.supabase.co
✓ SUPABASE_KEY: eyJ...
⏳ Connecting to Supabase...
✓ Connected successfully!
✓ Table exists! Current records: 0
✓ Storage bucket exists!
✅ All checks passed! Ready to use.
```

If you see errors, check your `.env` file credentials.

---

## Step 7: Run the Application

### Terminal 1 - Backend Server:

```powershell
cd "C:\Users\Lenovo\Desktop\BillBoard av\smart-billboard\backend"
.\run.bat
```

Wait until you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 - Frontend Server:

Open a NEW PowerShell window and run:
```powershell
cd "C:\Users\Lenovo\Desktop\BillBoard av\smart-billboard"
.\run-frontend.bat
```

Wait until you see:
```
➜  Local:   http://localhost:5174/
```

---

## Step 8: Test the System

### In Your Browser:

1. Open: http://localhost:5174
2. Go to **Detect** tab
3. Click **Upload** button
4. Choose any image with text (billboard, sign, etc.)
5. Click **Analyze Compliance**
6. Wait for analysis...
7. See results with extracted text and violations
8. Go to **Dashboard** tab
9. See your report appear in real-time!
10. Try uploading more images and watch the statistics update

---

## ✅ You're Done!

Your Smart Billboard Compliance System is now fully operational!

### What's Working:
- ✅ Frontend (React) on http://localhost:5174
- ✅ Backend (FastAPI) on http://localhost:8000
- ✅ Database (Supabase PostgreSQL) with real-time data
- ✅ Image Storage (Supabase Storage)
- ✅ OCR Analysis (Tesseract)
- ✅ Real-time Dashboard with auto-refresh

---

## Useful Links

- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Supabase Dashboard**: https://supabase.com
- **Backend README**: `backend/README.md`
- **Setup Guide**: `SETUP_GUIDE.md`

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'pytesseract'"
```powershell
pip install -r requirements.txt
```

### "tesseract is not installed or it's not in your PATH"
Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki

### "CORS error" or "Failed to fetch"
Make sure both servers are running:
- Backend: http://localhost:8000 ✓
- Frontend: http://localhost:5174 ✓

### "Connection error" in backend
Check your `.env` file - make sure credentials are correct

### "Database error"
Check Supabase dashboard to verify:
- Table `violation_reports` exists
- Storage bucket `billboard-images` exists

---

## Need Help?

1. **Check terminal output** - Error messages tell you exactly what's wrong
2. **Visit API docs** - http://localhost:8000/docs shows all endpoints
3. **Read README files** - More detailed info in `backend/README.md`
4. **Check Supabase dashboard** - Verify database and storage are set up

---

Happy Billboard Compliance Checking! 🎯
