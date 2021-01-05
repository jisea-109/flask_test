from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
#from flask_wtf import FlaskForm
#from wtforms import StringField, PasswordField
#from wtforms.validators import InputRequired, Email, Length

app = Flask(__name__,template_folder='app')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///register.db' # to make and load database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # disable track modification of objects
app.secret_key = "secret key"

db = SQLAlchemy(app)

tab = db.Table('tab',
      db.Column('id_number', db.Integer, db.ForeignKey('user.id_number')),
      db.Column('post_id', db.Integer, db.ForeignKey('post.post_id'))
)
class User(db.Model):
    id_number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    posts = db.relationship('Post', secondary=tab, backref=db.backref('fromUser', lazy= 'dynamic'))
    
    def __init__(self,name, username, password):
        self.name = name
        self.username = username
        self.password = password
        
class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    text = db.Column(db.String(5000))
    
    def __init__(self,title,text):
        self.title = title
        self.text = text
    
db.create_all()
db.session.commit()
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/online")
def online():
    if "user" in session:
        user = session["user"]
        check = User.query.filter_by(name=user).all()
    return render_template("index2.html", values=check)
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form.get("name") #id
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        results = User.query.filter_by(name=name).first()
        
        if ' ' in name:
            flash("id has whitespace")
            return render_template("register.html")
        if ' ' in password:
            flash("password has whitespace")
            return render_template("register.html")
        if len(name) < 5 or len(name) > 20:
            flash('Your id must be between 5 and 20 characters')
            return render_template("register.html")
        if len(password) < 8 or len(password) > 20:
            flash('Password must be between 8 and 20 characters')
            return render_template("register.html")
        count = 0
        for i in range(len(password)):
            ch = password[i]
            if ((ch>='a' and ch<= 'z') or (ch>='A' and ch <='Z')):
                count=count+1
            elif (ch >='0' and ch <= '9'):
                continue
            else:
                count += 1
        if count <= 3:
            flash("Password needs at least 3 characters")
            return render_template("register.html")
        if results:
            flash("Your ID is already being used")
            return render_template("register.html")
        else:
            if password == confirm: 
                usr = User(name,username,password)
                db.session.add(usr)
                db.session.commit()
                
                flash("Register Successful!")
                return redirect(url_for("login"))
            else:
                flash("Something wrong")
            
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        name = request.form["name"]
        password = request.form["password"]
        check = User.query.filter_by(name=name).first()
        if check:
            if check.password == password:
                session["user"] = name
                return redirect(url_for("online"))
            else:
                flash("Password is wrong")
        else:
            flash("Account does not exist!")
    
    else:
        if "user" in session:
            flash("Already Logged In!")
            return redirect(url_for("user"))
    return render_template("login.html") # when user hasn't login

@app.route("/user", methods=["POST", "GET"])
def user():
    if "user" in session: 
        user = session["user"]
        check = User.query.filter_by(name=user).first()
        if request.method == "POST":
            title = request.form["title"]
            text = request.form["text"]
            
        #    session["title"] = title
        #    session["text"] = text
            
            posting = Post(title=title, text=text)
            db.session.add(posting)
            db.session.commit()
            check.posts.append(posting)
            db.session.commit()
            flash("Works!")
        #    session.pop("title", None)
        #    session.pop("text", None)
        return render_template("user.html", values=User.query.filter_by(name=user).all())#, location=location, date=date)
    else:
        flash("You are not logged in")
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    if "user" in session:
        flash("You have been logged out")
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/view")
def post():
    if "user" in session:
        user = session["user"]
        check = User.query.filter_by(name=user).first()
        #id_check = Post.query.filter_by(id_number=check.id_number).all()
        id_check = Post.query.filter(Post.fromUser.any(id_number=check.id_number)).all()
        
        if id_check:
            return render_template("view.html", values=id_check)
        else:
            flash("No post have been found")
            return render_template("view.html")
    flash("Please Login first")
    return redirect(url_for("login"))
    
@app.route("/password_change", methods=['GET', 'POST'])
def setting():
    if "user" in session:
        user = session["user"]
        if request.method == 'POST':
            current = request.form["current"]
            password = request.form["password"]
            confirm = request.form["confirm"]
            
            check = User.query.filter_by(name=user).first()
            
            if check.password == current:
                if password == confirm:
                    check.password = password
                    db.session.commit()
                    flash("Password has been changed successfully!")
                    session.pop("user", None)
                    return redirect(url_for("login"))
            else:
                flash("current password and the password you want to change does not match")
    return render_template("setting.html")

if __name__ == "__main__":
    app.run(debug=True) # run application and remain open even if some codes are modified

