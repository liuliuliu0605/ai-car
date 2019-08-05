#!/usr/bin/env python3
# -*-coding:utf-8-*-
import socket


class CarControl(object):
    """Control car to move through socket"""

    def __init__(self, car_ip, control_port):
        print('Connect control server...')
        self.control_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_conn.connect((car_ip, control_port))
        print('Done!')
        self.commands = ['move forward', 'turn left', 'turn right', 'stop']
        self.pre_cmd = 'move forward'

    def steer(self, command):
        """Control car to move according to specific command

        Args:
            command: integer or string. String is like  'move forward' defined in
            self.commands while integer points to the command index in self.commands.

        Returns:
            An integer number pointing to the location of command.
        """
        if isinstance(command, int):
            assert command < len(self.commands)
            command = self.commands[command]        # change command id into real command
        if command == 'move forward':
            self.control_conn.sendall('upO'.encode())
        elif command == 'turn left':
            self.control_conn.sendall('leftO'.encode())
        elif command == 'turn right':
            self.control_conn.sendall('rightO'.encode())
        elif command == 'stop':
            self.control_conn.send('stopO'.encode())
        else:
            print('pre', self.pre_cmd)
            self.steer(self.pre_cmd)
            command = self.pre_cmd
        self.pre_cmd = command
        return self.commands.index(command)

    def close(self):
        """Send CLOSE command to tell server to shut up connection"""
        self.control_conn.sendall('CLOSE'.encode())

    def __del__(self):
        self.control_conn.sendall('cleanO'.encode())
        self.control_conn.close()
