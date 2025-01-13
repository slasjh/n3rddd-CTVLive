import re
import requests
import logging
from collections import OrderedDict
from datetime import datetime
import os

 

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#du qu m3u/txt
def fetch_channels(url):
    channels = OrderedDict()

    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        lines = response.text.split("\n")
        current_category = None
        is_m3u = any("#EXTINF" in line for line in lines[:15])
        source_type = "m3u" if is_m3u else "txt"
        logging.info(f"url: {url} 获取成功，判断为{source_type}格式")

        if is_m3u:
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF"):
                    match = re.search(r'group-title="(.*?)",(.*)', line)
                    if match:
                        current_category = match.group(1).strip()
                        channel_name = match.group(2).strip()
                        channel_name = replace_channel_name(channel_name)
                        if current_category not in channels:
                            channels[current_category] = []
                elif line and not line.startswith("#"):
                    channel_url = line.strip()
                    if current_category and channel_name:
                        channels[current_category].append((channel_name, channel_url))
        else:
            for line in lines:
                line = line.strip()
                if "#genre#" in line:
                    current_category = line.split(",")[0].strip()
                    channels[current_category] = []
                elif current_category:
                    match = re.match(r"^(.*?),(.*?)$", line)
                    if match:
                        channel_name = match.group(1).strip()
                        channel_name = replace_channel_name(channel_name)
                        channel_url = match.group(2).strip()
                        channels[current_category].append((channel_name, channel_url))
                    elif line:
                        channel_name = line.strip()
                        channel_name = replace_channel_name(channel_name)
                        channels[current_category].append((channel_name, ''))
        if channels:
            categories = ", ".join(channels.keys())
            logging.info(f"url: {url} 爬取成功✅，包含频道分类: {categories}")
    except requests.RequestException as e:
        logging.error(f"url: {url} 爬取失败❌, Error: {e}")

    return channels

# 替换频道名中的特定文字

def replace_channel_name(name):

    replacements = [

        ("cctv", "CCTV"), ("中央", "CCTV"), ("央视", "CCTV"), ("高清", ""), ("超高", ""),

        ("HD", ""), ("标清", ""), ("频道", ""), ("-", ""), (" ", ""), ("PLUS", "+"),

        ("＋", "+"), ("(", ""), (")", ""), (r"CCTV(\d+)台", r"CCTV\1"),

        ("CCTV1综合", "CCTV1"), ("CCTV2财经", "CCTV2"), ("CCTV3综艺", "CCTV3"),

        ("CCTV4国际", "CCTV4"), ("CCTV4中文国际", "CCTV4"), ("CCTV4欧洲", "CCTV4"),

        ("CCTV5体育", "CCTV5"), ("CCTV6电影", "CCTV6"), ("CCTV7军事", "CCTV7"),

        ("CCTV7军农", "CCTV7"), ("CCTV7农业", "CCTV7"), ("CCTV7国防军事", "CCTV7"),

        ("CCTV8电视剧", "CCTV8"),("CCTV9记录", "CCTV9"),("CCTV10科教", "CCTV10"),

        ("CCTV10科教", "CCTV10"),("CCTV11戏曲", "CCTV11"),("CCTV12社会与法", "CCTV12"),
        
        ("CCTV13新闻", "CCTV13"),("CCTV新闻", "CCTV13"),("CCTV14少儿", "CCTV14"),("CCTV15音乐", "CCTV15"),
        ("CCTV16奥林匹克", "CCTV16"),("CCTV17农业农村", "CCTV17"),("CCTV17农业", "CCTV17"),("CCTV5+体育赛视", "CCTV5+"),
        ("CCTV5+体育赛事", "CCTV5+"),("CCTV5+体育", "CCTV5+"),

    ]

    for old, new in replacements:

        name = name.replace(old, new)

    return name
 
