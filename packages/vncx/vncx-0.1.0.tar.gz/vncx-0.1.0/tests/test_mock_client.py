#!/usr/bin/env python3
"""
vncx 客户端模拟测试
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock, patch
from vncx import VNCClient

class TestMockVNCClient(unittest.TestCase):
    
    def setUp(self):
        self.client = VNCClient("127.0.0.1", 5900)
    
    def test_client_creation(self):
        """测试客户端创建"""
        self.assertEqual(self.client.host, "127.0.0.1")
        self.assertEqual(self.client.port, 5900)
        self.assertIsNone(self.client.socket)
        self.assertEqual(self.client.width, 0)
        self.assertEqual(self.client.height, 0)
        self.assertIsNone(self.client.password)
    
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
    
    def test_save_img_without_framebuffer(self):
        """测试无framebuffer时保存图片"""
        # 应该不抛出异常（空操作）
        self.client.save_img("test.png")
    
    def test_key_press_sequence(self):
        """测试按键序列"""
        with patch.object(self.client, 'key_down') as mock_down, \
             patch.object(self.client, 'key_up') as mock_up:
            
            self.client.key_press(ord('A'))
            
            # 验证按下和释放都被调用
            mock_down.assert_called_once_with(ord('A'))
            mock_up.assert_called_once_with(ord('A'))

if __name__ == "__main__":
    unittest.main()

if __name__ == "__main__":
    unittest.main()