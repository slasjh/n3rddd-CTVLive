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

all_lines =  []
#读取文本
excudelist_lines=read_txt_to_array('assets/special/ExcludeList.txt') 

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





def tiqu_gjz(output_file, feilei, gjz_or_gjzs):
    try:
        # 假设all_lines是从某个地方获取的文本行列表
        # 这里为了示例，我们将其硬编码在函数内部
        all_lines = [
            "这是一行测试文本。",
            "包含chinamobile.com的文本行：http://www.chinamobile.com/something",
            "另一行包含migu的文本：http://example.com/migu.php",
            "还有一行包含mg的文本：http://example.com/mg.php",
            "以及一行不包含目标网址的文本。"
        ]

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
        print("time: {}".format(datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")))

    except Exception as e:
        print(f"保存文件时发生错误：{e}")


# 定义
urls = [
    "https://ua.fongmi.eu.org/box.php?url=https://xn--dkw0c.v.nxog.top/m/tv",
    "https://ua.fongmi.eu.org/box.php?url=http://%E6%88%91%E4%B8%8D%E6%98%AF.%E6%91%B8%E9%B1%BC%E5%84%BF.com/live.php",
    "https://ua.fongmi.eu.org/box.php?url=http://sinopacifichk.com/tv/live",
]
# 处理
for url in urls:
    if url.startswith("http"):        
        # print(f"time: {datetime.now().strftime("%Y%m%d_%H_%M_%S")}")
        print(f"处理URL: {url}")
        process_url(url)
# 将合并后的文本写入文件
output_file1 = "assets/special/cm.txt"
feilei1 = "移动CM"
gjz1 = ".chinamobile.com"

output_file2 = "assets/special/migu.txt"
feilei2 = "migu分类"
gjz2 = [".migu.", "mg.php", "m.php"]  # 使用列表来存储多个关键字

# 调用函数示例，注意现在第三个参数对于第二个文件是一个列表
tiqu_gjz(output_file1, feilei1, gjz1)
tiqu_gjz(output_file2, feilei2, gjz2)

 
