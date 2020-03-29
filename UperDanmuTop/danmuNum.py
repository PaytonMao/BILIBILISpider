#coding=utf-8
import pymysql
import xlwt

# book = xlwt.Workbook()
# sheet = book.create_sheet(index=0)
# sheet.cell(1,1).value = '弹幕text'
# sheet.cell(1,2).value = '重复数量'
# sheet.cell(1,3).value = '统计数量'
book=xlwt.Workbook(encoding='utf-8',style_compression=0)    #style_compression:表示是否压缩
sheet=book.add_sheet('散人弹幕',cell_overwrite_ok=True)
sheet.write(0,0,'弹幕text')
sheet.write(0,1,'重复数量')
sheet.write(0,2,'统计数量')
n = 1
connection = pymysql.connect(
    host='localhost',
    db='csvData',
    port=3306,
    user='root',
    passwd='123456',
    charset='utf8',
    use_unicode=False
)
def save_to_excel(danmu,num,countnum):
    global n
    sheet.write(n, 0, danmu)
    sheet.write(n, 1, num)
    sheet.write(n, 2, countnum)
    # sheet.cell(n,1).value = danmu
    # sheet.cell(n,2).value = num
    # sheet.cell(n,3).value = countnum
    n = n + 1

def connect(connection):
    cursor = connection.cursor()
    sql = 'select distinct danmu,count(danmu) as count from sanren_danmu group by danmu order by count desc;'
    cursor.execute(sql)
    danmuArr = cursor.fetchmany(300)
    #print(danmuArr)
    for item in danmuArr:
        danmu = bytes(item[0]).decode('utf-8')
        print("重复弹幕：  "+danmu,"重复数量：   "+str(item[1]))

        sql = "select count(*) from sanren_danmu where danmu like '"+danmu+"%%%%'"      #or'%%%%"+danmu+"';"
        cursor.execute(sql)
        danmuArrin = cursor.fetchmany(5)
        for i in danmuArrin:
            print("---------统计弹幕:   "+str(i))
            save_to_excel(danmu,item[1],i[0])

def main():
    connect(connection)
    book.save(u'散人弹幕TOP.slsx')

if __name__ == '__main__':
    main()