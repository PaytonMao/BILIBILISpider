from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait  #selenium webDriverWait等待方法
from selenium.webdriver.support import expected_conditions as EC   #判断包
from selenium.webdriver.common.by import By   #定位包
from bs4 import BeautifulSoup
import xlwt




driver = webdriver.Chrome()   #获取浏览器对象
Wait = WebDriverWait(driver,10) #浏览器等待，参数1 选择浏览器   参数2 设置浏览器超时时间
driver.set_window_size(1400.900)     #设置浏览器显示位置
book = xlwt.Workbook(encoding='utf-8',style_compression=0)   #style_compression:表示是否压缩
sheet = book.add_sheet('NBA视频',cell_overwrite_ok=True)  #cell_overwrite_ok=True 表格为可写
sheet.write(0, 0, '名称')
sheet.write(0, 1, '地址')
sheet.write(0, 2, '描述')
sheet.write(0, 3, '观看次数')
sheet.write(0, 4, '弹幕数')
sheet.write(0, 5, '发布时间')

n = 1    #页数


def search():
    try:
        print("开始")
        driver.get('https://www.bilibili.com/')

        #解决登录遮罩
        # until方法等待返回结果为True
        # EC.element_to_be_clickable判断某个元素中是否可见并且可实现
        index = Wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#primary_menu > ul > li.home > a")))
        index.click()

        #  presence_of_element_located  判断某个元素是否被加到了dom树里，并不代表该元素一定可见
        input = Wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"#banner_link > div > div > form > input")))
        submit = Wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="banner_link"]/div/div/form/button')))

        input.send_keys('NBA')  #设置查询内容
        submit.click()

        print('跳转至新窗口')
        new_window = driver.window_handles #h获取新窗口句柄，如无新窗口句柄，则无法定位页面元素
        driver.switch_to.window(new_window[1])  #切换新窗口

        get_source()
        total = Wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#server-search-app > div.contain > div.body-contain > div > div.page-wrap > div > ul > li.page-item.last > button")))
        print(total)

        return int(total.text)

    except TimeoutException:
        return search()

def save_to_excel(soup):
    list = soup.find(class_='all-contain').find_all(class_='info')

    for item in list:
        item_title = item.find('a').get('title')
        item_link = item.find('a').get('href')
        item_dec = item.find(class_='des hide').text
        item_view = item.find(class_='so-icon watch-num').text
        item_biubiu = item.find(class_='so-icon hide').text
        item_date = item.find(class_='so-icon time').text

        print('爬取'+item_title)

        global n

        sheet.write(n, 0, item_title)
        sheet.write(n, 1, item_link)
        sheet.write(n, 2, item_dec)
        sheet.write(n, 3, item_view)
        sheet.write(n, 4, item_biubiu)
        sheet.write(n, 5, item_date)

        n = n+1


def next_page(page_Num):
    try:
        print("开始寻找下一页数据")
        next_buton = Wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#server-search-app > div.contain > div.body-contain > div > div.page-wrap > div > ul > li.page-item.next > button')))
        next_buton.click()
        Wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#server-search-app > div.contain > div.body-contain > div > div.page-wrap > div > ul > li.page-item.active > button')),str(page_Num))
        get_source()
    except TimeoutException:
        driver.refresh()
        return next_page(page_Num)




def get_source():
    Wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'#server-search-app > div.contain > div.body-contain > div > div.result-wrap.clearfix')))
    html = driver.page_source    #解析页面源码
    soup = BeautifulSoup(html,'lxml')
    save_to_excel(soup)















