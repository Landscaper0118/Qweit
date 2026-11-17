from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

#テーブル作成
with app.app_context():
    db.create_all()

#ホーム画面
@app.route("/")
def home():
    return render_template("home.html")

#新規登録画面
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username")

        new_user = User(
            email=email, 
            password=password, 
            username=username
        )
        
        db.session.add(new_user)

        db.session.commit()

        return f"データベースへの登録確認。登録情報: {username}, {email}, {password}"
    
    return render_template("register.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)