import keyring
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
from functools import partial
import threading
import urllib.parse
import datetime
import requests
import traceback
from hdbcli import dbapi
import polars as pl
import pandas as pd
import os
from hana_ml.dataframe import ConnectionContext, create_dataframe_from_pandas

config_file_g = ''
Browser_override_g = ''
data_frame_type_g = 'pandas' # Default data frame type for hana_sql function
debug = False

def initialize_settings(config_file = '', Browser_override = '', data_frame_type = 'pandas'):
    """
    Initializes global settings for the Hana Cloud interface.

    Parameters:
    config_file (str): Path to the configuration file.
    Browser_override (str): Optional browser override for OAuth authentication.
    data_frame_type (str): Default data frame type for SQL query results ('pandas' or 'polars').

    Sets global variables for configuration file path, browser override, and data frame type.
    """
    global config_file_g, Browser_override_g, data_frame_type_g
    config_file_g = config_file
    Browser_override_g = Browser_override
    data_frame_type_g = data_frame_type
    
    
    
def test_connection(oauth_config):
    oauth_Token = keyring.get_password('SAP_hana_sso', 'oauth_Token')
    
    if not oauth_Token:
        if debug: print('No existing token found')
        return False
    else:
        oauth_Token = json.loads(oauth_Token)
        try:    # Try to connect to server and automatically revalidate if It can't connect
            cursor = dbapi.connect(address=oauth_Token['prod_URL'],port='443',authenticationMethods='jwt',password=oauth_Token['access_token'],encrypt=True, sslValidateCertificate=True).cursor()
            #cursor.close() 
            
            age_Token =  datetime.datetime.now() -datetime.datetime.strptime(oauth_Token['time'], "%m/%d/%Y, %H:%M:%S")
            if debug: print('Connection successful token is {} mins old'.format(age_Token.seconds/60))
            
            if age_Token.seconds/60 > 30:
                if debug: print('Token is over 30 mins old will refresh')
                refresh_access_token(oauth_Token['refresh_token'],oauth_config)
        except :
            if debug: print("Error during connection attempt:")
            if debug: traceback.print_exc()
            # old token is invalid delete it
            keyring.delete_password('SAP_hana_sso', 'config_data')
            if debug: print('Connection failed')
            return False
        return cursor

def refresh_access_token(refresh_token,oauth_config): # Refreshers token
    token_url = oauth_config['TOKEN_URL']
    # Set up the request payload
    payload = {
        'grant_type': 'refresh_token',
        'client_id': oauth_config['CLIENT_ID'],
        'client_secret': oauth_config['CLIENT_SECRET'],
        'refresh_token': refresh_token
    }
    # Make the request to the token endpoint
    response = requests.post(token_url, data=payload)

    # Check if the request was successful
    if response.status_code == 200:
        # save to json
        token_response = response.json()
        
        dictionary = {
            "time": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            "access_token": token_response['access_token'],
            "refresh_token": token_response['refresh_token'],
            "prod_URL":oauth_config['HC_prod_URL'],
        }
        keyring.set_password('SAP_hana_sso', 'oauth_Token', json.dumps(dictionary))

        return
    else:
        response.raise_for_status()
        
        
# A class that runs the HTTP Server Responses
class RequestHandler(BaseHTTPRequestHandler):

    def __init__(self, oauth_input, *args, **kwargs):
        self.oauth_config = oauth_input
        # BaseHTTPRequestHandler calls do_GET **inside** __init__ !!!
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        # Parse the query parameters
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        # Check if the path is the callback path
        if self.path.startswith('/callback'):
            # Extract the authorization code
            authorization_code = query_components.get('code')
            if authorization_code:
                authorization_code = authorization_code[0]
                
                # Exchange the authorization code for an access token
                access_token,refresh_token = self.exchange_code_for_token(authorization_code)

                # Respond to the client
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Authorization code received. You can close this window.")
            
                # save to json
                dictionary = {
                    "time": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    "access_token": access_token,
                    "refresh_token":refresh_token,
                    "prod_URL":self.oauth_config['HC_prod_URL'],
                }
                keyring.set_password('SAP_hana_sso', 'oauth_Token', json.dumps(dictionary))

                threading.Thread(target=self.shutdown_server).start()
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Authorization code not found in the query parameters.")
                
    def exchange_code_for_token(self, code):
        # Prepare the token request payload
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.oauth_config['REDIRECT_URI'],
            'client_id': self.oauth_config['CLIENT_ID'],
            'client_secret': self.oauth_config['CLIENT_SECRET']
        }
        # Make the POST request to exchange the authorization code for an access token
        response = requests.post(self.oauth_config['TOKEN_URL'], data=payload)
        if response.status_code == 200:
            token_data = response.json()
            return token_data['access_token'],token_data['refresh_token']
        else:
            raise Exception(f"Failed to obtain access token: {response.status_code} {response.text}")               
    # Function to shut down the server
    def shutdown_server(self):
        print('end')
        self.server.shutdown()    
        
        
