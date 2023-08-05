import time
import os
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from gz_directory_extractor import extract_files_from_folder

##################################################################
# needs to Allowe browser to automatically download multiple files
##################################################################

def configure_chrome_options(download_directory):
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_directory,
        'profile.default_content_setting_values.automatic_downloads': 1  # Allow automatic downloads
    })
    return chrome_options

def enter_current_date(driver):
    current_date = time.strftime("%d/%m/%Y")
    date_input = driver.find_element(By.ID, "wDate")
    date_input.clear()
    date_input.send_keys(current_date)

def click_button(driver):
    button = driver.find_element(By.ID, "Button1")
    button.click()

def download_files(driver, download_directory):
    table_body = driver.find_element(By.TAG_NAME, "tbody")
    rows = table_body.find_elements(By.TAG_NAME, "tr")
    downloaded_store_ids = set()

    for row_number, row in enumerate(rows[1:], start=0):
        download_button = row.find_element(By.ID, f"button{row_number}")
        driver.execute_script(download_button.get_attribute("onclick"))

        file_name = download_button.get_attribute("onclick").split("'")[1]
        store_id = file_name.split('-')[1]

        if store_id in downloaded_store_ids:
            print(f"Skipping duplicate file: {file_name}")
            continue

        wait = WebDriverWait(driver, 20)
        downloaded_gz_file_path = os.path.join(download_directory, file_name)
        wait.until(lambda driver: os.path.exists(downloaded_gz_file_path) and os.path.getsize(downloaded_gz_file_path) > 0)

        downloaded_store_ids.add(store_id)

def zol_begadol_levi_web_scraper(download_directory, url):
    chrome_options = configure_chrome_options(download_directory)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    file_type_select = Select(driver.find_element(By.ID, "wFileType"))
    file_type_select.select_by_value("4")

    enter_current_date(driver)

    click_button(driver)

    time.sleep(5)

    download_files(driver, download_directory)

    driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Web scraping script for shufersal")
    parser.add_argument("--output_folder", required=True, help="The download directory")
    parser.add_argument("--url", required=True, help="URL of the website")
    args = parser.parse_args()

    try:
        zol_begadol_levi_web_scraper(args.output_folder, args.url)
        extract_files_from_folder(args.output_folder, False)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

# def zol_begadol_levi_web_scraper(download_directory,url):
#     # Set up Chrome options to ignore SSL certificate errors and set download preferences
#     chrome_options = Options()
#     chrome_options.add_argument('--ignore-certificate-errors')
#     chrome_options.add_experimental_option('prefs', {
#         'download.default_directory': download_directory,
#         'profile.default_content_setting_values.automatic_downloads': 1  # Allow automatic downloads
#     })

#     driver = webdriver.Chrome(options=chrome_options)
#     driver.get(url)

#     # Find the file type select element and select the desired file type (e.g., "מחירים מלא")
#     file_type_select = Select(driver.find_element(By.ID, "wFileType"))
#     file_type_option = "4"  # Replace with the value of the desired file type option
#     file_type_select.select_by_value(file_type_option)

#     # Get the current date in the format "dd/mm/yyyy"
#     current_date = time.strftime("%d/%m/%Y")

#     # Find the date input field and enter the current date
#     date_input = driver.find_element(By.ID, "wDate")
#     date_input.clear()
#     date_input.send_keys(current_date)

#     # Find and click the button with id "Button1"
#     button = driver.find_element(By.ID, "Button1")
#     button.click()

#     # Wait for a few seconds to allow the page to load after submitting the form
#     time.sleep(2)

#     # Find the table body (tbody) containing the rows
#     table_body = driver.find_element(By.TAG_NAME, "tbody")

#     # Find all rows in the table containing the download links
#     rows = table_body.find_elements(By.TAG_NAME, "tr")

#     # Create a set to keep track of store IDs
#     downloaded_store_ids = set()

#     # Loop through each row and download the file
#     for row_number, row in enumerate(rows[1:], start=0):
#         download_button = row.find_element(By.ID, f"button{row_number}")
#         driver.execute_script(download_button.get_attribute("onclick"))

#         # Get the file name from the download_button's onclick attribute
#         file_name = download_button.get_attribute("onclick").split("'")[1]

#         # Get the store ID from the file name
#         store_id = file_name.split('-')[1]
        
#         # Check if the store ID is already downloaded
#         if store_id in downloaded_store_ids:
#             print(f"Skipping duplicate file: {file_name}")
#             continue
        
#         file_full_path = os.path.join(download_directory, file_name)

#         # Wait for the file to be fully downloaded (explicit wait)
#         wait = WebDriverWait(driver, 20)  # Maximum wait time of 20 seconds
#         downloaded_gz_file_path = os.path.join(download_directory, file_name)
#         wait.until(lambda driver: os.path.exists(downloaded_gz_file_path) and os.path.getsize(downloaded_gz_file_path) > 0)
        
#         # Add the store ID to the downloaded_store_ids set
#         downloaded_store_ids.add(store_id)

#     # Close the browser window
#     driver.quit()