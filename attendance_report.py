from tkinter import *
from tkinter import ttk
import firebase_admin 
from firebase_admin import credentials, storage, firestore, db


config = credentials.Certificate('attendancesystem-d8663-ab876e77f936.json')
firebase_admin.initialize_app(config, {
    'databaseURL': 'https://attendancesystem-d8663-default-rtdb.firebaseio.com'
})
db = firestore.client()
# Reference and Fecth "users" collection
students = db.collection('users').get()
stu_collection = []
for stu in students:
    data = stu.to_dict()
    id = stu.id
    name = data.get('name')
    year = data.get('year')
    batch = data.get('batch')
    stu_collection.append({'id': id, 'name': name, 'year' : year, 'batch' : batch})
print(stu_collection)   

    
def view_report():
    # delete old table 
    tree.delete(*tree.get_children())
    
    # Reference and Fecth the "attendance" collection
    attendance_records = db.collection('attendance')
    # Fetch all documents from attendance
    documents = attendance_records.stream()
    for doc in documents:
        # document id is date
        date = doc.id
        # if user input date is equal to 'date', produce attendance report related to that date
        if dateEntry.get() == date:
            data = doc.to_dict()
            print("Data!!", data)
            print("Date: ", date)
            # Count row numbers
            count = 1
            # Loop attendance data from attendance colleciton
            for id, status in data.items():
                # Loop stu_collection that store data from users collection
                for dict in stu_collection:
                    # if yearEntry value is 'All', Show all records
                    if yearEntry.get() == 'All':
                        # if student id is equal to id from attendance collection, print attendance reports
                        if dict['id'] == id :
                            for key, value in data.items():
                                if key == id:
                                    arrival_time = value[1]
                                    status = value[0]
                                    print("ID:", id, "Name: ", dict['name'], "Year:", dict['year'] , "Batch:", dict['batch'], "Status:", status, "Arrival Time:", arrival_time)
                                    tree.insert('', 'end', text="1", values=( count, dict['name'], dict['year'], dict['batch'], status, arrival_time))
                                    count += 1
                    # if yearEntry value is not 'All', Show records related to the entry value
                    if yearEntry.get() != 'All' :
                        # if student id is equal to id from attendance collection, print attendance reports
                        if dict['id'] == id and dict['year'] == yearEntry.get():
                            for key, value in data.items():
                                if key == id:
                                    arrival_time = value[1]
                                    status = value[0]
                                    print("ID:", id, "Name: ", dict['name'], "Year:", dict['year'] , "Batch:", dict['batch'], "Status:", status, "Arrival Time:", arrival_time)
                                    tree.insert('', 'end', values=( count, dict['name'], dict['year'], dict['batch'], status, arrival_time))
                                    count += 1


# Dropdown List function of all available datesd in attendance collection
def dropdown_date():
    attendance_records = db.collection('attendance')
    documents = attendance_records.stream()
    available_dates = [doc.id for doc in documents]
    dateEntry['values'] = available_dates
    return dateEntry['values']

def dropdown_year():
    year_set = set({'All'})
    for student in stu_collection:
        year = student['year']
        if year is not None:
            year_set.add(year)
    print(year_set)
    yearEntry['values'] = tuple(year_set)


window = Tk()
window.title('attendance report')
window.geometry("800x550")
window.config(bg='#252B48')

frame = Frame(window)
frame.grid(row=4, column=0, columnspan=2, padx=15, pady=5, sticky="nsew" )
# Table scrollbar
scrollbar = ttk.Scrollbar(frame, orient="vertical")
scrollbar.grid(row=0, column=1, sticky='ns')
# Table using Treeview
tree = ttk.Treeview(frame,  column=("c1", "c2", "c3", "c4", "c5", "c6"), show='headings', yscrollcommand=scrollbar.set)
tree.column("# 1", anchor=CENTER, width = "30")
tree.heading("# 1", text="No:")
tree.column("# 2", anchor=CENTER)
tree.heading("# 2", text="Name")
tree.column("# 3", anchor=CENTER)
tree.heading("# 3", text="Academic Year")
tree.column("# 4", anchor=CENTER, width = "50")
tree.heading("# 4", text="Batch")
tree.column("# 5", anchor=CENTER, width = "50")
tree.heading("# 5", text="Status")
tree.column("# 6", anchor=CENTER)
tree.heading("# 6", text="Arrival Time")
tree.grid( row=4, column=0, sticky="nsew")
scrollbar.config(command=tree.yview)

# Date Label
dateLabel = Label(window, text="Date :")
dateLabel.grid(row=1, column=0, padx=(15, 0), pady=5, sticky="w")
# DropDown Lists that contains all available date in attendance records
dateEntry = ttk.Combobox(window)
dateEntry.grid(row=1, column=1, padx=(0, 0), pady=5, sticky="w")
dropdown_date()

# Year Label
yearLabel = Label(window, text="Academic Year :")
yearLabel.grid(row=2, column=0, padx=(15, 0), pady=5, sticky="w")
# DropDown Lists that contains all available values from 'year' column in attendance records
yearEntry = ttk.Combobox(window)
yearEntry.grid(row=2, column=1, padx=(0, 0), pady=5, sticky="w")
dropdown_year()

# Button to "View Attendance Report"
btn = Button(window, text="View Attendance Report", command=view_report)
btn.grid(row=3, column=0, padx=(15, 0), pady=5, sticky="w")

window.mainloop()
