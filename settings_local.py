import os

# Django settings for oscar project.
location = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': location('db.sqlite'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'ATOMIC_REQUESTS': True
    },
}