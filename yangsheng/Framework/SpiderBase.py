# -*- coding: utf-8 -*-

import requests
import os
import time
import json
from Framework.LogBase import LogBase
from bs4 import BeautifulSoup


class SpiderBase:

    config={}
    request=requests

    def __init__(self):
        self.config = json.loads(LogBase.readText('./config.json'))

    def log(self, text):
        self.__writeText(self.config['logPath']['log'],text)

    def logError(self, text):
        self.__writeText(self.config['logPath']['error'], text)


    def htmlToObj(self,html):
        return BeautifulSoup(html, "html.parser")

    def getHtmlObj(self,url,decode='utf-8'):

        htmlRequest = self.request.get(url)
        html = htmlRequest.text.encode(htmlRequest.encoding).decode(decode)

        if htmlRequest.status_code==200:
            return  self.htmlToObj(html)
        else:
            return False


    def __writeText(self,path,text):

        if self.config['print']['logOrErrorPrint']:
            print(text)

        LogBase.writeTextDaybyDay(path,text)




