from datetime import datetime
import firebase_admin
from firebase_admin import credentials, storage, firestore, db

config = credentials.Certificate('attendancesystem-d8663-ab876e77f936.json')
firebase_admin.initialize_app(config, {
    'databaseURL': 'https://attendancesystem-d8663-default-rtdb.firebaseio.com'
})

db = firestore.client()
currentDate = datetime.now().date().isoformat()
print("date" , currentDate)
# Set current date as document ID
attendance_ref = db.collection('attendance').document(currentDate)

data = {}

# Reference and Fecth the "users" collection
users = db.collection('users').get()
for user in users:
    id = user.id
    # Add All Users' ID into "attendance" collection
    data[id] = {'absent', '00:00:00'}

attendance_ref.set(data)

