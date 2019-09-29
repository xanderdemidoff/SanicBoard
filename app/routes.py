from main import app
from main import make_session
from sanic.response import json
from app.models import Category, Post, Comment
from contextlib import contextmanager
from datetime import datetime


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = make_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# -----------------------------------------------------C R E A T E------------------------------------------------------
@app.route("/add_category", methods=['POST'])
async def add_category(request) -> json:
    """
    :body title - заголовок (mandatory)
    :body summary - описание (mandatory)
    """
    title, summary = request.form.get('title'), request.form.get('summary')

    if not title or not summary:
        return json(status=400, body=f'Parameters "title" or "summary" has not been filled.')

    with session_scope() as session:
        # записываем данные в базу
        new_category = Category(title=title, summary=summary)
        session.add(new_category)
        session.commit()

    return json(status=200, body={'title': new_category.title,
                                  'summary': new_category.summary,
                                  'category_id': new_category.category_id,
                                  'created': new_category.created,
                                  'last_edit': new_category.last_edit})


@app.route("/add_post/<category_id:int>", methods=['POST'])
async def add_post(request, category_id) -> json:
    """
    :body title - заголовок (mandatory)
    :body body - тело сообщения (mandatory)
    """
    title, body = request.form.get('title'), request.form.get('body')

    if not title or not body:
        return json(status=400, body=f'Parameters "title" or "body" has not been filled.')

    with session_scope() as session:
        # проверяем, что категория существует
        if not session.query(Category).filter_by(category_id=category_id).first():
            return json(status=400, body=f'No category {category_id} in database.')

    with session_scope() as session:
        # записываем данные в базу
        new_post = Post(title=title, body=body, category_id=category_id)
        session.add(new_post)
        session.commit()

    return json(status=200, body={'title': new_post.title,
                                  'body': new_post.body,
                                  'category_id': new_post.category_id,
                                  'post_id': new_post.post_id,
                                  'created': new_post.created,
                                  'last_edit': new_post.last_edit})


@app.route("add_comment/<post_id:int>", methods=['POST'])
async def add_comment(request, post_id) -> json:
    """
    :body title - заголовок (mandatory)
    :body body - тело комментария (mandatory)
    :body parent_comment_id - добавляется, если комментируется другой комментарий, а не пост (optional)
    """
    title, body = request.form.get('title'), request.form.get('body')

    if not title or not body:
        return json(status=400, body=f'Parameters "title" or "body" has not been filled.')

    with session_scope() as session:
        # проверяем, что пост существует
        if not session.query(Post).filter_by(post_id=post_id).first():
            return json(status=400, body=f'No post {post_id} in database.')

    with session_scope() as session:
        # записываем данные в базу
        parent_comment_id = request.form.get('parent_comment_id')
        new_comment = Comment(title=title, body=body, post_id=post_id, parent_comment_id=parent_comment_id)
        session.add(new_comment)
        session.commit()

        return json(status=200, body={'title': new_comment.title,
                                      'body': new_comment.body,
                                      'post_id': new_comment.post_id,
                                      'comment_id': new_comment.comment_id,
                                      'parent_comment_id': new_comment.parent_comment_id,
                                      'created': new_comment.created,
                                      'last_edit': new_comment.last_edit})

# -----------------------------------------------------U P D A T E------------------------------------------------------
@app.route("/edit_category/<category_id:int>", methods=['POST'])
async def edit_category(request, category_id) -> json:
    """
    :body title - заголовок (optional)
    :body summary - описание категории (optional)
    """
    title, summary = request.form.get('title'), request.form.get('summary')

    if not title and not summary:
        return json(status=400, body=f'Parameters "title" or "summary" has not been filled.')

    with session_scope() as session:
        # проверяем, что категория существует
        category = session.query(Category).filter_by(category_id=category_id)
        if not category.first():
            return json(status=400, body=f'No category {category_id} in database.')

        if category.first().title == title or category.first().summary == summary:
            return json(status=400, body=f'Nothing to change')

        if title:
            category.update({'title': title, 'last_edit': datetime.utcnow()})
        if summary:
            category.update({'summary': summary, 'last_edit': datetime.utcnow()})

    edited_category = category.first()
    return json(status=200, body={'title': edited_category.title,
                                  'summary': edited_category.summary,
                                  'category_id': edited_category.category_id,
                                  'created': edited_category.created,
                                  'last_edit': edited_category.last_edit})


