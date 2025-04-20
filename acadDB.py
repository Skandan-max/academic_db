import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import mysql.connector
import csv

# This is the DB configuration (configure this as per your setup)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_db_password",
    database="college"
)
cursor = db.cursor()

def update_tree(tree_widget, data, columns):
    tree_widget.delete(*tree_widget.get_children())
    tree_widget["columns"] = columns
    tree_widget["show"] = "headings"
    for col in columns:
        tree_widget.heading(col, text=col + " 🔽", command=lambda _col=col: treeview_sort_column(tree_widget, _col, False))
        tree_widget.column(col, width=120)
    for row in data:
        tree_widget.insert("", tk.END, values=row)

def treeview_sort_column(tv, col, reverse):
    try:
        data = [(tv.set(k, col), k) for k in tv.get_children('')]
        data.sort(key=lambda t: (int(t[0]) if t[0].isdigit() else t[0]), reverse=reverse)
        for index, (val, k) in enumerate(data):
            tv.move(k, '', index)
        tv.heading(col, text=f"{col} {'🔽' if reverse else '🔼'}",
                   command=lambda: treeview_sort_column(tv, col, not reverse))
    except Exception as e:
        messagebox.showerror("Sort Error", str(e))

def export_to_csv():
    if not tree.get_children():
        messagebox.showinfo("No Data", "Nothing to export.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(tree["columns"])
        for row in tree.get_children():
            writer.writerow(tree.item(row)["values"])
    messagebox.showinfo("Success", f"Data exported to {file_path}")

def view_departments():
    try:
        cursor.execute("SELECT * FROM department")
        rows = cursor.fetchall()
        update_tree(tree, rows, [desc[0] for desc in cursor.description])
        export_button.pack()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def view_courses():
    try:
        cursor.execute("SELECT * FROM course")
        rows = cursor.fetchall()
        update_tree(tree, rows, [desc[0] for desc in cursor.description])
        export_button.pack()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def view_sem2_courses_2006():
    try:
        cursor.execute("SELECT * FROM teaching WHERE sem = '2' AND year = 2006")
        rows = cursor.fetchall()
        update_tree(tree, rows, [desc[0] for desc in cursor.description])
        export_button.pack()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_course():
    deptId = simpledialog.askstring("Input", "Enter Department ID:")
    courseId = simpledialog.askstring("Input", "Enter Course ID:")
    empId = simpledialog.askstring("Input", "Enter Teacher ID:")
    classRoom = simpledialog.askstring("Input", "Enter Classroom:")

    cursor.execute("SELECT * FROM course WHERE courseId = %s AND deptNo = %s", (courseId, deptId))
    if cursor.fetchone() is None:
        if messagebox.askyesno("Add Course", "Course ID doesn't exist. Add new course?"):
            course_name = simpledialog.askstring("Input", "Enter Course Name:")
            credits = simpledialog.askinteger("Input", "Enter Credits:")
            cursor.execute(
                "INSERT INTO course (courseId, cname, credits, deptNo) VALUES (%s, %s, %s, %s)",
                (courseId, course_name, credits, deptId)
            )
            db.commit()
        else:
            return

    cursor.execute("SELECT * FROM professor WHERE empId = %s AND deptNo = %s", (empId, deptId))
    if cursor.fetchone() is None:
        if messagebox.askyesno("Add Professor", "Professor doesn't exist. Add new professor?"):
            prof_name = simpledialog.askstring("Input", "Enter Professor Name:")
            sex = simpledialog.askstring("Input", "Enter Sex (M/F):")
            start_year = simpledialog.askinteger("Input", "Enter Start Year:")
            phone = simpledialog.askstring("Input", "Enter Phone:")
            cursor.execute(
                "INSERT INTO professor (empId, name, sex, startYear, deptNo, phone) VALUES (%s, %s, %s, %s, %s, %s)",
                (empId, prof_name, sex, start_year, deptId, phone)
            )
            db.commit()
        else:
            return

    cursor.execute(
        "INSERT INTO teaching (empId, courseId, sem, year, classRoom) VALUES (%s, %s, 2, 2006, %s)",
        (empId, courseId, classRoom)
    )
    db.commit()
    messagebox.showinfo("Success", "Course added for Sem 2, 2006")

def get_all_prereqs(courseId, visited=None):
    if visited is None:
        visited = set()
    if courseId in visited:
        return set()
    visited.add(courseId)
    cursor.execute("SELECT preReqCourse FROM preRequisite WHERE courseId = %s", (courseId,))
    prereqs = cursor.fetchall()
    all_prereqs = set()
    for (preReq,) in prereqs:
        all_prereqs.add(preReq)
        all_prereqs.update(get_all_prereqs(preReq, visited))
    return all_prereqs

def enroll_student():
    rollNo = simpledialog.askstring("Input", "Enter Student Roll No:")
    courseId = simpledialog.askstring("Input", "Enter Course ID to Enroll:")

    cursor.execute("SELECT * FROM student WHERE rollNo = %s", (rollNo,))
    if cursor.fetchone() is None:
        messagebox.showerror("Error", "Student does not exist.")
        return

    cursor.execute("SELECT * FROM teaching WHERE courseId = %s AND sem = '2' AND year = 2006", (courseId,))
    if cursor.fetchone() is None:
        messagebox.showerror("Error", "Course is not taught in Sem 2 of 2006")
        return

    prereqs = get_all_prereqs(courseId)
    for preReq in prereqs:
        cursor.execute("SELECT * FROM enrollment WHERE rollNo = %s AND courseId = %s", (rollNo, preReq))
        if cursor.fetchone() is None:
            messagebox.showerror("Error", f"Missing prerequisite: {preReq}")
            return

    cursor.execute("""
        INSERT INTO enrollment (rollNo, courseId, sem, year, grade) 
        VALUES (%s, %s, '2', 2006, '-')
    """, (rollNo, courseId))
    db.commit()
    messagebox.showinfo("Success", f"{rollNo} enrolled in {courseId}")

root = tk.Tk()
root.title("Academic Database")
root.geometry("1000x600")

header_frame = tk.Frame(root, bg="lightblue", pady=10)
header_frame.pack(fill=tk.X)

header_label = tk.Label(header_frame, text="   Academic Database", font=("Helvetica", 20), bg="lightblue")
header_label.pack(side=tk.LEFT, expand=True)

exit_button = tk.Button(header_frame, text="Exit", command=root.quit, font=("Helvetica", 12), bg="red", fg="white")
exit_button.pack(side=tk.RIGHT, padx=10)

frame = tk.Frame(root)
frame.pack(pady=20)

row1 = tk.Frame(frame)
row1.pack(pady=5)

row1.grid_columnconfigure(0, weight=1)
row1.grid_columnconfigure(1, weight=1)

tk.Button(row1, text="Add a Course to sem 2 of 2006", width=30, command=add_course).pack(side=tk.LEFT, padx=10)
tk.Button(row1, text="Enroll Student in a course", width=30, command=enroll_student).pack(side=tk.LEFT, padx=10)

row2 = tk.Frame(frame)
row2.pack(pady=5)
row2.grid_columnconfigure(0, weight=1)
row2.grid_columnconfigure(1, weight=1)
row2.grid_columnconfigure(2, weight=1)

tk.Button(row2, text="View Departments", width=25, command=view_departments).pack(side=tk.LEFT, padx=10)
tk.Button(row2, text="View Courses", width=25, command=view_courses).pack(side=tk.LEFT, padx=10)
tk.Button(row2, text="View Sem 2 Courses (2006)", width=25, command=view_sem2_courses_2006).pack(side=tk.LEFT, padx=10)

tree = ttk.Treeview(root)
tree.pack(fill=tk.BOTH, expand=True, pady=20)

export_button = tk.Button(root, text="Export to CSV", bg="lightblue", font=("Helvetica", 11), command=export_to_csv)
export_button.pack(pady=10)
export_button.pack_forget()

footer_frame = tk.Frame(root, bg="lightblue", pady=5)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

footer_label = tk.Label(footer_frame, text="CS3700, Group 4", font=("Helvetica", 12), bg="lightblue")
footer_label.pack(side=tk.TOP, expand=True)

footer_label2 = tk.Label(footer_frame, text="Assignment 4", font=("Helvetica", 10), bg="lightblue")
footer_label2.pack(side=tk.TOP, expand=True)

style = ttk.Style()
style.configure("Treeview", font=("Helvetica", 11), rowheight=30)

root.mainloop()

