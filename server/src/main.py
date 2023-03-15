#!/venv/bin/python3

from __future__ import print_function

from lxml.cssselect import CSSSelector
from stem.control import Controller
from requests import get
from array import array
from stem import Signal

import subprocess
import lxml.html
import argparse, requests
import socket, shutil
import socks
import time, json, html
import sys
import re, io, os

YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v={youtubeId}"
YOUTUBE_COMMENTS_AJAX_URL = "https://www.youtube.com/comment_service_ajax"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
CURRENT_WORKING_DIRECTORY = os.getcwd()

### Tor

def get_tor_session():
	session = requests.Session()
	session.proxies = {"http": "socks5://localhost:9150", "https": "socks5://localhost:9150"}
	return session

def rotate_connection():
	time.sleep(10)
	with Controller.from_port(port = 9151) as c:
		c.authenticate()
		c.signal(Signal.NEWNYM)

### Videos - https://youtu.be/Y6ljFaKRTrI

def video(url):
	attempts = 0
	accessible = 0
	#results_file = open("results.txt", 'w')
	#sys.stdout = results_file

	if "https://youtu.be/" in str(url) or "https://www.youtube.com/watch?v=" in str(url):
		try:
			get_tor_session().get("https://ip.seeip.org/")
		except IOError:
			return "Tor service is down serverside. Please try again later."
	else:
		return "Invalid input."

	page_data = requests.get(url).text
	parse_title = str(re.findall('<title>(.*?) - YouTube</title><meta name="title" content=', page_data))
	title = html.unescape(parse_title.split("'")[1])

	if title == "":
		print("Video unavailable")
	else:
		print(title)
	print(url + "\n")

	while attempts < 5:
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
		print("\nNo abnormal behavior detected.")
	elif attempts > accessible:
		print("\nQuestionable behavior detected.")
	elif accessible == 0:
		print("\nAlarming behavior detected.")

	#results_file.close()
	return(open("results.txt", "r").read())

### Comments - https://www.youtube.com/feed/history/comment_history
### Potential applications
#parent_links = str(re.findall('Commented on  <a href=(.*?)&', f))
#reply_links = str(re.findall('comment on  <a href=(.*?)&', f))
#list = comments.replace("['", "").replace("']", "").replace("`", "'")
#num = 1
#for i in range(int(list.count("', '"))):
#	num = num + 1
#	list = list.replace("', '", "\n" + str(num) + ". ", 1)
#a = re.sub('<div class="uUy2re"><div class="QTGV3c" jsname="r4nke">(.*?)`s Discussion tab</div>', '', html) WORKS?
#b = re.sub('<c-data id="i7" jsdata="(.*?)" data-date', '', a) DOESNT WORK
#<div class="QTGV3c" jsname="r4nke">Jubliani</div><div class="SiEggd">Commented on A S H`s Discussion tab</div>

def purge_uploads():
	folder = CURRENT_WORKING_DIRECTORY + "/uploads"
	for filename in os.listdir(folder):
		file_path = os.path.join(folder, filename)
		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path):
				shutil.rmtree(file_path)
		except Exception as e:
			print('Failed to delete %s. Reason: %s' % (file_path, e))

def comments():
	attempts = 0
	accessible = 0
	index = 1
	results_file = open("results.txt", 'w')
	sys.stdout = results_file

	try:
		open(CURRENT_WORKING_DIRECTORY + "/uploads/Google_-_My_Activity.html")
		try:
			get_tor_session().get("https://ip.seeip.org/")
		except IOError:
			purge_uploads()
			return "Tor service is down serverside. Please try again later."
	except IOError:
		purge_uploads()
		return "Incorrect file type."

	with io.open(CURRENT_WORKING_DIRECTORY + "/uploads/Google_-_My_Activity.html", "r", encoding = "utf-8") as raw_html:
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
			print('"' + comment.replace("`", "'") + '"')
			print(link + "\n")
			for i in range(0, 3, 1):
				rotate_connection()
				fetch_comments(link.replace("https://www.youtube.com/watch?v=", ""))
				if private == bool(True):
					break
				with open("temp.json", "r") as json:
					j = json.read()
					if j.find(uuid) >= 0:
						print("[ ✓ ]", end="")
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
					instances += 1
			if private == bool(False):
				if instances > 0:
					accessible += 1
					print("\nAccessible.\n")
				elif instances == 0:
					print("\nNon-accessible.\n")
			attempts += 1

		if attempts == accessible and accessible > 0:
			print("No abnormal behavior detected. All comments are publicly available.")
		if attempts > accessible:
			print("Questionable behavior detected in " + str(attempts - accessible) + " comment(s) of " + str(attempts) + " attempted.")
		else:
			print(str(accessible) + " of " + str(attempts) + " comments publicly available.")

	results_file.close()
	return(open("results.txt", "r").read())

def fetch_comments(youtubeId):
	parser = argparse.ArgumentParser()
	try:
		args, unknown = parser.parse_known_args()
		output = "temp.json"
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
		print("Video unavailable.\n")
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

if __name__ == "__main__":
	main()
