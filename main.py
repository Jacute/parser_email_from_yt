from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import time
import os
import csv
import sys


# options
options = webdriver.ChromeOptions()

# user-agent
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0")

# disable webdriver mode

# # for older ChromeDriver under version 79.0.3945.16
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option("useAutomationExtension", False)

# for ChromeDriver version 79.0.3945.16 or over
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    executable_path=os.path.abspath('chromedriver'),
    options=options
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
urls = []
data_without_mail = []
data = []
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

try:
    try:
        count_subs = int(input('Введите от какого кол-ва подписчиков вы хотите парсить каналы: '))
    except Exception:
        print('Неверно введено кол-во подписчиков')
    with open('data.txt', mode='r') as f:
        file = f.read().split('\n')
    for i in file:
        if i != '':
            driver.get(f'https://www.youtube.com/results?search_query={i}&sp=EgIQAg%253D%253D')
            driver.implicitly_wait(10)
            while True:
                scroll_height = 2000
                document_height_before = driver.execute_script("return document.documentElement.scrollHeight")
                driver.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
                time.sleep(1.5)
                document_height_after = driver.execute_script("return document.documentElement.scrollHeight")
                if document_height_after == document_height_before:
                    break
            blocks = driver.find_elements_by_xpath('//*[@id="main-link"]')
            subs = driver.find_elements_by_id('subscribers')
            for block in range(len(blocks)):
                data_subs = subs[block].text.split()[:-1]
                if len(data_subs) == 1:
                    sub = float(data_subs[0].replace(',', '.'))
                elif len(data_subs) == 2:
                    if data_subs[1] == 'тыс.':
                        sub = float(data_subs[0].replace(',', '.')) * 1000
                    elif data_subs[1] == 'млн':
                        sub = float(data_subs[0].replace(',', '.')) * 1000000
                    if sub >= count_subs:
                        url = blocks[block].get_attribute('href')
                        data_without_mail.append((url, ' '.join(data_subs), i))
            time.sleep(1)
    for i in data_without_mail:
        driver.get(i[0])
        driver.implicitly_wait(10)
        email = 'Почта не найдена'
        try:
            about = driver.find_element_by_css_selector('paper-tab.style-scope:nth-child(12)')
            if about:
                about.click()
                description = driver.find_element_by_xpath('//yt-formatted-string[@id="description"]')
                if '@' in description.text:
                    email = description.text[:description.text.index('@')].split()[-1] + description.text[description.text.index('@'):].split()[0]
                    if (re.search(regex, email)):
                        pass
                    else:
                        email = 'Почта не найдена'
                time.sleep(1)
        except Exception:
            email = 'Почта не найдена'
        data.append((email, i[0], i[1], i[2]))
    with open('1.csv', mode='w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(('Почта', ''))
        for i in data:
            if i[0] != 'Почта не найдена':
                writer.writerow((i[0], ''))

    with open('2.csv', mode='w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(('Почта', 'Ссылка на канал', 'Подписчики', 'Ключевое слово'))
        for i in data:
            if i[0] != 'Почта не найдена':
                writer.writerow(i)
finally:
    driver.close()
    driver.quit()
