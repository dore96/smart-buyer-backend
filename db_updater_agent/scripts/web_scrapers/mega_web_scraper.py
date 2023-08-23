import time
import os
import argparse
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from gz_directory_extractor import extract_files_from_folder
import datetime

def configure_chrome_options(download_directory):
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_directory,
        'profile.default_content_setting_values.automatic_downloads': 1  # Allow automatic downloads
    })
    return chrome_options

def click_button(driver):
    button = driver.find_element(By.ID, "Button1")
    button.click()

def download_files(driver, download_directory):
    try:
        table_body = driver.find_element(By.XPATH, '//tbody')
        rows = table_body.find_elements(By.XPATH, './/tr')

        # Iterate through the rows and find links that start with "PriceFull"
        for row in rows[3:-2]:
            link = row.find_element(By.XPATH, './/a')
            link_text = link.get_attribute('href')
            filename = link_text.split('/')[-1]
            
            if filename.startswith('PriceFull'):
                
                # Set the local path for downloading
                local_path = os.path.join(download_directory, filename)

                # Download the file using requests
                response = requests.get(link_text)

                # Save the file to the specified directory
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Error: {e}")

def mega_web_scraper(download_directory, url):
    chrome_options = configure_chrome_options(download_directory)
    driver = webdriver.Chrome(options=chrome_options)

    # Get the current date
    current_date = datetime.datetime.now()

    # Subtract one day from the current date
    previous_date = current_date - datetime.timedelta(days=1)

    # Format the previous date as "yyyymmdd"
    date_stamp = previous_date.strftime("%Y%m%d")

    # Append the date stamp to the base URL
    url_with_date = url + date_stamp

    # Navigate to the URL with the appended date stamp
    driver.get(url_with_date)

    download_files(driver, download_directory)
    time.sleep(10)
    driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Web scraping script for yeynot bitan")
    parser.add_argument("--output_folder", required=True, help="The download directory")
    parser.add_argument("--url", required=True, help="URL of the website")
    args = parser.parse_args()

    try:
        mega_web_scraper(args.output_folder, args.url)
        extract_files_from_folder(args.output_folder, False)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()