import pytest


@pytest.fixture
def nocache(settings):
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
