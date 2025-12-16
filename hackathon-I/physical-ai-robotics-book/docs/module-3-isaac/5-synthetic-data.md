---
sidebar_position: 5
sidebar_label: "3.5 Synthetic Data"
title: "Chapter 3.5: Synthetic Data Generation"
description: "Learn to generate labeled training datasets for perception using Isaac Sim Replicator"
keywords: [synthetic data, replicator, perception, training data, computer vision, isaac sim]
---

# Synthetic Data Generation

In this chapter, you will learn how to generate synthetic training data for perception models using Isaac Sim's Replicator framework, enabling training of computer vision models without manual labeling.

## Why Synthetic Data?

Training perception models requires massive labeled datasets. Manual labeling is:

| Challenge | Real Data | Synthetic Data |
|-----------|-----------|----------------|
| **Cost** | $1-10 per image | ~$0.001 per image |
| **Time** | Weeks/months | Hours |
| **Accuracy** | Human error prone | Pixel-perfect |
| **Edge cases** | Hard to capture | Easy to generate |
| **Privacy** | Concerns | None |
| **Iteration** | Slow | Fast |

### The Synthetic Data Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│              Synthetic Data Generation Pipeline              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   3D Scene  │───▶│  Replicator │───▶│   Labeled   │     │
│  │   Setup     │    │  Rendering  │    │   Dataset   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│        │                  │                  │              │
│        ▼                  ▼                  ▼              │
│   - Objects           - RGB images      - Bounding boxes    │
│   - Lighting          - Depth maps      - Segmentation      │
│   - Cameras           - Normals         - Keypoints         │
│   - Materials         - Motion vectors  - COCO/KITTI format │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Isaac Sim Replicator

**Replicator** is Isaac Sim's framework for synthetic data generation:

### Core Concepts

- **Semantics**: Label objects with classes
- **Randomizers**: Vary scene parameters
- **Writers**: Output data in standard formats
- **Annotators**: Generate ground truth labels

### Available Annotations

| Annotator | Output | Use Case |
|-----------|--------|----------|
| `rgb` | Color image | Object detection, classification |
| `depth` | Distance map | 3D reconstruction |
| `semantic_segmentation` | Class labels per pixel | Segmentation models |
| `instance_segmentation` | Instance IDs per pixel | Instance segmentation |
| `bounding_box_2d_tight` | 2D boxes | Object detection |
| `bounding_box_3d` | 3D boxes | 3D detection |
| `skeleton_2d` | Joint positions | Pose estimation |
| `normals` | Surface normals | Shape analysis |
| `motion_vectors` | Optical flow | Motion prediction |

## Basic Replicator Script

### Setting Up a Scene

```python
import omni.replicator.core as rep
from omni.isaac.kit import SimulationApp

# Launch simulation
simulation_app = SimulationApp({"headless": True})

import omni.isaac.core.utils.stage as stage_utils
from pxr import Gf, UsdGeom

# Create basic scene
def setup_scene():
    # Add ground plane
    rep.create.plane(
        position=(0, 0, 0),
        scale=(10, 10, 1),
        semantics=[("class", "floor")]
    )

    # Add light
    rep.create.light(
        light_type="dome",
        intensity=1000,
        rotation=(0, 0, 0)
    )

    # Add camera
    camera = rep.create.camera(
        position=(3, 3, 2),
        look_at=(0, 0, 0.5),
        focal_length=35
    )

    return camera
```

### Adding Objects with Semantics

```python
def create_objects():
    """Create objects with semantic labels."""

    # Red cube - labeled as "box"
    cube = rep.create.cube(
        position=(0, 0, 0.5),
        scale=(0.3, 0.3, 0.3),
        semantics=[("class", "box")],
        material=rep.create.material_omnipbr(
            diffuse=(1.0, 0.0, 0.0)
        )
    )

    # Blue sphere - labeled as "ball"
    sphere = rep.create.sphere(
        position=(1, 0, 0.3),
        scale=(0.3, 0.3, 0.3),
        semantics=[("class", "ball")],
        material=rep.create.material_omnipbr(
            diffuse=(0.0, 0.0, 1.0)
        )
    )

    # Green cylinder - labeled as "cylinder"
    cylinder = rep.create.cylinder(
        position=(-1, 0, 0.4),
        scale=(0.2, 0.2, 0.4),
        semantics=[("class", "cylinder")],
        material=rep.create.material_omnipbr(
            diffuse=(0.0, 1.0, 0.0)
        )
    )

    return cube, sphere, cylinder
```

