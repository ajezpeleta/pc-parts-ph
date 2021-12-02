from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.relative_locator import locate_with
# from selenium.webdriver.common.by import By
import json
import time
import csv


def get_product_info(locs, store_id_, store_name_, prod_category, prod_info_list):

    # wait = WebDriverWait(driver, 5)

    while True:
        # Locate the product elements on the page
        # products_on_page = driver.find_elements(locs["type"], locs["productsOnPage"])
        products_on_page = wait.until(EC.presence_of_all_elements_located((locs["type"], locs["productsOnPage"])))

        # For each product in products_on_page, create a dictionary of product info
        for product in products_on_page:
            # Initialize product_info with default values
            product_info = {
                "store": store_name_,
                "category": prod_category,
                "name": None,
                "price": None,
                "available": None
            }

            # DynaQuestPC data parsing
            if store_id_ == "dynaquestpc":

                product_info["name"] = product.find_element(locs["type"], locs["productName"]).text
                # _name = _name.split(">")[0].strip()
                # _name = _name.split("(must")[0].strip()
                # _name = _name.split("(Must")[0].strip()
                # _name = _name.replace(",", "")
                # if _name.endswith("."):
                #     product_info["name"] = _name.replace(".", "").strip()
                # else:
                #     product_info["name"] = _name
                # print(product_info["name"])

                _price = product.find_element(locs["type"], locs["productPrice"]).text
                if _price.lower() == "sold out":
                    product_info["price"] = "N/A"
                    product_info["available"] = False
                else:
                    _price = _price.replace("\u20b1", "").replace(",", "").strip()
                    product_info["price"] = f'{float(_price):.2f}'
                    product_info["available"] = True

            # EasyPC data parsing
            elif store_id_ == "easypc":

                # _json = json.loads(product.find_element(locs["type"], locs["productJSON"]).get_attribute("innerHTML"))
                _json = json.loads(product.get_attribute("innerHTML"))

                product_info["name"] = _json["title"]
                product_info["price"] = f'{float(_json["price_min"]/100):.2f}'
                product_info["available"] = _json["available"]

            # PCHub data parsing
            elif store_id_ == "pchub":

                # Click product WebElement to open more info about the product
                _prod = wait.until(EC.visibility_of(product))
                driver.execute_script("arguments[0].click();", _prod)

                product_info["name"] = product.find_element(locs["type"], locs["productName"]).text

                _price = product.find_element(locs["type"], locs["productPrice"]).text
                _price = _price.replace("\u20b1", "").replace(",", "").strip()
                product_info["price"] = f'{float(_price):.2f}'

                ok_status_list = ["in stock", "few remaining"]
                _available = driver.find_element(locate_with(locs["type"],
                                                             locs["productAvailable"]).below(product)).text
                if any(status in _available.lower() for status in ok_status_list):
                    product_info["available"] = True
                else:
                    product_info["available"] = False

            # Append the current product_info dictionary to prod_info_list
            prod_info_list.append(product_info)

        # Locate the next page button element and click it...
        # to continue scraping the remaining products in the current Category
        try:
            next_page = driver.find_element(locs["type"], locs["nextPage"])
            if next_page.get_attribute("class") != "disabled":
                # next_page.click()
                # time.sleep(0.5)
                driver.execute_script("arguments[0].click();", next_page)
                # driver.execute_script("window.scrollTo(0, 0)")
            else:
                raise NoSuchElementException
        # If no such element was found, break away from the loop;
        # All products from the current Category have been scraped.
        except NoSuchElementException:
            # Log to console "No more products left in Category"
            break


def refresh_scroll_top(_driver):
    _driver.refresh()
    _driver.execute_script("window.scrollTo(0, 0)")


start_time = time.perf_counter()

# Load the StoreWebsiteConfig.json config file
with open("config-files/StoreWebsiteConfig.json", mode='r') as f:
    store_website = json.load(f)

# Load the ProductInfoTemplate.json config file, then
# Write the keys into a list
with open("config-files/ProductInfoTemplate.json", mode='r') as f:
    _template = json.load(f)
    product_info_headers = _template.keys()

# product_info_list will contain the product_info dicts from get_product_info();
# It will also be used to write to a CSV file
product_info_list = []

# Iterate through the list of store websites
for store_id, store_info in store_website.items():
    store_name = store_info["name"]
    urls = store_info["urls"]
    product_category_list = urls.keys()
    locators = store_info["locators"]

    # if store_id in ["pchub"]:   # Test PCHub for now...
    with Chrome() as driver:
        wait = WebDriverWait(driver, 5)
        home_url = urls["home"]
        # driver.maximize_window()
        driver.get(home_url)
        # Add ExpectedCondition waiting for homepage to load
        time.sleep(3)   # Using sleep() for now...

        for product_category in product_category_list:
            # Skip the home URL
            # if product_category in ["home", "processor", "motherboard", "gpu", "ram", "psu"]:
            if product_category in ["home"]:
                continue

            # If no Category URL given, use the locator for WebDriver click() activity
            if urls[product_category] is None:
                if type(locators[product_category]) is list:
                    for category_locator in locators[product_category]:
                        refresh_scroll_top(driver)
                        wait.until(EC.presence_of_element_located((locators["type"], category_locator))).click()
                        get_product_info(locators, store_id, store_name, product_category, product_info_list)
                else:
                    refresh_scroll_top(driver)
                    wait.until(EC.presence_of_element_located((locators["type"],
                                                               locators[product_category]))).click()
                    get_product_info(locators, store_id, store_name, product_category, product_info_list)

            elif urls[product_category]:
                # If a list of URLs for a Category was given, iterate through the list
                if type(urls[product_category]) is list:
                    for category_url in urls[product_category]:
                        driver.get(category_url)
                        get_product_info(locators, store_id, store_name, product_category, product_info_list)
                # Else, just go to the given Category URL
                else:
                    driver.get(urls[product_category])
                    get_product_info(locators, store_id, store_name, product_category, product_info_list)
            else:
                break

# Write the extracted data to a CSV file
with open("ProductInfo.csv", mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=product_info_headers)
    writer.writeheader()
    writer.writerows(product_info_list)

end_time = time.perf_counter()
print(f"Execution time: {(end_time - start_time)/60:0.4f} min")
