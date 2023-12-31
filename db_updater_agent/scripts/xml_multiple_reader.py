import os
import decimal
import psycopg2
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
from psycopg2 import sql
from psycopg2.extras import execute_values
from ..config import db_settings

def parse_item(item_element):
    """
    Parse an XML item element and extract relevant data.

    Args:
        item_element (xml.etree.Element): The XML item element.

    Returns:
        dict: A dictionary containing extracted item data.
    """
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

def get_city_name(chain_id ,sub_chain_id ,store_id):
    """
    Retrieve the city name for a given chain, sub-chain, and store IDs.

    Args:
        chain_id (str): The chain ID.
        sub_chain_id (str): The sub-chain ID.
        store_id (str): The store ID.

    Returns:
        str: The city name associated with the provided IDs.
    """
    if chain_id and sub_chain_id and store_id:
        with conn.cursor() as cursor:
            query = sql.SQL("""
                SELECT city FROM stores_table
                WHERE chain_id = %s AND subchainid = %s AND storeid = %s
            """)
            cursor.execute(query, (chain_id, sub_chain_id, store_id))
            result = cursor.fetchone()
            if result:
                return(result[0].strip())

def parse_xml_file(xml_file_path):
    """
    Parse an XML file and extract item data.

    Args:
        xml_file_path (str): The path to the XML file.

    Returns:
        list: A list of dictionaries containing extracted item data.
    """
    items = []
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

        store_city = get_city_name(chain_id ,sub_chain_id ,store_id)
        if store_city:
            items = []
            for item_element in xml_items:
                item_data = parse_item(item_element)
                item_data['city'] = store_city
                item_data['ChainId'] = chain_id
                item_data['SubChainId'] = int(sub_chain_id)
                item_data['StoreId'] = int(store_id)
                items.append(item_data)

    except ET.ParseError as e:
        print(f"Error parsing XML file {xml_file_path}: {e}")
    except Exception as e:
        print(f"Error processing XML file {xml_file_path}: {e}")
    
    return items

def parse_xml_files_in_folder_to_db(folder_path,conn):
    """
    Parse XML files in a folder and insert the extracted data into the database.

    Args:
        folder_path (str): The path to the folder containing XML files.
        conn (psycopg2.extensions.connection): The database connection.
    """
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".xml"):
            xml_file_path = os.path.join(folder_path, file_name)
            items = parse_xml_file(xml_file_path)
            insert_data_to_db(items,conn)

def create_table(conn):
    """
    Create the 'products' table in the database if it doesn't exist.

    Args:
        conn (psycopg2.extensions.connection): The database connection.
    """
    # SQL command to create the table if it doesn't exist
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS products (
            city TEXT,
            chain_id TEXT,
            sub_chain_id INT,
            store_id INT,
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
    """
    Insert or update data into the 'products' table in the database.

    Args:
        items (list): A list of dictionaries containing item data.
        conn (psycopg2.extensions.connection): The database connection.
    """
    # Define the SQL query to insert or update data in the 'products' table
    insert_query = sql.SQL("""
        INSERT INTO products (
            city , chain_id, sub_chain_id, store_id, item_name, item_price, item_code,
            manufacturer_item_description, price_update_date, unit_qty, item_type,
            manufacturer_name, manufacture_country, unit_of_measure, quantity,
            b_is_weighted, qty_in_package, unit_of_measure_price, allow_discount,
            item_status, last_update_date, last_update_time
        ) VALUES %s
        ON CONFLICT (chain_id, sub_chain_id, store_id, item_code) 
        DO UPDATE SET
            city = EXCLUDED.city,
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

    # Convert the 'items' data into a list of dictionaries
    data_to_insert = []
    unique_items = set()
    for item in items:
        item_key = (
            item.get("ChainId"),
            item.get("SubChainId"),
            item.get("StoreId"),
            item.get("ItemCode")
        )
        # Check if the item_key already exists in the unique_items set
        # If not, add the item to the list and mark the item_key as seen
        if item_key not in unique_items:
            unique_items.add(item_key)
            data_to_insert.append({
                "city": item.get("city"),
                "ChainId": item.get("ChainId"),
                "SubChainId": item.get("SubChainId"),
                "StoreId": item.get("StoreId"),
                "ItemName": item.get("ItemName"),
                "ItemPrice": item.get("ItemPrice"),
                "ItemCode": item.get("ItemCode"),
                "ManufacturerItemDescription": item.get("ManufacturerItemDescription"),
                "PriceUpdateDate": item.get("PriceUpdateDate"),
                "UnitQty": item.get("UnitQty"),
                "ItemType": item.get("ItemType"),
                "ManufacturerName": item.get("ManufacturerName"),
                "ManufactureCountry": item.get("ManufactureCountry"),
                "UnitOfMeasure": item.get("UnitOfMeasure"),
                "Quantity": item.get("Quantity"),
                "bIsWeighted": item.get("bIsWeighted"),
                "QtyInPackage": item.get("QtyInPackage"),
                "UnitOfMeasurePrice": item.get("UnitOfMeasurePrice"),
                "AllowDiscount": item.get("AllowDiscount"),
                "ItemStatus": item.get("ItemStatus"),
            })

    # Convert data back to a list of tuples
    data_to_insert_tuples = [
        (
            item.get("city"),
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
        for item in data_to_insert
    ]

    try:
        # Execute the INSERT query with the data
        with conn.cursor() as cursor:
            execute_values(cursor, insert_query, data_to_insert_tuples)
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
