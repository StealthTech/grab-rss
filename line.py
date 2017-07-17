import re
from bs4 import BeautifulSoup as BS
import requests


class Line:
	def __init__(self, string):
		self.string = string
		self.url = fetch_url(string)

		if not self.url.startswith('http'):
			self.url = 'http://' + self.url


		self.error = False
		self.rss = []

	def parse(self):
		text, error = get_content(self.url)
		if error:
			self.error = True
			return None

		self.text = text

		for handler in self.rss_finders:
			result = handler(text)
			if result:
				self.rss = result
				break

		del self.text


def fetch_url(string):
	url = re.compile("(https?:\/\/)?([a-z0-9_-]{2,100}\.){1,3}[a-z]{2,5}", re.I)
	match = url.search(string)
	if match:
		return match.group(0)
	else:
		return None


def get_content(url):
	error = None

	try:
		r = requests.get(url)
		if r.status_code != 200:
			error = r.status_code
	except:
		error = 'Unknown exception'

	if not error:
		return r.text, None
	else:
		return None, error


def find_rss_meta(text):
	page = BS(text, 'html.parser')
	meta = page.find_all('link', {'type': 'application/rss+xml'})

	links = []
	for link in meta:
		if link.has_attr('href'):
			links.append(str(link['href']))

	return links


if __name__ == '__main__':
	Line.rss_finders = [
			find_rss_meta,
			#find_rss_links,
			#find_rss_icon
	]


	line = Line('Real ITSM (realitsm.ru)')
	print(line.url)
	line.parse()
	print(line.rss)