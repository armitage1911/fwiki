# https://stackoverflow.com/questions/30835901/inserting-images-using-flask-flastpages/47532359#47532359
# ^-- Как добавить пикчу с папки static/images в посте форматированном в markdown-е
# https://stackoverflow.com/questions/57519302/postgresql-ltree-query-to-get-comment-threads-nested-json-array-and-build-html-f

#   todo
# - добавить отдельную страницу для редактирования бокового списка категорий (может, банально сделать список в markdown
#   варианте и перевести его в обычный формат для хтмл страницы?)
# - в easymde попробовать сделать так, чтобы при загрузке картинки, выдавалось только её имя и расширение
# - в Маркдауне, надо будет добавить функцию нижнего подчёркивания самого текста

# import os.path as op
import psycopg
# from .__init__ import DSN, UPLOAD_FOLDER
from .__init__ import DSN
from markdown_it import MarkdownIt
from psycopg.rows import dict_row
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from wiki.auth import login_required
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MD_EXTENSIONS = {
    "typographer": True,
    "linkify": True,
    }
ENABLED_MD_EXTENSIONS = [
    "linkify",
    "table",
    "replacements",
    "smartquotes",
    "strikethrough",
    ]

bp = Blueprint('wiki', __name__)


@bp.route('/')
def index():
    return render_template('wiki/index.html')


def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)


# Для тестов
# @bp.route('/upload')
# def upload_file():
#     return render_template('wiki/upload.html')


# @bp.route('/uploader', methods=['GET', 'POST'])
# def uploader():
#     json_response_list = [{'error': 'noFilePart'},
#                           {'error': 'noFileGiven'},
#                           {'error': 'noAllowedFile'},
#                           ]
#     if 'image' not in request.files:
#         return jsonify(json_response_list[0]), 400
#     file = request.files['image']
#     if not file.filename:
#         return jsonify(json_response_list[1]), 400
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         folderandfilename = op.join(UPLOAD_FOLDER, filename)
#         file.save(folderandfilename)
#         json_success = {'data': {'filePath': fr"../static/images/{filename}"}}
#         return jsonify(json_success), 200
#     return jsonify(json_response_list[2]), 415  # Unsupported Media Type


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        error = None

        if not title:
            flash('Title is required!')

        if error is not None:
            flash(error)
        else:
            with psycopg.connect(DSN) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        'INSERT INTO pages (title, content, author_id)'
                        ' VALUES (%s, %s, %s)', (title, content, g.user['id']))
            return redirect(url_for('index'))

    return render_template('wiki/create.html')


def get_page(id, edit=0):
    md = MarkdownIt("commonmark", MD_EXTENSIONS)
    md.enable(ENABLED_MD_EXTENSIONS)
    with psycopg.connect(DSN, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            page = cur.execute(
                'SELECT * FROM pages WHERE id = (%s)', (id,)
                ).fetchone()

    if page is None:
        abort(404, f"Page id {id} doesn't exist.")

    if edit:
        page['created'] = page['created'].date()
        return page

    page['created'] = page['created'].date()
    if page['content'] is None:
        page['content'] = 'Содержимого данной страницы нет.'
        return page
    page['content'] = md.render(page['content'])

    return page


# TODO
def page_tree():
    with psycopg.connect(DSN, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            page = cur.execute(
                "SELECT nlevel(node_path) as depth, id, pid,"
                " title, node_path FROM pages ORDER BY node_path").fetchall()
    # prev_items_depth = 0
    # for i in range(len(page)):
    #     if prev_items_depth < page[i]["depth"]:
    #         if page[i]["pid"] == None: pass
    #     print("  " * page[i]["depth"], page[i]["title"])
    #     prev_items_depth = page[i]["depth"]
    #
    return page


@bp.route('/<int:id>')
def page(id):
    page_inst = get_page(id)
    return render_template('wiki/page.html', page=page_inst)


@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    page_inst = get_page(id, edit=1)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        error = None

        if not title:
            flash('Title is required!')

        if error is not None:
            flash(error)

        else:
            with psycopg.connect(DSN) as conn:
                with conn.cursor() as cur:
                    cur.execute('UPDATE pages SET title = (%s), content = (%s)'
                                ' WHERE id = (%s)', (title, content, id))
            return redirect(url_for('wiki.page', id=id))

    return render_template('wiki/edit.html', page=page_inst)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    page_inst = get_page(id)
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM pages WHERE id = (%s)', (id,))
    flash(f'Page {page_inst["id"]} deleted successfully')
    return redirect(url_for('index'))
