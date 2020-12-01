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


# class VersionFilterFormHelper(FormHelper):
#     form_method = 'GET'
#     layout = Layout(
#         'reference', 'year', 'month', 'forecast_type', 'description',
#         Submit('submit', _('Submit'))
#     )


class VersionForm(forms.ModelForm):
    reference = forms.CharField(disabled=True)
    year = forms.CharField(disabled=True)
    month = forms.CharField(disabled=True)
    forecast_type = forms.CharField(disabled=True)

    class Meta:
        model = Version
        fields = ('reference', 'year', 'month', 'forecast_type', 'is_budget', 'file_path', 'description', )

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
                Column('year', css_class='form-group col-md-3 mb-0'),
                Column('month', css_class = 'form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('file_path', css_class='form-group col-md-6 mb-0'),
                Column('description', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('is_budget', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', _('Submit'))
        )



    def clean(self):
        cleaned_data = super().clean()
        # write_through=True prevents TextIOWrapper from buffering internally;
        # you could replace it with explicit flushes, but you want something
        # to ensure nothing is left in the TextIOWrapper when you detach
        # csv_file = self.cleaned_data.get(
        #     'file_path').file.read().decode('utf-8')

        # self.save_csv_data(csv_file, version_id)

        # f = TextIOWrapper(csv_file, encoding='utf-8')
        # try:
        #     result_csvlist = csv.DictReader(f)
        #     event_info = next(result_csvlist)
        #     print(event_info)
        # finally:
        #     # Detaches input_io so it won't be closed when text_input cleaned up
        #     f.detach()



    def save_csv_data(self, csv_file, version_id):
        # Prepare data to process
        model_resource = ForecastResource()
        dataset = Dataset()

        imported_data = dataset.load(csv_file, format='csv')
        print('imported_data ', imported_data)
        # Append version column (pk of Version)
        imported_data = imported_data.append_col(
            (version_id,) * dataset.height, header='version')

        # Test the data import
        result = model_resource.import_data(
            dataset, dry_run=True)
        print('Data import tested')
        print*('result ', result)
        if result.has_errors():
            raise ValidationError(
                _('Warning: An error has occurred while processing the file')
            )
        else:
            # Actually import now
            model_resource.import_data(
                dataset, dry_run=False)
            print('data imported')

    #     # send email using the self.cleaned_data dictionary
    #     pass



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
