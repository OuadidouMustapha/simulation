from .components import helpers
''' Generate ids that will be used in the dashboard'''

# Prefix added to all ids
_prefix = 'forchest'

# Dropdowns
DROPDOWN_PRODUCT = helpers.generate_html_id(_prefix, 'DROPDOWN_PRODUCT')
DROPDOWN_CIRCUIT = helpers.generate_html_id(_prefix, 'DROPDOWN_CIRCUIT')
DROPDOWN_ABC = helpers.generate_html_id(_prefix, 'DROPDOWN_ABC')
DROPDOWN_FMR = helpers.generate_html_id(_prefix, 'DROPDOWN_FMR')
DROPDOWN_FORECAST_ACCURACY = helpers.generate_html_id(_prefix, 'DROPDOWN_FORECAST_ACCURACY')
DROPDOWN_FORECAST_STATUS = helpers.generate_html_id(_prefix, 'DROPDOWN_FORECAST_STATUS')

# Cards
CARD_NUM_ACHIEVED_SEGMENTS = helpers.generate_html_id(_prefix, 'CARD_NUM_ACHIEVED_SEGMENTS')
CARD_NUM_APPROVED_SEGMENTS = helpers.generate_html_id(_prefix, 'CARD_NUM_APPROVED_SEGMENTS')
CARD_NUM_REMAINING_SEGMENTS = helpers.generate_html_id(_prefix, 'CARD_NUM_REMAINING_SEGMENTS')

# Chart
CHART_ORDER_FORECAST = helpers.generate_html_id(_prefix, 'CHART_ORDER_FORECAST')
CHART_ORDER_FORECAST_COMPONENTS = helpers.generate_html_id(_prefix, 'CHART_ORDER_FORECAST_COMPONENTS')

# Datatable
DATABLE_HISTORY = helpers.generate_html_id(_prefix, 'DATABLE_HISTORY')
DATABLE_FORECAST = helpers.generate_html_id(_prefix, 'DATABLE_FORECAST')