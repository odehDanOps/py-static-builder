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

        templateName = content['template']
        templateDist = dest / templateName
        if content['type'] == "website":
            """Loop through pages"""
            for page in content['pages']:
                if page['framework'] == "bootstrap":
                    filePath = "web/bootstrap/main/"+templateName+"/"+page['name']+".html"
                    pageName = page['name']+".html"
                    # check if file path exits
                    if os.path.exists(filePath):
                        pointer = {
                            page['name']: filePath
                        }
                        cssFolder = "css"
                        templateDist = dest / templateName
                        templateCssDist = dest / templateName / cssFolder

                        templateDist.mkdir(parents=True, exist_ok=True)
                        templateCssDist.mkdir(parents=True, exist_ok=True)

                        cssFilePath = page['css_file']
                        shutil.copy2(pointer[page['name']], templateDist)
                        if cssFilePath:
                            with open(templateDist / pageName, 'r+', encoding='UTF-8') as file:
                                while (line := file.readline().rstrip()):
                            
                                    cssComment = "<!-- Core theme CSS-->"
                                    if cssComment in line:
                                        # copy css file
                                        cssFile = "web/bootstrap/head/"+templateName+"/css/"+cssFilePath
                                        assert os.path.exists(cssFile)
                                        with open(cssFile, "wb") as cssDir:
                                            shutil.copy2(cssFile, templateCssDist)
                                            # file.write('\n<link rel="stylesheet" href="css/bootstrap-v5-1-3.css">')
                                        # insert CSS script
                                        print(line)
