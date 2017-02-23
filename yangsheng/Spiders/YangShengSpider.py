from  Framework.SpiderBase import *
from  Models.YangShengModel import *
import re


class YangShengSpider(SpiderBase):
    classItems = [
        # {
        #     "url": "http://www.cnys.com/zixun/",
        #     "name": "养生咨询",
        #     "classid": 2,
        #     "classpath": "zixun"
        # },
        {
            "url": "http://www.cnys.com/shiliao/",
            "name": "食疗",
            "classid": 7,
            "classpath": "shiliao"
        },
        {
            "url": "http://www.cnys.com/jinji/",
            "name": "禁忌",
            "classid": 3,
            "classpath": "jinji"
        }
        ,
        {
            "url": "http://www.cnys.com/ysys/",
            "name": "饮食",
            "classid": 6,
            "classpath": "ysys"
        },
        {
            "url": "hhttp://www.cnys.com/xinde/",
            "name": "心得",
            "classid": 5,
            "classpath": "xinde"
        }

    ]
    urls=[]
    def __init__(self):
        self.model = SouFangWangModel()
        self.model.connection()
        SpiderBase.__init__(self)

    def start(self):

        self.log("服务启动")
        self.log("开始采集")

        # 获取分类
        # classItems = self.model.table("www_92game_net_cnys_enewsclass") \
        #     .select("classid,classpath").getRows()

        for item in self.classItems:
            self.spiderList(item)

    def spiderList(self, classItem,replace=''):
        self.log("开始采集:" + classItem['url'])
        objHtml = self.getHtmlObj(classItem['url'])
        if objHtml:
            nextUrl = objHtml.find('a', 'next')['href']
            objHtml = objHtml.find('ul', 'newslists')
        else:
            return
        urlall=self.model.table('www_92game_net_cnys_ecms_news').select('url').getRows()
        for item in urlall:
            self.urls.append(item.url)

        for item in objHtml.findAll('li', recursive=False):
            listInfo = {}
            listInfo['url'] = item.a['href']
            if listInfo['url'] in self.urls:
                self.log('采集过:%s,跳过'%(listInfo['url']))
                continue
            listInfo['dy'] = item.p.get_text()
            listInfo['pic'] = item.a.i.img['src']
            listInfo['classid'] = classItem['classid']
            listInfo['classpath'] = classItem['classpath']
            try:
                self.spiderInfo(listInfo)
            except:
                self.log('此url采集出错:'+classItem['url'])


        if classItem['url'].find(nextUrl)<0:
            classItem['url']=classItem['url'].replace(replace,'')+nextUrl
            self.spiderList(classItem,nextUrl)
        else:return

    def spiderInfo(self, listInfo):
        self.log("开始采集信息:" + listInfo['url'])
        objHtml = self.getHtmlObj(listInfo['url'])
        if objHtml:
            objHtml = objHtml.find('div', 'readbox')
        else:return

        itemInfo = {}
        itemInfo['url'] = listInfo['url']
        itemInfo['title'] = objHtml.h1.get_text()
        itemInfo['keyboard'] = objHtml.find('div', 'infos').span.string.replace("标签：", "")
        itemInfo['titlepic'] = listInfo['pic']
        itemInfo['smalltext'] = listInfo['dy']
        itemInfo['classid'] = listInfo['classid']

        timeMatch = re.match("(\d+-\d+-\d+\s\d+:\d+:\d+)", objHtml.find('div', 'infos').text)
        if timeMatch:
            timeArray = time.strptime(timeMatch.group(0), "%Y-%m-%d %H:%M:%S")
            timeMatch = int(time.mktime(timeArray))

        itemInfo['newstime'] = timeMatch
        itemInfo['truetime'] = itemInfo['newstime']
        itemInfo['lastdotime'] = itemInfo['newstime']
        itemInfo['truetime'] = itemInfo['newstime']
        itemInfo['ispic'] = 1
        itemInfo['havehtml'] = 1
        itemInfo['userid'] = 100
        itemInfo['username'] = 'dtl'

        content = objHtml.find('div', 'reads').prettify()

        page = objHtml.find('div', 'page').findAll('a')
        if len(page) > 1:
            for item in page[1:]:
                nextConent=self.getNextContent(item['href'])
                if nextConent:content += nextConent
                else:break

        result = self.model.table('www_92game_net_cnys_ecms_news').insert(itemInfo)
        id = result['insert_id']
        if id > 0:
            self.model.table('www_92game_net_cnys_ecms_news').whereID(id) \
                .update({
                "filename": id,
                "titleurl": "/%s/%s.html" % (listInfo['classpath'], id)
            })
            self.model.table("www_92game_net_cnys_ecms_news_index").insert({
                'id': id,
                'classid': listInfo['classid'],
                'checked': 1,
                'newstime': itemInfo['newstime'],
                'truetime': itemInfo['newstime'],
                'lastdotime': itemInfo['newstime'],
                'havehtml': 1,
            })

            self.model.table("www_92game_net_cnys_ecms_news_data_1").insert({
                'id': id,
                'classid': listInfo['classid'],

                'keyid': "",
                'dokey': 1,
                'newstempid': 0,
                'closepl': 0,
                'haveaddfen': 0,
                'infotags': itemInfo['keyboard'],
                'newstext': content
            })

    def getNextContent(self, url):
        result=self.getHtmlObj(url)
        if result:
            return result.find('div', 'reads').prettify()
        else:return False

    def spiderItemInfo2(self, ares, url, type):

        self.log("开始获取房产信息:" + url)
        objHtml = self.getHtmlObj(url).body

        itemInfo = {}
        itemInfo['url'] = url
        itemInfo['typeid'] = self.__getType(type)
        itemInfo['title'] = objHtml.find("div", "title").h2.string
        itemInfo['catid'] = self.__getcatid('')

        itemInfo['keyword'] = ''
        # for keyword in objHtml.find("div", "title").findAll('a'):
        #     itemInfo['keyword'] += keyword.string + ","
        # if len(itemInfo['keyword']) > 0: itemInfo['keyword'] = itemInfo['keyword'][0:-1]


        itemInfo['address'] = objHtml.find("div", "b_cardLeft").find('p')['title']
        itemInfo['areaid'] = ares.areaid

        xinxi = self.getHtmlObj(url + 'xinxi/').body
        text = xinxi.find('div', 'z_detail_main').string

        itemInfo['status'] = objHtml.find("span", "status").string
        itemInfo['telephone'] = objHtml.find(id="callmeBtn").text.replace('免费通话', '').replace('\n', '').replace('\t',
                                                                                                                '')

        itemInfo['adddate'] = objHtml.find("span", "time").em.string
        itemInfo['level'] = 5
        itemInfo['isnew'] = 1
        itemInfo['status'] = 3  # 信息通过
        itemInfo['buildtype'] = 3  # 信息通过

        itemInfo['thumb'] = ""
        thumbType = 0
        for item in objHtml.find("ul", "b_list_02 clearfix conClassName").findAll("li", recursive=False):
            if item.a['href'] != "javascript:void(0)":
                if thumbType == 0:
                    itemInfo['thumb'] = item.a.img['lsrc']
                else:
                    itemInfo['thumb'] = item.a.img['lazysrc']
                break

            else:
                thumbType = 1
                continue

        introduce = ''
        for item in xinxi.findAll('div', "z_main_box"):
            for li in item.findAll('li'):
                introduce += li.text + "\n"
                introduce += "\n\n"
        itemInfo['introduce'] = introduce

        result = self.model.table('aijiacms_newhouse_6').insertIgnore(itemInfo)
        if result['affected_rows'] > 0:
            self.log("获取 %s 房产信息成功" % (itemInfo['title']))
        else:
            self.log("%s 房产信息已存在库" % (itemInfo['title']))
