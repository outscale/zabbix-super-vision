import aiohttp_jinja2
import jinja2
import aiohttp
import settings
import time
import datetime
import logging
import sys
import random
import os
import json
import asyncio
import socket
from aiohttp import web
from zabbix_api import ZabbixAPI
from functools import lru_cache

stdio_handler = logging.StreamHandler()
stdio_handler.setLevel(logging.INFO)
_logger = logging.getLogger('aiohttp.access')
_logger.addHandler(stdio_handler)
_logger.setLevel(logging.INFO)

def convert_seconds(seconds):
	time = "a few sec"
	if seconds >= 60:
		time = str(round(seconds / 60)) + " min"
	if seconds > 3600:
		if round(seconds / 3600) == 1:
			time = "an hour"
		else:
			time = str(round(seconds / 3600)) + " hours"
	if seconds >= 86400:
		if round(seconds / 86400) == 1:
			time = "a day"
		else:
			time = str(round(seconds / 86400)) + " days"
	if seconds >= 2629746:
		if round(seconds / 2629746) == 1:
			time = "a month"
		else:
			time = str(round(seconds / 2629746)) + " months"
	if seconds >= 31536000:
		if round(seconds / 31536000) == 1:
			time = "a year"
		else:
			time = str(round(seconds / 31536000)) + " years"
	return time

def zabbix_login():
	global zapi
	x = 0

	while x < 10:
		try:
			zapi = ZabbixAPI(server=settings.ZABBIX_API, timeout=int(settings.TIMEOUT))
			zapi.login(settings.ZABBIX_LOGIN, settings.ZABBIX_PASS)
		except Exception as e:
			x+=1
			_logger.error("[ERR] - {} Retry #{}: {}".format(datetime.datetime.now(), x, e))
			time.sleep(x)
			continue
		break
	if x >= 10:
		sys.exit("Can't connect to Zabbix API.")
  
def zabbix_call(request, method):
	global zapi
	x = 0

	while x < 10:
		try:
			if method == 'hostgroup':
				resp = zapi.hostgroup.get(request)
			elif method == 'triggers':
				resp = zapi.trigger.get(request)
		except Exception as e:
			x+=1
			_logger.error("[ERR] - {} Retry #{}: {}".format(datetime.datetime.now(), x, e))
			time.sleep(x)
			continue
		break
	if x >= 10:
		sys.exit("Can't perform calls to Zabbix API.")
	else:
		return resp

def read_file(file_to_update):
	if os.path.exists(file_to_update):
		with open(file_to_update, 'r') as f:
			out = json.load(f)
		f.close()
		return out
	return False

def write_file(notes, file_to_update):
	with open(file_to_update, 'w+') as f:
		json.dump(notes, f)
	f.close()

def display_notes(request):
	note_list = []
	notes = read_file('./data/motd.json')
	teams = request.match_info.get('teams')
	if notes:
		for ts in notes:
			for note in notes[ts]:
				if note['team'] in teams or note['team'] == 'all':
					date_note = datetime.datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
					note_list.append({"lvl": note["lvl"], "date": date_note, "msg": note['msg'], "name": note['name'], "ts": ts })
	return note_list

def get_hostgroup_color(hostgroup):
	if hostgroup not in settings.COLOR_TEAM:
		color = "#%06x;" % random.randint(0, 0xFFFFFF)
		settings.COLOR_TEAM[hostgroup] = color
	else:
		color = settings.COLOR_TEAM[hostgroup]
	return color
 
def get_hostgroups():
	groups = []
 
	for hg in settings.HOSTGROUP:
		request = dict()
		request['output'] = 'extend'
		request['search'] = dict()
		request['search']['name'] = hg
		request['searchWildcardsEnabled'] = 1
		resp = zabbix_call(request, 'hostgroup')
		for x in range(len(resp)):
			groups.append(resp[x]['name'])
	return groups

def get_ttl_hash(seconds=45):
    return round(time.time() / seconds)

@lru_cache()
def get_problems(ttl_hash = None):
	del ttl_hash
	problems = []
	limit = settings.LIMIT
	groups = [group.lower() for group in get_hostgroups()]
	try:
		zapi.logged_in()
	except Exception as e:
		_logger.info('[INFO] - {}: Connection to Zabbix API'.format(datetime.datetime.now()))
		zabbix_login()
	
	team_list = settings.HOSTGROUP
  
	groupids = [] 
	for hg in team_list:
		req = dict()
		req['output'] = 'extend'
		req['search'] = dict()
		req['search']['name'] = hg
		req['searchWildcardsEnabled'] = 1
		resp = zabbix_call(req, 'hostgroup')
		for x in range(len(resp)):
			groupids.append(int(resp[x]['groupid']))
 
	req = dict()
	req['limit'] = limit
	req['groupids'] = groupids
	req['monitored'] = 1
	req['maintenance'] = 0
	req['active'] = 1
	req['min_severity'] = settings.SEVERITY
	req['output'] = "extend"
	req['expandData'] = 1
	req['selectHosts'] = "extend"
	req['selectGroups'] = "extend"
	req['expandDescription'] = 1
	req['only_true'] = 1
	req['skipDependent'] = 1
	req['withUnacknowledgedEvents'] = 1
	req['withLastEventUnacknowledged'] = 1
	req['selectTags'] = "extend"
	req['filter'] = dict()
	req['filter']['value'] = 1
	req['sortfield'] = ["priority","lastchange"]
	req['sortorder'] = ["DESC"]
 
	resp = zabbix_call(req, 'triggers')
	for x in range(len(resp)):
		data = resp[x]
		if len(data['hosts']) > 0:
			# Loop on problems
			for z in range(len(data['groups'])):
				if int(data['groups'][z]['groupid']) in groupids:
					hostgroup = data['groups'][z]['name']
					color = get_hostgroup_color(hostgroup)
					since = convert_seconds(int(time.time()) - int(data['lastchange']))
					problems.append({'description': data['description'], 'host': data['hosts'][0]['host'], 'priority': data['priority'], 'triggerid': data['triggerid'], 'since': since, 'hostgroup': hostgroup, 'color': color, 'lastchange': data['lastchange']})
			for y in range(len(data['tags'])):
				tag_value = data['tags'][y]['value']
				if tag_value.lower() in groups:
					color = get_hostgroup_color(tag_value)
					since = convert_seconds(int(time.time()) - int(data['lastchange']))
					problems.append({'description': data['description'], 'host': data['hosts'][0]['host'], 'priority': data['priority'], 'triggerid': data['triggerid'], 'since': since, 'hostgroup': tag_value, 'color': color, 'lastchange': data['lastchange']})
	_logger.info('[INFO] - {}: Refresh...'.format(datetime.datetime.now()))
	return problems

