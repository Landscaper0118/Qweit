import random
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#空欄時のランダムネーム
GroupA = ["はやぶさ", "孤高の", "ワールド", "異次元の", "忘却の", "ダーク", "プラチナ", "21世紀", "大御所", "流れる", "真夏の", "天才", "レッド", "ブルー", "イエロー", "北国の", "南国の",]
GroupB = ["カレー", "太郎", "花子", "天使", "大魔神", "社長", "工場長", "メガネ", "最先端", "パス", "村長", "一般人", "先生", "回避魚", "堕天使", "ステーキ", "大冒険", "野口英世",]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=False, nullable=False)
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
        username = request.form.get("username","").strip()

        #usernameが空欄ならランダムにリストから生成する
        if not username: 
            username = f"{random.choice(GroupA)}{random.choice(GroupB)}"

        new_user = User(
            email=email, 
            password=password, 
            username=username
        )
        
        db.session.add(new_user)

        db.session.commit()

        return render_template("register_complete.html")
    
    return render_template("register.html")

#ログイン画面
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            return f"ログインしました。ようこそ{user.username}さん"
        else:
            return render_template("login.html", error = "メールアドレスまたはパスワードが正しくありません。")

    return render_template("login.html")    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)