@app.route("/edit_post/<post_id:int>", methods=['POST'])
async def edit_post(request, post_id) -> json:
    """
    :body title - заголовок (optional)
    :body body - тело сообщения (optional)
    """
    title, body = request.form.get('title'), request.form.get('body')

    if not title and not body:
        return json(status=400, body=f'Parameters "title" or "body" has not been filled.')

    with session_scope() as session:
        # проверяем, что пост существует
        post = session.query(Post).filter_by(post_id=post_id)
        if not post.first():
            return json(status=400, body=f'No post {post_id} in database.')

        if post.first().title == title or post.first().body == body:
            return json(status=400, body=f'Nothing to change')

        if title:
            post.update({'title': title, 'last_edit': datetime.utcnow()})
        if body:
            post.update({'body': body, 'last_edit': datetime.utcnow()})

    edited_category = post.first()
    return json(status=200, body={'title': edited_category.title,
                                  'body': edited_category.body,
                                  'category_id': edited_category.category_id,
                                  'created': edited_category.created,
                                  'last_edit': edited_category.last_edit})


@app.route("/edit_comment/<comment_id:int>", methods=['POST'])
async def edit_comment(request, comment_id) -> json:
    """
    :body title - заголовок (optional)
    :body body - тело комментария (optional)
    """
    title, body = request.form.get('title'), request.form.get('body')

    if not title and not body:
        return json(status=400, body=f'Parameters "title" or "body" has not been filled.')

    with session_scope() as session:
        # проверяем, что комментарий существует
        comment = session.query(Comment).filter_by(comment_id=comment_id)
        if not comment.first():
            return json(status=400, body=f'No comment {comment_id} in database.')

        if comment.first().title == title or comment.first().body == body:
            return json(status=400, body=f'Nothing to change')

        if title:
            comment.update({'title': title, 'last_edit': datetime.utcnow()})
        if body:
            comment.update({'body': body, 'last_edit': datetime.utcnow()})

    edited_comment = comment.first()
    return json(status=200, body={'title': edited_comment.title,
                                  'body': edited_comment.body,
                                  'post_id': edited_comment.post_id,
                                  'comment_id': edited_comment.comment_id,
                                  'parent_comment_id': edited_comment.parent_comment_id,
                                  'created': edited_comment.created,
                                  'last_edit': edited_comment.last_edit})


# -----------------------------------------------------G E T------------------------------------------------------------
@app.route("/get_categories", methods=['GET'])
async def get_categories(request) -> json:
    """
    Example: /get_categories?limit=20&offset=0

    :arg limit - максимальное количество элементов в выдаче (mandatory)
    :arg offset - индекс элемента, с которого будет запрошен новый набор элементов
    """
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    if not offset or not limit:
        return json(status=400, body={'Error': 'Offset and limit are mandatory parameters.'})

    with session_scope() as session:
        categories = session.query(Category)
        if categories.count() == 0:
            return json(status=400, body='No categories was found.')

        chunk = list()
        for category in categories.limit(limit).offset(offset):
            chunk.append({
                'title': category.title,
                'summary': category.summary,
                'category_id': category.category_id,
                'created': category.created,
                'last_edit': category.last_edit,
                'posts_count': category.posts.count()
            })
        chunk.append({'all_categories_count': categories.count()})
        return json(status=200, body=chunk)


