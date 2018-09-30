from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

#Blog class with the necessary properties (i.e., an id, title, and body
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body        

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
        new_blog = Blog(title, body)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog?id='+str(new_blog.id))
    return render_template('newpost.html')

@app.route('/addpost', methods=['GET'])
def addpost():
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def blog():
    blog_id = request.args.get('id')
    if blog_id:
        return render_template('individual.html', blog=get_blog(blog_id))
    else:
        return render_template('blog.html', title='Build a Blog', blogs=get_blogs())

@app.route('/', methods=['GET'])
def main():
    return redirect('/blog')

def get_blogs():
    return Blog.query.filter_by().all()

def get_blog(blog_id):
    return Blog.query.filter_by(id=blog_id).first()

app.run()
