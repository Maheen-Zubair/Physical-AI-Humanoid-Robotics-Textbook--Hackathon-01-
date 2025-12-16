---
sidebar_position: 3
sidebar_label: "3.3 Domain Randomization"
title: "Chapter 3.3: Domain Randomization for Sim-to-Real"
description: "Learn techniques to bridge the simulation-to-reality gap using domain randomization"
keywords: [domain randomization, sim-to-real, transfer learning, robustness, training]
---

# Domain Randomization for Sim-to-Real

In this chapter, you will learn how to use domain randomization to train robust robot policies that transfer effectively from simulation to the real world.

## The Sim-to-Real Gap

Policies trained purely in simulation often fail when deployed on real robots. This **sim-to-real gap** arises from:

### Sources of the Gap

| Source | Simulation | Reality |
|--------|------------|---------|
| **Physics** | Idealized equations | Complex interactions |
| **Sensors** | Perfect or simple noise | Complex noise patterns |
| **Actuators** | Instant response | Delays and friction |
| **Lighting** | Uniform | Variable |
| **Objects** | Exact geometry | Manufacturing variance |
| **Environment** | Controlled | Unpredictable |

### The Domain Randomization Solution

Instead of making simulation more accurate (which is expensive and never perfect), **domain randomization** trains policies to be robust to variation:

```
┌─────────────────────────────────────────────────────────────┐
│              Domain Randomization Concept                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Simulation                        Reality                  │
│   ┌─────────────────────┐          ┌─────────────────┐     │
│   │ ○ ● ○ ● ○ ● ○ ● ○  │          │                 │     │
│   │  Randomized         │   ───▶   │   ★ Real World  │     │
│   │  Parameters         │          │   (One Point)   │     │
│   │ ● ○ ● ○ ● ○ ● ○ ●  │          │                 │     │
│   └─────────────────────┘          └─────────────────┘     │
│                                                              │
│   If policy works across all ○ and ●,                       │
│   it likely works for ★                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Types of Randomization

### Visual Randomization

Vary appearance to train perception models:

```python
import numpy as np
from omni.isaac.core.prims import XFormPrim
from pxr import UsdShade, Sdf

class VisualRandomizer:
    def __init__(self, stage):
        self.stage = stage

    def randomize_color(self, prim_path):
        """Randomize object color"""
        prim = self.stage.GetPrimAtPath(prim_path)
        material = UsdShade.Material.Get(self.stage, prim_path + "/Material")

        if material:
            shader = material.GetSurfaceOutput().GetConnectedSource()[0]
            color_input = shader.GetInput("diffuseColor")
            random_color = (
                np.random.uniform(0, 1),
                np.random.uniform(0, 1),
                np.random.uniform(0, 1)
            )
            color_input.Set(random_color)

    def randomize_lighting(self, light_path):
        """Randomize light intensity and color"""
        light_prim = self.stage.GetPrimAtPath(light_path)

        # Randomize intensity
        intensity = np.random.uniform(500, 2000)
        light_prim.GetAttribute("inputs:intensity").Set(intensity)

        # Randomize color temperature
        color_temp = np.random.uniform(3000, 7000)
        light_prim.GetAttribute("inputs:colorTemperature").Set(color_temp)

    def randomize_texture(self, prim_path, texture_paths):
        """Randomly select texture"""
        texture = np.random.choice(texture_paths)
        # Apply texture to material
        # Implementation depends on material setup
```

### Physics Randomization

Vary physical properties to handle real-world uncertainty:

```python
from pxr import UsdPhysics, PhysxSchema

class PhysicsRandomizer:
    def __init__(self, stage):
        self.stage = stage

    def randomize_mass(self, prim_path, mean, std):
        """Randomize object mass"""
        prim = self.stage.GetPrimAtPath(prim_path)
        mass_api = UsdPhysics.MassAPI(prim)

        random_mass = np.random.normal(mean, std)
        random_mass = max(0.01, random_mass)  # Ensure positive
        mass_api.GetMassAttr().Set(random_mass)

    def randomize_friction(self, material_path, mu_range):
        """Randomize friction coefficient"""
        prim = self.stage.GetPrimAtPath(material_path)
        physics_material = UsdPhysics.MaterialAPI(prim)

        mu = np.random.uniform(mu_range[0], mu_range[1])
        physics_material.GetStaticFrictionAttr().Set(mu)
        physics_material.GetDynamicFrictionAttr().Set(mu * 0.8)

    def randomize_joint_properties(self, robot_path):
        """Randomize joint damping and friction"""
        robot_prim = self.stage.GetPrimAtPath(robot_path)

        for prim in Usd.PrimRange(robot_prim):
            if prim.IsA(UsdPhysics.Joint):
                # Randomize damping
                damping = np.random.uniform(0.1, 1.0)
                prim.GetAttribute("physics:jointDamping").Set(damping)

                # Randomize friction
                friction = np.random.uniform(0.01, 0.1)
                prim.GetAttribute("physics:jointFriction").Set(friction)
