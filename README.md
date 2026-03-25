# 6-DOF Robotic Arm — ROS2 Humble + Ignition Gazebo

A 6-DOF robotic arm simulation using **ROS2 Humble** and **Ignition Gazebo Fortress**, with `ros2_control` integration for joint control via GUI sliders.

> **Repository**: [Kavish56345/six_dof_arm](https://github.com/Kavish56345/six_dof_arm)

---

## Project Overview

This project simulates a 6 degree-of-freedom robotic arm designed in **Fusion 360** and exported as URDF using the **Fusion2URDF** plugin. The arm is controlled in Ignition Gazebo through the `ign_ros2_control` pipeline, with a `joint_state_publisher_gui` for interactive slider-based joint control.

### Architecture

```
joint_state_publisher_gui → /gui_joint_states → gui_to_controller relay
    → /position_controller/commands → ForwardCommandController
    → ign_ros2_control → Ignition Gazebo (moves joints)
    → joint_state_broadcaster → /joint_states
    → robot_state_publisher → TF → RViz (visualizes)
```

---

## Package Structure

```
six_dof_urdf_description/
├── config/
│   ├── controller_config.yaml      # ros2_control controller definitions
│   ├── display.rviz                # RViz config for display.launch.py
│   ├── gazebo.rviz                 # RViz config for simulation
│   └── ros_gz_bridge_gazebo.yaml   # Ignition ↔ ROS2 bridge (clock)
├── launch/
│   ├── display.launch.py           # RViz + joint_state_publisher_gui only
│   ├── gazebo.launch.py            # Gazebo only (no control)
│   └── simulation.launch.py        # ★ Combined: Gazebo + controllers + GUI + RViz
├── meshes/                         # STL meshes from Fusion 360
├── urdf/
│   ├── six_dof_urdf.xacro          # Main robot description
│   ├── six_dof_urdf.gazebo         # Gazebo materials + ign_ros2_control plugin
│   ├── six_dof_urdf.ros2control    # ros2_control hardware interface
│   └── materials.xacro             # Material definitions
├── six_dof_urdf_description/
│   ├── __init__.py
│   └── gui_to_controller.py        # Relay: JointState → Float64MultiArray
├── package.xml
├── setup.py
└── setup.cfg
```

---

## What Has Been Done

### ✅ URDF & Simulation Setup
- Designed 6-DOF arm in **Fusion 360**, exported via **Fusion2URDF**
- 7 links (`base_platform` → `base_link` → `link_1_1` through `link_6_1`)
- 6 revolving joints (`joint_1` through `joint_6`, currently `continuous` type)
- STL meshes with inertial properties from Fusion 360
- Added **base platform** (200mm diameter, 5kg cylinder) fixed to `world` for stability

### ✅ Ignition Gazebo Integration
- Robot spawns in Ignition Gazebo Fortress (v6.17) via `ros_gz_sim`
- `ros_gz_bridge` configured for clock synchronization
- `use_sim_time: True` on all nodes for proper TF timestamping

### ✅ ros2_control Pipeline
- **Hardware interface**: `ign_ros2_control/IgnitionSystem` with position command interfaces on all 6 joints
- **Controllers**:
  - `joint_state_broadcaster` — publishes actual joint states from Gazebo
  - `position_controller` (`ForwardCommandController`) — accepts position commands
- **Gazebo plugin**: `ign_ros2_control::IgnitionROS2ControlPlugin`

### ✅ GUI Slider Control
- `joint_state_publisher_gui` publishes to `/gui_joint_states` (remapped to avoid conflict)
- Custom `gui_to_controller.py` relay converts `JointState` → `Float64MultiArray`
- Moving GUI sliders moves the arm in **both Gazebo and RViz simultaneously**

### ✅ Launch Files
- `simulation.launch.py` — single combined launch file with sequenced startup:
  - Gazebo (t=0s) → Spawn (t=5s) → RViz (t=8s) → Controllers (t=10-12s) → GUI (t=14s)

---

## How to Run

### Build
```bash
cd ~/mini_project
colcon build --packages-select six_dof_urdf_description --symlink-install
source install/setup.bash
```

### Launch Simulation (Gazebo + RViz + GUI Sliders)
```bash
ros2 launch six_dof_urdf_description simulation.launch.py
```

### Display in RViz Only (no Gazebo)
```bash
ros2 launch six_dof_urdf_description display.launch.py
```

### Verify Controllers
```bash
ros2 control list_controllers
# Expected: joint_state_broadcaster [active], position_controller [active]
```

---

## Future Work

### 🔲 Redesign Arm in Fusion 360
- Design a new 6-DOF arm with **proper joint limits** (revolute joints with `<limit>` tags)
- Design and integrate an **end effector / gripper**
- Re-export as URDF using Fusion2URDF
- Update all config files for the new arm

### 🔲 MoveIt2 Integration
- Run **MoveIt Setup Assistant** to generate MoveIt config package:
  - SRDF with planning groups ("arm", "gripper")
  - Kinematics solver config (KDL / IKFast)
  - Joint limits YAML
  - MoveIt controller config
- Switch from `ForwardCommandController` to `JointTrajectoryController` (required by MoveIt)
- Create MoveIt launch file integrated with Gazebo
- Test motion planning and execution in RViz MoveIt plugin

### 🔲 Velocity Control
- Add velocity command interface to `ros2control` config
- Set up velocity controller alongside position controller
- Implement velocity control mode switching

### 🔲 Advanced Features (Stretch Goals)
- Cartesian path planning with MoveIt
- Pick-and-place demos using the gripper
- Camera/sensor integration for visual servoing
- Custom motion planning algorithms

---

## Tech Stack

| Component | Version |
|---|---|
| ROS2 | Humble Hawksbill |
| Gazebo | Ignition Fortress (v6.17) |
| ros2_control | via `ign_ros2_control` |
| CAD | Fusion 360 + Fusion2URDF |
| OS | Ubuntu 22.04 |

---

## Key Topics & Services

| Topic | Type | Description |
|---|---|---|
| `/joint_states` | `sensor_msgs/JointState` | Actual joint states from Gazebo |
| `/gui_joint_states` | `sensor_msgs/JointState` | GUI slider values |
| `/position_controller/commands` | `std_msgs/Float64MultiArray` | Position commands to controller |
| `/robot_description` | `std_msgs/String` | URDF for spawning |
| `/clock` | `rosgraph_msgs/Clock` | Sim time from Gazebo |
