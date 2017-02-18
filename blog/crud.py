from blog import get_model
from flask import Blueprint, redirect, render_template, request, url_for


crud = Blueprint('blog', __name__, static_folder='static')


@crud.route("/")
def index():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    posts, next_page_token = get_model().index(cursor=token)

    return render_template(
        "index.html",
        posts=posts,
        next_page_token=next_page_token)


@crud.route('/posts/<id>')
def show(id):
    post = get_model().read(id)
    return render_template("show.html", post=post)


@crud.route('/posts/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        post = get_model().create(data)

        return redirect(url_for('.show', id=post['id']))

    return render_template("post_form.html", action="Add", post={})


@crud.route('/posts/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    post = get_model().read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        post = get_model().update(data, id)

        return redirect(url_for('.show', id=post['id']))

    return render_template("post_form.html", action="Edit", post=post)


@crud.route('/posts/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.index'))