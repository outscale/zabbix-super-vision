from zabbix_api import ZabbixAPI
from os import path

import asyncio
import json
import operator
import aiohttp
import aiohttp.web
import json
import time
import datetime
import logging
import sys
import os.path
import random
import argparse
import re
import config
import socket


stdio_handler = logging.StreamHandler()
stdio_handler.setLevel(logging.INFO)
_logger = logging.getLogger('aiohttp.access')
_logger.addHandler(stdio_handler)
_logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("--zabbix_ip", help="Zabbix Frontend IP.", required=True)
parser.add_argument("--zabbix_url", help="Zabbix URL. Used to build triggers URL.", required=True)
parser.add_argument("--alert_limit", help="Number of alerts to retrieve.", required=True)
parser.add_argument("--zabbix_hostgroup", help="Search for hostgroups which correspond to this parameter (Wildcard allowed).", required=True)
parser.add_argument("--zabbix_min_severity", help="Minimum trigger severity to retrieve.", required=True)
parser.add_argument("--zabbix_login", help="Login to connect to the Zabbix API.", required=True)
parser.add_argument("--zabbix_pass", help="Password to connect to the Zabbix API.", required=True)
parser.add_argument("--list_zabbix_servers", help="List of Zabbix Servers to check", required=True, nargs="+")
parser.add_argument("--zabbix_timeout", help="Timeout to the API.", required=True, type=int)
parser.add_argument("--port", help="Listen Port.", required=True)

args = parser.parse_args()

ZABBIX_API = 'http://'+args.zabbix_ip
ZABBIX_FRONTEND = args.zabbix_url + '/'
ZABBIX_LOGIN = args.zabbix_login
ZABBIX_PASS = args.zabbix_pass
LIMIT = args.alert_limit
HOSTGROUP = args.zabbix_hostgroup
SEVERITY = args.zabbix_min_severity
TIMEOUT = args.zabbix_timeout
PORT = args.port
ZABBIX_SERVERS_CHECK = args.list_zabbix_servers

_logger.info('\n[ENVIRONMENT VARIABLES]\n[ZABBIX API] - {}'.format(ZABBIX_API))
_logger.info('[ZABBIX FRONTEND] - {}'.format(ZABBIX_FRONTEND))
_logger.info('[ALERT LIMIT] - {}'.format(LIMIT))
_logger.info('[HOSTGROUP] - {}'.format(HOSTGROUP))
_logger.info('[MIN SEVERITY] - {}'.format(SEVERITY))
_logger.info('[TIMEOUT] - {}'.format(TIMEOUT))
_logger.info('[PORT] - {}'.format(PORT))
_logger.info('[ZABBIX SERVERS TO CHECK] - {}\n'.format(ZABBIX_SERVERS_CHECK))

zapi = None

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

def severity_badge(severity):
	if severity == 5:
		badge = '<span class="octicon octicon-flame"> </span>'
	elif severity == 4:
		badge = '<span class="badge badge-pill badge-danger">4</span>'
	elif severity == 3:
		badge = '<span class="badge badge-pill badge-warning">3</span>'
	elif severity == 2:
		badge = '<span class="badge badge-pill badge-primary">2</span>'
	elif severity == 1:
		badge = '<span class="badge badge-pill badge-info">1</span>'
	else:
		badge = '<span class="badge badge-pill badge-light">0</span>'
	return badge

def severity_css(severity):
	css = ""
	if severity == 5:
		css = 'class="disaster"'
	return css

def html_response(data):
	response = ""
	for x in range(len(data)):
		seconds = int(time.time()) - int(data[x]['lastchange'])
		since = convert_seconds(seconds)
		css_class = severity_css(int(data[x]['priority']))
		badge = severity_badge(int(data[x]['priority']))
		if data[x]['team'] not in config.COLOR_TEAM:
			color = "#%06x;" % random.randint(0, 0xFFFFFF)
			config.COLOR_TEAM[data[x]['team']] = color
		else:
			color = config.COLOR_TEAM[data[x]['team']]
		response += "<tr "+css_class+"><td><span class='badge badge-pill' style='background-color:"+color+"'>"+data[x]['team']+"</span></td><td>"+data[x]['host']+"</td><td><a href='"+ZABBIX_FRONTEND+"zabbix.php?action=problem.view&filter_set=1&filter_triggerids%5B%5D="+data[x]['triggerid']+"' target='_blank' "+css_class+">"+data[x]['description']+"</a></td><td>"+badge+"</td><td><span class='badge badge-pill badge-light'>"+since+"</span></td></tr>"

	return response

def capitalize_nth(s, n):
	if len(s) == 2:
		return s[:n].upper() + s[n:].capitalize()
	else:
		return s.title()

