#!/usr/bin/env python3
"""
vncx 客户端测试
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vncx import VNCClient

host = os.getenv('VNC_HOST', '127.0.0.1')
port = int(os.getenv('VNC_PORT', '5900'))
password = os.getenv('VNC_PASSWORD')

class TestVNCClient(unittest.TestCase):
    
    def setUp(self):
        self.client = VNCClient(host, port, password=password)
    
    def test_client_creation(self):
        """测试客户端创建"""
        self.assertEqual(self.client.host, host)  # 使用环境变量中的host
        self.assertEqual(self.client.port, port)  # 使用环境变量中的port
        self.assertIsNone(self.client.socket)
        self.assertEqual(self.client.width, 0)
        self.assertEqual(self.client.height, 0)
    
    def test_client_with_password(self):
        """测试带密码的客户端创建"""
        client = VNCClient("192.168.1.100", 5900, "password123")
        self.assertEqual(client.password, "password123")
    
    def test_disconnect_without_connection(self):
        """测试未连接时断开连接"""
        # 应该不抛出异常
        self.client.disconnect()
        self.assertIsNone(self.client.socket)
    
    def test_operations_without_connection(self):
        """测试未连接时的操作"""
        with self.assertRaises(Exception):
            self.client.capture_screen()
        
        with self.assertRaises(Exception):
            self.client.mouse_move(100, 100)
        
        with self.assertRaises(Exception):
            self.client.key_press(ord('A'))

    def test_connect_success(self):
        """测试成功连接VNC服务器"""
        try:
            self.client.connect()
            self.assertIsNotNone(self.client.socket)
            self.assertGreater(self.client.width, 0)
            self.assertGreater(self.client.height, 0)
        finally:
            self.client.disconnect()

    def test_capture_screen(self):
        """测试截图功能"""
        try:
            self.client.connect()
            img = self.client.capture_screen()
            self.assertIsNotNone(img)
            self.assertEqual(img.shape[0], self.client.height)
            self.assertEqual(img.shape[1], self.client.width)
        finally:
            self.client.disconnect()

    def test_mouse_operations(self):
        """测试鼠标操作"""
        try:
            self.client.connect()
            # 测试鼠标移动
            self.client.mouse_move(100, 100)
            
            # 测试鼠标点击
            self.client.mouse_click(1)  # 左键点击
            
            # 测试鼠标滚轮
            self.client.mouse_roll_up()
        finally:
            self.client.disconnect()

    def test_keyboard_operations(self):
        """测试键盘操作"""
        try:
            self.client.connect()
            # 测试单键按下
            self.client.key_press(ord('A'))
            
            # 测试按键按下和释放
            self.client.key_down(ord('B'))
            self.client.key_up(ord('B'))
        finally:
            self.client.disconnect()

if __name__ == "__main__":
    unittest.main()