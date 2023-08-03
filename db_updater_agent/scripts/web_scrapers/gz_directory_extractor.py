import os
import shutil
import gzip
import zipfile

def extract_gz_file(gz_file_path, extraction_directory):
    try:
        with gzip.open(gz_file_path, 'rb') as gz_file:
            extracted_file_path = os.path.join(extraction_directory, os.path.splitext(os.path.basename(gz_file_path))[0] +
                                                ('.xml' if not gz_file_path.endswith('.xml') else ''))
            with open(extracted_file_path, 'wb') as xml_file:
                shutil.copyfileobj(gz_file, xml_file)
        print(f"Extracted XML file from GZ: {extracted_file_path}")
        # Delete the .gz file after extracting its content
        os.remove(gz_file_path)
    except gzip.BadGzipFile:
        print(f"Skipping non-gzip file: {gz_file_path}")

def extract_zip_file(zip_file_path, extraction_directory):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        zip_file.extractall(path=extraction_directory)
    print(f"Extracted XML files from ZIP: {zip_file_path}")
    # Delete the .gz that is zip file after extracting its content
    os.remove(zip_file_path)

def extract_files_from_folder(folder_path, is_zol_begadol):
    for file_name in os.listdir(folder_path):
        file_full_path = os.path.join(folder_path, file_name)
        if is_zol_begadol:
            if file_name.endswith(".gz"):
              extract_zip_file(file_full_path, folder_path)
        elif file_name.endswith(".gz"):
            extract_gz_file(file_full_path, folder_path)
