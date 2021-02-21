import json
import random
import time

import requests
import xlrd as xlrd
import xlwt as xlwt
import matplotlib.pyplot as pl
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# user_agent列表
user_agent_list = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36'
]


def get_html(url):
    headers = {
        'Referer': 'http://fund.eastmoney.com/',
        'User-Agent': random.choice(user_agent_list),
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    try:
        resp = requests.get(url, headers=headers)
        print(resp.text)
        resp.encoding = "utf-8"
        # print(resp.status_code)
        if resp.status_code == 200:
            data = resp.text
            data = data[data.find("["):data.rfind("]") + 1]
            return json.loads(data)
        print("没有爬取到相应的内容")
        return None
    except Exception:
        print("没有爬取到相应的内容")
        return None


def write_excel(data, filename):
    excelpath = filename + ".xls"  # 新建excel文件
    workbook = xlwt.Workbook(encoding='utf-8')  # 写入excel文件
    sheet = workbook.add_sheet('Sheet1', cell_overwrite_ok=True)  # 新增一个sheet工作表
    headlist = [u'日期', u'单位净值', u'累计净值', u'日增长率', ]  # 写入数据头
    row = 0
    col = 0
    for head in headlist:
        sheet.write(row, col, head)
        col += 1
    for i in range(0, len(data)):
        sheet.write(i + 1, 0, data[i]["FSRQ"])
        sheet.write(i + 1, 1, data[i]["DWJZ"])
        sheet.write(i + 1, 2, data[i]["LJJZ"])
        sheet.write(i + 1, 3, data[i]["JZZZL"])
    workbook.save(excelpath)


def read_excel(filename):
    file_name = xlrd.open_workbook(filename)  # 得到文件
    table = file_name.sheets()[0]  # 得到sheet页
    nrows = table.nrows  # 总行数
    ncols = table.ncols  # 总列数
    i = 1
    fsrqs = []
    dwjzs = []
    ljjzs = []
    jzzzls = []
    while i < 100:
        fsrq = table.row_values(i)[0].replace("-", "")  # 得到数字列数据
        fsrqs.append(fsrq)
        dwjz = table.row_values(i)[1]
        dwjzs.append(dwjz)
        ljjz = table.row_values(i)[2]
        ljjzs.append(ljjz)
        jzzzl = table.row_values(i)[3]
        print(jzzzl)
        jzzzls.append(jzzzl)
        i = i + 1

    # 数据归一化
    fsrqs = list(map(int, fsrqs))
    dwjzs = list(map(float, dwjzs))
    ljjzs = list(map(float, ljjzs))
    return fsrqs, dwjzs, ljjzs


def hua_tu(fsrqs, dwjzs, ljjzs):
    # 画图
    pl.rcParams["font.sans-serif"] = ["FangSong"]
    pl.rcParams.update({'font.size': '16'})
    pl.figure(figsize=(16, 9))
    pl.xlabel("日期")
    pl.ylabel("单位净值")

    # 准备数据
    arr = np.array(list(zip(fsrqs, dwjzs, ljjzs)))
    pl.plot(arr[:, [0]], arr[:, [1]], label='单位净值变化')
    pl.plot(arr[:, [0]], arr[:, [2]], label='累计净值变化')

    # 预测
    test_data = np.array([20201228, 20201229, 20201230, 20201231, 20210101]).reshape(5, 1)
    ploy = PolynomialFeatures(degree=3)
    x_ploy = ploy.fit_transform(arr[1:, [0]])
    liner_req = LinearRegression()
    liner_req.fit(x_ploy, arr[1:, [2]])
    preg = liner_req.predict(ploy.fit_transform(test_data))
    print(preg)
    pl.plot(test_data, preg, label="预测数据")
    pl.legend()
    pl.show()


if __name__ == '__main__':
    t = time.time()
    rt = int(round(t * 1000))
    result = []
    code_num = input('请输入基金编码:')
    for num in range(1, 10):
        url = "http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18308192278761728433_1609140983486&fundCode=" + code_num + "&pageIndex=" + str(
            num) + "&pageSize=20&startDate=&endDate&_=" + str(rt)
        data = get_html(url)
        print(num, data)
        if data:
            result.extend(data)
        time.sleep(random.randint(1, 10))  # 设置随机时间间隔
    write_excel(result, code_num)

    fsrqs, dwjzs, ljjzs = read_excel(code_num + ".xls")
    hua_tu(fsrqs, dwjzs, ljjzs)
