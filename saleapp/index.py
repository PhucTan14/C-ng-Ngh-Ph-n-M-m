import math
from flask import render_template, request, redirect, session, jsonify
from app import dao, utils
from app import app, login
from flask_login import login_user, logout_user
from app.models import UserRole

# Trang chủ
@app.route("/")
def index():
    kw = request.args.get('kw')
    cate_id = request.args.get('category_id')
    page = request.args.get('page', 1)

    prods = dao.load_products(kw=kw, category_id=cate_id, page=int(page))

    total = dao.count_products()
    return render_template('index.html', products=prods,
                           pages=math.ceil(total/app.config["PAGE_SIZE"]))


# Load trang login
@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        u = dao.auth_user(username=username, password=password)
        if u:
            login_user(u)
            return redirect('/')

    return render_template('login.html')

# load trang admin
@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    u = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
    if u:
        login_user(u)

    return redirect('/admin')

# Sử lý đăng xuất
@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


# load trang đăng ký
@app.route('/register', methods=['get', 'post'])
def register_process():
    err_msg = ''
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password.__eq__(confirm):
            data = request.form.copy()
            del data['confirm']

            avatar = request.files.get('avatar')
            dao.add_user(avatar=avatar, **data)

            return redirect('/login')
        else:
            err_msg = 'Mật khẩu không khớp!'

    return render_template('register.html', err_msg=err_msg)

# api lưu trữ dữ liệu - lấy dữ liệu
@app.route("/api/carts", methods=['post'])
def add_to_cart():
    # {
    #     "1": {
    #         "id": 1,
    #         "name": 'iphone',
    #         "price": 123,
    #         "quantity": 2
    #     }, "2": {
    #         "id": 2,
    #         "name": 'iphone',
    #         "price": 123,
    #         "quantity": 2
    #     }
    # }
    cart = session.get('cart')
    if not cart:
        cart = {}

    id = str(request.json.get('id'))
    name = request.json.get('name')
    price = request.json.get('price')

    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            "id": id,
            "name": name,
            "price": price,
            "quantity": 1
        }

    session['cart'] = cart

    return jsonify(utils.cart_stats(cart))



#Load Trang Tiếp Nhận Học Sinh
@app.route('/Student_admission')
def Student_admission():
    return render_template('Student_admission.html')

#Load Trang lập danh sách lớp
@app.route('/Make_class_list')
def Make_class_list():
    return render_template('Make_class_list.html')

#load trang nhập điểm
@app.route('/Enter_score')
def Enter_score():
    return render_template('Enter_score.html')

#Load trang xuất điểm
@app.route('/Starting_point')
def Starting_point():
    return render_template('Starting_point.html')

#Load trang thống kê báo cáo
@app.route('/Reporting_statistics')
def Reporting_statistics():
    return render_template('Reporting_statistics.html')

#Load trang thay đổi quy định
@app.route('/Change_rules')
def Change_rules():
    return render_template('Change_rules.html')


# Xử lý user từ cơ sở dữ liệu
@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.context_processor
def common_response_data():
    return {
        'categories': dao.load_categories(),
        'cart_stats': utils.cart_stats(session.get('cart'))
    }


if __name__ == '__main__':
    with app.app_context():
        from app import admin
        app.run(debug=True)
