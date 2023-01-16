# Super-Vision

## Description
Super-Vision is a monitoring dashboard for Zabbix.

## Installation
You will need [Python 3.6+](https://www.python.org/) or later.
It is a good practice to create a dedicated virtualenv first. Even if it usually won't harm to install Python libraries directly on the system, better to contain dependencies in a virtual environment.

- Clone this repository
- Change directory
```
cd super-vision
```
- Create a virtualenv
```
python3 -m venv .venv
source .venv/bin/activate
```
- Install Python packages
```
pip3 install -r requirements.txt
```

## Usage
```
Usage: super-server.py [-h] 
	--zabbix_ip ZABBIX_IP 
	--zabbix_url ZABBIX_URL 
	--alert_limit ALERT_LIMIT 
	--zabbix_hostgroup ZABBIX_HOSTGROUP 
	--zabbix_min_severity ZABBIX_MIN_SEVERITY
	--zabbix_login ZABBIX_LOGIN 
	--zabbix_pass ZABBIX_PASS 
	--list_zabbix_servers LIST_ZABBIX_SERVERS [LIST_ZABBIX_SERVERS ...] 
	--zabbix_timeout ZABBIX_TIMEOUT
	--port PORT
```

| Argument | Description | Example |
| ----------- | ----------- | ----------- |
| zabbix_ip | IP/URL of the Zabbix Frontend. | 127.0.0.1:8080 |
| zabbix_url | IP/URL of the Zabbix Frontend. Used to create triggers URL. | https://zabbix.internal
| alert_limit | Number of alerts to retrieve for all hostgroups. | 2000 |
| zabbix_hostgroup | Hostgroup or Pattern | Team-* |
| zabbix_min_severity | Minimum severity to retrieve. | 3 |
| zabbix_login | Login to connect to Zabbix API. | Admin |
| zabbix_pass | Password to connect to Zabbix API. | admin |
| list_zabbix_servers | List of Zabbix server IP to check if they are running or no and display an alert on the dashboard. | 127.0.0.1:10051 |
| zabbix_timeout | Timeout call to the Zabbix API. | 30 |
| port | Listen server port. | 80 |

## Examples

```
python3 super-server.py --zabbix_ip=127.0.0.1:8080 --zabbix_url='https://zabbix.internal' --alert_limit=100 --zabbix_hostgroup="Team-*" --zabbix_min_severity=3 --zabbix_login=Admin --zabbix_pass='admin' --list_zabbix_servers=127.0.0.1:10051 --zabbix_timeout=30 --port=8080
```

## Contributing
- If you think you've found a bug in the code or you have a question regarding the usage of this software, please reach out to us by opening an issue in this GitHub repository.
- Contributions to this project are welcome: if you want to add a feature or a fix a bug, please do so by opening a Pull Request in this GitHub repository. In case of feature contribution, we kindly ask you to open an issue to discuss it beforehand.

## License
> Copyright Outscale SAS
>
> BSD-3-Clause

This project is compliant with [REUSE](https://reuse.software/).
