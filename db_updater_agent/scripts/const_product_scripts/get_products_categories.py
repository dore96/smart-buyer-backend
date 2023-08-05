from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import time

# Function to get the category from the first item after search
def get_category_after_search(driver, item_code):
    # Navigate to the website
    driver.get('https://www.zapmarket.co.il/')

    # Find the search input element
    search_input = driver.find_element(By.CSS_SELECTOR, 'input[data-ng-model="searchBox.query"]')

    # Enter the item code into the search bar
    search_input.clear()
    search_input.send_keys(item_code)

    search_icon_element = driver.find_element(By.CLASS_NAME,'searchIcon')
    search_icon_element.click()

    # Click on the first product item after search
    first_product_name_link = driver.find_element(By.XPATH, '//div[@class="productItem"][1]//div[@class="productName"]/a')
    first_product_name_link.click()

    # Wait for the product page to load (add appropriate waiting time if needed)
    time.sleep(5)  # Adjust the waiting time as per the website's load time

    # Get the category from the product page
    category_element = driver.find_element(By.CSS_SELECTOR, '.breadcrumbs li:last-child a')
    category_text = category_element.text

    return category_text

# Load the JSON data from the file
with open(r'C:\Users\dored\Desktop\smart buyer backend\smart-buyer-backend\updated_products_with_images.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Create a Selenium WebDriver instance (you may need to download the appropriate driver for your browser)
driver = webdriver.Chrome()  # Change to appropriate driver if using a different browser

# Loop through the data and get the category for each item after searching
for item in data:
    item_code = item['item_code']
    item['category'] = get_category_after_search(driver, item_code)

# Close the Selenium driver
driver.quit()

# Save the updated data back to the JSON file
with open('your_json_file.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=2)
