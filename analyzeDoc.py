from pyexcel_xlsx import get_data
import json
from datetime import time
import xlrd

def main():
    ''' Main function to run this class as standalone, mainly for testing. '''
    parsedData = importSpreadsheetData()
    for classDetail in parsedData[1]['classes']:
        print(classDetail)
    print('\n\nCLASSES SKIPPED...\n\n')
    for className in parsedData[1]['invalidClasses']:
        print(className)

def importSpreadsheetData():
    ''' Umbrella function to return list of rooms and list of classes,
        most useful when called from app.py '''
    roomsDict = parseRooms()
    classesList = parseCourseDetails(list(roomsDict))
    return {'roomsDict':roomsDict, 'classList':classesList}


def parseCourseDetails(roomsList,filename):
    ''' Function that reads in the list of classes from the appropriate
        spreadsheet and constructs a list of dictionaries, each dictionary
        containing relevant details of a single class that will be used
        by other parts of the program for room scheduling. The function also
        returns a list of rooms skipped due to inaccuracies in the presentation
        of the start-times and end-times data, because the program in its
        current state can only handle time fields with specific formatting.

        Returns a dictionary containing:
            'classes' :         list of class-detail dictionaries
            'invalidClasses' :  list of classes that had invalid time-field format
        '''

    allClasses= "static/img/"+filename



    # Open the workbook
    book = xlrd.open_workbook(allClasses)

    # get the list of sheets
    sheets = book.sheets()

    # print number of rows and cols in first sheet
    numberOfRows= sheets[1].nrows


    data= get_data(allClasses)
    s1=json.dumps(data)
    d2=json.loads(s1)
    # TODO: Standardize this to parse the template spreadsheet
    CLA= d2["CLA"][5:int(numberOfRows)]


    classes = []
    invalidClasses = []
    for row in range(len(CLA)):
        classValid = True
        # (1) Class name
        className= str(CLA[row][2]).strip() + str(CLA[row][3]).strip() + str(CLA[row][4]).strip()
        # (2-3) Class start and end times
        timeField = CLA[row][12]
        if not timeField:
            # Time field is blank
            classValid = False
        elif ('TBD' in timeField or 'TBA' in timeField):
            # Time field is 'TBD'
            classValid = False
        elif (' ' in timeField.strip()):
            # Time field contains spaces so is not in correct format
            classValid = False
        else:
            # Time field is in valid format, so parse
            # the start and end times into time() objects
            startTime_str, endTime_str = timeField[:timeField.index('-')], timeField[timeField.index('-')+1:]
            print(startTime_str, endTime_str)
            try:    startTimeSeparatorIndex = startTime_str.index(':')
            except: startTimeSeparatorIndex = startTime_str.index('.')
            try:    endTimeSeparatorIndex = endTime_str.index(':')
            except: endTimeSeparatorIndex = endTime_str.index('.')
            startTime = time(int(startTime_str[:startTimeSeparatorIndex]), int(startTime_str[startTimeSeparatorIndex+1:]))
            endTime = time(int(endTime_str[:endTimeSeparatorIndex]), int(endTime_str[endTimeSeparatorIndex+1:]))
        # (4) Days that class is offered as a list of numbers
        try:    days = [{'M':1,'T':2,'W':3,'R':4,'F':5}[day] for day in CLA[row][11]]
        except: days = []
        # (5) Class size (num of students)
        try:    classSize = int(CLA[row][14])
        except: classSize = 0
        # (6) Room needs and preferences of the class
        try:
            if CLA[row][16] in roomsList:
                # Class pref is a valid room
                roomPrefs= CLA[row][16]
                roomNeeds=0
            else:
                roomNeeds= CLA[row][16]
                roomNeeds=0
        except:
            roomNeeds=0
            roomPrefs= 0

        # If the current class is valid, construct the class detail dictionary
        # out of the above values and add it to the list of all classes
        if classValid:
            classes.append({'className':className, 'days':days, 'startTime':startTime, 'endTime':endTime, 'size':classSize, 'roomPrefs':roomPrefs})
        else:
            invalidClasses.append(className)

    # Return a dictionary containing the list of classes and the list
    # of classes considered invalid and thus excluded from consideration
    return {'classes':classes, 'invalidClasses':invalidClasses}

def parseRooms():
    allRooms= "static/img/Room_Sizes.xlsx"

    data= get_data(allRooms)
    s1=json.dumps(data)
    d2=json.loads(s1)
    ROOMS= d2["rooms"][1:]

    roomsDict = {}
    for row in range(len(ROOMS)):
        roomName = ROOMS[row][0]
        try:    capacity = room[counter][1]
        except: capacity = 0
        try:    features = room[counter][2]
        except: features = 0

        roomsDict[roomName] = [capacity, features]

    # Return roomsDict
    return roomsDict

if __name__ == '__main__':
    main()
