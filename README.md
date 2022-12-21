# UIUC Courses Dataset

UIUC Course Explorer data scraped from https://courses.illinois.edu/cisapp/explorer/schedule.xml

The current dataset spans from Fall 2004 to Spring 2023. 


## Structure 

Data structured as: schedule/[year]/[term]/[subject]/[course]/[section].xml

There are also XML files for each directory [year], [term], [subject], and [course]. Basically just add ".xml" to the end of the directory path, and it'll be the XML file. 

The directory structure is made to mirror the structure of the "href" links within the XML files such that the "href" links point to the correct file if accessing from the root directory of this repo.

E.g. the XML file for CS in Fall 2022 is "schedule/2022/fall/CS.xml", the XML file for CS 225 in Fall 2022 is "schedule/2022/fall/CS/225.xml", etc.

## TODO

* Refactor data from XML to JSON -- (XML format is clunky to handle, requiring directory traversals)
