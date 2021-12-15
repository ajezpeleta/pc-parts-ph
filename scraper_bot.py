import csv
import json
import sys
import time
import logging

from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.support.ui import WebDriverWait


class UnsupportedVendorError(Exception):
    """
        Thrown when an unsupported vendor id is given.

        Contact the developer to request support for the vendor.
    """
    pass


def get_product_info(in_vendor_id, in_vendor_name, in_category_name, in_on_page_selector, io_prod_info_list):

    while True:

        products_on_page = wait.until(ec.presence_of_all_elements_located(
                                        (in_on_page_selector["type"], in_on_page_selector["productsOnPage"])))

        # For each product in products_on_page, create a dictionary of product info
        for product in products_on_page:
            # Initialize product_info with default values
            product_info = {
                "store": in_vendor_name,
                "category": in_category_name,
                "name": None,
                "price": None,
                "remarks": None,
                "available": None
            }

            # product_info = dict(zip(key_list, value_list)

            # DynaQuestPC data parsing
            if in_vendor_id == "dynaquestpc":

                product_info["name"] = product.find_element(in_on_page_selector["type"],
                                                            in_on_page_selector["productName"]).text.replace(
                    "\u2161", "II")

                _price = product.find_element(in_on_page_selector["type"], in_on_page_selector["productPrice"]).text
                if _price.lower() == "sold out":
                    product_info["price"] = "N/A"
                    product_info["available"] = False
                else:
                    _price = _price.replace("\u20b1", "").replace(",", "").strip()
                    product_info["price"] = f'{float(_price):.2f}'
                    product_info["available"] = True

                # PRODUCT REMARKS

            # EasyPC data parsing
            elif in_vendor_id == "easypc":

                # _json = json.loads(product.find_element(locs["type"], locs["productJSON"]).get_attribute("innerHTML"))
                _json = json.loads(product.get_attribute("innerHTML"))

                product_info["name"] = _json["title"]
                product_info["price"] = f'{float(_json["price_min"]/100):.2f}'
                product_info["available"] = _json["available"]

            # PCHub data parsing
            elif in_vendor_id == "pchub":

                # Click product WebElement to open more info about the product
                _prod = wait.until(ec.visibility_of(product))
                driver.execute_script("arguments[0].click();", _prod)

                product_info["name"] = product.find_element(in_on_page_selector["type"],
                                                            in_on_page_selector["productName"]).text.replace(
                    "\u2161", "II")

                _price = product.find_element(in_on_page_selector["type"], in_on_page_selector["productPrice"]).text
                _price = _price.replace("\u20b1", "").replace(",", "").strip()
                product_info["price"] = f'{float(_price):.2f}'

                ok_status_list = ["in stock", "few remaining"]
                _available = driver.find_element(
                    locate_with(in_on_page_selector["type"],
                                in_on_page_selector["productAvailable"]).below(product)).text
                if any(status in _available.lower() for status in ok_status_list):
                    product_info["available"] = True
                else:
                    product_info["available"] = False

            else:
                raise UnsupportedVendorError(f'Unsupported vendor id "{in_vendor_id}"')

            # Append the current product_info dictionary to prod_info_list
            io_prod_info_list.append(product_info)

        # Locate the next page button element and click it...
        # to continue scraping the remaining products in the current Category
        try:
            next_page = driver.find_element(in_on_page_selector["type"], in_on_page_selector["nextPage"])
            if next_page.get_attribute("class") != "disabled":
                driver.execute_script("arguments[0].click();", next_page)
            else:
                raise NoSuchElementException
        # If no such element was found, break away from the loop;
        # All products from the current Category have been scraped.
        except NoSuchElementException:
            # Log to console "No more products left in Category"
            break


def refresh_scroll_top(_driver):
    _driver.refresh()
    _driver.execute_script("window.scrollTo(0, 0);")


start_time = time.perf_counter()

# START --- Initialization of program variables from config file
try:
    with open("config-files/config.json", mode='r') as f:
        config = json.load(f)
        VENDOR_LIST = config["vendorList"]
        # PRODUCT_INFO_HEADERS = config["productInfoHeaders"]
        PRODUCT_INFO_HEADERS = ["store", "category", "name", "price", "remarks", "available"]
        PRODUCT_INFO_LIST = []
        TIMEOUT = config["timeout"] if isinstance(config["timeout"], (float, int)) else 10
except FileNotFoundError or PermissionError as e:
    # print("Error loading config file!")
    print(e)
    sys.exit()

# END --- Initialization of program variables from config file

