import firebase_admin
from firebase_admin import credentials, db
import os, json
from django.conf import settings

# Kiểm tra biến môi trường
firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS')
if firebase_creds_json:
    # Chạy trên Render: dùng biến môi trường
    cred = credentials.Certificate(json.loads(firebase_creds_json))
else:
    # Chạy local: dùng file JSON
    # Đường dẫn tuyệt đối tới file firebase_config.json
    firebaseKey_path = os.path.join(settings.BASE_DIR, 'firebase_key.json')
    # Load credentials từ file JSON
    cred = credentials.Certificate(firebaseKey_path)
# Tránh khởi tạo lại Firebase nhiều lần
if not firebase_admin._apps:
    # cred = credentials.Certificate("firebase_key.json")  # đường dẫn đến file key JSON của bạn
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://xeghep-7bb2b-default-rtdb.asia-southeast1.firebasedatabase.app/'  # thay bằng URL thật của bạn
    })