async def post_note(request):
	data = await request.post()
	msg = data['msg']
	team = data['team']
	name = data['name']
	url = data['url']
	lvl = data['lvl']
	ts = int(time.time())

	j = {}
	j[ts] = []
	j[ts].append({
		'team': team,
		'name': name,
		'msg': msg,
		'lvl': lvl
	})

	if os.path.exists('./data/motd.json'):
		out = read_file('./data/motd.json')
		out.update(j)
		write_file(out, './data/motd.json')
	else:
		write_file(j, './data/motd.json')
	_logger.info("[ADD] - {}".format(j))
	return aiohttp.web.HTTPFound(location=url, text='{}'.format(ts), content_type='text/html')

async def del_note(request):
	data = await request.post()
	note_id = data['note_id']
	url = data['url']
	out = read_file('./data/motd.json')
	_logger.info('[DEL] - {}'.format(out[note_id]))
	del out[note_id]
	write_file(out, './data/motd.json')
	return aiohttp.web.HTTPFound(location=url)

async def check_servers():
	while True:
		_logger.info('[INFO] - Checking Zabbix Servers: {}'.format(settings.ZABBIX_SERVERS_CHECK))
		j = {}
		for ip in settings.ZABBIX_SERVERS_CHECK:
			port = 10051
			if ':' in ip:
				i = ip.split(':')
				ip = i[0]
				port = int(i[1].strip())
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(5)
			result = sock.connect_ex((ip, port))
			if result == 0:
				_logger.info("[INFO] - Port {} OK: {}".format(port, ip))
			else:
				_logger.error("[ERR] - Port {} KO: {}".format(port, ip))
			j[ip] = result
			sock.close()
		if os.path.exists('./data/zabbix-servers.json'):
			out = read_file('./data/zabbix-servers.json')
			out.update(j)
			write_file(out, './data/zabbix-servers.json')
		else:
			write_file(j, './data/zabbix-servers.json')
		await asyncio.sleep(60)

async def start_background_tasks(app):
	app['dispatch'] = app.loop.create_task(check_servers())

async def cleanup_background_tasks(app):
	app['dispatch'].cancel()
	await app['dispatch']

@aiohttp_jinja2.template('index.html')
def display_alerts(request):
	url = str(request.url)
	if '/tv/' in url:
		tv_mode = True
	else:
		tv_mode = False

	teams = request.match_info.get('teams')
	try:
		zapi.logged_in()
	except Exception as e:
		_logger.info('[INFO] - {}: Connection to Zabbix API'.format(datetime.datetime.now()))
		zabbix_login()

	if teams:
		team_list = teams.lower().split('+')
  
	check_servers = read_file('./data/zabbix-servers.json')
	notes = display_notes(request)
	problems = get_problems(ttl_hash=get_ttl_hash())
	_logger.info(len(problems))
	problems = [problem for problem in problems if problem.get('hostgroup').lower() in team_list]
	problems = sorted(problems,
				key = lambda i: (i['priority'], i['lastchange']),
				reverse=True)
	_logger.info('[NB ALERTS] - {}'.format(len(problems)))
	context = {'alerts': problems, 'total_alerts': len(problems), 'zabbix_url': settings.ZABBIX_URL, "hostgroups": get_hostgroups(), "notes": notes, "tv_mode": tv_mode, "check_servers": check_servers}
	return aiohttp_jinja2.render_template(
        'index.html', request, context)
 
def main():
	app = web.Application()
	aiohttp_jinja2.setup(app,
		loader=jinja2.FileSystemLoader('templates'))

	app.add_routes([
		web.get('/', display_alerts),
		web.get('/{teams}', display_alerts),
		web.get('/tv/{teams}', display_alerts),
		aiohttp.web.post('/post', post_note),
		aiohttp.web.post('/del', del_note),
		aiohttp.web.static('/images', 'images'),
		aiohttp.web.static('/css', 'css'),
		aiohttp.web.static('/js', 'js')
	])

	app.on_startup.append(start_background_tasks)
	app.on_cleanup.append(cleanup_background_tasks)
	aiohttp.web.run_app(app, port=settings.PORT)

if __name__ == '__main__':
	main()