import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    pkg_share = get_package_share_directory('six_dof_urdf_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # --- Paths ---
    xacro_file = os.path.join(pkg_share, 'urdf', 'six_dof_urdf.xacro')
    rviz_config = os.path.join(pkg_share, 'config', 'gazebo.rviz')
    bridge_config = os.path.join(pkg_share, 'config', 'ros_gz_bridge_gazebo.yaml')

    # --- Process URDF ---
    robot_description_config = xacro.process_file(xacro_file)
    robot_urdf = robot_description_config.toxml()

    # --- Launch arguments ---
    gui_arg = DeclareLaunchArgument(
        'gui', default_value='True',
        description='Launch joint_state_publisher_gui'
    )
    show_gui = LaunchConfiguration('gui')

    # ===================== NODES =====================

    # 1. Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_urdf}],
    )

    # 2. Ignition Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r -v 4 empty.sdf'}.items(),
    )

    # 3. Spawn robot in Gazebo (with delay)
    spawn_robot = TimerAction(
        period=5.0,
        actions=[Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-topic', '/robot_description',
                '-name', 'six_dof_urdf',
                '-allow_renaming', 'false',
                '-x', '0.0',
                '-y', '0.0',
                '-z', '0.32',
                '-Y', '0.0',
            ],
            output='screen',
        )],
    )

    # 4. ros_gz_bridge (clock)
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config}],
        output='screen',
    )

    # 5. Controller spawners (delayed to ensure Gazebo + spawn are ready)
    spawn_joint_state_broadcaster = TimerAction(
        period=10.0,
        actions=[Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster'],
            output='screen',
        )],
    )

    spawn_position_controller = TimerAction(
        period=12.0,
        actions=[Node(
            package='controller_manager',
            executable='spawner',
            arguments=['position_controller'],
            output='screen',
        )],
    )

    # 6. Joint State Publisher GUI (remapped to /gui_joint_states)
    joint_state_publisher_gui = TimerAction(
        period=14.0,
        actions=[Node(
            condition=IfCondition(show_gui),
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            remappings=[('joint_states', '/gui_joint_states')],
            parameters=[{'robot_description': robot_urdf}],
        )],
    )

    # 7. GUI-to-Controller relay node
    gui_to_controller = TimerAction(
        period=14.0,
        actions=[Node(
            condition=IfCondition(show_gui),
            package='six_dof_urdf_description',
            executable='gui_to_controller',
            name='gui_to_controller',
            output='screen',
        )],
    )

    # 8. RViz
    rviz = TimerAction(
        period=8.0,
        actions=[Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen',
        )],
    )

    return LaunchDescription([
        gui_arg,
        gazebo,
        robot_state_publisher,
        spawn_robot,
        ros_gz_bridge,
        spawn_joint_state_broadcaster,
        spawn_position_controller,
        joint_state_publisher_gui,
        gui_to_controller,
        rviz,
    ])
