# import requests
# from bs4 import BeautifulSoup
# import csv
# import os
# from datetime import date
#
# URL = 'https://www.eldorado.ru/c/elektricheskie-plity'
# HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#            'AppleWebKit/537.36 (KHTML, like Gecko) '
#            'Chrome/96.0.4664.93 Safari/537.36', 'accept': '*/*'}
# HOST = 'https://www.eldorado.ru'
# FILE = 'propositions.csv'
# CURRENT_DATE = date.today()
#
#
# def get_html(url, params=None):
#     r = requests.get(url, headers=HEADERS, params=params)
#     return r
#
#
# def get_pages_count(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     pagination = soup.find_all('a', class_='button')
#     print(pagination)
#     # if pagination:
#     #     return int(pagination[-1].get_text())
#     # else:
#     #     return 1
#
#
# # def get_content(html):
# #     soup = BeautifulSoup(html, 'html.parser')
# #     items = soup.find_all()
# #
# #     propositions = []
# #     for item in items:
# #         name = item.find().get_text
# #         brand = item.find().get_text
# #         price = item.find().get_text
# #         link = HOST + item.find().get('href')
# #
# #         propositions.append({
# #             'name': name,
# #             'brand': brand,
# #             'price': price,
# #             'link': link,
# #         })
# #     return propositions
# #
# #
# def save_file(items, path):
#     with open(path, 'w', newline='') as file:
#         writer = csv.writer(file, delimiter=';')
#         writer.writerow([f'Название', f'Бренд', f'Цена на {CURRENT_DATE}', f'Ссылка'])
#         for item in items:
#             writer.writerow([item['name'], item['brand'], item['price'], item['link']])
#
#
# def parse():
#     # URL = input('Введите URL: ')
#     # URL = URL.strip()
#     html = get_html(URL)
#     if html.status_code == 200:
#         # propositions = []
#         pages_count = get_pages_count(html.text)
#         # for page in range(1, pages_count + 1):
#         #     print(f'Парсинг страницы {page} из {pages_count}...')
#         #     html = get_html(URL, params={'page': page})
#         #     propositions.extend(get_content(html.text))
#         # save_file(propositions, FILE)
#         # print(f'Найдено {len(propositions)} предложений')
#         # os.startfile(FILE)
#     else:
#         print('Error')
#
#
# parse()


from bs4 import BeautifulSoup
import requests
import time
import csv
import os
import re
from datetime import date


URL = 'https://www.eldorado.ru/c/elektricheskie-plity'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
           'AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/96.0.4664.93 Safari/537.36', 'accept': '*/*'}
HOST = 'https://www.eldorado.ru'
FILE = 'propositions.csv'
TEMP_FILE = 'tmp.csv'
URL_PATTERN = 'https://eldorado.ru/c/.*'
CURRENT_DATE = date.today().strftime("%d/%m/%Y")


def get_html(url, params=None):
    html = requests.get(url, headers=HEADERS, params=params)
    return html


def get_soup(url, headers):
    html_source = requests.get(url=url, headers=headers).text
    return BeautifulSoup(html_source, 'lxml')


def save_file(parsed_info):
    if not os.path.exists(FILE):
        with open(FILE, 'x') as new_file:
            new_file.close()

    if os.path.getsize(FILE) == 0:
        with open(FILE, 'w', newline='') as db_file:
            csv_writer = csv.writer(db_file, delimiter=';')
            header = 'Название', 'Ссылка', f'{date.today().strftime("%d/%m/%Y")}'
            csv_writer.writerow(header)
            for info in parsed_info:
                csv_writer.writerow([info['Name'], info['Url'], info['Price']])
    else:
        with open(FILE, 'r', newline='') as db_file, open(TEMP_FILE, 'w', newline='') as temp_file:
            csv_reader = csv.reader(db_file, delimiter=';')
            csv_writer = csv.writer(temp_file, delimiter=';')

            current_date = date.today().strftime("%d/%m/%Y")
            db_header = next(csv_reader)
            db_header.append(current_date)
            csv_writer.writerow(db_header)

            for row, info in zip(csv_reader, parsed_info):
                row.append(info['Price'])
                csv_writer.writerow(row)

            db_file.close()
            temp_file.close()
            os.remove(FILE)
            os.rename(TEMP_FILE, FILE)


def parse():
    print('Данная программа предназначена для парсинга сайта по продаже бытовой электорники "Эльдорадо". ', end='\n')
    print('Если Вы хотите получить информацию по перечню товаров из определенного раздела на данном сайте, ', end='')
    print('Вам просто следует ввести ссылку на данный раздел. ', end='\n')
    print('Например, если Вы хотите получить информацию по всем смартфонам,', end='')
    print('которые представлены на сайте "Эльдорадо", ', end='')
    print('Вам достаточно будет ввести https://www.eldorado.ru/c/smartfony/', end='\n')
    print('Учтите, что парсинг может занять некоторое время (иногда, довольно продолжительное)', end='\n\n')

    URL = input('Введите URL раздела с товарами, по которому Вы хотите получить информацию: ')
    while True:
        if not re.fullmatch(URL_PATTERN, URL):
            URL = input('Кажется, Вы ввели неправильную ссылку. Попробуйте еще раз: ')
        else:
            break

    html = get_html(URL)
    if html.status_code == 200:
        print('Подключение установлено! Начинаю парсинг...')

        current_page = 1
        parsed_info = []

        soup = get_soup(URL, HEADERS)

        pages = soup.find_all('a', attrs={'role': 'button', 'aria-label': re.compile("Page.*")})
        page_quantity = ''
        for page in pages:
            page_quantity = int(page.text)

        while current_page <= page_quantity:
            print(f'Подождите, обрабатываем страницу номер {current_page} из {page_quantity}...')

            names = soup.find_all('a', attrs={"class": "sG"}, href=True)
            prices = soup.find_all('span', attrs={"class": "XR"})

            for name, price in zip(names, prices):
                parsed_info.append({'Name': name.text, 'Url': HOST + name['href'], 'Price': price.text})

            # Getting next page in list
            next_button = soup.find(attrs={'class': 'next'})
            href = next_button.a.get('href')
            URL = HOST + href

            current_page += 1
            time.sleep(5)

        print(f'Найдено предложений: {len(parsed_info)}')
        save_file(parsed_info)
        os.startfile(FILE)
    else:
        print('Шаловливые бесы мешают Вашему подключению!')


parse()
