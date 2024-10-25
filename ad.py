import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

# Database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'root',  # replace with your MySQL username
    'password': 'my5ql2420',  # replace with your MySQL password
    'database': 'attendance_system'
}

user_role = None
current_user = None

# Subjects for attendance
subjects = ["MATHS 3", "DS", "DBMS", "PYTHON"]

# Global variables for widgets
entry_name = None

# Connect to the database
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Initialize the database table if it doesn't exist
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_name VARCHAR(100) NOT NULL,
        subject VARCHAR(50) NOT NULL,
        total_classes INT NOT NULL,
        classes_attended INT NOT NULL,
        attendance_percentage DECIMAL(5, 2) NOT NULL
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Save attendance report to the database
def save_report(attendance_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO attendance (student_name, subject, total_classes, classes_attended, attendance_percentage)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, attendance_data)
    conn.commit()
    cursor.close()
    conn.close()
    messagebox.showinfo("Success", "Attendance saved successfully!")

# Calculate attendance percentage and save to database (only for teachers)
def calculate_attendance():
    if user_role == 'student':
        messagebox.showerror("Error", "Students cannot add or modify attendance.")
        return

    subject = subject_var.get()
    student_name = entry_student_name.get()

    try:
        total_classes = int(entry_total_classes.get())
        classes_attended = int(entry_classes_attended.get())
        
        if classes_attended > total_classes:
            messagebox.showerror("Error", "Classes attended cannot be more than total classes.")
            return
        
        percentage = (classes_attended / total_classes) * 100
        attendance_data = (student_name, subject, total_classes, classes_attended, round(percentage, 2))
        save_report(attendance_data)
        
        label_result.config(text=f"{student_name}'s attendance for {subject}: {round(percentage, 2)}%")
        
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for classes.")

# View saved attendance report in a table format
def view_report():
    conn = get_db_connection()
    cursor = conn.cursor()
    report_window = tk.Toplevel(window)
    report_window.title("Attendance Report")
    
    tree = ttk.Treeview(report_window, columns=("Student Name", "Subject", "Total Classes", "Classes Attended", "Attendance Percentage"), show='headings')
    tree.heading("Student Name", text="Student Name")
    tree.heading("Subject", text="Subject")
    tree.heading("Total Classes", text="Total Classes")
    tree.heading("Classes Attended", text="Classes Attended")
    tree.heading("Attendance Percentage", text="Attendance Percentage")
    tree.pack(fill=tk.BOTH, expand=True)

    cursor.execute("SELECT * FROM attendance")
    for row in cursor.fetchall():
        if user_role == 'teacher' or (user_role == 'student' and row[1] == current_user):
            tree.insert("", tk.END, values=row[1:])

    scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    cursor.close()
    conn.close()

# Function to handle login
def login():
    global user_role, current_user
    role = role_var.get()
    name = entry_name.get()

    if role == "student" and name:
        user_role = 'student'
        current_user = name
        load_student_interface()
    elif role == "teacher" and name:  # Allow any teacher name
        user_role = 'teacher'
        current_user = name
        load_teacher_interface()
    else:
        messagebox.showerror("Error", "Invalid login details.")

# Function to go back to the login screen
def go_back():
    clear_window()
    load_login_interface()

