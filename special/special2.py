import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone


#读取文本方法
def read_txt_to_array(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            return lines
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []



def process_url(url):
    try:

        # 创建一个请求对象并添加自定义header
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

        # 打开URL并读取内容
        with urllib.request.urlopen(req) as response:
            # 以二进制方式读取数据
            data = response.read()
            # 将二进制数据解码为字符串
            text = data.decode('utf-8')
            # 逐行处理内容
            lines = text.split('\n')
            print(f"行数: {len(lines)}")
            for line in lines:
                line = line.strip()
                if  "#genre#" not in line and "," in line and "://" in line and line not in excudelist_lines:
                    # 拆分成频道名和URL部分
                    # channel_name, channel_address = line.split(',', 1)
                    all_lines.append(line.strip())

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




def tiqu_gjz(output_file, feilei, gjz_or_gjzs):
    try:
        # 假设all_lines是从某个地方获取的文本行列表
        # 这里为了示例，我们将其硬编码在函数内部
        #all_lines = [
            #"这是一行测试文本。",
            #"包含chinamobile.com的文本行：http://www.chinamobile.com/something",
            #"另一行包含migu的文本：http://example.com/migu.php",
            #"还有一行包含mg的文本：http://example.com/mg.php",
            #"以及一行不包含目标网址的文本。"
        #]

        # 如果gjz_or_gjzs是字符串，则将其转换为单元素集合以便统一处理
        if isinstance(gjz_or_gjzs, str):
            gjz_set = {gjz_or_gjzs}
        else:
            gjz_set = set(gjz_or_gjzs)

        with open(output_file, 'w', encoding='utf-8') as f:
            # 注意：这里我们不再写入gjz_or_gjzs到文件，因为它可能是多个值
            # 如果您确实需要写入某种标识符，请考虑使用feilei参数
            f.write(f'{feilei},#genre#\n')  # 使用f-string格式化字符串并写入分类信息
            for line in all_lines:
                if any(gjz in line for gjz in gjz_set):
                    f.write(line + '\n')

        print(f"合并后的文本已保存到文件: {output_file}")
        #print("time: {}".format(datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")))

    except Exception as e:
        print(f"保存文件时发生错误：{e}")

all_lines =  []
#读取文本
excudelist_lines=read_txt_to_array('special/ExcludeList.txt') 
# 定义
urls = [
    "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u",
    "https://raw.githubusercontent.com/kimwang1978/collect-tv-txt/main/merged_output.txt",
    "https://raw.githubusercontent.com/slasjh/n3rddd-CTVLive/refs/heads/ipv4/live.txt",
    "https://raw.githubusercontent.com/slasjh/n3rddd-CTVLive/refs/heads/ipv6/live.txt",
]
# 处理
for url in urls:
    if url.startswith("http"):        
        # print(f"time: {datetime.now().strftime("%Y%m%d_%H_%M_%S")}")
        print(f"处理URL: {url}")
        process_url(url)
# 分级带#号直播源地址
all_lines=split_url(all_lines)
# 去$
all_lines=clean_url(all_lines)
# 去重
all_lines=remove_duplicates_url(all_lines)
# 将合并后的文本写入文件
output_file1 = "special/cm.txt"
feilei1 = "移动CM"
#gjz1 = ".chinamobile.com"
gjz1 = [".chinamobile.com", "channel-id=bestzb"]  # 使用列表来存储多个关键字

output_file2 = "special/migu.txt"
feilei2 = "migu分类"
gjz2 = [".migu.", "/migu/", "mg.php", "m.php", "/mg/","live.php",".php?"]  # 使用列表来存储多个关键字

output_file3 = "special/gaoma.txt"
feilei3 = "gaoma分类"
gjz3 = ":35455/"

output_file4 = "special/movie.txt"
feilei4 = "movie分类"
gjz4 = ["经典", "影院", "电影","iHOT爱","newtv","NEWTV","剧场","电视剧","热剧","大片","大剧"]  # 使用列表来存储多个关键字

output_file5 = "special/zixun.txt"
feilei5 = "资讯分类"
gjz5 = ["资讯", "新闻", "凤凰","翡翠"]  # 使用列表来存储多个关键字
output_file6 = "special/child.txt"
feilei6 = "少儿分类"
gjz6 = ["儿童", "少儿", "动漫","卡通","动画"]  # 使用列表来存储多个关键字

# 调用函数示例，注意现在第三个参数对于第二个文件是一个列表
tiqu_gjz(output_file1, feilei1, gjz1)
tiqu_gjz(output_file2, feilei2, gjz2)
tiqu_gjz(output_file3, feilei3, gjz3)
tiqu_gjz(output_file4, feilei4, gjz4)
tiqu_gjz(output_file5, feilei4, gjz5)
tiqu_gjz(output_file6, feilei6, gjz6)

 
