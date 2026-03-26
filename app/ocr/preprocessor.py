import cv2
import numpy as np
from PIL import Image



class ImagePreprocessor:
    """Preprocesses images for optimal OCR performance"""
    
    @staticmethod
    def preprocess(image: Image.Image, target_dpi: int = 300) -> Image.Image:
        """
        Apply preprocessing pipeline to improve OCR accuracy
        
        Args:
            image: PIL Image object
            target_dpi: Target DPI for OCR
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        
        # Convert to grayscale if not already
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Resize to target DPI if image is too small
        gray = ImagePreprocessor._resize_to_dpi(gray, target_dpi)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Adaptive thresholding for binarization
        binary = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Deskew if needed
        deskewed = ImagePreprocessor._deskew(binary)
        
        # Convert back to PIL Image
        return Image.fromarray(deskewed)
    
    @staticmethod
    def _resize_to_dpi(image: np.ndarray, target_dpi: int = 300) -> np.ndarray:
        """Resize image to target DPI"""
        height, width = image.shape[:2]
        
        # If image is too small, scale up
        if width < 1000:
            scale = target_dpi / 100
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(
                image, 
                (new_width, new_height), 
                interpolation=cv2.INTER_CUBIC
            )
        
        return image
    
    @staticmethod
    def _deskew(image: np.ndarray) -> np.ndarray:
        """Correct image skew"""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image
            
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Only deskew if angle is significant
        if abs(angle) < 0.5:
            return image
        
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image,
            M,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated