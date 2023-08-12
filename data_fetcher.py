import os
import xml.etree.ElementTree as ET
import requests
from urllib.parse import urlparse
from datetime import datetime

error_list = []

def url_parser(href_url):
    url_path = urlparse(href_url).path
    if not url_path.endswith(".xml"):
        url_path = url_path + ".xml"
    url_path = url_path.replace("cisapp/explorer/", "")
    url_path = url_path.replace("cisapi/", "")
    return url_path

def xml_writer(path:str, response_content:bytes):
    with open(path + ".xml", "w") as file_out:
        file_out.write(response_content.decode("utf-8").replace("https://courses.illinois.edu/cisapp/explorer/", "").replace("https://courses.illinois.edu/cisapi/", ""))
        file_out.close()

# I wanted to do recursive DFS but I can't reliably do it since each layer has unique tags (i.e. sections, courses, subjects, terms, years)
# But still, here's a functional implementation of iterative DFS
def section_handler(parent_path, parent_xml:ET.Element):
    for section in parent_xml.find('sections'):
        try:
            sec_response = requests.get("https://courses.illinois.edu/cisapp/explorer" + url_parser(section.get('href')))
        except Exception as e:
            error_list.append(str(int(datetime.now().timestamp())) + ": Section get error " + url_parser(section.get('href')) + ": " + str(e))
            continue
        sec_path = parent_path + '/' + str(section.get('id'))
        xml_writer(sec_path, sec_response.content)

def course_handler(parent_path, parent_xml:ET.Element):
    for course in parent_xml.find("courses"):
        try:
            cou_response = requests.get("https://courses.illinois.edu/cisapp/explorer" + url_parser(course.get('href')))
            cou_xml = ET.fromstring(cou_response.content)
        except Exception as e:
            error_list.append(str(int(datetime.now().timestamp())) + ": Course get error \'" + url_parser(course.get('href')) + "\' -- " + str(e))
            continue
        cou_id = cou_xml.get('id').split()[1]
        cou_path = parent_path + '/' + cou_id
        if not os.path.isdir(cou_path):
            os.mkdir(cou_path)
        xml_writer(cou_path, cou_response.content)
        section_handler(cou_path, cou_xml)

def subject_handler(parent_path, parent_xml:ET.Element):
    for subject in parent_xml.find("subjects"):
        try:
            sub_response = requests.get("https://courses.illinois.edu/cisapp/explorer" + url_parser(subject.get('href')))
            sub_xml = ET.fromstring(sub_response.content)
        except Exception as e:
            error_list.append(str(int(datetime.now().timestamp())) + ": Subject get error \'" + url_parser(subject.get('href')) + "\' -- " + str(e))
            continue
        sub_id = sub_xml.get('id')
        sub_path = parent_path + '/' + sub_id
        if not os.path.isdir(sub_path):
            os.mkdir(sub_path)
        xml_writer(sub_path, sub_response.content)
        course_handler(sub_path, sub_xml)

def semester_handler(parent_path, parent_xml:ET.Element):
    for sem in parent_xml.find('terms'):
        try:
            sem_response = requests.get("https://courses.illinois.edu/cisapp/explorer"+ url_parser(sem.get('href')))
            sem_xml = ET.fromstring(sem_response.content)
        except Exception as e:
            error_list.append(str(int(datetime.now().timestamp())) + ": Sem get error \'" + url_parser(sem.get('href')) + "\' -- " + str(e))
            continue
        sem_id = sem_xml.find('label').text.lower().split()[0]
        sem_path = parent_path + "/" + sem_id
        if not os.path.isdir(sem_path):
            os.mkdir(sem_path)
        xml_writer(sem_path, sem_response.content)
        subject_handler(sem_path, sem_xml)

def year_handler(parent_path, parent_xml:ET.Element):
    for year in parent_xml.find("calendarYears"):
        try:
            yrs_response = requests.get("https://courses.illinois.edu/cisapp/explorer" + url_parser(year.get('href')))
            yrs_xml = ET.fromstring(yrs_response.content)
        except Exception as e:
            error_list.append(str(int(datetime.now().timestamp())) + ": Year get error \'" + url_parser(year.get('href')) + "\' -- " + str(e))
            continue
        yrs_id = yrs_xml.get('id')
        yrs_path = parent_path + "/" + yrs_id
        if not os.path.isdir(yrs_path):
            os.mkdir(yrs_path)
        xml_writer(yrs_path, yrs_response.content)
        semester_handler(yrs_path, yrs_xml)


sch_response = requests.get("https://courses.illinois.edu/cisapp/explorer/schedule.xml")
sch_xml = ET.fromstring(sch_response.content)
sch_path = "schedule"
if not os.path.isdir("schedule"):
    os.mkdir('schedule')


with open('error_log_' + str(int(datetime.now().timestamp())) + ".log", 'w', encoding='utf-8') as error_log:
    error_log.writelines("{}\n".format(error) for error in error_list)
    error_log.close()
