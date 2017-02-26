from models import User, Post, Comment
from flask import Blueprint, session, redirect, render_template, request, url_for


blog = Blueprint('blog', __name__, static_folder='static')

# [START helpers]
from auth import username, user_id


def can_edit(obj):
    return obj['user_id'] == user_id()

def __render_template(template, **kwargs):
    return render_template(template, username=username(), **kwargs)
# [END helpers]


# [START posts]
@blog.route('/')
def index():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    posts, next_page_token = Post.index(cursor=token)

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

    posts, next_page_token = Post.index(cursor=token, user_id=user_id())

    return __render_template(
        'index.html',
        posts=posts,
        next_page_token=next_page_token)


@blog.route('/posts/<id>')
def show(id):
    post = Post.read(id)
    return __render_template('show.html', post=post, user_id=user_id())


@blog.route('/posts/add', methods=['GET', 'POST'])
def add():
    if not username():
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        data['user_id'] = user_id()
        data['username'] = username()
        data['like'] = 0
        data['liked_by'] = ['']

        post = Post.upsert(data)

        return redirect(url_for('.show', id=post['id']))

    return __render_template('post.html', action='Add', post={})


@blog.route('/posts/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    post = Post.read(id)

    if not can_edit(post):
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        data['user_id'] = user_id()
        data['username'] = username()

        post = Post.upsert(data, id)

        return redirect(url_for('.show', id=post['id']))

    return __render_template('post.html', action='Edit', post=post)


@blog.route('/posts/<id>/delete')
def delete(id):
    post = Post.read(id)

    if not can_edit(post):
        return redirect(url_for('auth.login'))

    Post.delete(id)
    return redirect(url_for('.index'))
# [END posts]


# [START comments]
@blog.route('/posts/<id>/comments/add', methods=['GET', 'POST'])
def add_comment(id):
    if not username():
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        data['username'] = username()
        data['user_id'] = user_id()
        data['post_id'] = id

        comment = Comment.upsert(data)

        return redirect(url_for('.show', id=id))

    return __render_template('comment.html', action='Add', comment={})


@blog.route('/comments/<id>/edit', methods=['GET', 'POST'])
def edit_comment(id):
    comment = Comment.read(id)

    if not can_edit(comment):
        return redirect(url_for('auth.login'), 403)
    elif request.method == 'POST':
        data = request.form.to_dict(flat=True)
        data['username'] = username()
        data['user_id'] = user_id()
        data['post_id'] = comment['post_id']

        comment = Comment.upsert(data, id)

        return redirect(url_for('.show', id=comment['post_id']))

    return __render_template('comment.html', action='Edit', comment=comment)


@blog.route('/comments/<id>/delete')
def delete_comment(id):
    comment = Comment.read(id)

    if not can_edit(comment):
        return redirect(url_for('auth.login'), 403)

    Comment.delete(id)
    return redirect(url_for('.show', id=comment['post_id']))
# [END comments]


# [START likes]
@blog.route('/posts/<id>/like', methods=['GET'])
def like(id):
    if not username():
        return redirect(url_for('auth.login'))

    post = Post.read(id)

    # post author can't like her own post
    if post['user_id'] == user_id():
        return redirect(url_for('.show', id=id), 403)

    # post can only be liked once
    if user_id() not in post['liked_by']:
        post['liked_by'].append(user_id())
        post['like'] += 1

    Post.put(post)

    return redirect(url_for('.show', id=id))
# [END likes]