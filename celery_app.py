from __future__ import absolute_import

import json

import celery
from celery import signals
from raven import Client as RavenClient
from raven.contrib.celery import register_signal, register_logger_signal


with open("settings.json") as fin:
    SETTINGS = json.loads(fin.read())


class Celery(celery.Celery):
    def on_configure(self):
        client = RavenClient(SETTINGS.get('sentry_dsn'))

        # register a custom filter to filter out duplicate logs
        register_logger_signal(client)

        # hook into the Celery error handler
        register_signal(client)


celery_app = Celery(SETTINGS.get('app_name'), broker=SETTINGS.get('broker'))
celery_app.conf.update(
    CELERY_ACCEPT_CONTENT=['pickle', 'json'],
    BROKER_URL=SETTINGS.get('broker'),
    CELERY_RESULT_BACKEND=SETTINGS.get('backend'),
    CELERY_ENABLE_UTC=True,
    CELERY_DEFAULT_QUEUE='quickbooks',
    CELERYD_HIJACK_ROOT_LOGGER=False,
    IGNORE_RESULT=False
)


