from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

#Blog class with the necessary properties (i.e., an id, title, and body
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    username = db.Column(db.String(20), db.ForeignKey('user.username'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user   


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password
      
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
    
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        title_error = ''
        body_error = ''
        if title == '':
            title_error = 'Title cannot be empty. '
        if body == '':
            body_error = 'Body cannot be empty.'
        if title_error or body_error:
            return render_template('newpost.html', 
            body_error=body_error,
            title_error=title_error, 
            title=title, body=body)
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog?id='+str(new_blog.id))
    return render_template('newpost.html')

@app.route('/blog', methods=['GET'])
def blog():
    blog_id = request.args.get('id')
    username = request.args.get('username')
    if blog_id:
        return render_template('individual.html', blog=get_blog(blog_id))
    elif username:
        return render_template('blog.html', title='blog posts!', blogs=get_user_blogs(username))
    else:
        return render_template('blog.html', title='blog posts!', blogs=get_blogs())

@app.route('/', methods=['GET'])
def index():
    users = User.query.filter_by().all()
    return render_template('index.html', title="Blog Userz!", users=users)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error, password_error, verify_error = '','',''
        # TODO - validate user's data
        if len(username)<3 or len(username)>20:
            username_error = 'Username must be between 3 and 20 characters long.'
        if len(password)<3 or len(password)>20:
            password_error = 'Password must be between 3 and 20 characters long.'
        if password != verify:
            verify_error = 'Verify password did not match password.'

        if username_error or password_error or verify_error:
            return render_template('signup.html',
                    username=username, 
                    username_error=username_error, 
                    password_error=password_error,
                    verify_error=verify_error)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            # TODO - user better response messaging
            flash('user already has an account')
            return redirect('/login')

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

def get_blogs():
    return Blog.query.filter_by().order_by(desc(Blog.id))

def get_user_blogs(username):
    return Blog.query.filter_by(username=username).order_by(desc(Blog.id))

def get_blog(blog_id):
    return Blog.query.filter_by(id=blog_id).first()

if __name__=='__main__':
    app.run()
