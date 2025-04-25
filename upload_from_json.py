import requests
import json

# Đọc file JSON sản phẩm
with open('products.json', 'r', encoding='utf-8') as file:
    products = json.load(file)

url = "http://localhost:5000/products" # API của Flask

# Gửi từng sản phẩm lên Flask API
for product in products:
    res = requests.post(url, json=product)
    if res.status_code == 201:
        print(f"✅ Đã thêm: {product['name']}")
    else:
        print(f"❌ Lỗi khi thêm {product['name']}: {res.text}")
