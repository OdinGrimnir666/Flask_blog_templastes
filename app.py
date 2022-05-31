from flask import Flask, render_template, flash, request, redirect, session
from flask_mysqldb import MySQL
import yaml, os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor

app = Flask(__name__)
app.config.from_object(__name__)
CKEditor(app)

db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = os.urandom(24)
mysql = MySQL(app)


@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    result = cursor.execute('select * from blog')
    if result > 0:
        blogs = cursor.fetchall()
        cursor.close()
        return render_template('index.html', blogs=blogs)
    return render_template('index.html', blogs=None)


@app.route('/aboute/')
def about():
    return render_template('about.html')


@app.route('/blogs/<int:id>')
def blogs(id):
    cursor = mysql.connection.cursor()
    result = cursor.execute('select * from blog where blog_id = {}'.format(id))
    if result > 0:
        blog = cursor.fetchone()
        return render_template('blogs.html', blog=blog)
    return 'blog is not found'


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_detail = request.form
        if user_detail['password'] != user_detail['confirmPassword']:
            flash('password do not match! Try again!', 'danger')
            return render_template('register.html')
        cursor = mysql.connection.cursor()
        cursor.execute('insert into user(first_name,last_name,username,email,password) VALUES (%s,%s,%s,%s,%s)',
                       (user_detail['firstname'], user_detail['lastname'], user_detail['username'],
                        user_detail['email1'],
                        generate_password_hash(user_detail['password'])))
        mysql.connection.commit()
        cursor.close()
        flash('Registion sucssecful!pliz login', 'succses')
        return redirect('/login/')

    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_deteils = request.form
        user_name = user_deteils['username']
        cursor = mysql.connection.cursor()
        result = cursor.execute('select * from user where username = %s', ([user_name]))
        if result > 0:
            user = cursor.fetchone()
            if check_password_hash(user['password'], user_deteils['password']):
                session['login'] = True
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
                flash('Welcome' + session['first_name'] + '! Your  have been successfully logged in!', 'success')
            else:
                cursor.close()
                flash('password is incorred', 'danger')
                return render_template('login.html')

        else:
            cursor.close()
            flash('User does not exist', 'danger')
            return render_template('login.html')
        cursor.close()
        return redirect('/')

    return render_template('login.html')


@app.route('/write-blog/', methods=['GET', 'POST'])
def write_blog():
    if request.method == 'POST':
        blogpost = request.form
        title = blogpost['title']
        body = blogpost['body']
        author = session.get('first_name') + ' ' + session.get('last_name')
        print(author)
        cursor = mysql.connection.cursor()
        cursor.execute('insert into blog(title,body,author) Value(%s,%s,%s)',
                       (title, body, author))
        mysql.connection.commit()
        cursor.close()
        flash('Your blog post is accessfully posteed ', 'success')
        return redirect('/')
    return render_template('write-blog.html')


@app.route('/my-blogs/')
def my_blogs():
    author = session.get('first_name') + ' ' + session.get('last_name')
    cursor = mysql.connection.cursor()
    result = cursor.execute('select * from blog where author = %s',[author])
    if result > 0:
        my_blogs = cursor.fetchall()
        return render_template('my-blogs.html', my_blogs=my_blogs)

    else:
        return render_template('my-blogs.html', my_blogs=None)


@app.route('/edit-blog/<int:id>', methods=['GET', 'POST'])
def edit_blog(id):
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        title = request.form['title']
        body = request.form['body']
        cursor.execute('UPDATE blog set title=%s,body=%s where blog_id =%s',(title, body,id))
        mysql.connection.commit()
        cursor.close()
        flash('Blogs is updated successfully', 'success')
        return redirect('/blogs/{}'.format(id))
    cursor = mysql.connection.cursor()
    result = cursor.execute('select * from blog where blog_id={}'.format(id))
    if result > 0:
        blog=cursor.fetchone()
        blog_form={}
        blog_form['title']=blog['title']
        blog_form['body']=blog['body']
        return render_template('edit-blog.html', blog_form=blog_form)


@app.route('/delete-blog/<int:id>')
def delete_blog(id):
    cursor=mysql.connection.cursor()
    cursor.execute('DELETE from blog where blog_id={}'.format(id))
    mysql.connection.commit()
    flash('Your blog has been delete','success')
    return redirect('/my-blogs')


@app.route('/logout/')
def logout():
    session.clear()
    flash('You have been logged out!','info')
    return redirect('/')


if __name__ == '__main__':
    app.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
