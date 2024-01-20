import mysql.connector
import hashlib
import itertools

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'Hashing'
}

# Function to generate MD5 hash
def generate_md5(value):
    return hashlib.md5(value.encode()).hexdigest()

# Function to insert data into the MySQL table, handle duplicates
def insert_data(cursor, plain_text, md5_hash, duplicate_file):
    try:
        insert_query = "INSERT INTO md5_4char_part1 (`key`, `md5`) VALUES (%s, %s)"
        cursor.execute(insert_query, (plain_text, md5_hash))
        connection.commit()
    except mysql.connector.Error as err:
        if err.errno == 1062:  # MySQL error code for duplicate entry
            print(f"Duplicate entry found: KEY={plain_text}")
            with open(duplicate_file, 'a') as duplicate_file:
                duplicate_file.write(plain_text + '\n')
        else:
            print("Error:", err)

# Function to retrieve the last inserted id and its corresponding key
def get_last_inserted_id_and_key(cursor):
    select_query = "SELECT id, `key` FROM md5_4char_part1 ORDER BY id DESC LIMIT 1"
    cursor.execute(select_query)
    result = cursor.fetchone()
    return result if result else (0, "")

# Establish MySQL connection
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Retrieve the last inserted id and key
last_inserted_id, last_inserted_key = get_last_inserted_id_and_key(cursor)

# Define characters for generating combinations
uppercase_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
lowercase_letters = 'abcdefghijklmnopqrstuvwxyz'
numbers = '0123456789'
symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?/ "\'\\'

# Generate all possible combinations of length 3
combinations = itertools.product(uppercase_letters + lowercase_letters + numbers + symbols, repeat=4)

# File to log duplicate entries
duplicate_file = 'duplicate.txt'

# Iterate through combinations and insert into the database
for combination in combinations:
    plain_text = ''.join(combination )

    # Skip values until reaching the last inserted id
    if plain_text <= last_inserted_key:
        continue

    md5_hash = generate_md5(plain_text)
    insert_data(cursor, plain_text, md5_hash, duplicate_file)

# Close the cursor and connection
cursor.close()
connection.close()
