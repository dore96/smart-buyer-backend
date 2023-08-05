import json

json_file_path = r'C:\Users\dored\Desktop\smart buyer backend\smart-buyer-backend\updated_products_with_images.json'

def load_json_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as infile:
        return json.load(infile)

# Load JSON data from the file
json_data = load_json_from_file(json_file_path)

# Calculate the number of items in the JSON array
num_items = len(json_data)

# Count the number of items where the 'image_path' is empty
num_items_with_empty_url = 0
for item in json_data:
    if not item.get('image_path'):
        num_items_with_empty_url += 1

# Create a dictionary to count the occurrences of each image URL
image_url_count = {}

# Loop through the data and count the occurrences of each image URL
for item in json_data:
    image_url = item["image_path"]
    if image_url in image_url_count:
        image_url_count[image_url] += 1
    else:
        image_url_count[image_url] = 1

duplicate_urls_count = sum(count > 1 for count in image_url_count.values())


print(f"Number of items in the JSON file: {num_items}")
print(f"Number of items with empty URL: {num_items_with_empty_url}")
print("Number of items with the same image URLs:", duplicate_urls_count)

