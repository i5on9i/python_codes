# coding=utf-8
import time
from datetime import date, timedelta

__author__ = 'namh'


def genSql(filepath='input.txt', startDate='2015-12-01', endDate='2015-12-31'):
    """
    generate all the dates

    input is the sorted dates in ascending order
    if date exists, set to true
    else set to false and set the pre_working_day with the last value

    :param filepath:
    :return:
    """
    DATE_INPUT_FORMAT = "%Y-%m-%d"
    TABLE_NAME = 'test_working_date'

    def getDate(line):
        return line.strip()

    def toDate(datestr):
        t = time.strptime(datestr, DATE_INPUT_FORMAT)
        return date(t.tm_year, t.tm_mon, t.tm_mday)

    def writeSql(date, isHoliday=False, preWorkingDate=None):
        tableName = TABLE_NAME
        preWdate = 'NULL' if preWorkingDate is None else preWorkingDate
        print "insert into %s (date, is_holiday, pre_working_date) values('%s', %s, %s);" % (tableName, date, isHoliday, preWdate)

    sdate = toDate(startDate)
    edate = toDate(endDate)
    cdate = sdate

    with open(filepath, 'r') as f:

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


def main():
    print genSql()

if __name__ == '__main__':
    main()
