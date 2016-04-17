# coding=utf-8
import sys
from selenium import webdriver
from git import Repo
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import datetime

# Git 仓库路径
repo_dir = ""

# Git 仓库分支
repo_branch = "master"

# Git 仓库提交人邮箱
author_email = ""

# 口袋助理账号密码
kd77_username = ""
kd77_password = ""

# 请求超时时间
timeout = 10

# ChromeDriver path
# download: https://sites.google.com/a/chromium.org/chromedriver/downloads
chrome_driver_path = ""

# ---------------------

# 任务开始...
def get_report():

    if not repo_dir:
        print("未指定本地 Git 仓库路径.")
        return
    if not author_email:
        print("未指定 Git 提交人邮箱.")
        return

    #
    repo = Repo(repo_dir)

    today = datetime.datetime.today()
    today_commit_messages = []

    for commit in repo.iter_commits(repo_branch):
        if commit.author.email == author_email:
            commit_datetime = datetime.datetime.fromtimestamp(commit.committed_date)
            if commit_datetime.year == today.year and commit_datetime.month == today.month and commit_datetime.day == today.day:
                if len(commit.message.strip()) > 6: # 长度在6以下的提交文案不记录 exclude bugfix
                    today_commit_messages.append(commit.message.strip())

    # 输出今天的 Commit
    today_commit_messages_string = ""
    if today_commit_messages:
        for commit_message in today_commit_messages:
            today_commit_messages_string = today_commit_messages_string + ' - ' + commit_message + '\n'
        
        print("\n--- 今天提交的 Commit ---\n")
        print(today_commit_messages_string)
        print("\r")

        return today_commit_messages_string
    else:
        print("今天没有 Commit")
        return


def get_loaded_element(browser, xpath):
    WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
    print(xpath)
    return browser.find_element_by_xpath(xpath)

def write_daily_report(report_str):
    if chrome_driver_path:
        browser = webdriver.Chrome(executable_path = chrome_driver_path)
    else:
        browser = webdriver.Chrome()
    try:
        browser.set_window_size(1024, 800) # 屏幕太小，点不到写日志会报错！
        browser.set_window_size(2048, 800) # 屏幕太小，点不到写日志会报错！
        browser.set_window_position(-1000000, 1000000) # 干脆移动到屏幕的左下角好了
        print("begin")
        browser.get("https://web.kd77.cn/")
        print(browser.title)
        browser.find_element_by_id("ext-comp-1001-username").send_keys(kd77_username)
        browser.find_element_by_id("ext-comp-1001-pwd").send_keys(kd77_password)
        browser.find_element_by_id("ext-comp-1001-btn").click() # 登陆
        print("login")

        get_loaded_element(browser, "//li[@path='0-5']").click() # 工作汇报
        get_loaded_element(browser, "//li[@path='0-5-0']").click() # 我的工作汇报

        try:
            # 在点击写工作汇报之前，需要等待之前的日报加载完成
            # 但是如果是第一条工作汇报，则不存在当前 xpath，因此加入 try except，相当于 time.sleep(5)，且不放弃任务
            get_loaded_element(browser, "//div[contains(text(),'今日工作总结：')]") 
        except:
            pass

        get_loaded_element(browser, "//button[contains(text(),'写工作汇报')]").click() # 写工作汇报
        get_loaded_element(browser, "//span[contains(text(),'写日报')]").click() # 写日报

        get_loaded_element(browser, "//textarea[@name='今日工作总结']").send_keys(report_str)
        get_loaded_element(browser, "//textarea[@name='明日工作计划']").send_keys("-")
        get_loaded_element(browser, "//button[contains(text(),'确定')]").click()

        print("写完啦！")
    except Exception as ex:
        print(ex)
    finally:
        browser.quit()

if __name__ == '__main__':
    report_str = get_report()
    if report_str:
        write_daily_report(report_str)
