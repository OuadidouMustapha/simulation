from django.apps import AppConfig


class ForecastingConfig(AppConfig):
    name = 'forecasting'

    # NOTE this is needed to import signals module
    def ready(self):
        import forecasting.signals
