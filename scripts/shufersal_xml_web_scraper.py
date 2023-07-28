import os
import gzip
import shutil
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import requests

# URL of the website
url = "http://prices.shufersal.co.il/"

# Set up options for the Chrome webdriver (you can adjust these as needed)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)

# Initialize the Chrome webdriver
driver = webdriver.Chrome(options=chrome_options)

try:
    # Open the website in the browser
    driver.get(url)

    # Find the dropdown menu by its ID
    dropdown_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ddlCategory"))
    )

    # Create a Select object to interact with the dropdown
    dropdown = Select(dropdown_element)

    # Select the "PricesFull" option by its value (2)
    dropdown.select_by_value("2")

    # Wait for the page to load after selecting 'PricesFull'
    time.sleep(5)  # You can adjust the waiting time based on the page loading speed

    while True:
        # Find the table body (tbody) containing the rows
        table_body = driver.find_element(By.TAG_NAME, "tbody")

        # Find all the rows (tr) in the table body
        rows = table_body.find_elements(By.TAG_NAME, "tr")

        # Create a folder to save the downloaded files
        if not os.path.exists("C:\Users\dored\Desktop\smart-buyer-backend\shofersal_xml"):
            os.makedirs("C:\Users\dored\Desktop\smart-buyer-backend\shofersal_xml")

        # Iterate through each row and download the files
        for row in rows:
            # Find the first link (a tag) in the row
            link = row.find_element(By.TAG_NAME, "a")
            if link:
                download_url = link.get_attribute("href")
                if "PriceFull" in download_url:
                    file_name = download_url.split("/")[-1].split("?")[0]
                    file_path = os.path.join("C:\Users\dored\Desktop\smart-buyer-backend\shofersal_xml", file_name)

                    # Check if the file already exists in the "shofersal_xml" directory
                    if os.path.exists(file_path[:-3] + ".xml"):
                        # Delete the old file
                        os.remove(file_path[:-3] + ".xml")
                        print(f"Deleted old file: {file_path[:-3]}.xml")
                            
                    # Download the file using requests
                    file_response = requests.get(download_url)

                    # Save the .gz file to disk
                    with open(file_path, "wb") as file:
                        file.write(file_response.content)

                    # Extract the .gz file
                    with gzip.open(file_path, "rb") as gz_file:
                        with open(file_path[:-3], "wb") as extracted_file:
                            shutil.copyfileobj(gz_file, extracted_file)

                    # Delete the .gz file
                    os.remove(file_path)

                    # Rename the extracted file to add .xml extension
                    xml_file_path = file_path[:-3] + ".xml"
                    os.rename(file_path[:-3], xml_file_path)

                    print(f"Downloaded and extracted: {xml_file_path}")

        # Check if there is a next page
        next_page_link = driver.find_element(By.XPATH, '//a[text()=">"]')
        if not next_page_link.get_attribute("disabled"):
            # Click on the next page link
            next_page_link.click()
            # Wait for the page to load after navigating to the next page
            time.sleep(5)
        else:
            # Break the loop if there is no next page
            break

finally:
    # Close the webdriver
    driver.quit()
