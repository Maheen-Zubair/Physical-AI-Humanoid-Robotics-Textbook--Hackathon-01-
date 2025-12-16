---
sidebar_position: 3
sidebar_label: "Setup"
title: "Development Environment Setup"
description: "Complete guide to installing Ubuntu, ROS 2, Python, and all tools needed for this book"
keywords: [setup, installation, ros2, ubuntu, python, gazebo, development environment]
---

# Development Environment Setup

This chapter guides you through installing all software needed to complete this book. Follow each section carefully, and verify each installation before proceeding.

## Overview

You will install:

1. **Ubuntu 22.04 LTS** - The operating system
2. **ROS 2 Humble** - Robot middleware
3. **Python 3.10+** - Programming language
4. **Gazebo Fortress** - Physics simulation
5. **Additional tools** - Colcon, RViz, development utilities

Total installation time: 1-2 hours (depending on internet speed)

## Step 1: Ubuntu 22.04 LTS

### Option A: Native Installation (Recommended)

Installing Ubuntu directly on your computer provides the best performance for robotics development.

1. **Download Ubuntu 22.04 LTS** from [ubuntu.com/download/desktop](https://ubuntu.com/download/desktop)
2. **Create bootable USB** using [Rufus](https://rufus.ie/) (Windows) or [Etcher](https://www.balena.io/etcher/) (Mac/Linux)
3. **Boot from USB** and follow the installation wizard
4. **Choose installation type**: "Install Ubuntu alongside Windows" for dual-boot, or "Erase disk" for Ubuntu-only

### Option B: Windows Subsystem for Linux (WSL2)

If you must stay on Windows, WSL2 provides a compatible environment.

```powershell
# Run in PowerShell as Administrator
wsl --install -d Ubuntu-22.04
```

After installation, launch Ubuntu from the Start menu and complete setup.

**WSL2 Limitations**:
- GUI applications require additional configuration
- Some ROS 2 features may have reduced performance
- Hardware access is limited

### Option C: Virtual Machine

Use VirtualBox or VMware with Ubuntu 22.04. Allocate at least:
- 4 CPU cores
- 8 GB RAM
- 50 GB disk space
- 3D acceleration enabled

### Verify Ubuntu Installation

```bash
lsb_release -a
```

Expected output:
```
Distributor ID: Ubuntu
Description:    Ubuntu 22.04.x LTS
Release:        22.04
Codename:       jammy
```

## Step 2: System Updates

Before installing ROS 2, update your system:

```bash
sudo apt update
sudo apt upgrade -y
```

Install essential development tools:

```bash
sudo apt install -y \
    build-essential \
    cmake \
    git \
    python3-pip \
    curl \
    wget \
    software-properties-common
```

## Step 3: ROS 2 Humble Installation

### Add ROS 2 Repository

```bash
# Add the ROS 2 GPG key
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Add the repository to sources list
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Update package index
sudo apt update
```

### Install ROS 2 Humble Desktop

The desktop installation includes RViz, demos, and tutorials:

```bash
sudo apt install -y ros-humble-desktop
```

This may take 10-20 minutes depending on your internet connection.

### Install Development Tools

```bash
sudo apt install -y \
    ros-dev-tools \
    python3-colcon-common-extensions \
    python3-rosdep
```

### Initialize rosdep

```bash
sudo rosdep init
rosdep update
```

### Source ROS 2 Environment

Add ROS 2 to your shell configuration:

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Verify ROS 2 Installation

```bash
ros2 --version
```

Expected output:
```
ros2 version 0.x.x
```

Test with a simple demo:

```bash
# Terminal 1: Run talker
ros2 run demo_nodes_cpp talker

# Terminal 2: Run listener (new terminal)
ros2 run demo_nodes_cpp listener
```

You should see messages being published and received.

## Step 4: Gazebo Fortress Installation

Gazebo (formerly Ignition) provides physics simulation for ROS 2.

### Add Gazebo Repository

```bash
sudo wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt update
```

### Install Gazebo Fortress

```bash
sudo apt install -y ignition-fortress
```

### Install ROS-Gazebo Bridge

```bash
sudo apt install -y ros-humble-ros-gz
```

### Verify Gazebo Installation

```bash
ign gazebo --version
```

Expected output:
```
Ignition Gazebo, version x.x.x
```

Launch the empty world:

```bash
ign gazebo empty.sdf
```

A window should open showing an empty simulation environment. Close it with Ctrl+C in the terminal.

## Step 5: Python Environment Setup

### Verify Python Version

```bash
python3 --version
```

Should show Python 3.10 or higher.

### Install Python Packages

```bash
pip3 install --upgrade pip
pip3 install \
    numpy \
    matplotlib \
    scipy \
    transforms3d \
    pyyaml
```

### Create ROS 2 Workspace

```bash
# Create workspace directory
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

# Build empty workspace (creates install/setup.bash)
colcon build

# Source workspace
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## Step 6: Verify Complete Installation

Run this verification script to confirm everything is installed:

```bash
#!/bin/bash
echo "=== System Information ==="
lsb_release -a

echo -e "\n=== ROS 2 ==="
ros2 --version
echo $ROS_DISTRO

echo -e "\n=== Python ==="
python3 --version
pip3 --version

echo -e "\n=== Gazebo ==="
ign gazebo --version

echo -e "\n=== Colcon ==="
colcon version-check

echo -e "\n=== Workspace ==="
ls ~/ros2_ws/

echo -e "\n=== Installation Complete! ==="
```

Save this as `check_install.sh` and run:

```bash
chmod +x check_install.sh
./check_install.sh
```

## Common Installation Issues

### Issue: "ros2 command not found"

**Solution**: Source the ROS 2 setup file:

```bash
source /opt/ros/humble/setup.bash
```

Add to ~/.bashrc if not already present.

### Issue: "rosdep init" fails with permission error

**Solution**: Use sudo:

```bash
sudo rosdep init
```

### Issue: Gazebo window is black or crashes

**Solution**: Check graphics drivers:

```bash
# For NVIDIA
nvidia-smi

# Update drivers if needed
sudo ubuntu-drivers autoinstall
```

### Issue: WSL2 GUI not working

**Solution**: Install an X server on Windows:

1. Install [VcXsrv](https://sourceforge.net/projects/vcxsrv/) or [X410](https://x410.dev/)
2. Add to ~/.bashrc:
   ```bash
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   export LIBGL_ALWAYS_INDIRECT=1
   ```

### Issue: Slow package downloads

**Solution**: Use a closer mirror:

```bash
sudo sed -i 's/archive.ubuntu.com/us.archive.ubuntu.com/g' /etc/apt/sources.list
sudo apt update
```

## Optional: VS Code Setup

Visual Studio Code provides an excellent development environment for ROS 2.

### Install VS Code

```bash
sudo snap install code --classic
```

### Recommended Extensions

Install these extensions in VS Code:

- **ROS** (ms-iot.vscode-ros)
- **Python** (ms-python.python)
- **C/C++** (ms-vscode.cpptools)
- **XML** (redhat.vscode-xml)
- **YAML** (redhat.vscode-yaml)

### Configure ROS 2 in VS Code

Create `.vscode/settings.json` in your workspace:

```json
{
    "python.analysis.extraPaths": [
        "/opt/ros/humble/lib/python3.10/site-packages",
        "~/ros2_ws/install"
    ],
    "ros.distro": "humble",
    "files.associations": {
        "*.launch.py": "python",
        "*.urdf": "xml",
        "*.xacro": "xml",
        "*.sdf": "xml"
    }
}
```

## Summary

You have now installed:

- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill
- Gazebo Fortress simulation
- Python development environment
- Colcon build system
- ROS 2 workspace structure

Your development environment is ready for Module 1.

---

## Exercise: Hello ROS 2

Verify your installation by creating a simple ROS 2 node.

### Step 1: Create Package

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python hello_ros2
```

### Step 2: Write Node

Edit `~/ros2_ws/src/hello_ros2/hello_ros2/hello_node.py`:

```python
import rclpy
from rclpy.node import Node

class HelloNode(Node):
    def __init__(self):
        super().__init__('hello_node')
        self.get_logger().info('Hello, ROS 2!')

def main(args=None):
    rclpy.init(args=args)
    node = HelloNode()
    rclpy.spin_once(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Step 3: Configure Package

Edit `~/ros2_ws/src/hello_ros2/setup.py` entry_points:

```python
entry_points={
    'console_scripts': [
        'hello_node = hello_ros2.hello_node:main',
    ],
},
```

### Step 4: Build and Run

```bash
cd ~/ros2_ws
colcon build --packages-select hello_ros2
source install/setup.bash
ros2 run hello_ros2 hello_node
```

**Expected Output**:
```
[INFO] [timestamp] [hello_node]: Hello, ROS 2!
```

If you see this message, your setup is complete and working!

**Next:** [Module 1: Introduction to ROS 2](./module-1-ros2/1-introduction.md)
