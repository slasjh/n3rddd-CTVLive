import os
import shutil
import requests
from datetime import datetime
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_file(url, local_filename, user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'):
    """下载文件并保存到本地，同时添加User-Agent头部"""
    headers = {'User-Agent': user_agent}
    try:
        with requests.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()  # 如果请求出错，抛出HTTPError异常
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info(f"Downloaded {url} to {local_filename}")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"Other error occurred: {err}")

def copy_to_history_with_timestamp(filename):
    """将文件复制到history目录，并添加时间戳"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在的目录
        history_dir = os.path.join(script_dir, 'history')
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)
        
        new_filename = os.path.join(history_dir, f"{timestamp}_{os.path.basename(filename)}")
        shutil.copy2(filename, new_filename)
        logging.info(f"Copied {filename} to {new_filename}")
    except Exception as e:
        logging.error(f"Failed to copy {filename} to history: {e}")

def main():
    m3u_files = [
        {"url": "https://raw.githubusercontent.com/slasjh/n3rddd-CTVLive/refs/heads/ipv4/litelive.txt", "filename": "v4_litelive.txt"},
        {"url": "https://raw.githubusercontent.com/slasjh/n3rddd-CTVLive/refs/heads/ipv6/litelive.txt", "filename": "v6_litelive.txt"},
        {"url": "https://live.fanmingming.com/tv/m3u/ipv6.m3u", "filename": "fmm.m3u"},
        {"url": "https://tv.iill.top/m3u/Gather", "filename": "Gather.m3u"},
    ]

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    for file_info in m3u_files:
        url = file_info["url"]
        local_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_info["filename"])  # 确保文件下载到脚本所在目录
        # 下载文件，同时传入User-Agent头部
        download_file(url, local_filename, user_agent)

        # 如果文件已经存在，则复制到history目录并添加时间戳
        if os.path.exists(local_filename):
            copy_to_history_with_timestamp(local_filename)

if __name__ == "__main__":
    main()
