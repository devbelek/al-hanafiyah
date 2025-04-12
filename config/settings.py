import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    DB_NAME=(str, 'hanafi'),
    DB_USER=(str, 'ustaz'),
    DB_PASSWORD=(str, 'ustaz'),
    DB_HOST=(str, 'db'),
    DB_PORT=(str, '5432'),
    TELEGRAM_BOT_TOKEN=(str, ''),
)

env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)
else:
    env_file = os.path.join(BASE_DIR, 'config', '.env')
    if os.path.exists(env_file):
        environ.Env.read_env(env_file)
    else:
        print(f"Файл .env не найден в {BASE_DIR} или {os.path.join(BASE_DIR, 'config')}")

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'ckeditor',
    'adminsortable2',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'drf_yasg',
    'django_elasticsearch_dsl',
    'rest_framework.authtoken',

    'apps.lessons',
    'apps.questions',
    'apps.articles',
    'apps.events',
    'apps.search',
    'apps.accounts',
    'apps.notifications',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='hanafi'),
        'USER': env('DB_USER', default='ustaz'),
        'PASSWORD': env('DB_PASSWORD', default='ustaz'),
        'HOST': env('DB_HOST', default='db'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / "db.sqlite3",
#     }
# }

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

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Bishkek'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CKEditor settings
CKEDITOR_CONFIGS = {
    'basic': {
        'toolbar': [
            ['Bold', 'Italic', 'Underline', '-',
             'NumberedList', 'BulletedList', '-',
             'JustifyLeft', 'JustifyCenter', 'JustifyRight',
             'Source'],
        ],
        'width': 'auto',
        'height': '200px',
        'removePlugins': 'elementspath',
        'toolbarCanCollapse': True,
        'uiColor': '#f0f0f0',
    },
    'default': {
        'toolbar': [
            ['Format', 'Font', 'FontSize', 'Bold', 'Italic', 'Underline', '-',
             'NumberedList', 'BulletedList', '-', 'JustifyLeft', 'JustifyCenter',
             'JustifyRight', 'JustifyBlock', 'Image', 'Link', 'Unlink', 'Table',
             'Source', 'Maximize'],
        ],
        'width': 'auto',
        'height': '200px',
        'toolbarCanCollapse': True,
        'uiColor': '#f0f0f0',
        'removePlugins': 'elementspath',
        'extraPlugins': 'font,maximize',
        'fontSize_sizes': (
            '8/8px;9/9px;10/10px;11/11px;12/12px;14/14px;16/16px;18/18px;'
            '20/20px;22/22px;24/24px;26/26px;28/28px;36/36px;48/48px;72/72px'
        ),
        'font_names': (
            'Arial/Arial, Helvetica, sans-serif;'
            'Times New Roman/Times New Roman, Times, serif;'
            'Verdana'
        ),
    },
}

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_IMAGE_BACKEND = "pillow"

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://elasticsearch:9200',
        'timeout': 30,
    }
}

ELASTICSEARCH_DSL_INDEX_SETTINGS = {
    'number_of_shards': 1,
    'number_of_replicas': 0,
    'analysis': {
        'analyzer': {
            'custom_analyzer': {
                'type': 'custom',
                'tokenizer': 'standard',
                'filter': [
                    'lowercase',
                    'stop',
                    'russian_stemmer',
                    'word_delimiter'
                ]
            }
        },
        'filter': {
            'russian_stemmer': {
                'type': 'stemmer',
                'language': 'russian'
            }
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

GOOGLE_OAUTH2_CLIENT_ID = env('GOOGLE_OAUTH2_CLIENT_ID', default='')
GOOGLE_OAUTH2_CLIENT_SECRET = env('GOOGLE_OAUTH2_CLIENT_SECRET', default='')

PWA_APP_NAME = 'Al-Hanafiyah'
PWA_APP_DESCRIPTION = 'Исламская образовательная платформа'
PWA_APP_THEME_COLOR = '#4CAF50'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_START_URL = '/'
PWA_APP_ICONS = [
    {
        'src': '/static/pwa/icons/icon-192x192.png',
        'sizes': '192x192',
        'type': 'image/png'
    }
]

TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', default='')
from .static_settings import *
