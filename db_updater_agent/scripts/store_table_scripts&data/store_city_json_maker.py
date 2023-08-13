import psycopg2
import json
import codecs

# Database connection parameters
db_settings = {
    "host": "127.0.0.1",
    "database": "smart_buyer_db",
    "user": "postgres",
    "password": "De9654",
    "client_encoding": "utf-8",
}

# Connect to the database
conn = psycopg2.connect(**db_settings)
cursor = conn.cursor()

# Fetch distinct city values
cursor.execute("SELECT DISTINCT city FROM public.stores_table")
distinct_cities = cursor.fetchall()

# Create a JSON file with the decoded city values
with open("distinct_cities.json", "w", encoding="utf-8") as json_file:
    json.dump(distinct_cities, json_file, ensure_ascii=False, indent=4)

# Close the database connection
cursor.close()
conn.close()
