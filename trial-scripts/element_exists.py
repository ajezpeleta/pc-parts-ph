import json
import time

from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, \
    ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://easypc.com.ph/collections/processor-amd"
with Chrome() as driver:
    # driver.implicitly_wait(3)
    driver.get("https://easypc.com.ph/")
    driver.get(URL)

    product_names = []
    product_prices = []

    while True:
        print(driver.current_url)
        products_on_page = driver.find_elements("css selector", ".bc-sf-filter-product-item")
        # For each product in products_on_page, extract the name and price of the product...
        # ... and append those data to a list.
        # print(len(products_on_page))
        for product in products_on_page:
            product_json = product.find_element(By.CSS_SELECTOR, 'script[type="application/json"]')
            var = product_json.get_attribute("innerHTML")
            var_dict = json.loads(var)
            # print(type(var_dict))
            _name = var_dict["title"]
            _price = f"{float(var_dict['price_min'])/100:.2f}"
            _available = var_dict["available"]
            print(_name)
            # print(_name, _price, _available)
            # print(product_json)

            # _name = product.find_element("css selector", ".product-title").text
            # _price = product.find_element("css selector", ".product-price").text
            # product_names.append(_name)
            # product_prices.append(_price)
            # print(f"Product: {_name}\tPrice: {_price}")

        try:
            next_page = driver.find_element("css selector", '#bc-sf-filter-bottom-pagination li:last-child a')
            if not next_page.get_attribute("class") == "disabled":
                next_page.click()
                time.sleep(0.5)
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            print("no more link lmaoooo")
            break
        # finally:
        #     print("Time's up! Element was not clickable.")
        #     break
