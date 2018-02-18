import json
from flask import Flask, jsonify, request
from db import PRODUCTS
from marshmallow import Schema, fields, ValidationError


app = Flask(__name__)


class ProductSchema(Schema):
    title = fields.Str(required=True)
    price_pub = fields.Int(required=True)
    product_image = fields.Str(required=False)
    in_store = fields.Bool(required=False)


@app.route('/products/', methods=['GET', 'POST'])
def products_handler():
    if request.method == 'GET':
        search_query = request.args.get('q')
        products_to_show = PRODUCTS
        if search_query is not None:
            products_to_show = [
                p for p in PRODUCTS if search_query.lower() in p['title'].lower()]
        is_only_in_store = 'is_only_in_store' in request.args
        if is_only_in_store:
            products_to_show = [
                p for p in PRODUCTS if p['in_store']]
        raw_from = request.args.get('from')
        raw_to = request.args.get('to')
        if raw_from and raw_to and raw_from.isdigit() and raw_to.isdigit():
            products_to_show = products_to_show[int(raw_from):int(raw_to)]
        raw_fields = request.args.get('fields')
        if raw_fields:
            fields = raw_fields.split(',')
            products_to_show = [
                {k: v for (k, v) in p.items() if k in fields} for p in products_to_show]

        return jsonify(products_to_show)
    elif request.method == 'POST':
        request_data = json.loads(request.data.decode())
        if is_product_data_valid(request_data):
            PRODUCTS.append(request_data)
            return jsonify('ok')
        else:
            response = jsonify('data error')
            response.status_code = 400
            return response


def is_product_data_valid(product_data):
    errors = ProductSchema().validate(product_data)
    return not errors


if __name__ == '__main__':
    app.run()
