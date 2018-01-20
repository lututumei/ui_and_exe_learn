from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import wx
from douban_filter_ui import *

driver = 0
filter_author_file = "douban_author_filter.txt"
saved_post_file = "E:/Download/python/script/filter_UI/douban_post.html"
author_list = []
filter_author_list = []
filter_author_set = []
save_post_num = 0
group_url = 0
page_num = 0
post_num = 0
comment_num = 0

def gather_author(dst_url):
    global driver
    driver.get(dst_url)
    #assert "上海租房@浦东租房小组" in driver.title 
    soup=BeautifulSoup(driver.page_source,'lxml')
    content = soup.select(".olt")[0]
    house_list = content.select("tbody > tr")
    for house in house_list:
        if(len(house.select(".title")) == 0):
            continue
        author = "".join(house.select("td")[1].stripped_strings)
        author_list.append(author)

def filter_author():
    author_set = set(author_list)
    sorted_author_list = {}
    for author in author_set:
        sorted_author_list[author] = author_list.count(author)
    for author in sorted_author_list:
        if sorted_author_list[author] > (post_num-1): #filter condition 1
            print(author, ":", sorted_author_list[author])
            filter_author_list.append(author)

def get_not_wanted_author_list():
    global filter_author_set
    for i in range(page_num):
        url = group_url + "discussion?start=" + str(i*25)
        print(url)
        gather_author(url)
    filter_author()

    with open(filter_author_file, "a+", encoding="utf-8") as f:
        for author in f:
            filter_author_list.append(author.strip())
        f.close()

    filter_author_set = set(filter_author_list)
    print(filter_author_set)
    print("get total filtered author: ", len(filter_author_set))

    f = open(filter_author_file, "w", encoding="utf-8")
    for author in filter_author_set:
        f.write(author)
        f.write('\n')
    f.close()

def save_post_info(href, title, author, post_save_file):
    print(title)
    post_save_file.write("<tr>")
    post_save_file.write("\n")
    post_save_file.write("<td>")
    post_save_file.write("\n")
    post_save_file.write("<a href=\"")
    post_save_file.write(href)
    post_save_file.write("\">")
    post_save_file.write(title)
    post_save_file.write("</a>")
    post_save_file.write("</td>")
    post_save_file.write("\n")
    post_save_file.write("<td>")
    post_save_file.write("\n")
    post_save_file.write(author)
    post_save_file.write("</td>")
    post_save_file.write("\n")
    post_save_file.write("</tr>")
    post_save_file.write("\n")

def get_wanted_post(dst_url, save_file):
    global driver, save_post_num, filter_author_set
    driver.get(dst_url)
    #assert "上海租房@浦东租房小组" in driver.title 
    soup=BeautifulSoup(driver.page_source,'lxml')
    content = soup.select(".olt")[0]
    house_list = content.select("tbody > tr")
    i = 0
    for house in house_list:
        if(len(house.select(".title")) == 0):
            continue
        href = house.select("td > a")[0]["href"]
        title = "".join(house.select("td")[0].stripped_strings)
        author = "".join(house.select("td")[1].stripped_strings)
        comments = "".join(house.select("td")[2].stripped_strings)
        time = "".join(house.select("td")[3].stripped_strings)
        if ((comments and int(comments) < comment_num) or not comments ) and author not in filter_author_set:
            save_post_info(href, title, author, save_file)
            save_post_num = save_post_num + 1

def get_douban_post(page):
    post_save_file = open(saved_post_file, "w", encoding="utf-8")
    post_save_file.write("<table>")
    for i in range(page):
        url = group_url + "discussion?start=" + str(i*25)
        get_wanted_post(url, post_save_file)
    post_save_file.write("</table>")
    post_save_file.close()

def load_filter_author():
    global filter_author_set
    author_list = []
    with open(filter_author_file, "a+", encoding="utf-8") as f:
        for author in f:
            author_list.append(author.strip())
            filter_author_set = set(author_list)
        f.close()    

def filter_douban_post():
    global filter_author_set, save_file_num, driver
    driver = webdriver.Chrome(executable_path="E:\Download\python\chromedriver_win32\chromedriver.exe")
    get_not_wanted_author_list()
    #load_filter_author()
    #print(filter_author_set)
    get_douban_post(page_num)
    print("共筛选出帖子：", save_post_num)
    driver.get("file:///" + saved_post_file)

class myFrame(filterFrame):
    def __init__(self, parent):
        filterFrame.__init__(self, parent)

    def filter_post( self, event ):
        global group_url, page_num, post_num, comment_num
        group_url = self.group_url.GetValue()
        page_num = int(self.page_num.GetValue())
        post_num = int(self.post_num.GetValue())
        comment_num = int(self.comment_num.GetValue())
        filter_douban_post()


if __name__ == "__main__":
    app = wx.App(False)
    frame = myFrame(None)
    frame.Show(True)
    app.MainLoop()