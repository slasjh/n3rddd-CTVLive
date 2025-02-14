import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import os
from urllib.parse import urlparse
import socket  #check p3p源 rtp源
import subprocess #check rtmp源
import requests
import logging
import json

timestart = datetime.now()

BlackHost=["127.0.0.1:8080","live3.lalifeier.eu.org","newcntv.qcloudcdn.com"]

# 读取文件内容
def read_txt_file(file_path):
    skip_strings = ['#genre#']  # 定义需要跳过的 字符串数组['#', '@', '#genre#'] 
    required_strings = ['://']  # 定义需要包含的字符串数组['必需字符1', '必需字符2'] 

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [
            line for line in file
            if not any(skip_str in line for skip_str in skip_strings) and all(req_str in line for req_str in required_strings)
        ]
    return lines

# 检测URL是否可访问并记录响应时间
def check_url(url, timeout=2):

    start_time = time.time()

    elapsed_time = None

    success = False

    headers = {

        'User-Agent': 'Lavf/58.12.100',

        'Accept': '*/*',

    }    

    try:

        if url.startswith("http"):

            if "/udp/" not in url and "/rtp/" not in url:  # 使用 and 而不是 or，确保 URL 中不包含 /udp/ 和 /rtp/

                response = requests.get(url, allow_redirects=True, headers=headers, timeout=timeout)

                response.raise_for_status()  # 如果响应状态码不是 200 OK，将引发 HTTPError 异常
                
                # 注意：response 对象没有 status 属性，只有 status_code 属性

                if response.status_code == 200 or response.status_code == 206:  # 部分内容响应也是成功的

                    success = True

        # 如果执行到这一步，没有异常，计算时间
        elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒
        print(f"{url} http速度为: {elapsed_time},{success}")
    except Exception as e:
        print(f"Error checking {url}: {e}")
        record_host(get_host_from_url(url))
        # 在发生异常的情况下，将 elapsed_time 设置为 None
        elapsed_time = None
        success = False

    return elapsed_time, success


