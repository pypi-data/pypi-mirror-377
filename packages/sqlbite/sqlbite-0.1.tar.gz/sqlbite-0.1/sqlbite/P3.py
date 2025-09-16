import time, threading

def print_numbers():
    for i in range(1, 6):
        print(f"[Task 1] Number: {i}")
        time.sleep(1)

def print_letters():
    for ch in ['A','B','C','D','E']:
        print(f"[Task 2] Letter: {ch}")
        time.sleep(1.5)

print("Multithreading Execution")
t1 = threading.Thread(target=print_numbers)
t2 = threading.Thread(target=print_letters)

t1.start()
t2.start()

t1.join()
t2.join()

print("Multithreading completed")