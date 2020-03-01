# weight-csv-to-gfit
Small python script for load bulk weight/steps data to a Google Fit account.
Original code is [here](https://github.com/motherapp/weight-csv-to-gfit).

## Requirements
To run this script, you will need:

 - `python 2.7` 
 - `pip` 
 -  `virtualenv` (to get it: pip install virtualenv)

## Download and installation
```
git clone https://github.com/TadWohlrapp/weight-csv-to-gfit.git
cd weight-csv-to-gfit
virtualenv -p /usr/bin/python2.7 venv
pip install -r requirements.txt
```

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
