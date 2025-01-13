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

def write_txt_optimized(channels, out_file):
    print("开始写入.txt文件...")

    result_counter = 8
    channel_counters = {}
    last_genre = ''
    category_mappers = {
        'CCTV': '央视频道',
        '卫视': '卫视频道',
        '香港': '港澳台频道',
        '台湾': '港澳台频道',
        '少儿': '少儿频道',
        '动漫': '少儿频道',
        '电影': '电影频道',
        '影院': '电影频道'
    }

    with open(out_file, 'w', encoding='utf-8') as file:
        for category in sorted(channels.keys()):
            for channel_name, channel_url in channels[category]:
                for key, genre in category_mappers.items():
                    if key in channel_name:
                        # 确保在访问之前，字典中已经有这个键（或安全地访问）
                        current_count = channel_counters.get(channel_name, 0)
                        if current_count < result_counter:
                            if genre != last_genre:
                                file.write(f"\n{genre},#genre#\n")
                                last_genre = genre
                            file.write(f"{channel_name},{channel_url}\n")
                            # 这里不需要再打印 current_count，因为它已经被安全获取

                            # 更新字典中的计数
                            channel_counters[channel_name] = current_count + 1
                        break  # 找到匹配的类别后退出内层循环

# 注意：这里的 channels 变量应该是一个已经定义好的、符合上述函数要求的字典结构
# 例如：channels = {'some_category': [('延边卫视', 'http://example.com/1'), ...], ...}
# 你需要确保在调用 write_txt_optimized 函数之前，channels 已经被正确加载和解析


       

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

    #out_file1 = os.path.join(parent_dir, 'live.txt')  # 输入文件路径1
    out_file1 = os.path.join(current_dir, 'tvlist.txt')  # 输入文件路径1
    out_file2 = os.path.join(current_dir, 'tvlist-yw.txt')  # 输入文件路径2

 
    for url in urls:
        print(f"处理URL: {url}")
        channels = fetch_channels(url)   #读取上面url清单
        print(f"获取到的频道数据: {channels}")
        # 写入频道到input_file1
        write_txt_optimized(channels,out_file1)
        print("所有频道写入tvlist.txt完成。")
        
     # 写入央视频道卫视频道到input_file2
     # Define the categories to extract (as a set)
    channels_to_extract = {'央视频道', '卫视频道'}
    extract_channels(out_file1, out_file2, channels_to_extract)
    print("央视频道卫视频道写入tvlist-yw.txt完成。")


        #with open(input_file1, 'r') as file:

            #content = file.read()
        # 打印文件内容
           # print(content)
        
