#!/usr/bin/env python3
"""
测试小区域截图，尝试不同坐标
"""

import os
import sys
import struct
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vncx import VNCClient

def test_small_region():
    """测试小区域截图"""
    host = os.getenv('VNC_HOST', '192.168.31.160')
    port = int(os.getenv('VNC_PORT', '5900'))
    password = os.getenv('VNC_PASSWORD', 'A7894561')
    
    print(f"Connecting to VNC server {host}:{port}...")
    
    client = VNCClient(host, port, password)
    
    try:
        # 连接
        client.connect()
        print(f"✓ Connected: {client.width}x{client.height}")
        
        # 测试多个小区域
        test_regions = [
            (0, 0, 50, 50),        # 左上角
            (client.width-50, 0, 50, 50),  # 右上角  
            (0, client.height-50, 50, 50), # 左下角
            (client.width//2-25, client.height//2-25, 50, 50),  # 中心
        ]
        
        for i, (x, y, w, h) in enumerate(test_regions):
            print(f"\n--- 测试区域 {i+1}: ({x},{y}) {w}x{h} ---")
            
            # 触发一些交互
            if i > 0:
                print("Moving mouse to trigger update...")
                client.mouse_move(x + 10, y + 10)
            
            # 获取区域数据
            region = client.capture_region(x, y, w, h)
            
            # 分析数据
            non_zero = np.count_nonzero(region)
            total_pixels = region.size
            
            print(f"Non-zero pixels: {non_zero}/{total_pixels} ({non_zero/total_pixels:.2%})")
            print(f"Min: {region.min()}, Max: {region.max()}, Mean: {region.mean():.2f}")
            
            if non_zero > 0:
                print("✓ 找到非黑色像素！")
                
                # 找到第一个非黑色像素
                for py in range(min(10, h)):
                    for px in range(min(10, w)):
                        pixel = region[py, px]
                        if np.any(pixel != 0):
                            print(f"第一个非黑色像素在 ({px},{py}): {pixel}")
                            return True
            else:
                print("✗ 所有像素都是黑色")
        
        print("\n⚠️  所有测试区域都是全黑的，可能是服务器配置问题")
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
    success = test_small_region()
    sys.exit(0 if success else 1)