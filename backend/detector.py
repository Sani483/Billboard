import pytesseract
from PIL import Image
import io
import re
from config import VIOLATION_KEYWORDS
from typing import Dict, List

class ViolationDetector:
    def __init__(self):
        self.violation_keywords = [kw.strip().lower() for kw in VIOLATION_KEYWORDS]
    
    def extract_text_from_image(self, image_data: bytes) -> str:
        """Extract text from image using OCR (Tesseract)"""
        try:
            image = Image.open(io.BytesIO(image_data))
            # Resize for better OCR accuracy
            image = image.resize((image.width * 2, image.height * 2))
            extracted_text = pytesseract.image_to_string(image)
            return extracted_text.lower()
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    def detect_violations(self, extracted_text: str) -> Dict:
        """Detect violation keywords in extracted text"""
        found_violations = []
        violation_text = []
        
        # Split text into words and search for violations
        words = re.findall(r'\b\w+\b', extracted_text)
        
        for keyword in self.violation_keywords:
            for word in words:
                if keyword in word.lower():
                    found_violations.append(keyword)
                    # Find the context (surrounding words)
                    for i, w in enumerate(words):
                        if keyword in w.lower():
                            context = ' '.join(words[max(0, i-2):min(len(words), i+3)])
                            violation_text.append(context)
        
        is_compliant = len(found_violations) == 0
        
        return {
            "is_compliant": is_compliant,
            "status": "Compliant" if is_compliant else "Unauthorized",
            "violations_found": list(set(found_violations)),
            "violation_count": len(set(found_violations)),
            "violation_context": list(set(violation_text)),
            "extracted_text": extracted_text[:500]  # First 500 chars
        }
    
    def analyze_image(self, image_data: bytes) -> Dict:
        """Complete analysis pipeline: extract text -> detect violations"""
        extracted_text = self.extract_text_from_image(image_data)
        detection_result = self.detect_violations(extracted_text)
        
        return {
            "success": True,
            "data": detection_result
        }

# Initialize detector
detector = ViolationDetector()
