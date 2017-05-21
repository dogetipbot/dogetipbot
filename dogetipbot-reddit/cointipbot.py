#!/usr/bin/env python
"""
    dogetipbot is a bot that lets you tip dogecoins on the internets
    Copyright (C) 2014-2017 Wow Such Business, Inc. and other contributors
    Portions of this software were derived from ALTcointip by Dmitriy Vi - https://github.com/vindimy/altcointip

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
"""
    This file is part of ALTcointip.

    ALTcointip is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ALTcointip is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ALTcointip.  If not, see <http://www.gnu.org/licenses/>.
"""
from ctb import ctb_action, ctb_coin, ctb_db, ctb_exchange, ctb_log, ctb_misc, ctb_user

import gettext, locale, logging, praw, smtplib, sys, time, traceback, yaml, decimal, requests, requests.auth, json
from email.mime.text import MIMEText
from jinja2 import Environment, PackageLoader

from requests.exceptions import HTTPError, ConnectionError, Timeout
from praw.errors import ExceptionList, APIException, InvalidCaptcha, InvalidUser, RateLimitExceeded
from socket import timeout
from decimal import *
from iron_mq import *

# Configure CointipBot logger
logging.basicConfig()
lg = logging.getLogger('cointipbot')


class CointipBot(object):
	"""
	Main class for cointip bot
	"""

	conf = None
	db = None
	reddit = None
	push = None
	push_queue = None
	pull_queue = None
	coins = {}
	exchanges = {}
	jenv = None
	runtime = {'ev': {}, 'regex': []}

	def init_logging(self):
		"""
		Initialize logging handlers
		"""

		handlers = {}
		levels = ['warning', 'info', 'debug']
		lg = logging.getLogger('cointipbot')
		bt = logging.getLogger('bitcoin')

		# Get handlers
		handlers = {}
		for l in levels:
			if self.conf.logs.levels[l].enabled:
				handlers[l] = logging.FileHandler(self.conf.logs.levels[l].filename, mode='a' if self.conf.logs.levels[l].append else 'w')
				handlers[l].setFormatter(logging.Formatter(self.conf.logs.levels[l].format))

		# Set handlers
		for l in levels:
			if handlers.has_key(l):
				level = logging.WARNING if l == 'warning' else (logging.INFO if l == 'info' else logging.DEBUG)
				handlers[l].addFilter(ctb_log.LevelFilter(level))
				lg.addHandler(handlers[l])
				bt.addHandler(handlers[l])

		# Set default levels
		lg.setLevel(logging.DEBUG)
		bt.setLevel(logging.DEBUG)

		lg.info('CointipBot::init_logging(): -------------------- logging initialized --------------------')
		return True

	def parse_config(self):
		"""
		Returns a Python object with CointipBot configuration
		"""
		lg.debug('CointipBot::parse_config(): parsing config files...')

		conf = {}
		try:
			prefix='./conf/'
			for i in ['coins', 'db', 'exchanges', 'fiat', 'keywords', 'logs', 'misc', 'reddit', 'regex']:
				lg.debug("CointipBot::parse_config(): reading %s%s.yml", prefix, i)
				conf[i] = yaml.load(open(prefix+i+'.yml'))
		except yaml.YAMLError as e:
			lg.error("CointipBot::parse_config(): error reading config file: %s", e)
			if hasattr(e, 'problem_mark'):
				lg.error("CointipBot::parse_config(): error position: (line %s, column %s)", e.problem_mark.line+1, e.problem_mark.column+1)
			sys.exit(1)

		lg.info('CointipBot::parse_config(): config files has been parsed')
		return ctb_misc.DotDict(conf)

	def connect_db(self):
		"""
		Returns a database connection object
		"""
		lg.debug('CointipBot::connect_db(): connecting to database...')

		dsn = "mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8" % (self.conf.db.auth.user, self.conf.db.auth.password, self.conf.db.auth.host, self.conf.db.auth.port, self.conf.db.auth.dbname)
		dbobj = ctb_db.CointipBotDatabase(dsn)

		try:
			conn = dbobj.connect()
		except Exception as e:
			lg.error("CointipBot::connect_db(): error connecting to database: %s", e)
			sys.exit(1)

		lg.info("CointipBot::connect_db(): connected to database %s as %s", self.conf.db.auth.dbname, self.conf.db.auth.user)
		return conn


	def connect_reddit(self):
		"""
		Returns a praw connection object
		"""

		seconds = int(1 * 3000)
		if hasattr(self.conf.reddit, 'last_refresh') and self.conf.reddit.last_refresh + seconds > int(time.mktime(time.gmtime())):
			lg.debug("< CointipBot::connect_reddit(): to connect to reddit(): DONE (skipping)")
			return self.reddit

		lg.debug('CointipBot::connect_reddit(): connecting to Reddit via OAuth2...')

		client_auth = requests.auth.HTTPBasicAuth(self.conf.reddit.auth.id, self.conf.reddit.auth.secret)
		post_data = {"grant_type": "password", "username": self.conf.reddit.auth.user, "password": self.conf.reddit.auth.password}

		conn = praw.Reddit(user_agent = self.conf.reddit.auth.user, api_request_delay=1.0)
		conn.set_oauth_app_info(client_id=self.conf.reddit.auth.id,
		client_secret=self.conf.reddit.auth.secret,
		redirect_uri=self.conf.reddit.auth.redirect)

		while True:

			response = requests.post("https://ssl.reddit.com/api/v1/access_token", auth=client_auth, data=post_data)

			r_info = json.loads(response.content)
			lg.debug(r_info)

			if (response.status_code == 200):
				self.conf.reddit.access_token = r_info['access_token']

				conn.set_access_credentials(set(['edit','identity','privatemessages','read','submit','vote', 'creddits']),r_info['access_token'])
				print "Access Granted"
				self.conf.reddit.last_refresh = int(time.mktime(time.gmtime()))
				lg.info("CointipBot::connect_reddit(): logged in to Reddit as %s", self.conf.reddit.auth.user)
				return conn
			else:
				print "Sleeping..."
				time.sleep(10)
				pass

#		 conn.login(self.conf.reddit.auth.user, self.conf.reddit.auth.password)

	def connect_push_queue(self):
		"""
		Returns an IronMQ connection object -- requires project_id/token/host
		Could use RabbitMQ here if you prefer though.
		"""
		conn = IronMQ(
			project_id="ironmq_project_id",
			token="ironmq_token",
			host="ironmq_host"
		)
		queue = conn.queue("push-queue-name")
		return queue

	def connect_pull_queue(self):
		"""
		Returns an IronMQ connection object
		"""
		conn = IronMQ(
			project_id="ironmq_project_id",
			token="ironmq_token",
			host="ironmq_host"
		)
		queue = conn.queue("pull-queue-name")
		return queue

	def mark_as_processed(self, thingid=None):
		if (thingid):
			lg.debug('> dogetipbot::mark_as_processed(%s)', thingid)
			sql = "INSERT into t_messages (fullname) values ('%s')" % thingid
			self.db.execute(sql)
		else:
			lg.debug('WHAT THE FUCK NO THINGID')

	def check_id(self, thingid=None):
		if (thingid):
			lg.debug('> dogetipbot::check_id(%s): ', thingid)
			sql = "SELECT * FROM t_messages where fullname='%s'" % thingid
			mysqlrow = self.db.execute(sql)
			if mysqlrow.rowcount >= 1:
				return True
			else:
				return False
		else:
			lg.debug('> dogetipbot::no thing_id()')


	def delete_message(self, message_id, reservation_id):
		if self.pull_queue:
			return self.pull_queue.delete(message_id, reservation_id)
		else:
			raise Exception('Cointipbot::delete_message(): Error deleting message with id: %s and reservation_id %s', message_id, reservation_id)

	def get_messages(self):
		for i in range(20):
			try:
				return self.pull_queue.reserve(max=100, timeout=1000)
			except HTTPError as e:
				lg.debug('Cointipbot::get_messages(): failed due to %s', e)
				lg.debug('Sleep and try again')
				time.sleep(self.conf.misc.times.sleep_seconds)


	def process_pull_queue(self):
		'''process items in the queue'''
		lg.info("Cointipbot::process_pull_queue()...")
		try:
			#fetch the queue
			lg.debug("Getting all messages in the queue")
			lg.debug("Total Messages should be %s", self.pull_queue.size())
				
			msgs = self.get_messages()

			lg.debug('ALL MESSAGES %s', msgs)
			for message in msgs['messages']:
				#message_obj = ctb_action.CtbAction(self, message)
				message_obj = ctb_action.eval_pull_message(message, ctb=self)

				if message_obj is False:
					queue_id = message['id']
					lg.info('PROCESS_PULL_QUEUE false message: %s', queue_id)

					pass
				else:
					message_obj.do()

		except Exception as e:
			lg.error('Cointipbot::process_pull_queue() %s', e)
			raise
		lg.debug("< Cointipbot::process_pull_queue() DONE")
		return True


	def check_inbox(self):
		"""
		Evaluate new messages until checkpoint is reached
		"""
		lg.debug('> CointipBot::check_inbox()')
		last_read=None
		running = True

		while running:
			try:
				# fetch all the messages since last read
				lg.debug("querying all messages since %s", last_read)
				my_params = {'after':last_read}
				messages = list(ctb_misc.praw_call(self.reddit.get_inbox, params=my_params))
				# Process messages
				for m in messages:
					last_read=m.fullname
					lg.debug("Checking %s", last_read)

					#check for checkpoint
					if self.check_id(thingid=last_read):
						lg.debug("Hit checkpoint")
						running=False
						break

					# Sometimes messages don't have an author (such as 'you are banned from' message)
					if not m.author:
						lg.info("CointipBot::check_inbox(): ignoring msg with no author")
						self.mark_as_processed(thingid=m.fullname)
						continue

					lg.info("CointipBot::check_inbox(): %s from %s", "comment" if m.was_comment else "message", m.author.name)


					# Ignore self messages
					if m.author and m.author.name.lower() == self.conf.reddit.auth.user.lower():
						lg.debug("CointipBot::check_inbox(): ignoring message from self")
						self.mark_as_processed(thingid=m.fullname)
						continue

					# Ignore messages from banned users
					if m.author and self.conf.reddit.banned_users:
						lg.debug("CointipBot::check_inbox(): checking whether user '%s' is banned..." % m.author)
						u = ctb_user.CtbUser(name = m.author.name, redditobj = m.author, ctb = self)
						if u.banned:
							lg.info("CointipBot::check_inbox(): ignoring banned user '%s'" % m.author)
							self.mark_as_processed(thingid=m.fullname)
							continue

					action = None
					if m.was_comment:
						# Attempt to evaluate as comment / mention
						action = ctb_action.eval_comment(m, self)
					else:
						# Attempt to evaluate as inbox message
						action = ctb_action.eval_message(m, self)

					# load into database
					if action:
						lg.info("CointipBot::check_inbox(): %s from %s (m.id %s)", action.type, action.u_from.name, m.id)
						lg.debug("CointipBot::check_inbox(): message body: <%s>", m.body)
						action.save_pending(state="pending")
					else:
						lg.info("CointipBot::check_inbox(): no match ... message body: <%s>", m.body)
						if self.conf.reddit.messages.sorry and not m.subject in ['post reply', 'comment reply']:
							user = ctb_user.CtbUser(name=m.author.name, redditobj=m.author, ctb=self)
							tpl = self.jenv.get_template('didnt-understand.tpl')
							msg = tpl.render(user_from=user.name, what='comment' if m.was_comment else 'message', source_link=m.permalink if hasattr(m, 'permalink') else None, ctb=self)
							lg.debug("CointipBot::check_inbox(): %s", msg)
							user.tell(subj='What?', msg=msg, msgobj=m if not m.was_comment else None)

					# Mark message as read
					self.mark_as_processed(thingid=m.fullname)



			except (HTTPError, ConnectionError, Timeout, RateLimitExceeded, timeout) as e:
				lg.warning("CointipBot::check_inbox(): Reddit is down (%s), sleeping", e)
				time.sleep(self.conf.misc.times.sleep_seconds)
				pass
			except Exception as e:
				lg.error("CointipBot::check_inbox(): %s", e)
				raise

		lg.debug("< CointipBot::check_inbox() DONE")
		return True

	def process_transactions(self):
		lg.debug("< CointipBot::process_transactions() ")
		sql = "SELECT * FROM pending_action where state='pending' group by created_utc limit 50"
		for mysqlrow in self.db.execute(sql):

			such_fullname = mysqlrow['fullname']

			#Check to see if message or comment
			check_fullname = such_fullname
			check_fullname = check_fullname.split('_')

			#process as a message
			if check_fullname[0] == 't4':

				#Set vars to pass into eval_db_message
				msg_body = mysqlrow['msg_body']
				permalink = mysqlrow['msg_link']
				fullname = such_fullname
				id = mysqlrow['msg_id']
				verify = mysqlrow['verify']
				fiat = mysqlrow['verify']
				coin = mysqlrow['coin']
				coin_val = mysqlrow['coin_val']
				to_addr = mysqlrow['to_addr']
				to_user = mysqlrow['to_user']
				from_user = mysqlrow['from_user']
				created_utc = mysqlrow['created_utc']
				type = mysqlrow['type']

				if not from_user:
					lg.warning('CointipBot::process_transactions(): no author')
					sql2 = "UPDATE pending_action SET state='completed' where fullname ='%s'" % such_fullname
					self.db.execute(sql2)
					continue
				if not msg_body:
					lg.warning('CointipBot::process_transactions(): message has no body dont process')
					sql2 = "UPDATE pending_action SET state='completed' where fullname ='%s'" % such_fullname
					self.db.execute(sql2)
					continue

				action = None
				action = ctb_action.eval_db_message(msg_body, permalink, fullname, id, verify, fiat, coin, coin_val, to_addr, to_user, from_user, created_utc, type, self)

				if action:
					lg.info("CointipBot::processing transaction(): %s from %s (m.id %s)", action.type, action.u_from.name, action.deleted_msg_id)
					action.send_to_push_queue()
					sql2 = "UPDATE pending_action SET state='completed' where fullname ='%s'" % fullname
					self.db.execute(sql2)
				else:
					sql2 = "UPDATE pending_action SET state='failed' where fullname ='%s'" % fullname
					self.db.execute(sql2)



			#its a comment
			else:
				lg.debug("< CointipBot::process_transactions() Processing %s " % such_fullname)
				m=ctb_misc.praw_call(self.reddit.get_info, thing_id=such_fullname)

				if not m:
					lg.warning('CointipBot::process_transactions(): message or post has been deleted')
					sql2 = "UPDATE pending_action SET state='completed' where fullname ='%s'" % such_fullname
					self.db.execute(sql2)
					continue

				if not m.author:
					lg.warning('CointipBot::process_transactions(): no author')
					sql2 = "UPDATE pending_action SET state='completed' where fullname ='%s'" % such_fullname
					self.db.execute(sql2)
					continue

				action = None
				if mysqlrow['msg_link']:
					action = ctb_action.eval_comment(m, self)


				if action:
					lg.info("CointipBot::processing transaction(): %s from %s (m.id %s)", action.type, action.u_from.name, m.id)
					action.send_to_push_queue()
					sql2 = "UPDATE pending_action SET state='completed' where fullname ='%s'" % such_fullname
					self.db.execute(sql2)
				else:
					sql2 = "UPDATE pending_action SET state='failed' where fullname ='%s'" % such_fullname
					self.db.execute(sql2)

	def refresh_ev(self):
		"""
		Refresh coin/fiat exchange values using self.exchanges
		"""

		# Return if rate has been checked in the past hour
		seconds = int(1 * 3600)
		if hasattr(self.conf.exchanges, 'last_refresh') and self.conf.exchanges.last_refresh + seconds > int(time.mktime(time.gmtime())):
			lg.debug("< CointipBot::refresh_ev(): DONE (skipping)")
			return

		# For each enabled coin...
		for c in vars(self.conf.coins):
			if self.conf.coins[c].enabled:

				# Get BTC/coin exchange rate
				values = []
				result = 0.0

				if not self.conf.coins[c].unit == 'btc':
					# For each exchange that supports this coin...
					for e in self.exchanges:
						if self.exchanges[e].supports_pair(_name1=self.conf.coins[c].unit, _name2='btc'):
							# Get ticker value from exchange
							value = self.exchanges[e].get_ticker_value(_name1=self.conf.coins[c].unit, _name2='btc')
							if value and float(value) > 0.0:
								values.append(float(value))

					# Result is average of all responses
					if len(values) > 0:
						result = sum(values) / float(len(values))

				else:
					# BTC/BTC rate is always 1
					result = 1.0

				# Assign result to self.runtime['ev']
				if not self.runtime['ev'].has_key(c):
					self.runtime['ev'][c] = {}
				self.runtime['ev'][c]['btc'] = result

		# For each enabled fiat...
		for f in vars(self.conf.fiat):
			if self.conf.fiat[f].enabled:

				# Get fiat/BTC exchange rate
				values = []
				result = 0.0

				# For each exchange that supports this fiat...
				for e in self.exchanges:
					if self.exchanges[e].supports_pair(_name1='btc', _name2=self.conf.fiat[f].unit):
						# Get ticker value from exchange
						value = self.exchanges[e].get_ticker_value(_name1='btc', _name2=self.conf.fiat[f].unit)
						if value and float(value) > 0.0:
							values.append(float(value))

				# Result is average of all responses
				if len(values) > 0:
					result = sum(values) / float(len(values))

				# Assign result to self.runtime['ev']
				if not self.runtime['ev'].has_key('btc'):
					self.runtime['ev']['btc'] = {}
				self.runtime['ev']['btc'][f] = result

		lg.debug("CointipBot::refresh_ev(): %s", self.runtime['ev'])

		# Update last_refresh
		self.conf.exchanges.last_refresh = int(time.mktime(time.gmtime()))

	def coin_value(self, _coin, _fiat):
		"""
		Quick method to return _fiat value of _coin
		"""
		try:
			value = self.runtime['ev'][_coin]['btc'] * self.runtime['ev']['btc'][_fiat]
		except KeyError as e:
			lg.warning("CointipBot::coin_value(%s, %s): KeyError", _coin, _fiat)
			value = 0.0
		return Decimal(value)

	def notify(self, _msg=None):
		"""
		Send _msg to configured destination
		"""

		# Construct MIME message
		msg = MIMEText(_msg)
		msg['Subject'] = self.conf.misc.notify.subject
		msg['From'] = self.conf.misc.notify.addr_from
		msg['To'] = self.conf.misc.notify.addr_to

		# Send MIME message
		server = smtplib.SMTP(self.conf.misc.notify.smtp_host)
		if self.conf.misc.notify.smtp_tls:
			server.starttls()
		server.login(self.conf.misc.notify.smtp_username, self.conf.misc.notify.smtp_password)
		server.sendmail(self.conf.misc.notify.addr_from, self.conf.misc.notify.addr_to, msg.as_string())
		server.quit()

	def yo(self):
		'''
		sends a yo to all subscribers
		'''

		requests.post("https://api.justyo.co/yoall/", data={'api_token': self.conf.misc.yo.apikey, 'username': 'username', 'link': 'http://nooooooooooooooo.com/'})
		lg.debug('Cointipbot::Yo() sent')

	def __init__(self, init_reddit=True, init_coins=True, init_exchanges=False, init_db=True, init_logging=True):
		"""
		Constructor. Parses configuration file and initializes bot.
		"""
		lg.info("CointipBot::__init__()...")

		# Configuration
		self.conf = self.parse_config()

		# Logging
		if init_logging:
			self.init_logging()

		# Templating with jinja2
		self.jenv = Environment(trim_blocks=True, loader=PackageLoader('cointipbot', 'tpl/jinja2'))

		# Database
		if init_db:
			self.db = self.connect_db()

		# Coins
		if init_coins:
			for c in vars(self.conf.coins):
				if self.conf.coins[c].enabled:
					self.coins[c] = ctb_coin.CtbCoin(_conf=self.conf.coins[c])
			if not len(self.coins) > 0:
				lg.error("CointipBot::__init__(): Error: please enable at least one type of coin")
				sys.exit(1)

		# Exchanges
		if init_exchanges:
			for e in vars(self.conf.exchanges):
				if self.conf.exchanges[e].enabled:
					self.exchanges[e] = ctb_exchange.CtbExchange(_conf=self.conf.exchanges[e])
			if not len(self.exchanges) > 0:
				lg.warning("Cointipbot::__init__(): Warning: no exchanges are enabled")

		# Reddit
		if init_reddit:
			self.reddit = self.connect_reddit()
			ctb_action.init_regex(self)

		# Connect to IronMQ
		self.push_queue = self.connect_push_queue()
		self.pull_queue = self.connect_pull_queue()

		lg.info("< CointipBot::__init__(): DONE, batch-limit = %s, sleep-seconds = %s", self.conf.reddit.scan.batch_limit, self.conf.misc.times.sleep_seconds)

	def __str__(self):
		"""
		Return string representation of self
		"""
		me = "<CointipBot: sleepsec=%s, batchlim=%s, ev=%s"
		me = me % (self.conf.misc.times.sleep_seconds, self.conf.reddit.scan.batch_limit, self.runtime['ev'])
		return me

	def main(self):
		"""
		Main loop
		"""
		while (True):
			try:
				lg.debug("CointipBot::main(): beginning main() iteration")



				# Refresh OAuth key if needed
				self.reddit = self.connect_reddit()

				# sweep the inbox
				self.check_inbox()

				#process transactions
				self.process_transactions()
				#start responding
				self.process_pull_queue()

				# Sleep
				lg.debug("CointipBot::main(): sleeping for %s seconds...", self.conf.misc.times.sleep_seconds)
				time.sleep(self.conf.misc.times.sleep_seconds)

			except Exception as e:
				lg.error("CointipBot::main(): exception: %s", e)
				lg.warning("CointipBot::main(): traceback: %s", e)
				tb = traceback.format_exc()
				lg.error("CointipBot::main(): traceback: %s", tb)
				lg.warning("CointipBot::main(): traceback: %s", tb)
				# Send a notification, if enabled
				if self.conf.misc.notify.enabled:
					self.notify(_msg=tb)
					self.yo()
				sys.exit(1)