@app.route("/get_posts/<category_id:int>", methods=['GET'])
async def get_posts(request, category_id) -> json:
    """
    Example: /get_posts/10?limit=20&offset=0

    :arg limit - максимальное количество элементов в выдаче (mandatory)
    :arg offset - индекс элемента, с которого будет запрошен новый набор элементов
    """
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    if not offset or not limit:
        return json(status=400, body={'Error': 'Offset and limit are mandatory parameters.'})

    with session_scope() as session:
        posts = session.query(Post).filter_by(category_id=category_id)
        if posts.count() == 0:
            return json(status=400, body='No posts was found.')

        chunk = list()
        for post in posts.limit(limit).offset(offset):
            chunk.append({
                'title': post.title,
                'body': post.body,
                'category_id': post.category_id,
                'post_id': post.post_id,
                'created': post.created,
                'last_edit': post.last_edit,
                'comments_count': post.comments.count()
            })
        chunk.append({'all_posts_count': posts.count()})
        return json(status=200, body=chunk)


@app.route("/get_post/<post_id:int>", methods=['GET'])
async def get_post(request, post_id) -> json:
    """
    Example: /get_post?limit=20&offset=0
    limit и offset применяются только для комментариев, оставленных к посту.

    :arg limit - максимальное количество элементов в выдаче (mandatory)
    :arg offset - индекс элемента, с которого будет запрошен новый набор элементов
    """
    offset = request.args.get('offset')
    limit = request.args.get('limit')

    with session_scope() as session:
        post = session.query(Post).filter_by(post_id=post_id).first()
        chunk = dict()

        chunk['post'] = {
                'title': post.title,
                'body': post.body,
                'category_id': post.category_id,
                'post_id': post.post_id,
                'created': post.created,
                'last_edit': post.last_edit,
                'comments_count': post.comments.count()
            }

        chunk['comments'] = []
        for comment in post.comments.limit(limit).offset(offset):
            chunk['comments'].append(
                {
                    'title': comment.title,
                    'body': comment.body,
                    'post_id': comment.post_id,
                    'parent_comment_id': comment.parent_comment_id,
                    'created': comment.created,
                    'last_edit': comment.last_edit,
                    'comments_count': comment.comments.count()
                }
            )
    return json(status=200, body=chunk)


@app.route("/get_comment/<comment_id:int>", methods=['GET'])
async def get_comment(request, comment_id) -> json:
    """
    Example: /get_comment?limit=20&offset=0
    limit и offset применяются только для комментариев, оставленных к запрошенному комментарию.

    :arg limit - максимальное количество элементов в выдаче (mandatory)
    :arg offset - индекс элемента, с которого будет запрошен новый набор элементов
    """
    offset = request.args.get('offset')
    limit = request.args.get('limit')

    with session_scope() as session:
        comment = session.query(Comment).filter_by(comment_id=comment_id).first()
        chunk = dict()

        chunk['comment'] = {
            'title': comment.title,
            'body': comment.body,
            'comment_id': comment.comment_id,
            'post_id': comment.post_id,
            'created': comment.created,
            'last_edit': comment.last_edit,
            'parent_comment_id': comment.parent_comment_id,
        }
        nested_comments = session.query(Comment).filter_by(parent_comment_id=comment_id)
        chunk['nested_comments'] = []
        for comment in nested_comments.limit(limit).offset(offset):
            chunk['nested_comments'].append(
                {
                    'title': comment.title,
                    'body': comment.body,
                    'post_id': comment.post_id,
                    'parent_comment_id': comment.parent_comment_id,
                    'created': comment.created,
                    'last_edit': comment.last_edit
                }
            )
    return json(status=200, body=chunk)


@app.route('/search_category', methods=['GET'])
async def search_category(request) -> json:
    """
    Выполняет поиск по полному/частичному имени категории.
    :arg limit - максимальное количество элементов в выдаче (mandatory)
    :arg offset - индекс элемента, с которого будет запрошен новый набор элементов
    :arg category_name - полное или частичное имя категории

    Example: /search_category?category_name='Main category&limit=20&offset=0'
    """
    category_name = request.args.get('category_name').replace("'", '')
    limit = request.args.get('limit')
    offset = request.args.get('offset')

    if not limit or not offset or not category_name:
        return json(status=400, body=f'ERROR: Category_name or offset or limit has not been filled. '
                                     f'Category_name: {category_name}, offset: {offset}, limit: {limit}')
    with session_scope() as session:
        categories = session.query(Category).filter(Category.title.like(f'%{category_name}%'))
        if categories.count() == 0:
            return json(status=400, body='No categories was found.')

        chunk = list()
        for category in categories.limit(limit).offset(offset):
            chunk.append({
                'title': category.title,
                'summary': category.summary,
                'category_id': category.category_id,
                'created': category.created,
                'last_edit': category.last_edit,
                'posts_count': category.posts.count()
            })
        chunk.append({'all_categories_count': categories.count()})
        return json(status=200, body=chunk)


