import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import mysql.connector
import re
from datetime import date
import hashlib
# Connect to database
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='YA241@yums',
            database='registration_db'
        )
        if conn.is_connected():
            return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Connection failed:\n{e}.")
        return None

def submit_form():
    name = name_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    contact = Contact_entry.get()
    gender = gender_var.get()
    position = position_combo.get()
    app_date = date_entry.get()
    status = employment_status.get()

    if not (name and email and password and contact and gender and position and app_date and status):
        messagebox.showerror("Error!", "All fields are required.")
        return
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        messagebox.showerror("Error", "Invalid email address")
        return
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
        messagebox.showerror("Error", "Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character.")
        return
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO users(name,email,password,contact,gender,position,application_date,employment_status)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (name, email,hashed_password, contact, gender, position, app_date, status)
            cursor.execute(query, values)
            conn.commit()
            messagebox.showinfo("Success", "Registration successful.")
            display_report()
            name_entry.delete(0, tk.END)
            email_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            Contact_entry.delete(0, tk.END)
            gender_var.set(None)
            position_combo.set('')
            date_entry.set_date(date.today())
            employment_status.set(None)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            conn.close()

def display_report():
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            treeview.delete(*treeview.get_children())
            for row in rows:
                treeview.insert("", "end", values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            conn.close()

def delete_record():
    selected = treeview.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a record to delete.")
        return
    item = treeview.item(selected)
    user_id = item['values'][0]

    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
            conn.commit()
            messagebox.showinfo("Success", "Record deleted successfully.")
            display_report()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            conn.close()

def load_for_edit():
    global editing_id
    selected = treeview.focus()
    if not selected:
        messagebox.showwarning("Select Row", "Please select a record to edit.")
        return

    data = treeview.item(selected)["values"]
    editing_id = data[0]   # remember which record we’re editing

    # fill the entry widgets
    name_entry.delete(0, tk.END)
    name_entry.insert(0, data[1])

    email_entry.delete(0, tk.END)
    email_entry.insert(0, data[2])

    password_entry.delete(0, tk.END)
    password_entry.insert(0, data[3])

    Contact_entry.delete(0, tk.END)
    Contact_entry.insert(0, data[4])

    gender_var.set(data[5])
    position_combo.set(data[6])
    date_entry.set_date(data[7])
    employment_status.set(data[8])

    # Optionally change your Submit button text to “Save”
    button.config(text="Save", command=save_update)
def save_update():
    global editing_id
    if editing_id is None:
        messagebox.showerror("Error", "No record loaded for editing.")
        return

    # grab the (possibly edited) values
    updated_data = (
        name_entry.get(),
        email_entry.get(),
        password_entry.get(),
        Contact_entry.get(),
        gender_var.get(),
        position_combo.get(),
        date_entry.get(),
        employment_status.get(),
    )

    # validation
    if not all(updated_data):
        messagebox.showerror("Error", "All fields are required for update.")
        return
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', updated_data[1]):
        messagebox.showerror("Error", "Invalid email address.")
        return
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$", updated_data[2]):
        messagebox.showerror("Error", "Password must be strong.")
        return
    hashed_password = hashlib.sha256(updated_data[2].encode()).hexdigest()
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
              UPDATE users
              SET name=%s, email=%s, password=%s, contact=%s,
                  gender=%s, position=%s, application_date=%s, employment_status=%s
              WHERE id=%s
            """
            cursor.execute(query, (
                updated_data[0],  # name
                updated_data[1],  # email
                hashed_password,  # hashed password
                #updated_data[2], #password
                updated_data[3],  # contact
                updated_data[4],  # gender
                updated_data[5],  # position
                updated_data[6],  # date
                updated_data[7],  # employment status
                editing_id
            ))
            conn.commit()
            messagebox.showinfo("Success", "Record updated successfully.")
            display_report()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            conn.close()

    # reset
    editing_id = None
    button.config(text="SUBMIT", command=submit_form)
    for w in (name_entry, email_entry, password_entry, Contact_entry):
        w.delete(0, tk.END)
    gender_var.set(None)
    position_combo.set('')
    date_entry.set_date(date.today())
    employment_status.set(None)

def search_record():
    keyword = search_entry.get()
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM users WHERE name LIKE %s OR email LIKE %s"
            like_keyword = f"%{keyword}%"
            cursor.execute(query, (like_keyword, like_keyword))
            rows = cursor.fetchall()
            treeview.delete(*treeview.get_children())
            if not rows:
                messagebox.showinfo("No Results", "No matching records found.")
            for row in rows:
                treeview.insert("", "end", values=row)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            conn.close()

root = tk.Tk()
root.title("Job Application Form")
root.geometry("1000x1000")
root.resizable(False, False)

bg_img = Image.open("download.jpeg")
bg_img = bg_img.resize((1000, 1000), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_img)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
# Title Label
title_label = tk.Label(root, text="Job Application Form", font=("Arial", 14, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="w")

#Name
Namelabel = tk.Label(root, text="Name:", font=("Arial", 10))
Namelabel.grid(column=0, row=1, pady=5, padx=10, sticky="w")

name_entry = tk.Entry(root, width=40)
name_entry.grid(column=1, row=1, pady=5, padx=10, sticky="w")


# Email Label and Entry
emaillabel = tk.Label(root, text="Email:", font=("Arial", 10))
emaillabel.grid(column=0, row=2, pady=5, padx=10, sticky="w")
errorlabel=tk.Label(root, text="")
errorlabel.grid(column=0, row=3, pady=5)
email_entry = tk.Entry(root, width=40)
email_entry.grid(column=1, row=2, pady=5, padx=10, sticky="w")

# Password Label and Entry
passwordlabel = tk.Label(root, text="Password:", font=("Arial", 10))
passwordlabel.grid(column=0, row=3, pady=5, padx=10, sticky="w")

password_entry = tk.Entry(root, show="*", width=40)
password_entry.grid(column=1, row=3, pady=5, padx=10, sticky="w")

#contact
Contactlabel = tk.Label(root, text="Contact:", font=("Arial", 10))
Contactlabel.grid(column=0, row=4, pady=5, padx=10, sticky="w")

Contact_entry = tk.Entry(root, width=40)
Contact_entry.grid(column=1, row=4, pady=5, padx=10, sticky="w")

#Gender
genderlabel = tk.Label(root, text="Gender:", font=("Arial", 10))
genderlabel.grid(column=0, row=5, pady=5, padx=10, sticky="w")

gender_var = tk.StringVar()  # Holds selected value

frame_gender = tk.Frame(root)
frame_gender.grid(column=1, row=5, padx=10, pady=5, sticky="w")

genders = ["Male", "Female", "Other"]
for idx, gender in enumerate(genders):
    ttk.Radiobutton(frame_gender, text=gender, variable=gender_var, value=gender).grid(column=idx, row=0, padx=5)
    

# Position Applying For (Dropdown)
dropDown_label = tk.Label(root, text="What position are you applying for:", font=("Arial", 10))
dropDown_label.grid(column=0, row=6, pady=5, padx=10, sticky="w")

position_combo = ttk.Combobox(root, values=["Software Engineer", "Data Analyst", "Project Manager", "Designer"], width=37, state="readonly")
position_combo.grid(column=1, row=6, padx=10, pady=5, sticky="w")

# Date Label and Entry
date_label = tk.Label(root, text="Date:", font=("Arial", 10))
date_label.grid(column=0, row=7, pady=5, padx=10, sticky="w")

date_entry = DateEntry(root, width=40,borderwidth=2, date_pattern='yyyy/mm/dd')
date_entry.grid(column=1, row=7, padx=10, pady=5, sticky="w")

# Employment Status
status_label = tk.Label(root, text="What is your current employee status:", font=("Arial", 10))
status_label.grid(column=0, row=8, pady=5, padx=10, sticky="w")

employment_status = tk.StringVar() #holds the selected option.
frame_status = tk.Frame(root) #groups all radio buttons.
frame_status.grid(column=1, row=8, padx=10, pady=5, sticky="w")

statuses = ["Employed", "Unemployed", "Self-Employed", "Student"]
for idx, status in enumerate(statuses): #creates four radio buttons dynamically.
    ttk.Radiobutton(frame_status, text=status, variable=employment_status, value=status).grid(column=idx, row=0, padx=5)

button = tk.Button(root, text="SUBMIT", font=("Arial", 12, "bold"), bg="blue", fg="white", width=9, command=submit_form)
button.grid(column=0, row=9, columnspan=2, pady=8)

report_btn = tk.Button(root, text="Report", font=("Arial", 12, "bold"), bg="blue", fg="white", width=9, command=display_report)
report_btn.grid(row=10, column=0, columnspan=2, pady=5)

# Treeview setup
columns = ("ID", "Name", "Email", "Password", "Contact", "Gender", "Position", "Date", "Employment Status")
treeview = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    treeview.heading(col, text=col)
    treeview.column(col, width=100)
treeview.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

treeview_scroll = ttk.Scrollbar(root, orient="vertical", command=treeview.yview)
treeview.configure(yscrollcommand=treeview_scroll.set)
treeview_scroll.grid(row=11, column=2, sticky="ns")

# Action Buttons
edit_label=tk.Label(root,text="Search by name or email:")
edit_label.grid(row=12,column=0,pady=5, padx=10, sticky="w")
edit_btn = tk.Button(root, text="Search", bg="green", fg="white", width=9, command=search_record)
edit_btn.grid(row=12, column=0, pady=5)

delete_btn = tk.Button(root, text="Delete", bg="red", fg="white", width=9, command=delete_record)
delete_btn.grid(row=12, column=1, pady=5)

search_entry = tk.Entry(root, width=30)
search_entry.grid(row=13, column=0, padx=10, pady=5)

search_btn = tk.Button(root, text="Edit", bg="purple", fg="white", width=9, command=load_for_edit)
search_btn.grid(row=13, column=1, pady=5)

display_report()
root.mainloop()
