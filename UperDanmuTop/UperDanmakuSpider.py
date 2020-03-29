import requests
from bs4 import BeautifulSoup
import time
import random
import pymysql

class api(object):
    def __init__(self, uid=0,pn=0,sql=None):
        self.uid = uid
        self.pn = pn
        self.aidurl = "https://api.bilibili.com/x/space/arc/search?mid={uid}&ps=30&tid=0&pn={pn}&keyword=&order=click&jsonp=jsonp"   #定位up主首页最多播放接口
        self.cidurl = "https://api.bilibili.com/x/web-interface/view?aid={aid}"
        self.monthdataurl = "https://api.bilibili.com/x/v2/dm/history/index?type=1&oid={cid}&month={monthdata}" #查看当前月份有弹幕天数
        self.danmakuurl = "https://api.bilibili.com/x/v2/dm/history?type=1&oid={oid}&date={monthdata}"
        self.headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Sec-Fetch-Dest': 'empty',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
            'Origin': 'https://www.bilibili.com',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://www.bilibili.com/video/av24594764',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': '_uuid=019E07D6-3389-73A3-3EC5-1C2F414DDDE224954infoc; buvid3=828BE641-6F6D-4A24-B5D0-A096A3B55490190964infoc; LIVE_BUVID=AUTO2415732243262806; CURRENT_FNVAL=16; stardustvideo=1; laboratory=1-1; rpdid=|(u)~ll|YR|~0J\'ul~JkkRJRl; UM_distinctid=16e4b8f9f3a57b-0af17259af795d-1c3b6a5b-13c680-16e4b8f9f3b9d1; im_notify_type_21683856=0; sid=897kk76i; im_notify_type_487138497=0; LIVE_PLAYER_TYPE=2; pgv_pvi=3772632064; CURRENT_QUALITY=116; bp_t_offset_487138497=359149614881144142; INTVER=1; stardustpgcv=0606; bsource=seo_baidu; DedeUserID=487138497; DedeUserID__ckMd5=394fe57b68bea65b; SESSDATA=5f2e718e%2C1599101884%2C95c41*31; bili_jct=c9bc789a55417be4586a7b9cfac6ca44'
        }
        self.connect = pymysql.connect(host='localhost', db='csvData',port=3306,user='root',passwd='123456',charset='utf8', use_unicode=False)
        self.cursor = self.connect.cursor()
        self.sql = sql
        self.list = {}
        self.danmakustats = []
        #self.danmuku = []
        self.monthlist = []

    def __getaid(self):
            print('--------------'+str(self.pn))
            res = self.__doget(self.aidurl.format(uid=self.uid, pn=self.pn))     #count根据up主投稿视频数量修改
            self.list = res['list']['vlist']
            print(self.list)

    def __getdanmaku(self):
        for rs in self.list:
            try:
                res = self.__doget(self.cidurl.format(aid=rs['aid']))
                #print(res)
                #monthlist = self.__doget(self.monthdataurl.format(oid=res['cid']),monthdata=2020.1)
                time.sleep(1)
                self.__danmakuSpider(res['cid'],res['title'])
            except:
                print("-----------------------------视频查找失败，视频最近没有弹幕或视频已被删除")

            # self.danmakustats.append({'name': res['title'], 'cid': res['cid'], 'danmaku': res['stat']['danmaku'],
            #                      'year': time.strftime("%Y",time.localtime(res['pubdate'])),
            #                      'month': time.strftime("%m",time.localtime(res['pubdate']))})

    def __danmakuSpider(self,cid,videoName):
        #先获取当前时间月份
        nowtime = time.strftime("%Y-%m", time.localtime(int(time.time())))
        #获取当前月份存在弹幕的天数列表
        #print(cid)
        #print(nowtime)
        self.monthlist = self.__doget(self.monthdataurl.format(cid=cid,monthdata=nowtime))
        #循环弹幕天数列表

        if len(self.monthlist) == 0:
            return 0
        elif len(self.monthlist) > 5:        #判断天数>5天 使用随机算法找寻随机5天内弹幕
            print('查询5天内所有随机天数弹幕')
            randomArr = self.__int_random(1,len(self.monthlist)-1, 5)
            for item in randomArr:
                #爬取大于5天的弹幕
                danmaku = self.__dodanmuku(self.danmakuurl.format(oid=cid,monthdata=self.monthlist[item]))
                for item in danmaku:
                    print(item.text+"                   "+videoName)
                    self._do_mysql(item.text,videoName)
        elif len(self.monthlist) <= 5:
            for days in self.monthlist:
                #elf.danmuku.append(self.__dodanmuku(self.danmakuurl.format(oid=cid, monthdata=days)))
                danmuku = self.__dodanmuku(self.danmakuurl.format(oid=cid, monthdata=days))
                for item in danmuku:
                    print(item.text+"                    "+videoName)
                    self._do_mysql(item.text, videoName)

    def _do_mysql(self,danmakuText,videoName):
        try:
            self.cursor.execute(self.sql, (danmakuText, videoName))
            self.connect.commit()
        except:
            print("数据插入错误---------------------")



    def __int_random(self,start, stop, n):
        a_list = []              # 定义一个空列表存储随机数
        while len(a_list) < n:
            d_int = random.randint(start, stop)
            if (d_int not in a_list):
                a_list.append(d_int)
            else:
                pass
        return tuple(a_list)     # 将生成的随机数列表转换成元组并返回


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

    def main(self,uid,count,sql):
        self.uid = uid
        self.pn = pn
        self.sql = sql
        self.__getaid()
        self.__getdanmaku()


if __name__ == '__main__':
    spider = api()
    uid = 168598   #up主uid
    sql = "insert into sanren_danmu(`danmu`,`videoName`) values (%s,%s)"
    pnSum = 19   #  up视频页数
    pn = 4
    while pn<pnSum+1:
        spider.main(uid,pn,sql)
        pn = pn+1









