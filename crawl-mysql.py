from config import blackboard_id, blackboard_pw, mysql_pw
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymysql

conn = pymysql.connect(host='localhost', user='root', password=mysql_pw(), db='bb', charset='utf8')
curs = conn.cursor()

announce_db = []
homework_db = []

sql = "select * from announcement"
curs.execute(sql)
rows = curs.fetchall()
for a in rows:
    announce_db.append(a[0])

sql = "select * from homework"
curs.execute(sql)
rows = curs.fetchall()
for h in rows:
    homework_db.append(h[0])

driver = webdriver.Chrome('/Users/TaeBbong/Projects/BlackBoard-Tutorial/chromedriver')
driver.implicitly_wait(3)
driver.get('https://kulms.korea.ac.kr')

driver.find_element_by_name('id').send_keys(blackboard_id())
driver.find_element_by_name('pw').send_keys(blackboard_pw())
driver.find_element_by_xpath('//*[@id="entry-login"]').click()

driver.get('https://kulms.korea.ac.kr/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_2_1')

try:
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "_22_1termCourses__62_1")))
finally:
    pass

html = driver.find_element_by_xpath('//*[@id="_22_1termCourses__62_1"]/ul').get_attribute('innerHTML')
soup = bs(html, 'html.parser')
course_list_raw = soup.find_all('a', href=True)
course_list = []
course_detail_base = 'https://kulms.korea.ac.kr/webapps/blackboard/execute/announcement?method=search&context=course_entry&course_id='
course_detail_list = []
for i in course_list_raw:
    course_each_id = str(i).split('id=')[1].split('&amp')[0]
    course_list.append(course_each_id)
    course_each_url = course_detail_base + course_each_id
    course_detail_list.append([course_each_url])

for i in course_detail_list:
    driver.get(i[0])
    try:
        # Page Load 기다리기
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "courseMenuPalette_contents")))

        # 공지 가져오기
        announce_raw = driver.page_source
        soup = bs(announce_raw, 'html.parser')
        announcements = soup.select('li.clearfix')[10:]
        announcements.reverse()
        for ann in announcements:
            print(ann.attrs['id'])
            print(ann.text)
            print('---------------')
            if ann.attrs['id'] not in announce_db:
                sql_ann = 'insert into announcement values(\"' + ann.attrs['id'] + '\")'
                curs.execute(sql_ann)
                conn.commit()

        # 과제란이 있으면 가져오기, 없으면 에러발생 -> except
        homework_html = driver.find_element_by_xpath('//*[@id="courseMenuPalette_contents"]').get_attribute('innerHTML')
        soup = bs(homework_html, 'html.parser')
        nav_bars = soup.find_all('a')
        for bar in nav_bars:
            if str(bar.find('span').text) == '과제' or str(bar.find('span').text) == 'Assignments':
                homework_url = 'https://kulms.korea.ac.kr' + str(bar['href'])
                i.append(homework_url)
                driver.get(homework_url)
                homework_raw = driver.page_source
                soup = bs(homework_raw, 'html.parser')
                homeworks = soup.select('ul.contentList > li')
                for home in homeworks:
                    print(home.attrs['id'])
                    print(home.text)
                    print('---------------')
                    if home.attrs['id'] not in homework_db:
                        sql_home = 'insert into homework values(\"' + home.attrs['id'] + '\")'
                        curs.execute(sql_home)
                        conn.commit()

    except Exception as e:
        homework_html = None
        print(e)
        pass
