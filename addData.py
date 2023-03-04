
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred,{
  "databaseURL":'https://classcapture-1362b-default-rtdb.firebaseio.com/'
})

ref = db.reference("Students")

data = {
  "321654":
    {
      "name":"Yaksh Gandhi",
      "Program": "CSE Core",
      "starting_year":2021,
      "Year":2,
      "total_attendance":10,
      "last_attendance_time": "2023-2-24 10:30:00"
    },
  "852741":
    {
      "name":"Emily Blunt",
      "Program": "Arts",
      "starting_year":2021,
      "Year":2,
      "total_attendance":3,
      "last_attendance_time": "2023-2-24 8:30:00"
      
    },
  "963852":
    {
      "name":"Elon Musk",
      "Program": "MBA",
      "starting_year":2017,
      "Year":2,
      "total_attendance":8,
      "last_attendance_time": "2023-2-24 12:34:00"
      
    }
}

for key,value in data.items():
  ref.child(key).set(value)