# START --- Vendor List loop
for index, vendor in enumerate(VENDOR_LIST):

    # START --- Assigning and validation of data from VENDOR_LIST
    try:
        vendor_id = vendor["id"]
        vendor_name = vendor["name"]
        baseURL = vendor["baseURL"]
        product_category = vendor["productCategory"]
        on_page_selector = vendor["onPageSelector"]

        if not (all([vendor_id, vendor_name, baseURL, product_category, on_page_selector])):
            raise ValueError(f'vendorList[{index}] has 1 or more missing required values')
        elif type(vendor_id) is not str:
            raise TypeError(f'Expected a type `string` for vendorList[{index}]["id"]')
        elif type(vendor_name) is not str:
            raise TypeError(f'Expected a type `string` for vendorList[{index}]["name"]')
        elif type(baseURL) is not str:
            raise TypeError(f'Expected a type `string` for vendorList[{index}]["baseURL"]')
        elif type(product_category) is not dict:
            raise TypeError(f'Expected a type `object` for vendorList[{index}]["productCategory"]')
        elif type(on_page_selector) is not dict:
            raise TypeError(f'Expected a type `object` for vendorList[{index}]["onPageSelector"]')
    except KeyError as e:               # Skip current vendor if KeyError is caught
        e.msg = f'vendorList[{index}] has a missing or misspelled key'
        print(e.msg)
        continue
    except ValueError as e:             # Skip current vendor if ValueError is caught
        print(e.msg)
        continue
    except TypeError as e:              # Skip current vendor if TypeError is caught
        print(e.msg)
        continue
    # END --- Assigning and validation of data from VENDOR_LIST

    # START --- WebDriver execution
    with Chrome() as driver:

        wait = WebDriverWait(driver, TIMEOUT)     # Set explicit wait time for the WebDriver

        # START --- Loading the homepage of vendor; Connection testing
        try:
            driver.get(baseURL)
        except TimeoutException as e:
            e.msg = f'Timeout reached waiting for "{baseURL} to load'
            print(e.msg)
            continue
        except WebDriverException as e:
            e.msg = f'Cannot reach "{baseURL}" from id: {vendor_id}'
            print(e.msg)
            continue
        # END --- Loading the homepage of vendor; Connection testing

        # START --- Product Category loop
        for category_name, category_info in product_category.items():

            try:
                if category_info["type"] == "url":
                    if type(category_info["value"]) is str:
                        driver.get(category_info["value"])
                        get_product_info(vendor_id, vendor_name, category_name, on_page_selector, PRODUCT_INFO_LIST)
                    elif type(category_info["value"]) is list:
                        for _url in category_info["value"]:
                            driver.get(_url)
                            get_product_info(vendor_id, vendor_name, category_name, on_page_selector, PRODUCT_INFO_LIST)
                    else:
                        e_msg = f'Expected either type `string` or type `array` for ' \
                                  f'vendorList[{index}]["productCategory"]["{category_name}"]["value"]'
                        raise TypeError(e_msg)

                elif category_info["type"] == "css selector" or "xpath":
                    if type(category_info["value"]) is str:
                        refresh_scroll_top(driver)
                        wait.until(ec.presence_of_element_located(
                            (category_info["type"], category_info["value"]))).click()
                        get_product_info(vendor_id, vendor_name, category_name, on_page_selector, PRODUCT_INFO_LIST)
                    elif type(category_info["value"]) is list:
                        for _value in category_info["value"]:
                            refresh_scroll_top(driver)
                            wait.until(ec.presence_of_element_located((category_info["type"], _value))).click()
                            get_product_info(vendor_id, vendor_name, category_name, on_page_selector, PRODUCT_INFO_LIST)
                    else:
                        e_msg = f'Expected either type `string` or type `array` for ' \
                                  f'vendorList[{index}]["productCategory"]["{category_name}"]["value"]'
                        raise TypeError(e_msg)

                else:
                    e_msg = f'Expected a value of "url", "css selector", or "xpath" for ' \
                              f'vendorList[{index}]["productCategory"]["{category_name}"]["type"]'
                    raise ValueError(e_msg)

            except TypeError as e:
                print(e.msg)
                continue
            except ValueError as e:
                print(e.msg)
                continue
            except TimeoutException as e:
                e.msg = f'Timeout reached waiting for "{category_info["value"]} to load'
                print(e.msg)
                continue
            except WebDriverException as e:
                e.msg = f'Cannot reach "{category_info["value"]}" from id: {vendor_id}'
                print(e.msg)
                continue
            except UnsupportedVendorError as e:
                print(e)
                break
        # END --- Product Category loop

    # END --- WebDriver execution

# END --- Vendor List loop

# START --- Writing of scraped data to output file
with open("ProductInfo.csv", mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=PRODUCT_INFO_HEADERS)
    writer.writeheader()
    writer.writerows(PRODUCT_INFO_LIST)
# END --- Writing of scraped data to output file

end_time = time.perf_counter()
print(f"Execution time: {(end_time - start_time)/60:0.4f} min")
