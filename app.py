import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "qweit_secret_key"  # セッション

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#空欄時のランダムネーム
GroupA = ["はやぶさ", "孤高の", "ワールド", "異次元の", "忘却の", "ダーク", "プラチナ", "21世紀", "大御所", "流れる", "真夏の", "天才","病弱", "レッド", "ブルー", "イエロー", "北国の", "南国の","封印されし","強欲な","転生したら","光の","特級","5等分の","異世界","4分割","偉大な"]
GroupB = ["カレー", "太郎", "花子", "天使", "大魔神", "社長", "工場長", "メガネ", "最先端", "パス", "村長", "一般人", "先生", "回避魚", "堕天使", "ステーキ", "大冒険", "野口英世","指揮官","管理人","プロデューサー","ドクター","マスター","ハッカー","戦士","プロキシ","旅人"]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)
    author = db.relationship('User', backref="questions")

#テーブル作成
with app.app_context():
    db.create_all()

#ホーム画面
@app.route("/")
def home():
    username = session.get("username")
    return render_template("home.html", username=username)

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
            session["user_id"] = user.id
            session["username"] = user.username

            active_question = Question.query.filter_by(user_id=user.id, is_resolved=False).first()
            if active_question:
                return redirect(url_for("waiting"))

            return redirect(url_for("question"))
        else:
            return render_template("login.html", error = "メールアドレスまたはパスワードが正しくありません。")

    return render_template("login.html")  

@app.route("/question", methods=["GET", "POST"])
def question():
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    active_question = Question.query.filter_by(user_id=session.get("user_id"), is_resolved=False).first()
    if active_question:
        return redirect(url_for("waiting"))
    
    if request.method == "POST":
        # フォームからのデータを取得
        category = request.form.get("question_category")
        text = request.form.get("question_text", "").strip()

        if not category or not text:
            return render_template("question.html", error="質問事項と質問内容を入力してください。")
    # データベースに質問を保存
        new_question = Question(
            user_id=session.get("user_id"),
            category=category,
            text=text
        )

        db.session.add(new_question)
        db.session.commit()

        return redirect(url_for("waiting"))
    
    return render_template("question.html")

#質問順番待ち画面
@app.route("/waiting")
def waiting():
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    active_question = (Question.query.filter_by(is_resolved=False).order_by(Question.id.asc()).limit(10).all())

    #対応完了してたら、質問登録画面へ遷移
    if not active_question:
        return redirect(url_for("question"))

    return render_template("waiting.html", question=active_question,)

#ログアウト
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)