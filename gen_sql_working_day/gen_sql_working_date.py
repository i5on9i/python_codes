# coding=utf-8
import os
import time
from datetime import date, timedelta

__author__ = 'namh'


def genSql(filepath='input.txt', startDate='2015-10-01', endDate='2015-12-31'):
    """
    generate all the dates

    input is the sorted dates in ascending order
    if date exists, set to true
    else set to false and set the pre_working_day with the last value

    :param filepath:
    :return:
    """
    DATE_INPUT_FORMAT = "%Y-%m-%d"
    TABLE_NAME = 'mfactors_workingdate'

    def getDate(line):
        return line.strip()

    def toDate(datestr):
        t = time.strptime(datestr, DATE_INPUT_FORMAT)
        return date(t.tm_year, t.tm_mon, t.tm_mday)

    def writeSql(date, isHoliday=False, preWorkingDate=None):
        tableName = TABLE_NAME
        preWdate = 'NULL' if preWorkingDate is None else "'%s'"%(preWorkingDate)

        isLastDayOfMonth = 'NULL'
        if (date + timedelta(days=1)).month != date.month:   # month is changed
            if isHoliday:
                # preWorkingDate of holiday is never be NULL
                print "UPDATE %s SET is_last_day_of_month = %s WHERE date='%s';" % (tableName, True, preWdate)
            else:
                isLastDayOfMonth = True


        if date.weekday() is 5:     # 4 : Friday
            if not isHoliday:
                print "insert into %s (date, is_holiday, pre_working_date, is_last_day_of_week, is_last_day_of_month) " \
                      "values('%s', %s, %s, %s, %s);" \
                      % (tableName, date, isHoliday, preWdate, True, isLastDayOfMonth)
            else:
                # preWorkingDate of holiday is never be NULL
                print "insert into %s (date, is_holiday, pre_working_date, is_last_day_of_month ) " \
                      "values('%s', %s, %s, %s );" \
                      % (tableName, date, isHoliday, preWdate, isLastDayOfMonth)
                print "UPDATE %s SET is_last_day_of_week = %s WHERE date=%s;" % (tableName, True, preWdate)


        else:
            print "insert into %s (date, is_holiday, pre_working_date, is_last_day_of_month ) values('%s', %s, %s, %s );" \
                  % (tableName, date, isHoliday, preWdate, isLastDayOfMonth)

    sdate = toDate(startDate)
    edate = toDate(endDate)
    cdate = sdate

    fpath = os.path.join('.', 'inputs', filepath)
    with open(fpath, 'r') as f:

        isHoliday = False

        # while cdate <= edate:
        preWorkingDate = None
        for line in f:
            datestr = getDate(line)
            indate = toDate(datestr)

            if indate < cdate:
                # if the input date is smaller than the startDate
                # skip inputs to the startDate
                continue

            if indate > cdate:
                # cdate does not exist in a input date file
                while indate > cdate:
                    writeSql(cdate, True, preWorkingDate)
                    cdate += timedelta(1)    # +1 day

            # cdate exists in a input file
            writeSql(cdate)
            preWorkingDate = indate
            cdate += timedelta(1)


def genSql2(filepath='per.txt', startDate='2015-10-01', endDate='2015-12-31'):
    """
        To generate the sql command to insert into the table mfactors_stockprice
        input files contents are just copied from the excel file.

        :output
            insert into mfactors_stockprice (code, date, closing_price,
                stock_count, per, pbr, market_capital, eps)
            values('A005930', '2015-10-01', 613000, NULL, 11.06, 1.75, 9.02945E+13,
                     -0.21);
    """


    def getDateList():

        dates = []
        inputFile = os.path.join('.', 'inputs', 'input.txt')
        with open(inputFile, 'r') as f:

            for line in f:

                dates.append({
                    'date': line.strip()
                })
        return dates

    def getPerList():
        inputFile = os.path.join('.', 'inputs', 'per.txt')
        companies = []
        with open(inputFile, 'r') as f:
            for line in f:
                item = {}
                vs = line.split('\t')
                companies.append({
                    'name' : vs[1],
                    'code' : vs[0],
                    'per_list' : vs[6:]
                })
        return companies

    def getValueDict(inputFile):

        ret = {}
        with open(inputFile, 'r') as f:
            for line in f:
                vs = line.split('\t')
                ret[vs[0]] = vs[6:]
        return ret

    def getIpoValueDict(inputFile):
        ret = {}
        with open(inputFile, 'r') as f:
            code = ''
            item = []
            for line in f:
                vs = line.split('\t')
                if vs[0] == '----':
                    ret[code] = item
                    item = []
                    code = vs[1].strip()
                    continue

                item.append(vs)

        return ret


    def getForecastValueDict(inputFile):
        ret = {}
        with open(inputFile, 'r') as f:
            for line in f:
                vs = line.split('\t')
                ret[vs[0]] = {
                    'rcount' : vs[6],
                    'date': '2015-10-02',
                    'cs3m':  vs[7],
                    'cs1m': vs[8],
                }

        return ret

    '''
        Start Here...
    '''
    sub = os.path.join('.', 'inputs')

    dates = getDateList()
    companies = getPerList()
    caps = getValueDict(os.path.join(sub, 'cap.txt'))
    pbrs = getValueDict(os.path.join(sub, 'pbr.txt'))
    eps1s = getValueDict(os.path.join(sub, 'eps1.txt'))
    prices = getValueDict(os.path.join(sub, 'closing_price.txt'))

    ipoinfo = getIpoValueDict(os.path.join(sub, 'ipo.txt'))
    # forecast = getIpoValueDict(os.path.join(sub, 'forecast.txt'))




    table = 'mfactors_stockprice'
    market = 'kospi'

    for cp in companies:
        i = 0
        code = cp['code']
        caplist = caps[code]
        pbrlist = pbrs[code]
        eps1list = eps1s[code]
        pricelist = prices[code]

        ipolist = None
        if code in ipoinfo:
            ipolist = ipoinfo[code]

        for date in dates:

            per = cp['per_list'][i]
            cap = caplist[i]
            pbr = pbrlist[i]
            eps1 = eps1list[i]
            closePrice = pricelist[i]

            openPrice = 'NULL'
            highPrice = 'NULL'
            lowPrice = 'NULL'
            if ipolist is not None:
                ipol = ipolist[i]
                closePrice = ipol[0]
                openPrice = ipol[1]
                highPrice = ipol[2]
                lowPrice = ipol[3].strip()


            print "insert into %s (code, date, market, close_price, stock_count, per, pbr, market_capital, eps," \
                  " open_price, high_price, low_price)" \
                  " values('%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s);"\
                  %(table, code, date['date'], market, closePrice, 'NULL', per, pbr, cap, eps1,
                    openPrice, highPrice, lowPrice)
            i+=1





def main():
    genSql()

if __name__ == '__main__':
    main()
