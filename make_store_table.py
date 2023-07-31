import xml.etree.ElementTree as ET
import psycopg2

def create_table(conn, table_name):
    # SQL command to create the table if it doesn't exist
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            chain_id TEXT,
            subchainid BIGINT,
            storeid BIGINT,
            bikoretno BIGINT,
            storetype BIGINT,
            chainname TEXT,
            subchainname TEXT,
            storename TEXT,
            address TEXT,
            city TEXT,
            zipcode BIGINT,
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

def insert_data(conn, table_name, data):
    # SQL command to insert data into the table
    insert_query = f"""
        INSERT INTO {table_name} (chain_id, subchainid, storeid, bikoretno, storetype, chainname, subchainname, storename, address, city, zipcode)
        VALUES (%(chain_id)s, %(subchainid)s, %(storeid)s, %(bikoretno)s, %(storetype)s, %(chainname)s, %(subchainname)s, %(storename)s, %(address)s, %(city)s, %(zipcode)s);
    """
    conn.cursor().execute(insert_query, data)
    conn.commit()

def main(xml_file):
    # Load the XML file using iterparse for iterative parsing
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # PostgreSQL connection settings
    db_settings = {
        "host": "127.0.0.1",
        "database": "smart_buyer_db",
        "user": "postgres",
        "password": "De9654",
    }
    conn = psycopg2.connect(**db_settings)

    try:
        # Create the table for the supermarket if it doesn't exist
        table_name = "stores_table"
        create_table(conn, table_name)

        # Get the constant chain_id value
        chain_id = "7290027600007"

        # Iterate over the XML elements
        for store in root.findall(".//STORE"):
            data = {
                "chain_id": chain_id,
                "subchainid": safe_convert_int(store.findtext("SUBCHAINID")),
                "storeid": safe_convert_int(store.findtext("STOREID")),
                "bikoretno": safe_convert_int(store.findtext("BIKORETNO")),
                "storetype": safe_convert_int(store.findtext("STORETYPE")),
                "chainname": store.findtext("CHAINNAME"),
                "subchainname": store.findtext("SUBCHAINNAME"),
                "storename": store.findtext("STORENAME"),
                "address": store.findtext("ADDRESS"),
                "city": store.findtext("CITY"),
                "zipcode": safe_convert_int(store.findtext("ZIPCODE"))
            }
            insert_data(conn, table_name, data)

        # Close the database connection
        conn.close()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Provide the path to the XML file as a command-line argument
    import sys
    if len(sys.argv) != 2:
        print("Usage: python xml_reader.py <xml_file_path>")
    else:
        xml_file_path = sys.argv[1]
        main(xml_file_path)

