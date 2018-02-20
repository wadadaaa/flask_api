import json

from sqlalchemy import Boolean
from flask import Flask, jsonify, request
from flask.views import View

from db import Product, Session
from schemas import ProductSchema, is_product_data_valid


class AbstractListView(View):
    allowed_methods = ['get']
    model = None
    search_field_name = None
    allow_boolean_filters = True

    def dispatch_request(self):
        if request.method.lower() not in self.allowed_methods:
            response = jsonify('method not allowed')
            response.status_code = 400
            return response
        return getattr(self, request.method.lower())()

    def get(self):
        session = Session()
        products_to_show = session.query(self.model)
        products_to_show = self.apply_search_param(products_to_show)
        if self.allow_boolean_filters:
            products_to_show = self.apply_boolean_filters(products_to_show)
        products_to_show = self.apply_limits_params(products_to_show)
        products_list = self.convert_to_jsonable_structure(products_to_show)
        return jsonify(products_list)

    def post(self):
        session = Session()
        request_data = json.loads(request.data.decode('utf-8'))
        if is_product_data_valid(request_data):
            product = self.model.from_dict(request_data)
            session.add(product)
            session.commit()
            return jsonify('ok')
        else:
            response = jsonify('data error')
            response.status_code = 400
            return response

    def apply_boolean_filters(self, products_to_show):
        for column_name in self.get_boolean_column_names_from_model():
            get_param = 'only_%s' % column_name
            is_apply_filter = get_param in request.args
            if is_apply_filter:
                products_to_show = products_to_show.filter(
                    getattr(self.model, column_name) == True
                )
        return products_to_show

    def apply_search_param(self, products_to_show):
        search_query = request.args.get('q')
        if search_query is not None:
            ilike_query = '%%%s%%' % search_query
            search_field = getattr(self.model, self.search_field_name)
            products_to_show = products_to_show.filter(
                search_field.ilike(ilike_query)
            )
        return products_to_show

    def apply_limits_params(self, products_to_show):
        raw_from = request.args.get('from')
        raw_to = request.args.get('to')
        if raw_from and raw_to and raw_from.isdigit() and raw_to.isdigit():
            products_to_show = products_to_show[int(raw_from):int(raw_to)]
        return products_to_show

    def convert_to_jsonable_structure(self, products_to_show):
        raw_fields = request.args.get('fields')
        fields = raw_fields.split(',') if raw_fields else None
        return [p.to_dict(fields) for p in products_to_show]

    @classmethod
    def get_boolean_column_names_from_model(cls):
        column_names = []
        for column in cls.model.__table__.columns:
            if isinstance(column.type, Boolean):
                column_names.append(column.name)
        return column_names


def add_crud_api_endpoint(app, model_class, _search_field_name, base_url):
    class ProductsListView(AbstractListView):
        allowed_methods = ['get', 'post']
        model = model_class
        search_field_name = _search_field_name

    view_name = model_class.__name__.lower()
    print(view_name, Product, base_url)
    print('%s/%s/' % (base_url.rstrip('/'), view_name))
    app.add_url_rule(
        '%s/%s/' % (base_url.rstrip('/'), view_name),
        view_func=ProductsListView.as_view('%s_list' % view_name)
    )