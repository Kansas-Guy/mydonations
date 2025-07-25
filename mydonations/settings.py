import os
import environ
import dj_database_url

from pathlib import Path

# Build paths inside the project like this:
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)
# Read the .env file from project root
env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY
SECRET_KEY = env('SECRET_KEY')  # Must be set in .env
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['mydonations-7bb26315ee30.herokuapp.com',
                 '127.0.0.1',
                 'localhost,']

DATABASES = {
    'default': dj_database_url.config(default=env('DATABASE_URL'))
}
SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = None
CSRF_COOKIE_SECURE = True
BBMS_PUBLIC_KEY= env('BBMS_PUBLIC_KEY')
BBMS_MERCHANT_ID= env('BBMS_MERCHANT_ID')
BB_API_SUBSCRIPTION = env('BB_API_SUBSCRIPTION')
BB_CLIENT_ID = env('BB_CLIENT_ID')
BB_CLIENT_SECRET = env('BB_CLIENT_SECRET')
BB_TOKEN_URL = env('BB_TOKEN_URL')
BB_OAUTH_SCOPES = env('BB_OAUTH_SCOPES')
BB_REFRESH_TOKEN = env('BB_REFRESH_TOKEN')
SENDGRID_API_KEY= env('SENDGRID_API_KEY')
SENDGRID_RECEIPT_TEMPLATE_ID= env('SENDGRID_RECEIPT_TEMPLATE_ID')
DEFAULT_FROM_EMAIL = 'foundationmail@fhsu.edu'
BB_REDIRECT_URI = 'https://mydonations-7bb26315ee30.herokuapp.com/skyapi/oauth/callback'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'donations',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mydonations.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': []
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mydonations.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default=env('DATABASE_URL'))
}

# Local development fallback (SQLite)
# If DATABASE_URL is not set, use SQLite for quick local testing
if not env('DATABASE_URL', default=None):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'donations', 'static'),
]

STATIC_URL = '/static/'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
