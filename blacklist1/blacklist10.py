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
                #req = urllib.request.Request(encoded_url, headers=headers)
                #req.allow_redirects = True  # 允许自动重定向（Python 3.4+）
                #with urllib.request.urlopen(req, timeout=timeout) as response:
                    #if response.status == 200 or response.status == 206:
                        #success = True
        elif url.startswith("p3p") or url.startswith("p2p") or url.startswith("rtmp") or url.startswith("rtsp") or url.startswith("rtp"):
            success = False
            print(f"{url}此链接为rtp/p2p/rtmp/rtsp等，舍弃不检测")

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


def extract_ipv4_sources(sources):

    ipv4_pattern = re.compile(r'm3u8.*?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

    return [src for src in sources if ipv4_pattern.search(src)]


def device_headers(device_type):
    headers = {
        'tvbox': {
            'User-Agent': 'com.github.tvbox.osc.base.App/1.1.1(Linux;Android 14) ExoplayerLib/2.18.7',
            'Accept': '*/*'
        },
        'easybox': {
            'User-Agent': 'Lavf/58.12.100',
            'Accept': '*/*'
        },
        'pc': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6429.15 Safari/537.36',
            'Accept': '*/*'
        },
        'android': {
            'User-Agent': 'Mozilla/5.0 (Linux;Android 14;22021211RC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Safari/537.36 XiaoMi/MiuiBrowser/18.9.71225',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }
    }
    
    if device_type in headers:
        return headers[device_type]
    else:
        raise ValueError("Unknown device type")

import requests
import time

# 定义一个包含多个 headers 的列表
headers_list = [
    {
        'User-Agent': 'Mozilla/5.0 (Linux;Android 14;22021211RC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Safari/537.36 XiaoMi/MiuiBrowser/18.9.71225',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
    },
    # xiaomi headers 配置
   {
        'User-Agent': 'Lavf/58.12.100',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    },
    # easybox 配置
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
    },
    # PC headers 配置

]


def measure_speed(url):
    url_t = url.rstrip(url.split('/')[-1])

    ts_url = None
    found = False

    def process_m3u8(m3u8_url, headers, processed_headers=None):
        nonlocal found, ts_url
        if processed_headers is None:
            processed_headers = set()

        if headers in processed_headers:
            return
        processed_headers.add(headers)

        response = requests.get(m3u8_url, allow_redirects=True, headers=headers, timeout=2)
        response.raise_for_status()

        final_url = response.url
        final_url_t = final_url.rstrip(final_url.split('/')[-1])

        response_f = requests.get(final_url, headers=headers, timeout=2)
        response_f.raise_for_status()

        lines = response_f.text.strip().split('\n')
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line.startswith('#') and '.ts' in stripped_line:
                ts_url = final_url_t + stripped_line if not stripped_line.startswith('http') else stripped_line
                found = True
                break

        if not found:
            for line in lines:
                stripped_line = line.strip()
                if not stripped_line.startswith('#') and '.m3u8' in stripped_line:
                    new_m3u8_url = final_url_t + stripped_line if not stripped_line.startswith('http') else stripped_line
                    process_m3u8(new_m3u8_url, headers, processed_headers.copy())  # 传递 processed_headers 的副本
                    if found:
                        break

    # 假设 check_url 函数已定义并返回 (elapsed_time, success)
    elapsed_time, success = check_url(url)

    if success and elapsed_time is not None:
        for headers in headers_list:
            process_m3u8(url, headers)
            if found:
                break

        if found:
            print(f"找到的TS文件: {ts_url}")
            start_time = time.time()
            range_request_url = f"{ts_url}?start=0&end=1048576"
            try:
                response = requests.get(range_request_url, headers=headers, stream=True, timeout=5)
                response.raise_for_status()
                total_length = int(response.headers.get('content-length', 0))
                data = b''.join(chunk for chunk in response.iter_content(1024))

                if total_length == 0 or len(data) == 0:
                    print(f"{ts_url} ts文件无法获取内容长度或数据为空，无法测量速度。")
                    return None, elapsed_time

                end_time = time.time()
                download_speed = len(data) / (end_time - start_time) / 1024  # in kB/s
                print(f"{url}的 ts文件下载速度为: {download_speed} kB/s ,{elapsed_time} ms")
                return download_speed, elapsed_time

            except requests.RequestException as e:
                print(f"下载 {ts_url} ts文件失败: {e}")
                return None, elapsed_time
        else:
            print(f"在{url}中没有找到有效的.ts文件条目，且尝试了所有可用的headers。")
            return None, elapsed_time

    else:
        print(f"检查URL {url} 失败或耗时无效。")
        return None, None




    
