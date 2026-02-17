from PIL import Image
import easyocr
import io
import numpy as np

class OCRProcessor:
    """Handles text extraction from images using EasyOCR (Deep Learning)"""
    
    def __init__(self):
        # Initialize reader for English - downloads models automatically if needed
        # gpu=False to ensure compatibility on all systems, though True is faster if CUDA available
        print("Loading EasyOCR model...")
        self.reader = easyocr.Reader(['en'], gpu=False)
        
    def extract_text(self, image_file):
        """
        Extract text from an uploaded image file.
        
        Args:
            image_file: Streamlit UploadedFile object or bytes
            
        Returns:
            dict: result with 'text' and 'error' keys
        """
        try:
            # Load image
            image = Image.open(image_file)
            
            # Convert to numpy array for EasyOCR
            image_np = np.array(image)
            
            # Run OCR
            # detail=0 returns just the text list
            result_list = self.reader.readtext(image_np, detail=0)
            
            text = " ".join(result_list)
            
            if not text.strip():
                return {'text': '', 'error': 'No text detected in image.'}
                
            return {'text': text.strip(), 'error': None}
            
        except Exception as e:
            return {'text': '', 'error': f"OCR Error: {str(e)}"}