def construct_menu():
	MENU = ""

	for key in config.CONTENT.keys():
		MENU += "<li class='nav-item'><a class='nav-link' href='/"+key+"'>"+ capitalize_nth(key.replace('Team-', ''),2) +"</a></li>"
	return MENU

def construct_form():
	FORM = "<div class='col'><select class='form-control' name='team'><option value='all'>All teams</option>"

	for key in config.CONTENT.keys():
		FORM += "<option value='"+key+"'>"+key+"</option>"
	FORM += "</select></div>"
	return FORM

async def check_servers():
	global ZABBIX_SERVERS_CHECK

	while True:
		_logger.info('[INFO] - Checking Zabbix Servers: {}'.format(ZABBIX_SERVERS_CHECK))
		j = {}
		for ip in ZABBIX_SERVERS_CHECK:
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

def read_file(file_to_update):
	if os.path.exists(file_to_update):
		with open(file_to_update, 'r') as f:
			out = json.load(f)
		return out
		f.close()
	return False

def write_file(notes, file_to_update):
	with open(file_to_update, 'w+') as f:
		json.dump(notes, f)
	f.close()

async def del_note(request):
	data = await request.post()
	note_id = data['note_id']
	url = data['url']
	out = read_file('./data/motd.json')
	_logger.info('[DEL] - {}'.format(out[note_id]))
	del out[note_id]
	write_file(out, './data/motd.json')
	return aiohttp.web.HTTPFound(location=url)

async def show_alerts(request):
	global CONTENT
	global NAVBAR
	global JS_CONTENT
	global TEMPLATE_FOOTER
	global TOTAL_ALERTS

	data_list = []
	html_content = ""
	html_notes = "<table class='table table-borderless'>"
	html_check = "<table class='table table-borderless table-sm'>"
	response = ""

	config.TEMPLATE_HEAD = config.TEMPLATE_HEAD.replace('FORM_TEAM', construct_form())

	config.NAVBAR = config.NAVBAR.replace('LIST', construct_menu())
	config.NAVBAR = re.sub('\[[0-9]+\]', '['+config.TOTAL_ALERTS+']', config.NAVBAR)

	url = str(request.url)
	if '/tv/' in url:
		config.TEMPLATE_FOOTER = config.TEMPLATE_FOOTER.replace('show', 'hide')
	else:
		config.TEMPLATE_FOOTER = config.TEMPLATE_FOOTER.replace('hide', 'show')

	teams = request.match_info.get('teams')
	if not teams:
		teams = []
	notes = read_file('./data/motd.json')
	if notes:
		for ts in notes:
			for note in notes[ts]:
				if note['team'] in teams or note['team'] == 'all':
					date_note = datetime.datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
					html_notes += "<tr class='bg-"+note['lvl']+"'><td class='text-left'><span class='octicon octicon-clock'></span> "+date_note+"</td><td class='text-center'> "+note['msg']+"</td><td class='text-right'><span class='octicon octicon-hubot'></span><i> (by "+note['name']+")</i></td><td class='text-right'><form action='/del' method='post' accept-charset='utf-8' enctype='application/x-www-form-urlencoded'><input type='text' class='form-control url_note' name='url' hidden readonly><input type='text' name='note_id' value='"+ts+"' readonly hidden><button type='submit' class='btn btn-outline-light btn-sm' id='del_note' ><span class='octicon octicon-trashcan'></span></button></form></td></tr>"
	html_notes += '</table>'
	check_zbx = read_file('./data/zabbix-servers.json')
	if check_zbx:
		for ip in check_zbx:
			if check_zbx[ip] != 0:
				html_check += "<tr class='bg-danger'><td class='text-center align-left'><span class='octicon octicon-alert'></span> Zabbix Server: "+ ip + " seems UNREACHABLE! <span class='octicon octicon-alert'></span></td></tr>"
	html_check += '</table>'
	IMAGE='<div class="container-fluid image-container"><img src="/images/zabbix_logo_500x131.png" width="30%"/></div>'
	if teams:
		team_list = teams.split('+')
		for team in team_list:
			team_alerts = config.CONTENT.get(team, {})
			data_list.extend(team_alerts)
		if data_list:
			data = sorted(data_list,
				key = lambda i: (i['priority'], i['lastchange']),
				reverse=True)
			result = html_response(data)
			html_content = config.TEMPLATE_HEAD.replace('[alerts]', '['+str(len(data))+']').replace('NAVBAR', config.NAVBAR).replace('NOTES', html_notes).replace('CHECK', html_check) + result + config.TEMPLATE_FOOTER
		else:
			html_content = config.TEMPLATE_HEAD.replace('NAVBAR', config.NAVBAR).replace('NOTES', html_notes).replace('CHECK', html_check) + '<div class="alert alert-dark text-center" role="alert">No Alerts for '+str(teams)+'! <span class="octicon octicon-thumbsup"></span></div>'+IMAGE+' ' + config.TEMPLATE_FOOTER
	else:
		html_content = config.TEMPLATE_HEAD.replace('NAVBAR', config.NAVBAR) + response + config.TEMPLATE_FOOTER
	return aiohttp.web.Response(text=html_content, content_type='text/html')

