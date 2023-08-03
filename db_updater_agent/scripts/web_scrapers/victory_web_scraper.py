import os
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from gz_directory_extractor import extract_files_from_folder

def setup_chrome_options(download_directory):
    # Set up Chrome options to ignore SSL certificate errors and set download preferences
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_directory,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    })
    return chrome_options

def perform_search(driver):
    # Find the search input field by its ID
    file_type_dropdown = Select(driver.find_element(By.ID, 'MainContent_fileType'))
    # Select the "pricefull" option from the dropdown
    file_type_dropdown.select_by_value('pricefull')
    
    # Click the "חיפוש" (Search) button
    search_button = driver.find_element(By.ID, 'MainContent_btnSearch')
    driver.execute_script("arguments[0].click();", search_button)
    time.sleep(3)  # Adding a sleep to wait for the search results to load

    # Click the "רשת" button to orgenize the search results by chains
    chain_header_link = driver.find_element(By.ID, 'MainContent_lblTableHeaderSubChain')
    chain_header_link.click()

def extract_chain_and_store_id(input_string):
    parts = input_string.split('-')
    chain_id = parts[0][9:]
    store_id = parts[1]
    return chain_id, store_id

def download_files(download_directory,driver):
    # Find the table body (tbody) containing the rows
    table_body = driver.find_element(By.TAG_NAME, "tbody")
    # Find all rows in the table containing the download links
    rows = table_body.find_elements(By.TAG_NAME, "tr")
    # Create a set to keep track of store IDs
    downloaded_store_ids = set()
    # Loop through each row and download the file
    for row in rows[1:]:
        # Extract the text from the first column (file name)
        file_name = row.find_element(By.XPATH, ".//td[1]").text
        # Extract chain_id and store_id from the file name
        chain_id, store_id = extract_chain_and_store_id(file_name)
        
        # Check if the store ID and chain ID tupel already downloaded
        if (store_id,chain_id) in downloaded_store_ids:
            print(f"Skipping duplicate file: {file_name}")
            continue
        if chain_id == "7290455000004":
            continue
        
        # Find the download link in the current row, click it, and wait to download complete
        download_link = row.find_element(By.XPATH, ".//a")
        download_link.click()
        download_path = os.path.join(download_directory, file_name + '.crdownload')
        while os.path.exists(download_path):
            time.sleep(1)
        wait = WebDriverWait(driver, 20)  # Maximum wait time of 20 seconds
        downloaded_gz_file_path = os.path.join(download_directory, file_name + '.xml.gz')
        wait.until(lambda driver: os.path.exists(downloaded_gz_file_path) and os.path.getsize(downloaded_gz_file_path) > 0)
        
        # Save the file with the modified name
        if chain_id == "7290633800006":
          new_file_name = f"PriceFull7290661400001-{store_id}-123.xml.gz"
          os.rename(downloaded_gz_file_path, os.path.join(download_directory, new_file_name))
        # Add the store ID to the downloaded_store_ids set
        downloaded_store_ids.add((store_id, chain_id))

def run_victory_web_scraper(download_directory, url):
    chrome_options = setup_chrome_options(download_directory)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    perform_search(driver)
    download_files(download_directory,driver)

    time.sleep(10)
    # Close the browser window
    print("Done downloading victory files.")
    driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Web scraping script for shufersal")
    parser.add_argument("--output_folder", required=True, help="The download directory")
    parser.add_argument("--url", required=True, help="URL of the website")
    args = parser.parse_args()

    try:
        run_victory_web_scraper(args.output_folder, args.url)
        extract_files_from_folder(args.output_folder, False)
    except Exception as e:
        print(f"An error occurred: {e}")

    

if __name__ == "__main__":
    main()