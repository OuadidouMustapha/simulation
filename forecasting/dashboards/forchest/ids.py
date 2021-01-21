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
MESSAGE_APPROVE = helpers.generate_html_id(_prefix, 'MESSAGE_APPROVE')
MESSAGE_REJECT = helpers.generate_html_id(_prefix, 'MESSAGE_REJECT')
MESSAGE_SUCCESS_SENT_FOR_REVIEW = helpers.generate_html_id(_prefix, 'MESSAGE_SUCCESS_SENT_FOR_REVIEW')

# Buttons
BUTTON_APPROVE = helpers.generate_html_id(_prefix, 'BUTTON_APPROVE')
BUTTON_REJECT = helpers.generate_html_id(_prefix, 'BUTTON_REJECT')
BUTTON_EVENT_ADD = helpers.generate_html_id(_prefix, 'BUTTON_EVENT_ADD')
BUTTON_EVENT_UPDATE = helpers.generate_html_id(_prefix, 'BUTTON_EVENT_UPDATE')
BUTTON_SAVE = helpers.generate_html_id(_prefix, 'BUTTON_SAVE')
BUTTON_SUBMIT_REVIEW = helpers.generate_html_id(_prefix, 'BUTTON_SUBMIT_REVIEW')
# Modal
MODAL_DIV = helpers.generate_html_id(_prefix, 'MODAL_DIV')
# MODAL_BODY = helpers.generate_html_id(_prefix, 'MODAL_BODY')
MODAL_DROPDOWN_USER = helpers.generate_html_id(_prefix, 'MODAL_DROPDOWN_USER')
MODAL_BUTTON_CLOSE = helpers.generate_html_id(_prefix, 'MODAL_BUTTON_CLOSE')
MODAL_BUTTON_SUBMIT = helpers.generate_html_id(_prefix, 'MODAL_BUTTON_SUBMIT')


# Datatable
DATABLE_FORECAST = helpers.generate_html_id(_prefix, 'DATABLE_FORECAST')
DATABLE_EVENTS = helpers.generate_html_id(_prefix, 'DATABLE_EVENTS')
