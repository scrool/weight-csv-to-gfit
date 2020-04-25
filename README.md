# weight-csv-to-gfit
Small python script for load bulk weight/steps data to a Google Fit account.
Original code is [here](https://github.com/motherapp/weight-csv-to-gfit).

## Requirements
To run this script, you will need:

 - `python 2.7` 
 - `pip` (sudo apt install python-pip)
 -  `virtualenv` (to get it: pip install virtualenv)

## Download and installation
```
git clone https://github.com/TadWohlrapp/weight-csv-to-gfit.git
cd weight-csv-to-gfit
python -m virtualenv -p /usr/bin/python2.7 venv
source venv/bin/activate
pip install -r requirements.txt
```

There are two options how to access API - register application to create credentials and API key or use OAuth 2.0 Playground to get Authorization Token.


## Input data
1. Export weight data from Withings
2. Place `weight.csv` to the project's main folder


## Acquire OAuth Credentials and API Key
### OAuth client ID
1. Go to https://console.developers.google.com/apis/credentials
2. Create a new OAuth client ID (Create credentials -> OAuth client ID)
3. Set the Redirect URI to the playground: https://developers.google.com/oauthplayground
4. Download the client secret json file, place it in this project's main folder and rename it to `client_secret.json`

### API Key
1. Go to https://console.developers.google.com/apis/credentials
2. Create a new API Key (Create credentials -> API Key)
3. Copy the key and save it as `api_key.txt` in the project's main folder


## Import weight data into Google Fit
```
cd weight
python import_weight_to_gfit.py
```

## Get Authorization Token
1. Go to https://developers.google.com/oauthplayground/
2. In Step 1 Select & Authorize APIs: select https://www.googleapis.com/auth/fitness.body.write under API Fitness 1
3. Authorize use of API on own account
4. In Step 2. Exchange authorization code for tokens: On left side of the screen click on Exchange authorization code for tokens.
5. On right side write down numeric part of `client_id` from the request and `access_token` from the response

## Import weight data into Google Fit
```
cd weight
python import_weight_to_gfit.py <client_id value> <access_token value>
```
