---
sidebar_position: 4
sidebar_label: "Installation Appendix"
title: "Software Installation Appendix"
description: "Complete installation guide for all software used in Physical AI & Humanoid Robotics"
keywords: [installation, setup, ros2, gazebo, isaac, dependencies]
---

# Software Installation Appendix

This appendix provides complete installation instructions for all software used throughout the Physical AI & Humanoid Robotics textbook, organized by system requirements and dependency chains.

## System Requirements

### Operating System Support
- **Primary**: Ubuntu 22.04 LTS (Jammy Jellyfish)
- **Alternative**: Ubuntu 20.04 LTS (Focal Fossa)
- **Windows**: WSL2 with Ubuntu 22.04 (for development only)
- **macOS**: Limited support, use virtual machine for full functionality

### Hardware Prerequisites
- **Minimum**: 16GB RAM, 100GB free disk space, x86_64 CPU
- **Recommended**: 32GB+ RAM, 500GB+ SSD, NVIDIA GPU with 8GB+ VRAM
- **GPU**: NVIDIA GPU with CUDA 11.8+ support (RTX 2070 or better)

## Ubuntu 22.04 Base Setup

### Initial System Configuration

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install basic development tools
sudo apt install -y build-essential cmake git curl wget vim htop \
    python3-dev python3-pip python3-venv python3-setuptools \
    software-properties-common gnupg lsb-release

# Install additional utilities
sudo apt install -y openssh-server net-tools nfs-common \
    htop iotop iftop tree jq
```

### NVIDIA GPU Drivers

```bash
# Add graphics drivers PPA
sudo add-apt-repository ppa:graphics-drivers/ppa -y
sudo apt update

# Install NVIDIA drivers (choose appropriate version)
sudo apt install -y nvidia-driver-535  # Or latest available

# Reboot to apply changes
sudo reboot
```

### Verify GPU Setup
```bash
# Check NVIDIA driver installation
nvidia-smi

# Install CUDA toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key add /var/cuda-repo-ubuntu2204/7fa2af80.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /"
sudo apt update
sudo apt install -y cuda-toolkit-12-3
```

## ROS 2 Humble Hawksbill Installation

### Setup ROS 2 Repository

```bash
# Set locale
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add ROS 2 GPG key and repository
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update
```

### Install ROS 2 Packages

```bash
# Install ROS 2 base packages
sudo apt install -y ros-humble-desktop-full

# Install additional ROS 2 packages for robotics
sudo apt install -y \
    ros-humble-ros-base \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-rosbridge-suite \
    ros-humble-teleop-tools \
    ros-humble-joy \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-xacro \
    ros-humble-urdf \
    ros-humble-urdf-tutorial \
    ros-humble-turtlebot3-* \
    python3-rosdep2 \
    python3-colcon-common-extensions \
    python3-rosinstall \
    python3-rosinstall-generator \
    python3-wstool \
    python3-rosdep \
    python3-catkin-tools
```

### Setup ROS 2 Environment

```bash
# Add ROS 2 to bashrc
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Initialize rosdep
sudo rosdep init
rosdep update
```

## Gazebo Garden Installation

### Install Gazebo Garden

```bash
# Add Gazebo repository
sudo curl -sSL http://get.gazebosim.org | sudo bash

# Install Gazebo Garden
sudo apt install -y gz-garden

# Install additional Gazebo plugins
sudo apt install -y \
    libgz-sim7-dev \
    libgz-physics6-dev \
    libgz-sensors7-dev \
    libgz-transport13-dev \
    libgz-msgs11-dev \
    libgz-math7-dev \
    libgz-common5-dev
```

### ROS 2 Gazebo Integration

```bash
# Install ROS 2 Gazebo bridge
sudo apt install -y \
    ros-humble-ros-gz \
    ros-humble-ros-gz-bridge \
    ros-humble-ros-gz-sim \
    ros-humble-ros-gz-image \
    ros-humble-ros-gz-sensors
```

## NVIDIA Isaac Sim Installation

### Install Omniverse Launcher

```bash
# Download and install Omniverse Launcher
cd ~/Downloads
wget https://developer.nvidia.com/omniverse-apps-linux64
chmod +x omniverse-apps-linux64
./omniverse-apps-linux64

