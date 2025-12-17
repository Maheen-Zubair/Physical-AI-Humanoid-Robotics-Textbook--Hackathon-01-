---
sidebar_position: 4
sidebar_label: "4.4 Action Generation"
title: "Chapter 4.4: Action Generation with VLA Models"
description: "Learn how to generate robot actions from vision and language using RT-2 and OpenVLA"
keywords: [rt-2, openvla, action generation, robotics, vla, manipulation]
---

# Action Generation with VLA Models

In this chapter, you will learn how Vision-Language-Action (VLA) models generate robot actions from visual observations and language instructions, focusing on RT-2 and OpenVLA architectures.

## Action Generation Overview

VLA models generate actions by treating them as a prediction problem:

```
┌─────────────────────────────────────────────────────────────┐
│                  VLA Action Generation                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Inputs:                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Camera    │  │ Instruction │  │  Robot      │         │
│  │   Image     │  │   "Pick up  │  │  State      │         │
│  │             │  │   the cup"  │  │  (joints)   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         └────────────────┼────────────────┘                 │
│                          ▼                                   │
│         ┌────────────────────────────────┐                  │
│         │        VLA Transformer         │                  │
│         │   (Vision + Language + Action) │                  │
│         └────────────────┬───────────────┘                  │
│                          ▼                                   │
│  Output:      ┌─────────────────────────┐                   │
│               │   Action: [Δx, Δy, Δz,  │                   │
│               │    Δroll, Δpitch, Δyaw, │                   │
│               │    gripper_open]        │                   │
│               └─────────────────────────┘                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## RT-2: Robotic Transformer 2

### Architecture

**RT-2** from Google DeepMind treats actions as language tokens:

```python
# Conceptual RT-2 architecture
class RT2(nn.Module):
    """RT-2: Vision-Language-Action model."""

    def __init__(self, vlm_backbone, action_dim=7, action_bins=256):
        super().__init__()

        # Pre-trained vision-language model
        self.vlm = vlm_backbone  # PaLI-X or PaLM-E

        # Action tokenization
        self.action_bins = action_bins
        self.action_dim = action_dim

        # Action embedding layer
        self.action_embeddings = nn.Embedding(
            action_bins * action_dim,
            vlm_backbone.hidden_dim
        )

    def discretize_action(self, continuous_action):
        """Convert continuous action to discrete tokens."""
        # Normalize to [0, 1]
        normalized = (continuous_action + 1) / 2  # Assuming [-1, 1] range

        # Discretize to bins
        tokens = (normalized * (self.action_bins - 1)).long()

        return tokens

    def continuous_action(self, action_tokens):
        """Convert discrete tokens back to continuous actions."""
        normalized = action_tokens.float() / (self.action_bins - 1)
        continuous = normalized * 2 - 1  # Back to [-1, 1]

        return continuous

    def forward(self, image, instruction, robot_state=None):
        """Generate action from observation and instruction."""

        # Encode image and text through VLM
        visual_tokens = self.vlm.encode_image(image)
        text_tokens = self.vlm.encode_text(instruction)

        # Combine inputs
        combined = torch.cat([visual_tokens, text_tokens], dim=1)

        # Generate action tokens autoregressively
        action_tokens = []
        for i in range(self.action_dim):
            logits = self.vlm.decode(combined)
            next_token = logits.argmax(dim=-1)
            action_tokens.append(next_token)

            # Add to context for next prediction
            token_embed = self.action_embeddings(next_token + i * self.action_bins)
            combined = torch.cat([combined, token_embed], dim=1)

        # Convert to continuous action
        action_tokens = torch.stack(action_tokens, dim=-1)
        action = self.continuous_action(action_tokens)

        return action
```

### Action Tokenization

RT-2 represents actions as discrete tokens:

| Dimension | Range | Bins | Example Token |
|-----------|-------|------|---------------|
| x (forward) | [-0.1m, 0.1m] | 256 | Token 145 = +0.03m |
| y (left) | [-0.1m, 0.1m] | 256 | Token 128 = 0.0m |
| z (up) | [-0.1m, 0.1m] | 256 | Token 200 = +0.06m |
| roll | [-π/4, π/4] | 256 | Token 128 = 0.0 rad |
| pitch | [-π/4, π/4] | 256 | Token 64 = -0.2 rad |
| yaw | [-π/4, π/4] | 256 | Token 192 = +0.4 rad |
| gripper | [0, 1] | 256 | Token 255 = closed |

## OpenVLA: Open Vision-Language-Action

### Overview

**OpenVLA** is an open-source VLA model:

- **7B parameters** based on Llama 2
- **Open weights** for research
- **970K trajectories** training data
- **Prismatic VLM** vision encoder

### Installation

```bash
# Clone OpenVLA
git clone https://github.com/openvla/openvla.git
cd openvla

# Install dependencies
pip install -e .

# Download model weights
python -c "from openvla import OpenVLA; model = OpenVLA.from_pretrained('openvla/openvla-7b')"
```

### Basic Inference

```python
from openvla import OpenVLA
from PIL import Image
import torch

