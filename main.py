import time
import re
import os
import urllib2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.wait = WebDriverWait(driver, 10)
driver.get("https://www.linkedin.com/learning/login")

def get_link_list():
    chapters = driver.find_elements_by_css_selector("li.chapter-item")
    chapters_list = []
    driver.execute_script("document.querySelectorAll('.toc-item-meta').forEach((el) => {el.remove()});")
    driver.execute_script("document.querySelectorAll('.visually-hidden').forEach((el) => {el.remove()});")
    for chapter in chapters:
        chapter_content = []
        chapter_content.append(chapter.find_element_by_css_selector('.chapter-name').text)
        items = chapter.find_elements_by_css_selector('a.video-item')
        item_list = []
        link_index = 1
        for item in items:
            item_data = []
            item_data.append(item.find_element_by_css_selector('.toc-item-content').text);
            item_data.append(item.get_attribute('href'))
            chapter_title = re.sub(r"(:|\/)", " -", chapter_content[0])
            video_title = re.sub(r"(:)", " -", item_data[0])
            video_title = re.sub(r"(\/)", "|", video_title)
            video_name = str(link_index) + '. ' + video_title + '.mp4'
            video_path = chapter_title + '/' + video_name
            if os.path.exists(video_path):
                print("Skipping " + video_title + ' ...')
            else:
                item_list.append(item_data)
            link_index = link_index + 1
        chapter_content.append(item_list)
        chapters_list.append(chapter_content)
    return chapters_list

def dl_course():
    chapters = get_link_list()
    chapter_counter = 1
    for chapter in chapters:
        chapter_title = re.sub(r"(:|\/)", " -", chapter[0])
        if not os.path.exists(chapter_title):
            os.mkdir(chapter_title)
        os.chdir(chapter_title)
        link_index = 1
        print('  ' + chapter_title)
        for link in chapter[1]:
            driver.get(link[1])
            video = driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "video.player")))
            video_title = re.sub(r"(:)", " -", link[0])
            video_title = re.sub(r"(\/)", "|", video_title)
            video_src = video.get_attribute('src')
            video_name = str(link_index) + '. ' + video_title + '.mp4'
            if not os.path.exists(video_name):
                print('      ' + video_title)
                f = urllib2.urlopen(video_src)
                data = f.read()
                with open(video_name, "wb") as code:
                    code.write(data)
            else:
                print('Skipping ' + video_title)
            link_index = link_index + 1
        os.chdir('..')
        chapter_counter = chapter_counter + 1

def get_course(state):
    if state == "new":
        course_title = driver.find_element_by_css_selector(".banner-course-title").text
    elif state == "continue":
        course_title = driver.find_element_by_css_selector(".course-title").text
    root = re.sub(r"(:)", " -", course_title)
    root = re.sub(r"(\/)", "|", root)
    if not os.path.exists(root):
        os.mkdir(root)
    else:
        print(root + ' exists.')
    os.chdir(root)
    print('Downloading "' + course_title + '"...')
    dl_course()
    print("Download finished.\n")
    os.chdir('..')

def get_courses_from_file(file_name, state):
    with open(file_name) as f:
        links = f.readlines()
        for link in links:
            print(link)
            driver.get(link)
            time.sleep(10)
            get_course(state)
