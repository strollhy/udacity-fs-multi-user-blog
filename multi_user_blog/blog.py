from multi_user_blog import get_model
from flask import Blueprint, session, redirect, render_template, request, url_for


blog = Blueprint('blog', __name__, static_folder='static')

# [START helpers]
from auth import username, user_id


def can_edit(post):
    return post['user_id'] == user_id()


def __render_template(template, **kwargs):
    return render_template(template, username=username(), **kwargs)
# [END helpers]


@blog.route('/')
def index():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    posts, next_page_token = get_model().index(cursor=token)

    return __render_template(
        'index.html',
        posts=posts,
        next_page_token=next_page_token)


@blog.route('/mypost')
def mypost():
    if not username():
        return redirect(url_for('auth.login'))

    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    posts, next_page_token = get_model().index(cursor=token, user_id=user_id())

    return __render_template(
        'index.html',
        posts=posts,
        next_page_token=next_page_token)



@blog.route('/posts/<id>')
def show(id):
    post = get_model().read(id)
    return __render_template('show.html', post=post, useraccess=can_edit(post))


@blog.route('/posts/add', methods=['GET', 'POST'])
def add():
    if not username():
        return redirect(url_for('auth.login'))
    elif request.method == 'POST':
        data = request.form.to_dict(flat=True)
        data['user_id'] = user_id()

        post = get_model().create(data)

        return redirect(url_for('.show', id=post['id']))

    return __render_template('post.html', action='Add', post={})


@blog.route('/posts/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    post = get_model().read(id)

    if not can_edit(post):
        return redirect(url_for('auth.login'))
    elif request.method == 'POST':
        data = request.form.to_dict(flat=True)
        data['user_id'] = user_id()

        post = get_model().update(data, id)

        return redirect(url_for('.show', id=post['id']))

    return __render_template("post.html", action="Edit", post=post)


@blog.route('/posts/<id>/delete')
def delete(id):
    post = get_model().read(id)

    if not can_edit(post):
        return redirect(url_for('auth.login'))

    get_model().delete(id)
    return redirect(url_for('.index'))