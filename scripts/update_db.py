import os
import subprocess

# Path to the "xml_reader.py" script
xml_reader_script = "xml_reader.py"

# Path to the "shofersal_xml" folder
xml_folder_path = r"C:\Users\dored\Desktop\smart-buyer-backend\shofersal_xml"

# Run the "shufersal_xml_web_scraper.py" script first
subprocess.run(["python", "shufersal_xml_web_scraper.py"])

# Iterate over the XML files in the "shofersal_xml" folder
for xml_file in os.listdir(xml_folder_path):
    if xml_file.endswith(".xml"):
        # Construct the full path to the XML file
        xml_file_path = os.path.join(xml_folder_path, xml_file)

        # Get the supermarket name from the file name using hyphens ("-")
        supermarket_name = xml_file.split("-")[1].strip()

        # Construct the command to run the "xml_reader.py" script with the XML file path
        command = ["python", "xml_reader.py", xml_file_path]

        # Run the command in a subprocess
        subprocess.run(command)
