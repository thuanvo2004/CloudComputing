from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash("Bạn cần đăng nhập với tư cách admin.")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function
