#!/usr/bin/env python3

import os
import sys
import requests
import click
import time
import base64

from prettytable import PrettyTable
from pathlib import Path
from PIL import Image
from io import BytesIO

class ApiKeyException(Exception):
	pass

class API():

	def __init__(self):

		self.set_key(os.getenv('HTB_KEY', None))

		if not self._key:
			raise ApiKeyException('Please set HTB API KEY.')

		self.api = requests.Session()
		self.api.headers = {
			'Authorization':'Bearer {}'.format(self._key),
			'Accept-Encoding':'gzip, deflate',
			'Accept':'application/json',
			'Connection':'Close',
		}
		self.url = 'https://labs.hackthebox.com/api/v4'


	def set_key(self, key):

		self._key = key

	def request(self, **kwargs):

		if 'method' not in kwargs:			
			kwargs['method'] = 'GET'
		if 'url' not in kwargs and kwargs['endpoint']:
			kwargs['url'] = '{}/{}'.format(self.url, kwargs['endpoint'])
			del kwargs['endpoint']
		try:
			return self.api.request(**kwargs)
		except Exception as e:
			print(e)
			sys.exit(1)

class Machines(API):

	def __init__(self):

		API.__init__(self)
		self.active = []
		self.retired = []
		self.load()
		self.all = self.active + self.retired

	def load(self):

		if not self.active:
			self.active = self.request(endpoint='machine/paginated?per_page=100').json()['data']

		if not self.retired:		
		    response = self.request(endpoint='machine/list/retired/paginated?per_page=100').json()
		    pages = response['meta']['last_page']

		    self.retired = [item for i in range(1, pages+1)  
		    				for item in self.request(endpoint='machine/list/retired/paginated?per_page=100&retired=1&page={}'.format(i)).json()['data'] ]		
		
		return self.active, self.retired

	def get_info(self, name):
		name = self.request(endpoint='machine/profile/{}'.format(name)).json()['info']		
		return name
	'''
	def get_by_name(self, name):
		return self._filter(name=name)

	def get_by_id(self, id):
		return self._filter(id=id)

	def _filter(self, **kwargs):
		search = self.all

		for field in kwargs:
			if field not in self.all[0].keys():
				raise Exception('Invalid search filter: {}'.format(kwargs))

		search = list(filter(lambda machine, field=field: machine[field] == kwargs[field], search))
		return search
	'''

class Data():

	def list(self, opt):
		
		machines = Machines()

		match opt:
			case 1:
				print("[green blink][+] There are {} machines ordered by release date.".format(len(machines.all)))
				return self.show_machines(machines.all)
			case 2:
				print("[green blink][+] There are {} active machines ordered by release date.".format(len(machines.active)))
				return self.show_machines(machines.active)
			case 3:
				print("[green blink][+] There are {} retired machines ordered by release date.".format(len(machines.retired)))
				return self.show_machines(machines.retired)

	def machine_info(self, machine):

		machines = Machines()
		return self.show(machines.get_info(machine))

	def show_machines(self, machines):
		table = PrettyTable()

		table.field_names = [
							"Name", 
							"OS", 
							"Release", 
							"Difficulty",
							"Points"
							]

		for machine in machines:
			table.add_row([
				machine['name'],
				machine['os'],
				machine['release'].split("T")[0],
				machine['difficultyText'],
				machine['points'],
				])
		table.align = 'l'
		table.sortby = 'Release'

		return table

	def show(self, machine):

		table = PrettyTable()
		table.add_column('Info',[
								'Name',
								'OS',
								'IP',
								'Release',
								'Difficulty',								
								'Points',
								'Completed?',
								'Active?',
								'User Owns',
								'Root Owns',
								'Maker',
								'User Blood',
								'User Root',												
						])
		
		maker = '{}'.format(machine['maker']['name']) if machine['maker2'] == None else '{} & {}'.format(machine['maker']['name'], machine['maker2']['name'])

		table.add_column('HackTheBox',[
							machine['name'],
							machine['os'],
							machine['ip'],
							machine['release'].split("T")[0],
							machine['difficultyText'],							
							machine['points'],
							'Yes' if machine['isCompleted'] else 'Nope!',
							'Yes' if machine['active'] == 1 else 'Nope!',
							machine['user_owns_count'],
							machine['root_owns_count'],							
							maker,
							'User Blood by {} in {}'.format(machine['userBlood']['user']['name'], machine['firstUserBloodTime']),
							'System Blood by {} in {}'.format(machine['rootBlood']['user']['name'], machine['firstRootBloodTime'])	
						])
		
		table.align = 'l'
		
		return table

	def get_img_machine(self, url):

		buffered = BytesIO()

		if requests.get(url, timeout=5).status_code == 200:
			pass
		else: 
			print("[-] Cannot get the box image.")
			print("[-] Sometimes the server stops accepting connections, try again.\n")
			return 0
		
		try:
			req = Image.open(requests.get(url, timeout=5, stream=True).raw)
		except:
		    print("error:", sys.exc_info()[0])
		    print(str(url))
		    return False
		    raise

		icon_sizes = [(24, 24),(64,64)]
		new_image = req.resize(icon_sizes[0])
		new_image.save(buffered, format="ICO",quality=100)
		new_image = base64.b64encode(buffered.getvalue())
		base = "![box_img_maker](data:image/png;base64,{0})".format(new_image.decode('utf-8'))
		
		return base.strip()

	def show_template(self, machine):

		from jinja2 import Template

		machines = Machines()
		m = machines.get_info(machine)		

		file = Path( os.path.dirname(os.path.realpath(__file__)) + '/card.template' ).read_text()

		template = Template(file)
		result = template.render(
								name   	   = m['name'],
	    						id_box	   = m['id'],
	    						os 		   = m['os'],
	    						os_icon	   = m['os'].lower(),
	    						points     = 'Retired' if m['points'] == 0 else m['points'],
	    						difficulty = m['difficultyText'], 
	    						ip 		   = m['ip'],
	    						data	   = list(m['feedbackForChart'].values()),
	    						avatar     = self.get_img_machine('https://labs.hackthebox.com' + m['avatar']),
	    						maker	   = m['maker'],
	    						maker2 	   = m['maker2'],
	    						release    = m['release'].split("T")[0]
	    						)

		return result

class CliPrinter():

	def __init__(self):
		self.cli()

	@click.group()
	def cli():
	    pass

	@cli.command('list_all', help='Lists all Machines.')
	def machines():
		machines = Data()
		print(machines.list(1))

	@cli.command('list_active', help='Lists all the current Active Machines')
	def active_machines():
		machines = Data()
		print(machines.list(2))

	@cli.command('list_retired', help='Lists all retired Machines')
	def retired_machines():
		machines = Data()
		print(machines.list(3))

	@cli.command('info', help='Gets info of the Machine by Name')
	@click.argument("name", type=str)
	def by_name(name):
		machines = Data()	
		print(machines.machine_info(name))

	@cli.command('card', help='Gets card info of the Machine by Name using template card')
	@click.argument("name", type=str)
	def show_card(name):
		machines = Data()
		print(machines.show_template(name))

if __name__ == '__main__':
   client = CliPrinter()
