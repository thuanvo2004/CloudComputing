from pymongo import MongoClient
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Kết nối MongoDB Atlas
client = MongoClient("mongodb+srv://thuanprozz2004:thuanvo2004@cluster0.2ozay.mongodb.net/CloudComputing?retryWrites=true&w=majority&appName=Cluster0")
db = client["CloudComputing"]  # thay bằng tên database thật


admin_data = {
    "username": "admin",
    "password": bcrypt.generate_password_hash("admin123").decode('utf-8'),
    "role": "admin"
}

# Thêm vào collection admins
db.admins.insert_one(admin_data)

print("✅ Admin đã được tạo: admin / admin123")