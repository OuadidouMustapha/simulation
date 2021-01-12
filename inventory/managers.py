from django.db import models
from django.db.models import (CharField, FloatField, DecimalField, IntegerField, DateTimeField, Value,
                              ExpressionWrapper, F, Q, Count, Sum, Avg, Subquery, OuterRef, Case, When, Window)
from django.db.models.functions import Concat


class LocationQuerySet(models.QuerySet):
    def get_all_locations(self):
        '''
        return list of unique/distinct locations
        '''
        return self.annotate(label=F('reference'), value=F('id')).values('label', 'value').distinct()

    def get_all_locations_by_attribute(self, attribute):
        '''
        return list of unique/distinct locations based on selected attribute
        '''
        return self.annotate(label=F(attribute), value=F(attribute)).values('label', 'value').order_by(attribute).distinct(attribute)

class StockCheckQuerySet(models.QuerySet):
    def get_all_stock_checks(self):
        '''
        return list of unique/distinct stock_checks
        '''
        return self.annotate(label= F('check_date'), value=F('check_date')).values('label', 'value').distinct()

    def get_all_stock_checks_by_attribute(self, attribute):
        '''
        return list of unique/distinct stock_checks based on selected attribute
        '''
        return self.annotate(label=F(attribute), value=F(attribute)).values('label', 'value').order_by(attribute).distinct(attribute)