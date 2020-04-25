# -------------------------------------------------------------------------------
# Purpose: Load weights.csv and import to a Google Fit account
# Some codes refer to:
# 1. https://github.com/tantalor/fitsync
# 2. http://www.ewhitling.com/2015/04/28/scrapping-data-from-google-fitness/
import json
import httplib2
import re
from apiclient.discovery import build

from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from read_weight_csv import read_weights_csv_with_gfit_format
from googleapiclient.errors import HttpError

# Change these to match your scale
MODEL = 'smart-body-analyzer'
UID = 'ws-50'

f = open('../client_secret.json', 'r')
data = f.read()
jsondata = json.loads(data)
secrets = jsondata['web']

CLIENT_ID = secrets['client_id']
CLIENT_SECRET = secrets['client_secret']

REDIRECT_URI = secrets['redirect_uris'][0]
PROJECT_ID = secrets['project_id']

# See scope here: https://developers.google.com/fit/rest/v1/authorization
SCOPE = 'https://www.googleapis.com/auth/fitness.body.write'

f = open("../api_key.txt", "r")
API_KEY = f.read()


def get_o2authorized_http(client_id, client_secret, redirect_uri):
    flow = OAuth2WebServerFlow(client_id=client_id, client_secret=client_secret, scope=SCOPE, redirect_uri=redirect_uri)
    auth_uri = flow.step1_get_authorize_url()
    print "Copy this url to web browser for authorization: "
    print auth_uri

    # hmm, had to manually pull this as part of a Google Security measure.
    # there must be a way to programatically get this, but this exercise doesn't need it ... yet...
    token = raw_input("Copy the Authorization code and input here: ")
    cred = flow.step2_exchange(token)
    http = httplib2.Http()
    return cred.authorize(http)


def discover_fitness_service(http, developer_key):
    # first step of auth
    return build('fitness','v1', http=http, developerKey=developer_key)


def import_weight_to_gfit():
    http = get_o2authorized_http(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    fitness_service = discover_fitness_service(http, API_KEY)

    # init the fitness objects
    fitusr = fitness_service.users()
    fitdatasrc = fitusr.dataSources()

    data_source = dict(
        type='raw',
        application=dict(name='weight_import'),
        dataType=dict(
          name='com.google.weight',
          field=[dict(format='floatPoint', name='weight')]
        ),
        device=dict(
          type='scale',
          manufacturer='withings',
          model=MODEL,
          uid=UID,
          version='1.0',
        )
      )

    def get_data_source_id(dataSource):
      return ':'.join((
        dataSource['type'],
        dataSource['dataType']['name'],
        re.sub("api-project-", "",PROJECT_ID),
        dataSource['device']['manufacturer'],
        dataSource['device']['model'],
        dataSource['device']['uid']
        ))

    data_source_id = get_data_source_id(data_source)

    # Ensure datasource exists for the device.
    try:
        fitness_service.users().dataSources().get(
            userId='me',
            dataSourceId=data_source_id).execute()
    except HttpError, error:
        if not 'DataSourceId not found' in str(error):
            raise error
        # Doesn't exist, so create it.
        fitness_service.users().dataSources().create(
            userId='me',
            body=data_source).execute()


    weights = read_weights_csv_with_gfit_format('../weight.csv')

    min_log_ns = weights[-1]["startTimeNanos"]
    max_log_ns = weights[0]["startTimeNanos"]
    dataset_id = '%s-%s' % (min_log_ns, max_log_ns)

    # patch data to google fit
    fitness_service.users().dataSources().datasets().patch(
      userId='me',
      dataSourceId=data_source_id,
      datasetId=dataset_id,
      body=dict(
        dataSourceId=data_source_id,
        maxEndTimeNs=max_log_ns,
        minStartTimeNs=min_log_ns,
        point=weights,
      )).execute()

    # read data to verify
    print fitness_service.users().dataSources().datasets().get(
        userId='me',
        dataSourceId=data_source_id,
        datasetId=dataset_id).execute()

if __name__=="__main__":
    import_weight_to_gfit()
