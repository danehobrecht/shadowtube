#!/user/bin/python3

### Dependencies

from __future__ import print_function
from array import array
import subprocess
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
    print("Some dependencies couldn't be imported (likely not installed).\n\nTo install dependencies, run:\n\tpip3 install -r requirements.txt\n\nExiting.")
    exit()

### Global variables/Settings

YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v={youtubeId}"
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
		print("Error: Failed to authenticate. Tor control port password incorrect.")
		exit()
	except SocketError:
		print("Error: Connection refused. Ensure cookie authentication/control port are enabled.")
		exit()

try:
	get_tor_session().get("http://icanhazip.com").text
except IOError:
	print("A Tor browser instance must be running during script execution to access required services.\n\nExiting.")
	exit()

### Videos - https://youtu.be/Y6ljFaKRTrI

def video(url, rotations):
	attempts = 0
	accessible = 0
	page_data = requests.get(url).text
	parse_title = str(re.findall('<title>(.*?) - YouTube</title><meta name="title" content=', page_data))
	title = html.unescape(parse_title.split("'")[1])
	if title == "":
		print("Video unavailable")
	else:
		print("\n" + title)
	print(url + "\n")
	while attempts < rotations:
		rotate_connection()
		title_query = "https://www.youtube.com/results?search_query=" + "+".join(title.split()).replace('\n', '')
		title_search = get_tor_session().get(title_query).text
		if title_search.find('"title":{"runs":[{"text":"') >= 0:
			if title_search.find(title) >= 0:
				accessible += 1
				print("[ ✓ ]", end="")
			else:
				print("[ X ]", end="")
			try:
				r = get_tor_session().get("https://ip.seeip.org/geoip")
				r_dict = r.json()
				print(" " + r_dict["country"] + " (" + r_dict["ip"] + ")")
			except IOError:
				print(" Unknown location.")
			attempts += 1
	if attempts == accessible and accessible > 0:
		print("\nNo abnormal behavior.")
	elif attempts > accessible:
		print("\nQuestionable behavior.")
	elif accessible == 0:
		print("\nAlarming behavior.")

### Comments - https://www.youtube.com/feed/history/comment_history

def comments():
	attempts = 0
	accessible = 0
	index = 1
	with io.open("Google - My Activity.html", "r", encoding = "utf-8") as raw_html:
		html = raw_html.read().replace("\n", "").replace("'", "`")
		comments = str(re.findall('<div class="QTGV3c" jsname="r4nke">(.*?)</div><div class="SiEggd">', html))
		uuids = str(re.findall('data-token="(.*?)" data-date', html))
		links = str(re.findall('<div class="iXL6O"><a href="(.*?)" jslog="65086; track:click"', html))
		for i in range(int(links.count("'") / 2)):
			link = links.split("'")[index]
			comment = comments.split("'")[index]
			uuid = uuids.split("'")[index]
			instances = 0
			index += 2
			print('\n"' + comment.replace("`", "'") + '"')
			print(link + "\n")
			for i in range(0, 3, 1):
				rotate_connection()
				fetch_comments(link.replace("https://www.youtube.com/watch?v=", ""))
				if private == bool(True):
					break
				with open("temp_comments.json", "r") as json:
					j = json.read()
					if j.find(uuid) >= 0:
						print("[ ✓ ]", end="")
						instances += 1
					else:
						print("[ X ]", end="")
						if instances > 0:
							instances -= 1
					try:
						r = get_tor_session().get("https://ip.seeip.org/geoip")
						r_dict = r.json()
						print(" " + r_dict["country"] + " (" + r_dict["ip"] + ")")
					except IOError:
						print(" Unknown location.")
			if private == bool(False):
				if instances > 0:
					accessible += 1
					print("\nAccessible.")
				elif instances == 0:
					print("\nNon-accessible.")
			attempts += 1

		if attempts == accessible and accessible > 0:
			print("No abnormal behavior detected. All comments are publicly available.")
		elif attempts > accessible:
			print("Questionable behavior in " + str(attempts - accessible) + " comment(s) of " + str(attempts) + " attempted.")
		else:
			print(str(accessible) + " of " + str(attempts) + " comments publicly available.")

def fetch_comments(youtubeId):
	parser = argparse.ArgumentParser()
	try:
		args, unknown = parser.parse_known_args()
		output = "temp_comments.json"
		limit = 1000
		if not youtubeId or not output:
			parser.print_usage()
			raise ValueError('Error: Faulty video I.D.')
		if os.sep in output:
			if not os.path.exists(outdir):
				os.makedirs(outdir)
		count = 0
		with io.open(output, 'w', encoding='utf8') as fp:
			for comment in download_comments(youtubeId):
				comment_json = json.dumps(comment, ensure_ascii=False)
				print(comment_json.decode('utf-8') if isinstance(comment_json, bytes) else comment_json, file=fp)
				count += 1
				if limit and count >= limit:
					break
	except Exception as e:
		print('Error:', str(e))
		exit()

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

def download_comments(youtubeId, sleep=.1):
	global private
	private = bool(False)
	session = requests.Session()
	session.headers['User-Agent'] = USER_AGENT

	response = session.get(YOUTUBE_VIDEO_URL.format(youtubeId=youtubeId))
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
		private = bool(True	)
		print("Video unavailable.")
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

### Menu/Init

print("ShadowTube\n\n1. Video\n2. Comments\n3. Dicussion/Community posts (under development)\n")
while True:
	try:
		choice = int(input("Choose an option: "))
	except ValueError:
		continue
	if choice in (1, 2):
		break
if choice == 1:
	while True:
		try:
			url = input("YouTube video URL in question: ")
			if "https://youtu.be/" in url or "https://www.youtube.com/watch?v=" in url:
				break
		except ValueError:
			continue
	while True:
		try:
			rotations = int(input("Number of locations to try (default & minimum is 5): ") or 5)
			if rotations >= 1000:
				print("Input exceeds logical value.")
				continue
			if rotations >= 5:
				break
		except ValueError:
			continue
	video(url, rotations)
elif choice == 2:
	while True:
		try:
			confirm = str(input('Basic HTML data from https://www.youtube.com/feed/history/comment_history\nmust be locally available to the script as "Google - My Activity.html".\nConfirm? (Y) ') or "y")
			if confirm == "Y" or confirm == "y":
				try:
					io.open("Google - My Activity.html", "r")
					break
				except IOError:
					print("Error: File does not exist. Please download the file listed above and place it in the project directory. Exiting")
					Sys.exit(1)
		except ValueError:
			continue
	comments()
