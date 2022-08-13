from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
                                        ElementClickInterceptedException
import time
import csv
import os



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DRVR_FILE = os.path.join(BASE_DIR, 'geckodriver')

info_to_file = []

link = "https://www.detmir.ru/catalog/index/name/lego/"

PROXY = "127.0.0.1:9150"
proxy = Proxy({
 'proxyType': ProxyType.MANUAL,
 'httpProxy': PROXY,
 'ftpProxy': PROXY,
 'sslProxy': PROXY,
 'noProxy': ''
})

service = Service(DRVR_FILE)
browser = webdriver.Firefox(service=service, proxy=proxy)
time.sleep(5)


def city(browser, input_region: str) -> None:
    city_push = browser.find_element(By.CSS_SELECTOR, "li.sd:nth-child(1)")
    city_push.click()
    city_push = browser.find_elements(By.CLASS_NAME, "Hd")
    for index in range(50):
        if city_push[index].text == input_region:
            city_push[index].click()
            break


def parse_info(browser) -> None:
     region = browser.find_element(By.CLASS_NAME, "o_6").text
     browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
     time.sleep(3)
     browser.execute_script("window.scroll(0,0)", "")
     button_find = 1
     while button_find == 1:
         try:
             down = browser.find_element(By.CSS_SELECTOR, ".dp > div:nth-child(1) > button:nth-child(1)")
             y_offset = down.location['y']-50
             browser.execute_script("arguments[0].scrollIntoView();", down)
             browser.execute_script(f"window.scroll(0, {y_offset})", "")
             down.click()
             browser.execute_script("window.scroll(0,0)", "")
         except (NoSuchElementException, StaleElementReferenceException):
             button_find = 0

     browser.execute_script("window.scroll(0,0)", "")
     time.sleep(5)
     items = browser.find_elements(By.CLASS_NAME, "RS.Sj")
     try:
         for ind, item in enumerate(items):
             url = item.get_attribute("href")
             id_item = url.split("/")[-2]
             title = item.find_element(By.CLASS_NAME, 'RW').text
             try:
                 price = item.find_element(By.CLASS_NAME, "R_8").text
                 promo_price = item.find_element(By.CLASS_NAME, "R_6").text
             except NoSuchElementException:
                 # "Нет акции"
                 try:
                    price = item.find_element(By.CLASS_NAME, "R_6").text
                    promo_price = None
                 except NoSuchElementException:
                     # "Нет в наличии"
                     price = None
                     promo_price = None
             info = [id_item, title, price, region, promo_price, url]
             info_to_file.append(info)
     except Exception:
         pass


def create_file(info_to_file:list) -> None:
    with open("Detmir.csv", 'w', newline='', encoding='utf-8') as file:
        titles = ['id', 'title', 'price', 'city', 'promo_price', 'url']
        writer = csv.writer(file)
        writer.writerow(titles)
        writer.writerows(info_to_file)


def start(link):
    browser.get(link)
    time.sleep(1)
    try:
        city(browser, input_region="Санкт-Петербург и Ленинградская область")
    except ElementClickInterceptedException:
        city(browser, input_region="Санкт-Петербург и Ленинградская область")
    parse_info(browser)
    browser.get(link)
    time.sleep(1)
    try:
        city(browser, input_region="Москва и Московская область")
    except ElementClickInterceptedException:
        city(browser, input_region="Москва и Московская область")
    parse_info(browser)
    create_file(info_to_file=info_to_file)
    browser.quit()

start(link=link)