import re

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, \
    DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    items = relationship('Item', back_populates='category')

    def name_url(self):
        return encode_url_spaces(self.name)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'items': [item.serialize for item in self.items]
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), unique=True)
    description = Column(String(768))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, back_populates="items")
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    def title_url(self):
        return encode_url_spaces(self.title)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category_id': self.category_id,
            'added_at': self.added_at
        }


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)

# Helper functions ---------------------------------------------------------- #
dash_nondash_matcher = re.compile('-([^-])')
nondash_dash_nondash_matcher = re.compile('([^-])-([^-])')


def encode_url_spaces(title):
    """
    Add one more dash to existing sequence of dashes
    (Save on the dashes during the decoding),
    and replace spaces with one dash.
    """
    return dash_nondash_matcher.sub(r'-\g<0>', title) \
        .replace(' ', '-')


def decode_url_spaces(url_title):
    """
    Replace single dashes with space and remove sequence of dashes.
    """
    title = nondash_dash_nondash_matcher.sub(r'\g<1> \g<2>', url_title)
    return dash_nondash_matcher.sub(r'\g<1>', title)
