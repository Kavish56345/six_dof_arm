#!/usr/bin/env python3
"""
Relay node: converts joint_state_publisher_gui JointState messages
into Float64MultiArray commands for the ForwardCommandController.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray


class GuiToController(Node):
    """Subscribes to GUI joint states, publishes position commands."""

    # Joint order must match the controller config
    JOINT_ORDER = [
        'joint_1', 'joint_2', 'joint_3',
        'joint_4', 'joint_5', 'joint_6',
    ]

    def __init__(self):
        super().__init__('gui_to_controller')

        self.sub = self.create_subscription(
            JointState,
            '/gui_joint_states',
            self.joint_state_cb,
            10,
        )

        self.pub = self.create_publisher(
            Float64MultiArray,
            '/position_controller/commands',
            10,
        )

        self.get_logger().info(
            'Relay started: /gui_joint_states -> /position_controller/commands'
        )

    def joint_state_cb(self, msg: JointState):
        """Convert JointState to Float64MultiArray in correct joint order."""
        if not msg.name or not msg.position:
            return

        # Build a lookup from joint name to position
        name_to_pos = dict(zip(msg.name, msg.position))

        cmd = Float64MultiArray()
        cmd.data = [
            name_to_pos.get(jname, 0.0) for jname in self.JOINT_ORDER
        ]
        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = GuiToController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
