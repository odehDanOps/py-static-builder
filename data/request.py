import markdownify
import typer
import requests
import sys

# from ssg.parsers import Parser

def getHtml():
	url = 'https://afjfarms.com/home'

	get_request = requests.get(url)
	get_source_code = get_request.text
	full_path = "content/afj-index.html"
	# Parser.write(path='index', dest='content', content=get_source_code)
	with open(full_path, "w") as file:
		file.write(get_source_code)
		output = sys.stdout.write("\x1b[1;32m{} converted to HTML. Metadata: {}\n")
		return output

def htmlToMarkdown(html):
	markdown = markdownify.markdownify(html, heading_style="ATX")
	return markdown

if __name__ == '__main__':
	getHtml()
