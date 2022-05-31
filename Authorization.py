import pyrebase

firebaseConfig = {
    'apiKey': "AIzaSyCkXdB3mIonc9F6Ic9D_0rDYc2HLInuxdc",
    'authDomain': "notey-ee724.firebaseapp.com",
    'projectId': "notey-ee724",
    'storageBucket': "notey-ee724.appspot.com",
    'messagingSenderId': "161243066116",
    'appId': "1:161243066116:web:fb27dce1e1235f600f2a51",
    'measurementId': "G-EL86SKZMD0"
  }

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

