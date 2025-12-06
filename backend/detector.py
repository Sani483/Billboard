import pytesseract
import cv2
import numpy as np
import io
import re
from typing import Dict, List, Tuple
from PIL import Image
from config import VIOLATION_KEYWORDS, OCR_CONFIDENCE_THRESHOLD, IMAGE_RESIZE_SCALE
from datetime import datetime

class ViolationDetector:
    """Advanced computer vision-based violation detection system"""
    
    def __init__(self):
        self.violation_keywords = [kw.strip().lower() for kw in VIOLATION_KEYWORDS]
        self.confidence_threshold = OCR_CONFIDENCE_THRESHOLD
    
    def load_image(self, image_data: bytes) -> np.ndarray:
        """Load image from bytes using OpenCV"""
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR and detection"""
        try:
            h, w = img.shape[:2]
            new_w = w * IMAGE_RESIZE_SCALE
            new_h = h * IMAGE_RESIZE_SCALE
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
            _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return thresh
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return img
    
    def extract_text_from_image(self, image_data: bytes) -> Tuple[str, float]:
        """Extract text from image using advanced OCR with confidence scoring"""
        try:
            img = self.load_image(image_data)
            if img is None:
                return "", 0.0
            
            processed = self.preprocess_image(img)
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            
            extracted_text = ""
            confidence_scores = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > (self.confidence_threshold * 100):
                    extracted_text += " " + data['text'][i]
                    confidence_scores.append(float(data['conf'][i]) / 100)
            
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            return extracted_text.lower().strip(), avg_confidence
        except Exception as e:
            print(f"Error extracting text: {e}")
            return "", 0.0
    
    def detect_text_regions(self, image_data: bytes) -> List[Dict]:
        """Detect and localize text regions in the image (bounding boxes)"""
        try:
            img = self.load_image(image_data)
            if img is None:
                return []
            
            processed = self.preprocess_image(img)
            contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 10 and h > 10:
                    text_regions.append({
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h),
                        "area": int(w * h)
                    })
            
            return text_regions
        except Exception as e:
            print(f"Error detecting text regions: {e}")
            return []
    
    def detect_violations(self, extracted_text: str, ocr_confidence: float) -> Dict:
        """Detect violation keywords with advanced context analysis"""
        found_violations = []
        violation_contexts = []
        severity_scores = []
        
        if not extracted_text.strip():
            return {
                "is_compliant": True,
                "status": "Compliant",
                "violations_found": [],
                "violation_count": 0,
                "violation_context": [],
                "extracted_text": "",
                "ocr_confidence": ocr_confidence,
                "detection_timestamp": datetime.utcnow().isoformat(),
                "severity_level": "none"
            }
        
        sentences = re.split(r'[.!?]', extracted_text)
        
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            
            for keyword in self.violation_keywords:
                for i, word in enumerate(words):
                    if keyword in word.lower():
                        if keyword not in found_violations:
                            found_violations.append(keyword)
                            start = max(0, i - 5)
                            end = min(len(words), i + 6)
                            context = ' '.join(words[start:end])
                            violation_contexts.append(context)
                            severity = self._calculate_severity(keyword, context)
                            severity_scores.append(severity)
        
        is_compliant = len(found_violations) == 0
        overall_severity = max(severity_scores) if severity_scores else 0
        
        return {
            "is_compliant": is_compliant,
            "status": "Compliant" if is_compliant else "Unauthorized",
            "violations_found": found_violations,
            "violation_count": len(found_violations),
            "violation_context": violation_contexts,
            "extracted_text": extracted_text[:500],
            "ocr_confidence": round(ocr_confidence, 2),
            "detection_timestamp": datetime.utcnow().isoformat(),
            "severity_level": self._severity_level(overall_severity),
            "severity_score": round(overall_severity, 1)
        }
    
    def _calculate_severity(self, keyword: str, context: str) -> float:
        """Calculate severity of violation (1-10 scale)"""
        base_severity_map = {
            "nude": 9, "adult": 8, "gambling": 7, "alcohol": 6,
            "tobacco": 5, "drugs": 9, "weapons": 9, "unauthorized": 6, "prohibited": 7
        }
        
        base = base_severity_map.get(keyword.lower(), 5)
        violation_count = sum(1 for kw in self.violation_keywords if kw in context.lower())
        multiplier = min(1 + (violation_count * 0.2), 1.5)
        
        return min(base * multiplier, 10.0)
    
    def _severity_level(self, score: float) -> str:
        """Convert severity score to text level"""
        if score >= 8.0:
            return "Critical"
        elif score >= 6.0:
            return "High"
        elif score >= 4.0:
            return "Medium"
        elif score >= 2.0:
            return "Low"
        else:
            return "None"
    
    def analyze_image(self, image_data: bytes) -> Dict:
        """Complete billboard analysis: text extraction + violation detection + text localization"""
        try:
            extracted_text, ocr_confidence = self.extract_text_from_image(image_data)
            violations = self.detect_violations(extracted_text, ocr_confidence)
            text_regions = self.detect_text_regions(image_data)
            
            return {
                **violations,
                "text_regions": text_regions,
                "analysis_complete": True
            }
        except Exception as e:
            print(f"Error analyzing billboard: {e}")
            return {
                "is_compliant": True,
                "status": "Compliant",
                "violations_found": [],
                "violation_count": 0,
                "violation_context": [],
                "extracted_text": "",
                "ocr_confidence": 0.0,
                "detection_timestamp": datetime.utcnow().isoformat(),
                "severity_level": "none",
                "severity_score": 0,
                "text_regions": [],
                "analysis_complete": False,
                "error": str(e)
            }

# Initialize detector
detector = ViolationDetector()
