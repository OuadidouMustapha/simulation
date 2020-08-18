from django import template
register = template.Library()

# @register.inclusion_tag('_product_category_tree.html')
# def product_category_tree(product_category_list):
#     return {'product_category_list': product_category_list}
