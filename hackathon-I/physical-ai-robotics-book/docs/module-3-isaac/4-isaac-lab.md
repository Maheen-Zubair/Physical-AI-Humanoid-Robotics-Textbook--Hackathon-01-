---
sidebar_position: 4
sidebar_label: "3.4 Isaac Lab"
title: "Chapter 3.4: Reinforcement Learning with Isaac Lab"
description: "Learn to train robot policies using Isaac Lab's RL framework"
keywords: [isaac lab, reinforcement learning, ppo, training, robot learning]
---

# Reinforcement Learning with Isaac Lab

In this chapter, you will learn how to use Isaac Lab to train robot policies using reinforcement learning, leveraging GPU acceleration for massively parallel training.

## What is Isaac Lab?

**Isaac Lab** (formerly Orbit) is a framework for robot learning built on Isaac Sim:

- **Parallel environments**: Train on thousands of robots simultaneously
- **RL libraries**: Integration with PPO, SAC, and other algorithms
- **Pre-built tasks**: Locomotion, manipulation, navigation
- **Modular design**: Easy to create custom environments

```
┌─────────────────────────────────────────────────────────────┐
│                    Isaac Lab Architecture                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  RL Agent   │  │   Policy    │  │   Reward    │         │
│  │  (rl_games) │  │  Network    │  │  Function   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┴────────────────┘                 │
│                          │                                  │
│  ┌───────────────────────▼─────────────────────────────┐   │
│  │              Isaac Lab Environment                   │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │ Env 0   │ │ Env 1   │ │  ...    │ │Env 4095 │   │   │
│  │  │ Robot   │ │ Robot   │ │         │ │ Robot   │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌───────────────────────▼─────────────────────────────┐   │
│  │                   Isaac Sim (PhysX 5)                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Getting Started

### Installation

```bash
# Clone Isaac Lab
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

# Create environment
conda create -n isaaclab python=3.10
conda activate isaaclab

# Install
./isaaclab.sh --install

# Verify installation
./isaaclab.sh -p scripts/tutorials/00_sim/spawn_prims.py
```

### Running Your First Training

```bash
# Train a quadruped robot to walk
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Anymal-D-v0 \
    --num_envs 4096 \
    --headless

# Watch the trained policy
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Velocity-Flat-Anymal-D-v0 \
    --num_envs 32
```

## Understanding Environments

### Environment Structure

An Isaac Lab environment consists of:

```python
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
from isaaclab.utils import configclass

@configclass
class MyEnvCfg(DirectRLEnvCfg):
    """Configuration for my custom environment."""

    # Environment settings
    decimation = 4  # Control frequency = physics_freq / decimation
    episode_length_s = 10.0  # Episode length in seconds

    # Observation and action spaces
    observation_space = 48  # Number of observations
    action_space = 12  # Number of actions
    state_space = 0  # For asymmetric training

    # Simulation settings
    sim: SimulationCfg = SimulationCfg(
        dt=1/120,  # Physics timestep
        render_interval=4,
    )

    # Scene settings
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=4096,
        env_spacing=2.5,
    )
```

### Observation Space

Define what the robot observes:

```python
def _get_observations(self) -> dict:
    """Compute observations for the policy."""

    # Base state
    base_quat = self.robot.data.root_quat_w
    base_lin_vel = self.robot.data.root_lin_vel_b
    base_ang_vel = self.robot.data.root_ang_vel_b

    # Projected gravity
    projected_gravity = math_utils.quat_rotate_inverse(
        base_quat,
        self.gravity_vec
    )

    # Joint state
    joint_pos = self.robot.data.joint_pos - self.default_joint_pos
    joint_vel = self.robot.data.joint_vel

    # Commands (target velocity)
    commands = self.command_manager.get_command("base_velocity")

    # Concatenate observations
    obs = torch.cat([
        base_lin_vel,           # 3
        base_ang_vel,           # 3
        projected_gravity,      # 3
        commands,               # 3
        joint_pos,              # 12
        joint_vel,              # 12
        self.actions,           # 12
    ], dim=-1)

    return {"policy": obs}
```

### Action Space

Define how actions control the robot:

```python
def _apply_actions(self):
    """Apply actions to the robot."""

    # Scale actions to joint position targets
    joint_pos_target = self.default_joint_pos + self.actions * self.action_scale

    # Apply PD control
    self.robot.set_joint_position_target(joint_pos_target)
```

### Reward Function

Design rewards to shape desired behavior:

```python
def _get_rewards(self) -> torch.Tensor:
    """Compute rewards for the current step."""

    # Velocity tracking reward
    lin_vel_error = torch.sum(
        torch.square(self.commands[:, :2] - self.base_lin_vel[:, :2]),
        dim=1
    )
    ang_vel_error = torch.square(self.commands[:, 2] - self.base_ang_vel[:, 2])

    velocity_reward = torch.exp(-lin_vel_error / 0.25) * self.reward_scales["velocity"]
    angular_reward = torch.exp(-ang_vel_error / 0.25) * self.reward_scales["angular"]

    # Regularization rewards
    action_rate_reward = -torch.sum(
        torch.square(self.actions - self.last_actions),
        dim=1
    ) * self.reward_scales["action_rate"]

    # Energy efficiency
    torque_reward = -torch.sum(
        torch.abs(self.robot.data.applied_torque),
        dim=1
    ) * self.reward_scales["torque"]

    # Total reward
    reward = velocity_reward + angular_reward + action_rate_reward + torque_reward

    return reward
