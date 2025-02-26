#!/usr/bin/env python3

import os
import select
import struct

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Temperature


class TemperaturePublisher(Node):
    def __init__(self, device_path):
        super().__init__('temperature_publisher')

        # Define device name
        self.device_path = device_path

        # Create a publisher for sensor_msgs/Temperature
        self.publisher_ = self.create_publisher(Temperature, 'temperature', 10)

        # Create a timer to publish at 1 Hz
        timer_period = 1.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info('TemperaturePublisher node has been started.')

    def timer_callback(self):
        # Read the temperature from the device
        temperature_value = self.read_temperature(self.device_path)

        # Create and populate a sensor_msgs/Temperature message
        msg = Temperature()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "temper_link"  # frame id can be any descriptive value
        msg.temperature = temperature_value
        msg.variance = 0.0  # No known variance here, so set to 0

        # Publish the message
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing Temperature: {temperature_value:.2f} °C')

    def read_temperature(self, device_path):
        """
        Reads the temperature (in degrees Celsius) from a Temper device.

        Credit to https://github.com/urwen/temper for the byte sequence used here.
        """
        # The "fetch temperature" query for the device
        QUERY = struct.pack('8B', 0x01, 0x80, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00)

        # Open the device for read-write
        f = os.open(device_path, os.O_RDWR)

        # Send the query
        os.write(f, QUERY)

        # Wait until the device has data to read
        poll = select.poll()
        poll.register(f, select.POLLIN)
        poll.poll()
        poll.unregister(f)

        # TemperGold sends 16 bytes; read them and then close the device
        data = os.read(f, 16)
        os.close(f)

        # Temperature is stored as a 2-byte, big-endian integer at byte offset 2
        # The value represents degrees in c * 100
        return struct.unpack_from('>h', data, 2)[0] / 100.0



def main(args=None):
    rclpy.init(args=args)
    device_path = os.getenv('TEMPERGOLD_DEV', '/dev/tempergold')

    TP = TemperaturePublisher(device_path)
    rclpy.spin(TP)

    TP.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
