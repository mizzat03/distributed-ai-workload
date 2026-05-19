import argparse
from typing import Tuple, List

import torch
from torchvision import models, transforms
from PIL import Image

import json
import urllib.request

def load_imagenet_labels() -> list:
    """Fetches the 1000 ImageNet class labels."""
    # This is a widely used, clean version of the ImageNet labels
    url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
    with urllib.request.urlopen(url) as response:
        labels = json.loads(response.read().decode())
    return labels



def load_model(pretrained: bool = True, device: str = "cpu") -> torch.nn.Module:
    """Load ResNet18 model and set to eval on given device."""
    model = models.resnet18(weights='DEFAULT')
    model.eval()
    model.to(device)
    return model


def preprocess_image(image_path: str) -> torch.Tensor:
    """Read image and apply ResNet preprocessing, returning a batch tensor."""
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    img = Image.open(image_path).convert("RGB")
    tensor = preprocess(img).unsqueeze(0)  # add batch dim
    return tensor


def predict(model: torch.nn.Module, input_tensor: torch.Tensor, device: str = "cpu", topk: int = 5) -> List[Tuple[int, float]]:
    """Run inference and return top-k (class_idx, probability) pairs."""
    input_tensor = input_tensor.to(device)
    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.nn.functional.softmax(outputs, dim=1)[0]
        topk_probs, topk_idxs = torch.topk(probs, topk)
        return [(int(idx.item()), float(prob.item())) for idx, prob in zip(topk_idxs, topk_probs)]


def main():
    parser = argparse.ArgumentParser(description="Local ResNet18 inference boilerplate")
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--device", default="cpu", help="Device to run on (cpu or cuda)")
    args = parser.parse_args()

    # Load the text labels
    print("Loading labels...")
    labels = load_imagenet_labels()

    device = args.device if torch.cuda.is_available() and args.device.startswith("cuda") else "cpu"
    model = load_model(pretrained=True, device=device)
    tensor = preprocess_image(args.image)
    
    print(f"Running inference on {args.device}...")
    results = predict(model, tensor, device=device, topk=5)

    print("\n--- Top 5 Predictions ---")
    for cls, prob in results:
        # Use the integer class index to grab the string name from our list
        class_name = labels[cls]
        print(f"Name: {class_name:<20} | Index: {cls:<4} | Confidence: {prob*100:.2f}%")

if __name__ == "__main__":
    main()