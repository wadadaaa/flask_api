from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///db.sqlite', echo=False)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    price_rub = Column(Integer)
    product_image = Column(String)
    in_store = Column(Boolean)

    def to_dict(self, fields=None):
        result_info = {}
        for column in self.__class__.__table__.columns:
            if fields and column.name not in fields:
                continue
            result_info[column.name] = getattr(self, column.name, None)
        return result_info

    @classmethod
    def from_dict(cls, product_info):
        product = cls()
        product.price_rub = product_info.get('price_rub')
        product.product_image = product_info.get('product_image')
        product.title = product_info.get('title')
        product.in_store = product_info.get('in_store')
        return product


def create_demo_products():
    products_info = [
        {
            'title': 'Iphone X',
            'price_rub': 8050000,
            'product_image': '/images/iphone.jpg',
            'in_store': True,
        },
        {
            'title': 'Macbook Air 2015',
            'price_rub': 5050000,
            'product_image': '/images/iphone.jpg',
            'in_store': True,
        },
        {
            'title': 'Macbook Air 2017',
            'price_rub': 6050000,
            'product_image': '/images/iphone.jpg',
            'in_store': False,
        },
    ]
    session = Session()
    for product_info in products_info:
        product = Product()
        product.price_rub = product_info['price_rub']
        product.product_image = product_info['product_image']
        product.title = product_info['title']
        product.in_store = product_info['in_store']
        session.add(product)
    session.commit()


def create_all_tables():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all_tables()
    create_demo_products()
