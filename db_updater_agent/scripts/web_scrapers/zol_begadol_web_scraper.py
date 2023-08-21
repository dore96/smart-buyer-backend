import time
import os
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from gz_directory_extractor import extract_files_from_folder

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

        downloaded_store_ids.add(store_id)

def zol_begadol_levi_web_scraper(download_directory, url):
    chrome_options = configure_chrome_options(download_directory)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    time.sleep(5)

    file_type_select = Select(driver.find_element(By.ID, "wFileType"))
    file_type_select.select_by_value("4")

    enter_current_date(driver)

    click_button(driver)

    time.sleep(10)

    download_files(driver, download_directory)
    time.sleep(10)
    driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Web scraping script for shufersal")
    parser.add_argument("--output_folder", required=True, help="The download directory")
    parser.add_argument("--url", required=True, help="URL of the website")
    args = parser.parse_args()

    try:
        zol_begadol_levi_web_scraper(args.output_folder, args.url)
        extract_files_from_folder(args.output_folder, True)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()