# Load the student interface after login
def load_student_interface():
    clear_window()
    global label_result, subject_var

    button_back = tk.Button(window, text="Back", command=go_back, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
    button_back.grid(row=0, column=0, padx=10, pady=10)

    label_welcome = tk.Label(window, text=f"Welcome {current_user} (Student)", font=("Arial", 16, "bold"), bg="#F0F8FF")
    label_welcome.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    label_subject = tk.Label(window, text="Select Subject", font=("Arial", 12), bg="#F0F8FF")
    label_subject.grid(row=2, column=0, padx=10, pady=5)
    subject_var = tk.StringVar(value=subjects[0])
    dropdown_subject = tk.OptionMenu(window, subject_var, *subjects)
    dropdown_subject.grid(row=2, column=1, padx=10, pady=5)

    button_view_report = tk.Button(window, text="View My Attendance", command=view_report, bg="#FFC107", fg="black", font=("Arial", 12, "bold"))
    button_view_report.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Load the teacher interface after login
def load_teacher_interface():
    clear_window()
    global entry_student_name, entry_total_classes, entry_classes_attended, label_result, subject_var

    button_back = tk.Button(window, text="Back", command=go_back, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
    button_back.grid(row=0, column=0, padx=10, pady=10)

    label_welcome = tk.Label(window, text="Welcome Teacher", font=("Arial", 16, "bold"), bg="#F0F8FF")
    label_welcome.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    label_subject = tk.Label(window, text="Select Subject", font=("Arial", 12), bg="#F0F8FF")
    label_subject.grid(row=2, column=0, padx=10, pady=5)
    subject_var = tk.StringVar(value=subjects[0])
    dropdown_subject = tk.OptionMenu(window, subject_var, *subjects)
    dropdown_subject.grid(row=2, column=1, padx=10, pady=5)

    label_student_name = tk.Label(window, text="Student Name", font=("Arial", 12), bg="#F0F8FF")
    label_student_name.grid(row=3, column=0, padx=10, pady=5)
    entry_student_name = tk.Entry(window)
    entry_student_name.grid(row=3, column=1, padx=10, pady=5)

    label_total_classes = tk.Label(window, text="Total Classes", font=("Arial", 12), bg="#F0F8FF")
    label_total_classes.grid(row=4, column=0, padx=10, pady=5)
    entry_total_classes = tk.Entry(window)
    entry_total_classes.grid(row=4, column=1, padx=10, pady=5)

    label_classes_attended = tk.Label(window, text="Classes Attended", font=("Arial", 12), bg="#F0F8FF")
    label_classes_attended.grid(row=5, column=0, padx=10, pady=5)
    entry_classes_attended = tk.Entry(window)
    entry_classes_attended.grid(row=5, column=1, padx=10, pady=5)

    button_calculate = tk.Button(window, text="Calculate Attendance", command=calculate_attendance, bg="#2196F3", fg="white", font=("Arial", 12, "bold"))
    button_calculate.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    label_result = tk.Label(window, text="", bg="#F0F8FF")
    label_result.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

    button_view_report = tk.Button(window, text="View All Attendance", command=view_report, bg="#FFC107", fg="black", font=("Arial", 12, "bold"))
    button_view_report.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

# Load the login interface
def load_login_interface():
    clear_window()
    global entry_name, role_var

    label_title = tk.Label(window, text="Attendance System", font=("Arial", 24, "bold"), bg="#F0F8FF")
    label_title.pack(pady=10)

    label_role = tk.Label(window, text="Select Role", font=("Arial", 16), bg="#F0F8FF")
    label_role.pack(pady=5)

    role_var = tk.StringVar(value="student")
    radio_student = tk.Radiobutton(window, text="Student", variable=role_var, value="student", bg="#F0F8FF")
    radio_student.pack(pady=5)
    radio_teacher = tk.Radiobutton(window, text="Teacher", variable=role_var, value="teacher", bg="#F0F8FF")
    radio_teacher.pack(pady=5)

    label_name = tk.Label(window, text="Enter Name", font=("Arial", 12), bg="#F0F8FF")
    label_name.pack(pady=5)
    entry_name = tk.Entry(window)
    entry_name.pack(pady=5)

    button_login = tk.Button(window, text="Login", command=login, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
    button_login.pack(pady=10)

# Clear the window
def clear_window():
    for widget in window.winfo_children():
        widget.destroy()

# Main window
window = tk.Tk()
window.title("Attendance Management System")
window.configure(bg="#F0F8FF")

initialize_database()
load_login_interface()
window.mainloop()
