---
sidebar_position: 2
sidebar_label: "Troubleshooting"
title: "Troubleshooting Guide"
description: "Common issues and solutions for Physical AI & Humanoid Robotics development"
keywords: [troubleshooting, debugging, robotics, issues, solutions]
---

# Troubleshooting Guide

This guide provides solutions for common issues encountered when working with Physical AI and humanoid robotics systems.

## ROS 2 Common Issues

### Package Not Found

**Problem**: `ros2 run` command fails with "Package not found" error.

**Solution**:
1. Check if the package is built:
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select <package_name>
   ```

2. Source the workspace:
   ```bash
   source install/setup.bash
   ```

3. Verify package exists:
   ```bash
   ros2 pkg list | grep <package_name>
   ```

### Node Communication Issues

**Problem**: Nodes cannot communicate via topics/services.

**Solution**:
1. Check if nodes are running:
   ```bash
   ros2 node list
   ```

2. Verify topic/service connections:
   ```bash
   ros2 topic list
   ros2 service list
   ```

3. Check network configuration if nodes are on different machines:
   ```bash
   export ROS_DOMAIN_ID=<same_value_on_all_machines>
   export ROS_LOCALHOST_ONLY=0  # If using different machines
   ```

### Permission Errors

**Problem**: Cannot access serial devices or hardware.

**Solution**:
1. Add user to dialout group:
   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and log back in
   ```

2. Check device permissions:
   ```bash
   ls -l /dev/ttyUSB*
   sudo chmod 666 /dev/ttyUSB*
   ```

## Simulation Issues

### Gazebo Not Launching

**Problem**: Gazebo fails to start or crashes immediately.

**Solution**:
1. Check graphics drivers:
   ```bash
   glxinfo | grep "OpenGL renderer"
   ```

2. Launch with software rendering:
   ```bash
   export LIBGL_ALWAYS_SOFTWARE=1
   gazebo
   ```

3. Check for conflicting processes:
   ```bash
   pkill -f gz
   pkill -f gazebo
   ```

### Physics Simulation Problems

**Problem**: Objects fall through the ground or behave unrealistically.

**Solution**:
1. Check collision geometry in URDF:
   ```xml
   <collision>
       <geometry>
           <box size="1 1 1"/>  <!-- Ensure geometry is defined -->
       </geometry>
   </collision>
   ```

2. Verify physics parameters:
   ```xml
   <gazebo reference="link_name">
       <mu1>0.5</mu1>
       <mu2>0.5</mu2>
   </gazebo>
   ```

3. Adjust time step in world file:
   ```xml
   <physics>
       <max_step_size>0.001</max_step_size>
   </physics>
   ```

### Sensor Data Not Publishing

**Problem**: Sensor topics show no data.

**Solution**:
1. Check sensor plugin configuration:
   ```xml
   <gazebo reference="camera_link">
       <sensor name="camera" type="camera">
           <topic>camera/image_raw</topic>
           <always_on>true</always_on>
           <update_rate>30</update_rate>
       </sensor>
   </gazebo>
   ```

2. Verify bridge configuration:
   ```bash
   ros2 topic list | grep sensor
   ros2 topic hz /sensor_topic
   ```

## Isaac Sim Issues

### Isaac Sim Not Launching

**Problem**: Isaac Sim fails to start or shows black screen.

**Solution**:
1. Check NVIDIA GPU and drivers:
   ```bash
   nvidia-smi
   ```

2. Verify Omniverse installation:
   ```bash
   # Check if Isaac Sim is installed
   ls ~/.local/share/ov/pkg/
   ```

3. Launch with specific GPU:
   ```bash
   CUDA_VISIBLE_DEVICES=0 ~/.local/share/ov/pkg/isaac_sim-*/isaac-sim.sh
   ```

### GPU Memory Issues

**Problem**: "Out of memory" errors during simulation or training.

