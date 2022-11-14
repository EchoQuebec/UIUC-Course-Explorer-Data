import os
import xml.etree.ElementTree as ET
import requests
from urllib.parse import urlparse

sch_response = requests.get("https://courses.illinois.edu/cisapp/explorer/schedule.xml")
sch_xml = ET.fromstring(sch_response.content)

error_list = []

os.mkdir('schedule')

def url_parser(href_url):
    url_path = urlparse(href_url).path
    if not url_path.endswith(".xml"):
        url_path = url_path + ".xml"
    url_path = url_path.replace("cisapp/explorer/", "")
    url_path = url_path.replace("cisapi/", "")
    return "https://courses.illinois.edu/cisapp/explorer" + url_path

for year in sch_xml.find("calendarYears"):
    try:
        yrs_response = requests.get(url_parser(year.get('href')))
        yrs_xml = ET.fromstring(yrs_response.content)
    except Exception as e:
        error_list.append("Year get error \'" + url_parser(year.get('href')) + "\' -- " + str(e))
        print("Year get error " + url_parser(year.get('href')) + ": " + str(e))
        continue
    yrs_id = yrs_xml.get('id')
    os.mkdir('schedule/' + yrs_id)
    with open("schedule/" + yrs_id + '/' + yrs_id + ".xml", 'wb') as yrs_out:
        yrs_out.write(yrs_response.content)
        yrs_out.close()
    for sem in yrs_xml.find('terms'):
        try:
            sem_response = requests.get(url_parser(sem.get('href')))
            sem_xml = ET.fromstring(sem_response.content)
        except Exception as e:
            error_list.append("Sem get error \'" + url_parser(sem.get('href')) + "\' -- " + str(e))
            print("Sem get error " + url_parser(sem.get('href')) + ": " + str(e))
            continue
        sem_id = sem_xml.find('label').text.lower().split()[0]
        os.mkdir('schedule/' + yrs_id + '/' + sem_id)
        with open('schedule/' + yrs_id + '/' + sem_id + '/' + sem_id + ".xml", "wb") as sem_out:
            sem_out.write(sem_response.content)
            sem_out.close()
        for subject in sem_xml.find("subjects"):
            try:
                sub_response = requests.get(url_parser(subject.get('href')))
                sub_xml = ET.fromstring(sub_response.content)
            except Exception as e:
                error_list.append("Subject get error \'" + url_parser(subject.get('href')) + "\' -- " + str(e))
                print("Subject get error " + url_parser(subject.get('href')) + ": " + str(e))
                continue
            sub_id = sub_xml.get('id')
            os.mkdir('schedule/' + yrs_id + '/' + sem_id + '/' + sub_id)
            with open('schedule/' + yrs_id + '/' + sem_id +  "/" + sub_id + "/" + sub_id + ".xml", 'wb') as sub_out:
                sub_out.write(sub_response.content)
                sub_out.close()
            for course in sub_xml.find("courses"):
                try:
                    cou_response = requests.get(url_parser(course.get('href')))
                    cou_xml = ET.fromstring(cou_response.content)
                except Exception as e:
                    error_list.append("Course get error \'" + url_parser(course.get('href')) + "\' -- " + str(e))
                    print("Course get error " + url_parser(course.get('href')) + ": " + str(e))
                    continue
                cou_id = cou_xml.get('id').replace(" ", "_")
                os.mkdir('schedule/' + yrs_id + '/' + sem_id + '/' + sub_id + '/' + cou_id)
                os.mkdir('schedule/' + yrs_id + '/' + sem_id + '/' + sub_id + '/' + cou_id + '/sections')
                with open('schedule/' + yrs_id + '/' + sem_id + '/' + sub_id + "/" + cou_id + "/" + cou_id + ".xml", 'wb') as cou_out:
                    cou_out.write(cou_response.content)
                    cou_out.close()
                for section in cou_xml.find('sections'):
                    try:
                        sec_response = requests.get(url_parser(section.get('href')))
                    except Exception as e:
                        error_list.append("Section get error " + url_parser(section.get('href')) + ": " + str(e))
                        print("Section get error \'" + url_parser(section.get('href')) + "\' -- " + str(e))
                        continue
                    with open('schedule/' + yrs_id + '/' + sem_id + '/' + sub_id + '/' + cou_id + '/sections/' + str(section.get('id')) + ".xml", 'wb') as output:
                        print("doing section " + str(section.get('id')) + " at " + 'schedule/' + yrs_id + '/' + sem_id + '/' + sub_id + '/' + cou_id + '/sections/' + str(section.get('id')) + ".xml")
                        output.write(sec_response.content)
                        output.close()

with open('error_log.log', 'w', encoding='utf-8') as error_log:
    error_log.writelines("{}\n".format(error) for error in error_list)
    error_log.close()