def zabbix_login():
	global zapi
	x = 0

	while x < 10:
		try:
			zapi = ZabbixAPI(server=ZABBIX_API, timeout=int(TIMEOUT))
			zapi.login(ZABBIX_LOGIN, ZABBIX_PASS)
		except Exception as e:
			x+=1
			_logger.error("[ERR] - {} Retry #{}: {}".format(datetime.datetime.now(), x, e))
			time.sleep(x)
			continue
		break
	if x >= 10:
		sys.exit("Can't connect to Zabbix API.")

def call_zabbix(request, method):
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

async def process_zabbix_queue():
	global CONTENT
	global TOTAL_ALERTS
	global HOSTGROUP
	global LIMIT
	global SEVERITY
	global zapi

	while True:
		try:
			zapi.logged_in()
		except Exception as e:
			_logger.info('[INFO] - {}: Connection to Zabbix API'.format(datetime.datetime.now()))
			zabbix_login()

		request = dict()
		request['output'] = 'extend'
		request['search'] = dict()
		request['search']['name'] = [HOSTGROUP]
		request['searchWildcardsEnabled'] = 1
		resp = call_zabbix(request, 'hostgroup')
		groupids = []
		for x in range(len(resp)):
			config.CONTENT[resp[x]['name']] = []
			groupids.append(resp[x]['groupid'])

		request = dict()
		request['limit'] = LIMIT
		request['groupids'] = groupids
		request['monitored'] = 1
		request['maintenance'] = 0
		request['active'] = 1
		request['min_severity'] = SEVERITY
		request['output'] = "extend"
		request['expandData'] = 1
		request['selectHosts'] = "extend"
		request['selectGroups'] = "extend"
		request['expandDescription'] = 1
		request['only_true'] = 1
		request['skipDependent'] = 1
		request['withUnacknowledgedEvents'] = 1
		request['withLastEventUnacknowledged'] = 1
		request['selectTags'] = "extend"
		request['filter'] = dict()
		request['filter']['value'] = 1
		request['sortfield'] = ["priority","lastchange"]
		request['sortorder'] = ["DESC"]
		_logger.info(request)
		resp = call_zabbix(request, 'triggers')
		config.TOTAL_ALERTS = str(len(resp))
		_logger.info('[NB ALERTS] - {}'.format(config.TOTAL_ALERTS))
		hostgroup_to_search = HOSTGROUP.replace('*','')
		for x in range(len(resp)):
			data = resp[x]
			if len(data['hosts']) > 0:
				for z in range(len(data['groups'])):
					if hostgroup_to_search in data['groups'][z]['name']:
						group = data['groups'][z]['name']
						config.CONTENT[group].append({'description': data['description'], 'host': data['hosts'][0]['host'], 'priority': data['priority'], 'triggerid': data['triggerid'], 'lastchange': data['lastchange'], 'team': group})
				for y in range(len(data['tags'])):
					if 'team' == data['tags'][y]['tag']:
						team = data['tags'][y]['value']
						config.CONTENT[team].append({'description': data['description'], 'host': data['hosts'][0]['host'], 'priority': data['priority'], 'triggerid': data['triggerid'], 'lastchange': data['lastchange'], 'team': team})
		_logger.info('[INFO] - {}: Refresh...'.format(datetime.datetime.now()))
		await asyncio.sleep(15)

async def start_background_tasks(app):
	app['dispatch'] = app.loop.create_task(process_zabbix_queue())
	app['dispatch'] = app.loop.create_task(check_servers())


async def cleanup_background_tasks(app):
	app['dispatch'].cancel()
	await app['dispatch']

def main():

	app = aiohttp.web.Application(logger=_logger)

	app.add_routes([aiohttp.web.get('/', show_alerts),
		aiohttp.web.post('/post', post_note),
		aiohttp.web.post('/del', del_note),
		aiohttp.web.get('/{teams}', show_alerts),
		aiohttp.web.get('/tv/{teams}', show_alerts),
		aiohttp.web.static('/images', 'images'),
		aiohttp.web.static('/css', 'css'),
		aiohttp.web.static('/js', 'js')])


	app.on_startup.append(start_background_tasks)
	app.on_cleanup.append(cleanup_background_tasks)
	aiohttp.web.run_app(app, port=PORT)

if __name__ == '__main__':
	main()