```

### Dynamics Randomization

Vary robot dynamics parameters:

```python
class DynamicsRandomizer:
    def __init__(self, robot):
        self.robot = robot
        self.default_gains = self.robot.get_gains()

    def randomize_control_gains(self, variation=0.2):
        """Randomize PD control gains"""
        kp_default, kd_default = self.default_gains

        # Random scaling factors
        kp_scale = np.random.uniform(1 - variation, 1 + variation, len(kp_default))
        kd_scale = np.random.uniform(1 - variation, 1 + variation, len(kd_default))

        new_kp = kp_default * kp_scale
        new_kd = kd_default * kd_scale

        self.robot.set_gains(new_kp, new_kd)

    def randomize_motor_strength(self, max_effort, variation=0.1):
        """Randomize motor strength limits"""
        effort_scale = np.random.uniform(1 - variation, 1 + variation)
        return max_effort * effort_scale

    def add_action_noise(self, action, noise_std=0.02):
        """Add noise to actions"""
        noise = np.random.normal(0, noise_std, action.shape)
        return action + noise

    def add_observation_noise(self, obs, noise_config):
        """Add noise to observations"""
        noisy_obs = obs.copy()

        for key, noise_std in noise_config.items():
            if key in noisy_obs:
                noise = np.random.normal(0, noise_std, noisy_obs[key].shape)
                noisy_obs[key] += noise

        return noisy_obs
```

## Isaac Lab Randomization

Isaac Lab provides built-in randomization through configuration:

### Environment Configuration

```python
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import EventTermCfg, SceneEntityCfg
from isaaclab.utils import configclass

@configclass
class RandomizationCfg:
    """Configuration for domain randomization."""

    # Physics randomization at episode start
    @configclass
    class PhysicsRandomization:
        # Randomize robot base mass
        robot_mass = EventTermCfg(
            func=randomize_mass,
            mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("robot"),
                "mass_range": (0.8, 1.2),  # Scale factor
            }
        )

        # Randomize friction
        ground_friction = EventTermCfg(
            func=randomize_friction,
            mode="reset",
            params={
                "asset_cfg": SceneEntityCfg("ground"),
                "friction_range": (0.5, 1.5),
            }
        )

    # Visual randomization
    @configclass
    class VisualRandomization:
        # Randomize lighting
        lighting = EventTermCfg(
            func=randomize_lighting,
            mode="reset",
            params={
                "intensity_range": (0.5, 1.5),
                "color_range": (0.8, 1.2),
            }
        )

    physics = PhysicsRandomization()
    visual = VisualRandomization()
```

### Action and Observation Noise

```python
@configclass
class NoiseCfg:
    """Configuration for noise injection."""

    # Add noise to actions
    action_noise = EventTermCfg(
        func=add_gaussian_noise,
        mode="interval",
        interval=1,
        params={"std": 0.05}
    )

    # Add noise to observations
    observation_noise = EventTermCfg(
        func=add_gaussian_noise,
        mode="interval",
        interval=1,
        params={
            "joint_pos_std": 0.01,
            "joint_vel_std": 0.1,
            "imu_std": 0.05,
        }
    )
```

## Implementing Randomization

### Complete Randomization Class

```python
import numpy as np
from typing import Dict, Tuple, Optional

class DomainRandomization:
    """Complete domain randomization for robotics training."""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get("enabled", True)

    def randomize_physics(self, env) -> None:
        """Apply physics randomization."""
        if not self.enabled:
            return

        cfg = self.config.get("physics", {})

        # Mass randomization
        if "mass" in cfg:
            mass_range = cfg["mass"]
            for robot in env.robots:
                base_mass = robot.get_default_mass()
                scale = np.random.uniform(mass_range[0], mass_range[1])
                robot.set_mass(base_mass * scale)

        # Friction randomization
        if "friction" in cfg:
            friction_range = cfg["friction"]
            mu = np.random.uniform(friction_range[0], friction_range[1])
            env.ground.set_friction(mu)

        # Joint properties
        if "joint_damping" in cfg:
            damping_range = cfg["joint_damping"]
            for robot in env.robots:
                for joint in robot.joints:
                    damping = np.random.uniform(damping_range[0], damping_range[1])
                    joint.set_damping(damping)

    def randomize_visual(self, env) -> None:
        """Apply visual randomization."""
        if not self.enabled:
            return

        cfg = self.config.get("visual", {})

        # Lighting
        if "lighting" in cfg:
            light_cfg = cfg["lighting"]
            for light in env.lights:
                intensity = np.random.uniform(
                    light_cfg["intensity"][0],
                    light_cfg["intensity"][1]
                )
                light.set_intensity(intensity)

                if "color" in light_cfg:
                    color = np.random.uniform(0.8, 1.0, 3)
                    light.set_color(color)

        # Object colors
        if "colors" in cfg:
            for obj in env.objects:
                color = np.random.uniform(0, 1, 3)
                obj.set_color(color)

    def add_observation_noise(self, obs: Dict) -> Dict:
        """Add noise to observations."""
        if not self.enabled:
            return obs

        cfg = self.config.get("observation_noise", {})
        noisy_obs = {}

        for key, value in obs.items():
            if key in cfg:
                noise_std = cfg[key]
                noise = np.random.normal(0, noise_std, value.shape)
                noisy_obs[key] = value + noise
            else:
                noisy_obs[key] = value

        return noisy_obs

    def add_action_noise(self, action: np.ndarray) -> np.ndarray:
        """Add noise to actions."""
        if not self.enabled:
            return action

        cfg = self.config.get("action_noise", {})
        noise_std = cfg.get("std", 0.0)

        if noise_std > 0:
            noise = np.random.normal(0, noise_std, action.shape)
            return action + noise

        return action

    def apply_action_delay(self, action: np.ndarray, delay_buffer: list) -> np.ndarray:
        """Simulate action delay."""
        cfg = self.config.get("action_delay", {})
        delay_steps = cfg.get("steps", 0)

        if delay_steps > 0:
            delay_buffer.append(action)
            if len(delay_buffer) > delay_steps:
                return delay_buffer.pop(0)
            return delay_buffer[0]

        return action
