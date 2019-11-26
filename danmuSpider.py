#coding=utf-8
import requests,json
from bs4 import BeautifulSoup
target='https://api.bilibili.com/x/web-interface/view?aid=replace'
headers = {'Referer':'ttps://www.bilibili.com/','User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
s=input("请输入av号:")
target=target.replace('replace',s)#简单进行替换
req=requests.get(url=target,headers=headers)
js1=json.loads(req.text)
cid=js1['data']['cid']#获取cid号
target='https://api.bilibili.com/x/v1/dm/list.so?oid=replace'
target=target.replace('replace',str(cid))
req=requests.get(url=target,headers=headers)
req.encoding = 'utf-8'#对resopn进行编码转换（因为肯会获取到乱码数据）
bf=BeautifulSoup(req.text,'lxml')
con1=bf.find_all('d')#这里就是进行弹幕分割找到所有弹幕
for each in range(len(con1)):
    print(con1[each].string)