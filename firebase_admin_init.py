import firebase_admin
from firebase_admin import credentials, firestore
import os

# Path to your Firebase service account key JSON file
FIREBASE_KEY_PATH = os.getenv('FIREBASE_KEY_PATH', 'firebase_service_account.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()
