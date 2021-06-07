#!/user/bin/python3

### Dependencies

from __future__ import print_function
import subprocess
import itertools, threading
import argparse
import socket, shutil
import time, json, html
import sys
import re, io, os

try:
	from lxml.cssselect import CSSSelector
	from stem.control import Controller
	from requests import get
	from stem import Signal
	from stem.connection import IncorrectPassword
	from stem import SocketError
	import lxml.html
	import requests
	import socket
	import socks
except ImportError:
    print("Run `pip3 install -r requirements.txt` to install dependencies.")
    sys.exit(1)

### Global variables/Settings

YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v={youtube_id}"
YOUTUBE_COMMENTS_AJAX_URL = "https://www.youtube.com/comment_service_ajax"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"

settings_dict = None
with open('settings.json') as f:
	settings_dict = json.load(f);

use_control_pass = settings_dict["use_control_pass"]
control_pass = settings_dict["control_pass"]
control_port = settings_dict["control_port"]
socks_port = settings_dict["socks_port"]

### Tor

def get_tor_session():
	session = requests.Session()
	session.proxies = {"http": "socks5://localhost:" + str(socks_port), "https": "socks5://localhost:" + str(socks_port)}
	return session

def rotate_connection():
	time.sleep(10)
	try:
		with Controller.from_port(port=9151) as c:
			if use_control_pass:
				c.authenticate(password=control_pass)
				c.signal(Signal.NEWNYM)
			else:
				c.authenticate()
				c.signal(Signal.NEWNYM)
	except IncorrectPassword:
		print("Error: Failed to authenticate. Control port password incorrect.")
		sys.exit(1)
	except SocketError:
		print("Error: Connection refused. Ensure cookie authentication/control port is enabled.")
		sys.exit(1)

### Outputs

def geoip():
	try:
		r = get_tor_session().get("https://ip.seeip.org/geoip")
		r_dict = r.json()
		print(r_dict["country"] + " — " + r_dict["ip"])
	except IOError:
		print("Unknown")

def conclusion(attempts, accessible):
	if attempts == 0:
		print("\nInterrupted before granted sufficient time.")
	elif accessible == 0 and attempts > 0:
		print("\nAlarming behavior.")
	elif attempts > accessible:
		print("\nQuestionable behavior.")
	elif attempts == accessible and attempts > 0:
		print("\nNo abnormal behavior.")

### Videos - https://youtu.be/Y6ljFaKRTrI

def video(youtube_id):
	attempts = 0
	accessible = 0
	url = "https://www.youtube.com/watch?v=" + youtube_id
	try:
		while True:
			try:
				page_data = get_tor_session().get(url).text
				parse_title = str(re.findall('<title>(.*?) - YouTube</title><meta name="title" content=', page_data))
				title = html.unescape(parse_title.split("'")[1])
				break
			except IndexError:
				rotate_connection()
		if title == "":
			print("\nPrivate video")
		else:
			print("\n" + title)
		print("Interrupt (CTRL+C) to stop the program\n")
		while True:
			rotate_connection()
			query = get_tor_session().get("https://www.youtube.com/results?search_query=" + "+".join(title.split())).text
			if query.find('"title":{"runs":[{"text":"') >= 0:
				if query.find(title) >= 0:
					accessible += 1
					print("[✓]", end=" ")
				else:
					print("[x]", end=" ")
				geoip()
				attempts += 1
		conclusion(attempts, accessible)
	except KeyboardInterrupt:
		conclusion(attempts, accessible)

### Comments - https://www.youtube.com/feed/history/comment_history 
### Non-existent comment url template - https://www.youtube.com/watch?v=OfsojVaqyAA&lc=Ugx5BtG_-N5pwDyvOiF4AaABAg.9NEWMl2CCJR9NI73GZeCDa

def comments():
	attempts = 0
	accessible = 0
	index = 1
	try:
		with io.open("Google - My Activity.html", "r", encoding = "utf-8") as raw_html:
			html = raw_html.read().replace("\n", "").replace("'", "`")
			text_list = str(re.findall('<div class="QTGV3c" jsname="r4nke">(.*?)</div><div class="SiEggd">', html))
			uuid_list = str(re.findall('data-token="(.*?)" data-date', html))
			url_list = str(re.findall('<div class="iXL6O"><a href="(.*?)" jslog="65086; track:click"', html))
			for i in range(int(url_list.count("'") / 2)):
				text = text_list.split("'")[index]
				uuid = uuid_list.split("'")[index]
				url = url_list.split("'")[index]
				comment_url = url + "&lc=" + uuid
				instances = 0
				index += 2
				print('\n"' + text.replace("`", "'") + '"')
				print(url + "\n")
				for i in range(0, 3, 1):
					fetch_comments(url.replace("https://www.youtube.com/watch?v=", ""))
					if private == bool(True):
						break
					with open("temp.json", "r") as json:
						j = json.read()
						if j.find(uuid) >= 0:
							print("[✓]", end=" ")
							instances += 1
						else:
							print("[x]", end=" ")
							if instances > 0:
								instances -= 1
						geoip()
					rotate_connection()
				if private == bool(False):
					if instances == 3:
						accessible += 1
					attempts += 1
		conclusion(attempts, accessible)
	except KeyboardInterrupt:
		conclusion(attempts, accessible)

