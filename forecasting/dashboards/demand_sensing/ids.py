from .components import helpers
''' Generate ids that will be used in the dashboard'''

# Prefix added to all ids
_prefix = 'demand-sensing'

# Chart
DUMMY_DIV_TRIGGER = helpers.generate_html_id(_prefix, 'DUMMY_DIV_TRIGGER')
DIV_CHART = helpers.generate_html_id(_prefix, 'DIV_CHART')
CHART_ORDER_FORECAST = helpers.generate_html_id(_prefix, 'CHART_ORDER_FORECAST')

# Messages
MESSAGE_SUCCESS_SAVE = helpers.generate_html_id(_prefix, 'MESSAGE_SUCCESS_SAVE')

# Buttons
BUTTON_SAVE = helpers.generate_html_id(_prefix, 'BUTTON_SAVE')
BUTTON_SUBMIT_REVIEW = helpers.generate_html_id(_prefix, 'BUTTON_SUBMIT_REVIEW')


# Datatable
DATABLE_FORECAST = helpers.generate_html_id(_prefix, 'DATABLE_FORECAST')
