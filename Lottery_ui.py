# -*- coding: utf-8 -*-
"""
@auther unknowcry
@date 2020-4-18
@desc 简单的彩票分析及ui
@filename Lottery_ui.py

"""

import os
import sys
import datetime
import tkinter as tk
import tkinter.messagebox
import matplotlib
import matplotlib.pyplot as plt
import configparser
from tkinter import ttk
from Lottery_data import Lottery
from Lottery_data import Lottery_multi
from matplotlib.pyplot import MultipleLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk

class window():
    """
    界面设计
    """
    root=None
    menubar=None
    filemenu=None
    windowmenu=None
    statusbar=None
    tabbar=None
    tab_new=None
    tab_history=None
    canvas_number=None
    canvas_position=None

    data=None
    data_no=0
    data_number=0
    data_date_start=0
    data_date_end=0
    data_sale=0
    data_jackpot=0
    data_query_no=0
    data_query_number=0
    data_query_date_start=0
    data_query_date_end=0
    data_query_sale=0
    data_query_jackpot=0
    data_newno=0

    myfont='Arial'

    def __init__(self):
        """
        切换工作目录为文件目录
        获取最新数据
        加载组件
        """
        path=os.path.realpath(__file__)
        dirpath=os.path.dirname(path)
        os.chdir(dirpath)
        self.get_data_new()
        self.set_root()
        self.set_statusbar()
        self.update_statusbar('准备中…')
        self.set_menubar()
        self.set_notebookbar()
        self.update_statusbar()

    #主窗口    
    def set_root(self):
        self.root=tk.Tk()
        self.root.title('超级大乐透')
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        try:
            config=configparser.ConfigParser()
            config.read("Lottery_ui.conf")
            # with open("Lottery_ui.conf", "r") as conf:
                # alignstr=conf.read()
            alignstr=config.get('window','geometry')
            self.root.geometry(alignstr)
            print(alignstr)
        except Exception as err:
            print(err)
            self.reset_root_geometry()
        self.root.resizable(width=True,height=True)
        self.root.protocol('WM_DELETE_WINDOW',self.quit)

    '''控件'''
    #菜单栏
    def set_menubar(self):
        self.menubar=tk.Menu(self.root)
        self.set_filemenu()
        self.set_windowmenu()
        self.root.config(menu=self.menubar)

    #文件项
    def set_filemenu(self):
        self.filemenu=tk.Menu(self.menubar)
        self.save=tk.Menu(self.filemenu)
        self.save.add_command(label='按数分析',font=self.myfont,command=self.save_number)
        self.save.add_command(label='按位分析',font=self.myfont,command=self.save_position)
        self.filemenu.add_cascade(label='图片另存为',font=self.myfont,menu=self.save)
        self.filemenu.add_command(label='退出',font=self.myfont,command=self.quit)
        self.menubar.add_cascade(label='文件',font=self.myfont,menu=self.filemenu)

    #窗口项
    def set_windowmenu(self):    
        self.windowmenu=tk.Menu(self.menubar)
        self.windowmenu.add_command(label='重置',font=self.myfont,command=self.reset_root_geometry)
        self.menubar.add_cascade(label='窗口',font=self.myfont,menu=self.windowmenu)

    #状态栏
    def set_statusbar(self):
        self.statusbar=tk.Label(self.root,text='状态',font=self.myfont,bd=1,relief=tk.SUNKEN,anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM,fill=tk.X)

    #标签页
    def set_notebookbar(self):
        self.tab=ttk.Notebook(self.root)
        self.set_tab_new()
        self.set_tab_history()
        self.set_tab_number()
        self.set_tab_position()
        self.tab.pack(expand=True,fill='both')
        self.tab.select(self.tab_new)

    #标签页-最新数据
    def set_tab_new(self):
        self.tab_new=tk.Frame(self.tab,bg='blue')
        self.tab.add(self.tab_new,text='现在')
        self.fill_tab_new()

    #标签页-历史数据查询
    def set_tab_history(self):
        self.tab_history=tk.Frame(self.tab,bg='red')
        self.tab.add(self.tab_history,text='历史')
        self.fill_tab_history()

    #标签页-按数分析
    def set_tab_number(self):
        self.tab_number=tk.Frame(self.tab)
        self.tab.add(self.tab_number,text='按数分析')
        self.fill_tab_number()

    #标签页-按位分析
    def set_tab_position(self):
        self.tab_position=tk.Frame(self.tab)
        self.tab.add(self.tab_position,text='按位分析')
        self.fill_tab_position()

    #小部件
    #填充最新页
    def fill_tab_new(self):
        self.tab_new_no=tk.Label(self.tab_new,text='第'+str(self.data_no)+'期',bg='orange',font=(self.myfont, 14))
        self.tab_new_no.pack(side='top',fill='x')
        if type(self.data_number)==tuple:
            self.tab_new_number=tk.Label(self.tab_new,text='开奖号码'+'{0}-{1}-{2}-{3}-{4}-{5}-{6}'.format(self.data_tmp_number[0], \
                self.data_tmp_number[1],self.data_tmp_number[2],self.data_tmp_number[3],self.data_tmp_number[4], \
                self.data_tmp_number[5],self.data_tmp_number[6]),bg='pink',font=(self.myfont, 14))
        else:
            tkinter.messagebox.showerror('error','数据错误')
            self.tab_new_number=tk.Label(self.tab_new,text='开奖号码'+str(self.data_number),bg='pink',font=(self.myfont, 14))
        self.tab_new_number.pack(side='top',fill='x')
        self.tab_new_date_start=tk.Label(self.tab_new,text='开奖日期'+str(self.data_date_start),bg='pink',font=(self.myfont, 14))
        self.tab_new_date_start.pack(side='top',fill='x')
        self.tab_new_date_end=tk.Label(self.tab_new,text='兑奖截止'+str(self.data_date_end),bg='pink',font=(self.myfont, 14))
        self.tab_new_date_end.pack(side='top',fill='x')
        self.tab_new_sale=tk.Label(self.tab_new,text='销售金额'+str(self.data_sale)+'亿',bg='pink',font=(self.myfont, 14))
        self.tab_new_sale.pack(side='top',fill='x')
        self.tab_new_jackpot=tk.Label(self.tab_new,text='奖池滚存'+str(self.data_jackpot)+'亿',bg='pink',font=(self.myfont, 14))
        self.tab_new_jackpot.pack(side='top',fill='x')

    #填充历史页
    def fill_tab_history(self):
        self.tab_history_query=tk.Frame(self.tab_history,bg='blue')
        self.tab_history_query.pack(side='top',fill='x')
        self.tab_history_label=tk.Label(self.tab_history_query,text='输入期号',bd=1,font=self.myfont)
        self.tab_history_label.pack(side='left')
        self.tab_history_btn=tk.Button(self.tab_history_query,text='搜索',bd=1,font=self.myfont,command=lambda :self.tab_history_search(self.tab_history_entry.get()))
        self.tab_history_btn.pack(side='right')
        self.tab_history_entry=tk.Entry(self.tab_history_query,bd=3,font=self.myfont)
        self.tab_history_entry.pack(side='left',fill='x')
        self.tab_history_frame=tk.Frame(self.tab_history,bg='pink')
        self.tab_history_frame.pack(side='top',fill='x')
        self.tab_history_no=tk.Label(self.tab_history_frame,text='第'+str(self.data_query_no)+'期',bg='orange',font=(self.myfont, 14))
        self.tab_history_no.pack(side='top',fill='x')
        self.tab_history_number=tk.Label(self.tab_history_frame,text='开奖号码'+str(self.data_query_number),bg='pink',font=(self.myfont, 14))
        self.tab_history_number.pack(side='top',fill='x')
        self.tab_history_date_start=tk.Label(self.tab_history_frame,text='开奖日期'+str(self.data_query_date_start),bg='pink',font=(self.myfont, 14))
        self.tab_history_date_start.pack(side='top',fill='x')
        self.tab_history_date_end=tk.Label(self.tab_history_frame,text='兑奖截止'+str(self.data_query_date_end),bg='pink',font=(self.myfont, 14))
        self.tab_history_date_end.pack(side='top',fill='x')
        self.tab_history_sale=tk.Label(self.tab_history_frame,text='销售金额'+str(self.data_query_sale)+'亿',bg='pink',font=(self.myfont, 14))
        self.tab_history_sale.pack(side='top',fill='x')
        self.tab_history_jackpot=tk.Label(self.tab_history_frame,text='奖池滚存'+str(self.data_query_jackpot)+'亿',bg='pink',font=(self.myfont, 14))
        self.tab_history_jackpot.pack(side='top',fill='x')

    #填充按数分析
    def fill_tab_number(self):
        self.tab_number_query=tk.Frame(self.tab_number,bg='blue')
        self.tab_number_query.pack(side='top',fill='x')
        self.tab_number_label=tk.Label(self.tab_number_query,text='最近',bd=1,font=self.myfont)
        self.tab_number_label.pack(side='left')
        self.tab_number_btn=tk.Button(self.tab_number_query,text='生成',bd=1,font=self.myfont,command=self.tab_number_search)
        self.tab_number_btn.pack(side='right')
        self.tab_number_entry=tk.Entry(self.tab_number_query,bd=3,font=self.myfont)
        self.tab_number_entry.pack(side='left',fill='x')
        self.tab_number_label2=tk.Label(self.tab_number_query,text='期',bd=1,font=self.myfont)
        self.tab_number_label2.pack(side='left')
        self.tab_number_frame=tk.Frame(self.tab_number,bg='pink')
        self.tab_number_frame.pack(side='top',fill='both')

    #填充按位分析
    def fill_tab_position(self):
        self.tab_position_query=tk.Frame(self.tab_position,bg='blue')
        self.tab_position_query.pack(side='top',fill='x')
        self.tab_position_label=tk.Label(self.tab_position_query,text='最近',bd=1,font=self.myfont)
        self.tab_position_label.pack(side='left')
        self.tab_position_btn=tk.Button(self.tab_position_query,text='生成',bd=1,font=self.myfont,command=self.tab_position_search)
        self.tab_position_btn.pack(side='right')
        self.tab_position_entry=tk.Entry(self.tab_position_query,bd=3,font=self.myfont)
        self.tab_position_entry.pack(side='left',fill='x')
        self.tab_position_label=tk.Label(self.tab_position_query,text='期',bd=1,font=self.myfont)
        self.tab_position_label.pack(side='left')
        self.tab_position_frame=tk.Frame(self.tab_position,bg='pink')
        self.tab_position_frame.pack(side='top',fill='both')

    '''事件'''

    #重置窗口大小和位置
    def reset_root_geometry(self):
        width=380
        height=300
        screenwidth=self.root.winfo_screenwidth()
        screenheight=self.root.winfo_screenheight()
        alignstr='{}x{}+{}+{}'.format(width,height,int((screenwidth-width)/2),int((screenheight-height)/2))
        self.root.geometry(alignstr)
        config=configparser.ConfigParser()
        config['window']={'geometry':'{}'.format(self.root.geometry())}
        with open("Lottery_ui.conf", "w") as conf:
            config.write(conf)

    #查询某期，并重新填充历史页
    def tab_history_search(self,no):
        self.update_statusbar('查询中…')
        if self.get_data_single(no):
            self.tab_history_no['text']='第'+'{:0^4}'.format(self.data_tmp_no)+'期'
            self.tab_history_number['text']='开奖号码'+'{0}-{1}-{2}-{3}-{4}-{5}-{6}'.format(self.data_tmp_number[0],self.data_tmp_number[1], \
                self.data_tmp_number[2],self.data_tmp_number[3],self.data_tmp_number[4],self.data_tmp_number[5],self.data_tmp_number[6])
            self.tab_history_date_start['text']='开奖日期'+'{}'.format(self.data_tmp_date_start)
            self.tab_history_date_end['text']='兑奖截止'+'{}'.format(self.data_tmp_date_end)
            self.tab_history_sale['text']='销售金额'+'{}'.format(self.data_tmp_sale)+'亿'
            self.tab_history_jackpot['text']='奖池滚存'+'{}'.format(self.data_tmp_jackpot)+'亿'
            self.update_statusbar()
        else:
            tkinter.messagebox.showerror('error','数据错误')    
            self.update_statusbar('就绪')

    #生成按数分析的图形
    def tab_number_search(self):
        self.update_statusbar('生成中…')
        self.tab_number_frame.destroy()
        self.tab_number_frame=tk.Frame(self.tab_number,bg='pink')
        self.tab_number_frame.pack(side='top',fill='both')
        no_number=str(self.tab_number_entry.get()) 
        if no_number.isdigit():
            nums=self.get_number_rate(int(no_number))
            self.draw_number_rate(nums)
            self.update_statusbar()
        else:
            tkinter.messagebox.showerror('error','输入数字')
            self.update_statusbar('就绪')

    #生成按位分析的图形
    def tab_position_search(self):
        self.update_statusbar('生成中…')
        self.tab_position_frame.destroy()
        self.tab_position_frame=tk.Frame(self.tab_position,bg='pink')
        self.tab_position_frame.pack(side='top',fill='both')
        pos=str(self.tab_position_entry.get())
        if pos.isdigit():
            nums=self.get_number_line(no_number=int(pos))
            self.draw_number_line(nums)
            self.update_statusbar()
        else:
            tkinter.messagebox.showerror('error','输入正确的期号')
            self.update_statusbar('就绪')

    #保存按数分析的图形
    def save_number(self):
        fname = tkinter.filedialog.asksaveasfilename(title=u'保存文件', filetypes=[("PNG", ".png")])
        if fname !=None and fname!='':
            filename, _ = os.path.splitext(fname)
            self.canvas_number.print_png('{}.png'.format(str(filename)))

    #保存按位分析的图形
    def save_position(self):
        fname = tkinter.filedialog.asksaveasfilename(title=u'保存文件', filetypes=[("PNG", ".png")])
        if fname !=None and fname!='':
            filename, _ = os.path.splitext(fname)
            self.canvas_position.print_png('{}.png'.format(str(filename)))
            
    #退出
    def quit(self):
        quit=tkinter.messagebox.askokcancel('tip','sure to exit?')
        if quit == True:
            self.update_statusbar('退出…')
            config=configparser.ConfigParser()
            config['window']={'geometry':'{}'.format(self.root.geometry())}
            with open("Lottery_ui.conf", "w") as conf:
                # conf.write(self.root.geometry())
                config.write(conf)
            self.root.destroy()
            sys.exit(0)

    '''操作'''
    #更新状态栏
    def update_statusbar(self,text='就绪'):
        self.statusbar['text']=str(text)
        self.statusbar.update()
        print(self.statusbar['text'])

    #数据
    #获取最新数据
    def get_data_new(self):
        """
        :return: bool
        """
        flag=self.get_data_newno()
        if flag:
            flag=self.get_data_single(no=self.data_newno)
            if flag:
                self.data_no=self.data_tmp_no
                self.data_number=self.data_tmp_number
                self.data_date_start=self.data_tmp_date_start
                self.data_date_end=self.data_tmp_date_end
                self.data_sale=self.data_tmp_sale
                self.data_jackpot=self.data_tmp_jackpot
                return True
            else:
                return False
        else:
            return False

    #获取指定某期数据
    def get_data_single(self,no):
        """
        :param no: 期号
        :return: bool
        """
        flag,lot=Lottery().data_single(no)
        if flag==False:
            return False
        self.data_tmp_no=lot[0]
        self.data_tmp_number=lot[1]
        self.data_tmp_date_start=lot[2]
        self.data_tmp_date_end=lot[3]
        self.data_tmp_sale=lot[4]
        self.data_tmp_jackpot=lot[5]
        if self.data_tmp_number!=None:
            return True
        else:
            return False

    #获取最新期号
    def get_data_newno(self):
        """
        :return: bool
        """
        flag,newno=Lottery().get_newno()
        if flag==False:
            return False
        else:
            self.data_newno=int(newno)
            return True

    #获取多期数据
    def get_data_multi(self,number):
        """
        :param number: 期数量
        :return: 开奖号码
        """
        lotm=Lottery_multi(number,max_workers=7)
        lotm.data_multi()
        datas=lotm.get_list()
        numbers=[]
        for data in datas:
            numbers.append(data[1])
        for number in numbers:
            print(number)
        return numbers

    #按频次分析号码
    def get_number_rate(self, no_number):
        """
        :param no_number: 期数量
        :return: 按顺序的号码频次
        """
        nums=[]
        for _ in range(35):
            nums.append(0)
        numbers=self.get_data_multi(no_number)
        for number in numbers:
            for i in number:
                nums[int(i)-1]=nums[int(i)-1]+1
        print(nums)
        return nums

    #按各个位置的号码分析
    def get_number_line(self,no_number):
        """
        :param no_number: 期数量
        :return: 各个位置的号码变化
        """
        nums=[[],[],[],[],[],[],[]]
        numbers=self.get_data_multi(no_number)
        for i in range(len(numbers)):
            for j in range(7):
                nums[j].append(int(numbers[i][j]))
        print(nums)
        return nums

    #图形
    #生成频次图
    def draw_number_rate(self,nums):
        """
        :param nums: 数据列表
        """
        self.figure_number=plt.figure()
        plt.barh(range(35),nums,height=0.8,color='steelblue',alpha=0.8)
        plt.yticks(range(35),list(range(1,36)))
        for x,y in enumerate(nums):
            plt.text(y,x,'{}'.format(y))
        # plt.show()
        self.canvas_number=FigureCanvasTkAgg(self.figure_number,self.tab_number_frame)
        self.canvas_number.draw()
        self.canvas_number.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)

    #生成折线图
    def draw_number_line(self,nums):
        """
        :param nums: 数据列表
        """
        self.figure_position=plt.figure()
        plt.plot(nums[0],label='1')
        plt.plot(nums[1],label='2')
        plt.plot(nums[2],label='3')
        plt.plot(nums[3],label='4')
        plt.plot(nums[4],label='5')
        plt.plot(nums[5],label='6')
        plt.plot(nums[6],label='7')
        plt.legend(loc='best')
        ax=plt.gca()
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.yaxis.set_major_locator(MultipleLocator(1))
        self.canvas_position=FigureCanvasTkAgg(self.figure_position,self.tab_position_frame)
        self.canvas_position.draw()
        self.canvas_position.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)


    '''外部调用'''
    #运行
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    w=window()
    w.run()
