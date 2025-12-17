---
sidebar_position: 3
sidebar_label: "4.3 Vision-Language"
title: "Chapter 4.3: Vision-Language Models for Scene Understanding"
description: "Learn to use CLIP, LLaVA, and other vision-language models for robot perception"
keywords: [vision-language, clip, llava, multimodal, perception, robotics]
---

# Vision-Language Models for Scene Understanding

Vision-Language Models (VLMs) represent a paradigm shift in robot perception. Instead of relying on task-specific computer vision models, VLMs enable robots to understand scenes through natural language, answering questions like "What objects are on the table?" or "Where is the red cup?"

## Learning Objectives

By the end of this chapter, you will be able to:

- Understand the architecture and capabilities of vision-language models
- Implement CLIP for zero-shot object recognition
- Use LLaVA for visual question answering in robotics
- Integrate VLMs with ROS 2 for real-time perception
- Ground natural language references to objects in the scene

## Why Vision-Language Models?

Traditional computer vision requires training separate models for each task: object detection, segmentation, classification, and more. Vision-language models offer a unified approach.

### Traditional vs VLM Approach

```
Traditional Pipeline:
Camera → Object Detector → Classifier → Segmenter → Scene Graph → Planner

VLM Pipeline:
Camera → Vision-Language Model ←→ Natural Language Query → Structured Output
```

### Key Advantages

1. **Zero-shot Recognition**: Identify objects without task-specific training
2. **Natural Language Interface**: Query scenes using everyday language
3. **Contextual Understanding**: Understand spatial relationships and attributes
4. **Flexible Grounding**: Connect language references to visual regions

## CLIP: Contrastive Language-Image Pre-training

CLIP, developed by OpenAI, learns visual concepts from natural language supervision. It can recognize virtually any object by comparing images to text descriptions.

### CLIP Architecture

```python
import torch
import clip
from PIL import Image

class CLIPPerception:
    """CLIP-based zero-shot object recognition for robotics."""

    def __init__(self, model_name: str = "ViT-B/32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load(model_name, device=self.device)

    def encode_image(self, image: Image.Image) -> torch.Tensor:
        """Encode an image into CLIP's embedding space."""
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
        return image_features / image_features.norm(dim=-1, keepdim=True)

    def encode_text(self, texts: list) -> torch.Tensor:
        """Encode text descriptions into CLIP's embedding space."""
        text_tokens = clip.tokenize(texts).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
        return text_features / text_features.norm(dim=-1, keepdim=True)

    def classify(self, image: Image.Image, candidates: list) -> dict:
        """Zero-shot classification of an image."""
        image_features = self.encode_image(image)
        text_features = self.encode_text(candidates)

        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)

        results = {}
        for i, candidate in enumerate(candidates):
            results[candidate] = similarity[0, i].item()

        return results
```

### Using CLIP for Robot Perception

```python
# Initialize CLIP perception
perception = CLIPPerception()

# Define object categories for a kitchen scene
kitchen_objects = [
    "a red apple",
    "a blue cup",
    "a wooden cutting board",
    "a metal knife",
    "a white plate"
]

# Classify what's in the robot's view
image = Image.open("robot_camera_view.jpg")
results = perception.classify(image, kitchen_objects)

# Find the most likely object
best_match = max(results, key=results.get)
confidence = results[best_match]
print(f"Detected: {best_match} (confidence: {confidence:.2%})")
```

## LLaVA: Large Language and Vision Assistant

LLaVA extends large language models with visual understanding, enabling conversational interaction about images. This is particularly useful for robots that need to answer complex questions about their environment.

### LLaVA for Visual Question Answering

```python
from transformers import LlavaForConditionalGeneration, AutoProcessor
import torch

class LLaVAPerception:
    """LLaVA-based visual question answering for robotics."""

    def __init__(self, model_name: str = "llava-hf/llava-1.5-7b-hf"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = LlavaForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto"
        )

    def ask(self, image: Image.Image, question: str) -> str:
        """Ask a question about an image."""
        prompt = f"USER: <image>\n{question}\nASSISTANT:"

        inputs = self.processor(
            text=prompt,
            images=image,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False
            )

        response = self.processor.decode(output[0], skip_special_tokens=True)
        return response.split("ASSISTANT:")[-1].strip()
```

### Robotics Applications

```python
# Initialize LLaVA
vlm = LLaVAPerception()

# Scene understanding queries
image = robot.get_camera_image()

# Object localization
location = vlm.ask(image, "Where is the red block in the image?")
print(f"Red block location: {location}")

# Spatial reasoning
relationship = vlm.ask(image, "What is to the left of the cup?")
print(f"Spatial relationship: {relationship}")

# State estimation
state = vlm.ask(image, "Is the drawer open or closed?")
print(f"Drawer state: {state}")

# Safety assessment
safety = vlm.ask(image, "Are there any obstacles between the robot and the table?")
print(f"Safety check: {safety}")
```

## Grounding Language to Visual Regions

For manipulation tasks, robots need to connect language references to specific regions in the image. This is called visual grounding.

### Grounding DINO for Open-Vocabulary Detection

```python
from groundingdino.util.inference import load_model, predict
import supervision as sv

class GroundingPerception:
    """Grounding DINO for open-vocabulary object detection."""

    def __init__(self):
        self.model = load_model(
            "groundingdino/config/GroundingDINO_SwinT_OGC.py",
            "weights/groundingdino_swint_ogc.pth"
        )
        self.box_threshold = 0.35
        self.text_threshold = 0.25

    def detect(self, image, text_prompt: str) -> list:
        """Detect objects matching the text prompt."""
        boxes, logits, phrases = predict(
            model=self.model,
            image=image,
            caption=text_prompt,
            box_threshold=self.box_threshold,
            text_threshold=self.text_threshold
        )

        detections = []
        for box, logit, phrase in zip(boxes, logits, phrases):
            detections.append({
                "box": box.tolist(),  # [x_center, y_center, width, height]
                "confidence": logit.item(),
                "label": phrase
            })

        return detections
```

