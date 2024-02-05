from schemas import ZabbixServer
from schemas.settings import Settings

settings = Settings(
    # Zabbix server, test if server id online
    ZABBIX_SERVERS_CHECK=[ZabbixServer(ip="192.168.0.1", port=10051), ZabbixServer(ip="192.168.0.2", port=10052), ZabbixServer(ip="192.168.0.3", port=10053)],
    # IP of the frontend of Zabbix used to make API calls
    ZABBIX_API_ENDPOINT="http://192.168.0.50:80",
    # Timeout for zabbix API
    ZABBIX_API_TIMEOUT=60,
    # Restry for zabbix API
    ZABBIX_API_RETRY=1,
    # Limit trigger on zabbix API
    ZABBIX_API_LIMIT=1000,
    # Latency for show message zabbix API is down
    ZABBIX_API_ACCEPTED_LATENCY=20,
    # Login used to call Zabbix API
    ZABBIX_API_LOGIN="LOGIN",
    ZABBIX_API_PASSWORD="PASSWORD",
    # URL of your Zabbix frontend used to create links about triggers informations
    ZABBIX_URL="https://zabbix-frontend.example",
    # List team and associate zabbix group
    TEAMS={ "Team-1": ["Group-1", "Group-2", "Group-3", "Group-4"],
            "Team-2": ["Group-10", "Group-20", "Group-30"],
            "Other": ["Group-100", "Group-200", "Group-300", "Group-4"] }
)
