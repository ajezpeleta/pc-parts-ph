import sys

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome

# this_dict = {
#     # "product_category": {
#     #     "processor": {
#     #         "type": "url",
#     #         "value": "kjk"
#     #     },
#     #     "motherboard": {
#     #         "type": "css selector",
#     #         "value": "#categoryCon option[value=\"Motherboard\"]"
#     #       },
#     #     "boi": None
#     # }
#     "a": [],
#     "b": "boi"
# }
#
# i = [1, 2, 3]
# j = {1: "hi"}
# k = None
#
# print(all([i, j, k]))

a = 1
if a == 2 or 1:
    print("hello")
else:
    print("oh no")

# with Chrome() as driver:
#     try:
#         # driver.get("https://djkfjadfj.com")
#         # raise WebDriverException("LMAO")
#         err_msg = f'boi boi boi boi ' \
#                   f'hello hello hello'
#         raise TypeError(err_msg)
#     except WebDriverException as e:
#         e.msg = e.msg + "\nCannot reach URL"
#         print(e.__dict__)
#         # driver.close()
#         sys.exit()
#     except TypeError as e:
#         print(e)


print("END")
#
#     for category_name, category_info in product_category.items():
#         if category_info["type"] == "url":
#             try:
#                 if type(category_info["value"]) is str:
#                     driver.get(category_info["value"])
#                 elif type(category_info["value"]) is list:
#                     for _url in category_info["value"]:
#                         driver.get(_url)
#             except WebDriverException as yo:
#                 print(yo)
#             else:
#                 continue
#         elif category_info["type"] == "css selector":
#             try:
#                 if type(category_info["value"]) is str:
#                     # driver.get(category_info["value"])
#                     print(category_info["value"])
#                 elif type(category_info["value"]) is list:
#                     for _url in category_info["value"]:
#                         # driver.get(_url)
#                         print(category_info["value"])
#             except WebDriverException as yo:
#                 print(yo)
#             else:
#                 raise TypeError
#         elif category_info["type"] == "xpath":
#             pass

