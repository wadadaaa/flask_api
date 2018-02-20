from flask import Flask

from db import Product
from base_api_views import add_crud_api_endpoint


app = Flask(__name__)


add_crud_api_endpoint(
    app,
    Product,
    _search_field_name='title',
    base_url='/api/v1/',
)


if __name__ == '__main__':
    app.run(port=5002)