### From Detection to 3D Coordinates

```python
import numpy as np

def pixel_to_3d(detection: dict, depth_image: np.ndarray,
                camera_intrinsics: dict) -> np.ndarray:
    """Convert 2D detection to 3D coordinates using depth."""

    # Get box center
    x_center, y_center, width, height = detection["box"]

    # Convert normalized coordinates to pixels
    img_height, img_width = depth_image.shape
    px = int(x_center * img_width)
    py = int(y_center * img_height)

    # Get depth at object center
    depth = depth_image[py, px]

    # Unproject to 3D
    fx, fy = camera_intrinsics["fx"], camera_intrinsics["fy"]
    cx, cy = camera_intrinsics["cx"], camera_intrinsics["cy"]

    x = (px - cx) * depth / fx
    y = (py - cy) * depth / fy
    z = depth

    return np.array([x, y, z])
```

## ROS 2 Integration

### VLM Perception Node

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from PIL import Image as PILImage
import numpy as np

class VLMPerceptionNode(Node):
    """ROS 2 node for vision-language perception."""

    def __init__(self):
        super().__init__('vlm_perception')

        # Initialize VLM
        self.clip = CLIPPerception()
        self.bridge = CvBridge()

        # Subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/color/image_raw',
            self.image_callback, 10
        )
        self.query_sub = self.create_subscription(
            String, '/vlm/query',
            self.query_callback, 10
        )

        # Publishers
        self.result_pub = self.create_publisher(
            String, '/vlm/result', 10
        )

        self.current_image = None
        self.get_logger().info('VLM Perception Node initialized')

    def image_callback(self, msg: Image):
        """Store latest camera image."""
        cv_image = self.bridge.imgmsg_to_cv2(msg, "rgb8")
        self.current_image = PILImage.fromarray(cv_image)

    def query_callback(self, msg: String):
        """Process a visual query."""
        if self.current_image is None:
            self.get_logger().warn('No image available')
            return

        query = msg.data

        # Parse query type
        if query.startswith("classify:"):
            candidates = query[9:].split(",")
            results = self.clip.classify(self.current_image, candidates)
            response = str(results)
        else:
            response = "Unknown query type"

        result_msg = String()
        result_msg.data = response
        self.result_pub.publish(result_msg)

def main(args=None):
    rclpy.init(args=args)
    node = VLMPerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Performance Optimization

### Quantization for Edge Deployment

```python
import torch
from transformers import BitsAndBytesConfig

# 4-bit quantization for efficient inference
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# Load quantized model
model = LlavaForConditionalGeneration.from_pretrained(
    "llava-hf/llava-1.5-7b-hf",
    quantization_config=quantization_config,
    device_map="auto"
)
```

### Caching for Real-Time Performance

```python
from functools import lru_cache
import hashlib

class CachedVLM:
    """VLM with response caching for repeated queries."""

    def __init__(self, vlm):
        self.vlm = vlm
        self.cache = {}

    def _image_hash(self, image: PILImage) -> str:
        """Create hash of image for cache key."""
        return hashlib.md5(image.tobytes()).hexdigest()

    def ask(self, image: PILImage, question: str) -> str:
        """Ask with caching."""
        cache_key = (self._image_hash(image), question)

        if cache_key in self.cache:
            return self.cache[cache_key]

        response = self.vlm.ask(image, question)
        self.cache[cache_key] = response
        return response
```

## Exercise: Build a Scene Understanding System

**Objective**: Create a VLM-based scene understanding system that can answer questions about a robot's environment.

**Prerequisites**: Complete Chapters 4.1 and 4.2

**Estimated Time**: 45 minutes

### Steps

1. Set up the environment:
   ```bash
   pip install transformers torch clip-by-openai pillow
   ```

2. Create a scene analyzer that combines CLIP and LLaVA:
   ```python
   class SceneAnalyzer:
       def __init__(self):
           self.clip = CLIPPerception()
           # Add LLaVA for detailed questions

       def analyze(self, image, query_type, query):
           if query_type == "classify":
               return self.clip.classify(image, query.split(","))
           elif query_type == "describe":
               # Use LLaVA for description
               pass
   ```

3. Test with sample images from a robotics dataset

4. Integrate with ROS 2 for real-time perception

### Expected Output

```
Query: What objects are visible?
Response: I can see a table with a red apple, a blue cup, and a white plate.

Query: classify:apple,banana,orange
Response: {'apple': 0.92, 'banana': 0.05, 'orange': 0.03}
```

### Stretch Goal

Add visual grounding to return bounding boxes for referenced objects.

## Summary

Vision-language models transform robot perception by enabling:

- Zero-shot object recognition with CLIP
- Visual question answering with LLaVA
- Open-vocabulary detection with Grounding DINO
- Natural language scene queries

Key integration points:
- ROS 2 image topics for camera input
- Quantization for edge deployment
- Caching for real-time performance
- Depth fusion for 3D localization

In the next chapter, you will learn how to generate robot actions from vision and language inputs using VLA models like RT-2 and OpenVLA.

**Next:** [Action Generation with VLA Models](./4-action-generation.md)