# 处理单行文本并检测URL
def process_line(line):
    if "#genre#" in line or "://" not in line:
        return None, None, None  # 跳过包含“#genre#”的行或不含“://”的行
    
    try:
        parts = line.split(',')
        if len(parts) != 2:
            raise ValueError("Line does not contain exactly one comma.")
        
        name, url = parts
        url = url.strip()
        
     
        speed, elapsed_time = measure_speed(url)
        if speed and elapsed_time is not None:
            return speed, elapsed_time, line.strip()
            
        else:
            logging.error(f"ts下载failed  for {url}")
            return None, elapsed_time, line.strip()
    
    except Exception as e:
        # 捕获任何未处理的异常并记录错误
        logging.error(f"{url}处理行时发生意外错误 while processing line: {e}")
        return None, None, line.strip()

# 多线程处理文本并检测m3u8 URL
def process_urls_multithreaded(lines, max_workers=30):
    blacklist =  [] 
    successlist = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_line, line): line for line in lines}
        for future in as_completed(futures):
            speed, elapsed_time, result = future.result()
            if speed and elapsed_time is not None:
                successlist.append(f"{speed:.1f}KB/S,{elapsed_time:.2f}ms,{result}")
                print(f"{speed:.1f}KB/S,{elapsed_time:.2f}ms,{result}")
            else:
                blacklist.append(result)
                logging.info(f"URL {result} 被添加到黑名单，因为速度或耗时信息缺失。")
    return successlist, blacklist

# 写入文件
def write_list(file_path, data_list):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data_list:
            item_str = str(item)
            file.write(item_str + '\n')

# 增加外部url到检测清单，同时支持检测m3u格式url
# urls里所有的源都读到这里。
urls_all_lines = []

def get_url_file_extension(url):
    # 解析URL
    parsed_url = urlparse(url)
    # 获取路径部分
    path = parsed_url.path
    # 提取文件扩展名
    extension = os.path.splitext(path)[1]
    return extension

def convert_m3u_to_txt(m3u_content):
    # 分行处理
    lines = m3u_content.split('\n')
    
    # 用于存储结果的列表
    txt_lines = []
    
    # 临时变量用于存储频道名称
    channel_name = ""
    
    for line in lines:
        # 过滤掉 #EXTM3U 开头的行
        if line.startswith("#EXTM3U"):
            continue
        # 处理 #EXTINF 开头的行
        if line.startswith("#EXTINF"):
            # 获取频道名称（假设频道名称在引号后）
            channel_name = line.split(',')[-1].strip()
        # 处理 URL 行
        elif line.startswith("http"):
            txt_lines.append(f"{channel_name},{line.strip()}")
    
    # 将结果合并成一个字符串，以换行符分隔
    # return '\n'.join(txt_lines)
    return txt_lines

url_statistics=[]

def process_url(url):
    try:
        # 打开URL并读取内容
        with urllib.request.urlopen(url) as response:
            # 以二进制方式读取数据
            data = response.read()
            # 将二进制数据解码为字符串
            text = data.decode('utf-8')
            if get_url_file_extension(url)==".m3u" or get_url_file_extension(url)==".m3u8":
                m3u_lines=convert_m3u_to_txt(text)
                url_statistics.append(f"{len(m3u_lines)},{url.strip()}")
                urls_all_lines.extend(m3u_lines) # 注意：extend
            elif get_url_file_extension(url)==".txt":
                lines = text.split('\n')
                url_statistics.append(f"{len(lines)},{url.strip()}")
                for line in lines:
                    if  "#genre#" not in line and "," in line and "://" in line:
                        #channel_name=line.split(',')[0].strip()
                        #channel_address=line.split(',')[1].strip()
                        urls_all_lines.append(line.strip())
    
    except Exception as e:
        print(f"处理URL时发生错误：{e}")


