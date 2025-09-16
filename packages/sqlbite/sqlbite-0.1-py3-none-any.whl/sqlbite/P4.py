import sqlite3

# --- Database Functions ---
def connect_to_database(db_name="College.db"):
    conn = sqlite3.connect(db_name)
    print("Connected to database successfully.")
    return conn

def create_table(conn):
    conn.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        grade TEXT
    )
    ''')
    conn.commit()
    print("Table 'students' created successfully.")

def drop_table(conn):
    conn.execute('DROP TABLE IF EXISTS students')
    conn.commit()
    print("Table 'students' dropped successfully.")

def insert_data(conn, name, age, grade):
    conn.execute('INSERT INTO students (name, age, grade) VALUES (?, ?, ?)',
                 (name, age, grade))
    conn.commit()
    print(f"Inserted student: {name}, Age: {age}, Grade: {grade}")

def update_data(conn, student_id, new_grade):
    conn.execute('UPDATE students SET grade=? WHERE id=?',
                 (new_grade, student_id))
    conn.commit()
    print(f"Updated student ID {student_id} to grade {new_grade}")

def show_all_students(conn):
    rows = conn.execute("SELECT * FROM students").fetchall()
    print("\nAll students:")
    if not rows:
        print("(No records found)")
    for row in rows:
        print(row)

if __name__ == "__main__":
    conn = connect_to_database()
    create_table(conn)

    while True:
        print("\n--- MENU ---")
        print("1. Insert Student")
        print("2. Update Student Grade")
        print("3. Show All Students")
        print("4. Drop Table")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            name = input("Enter student name: ")
            while True:
                age_input = input("Enter age: ")
                if age_input.isdigit():
                    age = int(age_input)
                    break
                else:
                    print("Please enter a valid age.")
            grade = input("Enter grade: ")
            insert_data(conn, name, age, grade)

        elif choice == "2":
            while True:
                student_id_input = input("Enter student ID to update: ")
                if student_id_input.isdigit():
                    student_id = int(student_id_input)
                    break
                else:
                    print("Please enter a valid numeric ID.")
            new_grade = input("Enter new grade: ")
            update_data(conn, student_id, new_grade)

        elif choice == "3":
            show_all_students(conn)

        elif choice == "4":
            confirm = input("Are u sure u want to drop the table (y/n: ")
            if confirm.lower() == "yes":
                drop_table(conn)
            else:
                print("Drop table cancelled.")

        elif choice == "5":
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 5.")

    conn.close()
    print("Database connection closed.")