```

### Using Randomization in Training

```python
# Configuration
randomization_config = {
    "enabled": True,
    "physics": {
        "mass": (0.8, 1.2),
        "friction": (0.4, 1.0),
        "joint_damping": (0.5, 2.0),
    },
    "visual": {
        "lighting": {
            "intensity": (0.5, 1.5),
        },
    },
    "observation_noise": {
        "joint_positions": 0.01,
        "joint_velocities": 0.1,
        "base_orientation": 0.02,
    },
    "action_noise": {
        "std": 0.02,
    },
    "action_delay": {
        "steps": 1,
    },
}

# Create randomizer
randomizer = DomainRandomization(randomization_config)

# Training loop
for episode in range(num_episodes):
    # Randomize at episode start
    randomizer.randomize_physics(env)
    randomizer.randomize_visual(env)

    obs = env.reset()
    done = False

    while not done:
        # Add observation noise
        noisy_obs = randomizer.add_observation_noise(obs)

        # Get action from policy
        action = policy(noisy_obs)

        # Add action noise and delay
        noisy_action = randomizer.add_action_noise(action)

        # Step environment
        obs, reward, done, info = env.step(noisy_action)
```

## Best Practices

### Randomization Ranges

| Parameter | Conservative | Aggressive |
|-----------|--------------|------------|
| Mass | ±10% | ±30% |
| Friction | 0.6-1.0 | 0.3-1.5 |
| Joint damping | ±20% | ±50% |
| Action noise | 0.01 | 0.05 |
| Observation noise | 0.5% | 2% |

### Progressive Randomization

Start with less randomization and increase during training:

```python
class ProgressiveRandomization:
    def __init__(self, initial_scale=0.1, final_scale=1.0, warmup_steps=10000):
        self.initial_scale = initial_scale
        self.final_scale = final_scale
        self.warmup_steps = warmup_steps
        self.current_step = 0

    def get_scale(self):
        if self.current_step >= self.warmup_steps:
            return self.final_scale

        progress = self.current_step / self.warmup_steps
        return self.initial_scale + (self.final_scale - self.initial_scale) * progress

    def step(self):
        self.current_step += 1

    def scale_range(self, range_tuple):
        scale = self.get_scale()
        center = (range_tuple[0] + range_tuple[1]) / 2
        half_width = (range_tuple[1] - range_tuple[0]) / 2 * scale
        return (center - half_width, center + half_width)
```

---

## Exercise: Implement Domain Randomization

Create a randomization system for a manipulation task.

### Requirements

1. Randomize object properties:
   - Mass (±20%)
   - Friction (0.3-0.8)
   - Size (±10%)
2. Randomize robot properties:
   - Joint damping (±30%)
   - Control gains (±15%)
3. Add observation noise:
   - Joint positions (σ=0.01)
   - Joint velocities (σ=0.1)
4. Track which randomizations improve transfer

### Expected Outcome

- Policy trained with randomization performs better in varied conditions
- Documented which randomizations have the most impact
- Quantified improvement in robustness

---

## Summary

Domain randomization is essential for sim-to-real transfer:

- **Visual randomization**: Colors, textures, lighting
- **Physics randomization**: Mass, friction, dynamics
- **Noise injection**: Actions and observations
- **Progressive training**: Start simple, increase complexity

Key principles:
- Randomize parameters that differ between sim and real
- Use reasonable ranges based on real-world variance
- Monitor training stability with randomization
- Validate on held-out randomization settings

In the next chapter, you will learn to use Isaac Lab for reinforcement learning.

**Next:** [Isaac Lab and RL](./4-isaac-lab)
