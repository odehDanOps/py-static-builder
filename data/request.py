import markdownify
import typer
import requests

from .ssg.parsers import Parser

def getHtml():
	url = 'https://afjfarms.com/home'

	get_request = requests.get(url)
	get_source_code = get_request.text
	Parser.write(path='index', dest='content', content=get_source_code)

def htmlToMarkdown(html):
	markdown = markdownify.markdownify(html, heading_style="ATX")
	return markdown

if __name__ == '__main__':
	typer.run(getHtml())
