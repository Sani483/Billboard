```md
# 🧠 Smart Billboard Compliance Detection

A smart-city solution designed to detect **unauthorized billboards**, measure **their dimensions**, and identify **non-compliant or “toxic” advertising content** based on government regulations.

## 📋 Project Overview

Unauthorized and non-compliant billboards lead to:

- Safety hazards  
- Visual pollution  
- Loss of municipal revenue  
- Promotion of banned or harmful content  

This system empowers **field agents** and **citizens** to capture billboard images, while the backend uses AI to automatically:

1. **Detect Text:** Extract text from the billboard and identify banned or “toxic” keywords as per local regulations (India-specific).
2. **Measure Dimensions:** Estimate the physical size of the billboard using computer-vision techniques.
3. **Report Violations:** Geotag, analyze, and upload data to a centralized dashboard for authorities.

---

## 🚀 Tech Stack

### **Frontend (Current)**

- **Framework:** React  
- **Styling:** Tailwind CSS  
- **Icons:** Lucide-React  

### **Backend & AI (In Progress / Roadmap)**

- **API Framework:** FastAPI (Python)  
- **Database & Storage:** Supabase  
- **Computer Vision:** OpenCV  
- **OCR:** Tesseract / EasyOCR  

---

## 🛠️ Installation & Setup

### **Prerequisites**

- Node.js (v18 or higher)  
- npm or yarn  

---

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/smart-billboard.git
cd smart-billboard
```

### **2. Install Frontend Dependencies**
```bash
npm install
```

### **3. Configure TailwindCSS**
Ensure your **tailwind.config.js** scans the correct files:

```js
/** @type {import('tailwindcss').Config} */
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
```

### **4. Run the Application**
```bash
npm run dev
```

Access the app at:
```
http://localhost:5173
```

---

## 📂 Project Structure

```bash
src/
├── components/         # Reusable UI components
│   └── Shared.jsx      # Buttons, cards, and shared design elements
├── pages/              # Main app screens
│   ├── Overview.jsx    # Problem statement & app overview
│   ├── Detect.jsx      # Image upload/capture and AI trigger
│   └── Dashboard.jsx   # Statistics, logs, and compliance reports
├── App.jsx             # Routing and global layout
└── main.jsx            # Entry point
```

---

## 🔮 Future Backend Integration (FastAPI + Supabase)

The frontend is designed to integrate with a FastAPI backend.  
`Detect.jsx` currently simulates analysis results but is ready to send **FormData** to an API endpoint.

### **Planned Workflow**

#### **1. Upload**
User selects or captures an image.

#### **2. API Call**
Frontend sends image to:

```
POST /api/analyze
```

#### **3. Processing**

- **Supabase:** Stores the image in a bucket and returns a URL.
- **OCR Engine:** Extracts text and checks for banned or harmful keywords.
- **OpenCV:** Measures billboard dimensions using CV algorithms.

#### **4. Response Example**
```json
{
  "isToxic": false,
  "dimensions": "12x8 ft",
  "complianceStatus": "Compliant",
  "imageUrl": "..."
}
```

---

## 🤝 Contributing

Contributions are welcome!  
Feel free to fork this repo and submit a PR.

---
```