def fetch_comments(youtube_id):
	parser = argparse.ArgumentParser()
	try:
		args, unknown = parser.parse_known_args()
		output = "temp.json"
		limit = 1000
		if not youtube_id or not output:
			parser.print_usage()
			raise ValueError('Error: Faulty video I.D.')
		if os.sep in output:
			if not os.path.exists(outdir):
				os.makedirs(outdir)
		count = 0
		with io.open(output, 'w', encoding='utf8') as fp:
			for comment in download_comments(youtube_id):
				comment_json = json.dumps(comment, ensure_ascii=False)
				print(comment_json.decode('utf-8') if isinstance(comment_json, bytes) else comment_json, file=fp)
				count += 1
				if limit and count >= limit:
					break
	except Exception as e:
		print('Error:', str(e))
		sys.exit(1)

def find_value(html, key, num_chars=2, separator='"'):
	pos_begin = html.find(key) + len(key) + num_chars
	pos_end = html.find(separator, pos_begin)
	return html[pos_begin: pos_end]

def ajax_request(session, url, params=None, data=None, headers=None, retries=5, sleep=20):
	for _ in range(retries):
		response = session.post(url, params=params, data=data, headers=headers)
		if response.status_code == 200:
			return response.json()
		if response.status_code in [403, 413]:
			return {}
		else:
			time.sleep(sleep)

def download_comments(youtube_id, sleep=.1):
	global private
	private = bool(False)
	session = requests.Session()
	session.headers['User-Agent'] = USER_AGENT

	response = session.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id))
	html = response.text

	session_token = find_value(html, 'XSRF_TOKEN', 3)
	session_token = session_token.encode('ascii').decode('unicode-escape')

	data = json.loads(find_value(html, 'var ytInitialData = ', 0, '};') + '}')
	for renderer in search_dict(data, 'itemSectionRenderer'):
		ncd = next(search_dict(renderer, 'nextContinuationData'), None)
		if ncd:
			break
	try:
		if not ncd:
			private = bool(False)
			return
	except UnboundLocalError:
		private = bool(True)
		print("Private video")
		return
	continuations = [(ncd['continuation'], ncd['clickTrackingParams'], 'action_get_comments')]
	while continuations:
		continuation, itct, action = continuations.pop()
		response = ajax_request(session, YOUTUBE_COMMENTS_AJAX_URL,
								params={action: 1,
										'pbj': 1,
										'ctoken': continuation,
										'continuation': continuation,
										'itct': itct},
								data={'session_token': session_token},
								headers={'X-YouTube-Client-Name': '1',
										'X-YouTube-Client-Version': '2.20201202.06.01'})

		if not response:
			break
		if list(search_dict(response, 'externalErrorMessage')):
			raise RuntimeError('Error returned from server: ' + next(search_dict(response, 'externalErrorMessage')))

		if action == 'action_get_comments':
			section = next(search_dict(response, 'itemSectionContinuation'), {})
			for continuation in section.get('continuations', []):
				ncd = continuation['nextContinuationData']
				continuations.append((ncd['continuation'], ncd['clickTrackingParams'], 'action_get_comments'))
			for item in section.get('contents', []):
				continuations.extend([(ncd['continuation'], ncd['clickTrackingParams'], 'action_get_comment_replies')
									for ncd in search_dict(item, 'nextContinuationData')])

		elif action == 'action_get_comment_replies':
			continuations.extend([(ncd['continuation'], ncd['clickTrackingParams'], 'action_get_comment_replies')
								for ncd in search_dict(response, 'nextContinuationData')])

		for comment in search_dict(response, 'commentRenderer'):
			yield {'cid': comment['commentId'],'text': ''.join([c['text'] for c in comment['contentText']['runs']])}

		time.sleep(sleep)

def search_dict(partial, search_key):
	stack = [partial]
	while stack:
		current_item = stack.pop()
		if isinstance(current_item, dict):
			for key, value in current_item.items():
				if key == search_key:
					yield value
				else:
					stack.append(value)
		elif isinstance(current_item, list):
			for value in current_item:
				stack.append(value)

### Init/Menu

def main():
	parser = argparse.ArgumentParser(description="A YouTube shadowban detection program.")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-v", "--video", help="analyze individual video URLs", action="store_true")
	group.add_argument("-c", "--comments", help="analyze locally available comment history", action="store_true")
	args = parser.parse_args()
	attempts = 0
	while True:
		try:
			get_tor_session().get("https://ip.seeip.org")
			break
		except IOError:
			if attempts == 0:
				print("Error: failed to reach Tor service.")
			print("Trying again in 10 seconds.")
			attempts += 1
			time.sleep(10)
			if attempts == 10:
				print("User idle. Exiting.")
				sys.exit(1)
	if args.video:
		os.system("clear")
		while True:
			youtube_id = input("https://www.youtube.com/watch?v=")
			count = 0
			for c in youtube_id:
				if c.isspace() != True:
					count = count + 1
			if count == 11:
				response = get_tor_session().get("https://www.youtube.com/watch?v=" + youtube_id)
				break
		video(youtube_id)
	elif args.comments:
		os.system("clear")
		print('The basic HTML page file from https://www.youtube.com/feed/history/comment_history must be locally available to the script as "Google - My Activity.html"')
		while True:
			try:
				confirm = input("Confirm? (Y) ") or "y"
				if confirm == "Y" or confirm == "y":
					try:
						io.open("Google - My Activity.html", "r")
						break
					except IOError:
						print("Error: File does not exist. Please download the file listed above and place it in the project directory.")
			except ValueError:
				continue
		comments()
	else:
		print("Run `python3 shadowtube.py -h` to list argumental options.")

if __name__ == "__main__":
	main()
