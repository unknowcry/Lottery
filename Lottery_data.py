# -*- coding: utf-8 -*-
"""
@author unknowcry
@date 2020-4-12
@desc 彩票数据
@filename Lottery_data.py
tips:
数据来自：http://kaijiang.500.com

"""

import requests
import re
import random
import datetime
import threading
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor,as_completed

class Lottery:
    """
    单一网页数据获取
    """
    no=None
    url=None
    header=None
    data=None
    data_history=None
    new_url=None
    __threadlock=None
    def __init__(self, no=None):
        '''
        :param no:期号
        '''
        if no == None:
            self.no=None
        else:
            self.no=no    
        self.url=None
        self.header=None
        self.data=None
        self.data_history=None
        self.new_url='http://kaijiang.500.com/dlt.shtml'
        self.threadlock=threading.Lock()

    def set_header(self):
        """
        随机生成ip，设置X-Forwarded-For
        设置用户代理
        :return:
        """
        if self.header == None:
            ua = UserAgent()
            ip = '{}.{}.{}.{}'.format(112, random.randint(64, 68), random.randint(0, 255), random.randint(0, 255))
            self.header={
                "X-Forwarded-For": ip,
                "User-Agent":ua.random
            }
        else:
            pass

    def set_url(self):
        """
        :return:
        """
        self.url='http://kaijiang.500.com/shtml/dlt/{}.shtml?'.format(self.no)

    def get_response(self,url):
        """
        链接测试
        :return: get请求返回的response
        """
        response = requests.get(url=url, headers=self.header)
        return response

    def get_html(self,response):
        """
        :return: html文档
        """
        try:
            r=response
            r.raise_for_status()
            charset=re.search(re.compile(r'charset=(\w+)'),r.text).group()[8:]
            r.encoding=charset
            return r.text
        except Exception as err:
            print(err)
            return ''
    
    def fill_data(self, soup):
        """
        :param soup:
        :return:
        """
        try:
            tableinfo=soup.find('table','kj_tablelist02')
            response_no=re.findall(re.compile(r'<font class="cfont2"><strong>(\d+)</strong></font>'),str(tableinfo))[0]
            if int(response_no) != int(self.no):
                raise Exception('期号错误，响应期号{0}不匹配请求期号{1}'.format(response_no,self.no))
            else:
                date_l=re.findall(re.compile(r'(\d+)年(\d+)月(\d+)日 兑奖截止日期：(\d+)年(\d+)月(\d+)日</span></td>'),str(tableinfo))
                date_start=datetime.date(int(date_l[0][0]),int(date_l[0][1]),int(date_l[0][2]))
                date_end=datetime.date(int(date_l[0][3]),int(date_l[0][4]),int(date_l[0][5]))
                nums=tuple(re.findall(re.compile(r'>(\d\d)<'),str(tableinfo)))
                money_l=re.findall(r'<span class="cfont1">(\d+(\.\d+)?)',str(tableinfo))
                sale=money_l[0][0]
                jackpot=money_l[1][0]
                self.data=tuple((response_no,nums,date_start,date_end,sale,jackpot))
        except Exception as err:
            print(err)

    def get_newno(self):
        """
        :return: bool,最新期号
        """
        self.set_header()
        response=self.get_response(self.new_url)
        if response.status_code != 200:
            print('error\n',response.status_code,self.url)
            return False,None
        else:
            soup=BeautifulSoup(self.get_html(response),'html.parser')
            tableinfo=soup.find('span','iSelectBox')
            newno=re.findall(re.compile(r'(\d\d\d\d\d)</a>'),str(tableinfo))[0]
            return True,newno

    def get_nos(self):
        """
        :return: 历史期号
        """
        self.set_header()
        response=self.get_response(self.new_url)
        if response.status_code != 200:
            print('error\n',response.status_code,self.url)
        else:
            soup=BeautifulSoup(self.get_html(response),'html.parser')
            tableinfo=soup.find('span','iSelectBox')
            nos=re.findall(re.compile(r'(\d\d\d\d\d)</a>'),str(tableinfo))
            return nos[1:]

    def data_single(self,no=None):
        """
        :return: bool,no期数据
        """
        if no == None:
            pass
        else:
            self.no=no
        self.set_header()
        self.set_url()
        response=self.get_response(self.url)
        if response.status_code != 200:
            print('error\n',response.status_code,self.url)
            return False,None
        else:
            soup=BeautifulSoup(self.get_html(response),'html.parser')
            self.fill_data(soup)
        return True,self.data

        
class Lottery_multi:
    """
    多网页数据获取
    """
    number=None
    data=None
    __threadlock=None
    max_workers=None
    nos=None
    renos=None
    list=None
    def __init__(self,number=None,max_workers=8):
        """
        :param number: 数量
        :param max_workers=5:默认线程数
        """
        self.number=number
        self.data=set()
        self.threadlock=threading.Lock()
        self.max_workers=max_workers
        self.nos=Lottery().get_nos()
        if number != None:
            self.nos=self.nos[:number]
        self.renos=None
        self.list=None

    def thread_onedata(self,no):
        """
        :param no: 期号
        :return: 期号,bool
        """
        a=Lottery()
        data=a.data_single(no)[1]
        if data == None:
            flag=False
        else:
            flag=True
            self.threadlock.acquire()
            self.data.add(data)
            self.threadlock.release()
        return no,flag

    def data_multi(self,number=None):
        """
        :return: 历史数据
        """
        self.data.clear()
        nos=self.nos
        with ThreadPoolExecutor(max_workers=self.max_workers) as t:
            obj_list=[]
            for i in nos:
                obj=t.submit(self.thread_onedata,i)
                obj_list.append(obj)
            for future in as_completed(obj_list):
                no,flag=future.result()
                if flag:
                    print('thread',no,'done')
                else:
                    print('thread',no,'failed')
        self.check()
        return self.data

    def check_no(self,number=None):
        """
        :param number: 期数量
        :return: 未匹配期号列
        """
        nos=self.nos
        if number != None:
            nos=nos[:number]
        for data in self.data:
            i=data[0]
            nos.remove(i)
        self.renos=nos
        print('check_no done')
        return nos

    def adddata(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as t:
            obj_list=[]
            for i in self.renos:
                print('thread',i,'restart')
                obj=t.submit(self.thread_onedata,i)
                obj_list.append(obj)
            for future in as_completed(obj_list):
                no,flag=future.result()
                if flag:
                    print('thread',no,'done')
                else:
                    print('thread',no,'failed')
        print('adddata done')

    def check(self):
        self.check_no(self.number)
        if len(self.renos)==0:
            print('no done')
            return True
        else:
            print('no',self.renos)
            self.adddata()
            self.check_no(self.number)
            if len(self.renos)==0:
                return True
            else:
                return False

    def get_list(self):
        """
        :return: 数据以顺序列表返回
        """
        self.list=list(self.data)
        self.list.sort(key=lambda x: x[0],reverse=True)    
        return self.list

if __name__ == "__main__":
    time_start=time.time()
    l=Lottery_multi(number=10,max_workers=5)
    l.data_multi()
    data=l.get_list()
    data.sort(key=lambda x: x[0],reverse=True)
    time_end=time.time()
    for i in range(len(data)):
        print(i+1,data[i])
    print('time',time_end-time_start)
