from marshmallow import Schema, fields, ValidationError


class ProductSchema(Schema):
    title = fields.Str(required=True)
    price_rub = fields.Int(required=True)
    product_image = fields.Str(required=False)
    in_store = fields.Bool(required=False)


def is_product_data_valid(product_data):
    errors = ProductSchema().validate(product_data)
    return not errors