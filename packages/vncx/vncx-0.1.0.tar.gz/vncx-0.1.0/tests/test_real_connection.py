#!/usr/bin/env python3
"""
实际VNC连接测试 - 需要设置环境变量
VNC_HOST=192.168.31.160 VNC_PORT=5900 VNC_PASSWORD=A7894561 python test_real_connection.py
"""

import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vncx import VNCClient

def test_real_connection():
    """测试实际VNC连接"""
    host = os.getenv('VNC_HOST', '127.0.0.1')
    port = int(os.getenv('VNC_PORT', '5900'))
    password = os.getenv('VNC_PASSWORD')
    
    print(f"Connecting to VNC server {host}:{port}...")
    
    client = VNCClient(host, port, password)
    
    try:
        # 连接
        client.connect()
        print(f"✓ Connected to VNC server: {client.width}x{client.height}")
        
        # 截图测试
        print("Capturing screen...")
        img = client.capture_screen()
        print(f"✓ Screen captured: {img.shape}")
        
        # 保存截图
        client.save_img("vnc_screenshot.png")
        print("✓ Screenshot saved as vnc_screenshot.png")
        
        # 区域截图
        region = client.capture_region(100, 100, 300, 200)
        print(f"✓ Region captured: {region.shape}")
        
        print("All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        client.disconnect()
        print("Disconnected from VNC server")

if __name__ == "__main__":
    success = test_real_connection()
    sys.exit(0 if success else 1)