# Load model
model = OpenVLA.from_pretrained(
    "openvla/openvla-7b",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

def get_action(image_path, instruction):
    """Get robot action from image and instruction."""

    # Load image
    image = Image.open(image_path)

    # Generate action
    action = model.predict_action(
        image=image,
        instruction=instruction,
        unnorm_key="bridge_orig"  # Action normalization key
    )

    return action

# Usage
action = get_action(
    "robot_camera.jpg",
    "Pick up the red block and place it on the blue block"
)

print(f"Action: x={action[0]:.3f}, y={action[1]:.3f}, z={action[2]:.3f}")
print(f"Rotation: roll={action[3]:.3f}, pitch={action[4]:.3f}, yaw={action[5]:.3f}")
print(f"Gripper: {action[6]:.3f}")
```

### Action Space

OpenVLA typically outputs 7-DoF actions:

```python
@dataclass
class RobotAction:
    """7-DoF robot action."""

    # End-effector translation (meters)
    delta_x: float  # Forward/backward
    delta_y: float  # Left/right
    delta_z: float  # Up/down

    # End-effector rotation (radians)
    delta_roll: float
    delta_pitch: float
    delta_yaw: float

    # Gripper state
    gripper: float  # 0=open, 1=closed

    def to_array(self):
        return np.array([
            self.delta_x, self.delta_y, self.delta_z,
            self.delta_roll, self.delta_pitch, self.delta_yaw,
            self.gripper
        ])
```

## Closed-Loop Control

### Action Execution Loop

```python
class VLAController:
    """Closed-loop VLA control."""

    def __init__(self, model, robot, camera):
        self.model = model
        self.robot = robot
        self.camera = camera
        self.control_rate = 10  # Hz

    def execute_instruction(self, instruction, max_steps=100):
        """Execute instruction using VLA model."""

        for step in range(max_steps):
            # Get current observation
            image = self.camera.get_image()

            # Predict action
            action = self.model.predict_action(
                image=image,
                instruction=instruction
            )

            # Safety check
            if not self.is_action_safe(action):
                print("Unsafe action detected, stopping")
                break

            # Execute action
            self.robot.step(action)

            # Check if task complete
            if self.is_task_complete(image, instruction):
                print(f"Task completed in {step} steps")
                return True

            # Rate limiting
            time.sleep(1.0 / self.control_rate)

        print("Max steps reached")
        return False

    def is_action_safe(self, action):
        """Check if action is within safe bounds."""
        # Position limits
        if abs(action[0]) > 0.1 or abs(action[1]) > 0.1 or abs(action[2]) > 0.1:
            return False

        # Rotation limits
        if abs(action[3]) > 0.5 or abs(action[4]) > 0.5 or abs(action[5]) > 0.5:
            return False

        return True

    def is_task_complete(self, image, instruction):
        """Check if task is complete (can use vision model)."""
        # This could use another vision model to verify completion
        return False
```

### Multi-Step Task Execution

```python
class TaskExecutor:
    """Execute multi-step tasks with VLA."""

    def __init__(self, vla_model, robot, camera):
        self.vla = VLAController(vla_model, robot, camera)

    def execute_compound_task(self, task_description):
        """Execute a compound task by breaking it down."""

        # Use LLM to decompose task
        subtasks = self.decompose_task(task_description)

        results = []
        for subtask in subtasks:
            print(f"Executing: {subtask}")
            success = self.vla.execute_instruction(subtask)
            results.append({"task": subtask, "success": success})

            if not success:
                print(f"Failed at subtask: {subtask}")
                break

        return results

    def decompose_task(self, task):
        """Break complex task into subtasks."""
        # This could use an LLM for decomposition
        # Simple example:
        if "pick up" in task.lower() and "place" in task.lower():
            obj = self._extract_object(task)
            location = self._extract_location(task)
            return [
                f"Move above the {obj}",
                f"Lower gripper to {obj}",
                f"Close gripper on {obj}",
                f"Lift {obj}",
                f"Move to {location}",
                f"Lower {obj}",
                f"Open gripper",
                f"Retract arm"
            ]
        return [task]
```

## ROS 2 Integration

### VLA Action Server

```python
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image, JointState
from std_msgs.msg import String
from cv_bridge import CvBridge
from robot_interfaces.action import ExecuteInstruction  # Custom action

class VLAActionServer(Node):
    def __init__(self):
        super().__init__('vla_action_server')

        # Load VLA model
        from openvla import OpenVLA
        self.model = OpenVLA.from_pretrained("openvla/openvla-7b")
        self.get_logger().info("VLA model loaded")

        # CV Bridge
        self.bridge = CvBridge()
        self.current_image = None

        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Action publisher
        self.action_pub = self.create_publisher(
            JointState,
            '/robot/joint_commands',
            10
        )

        # Action server
        self._action_server = ActionServer(
            self,
            ExecuteInstruction,
            'execute_instruction',
            self.execute_callback
        )

    def image_callback(self, msg):
        self.current_image = self.bridge.imgmsg_to_cv2(msg, "rgb8")

    async def execute_callback(self, goal_handle):
        """Execute VLA instruction."""
        instruction = goal_handle.request.instruction
        self.get_logger().info(f"Executing: {instruction}")

        feedback = ExecuteInstruction.Feedback()
        result = ExecuteInstruction.Result()

        step = 0
        max_steps = goal_handle.request.max_steps or 100

        while step < max_steps:
            if self.current_image is None:
                await asyncio.sleep(0.1)
                continue

            # Get action from VLA
            image_pil = Image.fromarray(self.current_image)
            action = self.model.predict_action(
                image=image_pil,
                instruction=instruction
            )

            # Publish action
            self.publish_action(action)

            # Send feedback
            feedback.current_step = step
            feedback.action = action.tolist()
            goal_handle.publish_feedback(feedback)

            step += 1
            await asyncio.sleep(0.1)  # 10 Hz control

        result.success = True
        result.steps_executed = step
        goal_handle.succeed()

        return result

    def publish_action(self, action):
        """Publish action to robot."""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.position = action[:6].tolist()  # Joint positions
        msg.velocity = [0.0] * 6
        self.action_pub.publish(msg)

def main():
    rclpy.init()
    node = VLAActionServer()
    rclpy.spin(node)
    rclpy.shutdown()
```

## Fine-Tuning for Custom Tasks

### Data Collection

```python
class TrajectoryCollector:
    """Collect demonstration data for fine-tuning."""

    def __init__(self, robot, camera, save_dir):
        self.robot = robot
        self.camera = camera
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

        self.current_trajectory = []
        self.trajectory_count = 0

    def start_trajectory(self, instruction):
        """Start recording a new trajectory."""
        self.current_trajectory = []
        self.current_instruction = instruction
        self.recording = True
        print(f"Recording: {instruction}")

    def record_step(self, action):
        """Record a single step."""
        if not self.recording:
            return

        step_data = {
            "image": self.camera.get_image(),
            "action": action,
            "instruction": self.current_instruction,
            "timestamp": time.time()
        }
        self.current_trajectory.append(step_data)

    def end_trajectory(self, success=True):
        """End and save trajectory."""
        self.recording = False

        if success and len(self.current_trajectory) > 0:
            # Save trajectory
            traj_path = self.save_dir / f"trajectory_{self.trajectory_count:04d}"
            traj_path.mkdir()

            for i, step in enumerate(self.current_trajectory):
                # Save image
                img_path = traj_path / f"image_{i:04d}.jpg"
                Image.fromarray(step["image"]).save(img_path)

                # Save action
                action_path = traj_path / f"action_{i:04d}.npy"
                np.save(action_path, step["action"])

            # Save metadata
            metadata = {
                "instruction": self.current_instruction,
                "num_steps": len(self.current_trajectory),
                "success": success
            }
            with open(traj_path / "metadata.json", "w") as f:
                json.dump(metadata, f)

            self.trajectory_count += 1
            print(f"Saved trajectory {self.trajectory_count}")
```

### Fine-Tuning Script

```python
from transformers import Trainer, TrainingArguments
from openvla import OpenVLA, OpenVLADataset

def fine_tune_openvla(data_dir, output_dir, epochs=10):
    """Fine-tune OpenVLA on custom data."""

    # Load model
    model = OpenVLA.from_pretrained("openvla/openvla-7b")

    # Create dataset
    dataset = OpenVLADataset(data_dir)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=8,
        learning_rate=2e-5,
        weight_decay=0.01,
        logging_steps=10,
        save_steps=500,
        fp16=True,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )

    # Train
    trainer.train()

    # Save
    trainer.save_model(output_dir)

# Usage
fine_tune_openvla(
    data_dir="collected_trajectories/",
    output_dir="custom_openvla/",
    epochs=10
)
```

---

## Exercise: Implement VLA Control Loop

Create a complete VLA control system.

### Requirements

1. Load OpenVLA (or mock with simpler model)
2. Implement closed-loop control with:
   - Image observation
   - Instruction input
   - Action execution
3. Add safety constraints
4. Track task progress

### Expected Outcome

```python
# Example usage
controller = VLAController(model, robot, camera)

# Execute instruction
success = controller.execute_instruction(
    "Pick up the red block",
    max_steps=50
)

print(f"Task success: {success}")
```

---

## Summary

VLA models enable end-to-end robot control from natural language:

- **RT-2**: Actions as language tokens
- **OpenVLA**: Open-source 7B parameter model
- **Action representation**: Discretized or continuous
- **Closed-loop control**: Continuous observation-action

Key implementation patterns:
- Tokenize actions for transformer processing
- Use safety bounds on generated actions
- Implement closed-loop control with feedback
- Fine-tune on domain-specific data

In the next chapter, you will learn about end-to-end robot control integration.

**Next:** [End-to-End Integration](./5-integration.md)