def write_txt(channels):
    print("开始写入tvlist.txt文件...")

    input_file1 = 'tvlist.txt'  # 添加了缺失的变量定义
    with open(input_file1, 'w', encoding='utf-8') as file:
        result_counter = 8  # 每个频道最多写入的次数
        channel_counters = {}

        # 处理央视频道
        print("开始写入央视频道...")
        file.write('央视频道,#genre#\n')

        categories = sorted(channels.keys())
        for category in categories:
            for channel_name, channel_url in channels[category]:
                if 'CCTV' in channel_name:
                    if channel_counters.get(channel_name, 0) < result_counter:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] = channel_counters.get(channel_name, 0) + 1

        # 处理卫视频道
        print("开始写入卫视频道...")
        file.write('\n卫视频道,#genre#\n')
        for category in categories:
            for channel_name, channel_url in channels[category]:
                if '卫视' in channel_name:
                    if channel_counters.get(channel_name, 0) < result_counter:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] = channel_counters.get(channel_name, 0) + 1

        # 处理港澳台频道
        print("开始写入港澳台频道...")
        file.write('\n港澳台频道,#genre#\n')
        for category in categories:
            for channel_name, channel_url in channels[category]:
                if '香港' in channel_name or '台湾' in channel_name:
                    if channel_counters.get(channel_name, 0) < result_counter:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] = channel_counters.get(channel_name, 0) + 1

        # 处理少儿频道
        print("开始写入少儿频道...")
        file.write('\n少儿频道,#genre#\n')
        for category in categories:
            for channel_name, channel_url in channels[category]:
                if '少儿' in channel_name or '动漫' in channel_name:
                    if channel_counters.get(channel_name, 0) < result_counter:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] = channel_counters.get(channel_name, 0) + 1

        # 处理电影频道
        print("开始写入电影频道...")
        file.write('\n电影频道,#genre#\n')
        for category in categories:
            for channel_name, channel_url in channels[category]:
                if '电影' in channel_name or '影院' in channel_name:
                    if channel_counters.get(channel_name, 0) < result_counter:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] = channel_counters.get(channel_name, 0) + 1

def extract_channels(input_file, output_file, channels_to_extract):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        current_category = None
        for line in infile:
            line = line.strip()
            if line.endswith(',#genre#'):
                current_category = line[:-len(',#genre#')].strip()
                if current_category in channels_to_extract:
                    outfile.write(f'{current_category},#genre#\n')
            elif  ',' in line :
                channel_name, url = line.split(',', 1)
                outfile.write(f"{channel_name.strip()}, {url.strip()}\n")


if __name__ == "__main__":
    # 定义要访问的多个URL
    urls = [
        #"https://gitlab.com/p2v5/wangtv/-/raw/main/lunbo.txt",
        #'https://gitlab.com/p2v5/wangtv/-/raw/main/wang-tvlive.txt'
        #'https://raw.githubusercontent.com/kimwang1978/collect-tv-txt/refs/heads/main/live.txt',
        'https://raw.githubusercontent.com/slasjh/n3rddd-CTVLive/refs/heads/ipv4/blacklist1/whitelist_auto_tv2.txt'
    ]
    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取上一层目录
    parent_dir = os.path.dirname(current_dir)
    # 获取再上一层目录
    #parent2_dir = os.path.dirname(parent_dir)
    # # 获取根目录
    # root_dir = os.path.abspath(os.sep)  

    #input_file1 = os.path.join(parent_dir, 'live.txt')  # 输入文件路径1
    input_file1 = os.path.join(current_dir, 'tvlist.txt')  # 输入文件路径1
    input_file2 = os.path.join(current_dir, 'tvlist-yw.txt')  # 输入文件路径2
 
    for url in urls:
        print(f"处理URL: {url}")
        channels = fetch_channels(url)   #读取上面url清单
        print(f"获取到的频道数据: {channels}")
        # 写入频道到input_file1
        write_txt(channels)
        print("写入完成。")
     
     # 写入央视频道卫视频道到input_file2
     # Define the categories to extract (as a set)
    channels_to_extract = {'央视频道', '卫视频道'}
    extract_channels(out_file1, out_file2, channels_to_extract)
    print("央视频道卫视频道写入tvlist-yw.txt完成。")


        #with open(input_file1, 'r') as file:

            #content = file.read()
        # 打印文件内容
           # print(content)
        
