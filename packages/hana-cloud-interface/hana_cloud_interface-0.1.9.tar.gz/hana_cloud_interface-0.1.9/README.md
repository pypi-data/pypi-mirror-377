# Usage of the `hana_cloud_interface` package 

This package provides a simple interface to connect to SAP HANA Cloud databases and execute SQL queries. Below are some examples of how to use the package.


## example
the main function is very simple It takes a SQL command as a string and returns the data
```python
import hana_cloud_interface as hci

sql_command = """
SELECT top 10
    "data1"
    "data2"
FROM "table1"
"""
    
data = hci.hana_sql(sql_command)

```

## initialising settings
Before using the package, you need to initialize the settings by specifying the configuration file location, browser override (if needed), and the default data frame type for SQL query results.

config_file : Path to the configuration file (JSON format) containing OAuth credentials and other settings.

Browser_override : Optional parameter to specify a browser for OAuth authentication. If left empty, the default browser will be used. this needs to be the path to the executable for the browser

data_frame_type : Default data frame type for SQL query results. Options are 'pandas' or 'polars'. Default is 'pandas'.

```python
hci.initialize_settings(config_file = 'location of configuration file', Browser_override = '', data_frame_type = 'pandas')
```
the configuration file is a .json file
```python
{
    "CLIENT_ID": "",
    "CLIENT_SECRET": "",
    "AUTH_URL": "",
    "TOKEN_URL": "",
    "protected_url": "",
    "REDIRECT_URI": "",
    "SCOPE": "",
	"HC_prod_URL": ""
}
```