@app.route('/search_post', methods=['GET'])
async def search_post(request) -> json:
    """
    Выполняет поиск по полному/частичному имени поста.
    :arg limit - максимальное количество элементов в выдаче (mandatory)
    :arg offset - индекс элемента, с которого будет запрошен новый набор элементов
    :arg post_name - полное или частичное имя поста

    Example: /search_category?post_name='My first post&limit=20&offset=0'
    """
    post_name = (request.args.get('post_name')).replace("'", '')
    limit = request.args.get('limit')
    offset = request.args.get('offset')

    if not limit or not offset or not post_name:
        return json(status=400, body=f'ERROR: Post_name or offset or limit has not been filled. '
                                     f'Post_name: {post_name}, offset: {offset}, limit: {limit}')

    with session_scope() as session:
        posts = session.query(Post).filter(Post.title.like(f'%{post_name}%'))
        if posts.count() == 0:
            return json(status=400, body='No posts was found.')

        chunk = list()
        for post in posts.limit(limit).offset(offset):
            chunk.append({
                'title': post.title,
                'body': post.body,
                'category_id': post.category_id,
                'post_id': post.post_id,
                'created': post.created,
                'last_edit': post.last_edit,
                'comments_count': post.comments.count()
            })
        chunk.append({'all_posts_count': posts.count()})
        return json(status=200, body=chunk)


# -----------------------------------------------------D E L E T E------------------------------------------------------
@app.route("/delete_category/<category_id:int>", methods=['DELETE'])
async def delete_category(request, category_id) -> json:
    """Категория удаляется вместе с постами и комментариями"""
    with session_scope() as session:
        category = session.query(Category).filter_by(category_id=category_id)
        if category.count() == 0:
            return json(status=400, body=f'No category {category_id} in database.')
        else:
            posts = session.query(Post).filter_by(category_id=category_id)
            for post in posts:
                comments = session.query(Comment).filter_by(post_id=post.post_id)
                for comment in comments:
                    # удаляем вложенные комментарии, затем родительский комментарий, затем пост и категорию
                    nested_comments = session.query(Comment).filter_by(parent_comment_id=comment.comment_id)
                    nested_comments.delete()
                comments.delete()
            posts.delete()
            category.delete()
            return json(status=200, body=f'Category {category_id} was successfully deleted')


@app.route("/delete_post/<post_id:int>", methods=['DELETE'])
async def delete_post(request, post_id) -> json:
    """Пост удаляется вместе с комментариями"""
    with session_scope() as session:
        post = session.query(Post).filter_by(post_id=post_id)
        if post.count() == 0:
            return json(status=400, body=f'No post {post_id} in database.')
        else:
            # удаляем комментарии к посту, затем пост
            session.query(Comment).filter_by(post_id=post_id).delete()
            post.delete()
            return json(status=200, body=f'Post {post_id} was successfully deleted')


@app.route("/delete_comment/<comment_id:int>", methods=['DELETE'])
async def delete_comment(request, comment_id) -> json:
    """Комментарий удаляется вместе с вложенными комментариями"""
    with session_scope() as session:
        comment = session.query(Comment).filter_by(comment_id=comment_id)
        if comment.count() == 0:
            return json(status=400, body=f'No comment {comment_id} in database.')
        else:
            # удаляем вложенные комментарии, затем родительский комментарий
            session.query(Comment).filter_by(parent_comment_id=comment_id).delete()
            comment.delete()
            return json(status=200, body=f'Comment {comment_id} was successfully deleted')
