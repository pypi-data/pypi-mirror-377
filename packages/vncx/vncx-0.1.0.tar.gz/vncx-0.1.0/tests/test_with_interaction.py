#!/usr/bin/env python3
"""
测试带交互的截图 - 先触发屏幕更新
"""

import os
import sys
import time
import cv2
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vncx import VNCClient

def test_with_interaction():
    """测试带交互的截图"""
    host = os.getenv('VNC_HOST', '192.168.31.160')
    port = int(os.getenv('VNC_PORT', '5900'))
    password = os.getenv('VNC_PASSWORD', 'A7894561')
    
    print(f"Testing with interaction to {host}:{port}")
    
    client = VNCClient(host, port, password)
    
    try:
        # 连接
        client.connect()
        print(f"✓ Connected: {client.width}x{client.height}")
        
        # 测试1: 初始状态截图（可能是全黑）
        print("\n--- 测试1: 初始截图 ---")
        img1 = client.capture_screen()
        print(f"Initial - Min: {img1.min()}, Max: {img1.max()}, Non-zero: {np.count_nonzero(img1)}/{img1.size}")
        
        # 触发屏幕更新
        print("\n--- 触发屏幕更新 ---")
        for i in range(3):
            print(f"Moving mouse to ({100 + i*10}, {100 + i*10})...")
            client.mouse_move(100 + i*10, 100 + i*10)
            time.sleep(0.5)
        
        # 测试2: 更新后截图
        print("\n--- 测试2: 更新后截图 ---")
        img2 = client.capture_screen()
        print(f"After interaction - Min: {img2.min()}, Max: {img2.max()}, Non-zero: {np.count_nonzero(img2)}/{img2.size}")
        
        # 保存截图比较
        client.save_img("after_interaction.png")
        
        # 检查保存的文件
        saved_img = cv2.imread("after_interaction.png")
        if saved_img is not None:
            print(f"Saved image - Min: {saved_img.min()}, Max: {saved_img.max()}, Non-zero: {np.count_nonzero(saved_img)}/{saved_img.size}")
            
            if np.count_nonzero(saved_img) > 0:
                print("✅ SUCCESS: 截图功能正常！")
                
                # 显示一些像素值作为验证
                print("\n一些像素值示例:")
                for y in range(0, min(5, saved_img.shape[0]), 2):
                    for x in range(0, min(5, saved_img.shape[1]), 2):
                        pixel = saved_img[y, x]
                        if np.any(pixel != 0):
                            print(f"  ({x},{y}): {pixel}")
                
                return True
            else:
                print("❌ FAIL: 保存的截图仍然是全黑的")
                return False
        
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.disconnect()
        print("Disconnected from VNC server")

if __name__ == "__main__":
    success = test_with_interaction()
    sys.exit(0 if success else 1)