import os
from tkinter import *
from PIL import ImageTk, Image
import firebase_admin
from firebase_admin import credentials, storage, firestore, db
import numpy as np
import json
import tkinter.filedialog as fd


config = credentials.Certificate('attendancesystem-d8663-ab876e77f936.json')
firebase_admin.initialize_app(config, {
    'databaseURL': 'https://attendancesystem-d8663-default-rtdb.firebaseio.com'
})


def check_fields(data, required_fields):
    fields = []

    for field in required_fields:
        if not data.get(field):
            fields.append(field)

    if fields:
        missing_fields = ', '.join(fields)
        return False, f"Fill Required Fields - {missing_fields} to Register !"
    else:
        return True, "All required fields are filled."


required_fields = ['name', 'year', 'gender', 'nationality', 'batch', 'dob', 'address', 'guardianName', 'phoneNumber']

def register_face():
    fileName = entry_dict['nameEntry'].get()
    db = firestore.client()
    data = {
        'name': entry_dict['nameEntry'].get(),
        'year': entry_dict['yearEntry'].get(),
        'gender' : entry_dict['genderEntry'].get(),
        'nationality' : entry_dict['nationalityEntry'].get(),
        'batch' : entry_dict['batchEntry'].get(), 
        'dob' : entry_dict['dobEntry'].get(),
        'address' : entry_dict['addressEntry'].get(),
        'guardianName' : entry_dict['guardianEntry'].get(),
        'phoneNumber' : entry_dict['phNumEntry'].get()   
    }
    is_valid, message = check_fields(data, required_fields)

    if is_valid:
        new_user_ref = db.collection('users').add(data)
        user_id = new_user_ref[1].id

        num_training_images = 12
        num_validate_images = 4
        train_images_folder = os.path.join('images/train_images', user_id)
        os.makedirs(train_images_folder, exist_ok=True)
        validate_images_folder = os.path.join('images/validate_images', user_id)
        os.makedirs(validate_images_folder, exist_ok=True)
        # Save uploaded images into the folder with student ID
        for i, img_path in enumerate(selected_images):
            img = Image.open(img_path)
            image_name = f'{fileName}_{i + 1}.jpg'
            image_path = os.path.join(train_images_folder if i < num_training_images else validate_images_folder,  image_name)
            img.save(image_path)

            # Flip images horizontally and save
            mirror_img = img.transpose(Image.FLIP_LEFT_RIGHT)
            mirror_img_name = f'{fileName}_{i + 1}_mirror.jpg'
            mirror_image_path = os.path.join(train_images_folder if i < num_training_images else validate_images_folder, mirror_img_name)
            mirror_img.save(mirror_image_path)

        message_label = Label(window, text="Registered Student Successfully")
        message_label.grid()
    # if required fields are blank, show error message
    else:
        message_label = Label(window, text = message, wraplength= 450)
        message_label.grid(row=14, column=0 , padx=15, pady=5, sticky = 'nsew')


def exit():
    window.destroy()


def label_entry(var, txt, r):
    # Label
    label = Label(window, text=txt, anchor = "center")
    label.grid(row=r, column=0, padx=15, pady=5, sticky="nsew")
    # Entry
    entry = Entry(window)
    entry.grid(row=r, column=1, padx=15, pady=5, sticky="nsew")
    # Initialize the Entry value into entry_dict[var]
    entry_dict[var] = entry


def upload_images():
    files = fd.askopenfilenames(parent=window, title='Upload 16 Images')
    selected_image_names = [os.path.basename(file) for file in files]
    selected_image_text = "\n".join(selected_image_names)
    selectedImages = Label(window, text=selected_image_text, wraplength=500, anchor='w')
    selectedImages.grid(row=11, column=0, padx=15, pady=5, sticky="nsew")

    # Save selected images into global variable
    global selected_images
    selected_images = files


window = Tk()
window.title('Students Registration')
window.geometry("550x650")
window.config(bg='#252B48')
window.grid_columnconfigure((0, 1), weight=1)
# Dictionary to store entry values
entry_dict = {}

def gui():
    message_label = Label(window, text="Students Registration for Attendance System", anchor = "center")
    message_label.grid(row=0, column=0, columnspan=2, padx= 15, pady=5, sticky="nsew")

    label_entry('nameEntry', 'Name :', 1)
    label_entry('yearEntry', 'Academic Year :', 2)
    label_entry('genderEntry', 'Gender :', 3)
    label_entry('nationalityEntry', 'Nationality :', 4)
    label_entry('batchEntry', 'Batch :', 5)
    label_entry('dobEntry', 'Date of Birth :', 6)
    label_entry('addressEntry', 'Address :', 7)
    label_entry('guardianEntry', 'Guardian Name :', 8)
    label_entry('phNumEntry', 'Phone Number :', 9)

    message_label = Label(window, text="", anchor = "center")
    message_label.grid(row=13, column=0, columnspan=2, padx= 15, pady=5, sticky="nsew")
    
    imgLabel = Label(window, text="Upload 16 Portrait Images" , anchor = "center")
    imgLabel.grid(row=10, column=0, padx=15, pady=5, sticky="nsew")

    upload_images_btn = Button(window, text="Select 16 Images", command=upload_images)
    upload_images_btn.grid(row=10, column=1, padx=15, pady=5, sticky="nsew")

    register_btn = Button(window, text="Register", command=register_face)
    register_btn.grid(row=12, column=0 , padx=15, pady=5, sticky="nsew")

    exit_btn = Button(window, text="Exit", command=exit)
    exit_btn.grid(row=12, column=1, padx=15, pady=5, sticky="nsew")



if __name__ == "__main__":
    gui()
    window.mainloop()

