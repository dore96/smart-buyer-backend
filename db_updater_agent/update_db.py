import os
import subprocess
import shutil

def run_web_scrapers(web_scraping_script_path_map,xml_data_folder_path,website_url_map):
    for chain, script_path in web_scraping_script_path_map.items():
        # Create a folder for each web scraper
        scraper_folder_name = f"{chain}_xmls"
        scraper_folder_path = os.path.join(xml_data_folder_path, scraper_folder_name)
        if not os.path.exists(scraper_folder_path):
            os.makedirs(scraper_folder_path)

         # Command to run the web scraping script using the Python interpreter
        command = ["python",script_path,"--output_folder",scraper_folder_path, "--url",website_url_map[chain]]

        # Use subprocess to execute the command in a new process
        try:
            subprocess.run(command, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running web scraper for {chain}: {e}")

def process_data_and_insert_into_db(web_scraping_script_path_map,xml_data_folder_path,xml_reader_script):
    for website, _ in web_scraping_script_path_map.items():
        scraper_folder_name = f"{website}_xmls"
        scraper_folder_path = os.path.join(xml_data_folder_path, scraper_folder_name)

        # Run xml_reader_script for each scraper's folder
        reader_command = ["python",xml_reader_script,"--input_folder",scraper_folder_path]

        try:
            subprocess.run(reader_command, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running xml_reader_script for {scraper_folder_name}: {e}")

        # After inserting data into the database, remove the unnecessary folder
        # try:
        #     shutil.rmtree(scraper_folder_path)
        # except OSError as e:
        #     print(f"Error removing folder {scraper_folder_path}: {e}")

def main():
    xml_reader_script = r'C:\Users\dored\Desktop\smart buyer backend\smart-buyer-backend\db_updater_agent\scripts\xml_multiple_reader.py'
    xml_data_folder_path = r"C:\Users\dored\Desktop\smart buyer backend\xml_data"
    web_scraping_script_path_map = {
        "zol_begadol": r'C:\Users\dored\Desktop\smart buyer backend\smart-buyer-backend\db_updater_agent\scripts\web_scrapers\zol_begadol_web_scraper.py',
        "rami_levi": r'C:\Users\dored\Desktop\smart buyer backend\smart-buyer-backend\db_updater_agent\scripts\web_scrapers\rami_levi_web_scraper.py',
        "shufersal": r'C:\Users\dored\Desktop\smart buyer backend\smart-buyer-backend\db_updater_agent\scripts\web_scrapers\shufersal_xml_web_scraper.py',
        "victory" : r'C:\Users\dored\Desktop\smart buyer backend\smart-buyer-backend\db_updater_agent\scripts\web_scrapers\victory_web_scraper.py'
    }
    website_url_map = {
        "victory" : "http://matrixcatalog.co.il/NBCompetitionRegulations.aspx",
        "rami_levi": "https://url.retail.publishedprices.co.il/login",
        "shufersal": "http://prices.shufersal.co.il/",
        "zol_begadol": "https://zolvebegadol.binaprojects.com/Main.aspx"
    }

    # run_web_scrapers(web_scraping_script_path_map,xml_data_folder_path,website_url_map)
    process_data_and_insert_into_db(web_scraping_script_path_map,xml_data_folder_path,xml_reader_script)

if __name__ == "__main__":
    main()
