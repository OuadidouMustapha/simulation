'''This file defines which configuration to use, depending on the environment'''
import os
import importlib
from decouple import config


# by default use production
ENV_ROLE = config('ENV_ROLE')

env_settings = importlib.import_module(f'orchest.settings.{ENV_ROLE}')

globals().update(vars(env_settings))

try:
  # import local settings if present
  from .local import *  # noqa
except ImportError:
  pass
