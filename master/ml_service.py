import io
import torch
from PIL import Image
from torchvision import transforms, models
import json
import urllib.request

print("Loading PyTorch model into memory...")
model = models.resnet18(weights='DEFAULT')
model.eval() # Set to evaluation mode

preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

"""Fetches the 1000 ImageNet class labels."""
url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
with urllib.request.urlopen(url) as response:
    labels = json.loads(response.read().decode())
    

def get_prediction(image_bytes: bytes) -> tuple[str, float]:
    """
    Takes raw image bytes from the FastAPI endpoint, runs it through
    the loaded model, and returns the class name and confidence score.
    """
    try:
        # Convert the raw bytes back into a PIL Image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Preprocess the image and add a batch dimension
        input_tensor = preprocess(image)
        input_batch = input_tensor.unsqueeze(0) 

        # Run the inference (no gradients needed for prediction)
        with torch.no_grad():
            output = model(input_batch)
        
        # Calculate probabilities (softmax) and get the highest score
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        confidence, predicted_idx = torch.max(probabilities, 0)

        index = predicted_idx.item()

        class_name = labels[index]
        
        return class_name, confidence.item()
        
    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")