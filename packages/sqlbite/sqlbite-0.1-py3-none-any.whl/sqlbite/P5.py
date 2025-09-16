# 1. ZeroDivisionError
try:
    num = 10 / 0
except ZeroDivisionError as e:
    print("ZeroDivisionError:", e)

# 2. ValueError
try:
    age = int("twenty")
except ValueError as e:
    print("ValueError:", e)

# 3. IndexError
try:
    lst = [1, 2, 3]
    print(lst[5])
except IndexError as e:
    print("IndexError:", e)

# 4. FileNotFoundError
try:
    with open("no_file.txt", "r") as file:
        data = file.read()
except FileNotFoundError as e:
    print("FileNotFoundError:", e)

# 5. Multiple Except Blocks
try:
    a = int(input("\nEnter a number: "))
    b = int(input("Enter another number: "))
    result = a / b
    print("Result:", result)
except ValueError:
    print("Please enter a valid number.")
except ZeroDivisionError:
    print("Cannot divide by zero.")

# 6. Combined Exceptions
try:
    a = int(input("\nEnter a number: "))
    b = int(input("Enter another number: "))
    print("Result:", a / b)
except (ValueError, ZeroDivisionError):
    print("Invalid value or zero division")

# 7. try–except–else–finally
try:
    x = int(input("\nEnter an even number: "))
    if x % 2 != 0:
        raise ValueError("That's not an even number")
except ValueError as e:
    print("Error:", e)
else:
    print("Even number accepted:", x)
finally:
    print("Finally block always runs.")

# 8. User-defined Exception
class AgeTooSmallError(Exception):
    def __init__(self, message="Age is too small!"):
        super().__init__(message)

try:
    age = int(input("\nEnter your age: "))
    if age < 18:
        raise AgeTooSmallError("You must be at least 18 years old.")
    print("Age accepted.")
except AgeTooSmallError as e:
    print("Custom Error:", e)
