import psycopg2
import csv

conn = psycopg2.connect(
    dbname="lab10",
    user="postgres",
    password="dfgh4639ryei0288ksk4",  # ← enter your own password
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Create table
cur.execute("""
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50),
        phone VARCHAR(20)
    );
""")
conn.commit()

# Load from CSV
def load_from_csv():
    with open('psycopg2.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 2:
                cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (row[0], row[1]))
    conn.commit()
    print("CSV has been loaded!")

# Manual entry
def insert_manually():
    name = input("Name: ")
    phone = input("Phone number: ")
    cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    print("Entry added!")

# Update entry
def update_entry():
    name = input("Which name do you want to update? ")
    new_phone = input("New phone number: ")
    cur.execute("UPDATE phonebook SET phone = %s WHERE name = %s", (new_phone, name))
    conn.commit()
    print("Entry updated!")

# Search
def query_data():
    filter_name = input("Search by name: ")
    cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s", ('%' + filter_name + '%',))
    results = cur.fetchall()
    for row in results:
        print(row)

# Delete entry
def delete_entry():
    name = input("Whom do you want to delete (name): ")
    cur.execute("DELETE FROM phonebook WHERE name = %s", (name,))
    conn.commit()
    print("Entry deleted!")

# Menu
while True:
    print("\n===== PHONEBOOK MENU =====")
    print("1. Load from CSV")
    print("2. Manual entry")
    print("3. Update entry")
    print("4. Search")
    print("5. Delete entry")
    print("0. Exit")

    choice = input("Choose: ")
    if choice == "1":
        load_from_csv()
    elif choice == "2":
        insert_manually()
    elif choice == "3":
        update_entry()
    elif choice == "4":
        query_data()
    elif choice == "5":
        delete_entry()
    elif choice == "0":
        break
    else:
        print("Invalid choice!")

cur.close()
conn.close()
