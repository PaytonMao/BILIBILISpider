# -*- coding: utf-8 -*-
import pymysql
import requests
import json
from bs4 import BeautifulSoup

class api(object):
    def __init__(self):
        self.aidurl = "https://search.bilibili.com/video?keyword=%E6%AD%A6%E6%B1%89&order=click&duration=0&tids_1=0&page={page}"
        self.videoUrl = "https://api.bilibili.com/x/web-interface/view?aid={avNum}"
        self.oidUrl = "https://api.bilibili.com/x/v1/dm/list.so?oid={oid}"
        self.headers = {
            'Connection': 'keep-alive',
            'Origin': 'https://www.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://www.bilibili.com/video/av85512712?spm_id_from=333.851.b_7265706f7274466972737431.10',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': '_uuid=019E07D6-3389-73A3-3EC5-1C2F414DDDE224954infoc; buvid3=828BE641-6F6D-4A24-B5D0-A096A3B55490190964infoc; LIVE_BUVID=AUTO2415732243262806; CURRENT_FNVAL=16; stardustvideo=1; laboratory=1-1; rpdid=|(u)~ll|YR|~0J\'ul~JkkRJRl; UM_distinctid=16e4b8f9f3a57b-0af17259af795d-1c3b6a5b-13c680-16e4b8f9f3b9d1; im_notify_type_21683856=0; sid=897kk76i; DedeUserID=487138497; DedeUserID__ckMd5=394fe57b68bea65b; im_notify_type_487138497=0; LIVE_PLAYER_TYPE=2; SESSDATA=b99b0ada%2C1580805246%2C46093c11; bili_jct=0f36ef624530ed912328ea511537b658; pgv_pvi=3772632064; bp_t_offset_487138497=349933340914054635; INTVER=1; bsource=seo_baidu; CURRENT_QUALITY=64'
        }
        self.connect = pymysql.connect(
            host='localhost',
            db='csvData',
            port=3306,
            user='root',
            passwd='123456',
            charset='utf8',
            use_unicode=False
        )
        self.cursor = self.connect.cursor()
        self.sql = "insert into wuhan_danmu (`danmu`,`videoName`) values (%s,%s)"
    def __getaid(self,page):
        #print("getAid----------start")
        res = self.__doget(self.aidurl.format(page=page))
        for item in list:
            #print(item.find('a').get('href'))
            videoUrl = item.find('a').get('href')
            avNum = str(videoUrl).split('/')[4].split('?')[0].split('av')[1]
            #print(avNum)
            self.__doSpider(avNum)

    def __doSpider(self,avNum):
        res = self.__doget(self.videoUrl.format(avNum=avNum))
        requestHtml = json.loads(res.text)  # 请求页面转为json格式
        #print(requestHtml)
        videoName = requestHtml['data']['title']  # 获取视频tittle
        #print('videoName:----' + videoName)
        barrageOid = requestHtml['data']['cid']  # 获取oid号
        soup = self.__doget(self.oidUrl.format(oid=barrageOid))
        danmakuList = soup.find_all('d')
        for item in danmakuList:
            print("弹幕信息："+item.text+"                          视频名称： "+videoName)
            try:
                self.cursor.execute(self.sql, (item.text, videoName))
                self.connect.commit()
            except(pymysql.err.InternalError,pymysql.err.DataError):
                continue



    def __doget(self, url):
        res = requests.request("GET", url, headers=self.headers)
        res.encoding='utf-8'
        soup = BeautifulSoup(res.text,'html.parser')
        return soup


    def main(self):
        for i in range(30):
            self.__getaid(i+1)


if __name__ == '__main__':
    api().main()



