
from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
import pymysql
import tempfile

pymysql.install_as_MySQLdb()

# Load environment variables from .env file (see .env for required keys)
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]
# Allow dynamic override from .env
_env_hosts = os.getenv("ALLOWED_HOSTS")
if _env_hosts:
    ALLOWED_HOSTS = [h.strip() for h in _env_hosts.split(',') if h.strip()]

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", 24))

# Email settings (provide safe defaults for development)
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "noreply@aubevents.local")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# Optional: Auto-configure SendGrid via SMTP if SENDGRID_API_KEY provided.
# (Do NOT commit real keys. Use .env file; ensure .env is in .gitignore.)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
if SENDGRID_API_KEY:
    # Override to SendGrid SMTP
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.sendgrid.net"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = "apikey"  # Per SendGrid spec
    EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@aubevents.com")

# Explicit verified sender (Single Sender or domain-authenticated address) for SendGrid.
# Falls back to DEFAULT_FROM_EMAIL if not provided.
VERIFIED_FROM_EMAIL = os.getenv("VERIFIED_FROM_EMAIL", DEFAULT_FROM_EMAIL)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    "accounts",
    "rest_framework", 
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
## CORS settings for local frontend development
# CORS dynamic origins
_cors_env = os.getenv("CORS_ORIGINS")
if _cors_env:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_env.split(',') if o.strip()]
else:
    CORS_ALLOWED_ORIGINS = [
        # Localhost variants commonly used by dev servers
        "http://localhost:5173",   # Vite default
        "http://127.0.0.1:5173",   # Vite opened via 127.0.0.1
        "http://localhost:3000",   # CRA/Next.js default
        "http://127.0.0.1:3000",   # CRA opened via 127.0.0.1
    ]
# For quick demo only (not for prod):
# CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'backend.urls'

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
TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'frontend', 'dist')]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Database (uses MySQL from .env if available)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
    # Set MySQL engine to use PyMySQL
    DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'
    
    # Add SSL CA if file path is provided
    ca_path = os.environ.get("MYSQL_SSL_CA_PATH")
    if ca_path and os.path.exists(ca_path):
        DATABASES['default']['OPTIONS'] = {
            'ssl': {'ca': ca_path}
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'frontend' / 'dist',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

