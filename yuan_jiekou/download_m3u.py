import os
import shutil
import requests
from datetime import datetime

def download_file(url, local_filename):
    """下载文件并保存到本地"""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()  # 如果请求出错，抛出HTTPError异常
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded {url} to {local_filename}")

def copy_to_history_with_timestamp(filename):
    """将文件复制到history目录，并添加时间戳"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_dir = 'history'
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
    
    new_filename = os.path.join(history_dir, f"{timestamp}_{os.path.basename(filename)}")
    shutil.copy2(filename, new_filename)
    print(f"Copied {filename} to {new_filename}")

def main():
    m3u_files = [
       {"url":"https://raw.githubusercontent.com/slasjh/n3rddd-CTVLive/refs/heads/ipv4/litelive.txt","filename":"v4_litelive.txt"},
       {"url":"https://raw.githubusercontent.com/slasjh/n3rddd-CTVLive/refs/heads/ipv6/litelive.txt","filename":"v4_litelive.txt"},
       {"url":"https://live.fanmingming.com/tv/m3u/ipv6.m3u","filename":"fmm.m3u"},
       {"url":"https://tv.iill.top/m3u/Gather","filename":"Gather.m3u"},
    ]
  #for url in urls:
        #local_filename = os.path.basename(url.split('/')[-1])
    for file_info in m3u_files:
         url = file_info["url"]
         local_filename = file_info["filename"]
# 如果文件已经存在，则复制到history目录并添加时间戳
        if os.path.exists(local_filename):
            copy_to_history_with_timestamp(local_filename)
            # 覆盖原文件（模拟重新下载）
            # 这里为了演示，我们重新下载的文件不会改变，所以这一步可以省略
            # 但在实际应用中，你可以在这里再次下载或处理文件
            # 例如，可以删除原文件再下载，或者保留原文件不变    
        
        # 下载文件
        download_file(url, local_filename)
        
        

if __name__ == "__main__":
    main()