**Solution**:
1. Reduce environment complexity:
   ```python
   # In Isaac Lab configuration
   scene: InteractiveSceneCfg = InteractiveSceneCfg(
       num_envs=1024,  # Reduce from default 4096
       env_spacing=2.0,  # Reduce spacing
   )
   ```

2. Enable GPU memory optimization:
   ```bash
   export ISAACSIM_HEADLESS=1  # For training
   ```

3. Monitor GPU usage:
   ```bash
   watch -n 1 nvidia-smi
   ```

## Isaac Lab Training Issues

### Training Not Converging

**Problem**: RL policy doesn't improve during training.

**Solution**:
1. Check reward function:
   ```python
   def _get_rewards(self) -> torch.Tensor:
       # Ensure rewards are properly scaled
       return torch.clamp(rewards, -10, 10)  # Prevent extreme values
   ```

2. Adjust learning rate:
   ```python
   # In PPO configuration
   learning_rate = 1e-4  # Try lower values if unstable
   ```

3. Verify observation space:
   ```python
   # Normalize observations
   obs = (obs - self.obs_mean) / (self.obs_std + 1e-8)
   ```

### Domain Randomization Problems

**Problem**: Policy doesn't transfer to real world.

**Solution**:
1. Verify randomization ranges are realistic:
   ```python
   # Don't randomize too broadly
   friction_range = (0.4, 1.0)  # Rather than (0.1, 10.0)
   ```

2. Add sufficient variation:
   ```python
   # Include real-world noise in simulation
   observation_noise = {"joint_pos": 0.01, "joint_vel": 0.1}
   ```

## Vision-Language-Action Issues

### Whisper Speech Recognition Problems

**Problem**: Whisper returns poor transcriptions or errors.

**Solution**:
1. Check audio format compatibility:
   ```python
   # Ensure 16kHz, mono, WAV format
   import librosa
   audio, sr = librosa.load("audio.wav", sr=16000, mono=True)
   ```

2. Try different model sizes:
   ```python
   # Use larger model for better accuracy
   model = whisper.load_model("medium")  # Instead of "base"
   ```

3. Preprocess audio:
   ```python
   # Reduce background noise
   result = model.transcribe("audio.wav", suppress_tokens=[-1])
   ```

### Vision Model Performance Issues

**Problem**: CLIP or other vision models are slow or inaccurate.

**Solution**:
1. Optimize model loading:
   ```python
   # Use GPU acceleration
   device = "cuda" if torch.cuda.is_available() else "cpu"
   model, preprocess = clip.load("ViT-B/32", device=device)
   ```

2. Batch process images:
   ```python
   # Process multiple images together
   images = torch.stack([preprocess(img) for img in image_list]).to(device)
   features = model.encode_image(images)
   ```

### VLA Action Generation Issues

**Problem**: VLA model generates unsafe or incorrect actions.

**Solution**:
1. Add safety validation:
   ```python
   def validate_action(action, robot_state):
       # Check joint limits
       new_joints = robot_state.joints + action
       if not all(min_limit <= pos <= max_limit for pos, (min_limit, max_limit) in zip(new_joints, joint_limits)):
           return False
       return True
   ```

2. Use action constraints:
   ```python
   # Limit action magnitude
   action = torch.clamp(action, -0.1, 0.1)  # Max 10cm movement per step
   ```

## Hardware Integration Issues

### Robot Communication Failures

**Problem**: Cannot communicate with physical robot.

**Solution**:
1. Check USB/serial connections:
   ```bash
   ls /dev/tty*  # List available serial devices
   dmesg | tail  # Check for device detection
   ```

2. Verify baud rate settings:
   ```python
   # Match robot's expected baud rate
   ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
   ```

3. Test connection:
   ```bash
   # Send simple command
   echo "status" > /dev/ttyUSB0
   ```

### Sensor Calibration Problems

**Problem**: Sensor readings are inaccurate.

