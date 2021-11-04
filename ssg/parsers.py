from re import template
import shutil
import sys

from typing import List
from pathlib import Path

from docutils.core import publish_parts
from markdown import markdown
from ssg.content import Content
from collections import OrderedDict

import json as luday_parser


class Parser:
    extensions: List[str] = []

    def valid_extension(self, extension):
        return extension in self.extensions

    def parse(self, path: Path, source: Path, dest: Path):
        raise NotImplementedError

    def read(self, path):
        with open(path, "r") as file:
            return file.read()

    def write(self, path, dest, content, ext=".html"):
        full_path = dest / path.with_suffix(ext).name
        with open(full_path, "w") as file:
            file.write(content)

    def copy(self, path, source, dest):
        shutil.copy2(path, dest / path.relative_to(source))


class ResourceParser(Parser):
    extensions = [".jpg", ".png", ".gif", ".css", ".html"]

    def parse(self, path, source, dest):
        self.copy(path, source, dest)


class MarkdownParser(Parser):
    extensions = [".md", ".markdown"]

    def parse(self, path, source, dest):
        content = Content.load(self.read(path))
        html = markdown(content.body)
        self.write(path, dest, html)
        sys.stdout.write(
            "\x1b[1;32m{} converted to HTML. Metadata: {}\n".format(path.name, content)
        )


class ReStructuredTextParser(Parser):
    extensions = [".rst"]

    def parse(self, path, source, dest):
        content = Content.load(self.read(path))
        html = publish_parts(content.body, writer_name="html5")
        self.write(path, dest, html["html_body"])
        sys.stdout.write(
            "\x1b[1;32m{} converted to HTML. Metadata: {}\n".format(path.name, content)
        )

if sys.version_info[:2] < (3, 0):
    from cgi import escape as html_escape
    text = unicode
    text_types = (unicode, str)
else:
    from html import escape as html_escape
    text = str
    text_types = (str,)

class LudayParser(Parser):
    extensions = [".json"]

    def parse(self, path, source, dest, div_attributes="", encode=False):
        """
            Convert JSON to HTML format
        """
        # div attributes such as class, id, data-attr-*, etc.
        # eg: div_attributes = 'class = "col-md-6 d-flex"'
        self.div_init_markup = "<div %s>" % div_attributes
        json_input = None
        content = Content.load(self.read(path))
        if not content:
            json_input = {}
        elif type(content) in text_types:
            try:
                json_input = luday_parser.loads(content, object_pairs_hook=OrderedDict)
            except ValueError as e:
                #so the string passed here is actually not a json string
                # - let's analyze whether we want to pass on the error or use the string as-is as a text node
                if u"Expecting property name" in text(e):
                    #if this specific json loads error is raised, then the user probably actually wanted to pass json, but made a mistake
                    raise e
                json_input = content
        else:
            json_input = content
            # converted = self.convert_json_node(json_input)
            converted = json_input
        if encode:
            return converted.encode('ascii', 'xmlcharrefreplace')
        return json_input


        # template = {about_us_1:/templateFolder/about_us_1, about_us_2:/templateFoler/about_us_2}
        # content = Content.load(self.read(path))
        # loop: for each line in content:
        # for x in content:
            # if x == "heading_1":
                # dic = 
        #   if line is equal to #page:
            #   pageDic =  getNextLine
            #   if(pageDec.name equal to about_us):
                #   write /templateFolder/about_us to destination folder
            #   elseif((pageDec.name equal to contact):
                #   write /templateFolder/about_us_2 to destination folder
        #  nextline            

        # html = publish_parts(content.body, writer_name="html5")
        # self.write(path, dest, html["html_body"])
        # sys.stdout.write(
            # "\x1b[1;32m{} converted to HTML. Metadata: {}\n".format(path.name, content)
        # )