# Or install via NVIDIA APT repository
curl -sL https://developer.download.nvidia.com/installer/omniverse-repo-ubuntu2004.deb | sudo dpkg -i -
sudo apt update
sudo apt install -y omniverse-launcher
```

### Install Isaac Sim via Launcher

1. Launch Omniverse Launcher
2. Sign in with NVIDIA Developer account
3. Search for "Isaac Sim"
4. Click "Install" to download and install Isaac Sim

### Isaac Sim Dependencies

```bash
# Install Isaac Sim Python dependencies
pip3 install --upgrade pip
pip3 install --user nvidia-isaac

# Or via conda (recommended)
conda create -n isaacsim python=3.10
conda activate isaacsim
pip install --user nvidia-isaac
```

## Isaac Lab Installation

### Clone Isaac Lab Repository

```bash
# Create workspace
mkdir -p ~/isaac_lab
cd ~/isaac_lab

# Clone Isaac Lab
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

# Verify repository
ls -la
```

### Install Isaac Lab

```bash
# Make install script executable
chmod +x isaaclab.sh

# Install Isaac Lab (this will take time)
./isaaclab.sh --install

# Or install in development mode
./isaaclab.sh --install-dev
```

### Verify Isaac Lab Installation

```bash
# Test basic functionality
./isaaclab.sh -p scripts/tutorials/00_sim/spawn_prims.py

# Test RL training (optional)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Anymal-D-v0 \
    --num_envs 64 \
    --headless
```

## Isaac ROS Installation

### Install Isaac ROS Common

```bash
# Create Isaac ROS workspace
mkdir -p ~/isaac_ros_ws/src
cd ~/isaac_ros_ws/src

# Clone Isaac ROS common
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git

# Clone desired Isaac ROS packages
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_object_detection.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_apriltag.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_tensor_rt.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_pipeline.git
```

### Build Isaac ROS Packages

```bash
cd ~/isaac_ros_ws

# Source ROS 2
source /opt/ros/humble/setup.bash

# Build with colcon
colcon build --symlink-install --packages-select \
    isaac_ros_common \
    isaac_ros_visual_slam \
    isaac_ros_object_detection \
    isaac_ros_apriltag \
    isaac_ros_tensor_rt \
    isaac_ros_image_pipeline

# Source the workspace
source install/setup.bash
```

## Python Development Environment

### Create Python Virtual Environment

```bash
# Create virtual environment for robotics projects
python3 -m venv ~/robotics_env
source ~/robotics_env/bin/activate

# Upgrade pip and install essential packages
pip install --upgrade pip setuptools wheel

# Install robotics-specific packages
pip install \
    numpy==1.24.3 \
    scipy==1.10.1 \
    matplotlib==3.7.1 \
    pandas==2.0.3 \
    opencv-python==4.8.0.74 \
    Pillow==10.0.0 \
    torch==2.0.1 \
    torchvision==0.15.2 \
    torchaudio==2.0.2 \
    transformers==4.31.0 \
    openai-whisper \
    faster-whisper \
    sentencepiece \
    protobuf==3.20.3
```

### Install Vision-Language-Action Dependencies

```bash
# Activate environment
source ~/robotics_env/bin/activate

# Install OpenAI CLIP
pip install git+https://github.com/openai/CLIP.git

# Install OpenVLA dependencies
pip install openvla

# Install LLaVA (if needed)
pip install transformers accelerate

# Install grounding models
pip install groundingdino-py
pip install segment-anything
```

## Docker Setup for Robotics

### Install Docker

```bash
# Install Docker
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl enable docker
sudo systemctl start docker
```

### Install NVIDIA Container Toolkit

```bash
# Add NVIDIA container toolkit repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-container-toolkit
sudo apt update
sudo apt install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

## Development Tools Installation

### Visual Studio Code

```bash
# Install VS Code
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt update
sudo apt install -y code

# Install ROS 2 extension
code --install-extension ms-iot.vscode-ros
code --install-extension ms-python.python
```

### Git Configuration

```bash
# Configure Git for robotics development
git config --global user.name "Your Name"
git config --global user.email "your.email@domain.com"
git config --global core.editor "vim"
git config --global pull.rebase false

# Configure Git for large files (if using LFS)
git lfs install
```

