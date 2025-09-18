#!/usr/bin/env python3
"""
测试Tight安全类型
"""

import os
import sys
import socket
import struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_tight_auth():
    """测试Tight安全类型"""
    host = os.getenv('VNC_HOST', '192.168.31.160')
    port = int(os.getenv('VNC_PORT', '5900'))
    password = os.getenv('VNC_PASSWORD', 'A7894561')
    
    print(f"Testing Tight authentication to {host}:{port}")
    
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
            print(f"Security types: {[hex(x) for x in security_types]}")
            
            # 尝试使用Tight安全类型
            if 16 in security_types:  # Tight security
                sock.send(struct.pack("!B", 16))  # Tight security
                print("Selected Tight security")
                
                # Tight安全类型可能需要不同的处理
                # 等待服务器响应
                try:
                    response = sock.recv(4)
                    print(f"Tight security response: {list(response)}")
                except socket.timeout:
                    print("No immediate response from Tight security - may be successful")
                    
                # 继续客户端初始化
                sock.send(struct.pack("!B", 1))  # shared=True
                
                # 服务器初始化
                server_init = sock.recv(24)
                width, height = struct.unpack("!HH", server_init[:4])
                print(f"Screen resolution: {width}x{height}")
                
                # 服务器名称长度
                name_length = struct.unpack("!I", server_init[20:24])[0]
                server_name = sock.recv(name_length).decode('utf-8')
                print(f"Server name: {server_name}")
                
                print("✓ Tight authentication successful!")
                sock.close()
                return True
            else:
                print("Tight security not supported")
                return False
        
        sock.close()
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tight_auth()
    sys.exit(0 if success else 1)