# coding=utf-8

from datetime import datetime
import re

from pyquery import PyQuery
import requests

__author__ = 'namh'


class Dart(object):
    """
    Get the list of the business of report of the company which is passed as a parameter
    """

    def __init__(self):
        host = 'https://dart.fss.or.kr'
        self.autoSearchUrl = host + '/dsab001/search.ax'
        self.reportUrl = host + '/dsaf001/main.do\?rcpNo='

    def getReportLinks(self, name, start, end):
        """

        :param name:
        :param start: datetime
        :param end:   datetime
        :return:
            ['http://dart.df/.fjdkls',
            'http://link.to/report3',
            ...
            ]

        """

        r = requests.post(self.autoSearchUrl, data={
            "currentPage": 1,
            "maxResults": 15,
            "maxLinks": 10,
            "sort": '',
            "series": '',
            "textCrpCik": '00155319',
            "textCrpNm": name,
            "finalReport": 'recent',
            "startDate": start.strftime('%Y%m%d'),
            "endDate": end.strftime('%Y%m%d'),
            'publicType': 'A001'

        })

        links = re.findall(r'href="/dsaf001/main.do\?rcpNo=(\d*?)"', r.text, re.DOTALL)
        return links


class FinancialStatement(object):
    """
    Get the besuiness report with ids which is passed through the parameter
        example of the url : https://dart.fss.or.kr/dsaf001/main.do?rcpNo=324343

    """

    def __init__(self, fsIds):
        self.reportUrl = 'https://dart.fss.or.kr/dsaf001/main.do'
        self.detailUrl = detailUrl = 'https://dart.fss.or.kr/report/viewer.do'
        self.fsIds = fsIds

    def getItems(self, key):
        r = []
        for id in self.fsIds:
            r.append(self.getItem(id, key))

        return r

    def getItem(self, rid, key):
        """

        :param rid:
            report id, that is rcpNo
        :param key:
        :return:
        """

        r = requests.get(self.reportUrl, params={'rcpNo': rid})
        body = r.text.encode('utf-8')

        fswords = ['연결재무제표', '재무']
        for word in fswords:
            if body.find(word) != -1:
                sre = re.search(r"[\w\d\s]*?(?="
                                + word
                                + r").*?viewDoc\('(?P<rid>\d*?)'[\s,]*'(?P<dno>\d*?)'[\s,]*'(?P<eid>\d*?)'[\s,]*"
                                  r"'(?P<offset>\d*?)'[\s,]*'(?P<length>\d*?)'.*?\)",
                                body, re.DOTALL)

                if sre is not None:
                    dno = sre.group('dno')
                    eid = sre.group('eid')
                    offset = sre.group('offset')
                    length = sre.group('length')

                r = requests.get(self.detailUrl, params={'rcpNo': rid,
                                                         'dcmNo': dno,
                                                         'eleId': eid,
                                                         'offset': offset,
                                                         'length': length})

                unitkey = '단위'
                unit = re.search(r'\(\s*' +
                                 unitkey.decode('utf-8') +
                                 r'\s*\:\s*(.*?)\)', r.text).group(1)

                doc = PyQuery(r.text.encode('utf-8'))

                ftable = doc("th").closest('table')
                tdContainKey = ftable.find("td:contains('" + key.decode('utf-8') + "')").eq(0)

                return (ftable.find("th").eq(1).text(),
                        tdContainKey.text(),
                        tdContainKey.siblings().eq(0).text(),
                        unit)

        return None


class FinancialStatementXls(object):
    """
    visit the besuiness report and get the pdf of ids' which is passed through the parameter
        example of the url : https://dart.fss.or.kr/dsaf001/main.do?rcpNo=324343

    """

    def __init__(self, fsIds):
        self.reportUrl = 'https://dart.fss.or.kr/dsaf001/main.do'
        self.detailUrl = detailUrl = 'https://dart.fss.or.kr/report/viewer.do'
        self.excelDownloadUrl = 'https://dart.fss.or.kr/pdf/download/excel.do'

        self.fsIds = fsIds

    def downloadAll(self):
        for fid in self.fsIds:
            self.download(fid)




    def download(self, rid, outFileName='out'):
        """

        :param rid:
            report id, that is rcpNo
        :param key:
        :return:
        """

        ofile = "{outFileName}_{rid}.xls".format(outFileName=outFileName, rid=rid)
        r = requests.get(self.reportUrl, params={'rcpNo': rid})
        body = r.text.encode('utf-8')

        sre = re.search(r"openPdfDownload\('(?P<rid>\d*)'[\s,]*'(?P<dno>\d*)'\)", body, re.DOTALL)
        if sre is not None:

            r = requests.get(self.excelDownloadUrl, stream=True,
                             params={'lang': 'ko',
                                     'rcp_no': rid,
                                     'dcm_no': sre.group('dno')})
            with open(ofile, 'wb') as wf:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        wf.write(chunk)
                        # f.flush() commented by recommendation from J.F.Sebastian

        return


def main():
    dart = Dart()
    # https://dart.fss.or.kr/report/viewer.do?rcpNo=20150518000229&dcmNo=4674350&eleId=15&offset=912975&length=110889
    rids = dart.getReportLinks('POSCO', datetime(2011, 01, 01), datetime(2016, 01, 01))
    fs = FinancialStatementXls(rids)
    rs = fs.downloadAll()


if __name__ == '__main__':
    main()
