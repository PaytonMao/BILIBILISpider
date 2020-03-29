from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pymysql
import random
from selenium import webdriver
import time
import json
from bs4 import BeautifulSoup
import requests

headers = {
  'Connection': 'keep-alive',
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
  'Origin': 'https://www.bilibili.com',
  'Sec-Fetch-Site': 'same-site',
  'Sec-Fetch-Mode': 'cors',
  'Referer': 'https://www.bilibili.com/video/av1561567',
  'Accept-Encoding': 'gzip, deflate, br',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'Cookie': '_uuid=019E07D6-3389-73A3-3EC5-1C2F414DDDE224954infoc; buvid3=828BE641-6F6D-4A24-B5D0-A096A3B55490190964infoc; LIVE_BUVID=AUTO2415732243262806; CURRENT_FNVAL=16; stardustvideo=1; laboratory=1-1; rpdid=|(u)~ll|YR|~0J\'ul~JkkRJRl; UM_distinctid=16e4b8f9f3a57b-0af17259af795d-1c3b6a5b-13c680-16e4b8f9f3b9d1; im_notify_type_21683856=0; sid=897kk76i; im_notify_type_487138497=0; LIVE_PLAYER_TYPE=2; pgv_pvi=3772632064; bp_t_offset_487138497=350218672773094082; CURRENT_QUALITY=112; INTVER=1; bsource=seo_baidu; DedeUserID=487138497; DedeUserID__ckMd5=394fe57b68bea65b; SESSDATA=2d699c90%2C1583488532%2C257e2621; bili_jct=ee1852b2e90e131ee8c1485eb2b1685b'
}

browser = webdriver.Chrome('/Users/maopeidong/Downloads/chromedriver')
WAIT = WebDriverWait(browser, 10)
browser.set_window_size(1400, 900)
es = Elasticsearch(hosts="http://172.16.115.128/", port=9200)
body = {
    "properties": {
        "danmu": {
            "type": "keyword",
            "fielddata": "true",
            "analyzer": "ik_max_word",
            "search_analyzer": "ik_smart"
        },
        "videoName": {
            "type": "keyword"
        }
    }

}
es.indices.create(index="lex_danmu")
connect = pymysql.connect(
            host = 'localhost',
            db = 'csvData',
            port = 3306,
            user = 'root',
            passwd = '123456',
            charset = 'utf8',
            use_unicode = False
        )
cursor = connect.cursor()
sql = "insert into lex_danmu (`danmu`,`videoName`) values (%s,%s)"
n=2

def search(url,pagenum):                       # 查找方法
    print('执行search方法----开始访问'+str(pagenum)+'页内容')
    browser.get(url)
    time.sleep(2)
    mostClick = WAIT.until(EC.element_to_be_clickable((By.XPATH,r'//div[@class="be-tab"]')))  #定位最多播放
    mostClick.click()                          #点击
    time.sleep(2)
    getSourse()

def getSourse():                               #获取页面文件
    print('执行获取网页文件方法')
    WAIT.until(EC.presence_of_all_elements_located((By.XPATH, r'//ul[@class="clearfix cube-list"]')))
    print('获取到视频列表')
    html = browser.page_source                 # 解析页面源码
    soup = BeautifulSoup(html, 'html.parser')
    list = soup.find(class_='clearfix cube-list')
    for item in list:
        videoID = item.get('data-aid')         #获取视频id
        print(videoID)
        time.sleep(1)
        Barragespider(videoID)

def Barragespider(av):
    print('获取视频请求')
    target='https://api.bilibili.com/x/web-interface/view?aid='+av
    browser.get(target)
    requestHtml = browser.page_source
    soup = BeautifulSoup(requestHtml, 'html.parser')
    print(soup.text)
    requestHtml = json.loads(soup.text)        #请求页面转为json格式
    videoName = requestHtml['data']['title']   # 获取视频tittle
    print('videoName:----'+videoName)
    barrageOid = requestHtml['data']['cid']    # 获取oid号
    print(barrageOid)
    time.sleep(1)                              #我睡

    month = 12
    while month >= 11:                         #循环最近2个月
        print('开始循环月份，当前月为' + str(month))
        monthurl = 'https://api.bilibili.com/x/v2/dm/history/index?type=1&oid='+str(barrageOid)+'&month=2019-' + str(month)
        response = requests.request("GET", monthurl, headers=headers)
        time.sleep(2)                          #我再睡
        soup = BeautifulSoup(response.content, 'html.parser')
        monthHtml = json.loads(soup.text)
        print(monthHtml)
        month = month - 1
        try:
            monthdata = monthHtml['data']
            print(monthdata)
        except :
            continue
        #monthMessage = monthHtml['message']
        #print("mothMessage:---------------"+monthMessage)
        if monthdata == None:
            print('当前月份没有弹幕，退出当前循环')
            continue
        print(monthdata)

        #修改版本：如果monthdata<5 获取范围内全部弹幕
        #         如果monthdata>5  获取范围内5天的随机弹幕
        monthNum = len(monthdata)               #计算出弹幕出现天数
        if monthNum > 5:
            print("视频出现天数>5")
            randomArr =  int_random(1,monthNum-1,5)
            for item in randomArr:
                DanmuSpider(monthdata[item],barrageOid,videoName)
        else:
            print("视频出现天数<5")
            for item in monthdata:
                DanmuSpider(item,barrageOid,videoName)


def DanmuSpider(randomMon,barrageOid,videoName):
    print('月份格式：' + str(randomMon))
    videoUrl = 'https://api.bilibili.com/x/v2/dm/history?type=1&oid=' + str(barrageOid) + '&date=' + str(randomMon)
    videoResponse = requests.request("GET", videoUrl, headers=headers)
    time.sleep(2)  # 我还睡
    videoSoup = BeautifulSoup(videoResponse.content, 'html.parser')
    barrage = videoSoup.find_all('d')
    print('获取结果集成功')

    danmudata = []
    for item in barrage:
        barrageText = item.text
        print('弹幕信息：  ' + barrageText+"                   "+"视频名称"+videoName)

        try:
            cursor.execute(sql, (barrageText,videoName))
            connect.commit()
        except:
            print('数据插入错误！---------------------------------------------------------------')

        action = {"_index": "lex_danmu",
                  "doc_type": "doc",
                  "_source": {"danmu": barrageText,
                              "videoName": videoName
                  }
        }
        danmudata.append(action)

    elasticSearch(danmudata)


def int_random(start, stop, n):
    # 定义一个空列表存储随机数
    a_list = []
    while len(a_list) < n:
        d_int = random.randint(start, stop)
        if (d_int not in a_list):
            a_list.append(d_int)
        else:
            pass
    #将生成的随机数列表转换成元组并返回
    return tuple(a_list)


def elasticSearch(danmudate):
    try:
        helpers.bulk(es, danmudate)
    except:
        print("存入数据错误！-----------")



def main():
    print('开始任务')
    pagenum = 1
    while pagenum < 10:  # 34为页数
        url = 'https://space.bilibili.com/777536/video?tid=0&page='+str(pagenum)+'&keyword=&order=pubdate'
        search(url, pagenum)
        pagenum = pagenum+1


if __name__ == '__main__':
    main()
    browser.close()