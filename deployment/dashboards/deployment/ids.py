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