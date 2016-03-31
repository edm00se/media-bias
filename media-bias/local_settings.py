import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'twitterdata',
        'USER': 'aspittel',
        'PASSWORD':'Sp.51141',
        'HOST': 'localhost',
        'PORT':'5432',
    }
}

DEBUG = True
