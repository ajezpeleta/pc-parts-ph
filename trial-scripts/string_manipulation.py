# home_url = 'https://dynaquestpc.com/'
# category_url = 'https://dynaquestpc.com/collections/processor'
#
# url_path = category_url.replace(home_url, "")
# print(url_path)
# var_str = '.pagination .next a[href*="{url_path}?page="]'
# locator = var_str.replace("{url_path}", url_path)
# print(locator)

# print("\u20b1")

value = '"Intel Core i9-12900K Processor 30M Cache, up to 5.20 GHz  (Must be purchased with compatible motherboard)"'
value = value.replace('"', "").split(">")[0].strip()
value = value.split("(m")[0].strip()
value = value.split("(M")[0].strip()
if value.endswith("."):
    value = value.replace(".", "").strip()
print(value.split("(M")[0].strip())

# root > div > div > div.appcontent.xcontainer > div > div.prodTablecon > div.col-xl-10 > div > div:nth-child(1) > div.xtable > div > table > tbody > tr:nth-child(1) > td:nth-child(4) > div > div > div.\36 .box.marginBox > div > div:nth-child(1) > span > span
