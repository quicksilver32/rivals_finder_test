#!/usr/bin/python3
# coding=utf-8

import codecs
import pprint
import requests
import sys

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
log = pprint.PrettyPrinter(indent=4)

base_url = 'fix-online.sbis.ru'

session = requests.Session()
user_id = ""


def rpc(service, method, params):
	global base_url
	if "http:" in service or "https:" in service:
		url = service
	else:
		url = "https://" + base_url + "/" + service + "/"

	headers = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
	body = {"jsonrpc": "2.0", "protocol": 4, "method": method, "params": params}

	sys.stdout.flush()
	raw = session.post(url, headers=headers, json=body)

	response = raw.json()
	result = response.get("result")
	if result is None:
		print("\n-- {} on {} failed --".format(method, base_url))
		log.pprint(response)
		sys.stdout.flush()
		raise response
	return result




def rpc_return_record(service, method, params):
	return parse_record(rpc(service, method, params))




def rpc_return_recordset(service, method, params):
	return parse_recordset(rpc(service, method, params))




def login(url, user, password):
	global base_url
	base_url = url
	rpc("auth/service", "САП.АутентифицироватьРасш", {"login": user, "password": password})
	user_info = rpc_return_record("service", "Пользователь.GetCurrentUserInfo", {})
	global user_id
	user_id = str(user_info['ИдентификаторПользователя'])
	# log.pprint(user_info)
	# for c in session.cookies:
	# 	log.pprint(f'{c.name}={c.value}')




def schema_type(s):
	return {
		'int': 'Число целое',
		'int[]': {'n': "Массив", 't': "Число целое"},
		'string': 'Строка',
		'bool': 'Логическое',
		'uuid': 'UUID',
		'date-time': 'Дата и время',
		'date': 'Дата',
		'time': 'Время'
	}[s]




def schema_field(s):
	(n, t) = s.split(':')
	return {'n': n, 't': schema_type(t)}




def schema(s):
	return list(map(lambda f: schema_field(f), s.split(' ')))




def record(s, d):
	return {'s': schema(s), 'd': d}




def recordset(s, d):
	return {'s': schema(s), 'd': d}




def navigation(page, page_size, has_more):
	return record('Страница:int РазмерСтраницы:int ЕстьЕще:bool', [page, page_size, has_more])




def field_type(t):
	if type(t) is str:
		return {
			'Число целое': 'int',
			'Текст': 'string',
			'Строка': 'string',
			'Логическое': 'bool',
			'UUID': 'uuid',
			'Дата и время': 'date-time',
			'Дата': 'date',
			'Время': 'time',
			'Запись': 'record',
			'Выборка': 'recordset',
			'Идентификатор': 'int'
		}[t]
	if type(t) is dict and t['n'] == 'Массив':
		return field_type(t['t']) + ' array'
	return str(t)




def print_uni(record_or_recordset, indent):
	s = record_or_recordset['s']
	data = record_or_recordset['d']
	_type = record_or_recordset['_type']
	for field_index in sorted([[x, i] for i, x in enumerate(s)], key=lambda x: x[0]['n']):
		field = field_index[0]
		index = field_index[1]
		type_name = field_type(field['t'])
		print(indent + field['n'] + ' ' + type_name)
		if type_name == 'record' or type_name == 'recordset':
			if _type == 'record':
				sample = data[index]
				if sample:
					print_uni(sample, indent + '\t')
			else:
				for r in data:
					sample = r[index]
					if sample:
						print_uni(sample, indent + '\t')
						break




def parse_schema(record_or_recordset):
	names = []
	for s in record_or_recordset['s']:
		names.append(s['n'])
	return names




def parse_data(names, d):
	item = {}
	i = 0
	for n in names:
		v = d[i]
		if isinstance(v, dict):
			if v['_type'] == 'record':
				v = parse_record(v)
			elif v['_type'] == 'recordset':
				v = parse_recordset(v)
		item[n] = v
		i += 1
	return item




def parse_recordset(rs):
	names = parse_schema(rs)
	items = []
	for d in rs['d']:
		items.append(parse_data(names, d))
	return items




def parse_record(r):
	return parse_data(parse_schema(r), r['d'])




def parse_record_or_recordset(r):
	if r['_type'] == 'record':
		return parse_record(r)
	else:
		return parse_recordset(r)