### Configuring Data Output

```python
def setup_writer(camera, output_dir):
    """Configure data writer for annotations."""

    # Create render product from camera
    render_product = rep.create.render_product(camera, (640, 480))

    # Initialize writer with annotations
    writer = rep.WriterRegistry.get("BasicWriter")
    writer.initialize(
        output_dir=output_dir,
        rgb=True,
        bounding_box_2d_tight=True,
        semantic_segmentation=True,
        instance_segmentation=True,
        distance_to_camera=True,
    )

    # Attach to render product
    writer.attach([render_product])

    return writer
```

### Running Data Generation

```python
def generate_data(num_frames=100):
    """Generate synthetic dataset."""

    camera = setup_scene()
    cube, sphere, cylinder = create_objects()
    writer = setup_writer(camera, "/output/dataset")

    # Define randomizers
    with rep.trigger.on_frame(num_frames=num_frames):
        # Randomize object positions
        with rep.get.prims(semantics=[("class", "box")]):
            rep.modify.pose(
                position=rep.distribution.uniform(
                    (-1, -1, 0.5),
                    (1, 1, 0.5)
                ),
                rotation=rep.distribution.uniform(
                    (0, 0, 0),
                    (0, 0, 360)
                )
            )

        # Randomize lighting
        with rep.get.prims(path_pattern="/Replicator/Light"):
            rep.modify.attribute(
                "intensity",
                rep.distribution.uniform(500, 2000)
            )

    # Run generation
    rep.orchestrator.run()

    print(f"Generated {num_frames} frames to /output/dataset")

# Execute
generate_data(100)
simulation_app.close()
```

## Advanced Randomization

### Domain Randomization for Perception

```python
def setup_randomizers():
    """Configure comprehensive domain randomization."""

    # Object pose randomization
    with rep.trigger.on_frame():
        # Randomize positions
        with rep.get.prims(semantics=[("class", "box")]):
            rep.modify.pose(
                position=rep.distribution.uniform((-2, -2, 0.3), (2, 2, 0.5)),
                rotation=rep.distribution.uniform((0, 0, 0), (360, 360, 360)),
                scale=rep.distribution.uniform((0.8, 0.8, 0.8), (1.2, 1.2, 1.2))
            )

        # Randomize colors
        with rep.get.prims(semantics=[("class", "box")]):
            rep.modify.material(
                diffuse=rep.distribution.uniform((0, 0, 0), (1, 1, 1)),
                roughness=rep.distribution.uniform(0.1, 0.9)
            )

        # Randomize lighting
        with rep.get.prims(path_pattern="/Replicator/Light"):
            rep.modify.attribute(
                "intensity",
                rep.distribution.uniform(300, 3000)
            )
            rep.modify.pose(
                rotation=rep.distribution.uniform((0, 0, 0), (60, 360, 0))
            )

        # Randomize camera
        with rep.get.prims(path_pattern="/Replicator/Camera"):
            rep.modify.pose(
                position=rep.distribution.uniform((2, -2, 1), (4, 2, 3)),
                look_at=(0, 0, 0.5)
            )
```

### Texture Randomization

```python
def randomize_textures():
    """Apply random textures to objects."""

    # Load texture library
    texture_paths = [
        "/Isaac/Materials/Textures/Patterns/wood_*",
        "/Isaac/Materials/Textures/Patterns/metal_*",
        "/Isaac/Materials/Textures/Patterns/fabric_*",
    ]

    with rep.trigger.on_frame():
        with rep.get.prims(semantics=[("class", "box")]):
            rep.modify.material(
                diffuse_texture=rep.distribution.choice(
                    rep.utils.get_usd_files(texture_paths)
                )
            )
```

### Background Randomization