**Solution**:
1. Calibrate camera intrinsics:
   ```bash
   # Use ROS camera calibration tools
   ros2 run camera_calibration cameracalibrator --size 8x6 --square 0.108 image:=/camera/image_raw
   ```

2. Check IMU calibration:
   ```bash
   # Ensure robot is stationary during calibration
   # Verify orientation conventions (ROS vs robot frame)
   ```

## Network and Communication Issues

### ROS 2 Network Problems

**Problem**: Nodes on different machines cannot communicate.

**Solution**:
1. Set consistent domain ID:
   ```bash
   export ROS_DOMAIN_ID=0  # Same on all machines
   ```

2. Configure firewall:
   ```bash
   # Open necessary ports (7400-7499 for DDS)
   sudo ufw allow 7400:7499/tcp
   sudo ufw allow 7400:7499/udp
   ```

3. Use same network interface:
   ```bash
   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
   export CYCLONEDDS_URI=file://$(pwd)/cyclone_config.xml
   ```

### High Latency Issues

**Problem**: Slow response times in robot control.

**Solution**:
1. Optimize message frequency:
   ```python
   # Reduce unnecessary publications
   publisher = node.create_publisher(MsgType, 'topic', 1)  # Lower queue size
   ```

2. Use intra-process communication:
   ```python
   # For same-process communication
   rclpy.init(options=rclpy.init_options.InitOptions(use_global_arguments=False))
   ```

## Performance Optimization

### Slow Training Speed

**Problem**: Isaac Lab training is too slow.

**Solution**:
1. Increase parallel environments:
   ```python
   # In environment configuration
   scene: InteractiveSceneCfg = InteractiveSceneCfg(
       num_envs=8192,  # Use maximum GPU capacity
   )
   ```

2. Optimize network architecture:
   ```python
   # Use smaller models for faster inference
   policy = ActorCriticCfg(
       actor_hidden_dims=[256, 128],  # Smaller than default
   )
   ```

### Memory Leaks

**Problem**: Memory usage increases over time.

**Solution**:
1. Properly clean up resources:
   ```python
   # In ROS nodes
   def destroy_node(self):
       # Clean up publishers, subscribers, timers
       super().destroy_node()
   ```

2. Monitor memory usage:
   ```bash
   # Check memory usage
   htop
   # Or specific process
   ps aux | grep ros2
   ```

## Debugging Strategies

### General Debugging Approach

1. **Isolate the problem**: Test components individually
2. **Check logs**: Use `ros2 launch` with `--log-level debug`
3. **Verify assumptions**: Check sensor values, transforms, and parameters
4. **Use visualization**: RViz, Isaac Sim viewer, or custom plots
5. **Test incrementally**: Build and test small pieces before integration

### Useful Debugging Commands

```bash
# ROS 2 debugging
ros2 doctor  # Check ROS 2 installation health
ros2 bag record --all  # Record all topics for analysis
ros2 run rqt_graph rqt_graph  # Visualize node connections

# System monitoring
htop  # CPU and memory usage
nvidia-smi  # GPU usage
iotop  # Disk I/O

# Network debugging
netstat -tuln  # Check open ports
ping <robot_ip>  # Test connectivity
```

## Common Error Messages and Solutions

### "Failed to create subscriber"
- **Cause**: Node not properly initialized
- **Solution**: Ensure `rclpy.init()` is called before creating subscribers

### "Transform not available"
- **Cause**: TF tree not properly populated
- **Solution**: Check robot_state_publisher and static_transform_publisher

### "GPU out of memory"
- **Cause**: Model too large for available VRAM
- **Solution**: Reduce batch size, use smaller models, or enable gradient checkpointing

### "Time stamp mismatch"
- **Cause**: Clock synchronization issues
- **Solution**: Ensure all nodes use the same clock source (ROS time vs system time)

---

**Next:** [Hardware Guide](./hardware-guide.md) | [Installation Appendix](./installation.md)