## Troubleshooting Common Issues

### ROS 2 Installation Issues

**Problem**: `rosdep init` fails
```bash
# Solution: Manually create rosdep sources
sudo mkdir -p /etc/ros/rosdep/sources.list.d
sudo rosdep init
rosdep update
```

**Problem**: Permission denied accessing `/dev/ttyUSB*`
```bash
# Solution: Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and log back in
```

### GPU/CUDA Issues

**Problem**: `nvidia-smi` not found
```bash
# Solution: Check if drivers are properly installed
sudo apt install --reinstall nvidia-driver-535
sudo reboot
```

**Problem**: CUDA not found
```bash
# Add CUDA to PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### Isaac Sim Issues

**Problem**: Isaac Sim fails to launch
```bash
# Check if GPU drivers are working
nvidia-smi

# Launch with software rendering (for testing)
export LIBGL_ALWAYS_SOFTWARE=1
# Then try launching Isaac Sim
```

### Isaac Lab Issues

**Problem**: Isaac Lab build fails
```bash
# Ensure all dependencies are installed
sudo apt install build-essential cmake python3-dev

# Check Python version (should be 3.10)
python3 --version

# Reinstall with clean environment
./isaaclab.sh --uninstall
./isaaclab.sh --install
```

## Verification Checklist

### ROS 2 Verification
```bash
# Test ROS 2 installation
source /opt/ros/humble/setup.bash
ros2 run demo_nodes_cpp talker
# In another terminal: ros2 run demo_nodes_py listener
```

### Gazebo Verification
```bash
# Test Gazebo
gz sim -v 4
# Should open Gazebo GUI without errors
```

### Isaac Sim Verification
```bash
# Launch Isaac Sim (through Omniverse Launcher)
# Should open without GPU errors
```

### Isaac Lab Verification
```bash
# Test Isaac Lab
cd ~/IsaacLab
./isaaclab.sh -p scripts/tutorials/00_sim/spawn_prims.py
# Should run without errors
```

### Isaac ROS Verification
```bash
# Test Isaac ROS workspace
cd ~/isaac_ros_ws
source install/setup.bash
ros2 launch vda5050_connector vda5050_connector.launch.py
# Should launch without errors
```

## Optional: Development Container Setup

### Create Development Container

```bash
# Create container configuration
mkdir -p ~/robotics_dev/.devcontainer
cat > ~/robotics_dev/.devcontainer/devcontainer.json << 'EOF'
{
    "name": "Robotics Development",
    "image": "nvidia/cuda:12.3-devel-ubuntu22.04",
    "runArgs": [
        "--gpus", "all",
        "--privileged",
        "--network", "host"
    ],
    "mounts": [
        "source=${localWorkspaceFolder},target=/workspace,type=bind,consistency=cached"
    ],
    "workspaceFolder": "/workspace",
    "features": {
        "ghcr.io/devcontainers/features/docker-in-docker:2": {}
    },
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-iot.vscode-ros",
                "ms-python.python",
                "ms-vscode.cpptools"
            ]
        }
    },
    "postCreateCommand": "apt-get update && apt-get install -y python3-pip git curl wget"
}
EOF
```

## Post-Installation Steps

### Create Robotics Workspace Structure

```bash
# Create standard robotics workspace
mkdir -p ~/robotics_ws/{src,build,install,log}
cd ~/robotics_ws/src

# Create a test ROS 2 package
cd ~/robotics_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

### Set Up Development Environment

```bash
# Create aliases for common robotics commands
cat >> ~/.bashrc << 'EOF'

# Robotics aliases
alias cw='cd ~/robotics_ws'
alias cs='cd ~/robotics_ws/src'
alias cb='cd ~/robotics_ws && colcon build --symlink-install'
alias sb='source ~/robotics_ws/install/setup.bash'
alias gs='gz sim'
alias rs='ros2 run'
alias rl='ros2 launch'

# Isaac Lab
alias il='cd ~/IsaacLab && source ~/.bashrc'

# Isaac Sim
alias is='~/.local/share/ov/pkg/isaac_sim-*/isaac-sim.sh'
EOF

source ~/.bashrc
```

---

**Next:** [Quick Start Guide](../setup.md) | [Module 1: ROS 2](../module-1-ros2/1-introduction.md)
