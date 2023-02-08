ZABBIX_API = 'http://127.0.0.1:8080' # IP of the frontend of Zabbix used to make API calls
ZABBIX_URL = 'https://zabbix.internal' # URL of your Zabbix frontend used to create links about triggers informations
ZABBIX_LOGIN = 'Admin' # Login used to call Zabbix API
ZABBIX_PASS = 'admin' # Password used to call Zabbix API
LIMIT = 3000 # Number of alerts to retrieve for all host groups mentioned below
HOSTGROUP = ["Zabbix*"] # Host groups related to your alerts (e.g: "Zabbix servers","Zabbix proxy","Zabbix Frontend"). You can use a wildcard.
SEVERITY = 3 # Minimum severity to retrieve
TIMEOUT = 20 # API Timeout
PORT = 8080 # Listen port for the super-server
ZABBIX_SERVERS_CHECK = ['127.0.0.1:10051'] # Zabbix server IP to check. (Makes a socket connection on the IP:port)
COLOR_TEAM = {
"Zabbix servers": "#04B404"
} # Possibility to fix color for host groups
