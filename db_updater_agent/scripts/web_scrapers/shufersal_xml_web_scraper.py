import os
import gzip
import shutil
import time
import requests
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

def set_up_webdriver(download_directory):
    # Set up Chrome options to ignore SSL certificate errors and set download preferences
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_directory,
    })

    # Initialize the Chrome webdriver
    driver = webdriver.Chrome(options=chrome_options)
    return driver   

def select_prices_full_option(driver):
    # Find the dropdown menu by its ID
    dropdown_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ddlCategory"))
    )

    # Create a Select object to interact with the dropdown
    dropdown = Select(dropdown_element)

    # Select the "PricesFull" option by its value (2)
    dropdown.select_by_value("2")

    time.sleep(5)

def download_and_extract_file(download_url, download_directory):
    file_name = download_url.split("/")[-1].split("?")[0]
    file_path = os.path.join(download_directory, file_name)

    # Check if the file already exists in the download directory
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

def scrape_website(download_directory,url):
    # Initialize the Chrome webdriver
    driver = set_up_webdriver(download_directory)

    try:
        # Open the website in the browser
        driver.get(url)
        # Select the "PricesFull" option
        select_prices_full_option(driver)
        while True:
            # Find the table body (tbody) containing the rows
            table_body = driver.find_element(By.TAG_NAME, "tbody")
            # Find all the rows (tr) in the table body
            rows = table_body.find_elements(By.TAG_NAME, "tr")
            # Create a folder to save the downloaded files
            if not os.path.exists(download_directory):
                os.makedirs(download_directory)
            # Iterate through each row and download the files
            for row in rows:
                # Find the first link (a tag) in the row
                link = row.find_element(By.TAG_NAME, "a")
                if link:
                    download_url = link.get_attribute("href")
                    if "PriceFull" in download_url:
                        download_and_extract_file(download_url, download_directory)

            try: 
                # Check if there is a next page
                next_page_link = driver.find_element(By.XPATH, '//a[text()=">"]')
                if not next_page_link.get_attribute("disabled"):
                    next_page_link.click()
                    time.sleep(5)
                else:
                    # Break the loop if there is no next page
                    break
            except NoSuchElementException:
                # The "Next" page link is not found, indicating the last page
                print("Reached the last page.")
                break  # Exit the loop as we are on the last page
            
    finally:
        driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Web scraping script for shufersal")
    parser.add_argument("--output_folder", required=True, help="The download directory")
    parser.add_argument("--url", required=True, help="URL of the website")
    args = parser.parse_args()

    scrape_website(args.output_folder, args.url)

if __name__ == "__main__":
    main()