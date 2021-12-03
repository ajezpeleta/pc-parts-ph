# PC Parts PH
A python bot that scrapes product information of PC parts being sold in the Philippines.

## If you are cloning this repo:
- Put it in a venv and import selenium package

### Websites currently scraping from:
- https://dynaquestpc.com/
- https://easypc.com.ph/
- https://pchubpricelist.online/

### What-to-Do

- Have a config file of PC store websites.
- Have a config file for the PC parts categories.
    - Figure out the schema for PC parts categories.
- Retrieve and encode the products' information into a database.
- Figure out the schema for products' information

### Questions

- Use SQL for database? Maybe MongoDB? Time-series Database?
- Use JSON for product categories?
- Use JSON for product information?
    - How to consolidate information for the same product from the different websites?
    - Product names may be different among the websites.
- Make a Price History Graph?