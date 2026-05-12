# face-recognition-attendance-system | Python, OpenCV, Firebase
# Face recognition attendance system, including primary data collection, model training, and real-time pre-launch testing.
# Fine-tuned a VGG16 CNN model on a custom primary dataset, optimizing for accuracy and performance in real-world environmental conditions.

This system includes 3 features.
Student Registration, Face Recognition Attendance Taking and Daily Attendance Report.
There are all together 4 main components.
- Training model written by using VGG16 model in train_model.py
- Fae Recognition attendance taking process is written in face_recognition.py.
- New student registration process is written in student_registeration.py.
- Attendance report feature is written in two files - attendance_records.py and attendance_report.py.
haarcascade_frontalface XML model is used for face detection.
The trained VGG16 model is saved as face_recognition_l6.h5.
Main Python libraries used for the implementation are Open CV for face detection, Keras for face recognition using CNN, tkinder for Python GUI and matplotlib, for visualization training and validation accuracy.
Students’ information are stored in firebase real-time database.