```python
def randomize_backgrounds():
    """Randomize scene backgrounds."""

    # HDRI environment maps
    hdri_paths = [
        "/Isaac/Environments/HDR/industrial_*",
        "/Isaac/Environments/HDR/outdoor_*",
        "/Isaac/Environments/HDR/studio_*",
    ]

    with rep.trigger.on_frame():
        with rep.get.prims(path_pattern="/Replicator/DomeLight"):
            rep.modify.attribute(
                "texture:file",
                rep.distribution.choice(
                    rep.utils.get_usd_files(hdri_paths)
                )
            )
```

## Output Formats

### COCO Format

```python
# Configure COCO writer
writer = rep.WriterRegistry.get("COCOWriter")
writer.initialize(
    output_dir="/output/coco_dataset",
    semantic_types=["class"],
    rgb=True,
    bounding_box_2d_tight=True,
    semantic_segmentation=True,
)
```

Output structure:
```
/output/coco_dataset/
├── images/
│   ├── 000000.png
│   ├── 000001.png
│   └── ...
├── annotations/
│   ├── instances_default.json
│   └── semantic_segmentation/
│       ├── 000000.png
│       └── ...
└── metadata.json
```

### KITTI Format

```python
# Configure KITTI writer for 3D detection
writer = rep.WriterRegistry.get("KittiWriter")
writer.initialize(
    output_dir="/output/kitti_dataset",
    bounding_box_3d=True,
    rgb=True,
    point_cloud=True,
)
```

### Custom Writer

```python
import json
import numpy as np

class CustomWriter(rep.Writer):
    """Custom data writer."""

    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.frame_id = 0

    def write(self, data):
        """Process and save frame data."""

        # Save RGB image
        rgb = data.get("rgb")
        if rgb is not None:
            rgb_path = f"{self.output_dir}/rgb/{self.frame_id:06d}.png"
            self._save_image(rgb, rgb_path)

        # Save bounding boxes
        boxes = data.get("bounding_box_2d_tight")
        if boxes is not None:
            boxes_path = f"{self.output_dir}/labels/{self.frame_id:06d}.json"
            self._save_json(boxes, boxes_path)

        self.frame_id += 1

    def _save_image(self, data, path):
        from PIL import Image
        Image.fromarray(data).save(path)

    def _save_json(self, data, path):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

# Register custom writer
rep.WriterRegistry.register(CustomWriter)
```

## Robot-Specific Data Generation

### Generating Manipulation Data

```python
def generate_manipulation_dataset():
    """Generate dataset for robotic manipulation."""

    # Setup robot and objects
    robot = rep.create.from_usd(
        "/Isaac/Robots/Franka/franka.usd",
        semantics=[("class", "robot")]
    )

    # Objects to manipulate
    objects = []
    for i in range(5):
        obj = rep.create.cube(
            position=(0.5 + i*0.1, 0, 0.02),
            scale=(0.04, 0.04, 0.04),
            semantics=[("class", "object"), ("instance", f"obj_{i}")]
        )
        objects.append(obj)

    # Camera on robot end-effector
    camera = rep.create.camera(
        position=(0, 0, 0),
        parent="/World/Robot/panda_hand"
    )

    # Randomize for each frame
    with rep.trigger.on_frame(num_frames=1000):
        for obj in objects:
            with obj:
                rep.modify.pose(
                    position=rep.distribution.uniform(
                        (0.3, -0.3, 0.02),
                        (0.7, 0.3, 0.02)
                    ),
                    rotation=rep.distribution.uniform(
                        (0, 0, 0), (0, 0, 360)
                    )
                )

    # Output
    render_product = rep.create.render_product(camera, (640, 480))
    writer = rep.WriterRegistry.get("BasicWriter")
    writer.initialize(
        output_dir="/output/manipulation_dataset",
        rgb=True,
        bounding_box_2d_tight=True,
        semantic_segmentation=True,
        depth=True,
    )
    writer.attach([render_product])

    rep.orchestrator.run()
```

### Generating Navigation Data