```

## Creating Custom Environments

### Step 1: Define Configuration

```python
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.assets import ArticulationCfg
from isaaclab.utils import configclass

@configclass
class CartpoleEnvCfg(DirectRLEnvCfg):
    """Configuration for cartpole balancing task."""

    # Environment
    decimation = 2
    episode_length_s = 5.0
    action_scale = 100.0

    # Spaces
    action_space = 1
    observation_space = 4
    state_space = 0

    # Simulation
    sim = SimulationCfg(dt=1/120, render_interval=2)

    # Scene
    scene = InteractiveSceneCfg(num_envs=4096, env_spacing=4.0)

    # Robot
    robot_cfg = ArticulationCfg(
        prim_path="/World/envs/env_.*/Robot",
        spawn=sim_utils.UsdFileCfg(
            usd_path="{ISAAC_NUCLEUS_DIR}/Robots/Simple/cartpole.usd",
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.0),
        ),
        actuators={
            "cart": ImplicitActuatorCfg(
                joint_names_expr=["slider_to_cart"],
                effort_limit=400.0,
                stiffness=0.0,
                damping=10.0,
            ),
        },
    )

    # Termination and reset
    max_cart_pos = 3.0
    initial_pole_angle_range = [-0.25, 0.25]

    # Reward scales
    rew_scale_alive = 1.0
    rew_scale_terminated = -2.0
    rew_scale_pole_pos = -1.0
    rew_scale_cart_vel = -0.01
```

### Step 2: Implement Environment

```python
from isaaclab.envs import DirectRLEnv
import torch

class CartpoleEnv(DirectRLEnv):
    """Cartpole balancing environment."""

    cfg: CartpoleEnvCfg

    def __init__(self, cfg: CartpoleEnvCfg, **kwargs):
        super().__init__(cfg, **kwargs)

        # Get joint indices
        self.cart_dof_idx = self.robot.find_joints("slider_to_cart")[0]
        self.pole_dof_idx = self.robot.find_joints("cart_to_pole")[0]

    def _setup_scene(self):
        """Setup the scene with robot and ground."""
        self.robot = Articulation(self.cfg.robot_cfg)
        self.scene.articulations["robot"] = self.robot

        # Add ground
        self.scene.ground = GroundPlane(self.cfg.ground_cfg)

    def _get_observations(self) -> dict:
        """Get observations: cart pos, cart vel, pole angle, pole vel."""
        joint_pos = self.robot.data.joint_pos
        joint_vel = self.robot.data.joint_vel

        obs = torch.cat([
            joint_pos[:, self.cart_dof_idx].unsqueeze(1),
            joint_vel[:, self.cart_dof_idx].unsqueeze(1),
            joint_pos[:, self.pole_dof_idx].unsqueeze(1),
            joint_vel[:, self.pole_dof_idx].unsqueeze(1),
        ], dim=-1)

        return {"policy": obs}

    def _get_rewards(self) -> torch.Tensor:
        """Compute rewards."""
        joint_pos = self.robot.data.joint_pos
        joint_vel = self.robot.data.joint_vel

        pole_angle = joint_pos[:, self.pole_dof_idx]
        cart_vel = joint_vel[:, self.cart_dof_idx]

        # Alive reward
        reward = self.cfg.rew_scale_alive * torch.ones(self.num_envs, device=self.device)

        # Penalize pole angle
        reward += self.cfg.rew_scale_pole_pos * torch.abs(pole_angle)

        # Penalize cart velocity
        reward += self.cfg.rew_scale_cart_vel * torch.abs(cart_vel)

        # Penalize termination
        reward += self.cfg.rew_scale_terminated * self.reset_terminated.float()

        return reward

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        """Check termination conditions."""
        joint_pos = self.robot.data.joint_pos

        cart_pos = joint_pos[:, self.cart_dof_idx]
        pole_angle = joint_pos[:, self.pole_dof_idx]

        # Terminate if cart out of bounds or pole fallen
        out_of_bounds = torch.abs(cart_pos) > self.cfg.max_cart_pos
        pole_fallen = torch.abs(pole_angle) > 0.5  # ~30 degrees

        terminated = out_of_bounds | pole_fallen
        truncated = self.episode_length_buf >= self.max_episode_length

        return terminated, truncated

    def _reset_idx(self, env_ids: torch.Tensor):
        """Reset specified environments."""
        super()._reset_idx(env_ids)

        # Randomize initial pole angle
        pole_angle = torch.zeros(len(env_ids), device=self.device)
        pole_angle.uniform_(*self.cfg.initial_pole_angle_range)

        # Set initial joint positions
        joint_pos = torch.zeros(len(env_ids), self.robot.num_joints, device=self.device)
        joint_pos[:, self.pole_dof_idx] = pole_angle

        self.robot.write_joint_state_to_sim(
            joint_pos,
            torch.zeros_like(joint_pos),
            env_ids=env_ids,
        )

    def _apply_actions(self):
        """Apply actions to the cart."""
        forces = self.actions * self.cfg.action_scale
        self.robot.set_joint_effort_target(
            forces,
            joint_ids=[self.cart_dof_idx],
        )
