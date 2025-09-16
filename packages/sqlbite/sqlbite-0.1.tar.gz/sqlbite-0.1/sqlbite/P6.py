import tkinter as tk
from tkinter import font

root = tk.Tk()
root.title("GUI Demo - Fonts, Colors, Layouts & Events")
root.geometry("500x400")
root.configure(bg="lightblue")

label1 = tk.Label(root, text="GUI Demo", 
                  font=("Arial", 20, "bold"), fg="blue", bg="white")
label1.pack(pady=10)

label2 = tk.Label(root, text="Different Font Example", 
                  font=("Courier", 16, "italic"), fg="green", bg="white")
label2.pack(pady=5)


frame = tk.Frame(root, bg="lightgray", padx=10, pady=10)
frame.pack(pady=10)

tk.Label(frame, text="Name", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
entry_name = tk.Entry(frame, font=("Arial", 12))
entry_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Age", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5)
entry_age = tk.Entry(frame, font=("Arial", 12))
entry_age.grid(row=1, column=1, padx=5, pady=5)

label3 = tk.Label(root, text="(This label uses place layout)", font=("Arial", 10), fg="red")
label3.place(x=150, y=250)

def show_info():
    name = entry_name.get()
    age = entry_age.get()
    label_output.config(text=f"Hello {name}, Age: {age}")

btn = tk.Button(root, text="SuBmit", command=show_info, bg="orange", font=("Arial", 12))
btn.pack(pady=20)

label_output = tk.Label(root, text="", font=("Arial", 12), fg="purple", bg="yellow")
label_output.pack()

root.mainloop()