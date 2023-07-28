import json

# Read JSON data from file
json_file_path = r"C:\Users\dored\Desktop\smart-buyer-backend\shofersal_stores.json"

with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Map structure to store supermarket IDs and names
shofersal_supermarket_map = {}

# Extracting data from the JSON and converting it to the desired format
for store in data["abap"]["values"]["STORES"]["STORE"]:
    store_id = str(store["STOREID"]).zfill(3)
    chain_name = store["CHAINNAME"]
    store_name = store["STORENAME"].replace(" ", "_").replace('"', '')  # Replace spaces with underscores and remove double quotes
    full_name = f"{chain_name}_{store_name}"
    shofersal_supermarket_map[store_id] = full_name

# Sorting the dictionary by store ID in ascending order
sorted_shofersal_map = sorted(shofersal_supermarket_map.items(), key=lambda x: int(x[0]))

# Printing each entry on a separate line with quotes around the key and value
for store_id, store_name in sorted_shofersal_map:
    print(f'"{store_id}": "{store_name}",')
