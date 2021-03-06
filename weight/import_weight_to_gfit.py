# -------------------------------------------------------------------------------
# Purpose: Load weights.csv and import to a Google Fit account
# Some codes refer to:
# 1. https://github.com/tantalor/fitsync
# 2. http://www.ewhitling.com/2015/04/28/scrapping-data-from-google-fitness/
import json
import httplib2
import re
import sys
from apiclient.discovery import build, build_from_document

from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import AccessTokenCredentials
from read_weight_csv import read_weights_csv_with_gfit_format
from googleapiclient.errors import HttpError


# Trusted testers can download discovery document from the developers page:
# https://www.googleapis.com/discovery/v1/apis/fitness/v1/rest
# and direct following constant its filename, e.g.
# "../fitness-v1-discoverydocument.json"
DISCOVERY_FILE = None

# Change these to match your scale
MODEL = 'smart-body-analyzer'
UID = 'ws-50'

# See scope here: https://developers.google.com/fit/rest/v1/authorization
SCOPE = 'https://www.googleapis.com/auth/fitness.body.write'


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

def get_o2authorized_http_token(access_token):
    credentials = AccessTokenCredentials(access_token, 'weight-csv-to-gfit/1.0')
    http = httplib2.Http()
    return credentials.authorize(http)


def read_fitness_service(http, discovery_json_data):
    jsondata = json.loads(doc)
    return build_from_document(jsondata, http=http)


def discover_fitness_service(http, developer_key):
    # first step of auth
    return build('fitness','v1', http=http, developerKey=developer_key)


def import_weight_to_gfit(fitness_service, project_id):
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
        re.sub("api-project-", "", project_id),
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
    if len(sys.argv) == 3:
        project_id = sys.argv[1]
        http = get_o2authorized_http_token(sys.argv[2])
    else:
        f = open('../client_secret.json', 'r')
        data = f.read()
        jsondata = json.loads(data)
        secrets = jsondata['web']

        project_id = secrets['project_id']

        http = get_o2authorized_http(secrets['client_id'], secrets['client_secret'], secrets['redirect_uris'][0])

    if not DISCOVERY_FILE:
        f = open("../api_key.txt", "r")
        api_key = f.read()
        fitness_service = discover_fitness_service(http, api_key)
    else:
        with open(DISCOVERY_FILE, "r") as f:
            doc = f.read()
        fitness_service = read_fitness_service(http, doc)

    import_weight_to_gfit(fitness_service, project_id)
