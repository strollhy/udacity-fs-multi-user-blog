from models import User
from flask import Blueprint, current_app, session, redirect, render_template, request, url_for


auth = Blueprint('auth', __name__, static_folder='static')


def username():
    return session.get('username')


def user_id():
    return session.get('user_id')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        user = User.signup(data)

        if user:
            session['username'] = user['name']
            session['user_id'] = user['id']
            return redirect(url_for('blog.index'))
        else:
            return render_template('signup.html', data=data, error="User already exists."), 403
    elif session.get('username'):
        return redirect(url_for('blog.index'))

    return render_template('signup.html', data={})


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        user = User.login(data)

        if user:
            session['username'] = user['name']
            session['user_id'] = user['id']
            return redirect(url_for('blog.index'))
        else:
            return render_template('login.html', data=data, error=True), 403
    elif session.get('username'):
        return redirect(url_for('blog.index'))

    return render_template('login.html', data={})


@auth.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('blog.index'))
