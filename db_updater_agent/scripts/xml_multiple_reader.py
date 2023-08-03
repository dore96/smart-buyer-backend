import os
import decimal
import psycopg2
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
from psycopg2 import sql
from psycopg2.extras import execute_values

# PostgreSQL connection settings
db_settings = {
    "host": "127.0.0.1",
    "database": "smart_buyer_db",
    "user": "postgres",
    "password": "De9654",
}

def parse_item(item_element):
    item_data = {}
    for child in item_element:
        if child.tag in ['ItemName', 'ItemNm']:
            item_data['ItemName'] = child.text
        elif child.tag == 'QtyInPackage':
            qty_in_package = child.text.strip()
            try:
                item_data[child.tag] = int(qty_in_package)
            except ValueError:
                item_data[child.tag] = None
        elif child.tag == 'ItemPrice':
            item_price = child.text.strip()
            try:
                item_data[child.tag] = decimal.Decimal(item_price)
            except decimal.InvalidOperation:
                item_data[child.tag] = None
        else:
            item_data[child.tag] = child.text
    return item_data

def parse_xml_file(xml_file_path):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        chain_id = root.findtext('ChainId')
        if chain_id is None:
            chain_id = root.findtext('ChainID')
        sub_chain_id = root.findtext('SubChainId')
        if sub_chain_id is None:
            sub_chain_id = root.findtext('SubChainID')
        store_id = root.findtext('StoreId')
        if store_id is None:
            store_id = root.findtext('StoreID')
        xml_items = root.findall('.//Item')
        if not xml_items:
            xml_items = root.findall('.//Product')
        items = []
        for item_element in xml_items:
            item_data = parse_item(item_element)
            item_data['ChainId'] = chain_id
            item_data['SubChainId'] = sub_chain_id
            item_data['StoreId'] = store_id
            items.append(item_data)

    except ET.ParseError as e:
        print(f"Error parsing XML file {xml_file_path}: {e}")
    except Exception as e:
        print(f"Error processing XML file {xml_file_path}: {e}")
    
    return items

def parse_xml_files_in_folder_to_db(folder_path,conn):
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".xml"):
            xml_file_path = os.path.join(folder_path, file_name)
            items = parse_xml_file(xml_file_path)
            insert_data_to_db(items,conn)

def create_table(conn):
    # SQL command to create the table if it doesn't exist
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS products (
            chain_id TEXT,
            sub_chain_id TEXT,
            store_id TEXT,
            item_name TEXT,
            item_price NUMERIC,
            item_code TEXT,
            manufacturer_item_description TEXT,
            price_update_date TIMESTAMP,
            unit_qty TEXT,
            item_type INT,
            manufacturer_name TEXT,
            manufacture_country TEXT,
            unit_of_measure TEXT,
            quantity NUMERIC,
            b_is_weighted INT,
            qty_in_package NUMERIC,
            unit_of_measure_price NUMERIC,
            allow_discount INT,
            item_status INT,
            last_update_date TEXT,
            last_update_time TEXT,
            CONSTRAINT unique_item_info UNIQUE (chain_id, sub_chain_id, store_id, item_code) -- Unique constraint definition
        );
    """
    conn.cursor().execute(create_table_query)
    conn.commit()

def insert_data_to_db(items, conn):
    # Define the SQL query to insert or update data in the 'products' table
    insert_query = sql.SQL("""
        INSERT INTO products (
            chain_id, sub_chain_id, store_id, item_name, item_price, item_code,
            manufacturer_item_description, price_update_date, unit_qty, item_type,
            manufacturer_name, manufacture_country, unit_of_measure, quantity,
            b_is_weighted, qty_in_package, unit_of_measure_price, allow_discount,
            item_status, last_update_date, last_update_time
        ) VALUES %s
        ON CONFLICT (chain_id, sub_chain_id, store_id, item_code) 
        DO UPDATE SET
            item_name = EXCLUDED.item_name,
            item_price = EXCLUDED.item_price,
            manufacturer_item_description = EXCLUDED.manufacturer_item_description,
            price_update_date = EXCLUDED.price_update_date,
            unit_qty = EXCLUDED.unit_qty,
            item_type = EXCLUDED.item_type,
            manufacturer_name = EXCLUDED.manufacturer_name,
            manufacture_country = EXCLUDED.manufacture_country,
            unit_of_measure = EXCLUDED.unit_of_measure,
            quantity = EXCLUDED.quantity,
            b_is_weighted = EXCLUDED.b_is_weighted,
            qty_in_package = EXCLUDED.qty_in_package,
            unit_of_measure_price = EXCLUDED.unit_of_measure_price,
            allow_discount = EXCLUDED.allow_discount,
            item_status = EXCLUDED.item_status,
            last_update_date = EXCLUDED.last_update_date,
            last_update_time = EXCLUDED.last_update_time
    """)

    # Convert the 'items' data into a list of tuples to use with execute_values
    data_to_insert = [
        (
            item.get("ChainId"),
            item.get("SubChainId"),
            item.get("StoreId"),
            item.get("ItemName"),
            item.get("ItemPrice"),
            item.get("ItemCode"),
            item.get("ManufacturerItemDescription"),
            item.get("PriceUpdateDate"),
            item.get("UnitQty"),
            item.get("ItemType"),
            item.get("ManufacturerName"),
            item.get("ManufactureCountry"),
            item.get("UnitOfMeasure"),
            item.get("Quantity"),
            item.get("bIsWeighted"),
            item.get("QtyInPackage"),
            item.get("UnitOfMeasurePrice"),
            item.get("AllowDiscount"),
            item.get("ItemStatus"),
            datetime.now().strftime('%Y-%m-%d'),
            datetime.now().strftime('%H:%M:%S'),
        )
        for item in items
    ]
    # Remove duplicates from the data before inserting
    data_to_insert = list(set(data_to_insert))
    try:
        # Execute the INSERT query with the data
        with conn.cursor() as cursor:
            execute_values(cursor, insert_query, data_to_insert)
        conn.commit()
        print(f"Successfully inserted/updated {len(items)} items into the database.")
    except psycopg2.Error as e:
        print(f"Error inserting/updating data into the database: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web scraping script for shufersal")
    parser.add_argument("--input_folder", required=True, help="The download directory")
    args = parser.parse_args()
    folder_path = args.input_folder
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_settings)
        create_table(conn)
        parse_xml_files_in_folder_to_db(folder_path,conn)
    except psycopg2.Error as e:
        print(f"Error inserting/updating data into the database: {e}")
    conn.close()
