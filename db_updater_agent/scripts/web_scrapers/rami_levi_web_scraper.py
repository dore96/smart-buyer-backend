import os
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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

def login_to_website(url,driver):
    driver.get(url)
    # Find the username input field by its name
    username_input = driver.find_element(By.NAME, 'username')
    # Enter the username 'RamiLevi'
    username_input.send_keys('RamiLevi')
    # Press Enter key to submit the form
    username_input.send_keys(Keys.ENTER)
    # Wait for a few seconds to allow the page to load after performing the search
    time.sleep(3)

def perform_search(driver):
    # Find the search input field by its class name
    search_input = driver.find_element(By.CLASS_NAME, 'form-control')
    # Enter "pricefull" into the search bar
    search_input.send_keys('pricefull')
    # Press Enter key to perform the search (if needed)
    search_input.send_keys(Keys.ENTER)
    # Wait for a few seconds to allow the page to load after submitting the form
    time.sleep(3)

def download_files(download_directory,driver):
    # Find the table body (tbody) containing the rows
    table_body = driver.find_element(By.TAG_NAME, "tbody")
    # Find all rows in the table containing the download links
    rows = table_body.find_elements(By.TAG_NAME, "tr")

    # Create a set to keep track of store IDs
    downloaded_store_ids = set()

    # Loop through each row and download the file
    for row in rows:
        link = row.find_element(By.XPATH, './/a[contains(@href, "/file/d/")]')
        file_url = link.get_attribute('href')
        file_name = file_url.split('/')[-1]

        # Get the store ID from the file name
        store_id = file_name.split('-')[1]
        
        # Check if the store ID is already downloaded
        if store_id in downloaded_store_ids:
            print(f"Skipping duplicate file: {file_name}")
            continue

        # Download the file using the Chrome driver and wait for download to complete
        driver.get(file_url)
        download_path = os.path.join(download_directory, file_name + '.crdownload')
        while os.path.exists(download_path):
            time.sleep(1)

        # # Wait for the file to be fully downloaded (explicit wait)
        wait = WebDriverWait(driver, 20)  # Maximum wait time of 20 seconds
        downloaded_gz_file_path = os.path.join(download_directory, file_name)
        wait.until(lambda driver: os.path.exists(downloaded_gz_file_path) and os.path.getsize(downloaded_gz_file_path) > 0)
        
        # Add the store ID to the downloaded_store_ids set
        downloaded_store_ids.add(store_id)

def run_rami_levi_web_scraper(download_directory, url):
    chrome_options = setup_chrome_options(download_directory)
    driver = webdriver.Chrome(options=chrome_options)

    login_to_website(url,driver)
    perform_search(driver)
    download_files(download_directory,driver)

    time.sleep(10)
    # Close the browser window
    print("Done downloading rami levi files.")
    driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Web scraping script for shufersal")
    parser.add_argument("--output_folder", required=True, help="The download directory")
    parser.add_argument("--url", required=True, help="URL of the website")
    args = parser.parse_args()

    try:
        run_rami_levi_web_scraper(args.output_folder, args.url)
        extract_files_from_folder(args.output_folder, False)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()