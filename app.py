from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Food, CartItem

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-change-later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ---------- LOGIN MANAGER ----------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------- SEED FOODS ONCE ----------
def seed_foods():
    if Food.query.count() == 0:
        foods = [
            Food(name="Chicken Biryani", price=249, rating=4.5, time="30 min", category="Biryani",
                 img="https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400"),
            Food(name="Margherita Pizza", price=199, rating=4.3, time="25 min", category="Pizza",
                 img="https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400"),
            Food(name="Veg Burger", price=129, rating=4.1, time="20 min", category="Burger",
                 img="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400"),
            Food(name="Masala Dosa", price=99, rating=4.6, time="15 min", category="Healthy",
                 img="https://images.unsplash.com/photo-1630383249896-424e482df921?w=400"),
            Food(name="Paneer Butter Masala", price=279, rating=4.4, time="35 min", category="Healthy",
                 img="https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400"),
            Food(name="Chocolate Cake", price=149, rating=4.7, time="20 min", category="Desserts",
                 img="https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400"),
            Food(name="Farmhouse Pizza", price=279, rating=4.4, time="30 min", category="Pizza",
                 img="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400"),
            Food(name="Chicken Burger", price=169, rating=4.2, time="22 min", category="Burger",
                 img="https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=400"),
            Food(name="Cold Coffee", price=119, rating=4.5, time="10 min", category="Drinks",
                 img="https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400"),
            Food(name="Fresh Lime Soda", price=79, rating=4.1, time="8 min", category="Drinks",
                 img="https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400"),
        ]
        db.session.add_all(foods)
        db.session.commit()


# ---------- HOME ----------
@app.route("/")
def home():
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    foods_query = Food.query
    if query:
        foods_query = foods_query.filter(Food.name.ilike(f"%{query}%"))
    if category:
        foods_query = foods_query.filter(Food.category == category)

    foods = foods_query.all()

    cart_qty = {}
    if current_user.is_authenticated:
        items = CartItem.query.filter_by(user_id=current_user.id).all()
        cart_qty = {item.food_id: item.quantity for item in items}

    return render_template(
        "index.html",
        foods=foods,
        cart_qty=cart_qty,
        search_query=query,
        active_category=category
    )


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already taken", "error")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created!", "success")
        return redirect(url_for("home"))

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in!", "success")
            return redirect(url_for("home"))

        flash("Invalid username or password", "error")

    return render_template("login.html")


# ---------- LOGOUT ----------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "success")
    return redirect(url_for("home"))


# ---------- ADD TO CART ----------
@app.route("/add-to-cart/<int:food_id>", methods=["POST"])
@login_required
def add_to_cart(food_id):
    item = CartItem.query.filter_by(user_id=current_user.id, food_id=food_id).first()
    if item:
        item.quantity += 1
    else:
        item = CartItem(user_id=current_user.id, food_id=food_id, quantity=1)
        db.session.add(item)
    db.session.commit()
    return redirect(request.referrer or url_for("home"))


# ---------- INCREASE QUANTITY ----------
@app.route("/increase/<int:food_id>", methods=["POST"])
@login_required
def increase_qty(food_id):
    item = CartItem.query.filter_by(user_id=current_user.id, food_id=food_id).first()
    if item:
        item.quantity += 1
        db.session.commit()
    return redirect(request.referrer or url_for("home"))


# ---------- DECREASE QUANTITY ----------
@app.route("/decrease/<int:food_id>", methods=["POST"])
@login_required
def decrease_qty(food_id):
    item = CartItem.query.filter_by(user_id=current_user.id, food_id=food_id).first()
    if item:
        if item.quantity > 1:
            item.quantity -= 1
        else:
            db.session.delete(item)
        db.session.commit()
    return redirect(request.referrer or url_for("home"))


# ---------- VIEW CART ----------
@app.route("/cart")
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(i.food.price * i.quantity for i in items)
    return render_template("cart.html", items=items, total=total)


# ---------- REMOVE FROM CART ----------
@app.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("cart"))


# ---------- CREATE DB TABLES + RUN ----------
with app.app_context():
    db.create_all()
    seed_foods()

if __name__ == "__main__":
    app.run(debug=True)