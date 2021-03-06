#!/usr/bin/env python
import os
import sys
import logging

sys.path.insert(0, 'sandbox')

from django.conf import settings

from oscar import get_core_apps
from oscar.defaults import OSCAR_SETTINGS
from oscar import OSCAR_MAIN_TEMPLATE_DIR

location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), x)

EWAY_RUN_EXTERNAL_TESTS = int(os.environ.get('EWAY_RUN_EXTERNAL_TESTS', 0))


def configure():
    if not settings.configured:
        OSCAR_SETTINGS['OSCAR_ALLOW_ANON_CHECKOUT'] = True

        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            SITE_ID=1,
            MEDIA_ROOT=location('public/media'),
            MEDIA_URL='/media/',
            STATIC_URL='/static/',
            STATICFILES_DIRS=(location('static/'),),
            STATIC_ROOT=location('public'),
            STATICFILES_FINDERS=(
                'django.contrib.staticfiles.finders.FileSystemFinder',
                'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                'compressor.finders.CompressorFinder',
            ),
            TEMPLATE_LOADERS=(
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ),
            TEMPLATE_CONTEXT_PROCESSORS = (
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.request",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.static",
                "django.contrib.messages.context_processors.messages",
                # Oscar specific
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
            ),
            MIDDLEWARE_CLASSES=(
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'debug_toolbar.middleware.DebugToolbarMiddleware',
                'oscar.apps.basket.middleware.BasketMiddleware',
            ),
            ROOT_URLCONF='sandbox.urls',
            TEMPLATE_DIRS=(
                location('sandbox/templates'),
                os.path.join(OSCAR_MAIN_TEMPLATE_DIR, 'templates'),
                OSCAR_MAIN_TEMPLATE_DIR,
            ),
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.sites',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'django.contrib.admin',
                'django.contrib.flatpages',
                'eway',
                'compressor',
            ] + get_core_apps(
                'sandbox.apps.checkout',
            ),
            AUTHENTICATION_BACKENDS=(
                'oscar.apps.customer.auth_backends.Emailbackend',
                'django.contrib.auth.backends.ModelBackend',
            ),
            LOGIN_REDIRECT_URL='/accounts/',
            APPEND_SLASH=True,
            HAYSTACK_CONNECTIONS={
                'default': {
                    'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
                },
            },
            EWAY_API_KEY=os.environ.get('EWAY_API_KEY'),
            EWAY_PASSWORD=os.environ.get('EWAY_PASSWORD'),
            EWAY_USE_SANDBOX=True,
            EWAY_RUN_EXTERNAL_TESTS=(EWAY_RUN_EXTERNAL_TESTS > 0),
            EWAY_CURRENCY="AUD",
            NOSE_ARGS=[
                '-s',
                '--with-specplugin',
            ],
            **OSCAR_SETTINGS
        )

logging.disable(logging.CRITICAL)


def run_tests(*test_args):
    from django_nose import NoseTestSuiteRunner
    test_runner = NoseTestSuiteRunner(verbosity=1)
    if not test_args:
        test_args = ['tests']
    num_failures = test_runner.run_tests(test_args)
    if num_failures:
        sys.exit(num_failures)


if __name__ == '__main__':
    configure()
    run_tests(*sys.argv[1:])
