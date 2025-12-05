# Smart Billboard Compliance Detection

A smart city solution designed to detect unauthorized billboards, measure their dimensions, and identify non-compliant or "toxic" content based on government regulations.

## 📋Project Overview

Urban areas struggle with unauthorized advertising that poses safety hazards and revenue loss. This application provides an interface for field agents and citizens to capture billboard images. The system is designed to use AI to automatically:

1. Detect Text: Analyze content for keywords deemed illegal or "toxic" by local governance (specifically tailored for Indian regulations).
2. Measure Dimensions: Estimate the physical size of the billboard to check against zoning permits.
3. Report: Geotag and upload violations to a central dashboard.

## 🚀 Tech Stack

Frontend (Current)

- Framework: [React] (https://react.dev/reference/react)
- Styling: [Tailwind CSS] (https)
- Icons: Lucide React

Backend & AI (Roadmap/In-Progress)

- API Framework: FastAPI (Python)
- Database & Storage: Supabase
- Computer Vision: OpenCV (Dimension estimation)
- OCR: Tesseract / EasyOCR (Text extraction)

## 🛠️ Installation & SetupPrerequisitesNode.js (v18 or higher)npm or yarn

1.  Clone the Repository 
``` bash git clone [https://github.com/your-username/smart-billboard.git](https://github.com/your-username/smart-billboard.git)```
cd smart-billboard
2.  Install Frontend Dependencies
``` bash npm install ```
3. Configure Tailwind CSSEnsure ``` bash tailwind.config.js``` is set to scan your source files:/** 
 bash @type {import('tailwindcss').Config} */
    export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {},
    },
    plugins: [],
    }
4. Run the Application 
``` bash npm run dev```
Access the app at ``` bash http://localhost:5173.``` 
## 📂Project Structure
``` bash src/
├── components/       # Reusable UI components
│   └── Shared.jsx    # Buttons, Cards, and other shared UI elements
├── pages/            # Main application screens
│   ├── Overview.jsx  # Landing page with problem statement & features
│   ├── Detect.jsx    # Image capture/upload & AI analysis trigger
│   └── Dashboard.jsx # Statistics and reporting interface
├── App.jsx           # Main routing and layout logic
└── main.jsx          # Entry point 
``` 
## 🔮 Future Backend Integration (FastAPI + Supabase)

The frontend is designed to integrate with a FastAPI backend. The Detect.jsx page currently simulates the analysis process but is ready to send FormData to an API endpoint.

### Planned Workflow

1. Upload: User selects an image in React.

2. API Call: Image is sent to POST /api/analyze.

3. Processing:

- Supabase: Image is stored in a storage bucket; URL is retrieved.

- AI Engine: Python script runs OCR to find banned words (e.g., hate speech, unauthorized substance ads).- 
- Dimensions: Computer vision algorithm estimates the billboard area.

4. Response: JSON data containing isToxic, dimensions, and complianceStatus is returned to the frontend.🤝 