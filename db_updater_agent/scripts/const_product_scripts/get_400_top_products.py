import psycopg2
import json
import requests
import os
import re

BING_API_KEY = '521233898fa246d59622bebfcc7f2ddb'
json_file_path = r'C:\Users\dored\Desktop\smart buyer backend\smart-buyer-backend\db_updater_agent\scripts\const_product_scripts\top_400_items.json'

# PostgreSQL connection settings
db_settings = {
    "host": "127.0.0.1",
    "database": "smart_buyer_db",
    "user": "postgres",
    "password": "De9654",
}
def get_top_400_items():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_settings)

        # SQL query to get the top 400 most frequently occurring item_code values
        query = """
            SELECT p.item_name, p.item_code,
                   p.manufacturer_item_description, p.unit_qty,
                   COUNT(*) AS occurrence_count
            FROM products p
            JOIN (
                SELECT COALESCE(item_code, '') AS item_code
                FROM products
                GROUP BY item_code
                ORDER BY COUNT(*) DESC
                LIMIT 400
            ) t
            ON p.item_code = t.item_code
            GROUP BY p.item_name, p.item_code,
                    p.manufacturer_item_description, p.unit_qty
            ORDER BY occurrence_count DESC;  -- Sort by occurrence count in descending order
        """

        # Execute the query and fetch the results
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

            # Sort the rows based on the occurrence_count in descending order
            sorted_rows = sorted(rows, key=lambda row: row[4], reverse=True)

            # Take only the top 400 rows
            top_400_rows = sorted_rows[:400]

            # Convert the results to a list of dictionaries
            results = []
            for idx,row in enumerate(top_400_rows, start=1):
                result_dict = {
                    "id": idx,
                    "name": row[0],
                    "code": row[1],
                    "category": 'snacks',
                    "description": row[2],
                    "unit_qty": row[3],
                    "occurrence_count": row[4],  # Number of occurrences
                }
                results.append(result_dict)

        # Save the results in a JSON file
        with open("top_400_items.json", "w", encoding="utf-8") as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=2)

        print("Results saved in 'top_400_items.json'")

    except psycopg2.Error as e:
        print(f"Error executing the query: {e}")

    finally:
        # Close the connection
        conn.close()

# Function to remove invalid characters from a string
def clean_filename(filename):
    return re.sub(r'[\\/:*?"<>|]', '', filename)

# Function to download product image and save it with the desired name
def download_product_image(item_code, item_name):
    url = f"https://m.pricez.co.il/ProductPictures/{item_code}.jpg"
    response = requests.get(url)
    if response.status_code == 200:
        item_name_cleaned = clean_filename(item_name)
        filename = f"product_{item_name_cleaned}_{item_code}.jpg"
        folder_path = r"C:\Users\dored\Desktop\smart buyer backend\product_pictures"
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path
    else:
        return None
    
# Load JSON data from the file
def load_json_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as infile:
        return json.load(infile)

# Save JSON data to the file
def save_json_to_file(json_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as outfile:
        json.dump(json_data, outfile, ensure_ascii=False, indent=2)

def add_images_from_web():
  # Load JSON data from the file
  json_data = load_json_from_file(json_file_path)

  # Process each item in the JSON data and download the image
  for item in json_data:
      item_code = item['code']
      item_name = item['name']
      image_path = download_product_image(item_code, item_name)
      if image_path:
          item['image_path'] = image_path
      else:
          item['image_path'] = None

  # Save the updated JSON data back to the file
  save_json_to_file(json_data, json_file_path)

  print("Image URLs added and JSON data saved to 'updated_products_with_images.json'")

if __name__ == "__main__":
    get_top_400_items()
    add_images_from_web()