```

### Step 3: Register Environment

```python
# In __init__.py of your task package
import gymnasium as gym
from . import cartpole_env

gym.register(
    id="Isaac-Cartpole-Direct-v0",
    entry_point="my_tasks.cartpole:CartpoleEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": "my_tasks.cartpole:CartpoleEnvCfg",
    },
)
```

## Training with RL Libraries

### Using RSL-RL (PPO)

```bash
# Train
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Cartpole-Direct-v0 \
    --num_envs 4096 \
    --headless \
    --max_iterations 500

# Play
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Cartpole-Direct-v0 \
    --num_envs 32
```

### RSL-RL Configuration

```python
from rsl_rl.runners import OnPolicyRunner
from rsl_rl.algorithms import PPO

@configclass
class PPORunnerCfg:
    """Configuration for PPO training."""

    # Runner
    num_steps_per_env = 24
    max_iterations = 1500
    save_interval = 50
    experiment_name = "cartpole"

    # Algorithm
    algorithm = PPOCfg(
        value_loss_coef = 1.0,
        use_clipped_value_loss = True,
        clip_param = 0.2,
        entropy_coef = 0.01,
        num_learning_epochs = 5,
        num_mini_batches = 4,
        learning_rate = 1e-3,
        schedule = "adaptive",
        gamma = 0.99,
        lam = 0.95,
        desired_kl = 0.01,
        max_grad_norm = 1.0,
    )

    # Policy
    policy = ActorCriticCfg(
        init_noise_std = 1.0,
        actor_hidden_dims = [256, 256, 256],
        critic_hidden_dims = [256, 256, 256],
        activation = "elu",
    )
```

### Using Stable-Baselines3

```bash
# Train with SB3
./isaaclab.sh -p scripts/reinforcement_learning/sb3/train.py \
    --task Isaac-Cartpole-Direct-v0 \
    --num_envs 4096 \
    --headless
```

## Monitoring Training

### TensorBoard

```bash
# Start TensorBoard
tensorboard --logdir logs/rsl_rl/

# View at http://localhost:6006
```

### Key Metrics to Watch

| Metric | Good Sign | Bad Sign |
|--------|-----------|----------|
| **Mean reward** | Steadily increasing | Flat or decreasing |
| **Episode length** | Increasing (for survival) | Erratic |
| **Policy loss** | Decreasing | Exploding |
| **Value loss** | Decreasing | Exploding |
| **KL divergence** | Around target (0.01) | Too high (>0.05) |

## Hyperparameter Tuning

### Learning Rate

```python
# Start conservative
learning_rate = 3e-4

# For complex tasks, try lower
learning_rate = 1e-4

# With learning rate schedule
schedule = "adaptive"  # Adjust based on KL divergence
```

### Number of Environments

```python
# More environments = faster training but more GPU memory
# RTX 3090: ~4096-8192 environments
# RTX 4090: ~8192-16384 environments

num_envs = 4096
```

### Network Architecture

```python
# Simple tasks
actor_hidden_dims = [128, 128]
critic_hidden_dims = [128, 128]

# Complex locomotion
actor_hidden_dims = [512, 256, 128]
critic_hidden_dims = [512, 256, 128]
```

---

## Exercise: Train a Locomotion Policy

Train a quadruped robot to walk using Isaac Lab.

### Requirements

1. Use the `Isaac-Velocity-Flat-Anymal-D-v0` environment
2. Train for 1000 iterations with 4096 environments
3. Monitor training with TensorBoard
4. Evaluate the final policy

### Commands

```bash
# Train
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Anymal-D-v0 \
    --num_envs 4096 \
    --headless \
    --max_iterations 1000

# Monitor
tensorboard --logdir logs/rsl_rl/

# Evaluate
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Velocity-Flat-Anymal-D-v0 \
    --num_envs 16
```

### Expected Outcome

- Mean reward increases over training
- Robot walks forward when commanded
- Policy handles various velocity commands

---

## Summary

Isaac Lab provides a powerful framework for robot RL:

- **Parallel training**: Thousands of environments on GPU
- **Flexible environments**: Observations, actions, rewards
- **RL library integration**: RSL-RL, SB3, skrl
- **Pre-built tasks**: Quick start with locomotion, manipulation

Key skills learned:
- Creating custom environments
- Defining observations and rewards
- Training with PPO
- Monitoring and tuning

In the next chapter, you will learn about synthetic data generation.

**Next:** [Synthetic Data Generation](./5-synthetic-data.md)
