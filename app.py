import boto3
import flask
import logging
import os
import signal
import sys
import waitress


class Settings:
    @property
    def hosted_zone_ids(self):
        return os.getenv('HOSTED_ZONE_IDS').split()

    @property
    def log_format(self):
        return os.getenv('LOG_FORMAT', '%(levelname)s [%(name)s] %(message)s')

    @property
    def log_level(self):
        return os.getenv('LOG_LEVEL', 'INFO')

    @property
    def version(self):
        return os.getenv('APP_VERSION', 'unknown')


settings = Settings()
app = flask.Flask(__name__)


@app.route('/present', methods=['POST'])
def present():
    data = flask.request.json
    fqdn = data.get('fqdn')
    value = data.get('value')
    app.logger.info(f'Presenting: {fqdn} IN TXT {value}')
    client = boto3.client('route53')
    for hosted_zone_id in settings.hosted_zone_ids:
        client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': fqdn,
                            'Type': 'TXT',
                            'TTL': 30,
                            'ResourceRecords': [
                                {'Value': value}
                            ]
                        }
                    }
                ]
            }
        )
    return 'OK'


@app.route('/cleanup', methods=['POST'])
def cleanup():
    data = flask.request.json
    fqdn = data.get('fqdn')
    value = data.get('value')
    app.logger.info(f'Cleaning up: {fqdn} IN TXT {value}')
    client = boto3.client('route53')
    for hosted_zone_id in settings.hosted_zone_ids:
        client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': fqdn,
                            'Type': 'TXT',
                            'TTL': 30,
                            'ResourceRecords': [
                                {'Value': value}
                            ]
                        }
                    }
                ]
            }
        )
    return 'OK'


def main():
    logging.basicConfig(format=settings.log_format, level=logging.DEBUG, stream=sys.stdout)
    app.logger.debug(f'split-horizon-helper {settings.version}')
    if not settings.log_level == 'DEBUG':
        app.logger.debug(f'Changing log level to {settings.log_level}')
    logging.getLogger().setLevel(settings.log_level)

    waitress.serve(app, ident=None)


def handle_signal(_signal, _frame):
    sys.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, handle_signal)
    main()
