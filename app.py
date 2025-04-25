from flask import Flask, request, jsonify, render_template, redirect, url_for, flash,session
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from functools import wraps

# Định nghĩa hàm admin_required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash("Bạn cần đăng nhập với tư cách admin.")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


app = Flask(__name__)

# Kết nối MongoDB Atlas
app.config["MONGO_URI"] = "mongodb+srv://thuanprozz2004:thuanvo2004@cluster0.2ozay.mongodb.net/CloudComputing?retryWrites=true&w=majority&appName=Cluster0"
app.secret_key = 'supersecretkey'  # Khóa bí mật cho Flask session

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Khởi tạo Bcrypt
bcrypt = Bcrypt(app)

# Tạo lớp User cho Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Kết nối MongoDB
mongo = PyMongo(app)
db = mongo.db


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# 1. API lấy danh sách sản phẩm
@app.route('/products', methods=['GET'])
@login_required  # Bảo vệ route này bằng login_required
def get_products():
    products = db.products.find()
    return dumps(products), 200


# 2. API thêm sản phẩm mới
@app.route('/products', methods=['POST'])
@login_required  # Bảo vệ route này bằng login_required
def add_product():
    data = request.json
    if not data or not "name" in data:
        return jsonify({"error": "Missing data!"}), 400

    new_product = {
        "name": data["name"],
        "description": data["description"],
        "price": data["price"],
        "category_id": data["category_id"]
    }

    result = mongo.db.products.insert_one(new_product)
    print(f"✅ Đã thêm vào MongoDB với ID: {result.inserted_id}")
    return jsonify({"message": "Product added!", "id": str(result.inserted_id)}), 201


# 3. API xóa sản phẩm

@app.route("/delete-product/<id>", methods=["POST"])
@admin_required
def delete_product(id):
    db.products.delete_one({"_id": ObjectId(id)})
    flash("Đã xóa sản phẩm thành công!")
    return redirect(url_for('admin_dashboard'))



# Route GET - Lấy dữ liệu sản phẩm và render form cập nhật
@app.route('/update-product/<id>', methods=['GET'])
@admin_required
def update_product(id):
    product = db.products.find_one({"_id": ObjectId(id)})
    if product is None:
        flash("Sản phẩm không tồn tại.")
        return redirect(url_for('admin_dashboard'))

    return render_template("update_product_form.html", product=product)


# Route POST - Cập nhật sản phẩm trong MongoDB
@app.route('/update-product/<id>', methods=['POST'])
@admin_required
def handle_update_product(id):
    data = {
        "name": request.form["name"],
        "description": request.form["description"],
        "price": int(request.form["price"]),
        "category_id": int(request.form["category_id"])
    }

    # Cập nhật sản phẩm trong MongoDB
    result = db.products.update_one(
        {"_id": ObjectId(id)},
        {"$set": data}
    )

    if result.matched_count > 0:
        flash("Sản phẩm đã được cập nhật thành công!")
    else:
        flash("Không tìm thấy sản phẩm để cập nhật.")

    return redirect(url_for('admin_dashboard'))



# Hiển thị form cập nhật sản phẩm
@app.route('/form-update-product/<id>', methods=['GET', 'POST'])
@admin_required
def update_product_form(id):
    product = db.products.find_one({"_id": ObjectId(id)})

    if not product:
        flash("❌ Không tìm thấy sản phẩm.")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        # Lấy dữ liệu từ form
        name = request.form.get("name")
        description = request.form.get("description")
        price = int(request.form.get("price"))
        category_id = int(request.form.get("category_id"))

        # Cập nhật vào MongoDB
        db.products.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "name": name,
                    "description": description,
                    "price": price,
                    "category_id": category_id
                }
            }
        )

        flash("✅ Cập nhật sản phẩm thành công!")
        return redirect(url_for("admin_dashboard"))

    return render_template("update_product_form.html", product=product)



# Giao diện thêm sản phẩm
@app.route('/form-add-product', methods=['GET'])
@admin_required
def product_form():
    return render_template("product_form.html")


# Xử lý thêm sản phẩm từ form
@app.route('/form-add-product', methods=['POST'])
@admin_required
def handle_form_product():
    name = request.form.get("name")
    description = request.form.get("description")
    price = int(request.form.get("price"))
    category_id = int(request.form.get("category_id"))

    new_product = {
        "name": name,
        "description": description,
        "price": price,
        "category_id": category_id
    }

    db.products.insert_one(new_product)
    return render_template("product_form.html", message=" Thêm sản phẩm thành công!")


# Đăng nhập cho Admin
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = db.users.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            user_obj = User(username)
            login_user(user_obj)
            flash("Đăng nhập thành công!")
            return redirect(url_for('home'))
        else:
            flash(" Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/admin-dashboard")
def admin_dashboard():
    if 'admin' not in session:
        flash("Vui lòng đăng nhập với tư cách Admin.")
        return redirect(url_for('admin_login'))

    products = db.products.find()
    return render_template("admin_dashboard.html", username=session['admin'], products=products)




@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Đăng xuất thành công!")
    return redirect(url_for('home'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Kiểm tra xem username đã tồn tại chưa trong MongoDB
        existing_user = db.users.find_one({"username": username})
        if existing_user:
            flash("Tên người dùng đã tồn tại!")
            return redirect(url_for("register"))

        # Hash mật khẩu rồi lưu vào MongoDB
        hashed_password = generate_password_hash(password)
        db.users.insert_one({"username": username, "password": hashed_password})

        flash("Tạo tài khoản thành công! Bạn có thể đăng nhập ngay.")
        return redirect(url_for("login"))

    return render_template("register.html")



@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = db.admins.find_one({'username': username})

        if admin and bcrypt.check_password_hash(admin['password'], password):
            session['admin'] = username
            flash('Đăng nhập admin thành công!', 'success')
            return redirect(url_for("admin_dashboard"))
        else:
            flash('Thông tin đăng nhập sai.', 'danger')
    return render_template('admin_login.html')


@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    flash('Đã đăng xuất admin.', 'success')
    return redirect(url_for('home'))




@app.route('/product/<id>')
def product_detail(id):
    product = db.products.find_one({"_id": ObjectId(id)})
    if not product:
        flash("Không tìm thấy sản phẩm.")
        return redirect(url_for('home'))
    return render_template("product_detail.html", product=product,current_user=current_user)




# Route mặc định
@app.route("/")
def home():
    products = list(db.products.find())
    return render_template("home.html",products=products,current_user=current_user)





if __name__ == '__main__':
    app.run(debug=True, port=5000)
