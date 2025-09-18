#!/usr/bin/env python3
"""
测试 save_img 修复
"""

import os
import sys
import cv2
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vncx import VNCClient

def test_save_img_fix():
    """测试 save_img 修复"""
    host = os.getenv('VNC_HOST', '192.168.31.160')
    port = int(os.getenv('VNC_PORT', '5900'))
    password = os.getenv('VNC_PASSWORD', 'A7894561')
    
    print(f"Testing save_img fix to {host}:{port}")
    
    client = VNCClient(host, port, password)
    
    try:
        # 连接
        client.connect()
        print(f"✓ Connected: {client.width}x{client.height}")
        
        # 先截取全屏并保存
        print("Capturing full screen...")
        full_img = client.capture_screen()
        client.save_img("test_full.png")
        
        # 检查截图
        saved_img = cv2.imread("test_full.png")
        print(f"Full screenshot - Min: {saved_img.min()}, Max: {saved_img.max()}, Non-zero: {np.count_nonzero(saved_img)}/{saved_img.size}")
        
        # 截取区域并保存
        print("Capturing region...")
        region_img = client.capture_region(100, 100, 200, 200)
        client.save_img("test_region.png")
        
        # 检查区域截图
        saved_region = cv2.imread("test_region.png")
        if saved_region is not None:
            print(f"Region screenshot - Min: {saved_region.min()}, Max: {saved_region.max()}, Non-zero: {np.count_nonzero(saved_region)}/{saved_region.size}")
        
        # 验证两个截图应该不同（区域截图应该包含全屏的一部分）
        if saved_img is not None and saved_region is not None:
            # 检查对应区域
            corresponding_region = saved_img[100:300, 100:300]
            
            if np.array_equal(corresponding_region, saved_region):
                print("✅ SUCCESS: Region screenshot matches corresponding area in full screenshot!")
                return True
            else:
                print("❌ FAIL: Region screenshot doesn't match full screenshot!")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.disconnect()
        print("Disconnected from VNC server")

if __name__ == "__main__":
    success = test_save_img_fix()
    sys.exit(0 if success else 1)