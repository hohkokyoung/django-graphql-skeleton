import os
from datetime import timedelta, datetime
from logging.handlers import TimedRotatingFileHandler

"""
Django settings for adrift project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

# Application definition

LOCAL_APPS = [
    "users",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'graphene_django',
    'graphql_jwt.refresh_token.apps.RefreshTokenConfig',
    'django_filters',
    'graphql_auth',
] + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.utils.GraphQLLoggingMiddleware'
]

ROOT_URLCONF = 'adrift.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_USER_MODEL = 'users.User'

WSGI_APPLICATION = 'adrift.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = ["http://localhost:1337"]

GRAPHENE = {
    'SCHEMA': 'api.graphql.schema.schema', # this file doesn't exist yet
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

AUTHENTICATION_BACKENDS = [
    'graphql_auth.backends.GraphQLAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

GRAPHQL_JWT = {
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LONG_RUNNING_REFRESH_TOKEN': True,
    'JWT_EXPIRATION_DELTA': timedelta(days=7),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),    
    'JWT_SECRET_KEY': os.environ.get('JWT_SECRET'),
    'JWT_ALGORITHM': 'HS256',
    "JWT_ALLOW_ANY_CLASSES": [
        "graphql_auth.relay.Register",
        "graphql_auth.relay.VerifyAccount",
        "graphql_auth.relay.ResendActivationEmail",
        "graphql_auth.relay.SendPasswordResetEmail",
        "graphql_auth.relay.PasswordReset",
        "graphql_auth.relay.ObtainJSONWebToken",
        "graphql_auth.relay.VerifyToken",
        "graphql_auth.relay.RefreshToken",
        "graphql_auth.relay.RevokeToken",
    ],
}

GRAPHQL_AUTH = {
    "LOGIN_ALLOWED_FIELDS": ["username"],
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


class DateBasedFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, *args, **kwargs):
        self.log_file = filename
        self.update_filename()
        super().__init__(self.current_log_path, *args, **kwargs)

    def update_filename(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        dated_dir = os.path.join("logs", current_date)
        if not os.path.exists(dated_dir):
            os.makedirs(dated_dir)
        self.current_log_path = os.path.join(dated_dir, self.log_file)

    def doRollover(self):
        self.update_filename()
        self.baseFilename = self.current_log_path
        super().doRollover()

LOGGING = {
    'version': 1,
    'disable_existing_loggers' : False,
    'loggers': {
        'general': {
            'handlers': ['console', 'info', 'debug', 'warning', 'error', 'critical'],
            'level': 'DEBUG',
            "propagate": False,
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        },
        'info': {
            'class': 'adrift.settings.DateBasedFileHandler',
            'filename': "info.log",
            'level': 'INFO',
            'formatter': 'simple',
            'when': 'midnight',
            'interval': 1,
        },
        'debug': {
            'class': 'adrift.settings.DateBasedFileHandler',
            'filename': "debug.log",
            'level': 'DEBUG',
            'formatter': 'simple',
            'when': 'midnight',
            'interval': 1,
        },
        'warning': {
            'class': 'adrift.settings.DateBasedFileHandler',
            'filename': "warning.log",
            'level': 'WARNING',
            'formatter': 'verbose',
            'when': 'midnight',
            'interval': 1,
        },
        'error': {
            'class': 'adrift.settings.DateBasedFileHandler',
            'filename': "error.log",
            'level': 'ERROR',
            'formatter': 'verbose',
            'when': 'midnight',
            'interval': 1,
        },
        'critical': {
            'class': 'adrift.settings.DateBasedFileHandler',
            'filename': "critical.log",
            'level': 'CRITICAL',
            'formatter': 'verbose',
            'when': 'midnight',
            'interval': 1,
        }
    },
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(module)s | %(levelname)s] %(message)s',
        },
        'verbose': {
            'format': '%(asctime)s [%(module)s | %(levelname)s] %(message)s @ %(pathname)s : %(lineno)d : %(funcName)s',
        },
    },
}