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
        templatePages = content['pages']
        templateType = content['type']

        if templateType == "website":
            """Loop through pages"""
            for page in templatePages:
                templateFramework = page['framework']
                templatePageName = page['name']
                if templateFramework == "bootstrap":
                    filePath = "web/bootstrap/main/"+templateName+"/"+templatePageName+".html"
                    # check if file path exits
                    if os.path.exists(filePath):
                        cssFolder = "css"
                        jsFolder = "js"
                        assets_folder = "assets"
                        image_folder = "img"
                        pageName = templatePageName+".html"
                        convertedOutput = ""

                        templateDist = dest / templateName
                        templateCssDist = dest / templateName / cssFolder
                        templateJsDist = dest / templateName / jsFolder
                        template_assets_dist = dest / templateName / assets_folder
                        template_images = template_assets_dist /image_folder

                        templateDist.mkdir(parents=True, exist_ok=True)

                        if page.get('sections'):
                            assets_path = "web/bootstrap/head/"+templateName+"/"+assets_folder
                            # check if assets file path exits
                            # if os.path.exists(assets_path):
                            #     image_path = "web/bootstrap/head/"+templateName+"/"+assets_folder+"/"+image_folder
                            #     if os.path.exists(image_path):
                            #         print("exists")
                            #         template_images.mkdir(parents=True, exist_ok=True)
                            #         shutil.copy2(image_path, template_images.relative_to(image_path))
                            with open(templateDist / pageName, 'w', encoding='UTF-8') as file:

                                convertedOutput += '<!DOCTYPE html>\n'
                                convertedOutput += '<html>\n<head>\n'
                                convertedOutput += '\t<meta charset="utf-8">\n\t<meta http-equiv="X-UA-Compatible" content="IE=edge">\n\t<title>Luday Template</title>\n\t<meta name="description" content="">\n\t<meta name="viewport" content="width=device-width, initial-scale=1">\n\t<!-- Bootstrap icons-->\n\t<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css" rel="stylesheet" />\n\t<!-- Core theme CSS-->\n'
                                file.writelines(convertedOutput)

                                with open(templateDist / pageName, 'a', encoding='UTF-8') as file:
                                    if page.get('css_file'):
                                        cssFilePath = page['css_file']
                                        cssFile = "web/bootstrap/head/"+templateName+"/css/"+cssFilePath

                                        templateCssDist.mkdir(parents=True, exist_ok=True)
                                        # TO DO:try and catch cssFile page exist before copying
                                        shutil.copy2(cssFile, templateCssDist)
                                        
                                        convertedOutput += '\t<link rel="stylesheet" href="css/'+cssFilePath+'">'

                                    if page.get('js_file'):
                                        jsFilePath = page['js_file']
                                        jsFile = "web/bootstrap/head/"+templateName+"/js/"+jsFilePath

                                        templateJsDist.mkdir(parents=True, exist_ok=True)
                                        # TO DO:try and catch jssFile page exist before copying
                                        shutil.copy2(jsFile, templateCssDist)

                                    convertedOutput += '\n</head>\n<body id="page-top">\n\t'

                                    if page.get('sections'):
                                        for section in page['sections']:
                                            if section.get('nav'):
                                                navFile = "web/bootstrap/main/"+templateName+"/sections/headers/"+section['nav']['file_name']+".html"
                                                # TO DO: Put assertion in try and catch
                                                assert os.path.exists(navFile)
                                                with open(navFile, 'r+', encoding='UTF-8') as nav:
                                                    for navLine in nav:
                                                        convertedOutput += navLine

                                            if section.get('div'):
                                                for div in section['div']:
                                                    if div['type'] == "header":
                                                        headerFile = "web/bootstrap/main/"+templateName+"/sections/columns/"+div['file_name']+".html"
                                                        # TO DO: Put assertion in try and catch
                                                        assert os.path.exists(headerFile)
                                                        with open(headerFile, 'r+', encoding='UTF-8') as div:
                                                            for divLine in div:
                                                                convertedOutput += divLine
                                                    elif div['type'] == "body":
                                                        bodyFile = "web/bootstrap/main/"+templateName+"/sections/columns/"+div['file_name']+".html"
                                                        # TO DO: Put assertion in try and catch
                                                        assert os.path.exists(bodyFile)
                                                        with open(bodyFile, 'r+', encoding='UTF-8') as body:
                                                            for body_line in body:
                                                                convertedOutput += body_line
                                                    elif div['type'] == "footer":
                                                        footer_file = "web/bootstrap/main/"+templateName+"/sections/footer/"+div['file_name']+".html"
                                                        # TO DO: Put assertion in try and catch
                                                        assert os.path.exists(footer_file)
                                                        with open(footer_file, 'r+', encoding='UTF-8') as footer:
                                                            for footer_line in footer:
                                                                convertedOutput += footer_line

                                    file.writelines(convertedOutput)                                    # data = file.readlines()
  
                                    # print(data)
                                    # data[1] = "Here is my modified Line 2\n"
                                    
                                    # with open('example.txt', 'w', encoding='utf-8') as file:
                                    #     file.writelines(data)
                                    # # print(line)
                                    # if line.startswith('<!DOCTYPE html>'):
                                    #     # print(line)
                                    #     line = line.strip() + '2012n'
                                    # file.write(line)

                                # for line in lines:
                                #     # line.rstrip                            
                                #     cssComment = "<!-- Core theme CSS-->"
                                #     if line == cssComment:
                                #         # copy css file
                                #         # nextLine = next(file)
                                #         cssFile = "web/bootstrap/head/"+templateName+"/css/"+cssFilePath
                                #         assert os.path.exists(cssFile)
                                #         shutil.copy2(cssFile, templateCssDist)
                                #         file.writelines('\n<link rel="stylesheet" href="css/bootstrap-v5-1-3.css">')
                                #         # with open(cssFile, "wb") as cssDir:
                                #         #     shutil.copy2(cssFile, templateCssDist)
                                #             # file.write('\n<link rel="stylesheet" href="css/bootstrap-v5-1-3.css">')
                                #         # insert CSS script
                                #         print(line)
