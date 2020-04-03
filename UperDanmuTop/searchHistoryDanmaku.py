import requests
from bs4 import BeautifulSoup
import time
import random
import pymysql


class danmakuApi(object):
    def __init__(self):
        self.mostPlayVideoUrl = "https://api.bilibili.com/x/space/arc/search?mid={mid}&ps=30&tid=0&pn={pn}&keyword=&order=pubdate&jsonp=jsonp"  #获取最多视频播放列表
        self.vidoInfUrl = "https://api.bilibili.com/x/web-interface/view?cid=151165301&bvid=BV157411V72y"   #获取视频信息url
        self.danmakuurl = "https://api.bilibili.com/x/v2/dm/history?type=1&oid={oid}&date={monthdata}"
        self.headers = {
              'Connection': 'keep-alive',
              'Pragma': 'no-cache',
              'Cache-Control': 'no-cache',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
              'Sec-Fetch-Dest': 'empty',
              'Accept': '*/*',
              'Origin': 'https://www.bilibili.com',
              'Sec-Fetch-Site': 'same-site',
              'Sec-Fetch-Mode': 'cors',
              'Referer': 'https://www.bilibili.com/video/BV157411V72y',
              'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
              'Cookie': 'INTVER=1; bsource=seo_baidu; _uuid=51C23958-8D42-45AB-BE94-3022F78DABA502354infoc; buvid3=130D1AA0-4FB4-484F-902E-373A7C83BB53155824infoc; sid=cuc2hd4j; DedeUserID=487138497; DedeUserID__ckMd5=394fe57b68bea65b; SESSDATA=08099e5f%2C1601446454%2C281a2*41; bili_jct=2e282ef8342cc7c900e584b9a794aabc; CURRENT_FNVAL=16; LIVE_BUVID=AUTO3115858948095948; bp_t_offset_487138497=373840902702020141'
        }
        self.payload = {}
        #self.videoList = []


    def __getVideoList(self,conunt,mid):
        pn = 1
        while(pn < conunt):
            time.sleep(3)
            videoInfo = self.__doget(self.mostPlayVideoUrl.format(mid=mid,pn=pn))
            list = videoInfo['list']['vlist']
            for item in list:
                print(item)


            pn = pn+1


    def __doget(self,url):
        print(url)
        res = requests.request("GET", url, headers=self.headers, data = self.payload)
        res = res.json()
        return res['data']

    def main(self):
        self.__getVideoList(10,546195)
        #for item in self.videoList:
            #print(item)



if __name__ == '__main__':
    supider = danmakuApi()
    supider.main()