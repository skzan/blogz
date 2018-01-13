from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'root'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #Links class Blog to class User
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    blogs = db.relationship('Blog', backref='owner') #Links class Blog to class user_id

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    user_id = request.args.get('id')
    users = User.query.all()
    usernames = request.args.get('username')
    return render_template('index.html', users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()
    blog_title_error = ""
    blog_body_error = ""

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        if len(blog_title) <= 0:
            blog_title_error = "Please include a blog title"
            return render_template('newpost.html', blog_title_error=blog_title_error)


        if len(blog_body) <= 0:
            blog_body_error = "Please include a post body"
            return render_template('newpost.html', blog_body_error=blog_body_error)

        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blog?id={}'.format(new_blog.id))
    return render_template('newpost.html')

@app.route('/user_blog', methods=['POST', 'GET'])
def user_blog():
    blog_post_value = request.args.get('id')
    userID = request.args.get('user')
    user = User.query.filter_by(username=userID).first()
    return render_template('user.html', blogs=get_user_blogs(userID))

@app.route('/blog', methods=['GET'])
def blog():
    blogs = []
    #blog_id = request.args.get('id')

    #blogs = Blog.query.all()

    if request.args.get('id'):
        blog_id = request.args.get('id')
        blogs = Blog.query.filter_by(id=blog_id).all()#first()
        return render_template('titlebody.html', blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs) #else loop over every blog in blogs, printing out the blog’s attributes

@app.route("/signup", methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ""
        password_error = ""
        verify_error = ""
        matching_error = ""
        username_taken = ""

        if len(username) < 3 or len(username) > 20:
            username_error = "That's not a valid username"
            return render_template("signup.html", username_error=username_error)

        if len(password) <3 or len(password) >20:
            password_error = "That's not a valid password"
            return render_template("signup.html", password_error=password_error)

        if len(verify) <3 or len(verify) >20:
            verify_error = "That's not a valid password"
            return render_template("signup.html", verify_error=verify_error)

        if not verify == password:
            matching_error = "Passwords don't match"
            return render_template("signup.html", matching_error=matching_error)

        existing_user = User.query.filter_by(username=username).first()

        if not username_error and not password_error and not verify_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                username_taken = "That username is already taken."
                return render_template('signup.html', username=username, password_error = password_error, verify_error = verify_error, matching_error=matching_error, username_taken=username_taken)
    """else:
        return render_template("signup.html", username = username, password = password, verify = verify,
            username_error = username_error, password_error = password_error,
            verify_error = verify_error, matching_error = matching_error)"""
    return render_template("signup.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    username_error = ""
    password_error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if len(username) < 1:
            username_error = "Please enter a username."
            return render_template('login.html', username_error=username_error)
        if not user:
            username_error = "That username does not exist"
            return render_template('login.html', username_error=username_error)
        if user:
            if user.password != password:
                password_error = "Password incorrect. Please re-enter password"
                return render_template('login.html', password_error=password_error, username=username)
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
