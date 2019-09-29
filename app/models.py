from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime


Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'
    category_id = Column(Integer, primary_key=True)
    title = Column(String)
    summary = Column(String)
    created = Column(DateTime, default=datetime.utcnow)
    last_edit = Column(DateTime)
    posts = relationship('Post', lazy='dynamic')

    def __repr__(self):
        return f' category_id: {self.category_id}, title: {self.title},' \
               f' summary: {self.summary},' \
               f' created: {self.created}, last_edit: {self.last_edit}, posts: {self.posts}'


class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.category_id'))
    title = Column(String)
    body = Column(String)
    created = Column(DateTime, default=datetime.utcnow)
    last_edit = Column(DateTime)
    comments = relationship('Comment', lazy='dynamic')

    def __repr__(self):
        return f' post_id: {self.post_id} , category_id: {self.category_id}, title: {self.title},' \
               f' body: {self.body}, created: {self.created}, ' \
               f' last_edit: {self.last_edit}, comments: {self.comments}'


class Comment(Base):
    __tablename__ = 'comments'
    comment_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    parent_comment_id = Column(Integer)
    title = Column(String)
    body = Column(String)
    created = Column(DateTime, default=datetime.utcnow)
    last_edit = Column(DateTime)

    def __repr__(self):
        return f'comment_id: {self.comment_id}, post_id: {self.post_id},' \
               f'parent_comment_id: {self.parent_comment_id},' \
               f'title: {self.title}, body: {self.body}, ' \
               f'created: {self.created}, last_edit: {self.last_edit}'
