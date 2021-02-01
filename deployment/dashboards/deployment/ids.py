from .components import helpers
''' Generate ids that will be used in the dashboard'''

# Prefix added to all ids
_prefix = 'deployment'

# Input fields
DROPDOWN_SHOW_BY = helpers.generate_html_id(_prefix, 'DROPDOWN_SHOW_BY')
INPUT_DATE_RANGE = helpers.generate_html_id(_prefix, 'INPUT_DATE_RANGE')
DATATABLE_TRUCKAVAILABILITY = helpers.generate_html_id(_prefix, 'DATATABLE_TRUCKAVAILABILITY')
BUTTON_RUN = helpers.generate_html_id(_prefix, 'BUTTON_RUN')
BUTTON_SAVE = helpers.generate_html_id(_prefix, 'BUTTON_SAVE')

# Output
MESSAGE_SUCCESS = helpers.generate_html_id(_prefix, 'MESSAGE_SUCCESS')
DATATABLE_DEPLOYMENT = helpers.generate_html_id(_prefix, 'DATATABLE_DEPLOYMENT')
DATATABLE_TRUCK = helpers.generate_html_id(_prefix, 'DATATABLE_TRUCK')


FIGURE_WAREHOUSES_ID = helpers.generate_html_id(_prefix, 'FIGURE_WAREHOUSES_ID')

FIGURE_PIE_ID = helpers.generate_html_id(_prefix, 'FIGURE_PIE_ID')

FIGURE_TOP_ID = helpers.generate_html_id(_prefix, 'FIGURE_TOP_ID')

DROPDOWN_W_PIE_BY = helpers.generate_html_id(_prefix, 'DROPDOWN_W_PIE_BY')

DROPDOWN_T_PIE_BY = helpers.generate_html_id(_prefix, 'DROPDOWN_T_PIE_BY')
DIV_W_PIE_BY = helpers.generate_html_id(_prefix, 'DIV_W_PIE_BY')

DROPDOWN_W_T_BY = helpers.generate_html_id(_prefix, 'DROPDOWN_W_T_BY')
DIV_W_T_BY = helpers.generate_html_id(_prefix, 'DIV_W_T_BY')
