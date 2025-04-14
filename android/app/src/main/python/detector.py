import numpy as np
import torch
import base64
import io
from PIL import Image

def detect(image_base64):
    # Decode base64 image
    img_bytes = base64.b64decode(image_base64)
    img = Image.open(io.BytesIO(img_bytes))
    
    # Load YOLO model (pretrained)
    yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    
    # Run YOLO inference
    results = yolo_model(img)
    if "food" not in results.pandas().xyxy[0]['name'].values:
        return "No food detected"
    
    # Load classification model (replace with your 264-class model)
    classifier_model = torch.load('food_classifier.pt')
    category = classifier_model(img).argmax().item()
    
    return str(category)  # Return category ID