#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Key加密工具

该模块提供了API Key的加密和解密功能，用于保护用户的API密钥安全。
使用AES-256-GCM加密算法，确保API Key在本地存储时的安全性。
"""

import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
from .logger import get_logger

logger = get_logger()

# 常量定义
SALT_SIZE = 16  # 盐值大小，单位字节
IV_SIZE = 12     # 初始向量大小，单位字节
TAG_SIZE = 16   # 认证标签大小，单位字节
KEY_LENGTH = 32  # 密钥长度，单位字节
ITERATIONS = 100000  # PBKDF2迭代次数

# 生成密钥的密码（固定值，用于本地加密）
# 注意：在生产环境中，应该使用更安全的方式管理这个密码
PASSWORD = b"agent_discussion_system_secure_password"


def generate_key(salt: bytes) -> bytes:
    """使用PBKDF2从密码和盐值生成密钥
    
    Args:
        salt (bytes): 盐值
    
    Returns:
        bytes: 生成的密钥
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(PASSWORD)


def encrypt_api_key(api_key: str) -> str:
    """加密API Key
    
    Args:
        api_key (str): 要加密的API Key
    
    Returns:
        str: 加密后的API Key（base64编码）
    """
    try:
        # 生成盐值
        salt = os.urandom(SALT_SIZE)
        
        # 生成密钥
        key = generate_key(salt)
        
        # 生成初始向量
        iv = os.urandom(IV_SIZE)
        
        # 创建密码器
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # 加密数据
        ciphertext = encryptor.update(api_key.encode('utf-8')) + encryptor.finalize()
        
        # 获取认证标签
        tag = encryptor.tag
        
        # 组合盐值、初始向量、认证标签和密文
        encrypted_data = salt + iv + tag + ciphertext
        
        # Base64编码
        encrypted_base64 = urlsafe_b64encode(encrypted_data).decode('utf-8')
        
        return encrypted_base64
    except Exception as e:
        logger.error(f"加密API Key失败: {str(e)}")
        return ""


def decrypt_api_key(encrypted_api_key: str) -> str:
    """解密API Key
    
    Args:
        encrypted_api_key (str): 加密的API Key（base64编码）
    
    Returns:
        str: 解密后的API Key
    """
    try:
        # Base64解码
        encrypted_data = urlsafe_b64decode(encrypted_api_key.encode('utf-8'))
        
        # 解析盐值、初始向量、认证标签和密文
        salt = encrypted_data[:SALT_SIZE]
        iv = encrypted_data[SALT_SIZE:SALT_SIZE+IV_SIZE]
        tag = encrypted_data[SALT_SIZE+IV_SIZE:SALT_SIZE+IV_SIZE+TAG_SIZE]
        ciphertext = encrypted_data[SALT_SIZE+IV_SIZE+TAG_SIZE:]
        
        # 生成密钥
        key = generate_key(salt)
        
        # 创建密码器
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # 解密数据
        api_key = decryptor.update(ciphertext) + decryptor.finalize()
        
        return api_key.decode('utf-8')
    except Exception as e:
        logger.error(f"解密API Key失败: {str(e)}")
        return ""
