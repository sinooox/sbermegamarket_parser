import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

baseURL = 'https://megamarket.ru'
target = input('target? ')
targetURL = baseURL + '/catalog/?q=' + target.replace(' ', '%20')

def get_source_html(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    
    try:
        driver.get(url=url)
        WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.TAG_NAME, "html")))
        with open('source-page.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

def get_items(file_path):
    with open(file_path, encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    items_divs = soup.find_all('div', attrs={'router-link-uri': True})

    items = {}
    for item in items_divs:
        item_block = item.find('div', class_='item-block')
        item_price_block = item_block.find('div', class_='inner catalog-item__prices-container')
        item_money = item_price_block.find('div', class_='item-money')
        item_price = item_money.find('div', class_='item-price')
        item_price_result = item_price.find('span').get_text()
        
        item_bonus = item_money.find('div', class_='item-bonus')
        if isinstance(item_bonus, bs4.element.Tag):
            item_bonus_percent = item_bonus.find('span', class_='bonus-percent').get_text()
            item_bonus_amount = item_bonus.find('span', class_='bonus-amount').get_text()
        else:
            continue

        bonus = int(item_bonus_amount.replace(' ', ''))
        price = int(item_price_result[0:-1].replace(' ', ''))
        k = price / bonus
        item_url = item.get('router-link-uri')
        link = baseURL + item_url.replace(' ', '%20')
        items[k] = {'price': item_price_result[0:-2], 'bonus amount': item_bonus_amount, 'bonus percent': item_bonus_percent, 'link': link}

    items = dict(sorted(items.items(), key=lambda x: x[0]))
    for item in items:
        print(f'{item} - {items[item]}')

    return items

def main():
    get_source_html(url=targetURL)
    get_items(file_path='source-page.html')

if __name__ == '__main__':
    main()