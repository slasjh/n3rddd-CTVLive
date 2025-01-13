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
def write_channels_to_file(channels, filename, categories):
    result_counter = 8  # 每个频道最多写入的次数
    channel_counters = {}

    def write_channels(file, category_name, keyword_list):
        print(f"开始写入{filename}中的{category_name}...")
        file.write(f"\n{category_name},#genre#\n")
        # 注意：这里不再遍历sorted(channels.keys())，因为我们要按categories的顺序处理
        if category_name in channels:  # 确保category_name在channels中存在
            # 对当前类别下的频道按名称排序
            sorted_channels = sorted(channels[category_name], key=lambda x: x[0])  # x[0]是频道名称
            for channel_name, channel_url in sorted_channels:
                if any(keyword in channel_name for keyword in keyword_list):
                    if channel_counters.get(channel_name, 0) < result_counter:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] = channel_counters.get(channel_name, 0) + 1
        else:
            print(f"警告：{category_name}在频道数据中不存在。")

    # 注意：修复了原始代码中的语法错误（缺少逗号）
    keyword_list_map = {
        "央视频道": ['CCTV'],
        "卫视频道": ['卫视'],
        "港澳台": ['香港', '澳门', '台湾'],  # 合并其他关键词
        "少儿频道": ['儿童', '少儿', '动漫', '卡通', '动画'],  # 合并其他关键词
        "电影频道": ['电影', '影院'],  # 合并其他关键词
    }

    # 检查categories中的每个项是否在keyword_list_map中有对应的关键词列表
    # 如果不是，您可能需要处理这种情况（例如，跳过该类别或打印警告）
    # 但在这里，我们假设categories是有效的，并且与keyword_list_map中的键匹配

    with open(filename, 'w', encoding='utf-8') as file:
        for category_name in categories:
            keyword_list = keyword_list_map.get(category_name, [])  # 使用get以防category_name不在映射中
            if keyword_list:  # 确保有关键词列表才写入
                write_channels(file, category_name, keyword_list)


# 定义输入文件和频道数据
#input_file1 = 'output1.txt'  # 第一个输出文件
#input_file2 = 'output2.txt'  # 第二个输出文件
#channels = {
    # 示例频道数据
    #'category1': [('CCTV1', 'http://example.com/cctv1'), ('CCTV2', 'http://example.com/cctv2')],
    #'category2': [('北京卫视', 'http://example.com/bjtv'), ('湖南卫视', 'http://example.com/hntv')],
    # 其他类别...
#}





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
    input_file2 = os.path.join(current_dir, 'tvlist-q.txt')  # 输入文件路径2
    if not os.path.exists(input_file1):
        os.makedirs(input_file1)
    if not os.path.exists(input_file2):
        os.makedirs(input_file2)
    for url in urls:
        print(f"处理URL: {url}")
        channels = fetch_channels(url)   #读取上面url清单
        print(f"获取到的频道数据: {channels}")
        # 写入央视频道和卫视频道到input_file2
        write_channels_to_file(channels, input_file1, ['央视频道', '卫视频道'])
        # 写入其他频道到input_file1
        write_channels_to_file(channels, input_file2, ['央视频道', '卫视频道','港澳台', '少儿频道', '电影频道'])
        print("写入完成。")


        #with open(input_file1, 'r') as file:

            #content = file.read()
        # 打印文件内容
           # print(content)
        