# 去重复源 2024-08-06 (检测前剔除重复url，提高检测效率)
def remove_duplicates_url(lines):
    urls =[]
    newlines=[]
    for line in lines:
        if "," in line and "://" in line:
            # channel_name=line.split(',')[0].strip()
            channel_url=line.split(',')[1].strip()
            if channel_url not in urls: # 如果发现当前url不在清单中，则假如newlines
                urls.append(channel_url)
                newlines.append(line)
    return newlines

# 处理带$的URL，把$之后的内容都去掉（包括$也去掉） 【2024-08-08 22:29:11】
#def clean_url(url):
#    last_dollar_index = url.rfind('$')  # 安全起见找最后一个$处理
#    if last_dollar_index != -1:
#        return url[:last_dollar_index]
#    return url
def clean_url(lines):
    urls =[]
    newlines=[]
    for line in lines:
        if "," in line and "://" in line:
            last_dollar_index = line.rfind('$')
            if last_dollar_index != -1:
                line=line[:last_dollar_index]
            newlines.append(line)
    return newlines

# 处理带#的URL  【2024-08-09 23:53:26】
def split_url(lines):
    newlines=[]
    for line in lines:
        # 拆分成频道名和URL部分
        channel_name, channel_address = line.split(',', 1)
        #需要加处理带#号源=予加速源
        if  "#" not in channel_address:
            newlines.append(line)
        elif  "#" in channel_address and "://" in channel_address: 
            # 如果有“#”号，则根据“#”号分隔
            url_list = channel_address.split('#')
            for url in url_list:
                if "://" in url: 
                    newline=f'{channel_name},{url}'
                    newlines.append(line)
    return newlines

# 取得host
def get_host_from_url(url: str) -> str:
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc
    except Exception as e:
        return f"Error: {str(e)}"

# 使用字典来统计blackhost的记录次数
blacklist_dict = {}
def record_host(host):
    # 如果 host 已经在字典中，计数加 1
    if host in blacklist_dict:
        blacklist_dict[host] += 1
    # 如果 host 不在字典中，加入并初始化计数为 1
    else:
        blacklist_dict[host] = 1


