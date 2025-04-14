import torch
import torchvision.transforms as transforms
from efficientnet_pytorch import EfficientNet
import onnxruntime as ort
import base64
from PIL import Image
import io
import numpy as np
import os
import atexit

# Constants
MODEL_INPUT_SIZE = 224  # Match this to your model's expected input size

# Pre-load models during initialization to avoid reloading on every call
_model_dir = os.path.dirname(os.path.abspath(__file__))
_effnet_model = None
_ort_session = None

def _initialize_models():
    global _effnet_model, _ort_session
    
    # Load classification model (PyTorch)
    _effnet_model = torch.jit.load(os.path.join(_model_dir, "mobile.ptl"))
    _effnet_model.eval()
    
    # Load YOLO model (ONNX Runtime)
    _ort_session = ort.InferenceSession(
        os.path.join(_model_dir, "best.onnx"),
        providers=['CPUExecutionProvider']  # Required for Android
    )
    
    # Register cleanup
    atexit.register(_cleanup)

def _cleanup():
    if _ort_session:
        _ort_session.end_profiling()

def _preprocess_image(image):
    """Convert base64 to tensor and apply model-specific preprocessing"""
    # Convert base64 to PIL Image
    img_bytes = base64.b64decode(image)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    
    # Classification model preprocessing
    transform = transforms.Compose([
        transforms.Resize((MODEL_INPUT_SIZE, MODEL_INPUT_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                             std=[0.229, 0.224, 0.225])
    ])
    img_tensor = transform(img).unsqueeze(0)
    
    # YOLO model preprocessing
    yolo_img = img.resize((640, 640))
    yolo_array = np.array(yolo_img).astype(np.float32) / 255.0
    yolo_array = np.transpose(yolo_array, (2, 0, 1))[np.newaxis, :]
    
    return img_tensor, yolo_array

def detect_food(base64_image):
    try:
        # Lazy load models on first call
        if _effnet_model is None:
            _initialize_models()
        
        # Preprocess image
        img_tensor, yolo_array = _preprocess_image(base64_image)
        
        # Run classification model
        with torch.no_grad():
            out = _effnet_model(img_tensor)
            category = int(torch.argmax(out))
        
        # Run YOLO detection
        yolo_outputs = _ort_session.run(None, {"images": yolo_array})
        
        # TODO: Add your custom logic to interpret YOLO outputs
        # This example assumes food is detected if YOLO returns any objects
        food_detected = len(yolo_outputs[0]) > 0
        
        if not food_detected:
            return {
                "error": "No food detected",
                "category": None,
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fats": 0
            }
        
        # TODO: Replace with your actual nutrition database lookup
        nutrition_data = {
            0: {"name": "Apple", "calories": 95, "protein": 0.5, "carbs": 25, "fats": 0.3},
            1: {"name": "Pizza", "calories": 285, "protein": 12, "carbs": 36, "fats": 10}
            # Add all 264 categories
        }
        
        return {
            "category": nutrition_data.get(category, {}).get("name", f"Class {category}"),
            "calories": nutrition_data.get(category, {}).get("calories", 0),
            "protein": nutrition_data.get(category, {}).get("protein", 0),
            "carbs": nutrition_data.get(category, {}).get("carbs", 0),
            "fats": nutrition_data.get(category, {}).get("fats", 0)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "category": None,
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fats": 0
        }

# Initialize models when module loads (optional)
_initialize_models()