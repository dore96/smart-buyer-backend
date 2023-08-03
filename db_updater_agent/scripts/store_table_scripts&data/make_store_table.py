import xml.etree.ElementTree as ET
import psycopg2
import sys
import re

chains_id_map ={
    "שופרסל" :  "7290027600007",
    "רמי לוי" :  "7290058140886",
    "זול ובגדול" : "7290058173198",
    "ויקטורי" : "7290696200003",
    "מחסני השוק" : "7290661400001",
    "סופר ברקת" : "7290875100001"
}

# PostgreSQL connection settings
db_settings = {
    "host": "127.0.0.1",
    "database": "smart_buyer_db",
    "user": "postgres",
    "password": "De9654",
}

def create_table(conn, table_name):
    # SQL command to create the table if it doesn't exist
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            chainname TEXT,
            subchainname TEXT,
            storename TEXT,
            address TEXT,
            city TEXT,
            zipcode BIGINT,
            chain_id TEXT,
            subchainid BIGINT,
            storeid BIGINT,
            PRIMARY KEY (chain_id, subchainid, storeid)
        );
    """
    conn.cursor().execute(create_table_query)
    conn.commit()

def safe_convert_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def parse_and_insert_stores_db(root, conn,table_name, chain_id):
    if chain_id == chains_id_map["שופרסל"]:
        shofersal_data_insertion(root, conn,table_name)
    elif chain_id == chains_id_map["רמי לוי"] or chain_id == chains_id_map["זול ובגדול"]:
        rami_levi_data_insertion(root, conn,table_name, chain_id)
    elif chain_id == chains_id_map["ויקטורי"] or chain_id == chains_id_map["מחסני השוק"] or chain_id == chains_id_map["סופר ברקת"]:
        victory_data_insert(root, conn,table_name, chain_id)

def insert_data(conn, table_name, data):
    # SQL command to insert data into the table
    insert_query = f"""
        INSERT INTO {table_name} (chain_id, subchainid, storeid, chainname, subchainname, storename, address, city, zipcode)
        VALUES (%(chain_id)s, %(subchainid)s, %(storeid)s, %(chainname)s, %(subchainname)s, %(storename)s, %(address)s, %(city)s, %(zipcode)s);
    """
    conn.cursor().execute(insert_query, data)
    conn.commit()

def shofersal_data_insertion(root, conn, table_name):
    # Get the constant chain_id value
    chain_id = "7290027600007"

    # Iterate over the XML elements
    for store in root.findall(".//STORE"):
        data = {
            "chain_id": chain_id,
            "subchainid": safe_convert_int(store.findtext("SUBCHAINID")),
            "storeid": safe_convert_int(store.findtext("STOREID")),
            "chainname": store.findtext("CHAINNAME"),
            "subchainname": store.findtext("SUBCHAINNAME"),
            "storename": store.findtext("STORENAME"),
            "address": store.findtext("ADDRESS"),
            "city": store.findtext("CITY"),
            "zipcode": safe_convert_int(store.findtext("ZIPCODE"))
        }
        insert_data(conn, table_name, data)

def rami_levi_data_insertion(root, conn, table_name, chain_id):

    subchain = root.find(".//SubChain")

    # Check if SubChain element is found
    if subchain is not None:
        stores = subchain.find(".//Stores")
        if stores is not None:
            # Iterate over the Store elements
            for store in stores.findall(".//Store"):
                data = {
                    "chain_id": chain_id,
                    "subchainid": safe_convert_int(subchain.findtext("SubChainId")),
                    "storeid": safe_convert_int(store.findtext("StoreId")),
                    "chainname": root.findtext("ChainName"),
                    "subchainname": subchain.findtext("SubChainName"),
                    "storename": store.findtext("StoreName"),
                    "address": store.findtext("Address"),
                    "city": store.findtext("City"),
                    "zipcode": safe_convert_int(store.findtext("ZipCode"))
                }
                insert_data(conn, table_name, data)
        else:
            print("Stores element not found.")
    else:
        print("SubChain element not found.")

def victory_data_insert(root, conn, table_name, chain_id):
    subchain = root.find(".//Branches")
    # Iterate over the XML elements
    for store in subchain.findall(".//Branch"):
        data = {
            "chain_id": chain_id,
            "subchainid": safe_convert_int(store.findtext("SubChainID")),
            "storeid": safe_convert_int(store.findtext("StoreID")),
            "chainname": store.findtext("ChainName"),
            "subchainname": store.findtext("SubChainName"),
            "storename": store.findtext("StoreName"),
            "address": store.findtext("Address"),
            "city": store.findtext("City"),
            "zipcode": safe_convert_int(store.findtext("ZIPCode"))
        }
        if data["chainname"] == '':
            data["chainname"] = data["subchainname"] = "סופר ברקת"
        insert_data(conn, table_name, data)

def get_chain_id(xml_path):
    # Use regular expression to find the number that comes after "Stores" and before the first "-"
    pattern = r"Stores(?:Full)?(\d+)"
    match = re.search(pattern, xml_path)

    if match:
        number = match.group(1)
    else:
        raise ValueError("Number not found in the file path.")
    return number

def main(xml_file):
    # Load the XML file using iterparse for iterative parsing
    tree = ET.parse(xml_file)
    root = tree.getroot()
    conn = psycopg2.connect(**db_settings)

    try:
        table_name = "stores_table"
        create_table(conn, table_name)
        chain_id = get_chain_id(xml_file)
        parse_and_insert_stores_db(root, conn,table_name, chain_id)
        conn.close()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python xml_reader.py <xml_file_path>")
    else:
        xml_file_path = sys.argv[1]
        main(xml_file_path)