if __name__ == "__main__":
    # 定义要访问的多个URL
    urls = [
        #"https://gitlab.com/p2v5/wangtv/-/raw/main/lunbo.txt",
        #'https://gitlab.com/p2v5/wangtv/-/raw/main/wang-tvlive.txt'
        #'https://raw.githubusercontent.com/kimwang1978/collect-tv-txt/refs/heads/main/live.txt',
        'https://raw.githubusercontent.com/slasjh/n3rddd-CTVLive/refs/heads/ipv4/litelive_cctvweishi_test.txt'
    ]
    for url in urls:
        print(f"处理URL: {url}")
        process_url(url)   #读取上面url清单中直播源存入urls_all_lines

    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取上一层目录
    parent_dir = os.path.dirname(current_dir)
    # 获取再上一层目录
    #parent2_dir = os.path.dirname(parent_dir)
    # # 获取根目录
    # root_dir = os.path.abspath(os.sep)  

    #input_file1 = os.path.join(parent_dir, 'live.txt')  # 输入文件路径1
    input_file1 = os.path.join(current_dir, 'live_test.txt')  # 输入文件路径1
    #input_file2 = os.path.join(current_dir, 'blacklist_auto2.txt')  # 输入文件路径2
    input_file2 = os.path.join(current_dir, 'live_test.txt')  # 输入文件路径2 
    success_file = os.path.join(current_dir, 'whitelist_auto2.txt')  # 成功清单文件路径
    success_file_tv = os.path.join(current_dir, 'whitelist_auto_tv2.txt')  # 成功清单文件路径（另存一份直接引用源）
    blacklist_file = os.path.join(current_dir, 'blacklist_auto2.txt')  # 黑名单文件路径

    # 读取输入文件内容
    lines1 = read_txt_file(input_file1)
    lines2 = read_txt_file(input_file2)
    lines=urls_all_lines + lines1 + lines2 # 从list变成集合提供检索效率⇒发现用了set后加#合并多行url，故去掉
    #lines=urls_all_lines  # Test
    
    # 计算合并后合计个数
    urls_hj_before = len(lines)

    # 分级带#号直播源地址
    lines=split_url(lines)
    urls_hj_before2 = len(lines)

    # 去$
    lines=clean_url(lines)
    urls_hj_before3 = len(lines)

    # 去重
    lines=remove_duplicates_url(lines)
    urls_hj = len(lines)

    # 处理URL并生成成功清单和黑名单
    successlist, blacklist = process_urls_multithreaded(lines)
    
    # 给successlist, blacklist排序
    # 定义排序函数
    def successlist_sort_key(item):
        time_str = item.split(',')[0].replace('KB/S', '')
        return float(time_str)
        # 定义排序函数

    
    successlist=sorted(successlist, key=successlist_sort_key, reverse=True)
    blacklist=sorted(blacklist)

    # 计算check后ok和ng个数
    urls_ok = len(successlist)
    urls_ng = len(blacklist)

    ## 把successlist整理一下，生成一个可以直接引用的源，方便用zyplayer手动check
    def remove_prefix_from_lines(lines):
        result = []
        for line in lines:
            if  "#genre#" not in line and "," in line and "://" in line:
                parts = line.split(",")
                result.append(",".join(parts[2:]))
        return result


    # 加时间戳等
    version=datetime.now().strftime("%Y%m%d-%H-%M-%S")+",url"
    successlist_tv = ["更新时间,#genre#"] +[version] + ['\n'] +\
                  ["whitelist,#genre#"] + remove_prefix_from_lines(successlist)
    successlist = ["更新时间,#genre#"] +[version] + ['\n'] +\
                  ["speed,RespoTime,whitelist,#genre#"] + successlist
    blacklist = ["更新时间,#genre#"] +[version] + ['\n'] +\
                ["blacklist,#genre#"]  + blacklist

    # 写入成功清单文件
    write_list(success_file, successlist)
    write_list(success_file_tv, successlist_tv)

    # 写入黑名单文件
    write_list(blacklist_file, blacklist)

    print(f"成功清单文件已生成: {success_file}")
    print(f"成功清单文件已生成(tv): {success_file_tv}")
    print(f"黑名单文件已生成: {blacklist_file}")

    # 写入history
    timenow=datetime.now().strftime("%Y%m%d_%H_%M_%S")
    history_success_file = f'history/blacklist/{timenow}_whitelist_auto.txt'
    history_blacklist_file = f'history/blacklist/{timenow}_blacklist_auto.txt'
    write_list(history_success_file, successlist)
    write_list(history_blacklist_file, blacklist)
    print(f"history成功清单文件已生成: {history_success_file}")
    print(f"history黑名单文件已生成: {history_blacklist_file}")

    # 执行的代码
    timeend = datetime.now()

    # 计算时间差
    elapsed_time = timeend - timestart
    total_seconds = elapsed_time.total_seconds()

    # 转换为分钟和秒
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)

    # 格式化开始和结束时间
    timestart_str = timestart.strftime("%Y%m%d_%H_%M_%S")
    timeend_str = timeend.strftime("%Y%m%d_%H_%M_%S")

    print(f"开始时间: {timestart_str}")
    print(f"结束时间: {timeend_str}")
    print(f"执行时间: {minutes} 分 {seconds} 秒")
    print(f"urls_hj最初: {urls_hj_before} ")
    print(f"urls_hj分解井号源后: {urls_hj_before2} ")
    print(f"urls_hj去$后: {urls_hj_before3} ")
    print(f"urls_hj去重后: {urls_hj} ")
    print(f"  urls_ok: {urls_ok} ")
    print(f"  urls_ng: {urls_ng} ")


# 确保路径存在
blackhost_dir = os.path.join(current_dir, "blackhost")
os.makedirs(blackhost_dir, exist_ok=True)

# 构造文件名
blackhost_filename = os.path.join(
    blackhost_dir,
    f"{datetime.now().strftime('%Y%m%d_%H_%M_%S')}__count.txt"
)

# 将结果保存为 txt 文件 
def save_blackhost_to_txt(filename=blackhost_filename):
    with open(filename, "w") as file:
        for host, count in blacklist_dict.items():
            file.write(f"{host}: {count}\n")
    print(f"结果已保存到 {filename}")

save_blackhost_to_txt()
            
for statistics in url_statistics: #查看各个url的量有多少 2024-08-19
    print(statistics)
    
