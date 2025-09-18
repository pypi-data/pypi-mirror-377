#!/usr/bin/env python3
"""
直接测试VNC连接 - 使用最简单的方法
"""

import os
import sys
import socket
import struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_direct_vnc():
    """直接测试VNC连接"""
    host = os.getenv('VNC_HOST', '192.168.31.160')
    port = int(os.getenv('VNC_PORT', '5900'))
    password = os.getenv('VNC_PASSWORD', 'A7894561')
    
    print(f"Testing direct VNC connection to {host}:{port}")
    
    try:
        # 直接使用socket连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print("✓ TCP connection established")
        
        # 接收服务器版本
        server_version = sock.recv(12)
        print(f"Server version: {server_version}")
        
        # 发送客户端版本
        sock.send(b"RFB 003.008\n")
        
        # 安全类型协商
        security_types_length = struct.unpack("!B", sock.recv(1))[0]
        print(f"Security types length: {security_types_length}")
        
        if security_types_length > 0:
            security_types = sock.recv(security_types_length)
            print(f"Security types: {list(security_types)}")
            
            # 选择安全类型
            if 2 in security_types:  # VNC Authentication
                sock.send(struct.pack("!B", 2))  # SECURITY_VNC_AUTH
                print("Selected VNC authentication")
                
                # 处理 VNC 认证
                challenge = sock.recv(16)
                print(f"VNC challenge received: {list(challenge)}")
                
                # 简化认证（实际需要 DES 加密）
                response = b"\x00" * 16  # 空响应
                sock.send(response)
                print("Sent authentication response")
                
                # 检查认证结果
                auth_result = struct.unpack("!I", sock.recv(4))[0]
                print(f"Authentication result: {auth_result}")
                if auth_result != 0:
                    print("VNC authentication failed")
                    return False
                    
            else:
                print("No supported security types")
                return False
        
        # 客户端初始化
        sock.send(struct.pack("!B", 1))  # shared=True
        
        # 服务器初始化
        server_init = sock.recv(24)
        width, height = struct.unpack("!HH", server_init[:4])
        print(f"Screen resolution: {width}x{height}")
        
        # 解析像素格式
        pixel_format = server_init[4:20]
        print(f"Pixel format data: {list(pixel_format)}")
        
        # 服务器名称长度
        name_length = struct.unpack("!I", server_init[20:24])[0]
        server_name = sock.recv(name_length).decode('utf-8')
        print(f"Server name: {server_name}")
        
        # 设置编码为 RAW
        sock.send(struct.pack("!B x H i", 2, 1, 0))  # SET_ENCODINGS, 1 encoding, ENCODING_RAW
        
        print("\nSending framebuffer update request...")
        
        # 请求帧缓冲区更新
        sock.send(struct.pack("!B B HH HH", 3, 1, 0, 0, 100, 100))  # incremental update, 100x100 region
        
        # 接收响应
        response = sock.recv(4)
        msg_type, num_rectangles = struct.unpack("!B x H", response)
        print(f"Response: type={msg_type}, rectangles={num_rectangles}")
        
        if num_rectangles > 0:
            # 读取矩形头部
            rect_header = sock.recv(12)
            rect_x, rect_y, rect_width, rect_height, encoding = struct.unpack("!HH HH i", rect_header)
            print(f"Rectangle: {rect_x},{rect_y} {rect_width}x{rect_height}, encoding={encoding}")
            
            if encoding == 0:  # RAW
                bytes_per_pixel = 4  # 假设32位
                pixel_data_size = rect_width * rect_height * bytes_per_pixel
                print(f"Expected pixel data size: {pixel_data_size} bytes")
                
                # 读取前100字节看看内容
                sample_data = sock.recv(min(100, pixel_data_size))
                print(f"First {len(sample_data)} bytes of pixel data:")
                
                # 显示字节内容
                for i in range(0, len(sample_data), 4):
                    if i + 4 <= len(sample_data):
                        pixel = sample_data[i:i+4]
                        values = struct.unpack("!I", pixel)[0]
                        print(f"  {i:04x}: {values:08x} - {list(pixel)}")
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_vnc()
    sys.exit(0 if success else 1)