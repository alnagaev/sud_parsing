from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import csv
import os

from bs4 import BeautifulSoup, Tag, NavigableString
from itertools import cycle
from time import sleep

import pandas as pd
import requests

sud_url = 'https://sudact.ru/regular/doc/?regular-txt=&regular-case_doc=&regular-lawchunkinfo=%D0%A1%D1%82%D0%B0%D1%82%D1%8C%D1%8F+151.+%D0%9A%D0%BE%D0%BC%D0%BF%D0%B5%D0%BD%D1%81%D0%B0%D1%86%D0%B8%D1%8F+%D0%BC%D0%BE%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B3%D0%BE+%D0%B2%D1%80%D0%B5%D0%B4%D0%B0%28%D0%93%D0%9A+%D0%A0%D0%A4%29&regular-date_from=01.12.2018&regular-date_to=31.12.2018&regular-workflow_stage=10&regular-area=&regular-court=&regular-judge=#searchResult'


# wait = WebDriverWait(self.driver, 1000) - это про вермя на капчу

class Parser:
    """Набор методов и данных. Чтобы все было в одном месте. Но в одном месте не будет из-за асинхронки
    """
    proxy_list = ['http://sergeychuvakin1_mail:44f869ef05@2.56.114.95:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@5.182.118.50:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@5.182.118.225:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@5.182.118.25:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@5.182.118.134:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@5.182.119.98:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@45.90.199.163:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@45.90.198.88:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@45.90.198.180:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@45.90.198.158:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@45.90.199.240:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@45.91.11.10:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@45.91.11.220:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@45.91.11.191:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@45.91.10.187:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@45.91.10.200:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@2.56.114.17:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@2.56.114.151:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@2.56.115.17:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@2.56.115.167:30001',
                  'http://sergeychuvakin1_mail:44f869ef05@2.56.114.82:30001']

    """Тестовые ссылки для отладки прогаммы"""
    with open('test_links.txt', 'r') as file:
        test_links = file.read().strip().split(',')

    def __init__(self, link=None):
        self.driver = webdriver.Firefox(executable_path=r'C:\\Egor\\try\\geckodriver2.exe')
        # может быть поменяю на словарь, но 3 списка не так уж много, чтобы запариваться
        self.names = []
        self.links = []
        self.text = []
        self.counter = 1

    def login(self):
        self.driver.get('https://sudact.ru')
        sleep(1)
        auth = self.driver.find_element_by_id('auth_block_intro')
        auth.click()
        self.driver.find_element_by_id('id_username').send_keys('e.tokalova@mail.ru')
        self.driver.find_element_by_id('id_password').send_keys('test_password')
        self.driver.find_element_by_class_name('f-submit').click()
        print('Log in complete')
        return self.driver.get_cookies()

    def _backup_counter(self):
        return len([i for i in os.listdir() if i.startswith('backups_')])


    def get_data(self, link, full=True):
        print('Сбор ссылок запущен')
        self.driver.get(link)
        sleep(1)
        a = self.driver.find_elements_by_class_name("results")
        if not a:
            wait = WebDriverWait(self.driver, 1000)
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'results')))
            sleep(1)
            a = self.driver.find_elements_by_class_name("results")
        try:
            a = [i.find_elements_by_tag_name('a') for i in a][0]
            self.names = [i.text for i in a]
            self.links = [i.get_attribute('href') for i in a]

        except IndexError as ie:
            print(self.driver.page_source)

        # get all pages
        while full:
            sleep(1)
            try:
                path = '/html/body/div[1]/div[6]/div/div[2]/div[3]/div/span[2]/a'
                next_page = self.driver.find_element_by_xpath(path)
                if not next_page:
                    wait = WebDriverWait(self.driver, 1000)
                    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'results')))
                    sleep(1)
                    next_page = self.driver.find_element_by_xpath(path)
                next_page.click()
            except Exception as e:
                print(e)
                break

            a = self.driver.find_elements_by_class_name("results")
            a = [i.find_elements_by_tag_name('a') for i in a][0]
            self.names.extend([i.text for i in a])
            self.links.extend([i.get_attribute('href') for i in a])

        print('Сбор ссылок завершен')

    def txt_backup(self, data):
        dir_name = self.dir_name
        with open('./{}/{}.txt'.format(dir_name, self.counter), 'w') as file:
            file.write(data)
        self.counter += 1

    def sel_text(self, url, csv_backup=False, txt_backup=False):
        self.driver.get(url)
        source = BeautifulSoup(self.driver.page_source, "lxml")
        try:
            target = source.select('.h-col1.h-col1-inner3')[0]
            if csv_backup:
                with open('backup_result.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=' ',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow((url, target.text))
            if txt_backup:
                self.txt_backup(target.text)
            return url, target.text
        except Exception as e:
            print('Капча/Защита документов\nпрокси заблокирован')
            print(e)
            wait = WebDriverWait(self.driver, 1000)
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'h-col1')))
            source = BeautifulSoup(self.driver.page_source, "lxml")
            target = source.select('.h-col1.h-col1-inner3')[0]
            if csv_backup:
                with open('backup_result.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=' ',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow((url, target.text))
            if txt_backup:
                self.txt_backup(target.text)
            return url, target.text
            # return None

    @staticmethod
    def text_parse(session, url):
        res = session.get(url)
        source = BeautifulSoup(res.text, "lxml")
        try:
            target = source.select('.h-col1.h-col1-inner3')[0]
            return url, target.text
        except Exception as e:
            print('Капча/Защита документов\nпрокси заблокирован')
            print(str(e))
            return None

    def session_get(self, url_list, cookies=None, limit=None, csv_backup=False, txt_backup=False):
        print('Сбор текста запущен')
        text_list = []
        url_list = url_list[:limit]
        length = len(url_list)
        if csv_backup:
            with open('backup_result.csv', 'w', newline='', encoding='utf-8') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=' ',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow(('url', 'target_text'))

        if txt_backup:
            self.dir_name = str(input('Введите название папки для бэкапа данных'))
            if self.dir_name not in os.listdir():
                os.mkdir(self.dir_name)

        if cookies:
            s = grequests.Session()
            for cookie in cookies:
                s.cookies.set(cookie['name'], cookie['value'])

            for index, url in enumerate(url_list):
                text_list.append(self.text_parse(s, url))
                if index in [length // 4, length // 2, length * 3 // 4]:
                    print(index)
                sleep(1)

        else:
            for index, url in enumerate(url_list):
                try:
                    text_list.append(self.sel_text(url, csv_backup=csv_backup, txt_backup=txt_backup))
                except Exception:
                    text_list.append(self.sel_text(url, csv_backup=csv_backup, txt_backup=txt_backup))
                if index in [length // 4, length // 2, length * 3 // 4]:
                    print(index)
                sleep(0.5)

        print('Сбор текста звершен')
        return text_list

    @staticmethod
    def getFreeProxies():
        '''
        free proxies from https://free-proxy-list.net/ with all parameters. Function proxy list.
        '''
        r = requests.get('https://free-proxy-list.net/')  # , headers=header
        soup = BeautifulSoup(r.text, 'html.parser')
        t = soup.find_all('table', {'id': 'proxylisttable'})[0]
        tds = t.select('td')
        result = ['http://{}:{}'.format(x.text, y.text) for x, y in zip(tds[0::8], tds[1::8])]
        return result

    def close_driver(self):
        self.driver.close()

    def createDf(self, count=None):
        if count:
            return pd.DataFrame({'names': self.names[:count], 'links': self.links[:count]})
        return pd.DataFrame({'names': self.names, 'links': self.links})

    """Асинхронка не очень дружит с классами, поэтому дальше обойдемся без него"""


def create_cycle(array):
    """Корутина/генератор для карусели прокси"""
    proxy_pool = cycle(array)
    for i in proxy_pool:
        yield i


def main(full=True, limit=None, csv_backup=True, txt_backup=True):
    a = Parser()
    try:
        a.get_data(sud_url, full=full)
        # cookies = a.login()
        text = a.session_get(a.links, limit=limit, csv_backup=csv_backup, txt_backup=txt_backup)  # limit
        name_links = a.createDf(count=limit)  # count
        html_links = pd.DataFrame(text, columns=['links', 'html'])
        name_links['id'] = [i.split('doc/')[1].split('/?')[0] for i in name_links['links']]
        html_links['id'] = [i.split('doc/')[1].split('/?')[0] for i in html_links['links']]
        result = name_links.merge(html_links, on='id', how='inner')  # джоиним датафреймы в итоговый результат
        result = result[['names', 'links_y', 'html']]
        return result
    except Exception as e:
        print(str(e))
        print('Если у вас вылез index error - попробуйте запустить скрипт ещё раз, иногда селениум глючит и не '
              'находит нужные данные с первой попытки')

    finally:
        a.close_driver()


if __name__ == '__main__':
    result = main(full=True, limit=None, csv_backup=True, txt_backup=False)  # настраиваем параметры тут
    print(result)  # закоментить, если режим full


    def write_xlsx(debug=True):
        if debug:
            filename = 'results'
        else:
            filename = ''.join(e for e in str(input('Введите название файла: ')) if e.isalnum())
        writer = pd.ExcelWriter('{}.xlsx'.format(filename), engine='xlsxwriter', options={'strings_to_urls': False})
        result.to_excel(writer, index=False)
        writer.close()
        print('Файл записан')


    write_xlsx(debug=True)  # если здесь вбить False, то можно вводить название итоговому эксел файлу
