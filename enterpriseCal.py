import mechanize
from BeautifulSoup import BeautifulSoup
from soupselect import select
import logging
import datetime

class EnterpriseBrowser(object):
    def __init__(self,username, password):
        self.username = username
        self.password = password

    def getClassTable(self):
        br = mechanize.Browser()
        br.set_handle_robots(False)
        #directly open the U of I login page
        br.open("https://eas.admin.uillinois.edu/eas/servlet/EasLogin?redirect=https://webprod.admin.uillinois.edu/ssa/servlet/SelfServiceLogin?appName=edu.uillinois.aits.SelfServiceLogin&dad=BANPROD1")
        br.select_form(name="easForm")
        br["inputEnterpriseId"] = self.username#self.username
        br["password"] = self.password#self.password
        br.submit()
        br.open("https://ui2web1.apps.uillinois.edu/BANPROD1/bwskcrse.P_CrseSchdDetl")
        try:
            br.select_form(nr=1)
        except:
            return None
        resp = br.submit()
        soup = BeautifulSoup(resp.read())
        br.close()
        sem_info_row = BeautifulSoup(str(select(soup, "div.pagetitlediv table tr td")[2]))
        #get course metadata and append it to courses data
        course_sch_table = BeautifulSoup(str(select(soup,"div.pagebodydiv table")[-2]))
        courses = self.parseSchTable(course_sch_table)
        return courses

    #takes the whole table and parses it. Returns list of course dicts
    def parseSchTable(self, table_soup):
        courses = []
        for row_str in select(table_soup,"tr")[1:-1]:
            row_soup = BeautifulSoup(str(row_str))
            courses.append(self.parseSchRow(row_soup))
        return courses
    #takes each row and parses it and returns course dict
    def parseSchRow(self, row_soup):
        params = []
        for td in select(row_soup,"td"):
            td_soup = BeautifulSoup(str(td))
            params.append(td_soup.text)
        return self.class_json(params)

    def class_json(self, lst):
        crn = lst[0]
        course = lst[1]
        title = lst[2]
        campus = lst[3]
        credits = lst[4]
        level = lst[5]
        start_date = lst[6]
        end_date = lst[7]
        days_str =  lst[8]
        time = lst[9]
        location = lst[10]
        instructor = lst[11]



        start_date = self.parse_date(start_date)
        end_date = self.parse_date(end_date)
        #make sure the end date is at the last minute of the end date given
        end_date = end_date.replace(end_date.year, end_date.month, end_date.day, 23, 59,59)

        tmp_times = self.parse_time(time, start_date)
        start_time = tmp_times[0]
        end_time = tmp_times[1]

        days = ""
        for each in days_str:
            days = days + self.parse_day(each) + ','
        days = days[:-1] #remove the extra ',' from the end
        credits = int(float(credits))

        return {
            "crn":crn,
            "course":course,
            "title": title,
            "campus":campus,
            "credits":credits,
            "level":level,
            "start_date":start_date.strftime("%Y%m%dT%H%M%SZ"),
            "end_date":end_date.strftime("%Y%m%dT%H%M%SZ"),
            "days":days,
            "start_time":start_time.strftime("%Y-%m-%dT%H:%M:%S"), #RFC3339 conversion
            "end_time":end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "location":location,
            "instructor":instructor
        }



    def parse_day(self, day_letter):
        days_dict = {"M":"MO",
                        "T":"TU",
                        "W":"WE",
                        "R":"TH",
                        "F":"FR",
                        "S":"SA"}
        try:
            ret = days_dict[day_letter]
        except KeyError:
            ret = "SU"
        return ret

    def parse_date(self, date_str):
        # Aug 27, 2012 -> datetime object
        date_str = date_str.replace(",","")
        splitted = date_str.split(" ")
        month = self.parse_month(splitted[0])
        day = splitted[1]
        year = splitted[2]
        ret = datetime.datetime(int(year), int(month), int(day))
        return ret

    def parse_month(self, mnth):
        mnth_dict = {
            "JAN":1,
            "FEB":2,
            "MAR":3,
            "APR":4,
            "MAY":5,
            "JUN":6,
            "JUL":7,
            "AUG":8,
            "SEP":9,
            "OCT":10,
            "NOV":11,
            "DEC":12
        }
        try:
            ret = mnth_dict[mnth.upper()]
        except KeyError:
            ret = -1
        return ret

    #parses the time string and also takes in the start date as an argument
    #this is to return the optimal start and end for GCal
    def parse_time(self, time_str, start_date):
        # 12:00 pm - 12:50 pm -> datetime object
        if time_str == "TBA":
            start_time = datetime.datetime(start_date.year,start_date.month,start_date.day,12,0,0)
            end_time = datetime.datetime(start_date.year,start_date.month,start_date.day,13,0,0)
            return [start_time,end_time]
        #remove all the unneeded things and split into two
        splitted = (time_str.replace(" ","")).split("-")
        #now convert the splitted text into datetime objects
        start_time = self.parse_time_time(splitted[0])
        end_time = self.parse_time_time(splitted[1])
        #append the start_date to the created datetime objects
        start_time = start_time.replace(start_date.year, start_date.month, start_date.day)
        end_time = end_time.replace(start_date.year, start_date.month, start_date.day)
        return [start_time, end_time]
        

    def parse_time_time(self,time_str):
        #extract am/pm info
        am_pm = time_str[-2:]
        #extract time and hour
        time_str = time_str[:-2]
        splitted = time_str.split(":")
        hour = int(splitted[0])
        minute = int(splitted[1])
        #if pm up the hour by 12
        if(am_pm.upper() == "PM" and hour != 12):
            hour += 12
        if(hour == 12 and am_pm.upper() == "AM"):
            hour = 0
        ret = datetime.datetime(2000,1,1,hour,minute,0)
        return ret