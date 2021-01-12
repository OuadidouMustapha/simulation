from django.core.exceptions import ValidationError
from tablib import Dataset
import csv
from io import TextIOWrapper
from .models import Version, Forecast
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.utils.translation import gettext as _
from .resources import ForecastResource
from account.models import CustomUser


# class VersionFilterFormHelper(FormHelper):
#     form_method = 'GET'
#     layout = Layout(
#         'reference', 'year', 'month', 'forecast_type', 'description',
#         Submit('submit', _('Submit'))
#     )


class VersionForm(forms.ModelForm):
    reference = forms.CharField(disabled=True)
    # year = forms.CharField(disabled=True)
    # month = forms.CharField(disabled=True)
    forecast_type = forms.CharField(disabled=True)

    class Meta:
        model = Version
        fields = ('reference', 'forecast_type',
                  'file_path', 'description',)
        exclude = ('created_by',)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.attrs = {'novalidate': ''}
        self.helper.layout = Layout(
            Row(
                Column('reference',
                       css_class='form-group col-md-3 mb-0'),
                Column('forecast_type', css_class='form-group col-md-3 mb-0'),
                # Column('year', css_class='form-group col-md-3 mb-0'),
                # Column('month', css_class = 'form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('file_path', css_class='form-group col-md-6 mb-0'),
                Column('description', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            # Row(
            #     Column('is_budget', css_class='form-group col-md-4 mb-0'),
            #     css_class='form-row'
            # ),
            Submit('submit', _('Submit'))
        )


class VersionReviewForm(forms.ModelForm):
    # created_by = forms.CharField(disabled=True)

    class Meta:
        model = Version
        fields = ('approved_by',)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['approved_by'].queryset = CustomUser.objects.filter(groups__name='supervisor')

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.attrs = {'novalidate': ''}
        self.helper.layout = Layout(
            Row(
                Column('approved_by',
                       css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', _('Submit'))
        )

class ForecastForm(forms.ModelForm):
    class Meta:
        model = Forecast
        fields = ('category', 'warehouse',
                  'forecast_date', 'forecasted_quantity',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.attrs = {'novalidate': ''}
        self.helper.form_class = 'form-horizontal'

        self.helper.layout = Layout(
            Row(
                Column('category', css_class='form-group col-md-3 mb-0'),
                Column('warehouse', css_class='form-group col-md-2 mb-0'),
                Column('forecast_date', css_class='form-group col-md-2 mb-0'),
                Column('forecasted_quantity', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', _('Submit'))
        )
