#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
aiohttp下载器配置示例
"""

# 基础配置
SETTINGS = {
    # 下载器配置
    'DOWNLOADER': 'crawlo.downloader.aiohttp_downloader.AioHttpDownloader',
    'DOWNLOADER_TYPE': 'aiohttp',
    
    # aiohttp特定配置
    'AIOHTTP_AUTO_DECOMPRESS': True,
    'AIOHTTP_FORCE_CLOSE': False,
    
    # 代理配置
    'PROXY_ENABLED': True,
    'PROXY_API_URL': 'http://test.proxy.api:8080/proxy/getitem/',
    'PROXY_EXTRACTOR': 'proxy',
    'PROXY_REFRESH_INTERVAL': 60,
    'PROXY_POOL_SIZE': 5,
    
    # 通用下载配置
    'DOWNLOAD_TIMEOUT': 30,
    'CONNECTION_POOL_LIMIT': 100,
    'CONNECTION_POOL_LIMIT_PER_HOST': 20,
    'DOWNLOAD_MAXSIZE': 10 * 1024 * 1024,  # 10MB
    'VERIFY_SSL': True,
    
    # 日志配置
    'LOG_LEVEL': 'INFO',
}

def get_settings():
    """获取配置"""
    return SETTINGS

if __name__ == "__main__":
    print("aiohttp下载器配置:")
    for key, value in SETTINGS.items():
        print(f"  {key}: {value}")