# Requests a new token
def get_token(i=0):
    #print('get token', i)
    oauth_config = config_reader() 
    result = test_connection(oauth_config)
    if not result:

        

        params = {
        'response_type': 'code',
        'client_id': oauth_config['CLIENT_ID'],
        'redirect_uri': oauth_config['REDIRECT_URI'],
        'scope': oauth_config['SCOPE']
        }
        authorization_url = f"{oauth_config['AUTH_URL']}?{urllib.parse.urlencode(params)}"

        # Open web browser and go to oauth url
        if Browser_override_g != '':
            webbrowser.get(Browser_override_g).open(authorization_url,new=1)
        else:
            webbrowser.open(authorization_url,new=1)
            
        server_address = ('', 8080)
        handler = partial(RequestHandler, oauth_config)
        httpd = HTTPServer(server_address, handler)
        httpd.timeout = 10  # timeout

        httpd.handle_request() 
        
        
        # see if function timed out and failed
        if i > 0:
            raise TimeoutError('Failed to get token after 2 attempts')
        if keyring.get_password('SAP_hana_sso', 'oauth_Token') is None:
            print('Request Timed out will try again')

        return get_token(i+1)
    else:
        return result


# returns configuration data for single sign on from either file or keychain
def config_reader():
    # reads config data from keychain
    config_data = keyring.get_password('SAP_hana_sso', 'config_data')
    if not config_data: # If there is no existing config data saved to the credentials manager read from file and save it
        if not os.path.exists(config_file_g):
            raise FileNotFoundError(f"Config file not found: {config_file_g}")
        with open(config_file_g) as file:
            config_data = json.load(file)
        keyring.set_password('SAP_hana_sso', 'config_data', json.dumps(config_data))
        return config_data
    else:
        return json.loads(config_data)




def hana_sql(sql_command='test',DF_type = data_frame_type_g):
    """ handles single sign on then runs a SQL command

    Parameters:
    sql_command (str): SQL command to run or 'test' to just validate token
    df_type (str): Type of data frame to return ('pandas' or 'polars') defaults to pandas

    Returns:
    data frame of type specified in df_type

    """
    cursor = get_token()

    #cursor = dbapi.connect(address=oauth_Token['prod_URL'],port='443',authenticationMethods='jwt',password=oauth_Token['access_token'],encrypt=True, sslValidateCertificate=True).cursor()

    cursor.execute(sql_command) # Run SQL command
    # Retrieve data and convert it to a pandas data frame
    data = cursor.fetchall() 
    data_name = [i[0] for i in cursor.description] 
    cursor.close() 

    
    if DF_type == 'pandas':
        return pd.DataFrame(data,columns=data_name)
    elif DF_type == 'polars':
        data = [row.column_values for row in data]
        return pl.DataFrame(data,orient='row',schema=data_name)
    else:
        raise ValueError("DF_type must be either 'pandas' or 'polars'")

def hana_upload(data, data_name, SCHEMA):
    """
    Uploads a pandas DataFrame to an SAP HANA Cloud table.
    Args:
        data (pandas.DataFrame): The DataFrame to upload to HANA.
        data_name (str): The name of the target table in HANA.
        SCHEMA (str): The schema in which the table resides.
    Returns:
        bool: True if the upload is successful.
    Notes:
        - Uses JWT authentication to connect to SAP HANA Cloud.
        - Overwrites the target table if it exists (force=True, replace=True).
        - Requires valid OAuth token stored in the system keyring under 'SAP_hana_sso'.
    """


    cursor = get_token()
    cursor.close()

    #oauth_config = config_reader() 
    oauth_Token = keyring.get_password('SAP_hana_sso', 'oauth_Token')
    oauth_Token = json.loads(oauth_Token)
    
    conn = ConnectionContext(address=oauth_Token['prod_URL'],port='443',authenticationMethods='jwt',password=oauth_Token['access_token'],encrypt=True, sslValidateCertificate=True) 

    create_dataframe_from_pandas(conn, data, data_name,
                                schema=SCHEMA, 
                                force=True, # True: truncate and insert
                                replace=True) # True: Null is replaced by 0
    return True