```python
def generate_navigation_dataset():
    """Generate dataset for robot navigation."""

    # Create warehouse environment
    warehouse = rep.create.from_usd(
        "/Isaac/Environments/Simple_Warehouse/warehouse.usd"
    )

    # Add obstacles with semantics
    obstacle_positions = [
        (2, 1, 0), (3, -2, 0), (-1, 3, 0), (4, 4, 0)
    ]

    for i, pos in enumerate(obstacle_positions):
        rep.create.cube(
            position=pos,
            scale=(0.5, 0.5, 1.0),
            semantics=[("class", "obstacle")]
        )

    # Robot with LIDAR camera
    robot_camera = rep.create.camera(
        position=(0, 0, 0.5),
        rotation=(0, 0, 0),
        focal_length=18  # Wide angle
    )

    # Generate path variations
    with rep.trigger.on_frame(num_frames=500):
        with rep.get.prims(path_pattern="/Replicator/Camera"):
            rep.modify.pose(
                position=rep.distribution.uniform(
                    (-5, -5, 0.5), (5, 5, 0.5)
                ),
                rotation=rep.distribution.uniform(
                    (0, 0, 0), (0, 0, 360)
                )
            )

    # Output with depth for obstacle detection
    render_product = rep.create.render_product(robot_camera, (320, 240))
    writer = rep.WriterRegistry.get("BasicWriter")
    writer.initialize(
        output_dir="/output/navigation_dataset",
        rgb=True,
        depth=True,
        semantic_segmentation=True,
    )
    writer.attach([render_product])

    rep.orchestrator.run()
```

## Training with Synthetic Data

### Using with PyTorch

```python
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import json
import os

class SyntheticDataset(Dataset):
    """PyTorch dataset for synthetic data."""

    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform

        # Load annotations
        with open(os.path.join(data_dir, "annotations.json")) as f:
            self.annotations = json.load(f)

        self.image_ids = list(self.annotations.keys())

    def __len__(self):
        return len(self.image_ids)

    def __getitem__(self, idx):
        image_id = self.image_ids[idx]

        # Load image
        image_path = os.path.join(self.data_dir, "rgb", f"{image_id}.png")
        image = Image.open(image_path).convert("RGB")

        # Load labels
        labels = self.annotations[image_id]
        boxes = torch.tensor(labels["boxes"], dtype=torch.float32)
        classes = torch.tensor(labels["classes"], dtype=torch.long)

        if self.transform:
            image = self.transform(image)

        return image, {"boxes": boxes, "labels": classes}

# Create dataloader
dataset = SyntheticDataset("/output/dataset")
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
```

### Mixed Training (Synthetic + Real)

```python
from torch.utils.data import ConcatDataset

# Combine synthetic and real datasets
synthetic_dataset = SyntheticDataset("/output/synthetic")
real_dataset = RealDataset("/data/real_images")

# Weight synthetic data less (optional)
combined_dataset = ConcatDataset([
    synthetic_dataset,
    real_dataset,
    real_dataset,  # Duplicate real data to increase weight
])

dataloader = DataLoader(combined_dataset, batch_size=32, shuffle=True)
```

---

## Exercise: Generate Object Detection Dataset

Create a synthetic dataset for training an object detection model.

### Requirements

1. Create a scene with 5 different object types
2. Add semantic labels to each object type
3. Configure domain randomization:
   - Object positions and rotations
   - Lighting intensity and direction
   - Camera viewpoint
4. Generate 500 frames with bounding box annotations
5. Output in COCO format

### Expected Outcome

- 500 RGB images with varied conditions
- COCO-format annotations file
- Class distribution across all images
- Ready for training with Detectron2 or YOLO

### Starter Code

```python
import omni.replicator.core as rep

# TODO: Setup scene with labeled objects
# TODO: Configure randomizers
# TODO: Setup COCO writer
# TODO: Generate dataset

rep.orchestrator.run()
```

---

## Summary

Synthetic data generation accelerates perception model development:

- **Cost effective**: Generate millions of labeled images
- **Perfect labels**: Pixel-accurate ground truth
- **Edge cases**: Create rare scenarios easily
- **Domain randomization**: Built-in for robustness

Key skills learned:
- Creating scenes with semantic labels
- Configuring data randomization
- Outputting standard formats (COCO, KITTI)
- Integrating with training pipelines

In the next chapter, you will learn about Isaac ROS for deploying AI on real robots.

**Next:** [Isaac ROS Deployment](./6-isaac-ros)
