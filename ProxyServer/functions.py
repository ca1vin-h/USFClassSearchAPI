import requests
from bs4 import BeautifulSoup
import os.path
import json
from fastapi import HTTPException


# requests data from url with headers
# returns the data in json format
def requestData(P_SEMESTER, P_SUBJ, P_NUM):

    url = "http://usfweb.usf.edu/DSS/StaffScheduleSearch/StaffSearch/Results"
    data = {"P_SEMESTER": P_SEMESTER, "P_SUBJ": P_SUBJ, "P_NUM": P_NUM}

    # make the request using the above headers
    response = requests.post(url, data=data)

    # use beautiful soup to parse the html response from the staff search
    soup = BeautifulSoup(response.text, 'html.parser')

    # Replace all occurrences of '\u00a0' with ' ' in the BeautifulSoup object's strings (CRS SUBJ#)
    for string in soup.strings:
        if '\u00a0' in string:
            string.replace_with(string.replace('\u00a0', ' '))

    # replace br tags with space to help split classes that have different meeting times on different days
    for br_tag in soup.find_all('br'):
        br_tag.replace_with(' ')

    table = soup.find('table', id='results')

    # create the json object
    row_data = {}
    row_data["semester"] = P_SEMESTER
    row_data["subject"] = P_SUBJ
    row_data["number"] = P_NUM
    row_data["sections"] = []

    for row in table.find_all('tr')[1:]:
        # Store the rest of the data under the "sections" key
        sections = {}
        headers = [header.get_text().strip().replace('\n', ' ').replace(' ', '_').replace("#", "")
                   for header in table.find_all('th')]
        for i, cell in enumerate(row.find_all(['td'])):
            # print(cell.get_text().strip().replace('\xa0', ' '))
            sections[headers[i]] = cell.get_text().strip().replace('\xa0', ' ').replace("#", "")

        # Remove keys
        '''
        del_keys = ["SUBJ_CRS#"]
        for key in del_keys:
            if key in sections:
                del sections[key]
        '''

        # split schedules for classes that have multiple meet times
        sections['DAYS'] = sections['DAYS'].split(' ')
        sections['TIME'] = sections['TIME'].split(' ')
        sections['BLDG'] = sections['BLDG'].split(' ')
        sections['ROOM'] = sections['ROOM'].split(' ')

        # check if course is what was requested
        if not sections['SUBJ_CRS'] == P_SUBJ + ' ' + P_NUM:
            continue

        # remove dual enrollment only classes
        if "DUAL ENROLLMENT".lower() in sections['TITLE'].lower():
            continue
        

        print("\n\n")

        if sections['DAYS'] == ['']:
            sections['DAYS'] = "ONLINE"
        else:
            #make date/time easier to use 
            dayDict = {'M': [], 'T': [], 'W': [], 'R': [], 'F': [], 'S': []}
            for day, time in zip(sections['DAYS'], sections['TIME']):
                for key in dayDict:
                    if key.upper() in day.upper():
                        dayDict[key].append(time)
            sections['DAYS'] = dayDict
        del sections['TIME']




        row_data["sections"].append(sections)
    return row_data



def checkCourseCache(P_SEMESTER, P_SUBJ, P_NUM):
    if not os.path.exists(P_SEMESTER + "/"):
        os.mkdir(P_SEMESTER + "/")

    # check if course has already been scraped
    if os.path.isfile(P_SEMESTER + "/" + P_SUBJ + "/" + P_NUM + ".json"):
        with open(P_SEMESTER + "/" + P_SUBJ + "/" + P_NUM + ".json", 'r') as f:
            print("file found in cache")
            return json.loads(f.read())

    # check if course has been found to not exist
    if os.path.isfile(P_SEMESTER + "/" + "junkClasses.csv"):
        with open(P_SEMESTER + "/" + "junkClasses.csv") as f:
            for line in f:
                if line.strip() == P_SEMESTER + "," + P_SUBJ + "," + P_NUM:
                    print("Bad course 1")
                    raise HTTPException(
                        status_code=404, detail="No sections found from previous time course was checked")

    # request the json object
    stuff = requestData(P_SEMESTER, P_SUBJ, P_NUM)

    # check if no data found
    if stuff["sections"] == []:
        with open(P_SEMESTER + "/" + "junkClasses.csv", 'a') as f:
            # write junk class to list of junk classes
            f.write(P_SEMESTER + "," + P_SUBJ + "," + P_NUM + "\n")
            print("Bad course 2")
            raise HTTPException(status_code=404, detail="No sections found")
    else:
        # make semester/subject folders
        if not os.path.exists(P_SEMESTER + "/" + P_SUBJ):
            os.makedirs(P_SEMESTER + "/" + P_SUBJ)
        # write json file to semester/subject/number.txt
        with open(P_SEMESTER + "/" + P_SUBJ + "/" + P_NUM + ".json", 'a') as f:
            f.write(json.dumps(stuff))
            print("File scraped")
            return stuff


# check if valid semester
def validateSemester(P_SEMESTER):
    with open("validFormData/validSemesters.txt") as f:
        for line in f:
            if line.strip() == P_SEMESTER:
                return True
    return False


# check if valid class
def validateClass(P_SUBJ, P_NUM):
    with open("validFormData/validCourses.csv") as f:
        for line in f:
            if line.split(',')[0].strip() == P_SUBJ + " " + P_NUM:
                return True
    return False

#validate semester and course
def validateAndRequest(P_SEMESTER, P_SUBJ, P_NUM):
    if not validateSemester(P_SEMESTER):
        raise HTTPException(status_code=400, detail="Invalid Semester")
    if not validateClass(P_SUBJ, P_NUM):
        raise HTTPException(
            status_code=400, detail="Invalid Course - Course not found on USF Course Catalog as of 3/15/2024")
    return checkCourseCache(P_SEMESTER, P_SUBJ, P_NUM)


#print(validateAndRequest("202408", "PHY", "2049"))
'''




stuff = checkCourseCache(P_SEMESTER, P_SUBJ, P_NUM)



print(json.dumps(stuff, indent=4))

exit()
if "semester" in stuff and stuff["semester"] == "202408":
    if "subject" in stuff and stuff["subject"] == "COP":
        if "number" in stuff and stuff["number"] == "4931":
            if "sections" in stuff and not stuff["sections"] == []:
                print("yup")
                '''
