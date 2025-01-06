ip_version_priority = "ipv4"

source_urls = [
    "http://156.238.251.122:35455/tv.m3u", #ADDED BY lee from sshh. ON 31/12/2024
    "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u", #ADDED BY lee from sshh. ON 4/1/2025
    "https://raw.githubusercontent.com/Guovin/TV/gd/output/result.m3u", #ADDED BY lee from Guovin/TV/gd/ (juhe) ON 31/12/2024
    "https://raw.githubusercontent.com/zwc456baby/iptv_alive/master/live.m3u", #ADDED BY lee from zwc456baby cu (juhe) ON 31/12/2024 
    "https://live.fanmingming.com/tv/m3u/ipv6.m3u", #ADDED BY lee from fanmingming. ON 31/12/2024 
    "https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u", #ADDED BY lee from https://tv.iill.top/m3u/Gather" ON 31/12/2024 
    "http://175.178.251.183:6689/live.m3u", #ADDED BY lee from yuanlz77" ON 31/12/2024  
    "https://live.iptv365.org/live.txt", #ADDED BY lee from kimwang1978/collect-tv-txt (juhe) ON 31/12/2024 
    "https://raw.githubusercontent.com/hero1898/tv/refs/heads/main/IPTV.m3u", #ADDED BY lee from hero1898 (juhe) ON 31/12/2024 
    "https://live.zbds.top/tv/iptv6.txt", #ADDED zbds (juhe) ON 31/12/2024 
    "https://live.zbds.top/tv/iptv4.txt", #ADDED zbds (juhe) ON 31/12/2024
    "https://raw.githubusercontent.com/n3rddd/CTVLive/master/live.m3u", #ADDED /n3rddd (juhe) ON 31/12/2024
    "https://raw.githubusercontent.com/xiongjian83/zubo/refs/heads/main/live.txt", #ADDED xiongjian83 (juhe) ON 31/12/2024
    "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u", #ADDED /YueChan(juhe) ON 31/12/2024    
]

url_blacklist = [
    "epg.pw/stream/",
    "103.40.13.71:12390",
    "[2409:8087:1a01:df::4077]/PLTV/",
    "8.210.140.75:68",
    "154.12.50.54",
    "yinhe.live_hls.zte.com",
    "8.137.59.151",
    "[2409:8087:7000:20:1000::22]:6060",
    "histar.zapi.us.kg",
    "www.tfiplaytv.vip",
    "dp.sxtv.top",
    "111.230.30.193",
    "148.135.93.213:81",
    "live.goodiptv.club",
    "wouu.net",
    "kkk.jjjj.jiduo.me",
    "iptv.luas.edu.cn"
]

announcements = [
    {
        "channel": "🤠小土豆央视卫视",
        "entries": [
            {"name":"小土豆直播","url":"https://cors.isteed.cc/https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/N3RD/W/CTVThemeSong1.mp4","logo":"https://cors.isteed.cc/https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/N3RD/W/ICON1.png"},
            {"name":"免费自用勿商用","url":"https://cors.isteed.cc/https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/N3RD/W/CTVThemeSong2.mp4","logo":"https://cors.isteed.cc/https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/N3RD/W/ICON2.png"},
            {"name":"更新日期","url":"https://cors.isteed.cc/https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/N3RD/W/CRIMETVPV1.mkv","logo":"https://cors.isteed.cc/https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/N3RD/W/ICON3.png"},
            {"name":"20241231","url":"https://cors.isteed.cc/https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/N3RD/W/CRIMETVPV2.mkv","logo":"https://cors.isteed.cc/https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/N3RD/W/ICON4.png"}
        ]
    }
]

epg_urls = [
    "https://live.fanmingming.com/e.xml",
    "http://epg.51zmt.top:8000/e.xml",
    "http://epg.aptvapp.com/xml",
    "https://epg.pw/xmltv/epg_CN.xml",
    "https://epg.pw/xmltv/epg_HK.xml",
    "https://epg.pw/xmltv/epg_TW.xml"
]
