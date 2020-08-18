"""
WSGI config for orchest project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# # The following dashapp import is used to fix Dash `Plotly Dash Error loading layout` issue
# # See https://community.plot.ly/t/dash-pythonanywhere-deployment-issue/5062/8
# from dashapp import server as application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orchest.settings')

application = get_wsgi_application()

