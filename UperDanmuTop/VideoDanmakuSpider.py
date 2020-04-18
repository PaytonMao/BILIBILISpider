import requests
from bs4 import BeautifulSoup
import time
import random
import pymysql

class api(object):
    def __init__(self,sql=None):
        self.aidurl = "https://api.bilibili.com/x/web-interface/view?bvid={aid}"
        self.monthdataurl = "https://api.bilibili.com/x/v2/dm/history/index?type=1&oid={cid}&month={monthdata}"
        self.danmakuurl = "https://api.bilibili.com/x/v2/dm/history?type=1&oid={oid}&date={monthdata}"
        self.headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Sec-Fetch-Dest': 'empty',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'Origin': 'https://www.bilibili.com',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://www.bilibili.com/video/BV1rx411t7nz',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': '_uuid=019E07D6-3389-73A3-3EC5-1C2F414DDDE224954infoc; buvid3=828BE641-6F6D-4A24-B5D0-A096A3B55490190964infoc; LIVE_BUVID=AUTO2415732243262806; CURRENT_FNVAL=16; stardustvideo=1; laboratory=1-1; rpdid=|(u)~ll|YR|~0J\'ul~JkkRJRl; UM_distinctid=16e4b8f9f3a57b-0af17259af795d-1c3b6a5b-13c680-16e4b8f9f3b9d1; im_notify_type_21683856=0; sid=897kk76i; im_notify_type_487138497=0; LIVE_PLAYER_TYPE=2; pgv_pvi=3772632064; CURRENT_QUALITY=116; DedeUserID=487138497; DedeUserID__ckMd5=394fe57b68bea65b; SESSDATA=5f2e718e%2C1599101884%2C95c41*31; bili_jct=c9bc789a55417be4586a7b9cfac6ca44; PVID=2; bsource=seo_baidu; bp_t_offset_487138497=378877709633859228'
        }
        self.connect = pymysql.connect(host='localhost', db='csvData',port=3306,user='root',passwd='123456',charset='utf8', use_unicode=False)
        self.cursor = self.connect.cursor()
        self.sql = sql
        self.monthlist = []


    def __danmakuSpider(self,cid,videoName,videoTime):
            danmaku = self.__dodanmuku(self.danmakuurl.format(oid=cid,monthdata=videoTime))
            for item in danmaku:
                print(item.text+"                   "+videoName)
                self.__do_mysql(item.text,videoName)

    def __do_mysql(self,danmakuText,videoName):
        try:
            self.cursor.execute(self.sql, (danmakuText, videoName))
            self.connect.commit()
        except:
            print("数据插入错误---------------------")


    def __doget(self,url):
        res = requests.request("GET",url,headers = self.headers)
        res = res.json()
        print(res)
        return res['data']


    def __dodanmuku(self,url):
        print(url)
        res = requests.request("GET",url,headers = self.headers)
        print(res)
        res = BeautifulSoup(res.content, 'html.parser')
        return res.find_all('d')


    def main(self,aid,videoTime,sql):
        self.sql = sql
        res = self.__doget(self.aidurl.format(aid=aid))
        print("cid-----------"+str(res['cid']))
        self.monthlist = self.__doget(self.monthdataurl.format(cid=res['cid'], monthdata=videoTime))
        for item in self.monthlist:
            print(item)
            self.__danmakuSpider(res['cid'],res['title'],item)



if __name__ == '__main__':
    spider = api()
    sql = "insert into sanren_danmu(`danmu`,`videoName`) values (%s,%s)"
    videoTime = "2020-02"
    aid = "BV1rx411t7nz"
    spider.main(aid,videoTime,sql)









