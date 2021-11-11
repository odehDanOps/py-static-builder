from re import template
import shutil
import sys
import os

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
        # print(path)


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

class LudayHtmlParser(Parser):
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

    extensions = [".json"]

    def parse(self, path, source, dest):

        obj = luday_parser.load(open(path))
        content = None

        if not obj:
            content = {}
        else:
            try:
                content = obj
            except ValueError as e:
                raise e

        # dir(content)
        templateName = content['template']
        if content['type'] == "website":
            """Loop through pages"""
            for page in content['pages']:
                if page['framework'] == "bootstrap":
                    filePath = "framework/bootstrap/main/"+templateName+"/"+page['name']+".html"
                    pageName = page['name']+".html"
                    if os.path.exists(filePath):
                        pointer = {
                            page['name']: filePath
                        }
                        shutil.copy2(pointer[page['name']], dest)
                        with open(dest / pageName,"a") as file:
                            file.write('<script></script>')
                        print(filePath, source, dest)
                # print(pages['sections'])
        # for key, value in pages.items():
        #     if key == "page_1" and value == "about_us_1":
        #         print(key)
        #         shutil.copy2(pointer["about_us_1"], dest)
        #     elif key == "page_2" and value == "about_us_2":
        #         shutil.copy2(pointer["about_us_2"], dest)

class JSONtoHTMLParser(Parser):
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
            """if <class 'str'>"""
            try:
                """{'key': 'value'} => OrderedDict([('key', 'value')])"""
                json_input = luday_parser.loads(content, object_pairs_hook=OrderedDict)
            except ValueError as e:
                # the string passed here is not a json string
                # let's analyze whether we want to pass on the error or use the string as-is as a text node
                if u"Expecting property name" in text(e):
                    #if this specific json loads error is raised, then the user probably actually wanted to pass json, but made a mistake
                    raise e
                json_input = content
        else:
            json_input = content
            converted = self.convert_json_node(json_input)
        if encode:
            return converted.encode('ascii', 'xmlcharrefreplace')
        return json_input

    def convert_json_node(self, json_input):
        """
            Dispatch JSON input according to the outermost type and process it
            to generate the super awesome HTML format.
            We try to adhere to duck typing such that users can just pass all kinds
            of funky objects to LudayParser that *behave* like dicts and lists and other
            basic JSON types.
        """
        if type(json_input) in text_types:
            if self.escape:
                return html_escape(text(json_input))
            else:
                return text(json_input)
        # dir(json_input)
        if hasattr(json_input, 'items'):
            return self.convert_object(json_input)
        if hasattr(json_input, '__iter__') and hasattr(json_input, '__getitem__'):
            return self.convert_list(json_input)
        return text(json_input)

    def convert_list(self, list_input):
        """"
            Iterate over the JSON list and process it
            to generate either an HTML  
        """
        if not list_input:
            return ""
        converted_output = ""
        column_headers = None
        # if self.clubbing:
            # column_headers = self.column_headers_from_list_of_dicts(list_input)
        if column_headers is not None:
            converted_output += self.div_init_markup
            converted_output += '<thead>'
            converted_output += '<tr><th>' + '</th><th>'.join(column_headers) + '</th></tr>'
            converted_output += '</thead>'
            converted_output += '<tbody>'
            for list_entry in list_input:
                converted_output += '<tr><td>'
                converted_output += '</td><td>'.join([self.convert_json_node(list_entry[column_header]) for column_header in
                                                     column_headers])
                converted_output += '</td></tr>'
            converted_output += '</tbody>'
            converted_output += '</table>'
            return converted_output

        #so you don't want or need clubbing eh? This makes @muellermichel very sad... ;(
        #alright, let's fall back to a basic list here...
        converted_output = '<ul><li>'
        converted_output += '</li><li>'.join([self.convert_json_node(child) for child in list_input])
        converted_output += '</li></ul>'
        return converted_output