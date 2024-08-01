import csv
import requests
from bs4 import BeautifulSoup
import re


def decrypt_text_file(file_path, delimiter='\n'):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        elements = text.split(delimiter)
        elements = [element.strip() for element in elements if element.strip()]
        return elements
    except FileNotFoundError:
        print(f'Файл {file_path} не найден.')
        return None
    except Exception as e:
        print(f'Произошла ошибка при чтении файла: {e}')
        return None

def create_link_list_from_csv(csv_file):
    link_list = []
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    link_list.append(row[0].strip())
        return link_list
    except FileNotFoundError:
        print(f'Файл {csv_file} не найден.')
        return None
    except Exception as e:
        print(f'Произошла ошибка при чтении файла: {e}')
        return None


def write_string_to_txt(file_path, words_string):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(words_string)
        print(f"Строка успешно записана в файл {file_path}")
    except Exception as e:
        print(f"Произошла ошибка при записи в файл: {e}")


def find_phone_number(link, flag, key):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")
        phones_list = []
        if "https://" or "http://" not in link:
            link = "https://" + link
        for keyword in key:
            tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
            if flag and find_word_near_phone(soup, keyword):
                print(f"Ключевое слово '{keyword}' найдено рядом с номером телефона на странице: {link}")
                phone_number = tel_links[0].text.strip()
                if phone_number not in phones_list:
                    phones_list.append(phone_number)
                    save_to_csv(link, phone_number)
                    break
            if not flag:
                print(f"Ключевое слово '{keyword}' найдено рядом с номером телефона на странице: {link}")
                phone_number = tel_links[0].text.strip()
                if phone_number not in phones_list:
                    phones_list.append(phone_number)
                    save_to_csv(link, phone_number)
                    break

    except Exception as e:
        print(f"Ошибка при парсинге сайта {link}: {e}")


def save_to_csv(site, number):
    try:
        with open('phones.csv', 'a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([site, number])
    except Exception as e:
        print(f"Ошибка при сохранении данных в CSV файл: {e}")

tel_regex = re.compile(r'^tel:')


def find_word_near_phone(soup, word):
    word_regex = re.compile(r'\b{}\b'.format(re.escape(word)), re.IGNORECASE)
    tel_links = soup.find_all('a', href=tel_regex)

    for tel_link in tel_links:
        parent = tel_link.find_parent()
        if parent:
            parent_text = parent.get_text()
            phone_position = parent_text.find(tel_link.get_text())
            if phone_position != -1:
                preceding_text = parent_text[:phone_position].strip()
                if word_regex.match(preceding_text):
                    return True
    return False
