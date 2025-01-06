import requests
import re
import cv2
import subprocess
import time
from io import BytesIO
from urllib.parse import urlparse

def fetch_sources(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

def extract_ipv4_sources(sources):
    ipv4_pattern = re.compile(r'm3u8.*?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    return [src for src in sources if ipv4_pattern.match(src)]

def check_image(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
        if cv2.countNonZero(image) == 0:
            return False
    except Exception as e:
        print(f"Error checking image for {url}: {e}")
        return False
    return True

def validate_source(source):
    parsed = urlparse(source)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    playlist_url = source
    image_url = f"{base_url}/screenshot.jpg"  # Assuming screenshot.jpg is available at the same base URL

    if not check_image(image_url):
        return False, None

    try:
        # Using ffmpeg to validate the stream (install ffmpeg first)
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', playlist_url,
            '-c', 'copy',
            '-f', 'null', '-',
            '-v', 'error',
            '-y',
            '-timeout', '5000000',  # 5 seconds timeout
            '-probesize', '32768',
            '-analyzeduration', '32768'
        ]
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, None  # We could return additional info here if needed
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg validation failed for {source}: {e.stderr.decode()}")
        return False, None

def measure_speed(source):
    start_time = time.time()
    parsed = urlparse(source)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    playlist_url = source

    # Here we just download a small part of the stream to measure speed
    # Adjust the range as needed
    range_request_url = f"{playlist_url}?start=0&end=1048576"  # 1MB range
    response = requests.get(range_request_url, stream=True, timeout=5)
    total_length = int(response.headers.get('content-length', 0))
    data = response.content
    end_time = time.time()

    if total_length == 0 or len(data) == 0:
        return 0

    download_speed = len(data) / (end_time - start_time) / (1024 ** 2)  # in MB/s
    return download_speed

def main():
    url = 'https://raw.githubusercontent.com/ssili126/tv/main/itvlist.txt'
    sources = fetch_sources(url)
    ipv4_sources = extract_ipv4_sources(sources)

    valid_sources = []
    for source in ipv4_sources:
        is_valid, _ = validate_source(source)
        if is_valid:
            valid_sources.append(source)

    sorted_sources = sorted(valid_sources, key=measure_speed, reverse=True)

    for src in sorted_sources:
        speed = measure_speed(src)
        print(f"Source: {src}, Speed: {speed:.2f} MB/s")

if __name__ == "__main__":
    import numpy as np  # Don't forget to import numpy for image processing
    main()
