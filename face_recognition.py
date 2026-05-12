import cv2
import numpy as np
from keras.models import load_model
from tkinter import messagebox
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from tkinter import *
import os, sys
import subprocess

window = Tk()
window.title('Face Recognition Attendance System')
window.geometry("250x150")
window.config(bg='#252B48')

config = credentials.Certificate('attendancesystem-d8663-ab876e77f936.json')
firebase_admin.initialize_app(config, {
    'databaseURL': 'https://attendancesystem-d8663-default-rtdb.firebaseio.com'
})
db = firestore.client()
# Reference and Fecth the "users" collection
users = db.collection('users').get()
user_collection = []
for user in users:
    data = user.to_dict()
    id = user.id
    name = data.get('name')
    year = data.get('year')
    batch = data.get('batch')
    user_collection.append({'id': id, 'name': name, 'year' : year, 'batch' : batch})

    
def recognition():
    global user_id
    # Load the face cascade XML file
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') 
    # Load the VGG16 fine-tuned model
    face_recognition_model = load_model('face_recognition_l6.h5') 
    # Load the image folder ( Students ID ) names for recognized faces
    train_data_dir = '../images/images/train_images'
    label_names = os.listdir(train_data_dir)
    # Capture Video 
    video_capture = cv2.VideoCapture(0) 
    # Minimum Threshold Value for Predicting Face
    threshold = 0.75
    attempt = 0
    prediction_list = [] # Store prediction label and prediction probability 
    status = False
    while True:
        if attempt < 20:
            attempt += 1
            # Read the frame via webcam, flip the fram horizontall,y convert to grayscale and detect faces
            ret, frame = video_capture.read()
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Initialize a list to store all predictions for each face
            face_predictions = []
            # Loop over detected faces
            for (x, y, w, h) in faces:
                # Extract the face region from the frame
                face = frame[y:y + h, x:x + w]
                # Preprocess the face image for recognition
                face = cv2.resize(face, (224, 224))     # Resize The image
                face = face / 255.0                     # Normalization to make each pixel values to be within value - 0 - 1
                face = np.expand_dims(face, axis=0)

                # face recognition using trained model
                predictions = face_recognition_model.predict(face)
                predicted_label = np.argmax(predictions)
                # Display probabilities for all labels
                for i, probability in enumerate(predictions[0]):
                    label = label_names[i]
                    for data in user_collection:
                        if label == data['id']:
                            label_name = data['name']
                            break
                    print(label + ' - ' + label_name + ' : {:.2%}'.format(probability))
                    # Get  predicted probability for the predicted label
                    predicted_probability = predictions[0][predicted_label]
                    # Store the prediction in the list
                    face_predictions.append((label_names[predicted_label], predicted_probability))

                for data in user_collection:
                    if label_names[predicted_label] == data['id']:
                        label_name = data['name']
                        # Draw a rectangle around the face and display the label
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, label_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        break
            # Show the best accurate predicted label
            if len(face_predictions) > 0:
                # Find the maximum predicted probability
                best_prediction = max(face_predictions, key=lambda x: x[1])
                best_label = best_prediction[0]
                for data in user_collection:
                    if best_label == data['id']:
                        label_name = data['name']
                        break
                if best_prediction[1] > threshold:
                    print('Best Accurate Prediction:', label_name, ' :' , best_prediction[1]*100 , '%')
                    # Store prediction label and probability in the list for each attempts
                    prediction_list.append((best_label, label_name, best_prediction[1]*100))
                else:
                    print('Unknown')
            # Display the resulting frame
            cv2.imshow('Face Recognition', frame)

        elif attempt >= 20:
            print(prediction_list)
            correct_label = []
            tmp_unique_label = set([i[0] for i in prediction_list])
            for i in tmp_unique_label:
                tmp_label = i
                tmp_name = i
                tmp_value = 0.0
                count = 0
                for j in prediction_list:
                    if i == j[0]:
                        count += 1
                        tmp_label = j[0]
                        tmp_name = j[1]
                        tmp_value = tmp_value + j[2]
                # avg_value = tmp_value / count
                avg_value = tmp_value / 20
                correct_label.append((tmp_label, tmp_name, avg_value))
                # print(tmp_label + " " + tmp_name, " ", str(avg_value))
            #print("Possible Prediction : ", correct_label)
            if correct_label:
                # Find the highest prediction probability
                highest_prediction = max(correct_label, key=lambda x: x[2])
                user_id, user_name, prob = highest_prediction
                if prob >= threshold * 100:
                    print("Most Possible Prediction : ", user_name, " : " , prob, "%")
                    message = f"Most Possible Prediction - {user_name} - {prob:.2f}%"
                    message_label = Label(window, text=message)
                    message_label.pack()
                    exit_btn = Button(window, text="Exit", command=exit)
                    exit_btn.pack()
                    continue_btn = Button(window, text="Continue", command=Continue)
                    continue_btn.pack()
                    window.mainloop()
                    status = 'pending'
                    print("Attendance Successfully Taken For Recognized Student...")
                    return "Most Possible Prediction : ", user_name, " : " , prob, "%"
                    break  
                else: 
                    message = f"Unknown Face - Please Try Again or Register First. "
                    message_label = Label(window, text=message)
                    message_label.pack()
                    btn = Button(window, text="Try Again", command=try_again)
                    btn.pack()
                    exit_btn = Button(window, text="Exit", command=exit)
                    exit_btn.pack()
                    window.mainloop()
                    return "Unknown Face - Please Try Again or Register First."
                    break 
            else:
                status = 'fail'
                label = Label(window, text="No Input Detected or Nothing is predicted. Please Try Again ")
                label.pack()
                btn = Button(window, text="Try Again", command=try_again)
                btn.pack()
                window.mainloop()
                break
    
        # Break the loop if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release the webcam and close OpenCV windows
    video_capture.release()
    cv2.destroyAllWindows()

    if status == False:
        messagebox.showinfo("Fail", "Unknown Person - Please Try Again or Register First.")


def Continue():
    # Give attendance to Recognized Face 
    attendance_records = db.collection('attendance').get()
    tdyDate = datetime.now().date().isoformat()
    record_found = False
    
    for r in attendance_records:
        # Attendance Record Date
        record_date = r.id
        
        # Check first - whether current date exists in attendace record
        if tdyDate == record_date:
            # Fetch attendances for today date
            data = r.to_dict()
            if user_id in data:
                # Record 'present for current user id
                current_time = datetime.now().strftime("%H:%M:%S")
                data[user_id] = ['present', current_time]
                r.reference.update(data)
                record_found = True
                break
    if not record_found:
        # Execute the attendance_records file to create a new attendance record with tdy date
        subprocess.run(["python", "attendance_records.py"])
        attendance_records = db.collection('attendance').get()
        for r in attendance_records:
            # Attendance Record Date
            record_date = r.id
            # Check first - whether current date exists in attendace record
            if tdyDate == record_date:
                # Fetch attendances for today date
                data = r.to_dict()
                if user_id in data:
                    # Record 'present for current user id
                    current_time = datetime.now().strftime("%H:%M:%S")
                    data[user_id] = ['present', current_time]
                    r.reference.update(data)
                    record_found = True
                    break

    status = True
    messagebox.showinfo("Success", "Successful Recognition")
    window.quit()
    

def exit():
    window.quit()


def try_again():
    os.execv(sys.executable, ['python'] + sys.argv)



if __name__ == "__main__":
    recognition()

