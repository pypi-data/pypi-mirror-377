import datetime

def main():
    while True:
        print("\n=== Date & Time Application ===")
        print("1. Show current date and time")
        print("2. Find day of the week for a given date")
        print("3. Find difference between two dates")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            now = datetime.datetime.now()
            print("\nCurrent Date and Time:", now.strftime("%Y-%m-%d %H:%M:%S"))
            print("Today's Date:", now.date())
            print("Current Time:", now.time().strftime("%H:%M:%S"))

        elif choice == '2':
            date_str = input("Enter a date (YYYY-MM-DD): ")
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                print("That day is:", date_obj.strftime("%A"))
            except ValueError:
                print("Invalid date format! Please enter in YYYY-MM-DD format.")

        elif choice == '3':
            date1_str = input("Enter the first date (YYYY-MM-DD): ")
            date2_str = input("Enter the second date (YYYY-MM-DD): ")
            try:
                date1 = datetime.datetime.strptime(date1_str, "%Y-%m-%d")
                date2 = datetime.datetime.strptime(date2_str, "%Y-%m-%d")
                difference = abs((date2 - date1).days)
                print(f"Difference between {date1_str} and {date2_str} is {difference} days.")
            except ValueError:
                print("Invalid date format! Please enter in YYYY-MM-DD format.")

        elif choice == '4':
            print("Exiting... Thank you for using the app!")
            break

        else:
            print("Invalid choice! Please select from 1 to 4.")

if __name__ == "__main__":
    main()
