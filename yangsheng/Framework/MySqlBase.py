from Framework.LogBase import LogBase
import pymysql, json, time, os


class GetObject:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class MySqlBase:
    tableName = ""
    selectText = '*'
    whereText = ""

    def __init__(self):

        self.config = json.loads(LogBase.readText('./config.json'))

    def connection(self):
        self.conn = pymysql.connect(host=self.config['mysql']['host'],
                                    user=self.config['mysql']['user'],
                                    passwd=self.config['mysql']['passwd'],
                                    db=self.config['mysql']['db'],
                                    charset=self.config['mysql']['charset'])
        return self.conn

    def query(self, sql):
        cur = self.executeQuery(sql)
        resutls = cur.fetchall()

        rows = []
        row = {}
        index = 0
        for file in cur.description:
            row[index] = file[0]
            index = index + 1

        for resutl in resutls:
            index = 0
            oneRow = {}
            for one in resutl:
                oneRow[row[index]] = one
                index = index + 1
            rows.append(GetObject(**oneRow))

        cur.close()
        self.__clearP()
        return rows

    def executeQuery(self, sql):
        LogBase.writeTextDaybyDay(self.config['logPath']['sql'], sql, 'sql')
        cur = self.conn.cursor()
        cur._defer_warnings = True
        #cur.execute(sql)
        self.__clearP()
        return cur

    def execute(self, sql):
        LogBase.writeTextDaybyDay(self.config['logPath']['sql'], sql, 'sql')
        cur = self.conn.cursor()
        cur._defer_warnings = True
        #cur.execute(sql)
        self.__clearP()

        result = {}
        result['affected_rows'] = cur._result.affected_rows
        result['insert_id'] = cur._result.insert_id

        return result

    def close(self):
        self.conn.close()

    def table(self, tableStr):
        self.tableName = tableStr
        return self

    def whereID(self, id):
        self.whereText = 'where id =' + str(id)
        return self

    def select(self, text):
        self.selectText = text
        return self

    def getRows(self):

        sql = "select %s from %s %s" % (self.selectText, self.tableName, self.whereText)

        return self.query(sql)

    def where(self, field,value,operation="="):
        self.whereText = " where %s %s %s "%(field,operation,str(value))
        return self


    def where(self, whereText):
        self.whereText = 'where ' + whereText
        return self

    def __clearP(self):
        self.whereText = ""
        self.tableName = ""
        self.selectText = '*'

    def insert(self, item):
        keyValueStr = self.__getKeyValueStr(item)

        sql = "insert  into %s (%s) VALUES (%s)" % (self.tableName, keyValueStr['key'], keyValueStr['value'])

        return self.execute(sql)

    def insertIgnore(self, item):

        keyValueStr = self.__getKeyValueStr(item)

        sql = "insert ignore into %s (%s) VALUES (%s)" % (self.tableName, keyValueStr['key'], keyValueStr['value'])

        return self.execute(sql)

    def update(self, item):

        sql = "update  %s set %s %s" % (self.tableName, self.__makeUpdate(item), self.whereText)

        return self.execute(sql)

    def __getKeyValueStr(self, dict):
        sql = {}
        sql['key'] = ''
        sql['value'] = ''
        for key, value in dict.items():
            sql['key'] += "%s," % (key)
            sql['value'] += "%s," % (value if not isinstance(value, str) else "'%s'" % (value))
        if len(sql['key']) > 0: sql['key'] = sql['key'][0:-1]
        if len(sql['value']) > 0: sql['value'] = sql['value'][0:-1]
        return sql

    def __makeUpdate(self, dict):
        update = ''
        for key, value in dict.items():
            update += '%s = %s ,' % (key, value if not isinstance(value, str) else "'%s'" % (value))

        if len(update) > 0: update = update[0:-1]
        return update
