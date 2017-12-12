from flask import Flask, render_template, request
from datetime import time
from flask_uploads import UploadSet, configure_uploads, IMAGES, ALL
from pyexcel_xlsx import get_data
from operator import attrgetter, itemgetter
import json
from analyzeDoc import *
import math


app=Flask(__name__)
photos = UploadSet('photos', ALL)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

# Set global variables
roomAvailList = None

@app.route("/")
def index():


    return render_template("index.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        return show(filename)
    return render_template('upload.html')

def show(filename):
    filePosition= "static/img/"+filename

    data = get_data(filePosition)
    s1=json.dumps(data)
    # d2=json.loads(s1)
    # d2= d2["Summary"]
    # s2=json.dumps(d2)
    return s1


@app.route('/analyze', methods=['GET','POST'])
def analyze():
    # Import data from spreadsheet
    classesStuff = parseCourseDetails(parseRooms())
    classList = classesStuff['classes']
    invalidClasses = classesStuff['invalidClasses']

    buildRoomAvailList(parseRooms())


    #TEST binClasses() function:
    # classList = [{'className':'MATH151C','days':[1, 3],'startTime':time(12,25),'endTime':time(13,30),'size':8, 'roomPrefs':'ARTS 102'},
    #             {'className':'MCOM201KZ','days':[1, 3],'startTime':time(14,00),'endTime':time(15,30),'size':8, 'roomPrefs':'ARTS 121'},
    #             {'className':'CSCI150','days':[1, 3],'startTime':time(14,00),'endTime':time(15,30),'size':8, 'roomPrefs':'ARTS 121'}]
    bins=binClasses(classList)
    bin1=bins[0]
    bin2=bins[1]


    # print(bins)

    # print(roomAvailList)
        # TEST blockRoom() function:
    print(bin1)
    print('\n\n')
    print(bin2)
    print('\n\n')

    unscheduledClasses = []

    for classes in bin1:
        count=0
        # print(rooms,rooms['days'][0],rooms['days'][1], len(rooms['days']))
        for x in range(len(classes['days'])):
            if classes['roomPrefs'] == 0:
                pass
            else:
                if not (blockRoom (classes['className'],classes['roomPrefs'],classes['days'][count], classes['startTime'], classes['endTime'])):
                    # Wasn't scheduled
                    unscheduledClasses.append(classes)
            count+=1

    for classes in bin2:
        count=0
        # print(rooms,rooms['days'][0],rooms['days'][1], len(rooms['days']))
        for x in range(len(classes['days'])):
            if classes['roomPrefs'] == 0:
                pass
            else:
                if not (blockRoom (classes['className'],classes['roomPrefs'],classes['days'][count], classes['startTime'], classes['endTime'])):
                    # Wasn't scheduled
                    unscheduledClasses.append(classes)
            count+=1

    # fatalFailures = []
    #
    # for classes in unscheduledClasses:
    #     count=0
    #     # print(rooms,rooms['days'][0],rooms['days'][1], len(rooms['days']))
    #     for x in range(len(classes['days'])):
    #         if classes['roomPrefs'] == 0:
    #             pass
    #         else:
    #             nextRoom = nextFreeRoom()
    #             while not roomIsAvailable(nextRoom, classes['days'], classes['startTime'], classes['endTime']):
    #                 nextRoom = nextFreeRoom()
    #             if not (blockRoom (classes['className'], nextFreeRoom(),classes['days'][count], classes['startTime'], classes['endTime'])):
    #                 # Cannot be scheduled
    #                 fatalFailures.append(classes)
    #         count+=1



    print('\n\n')
    print(roomAvailList)
    print('\n\n')
    print(len(unscheduledClasses))
    print((len(bin1)+len(bin2))-len(unscheduledClasses))

    return render_template('success.html', roomAvailList=roomAvailList)

def binClasses(classList):
    ''' Classify classes into two bins:
            Bin One with classes with sizes above the threshold (explained below),
                sorted in descending order of class size.
            Bin Two with all other classes, sorted in increasing order of the number
                of preferred classrooms specified.
            (Threshold determines which classes go into bin one.
                We define threshold to be the constant value 0.75) '''
    highestSize = max([classDetail['size'] for classDetail in classList])
    threshold = math.floor(0.75 * highestSize)
    # Get bin one as all classes with size > threshold, then sort it
    binONE = [classDetail for classDetail in classList if classDetail['size'] >= threshold]
    binONE = sorted(binONE, key=itemgetter('size'), reverse=True)
    # Get bin two as all other classes, then sort in increasing
    # order of number of classroom preferences specified
    binTWO = [classDetail for classDetail in classList if classDetail not in binONE]
    binTWO = sorted(binTWO, key=itemgetter('size'), reverse=True)#lambda classDetail: len(classDetail['roomPrefs']))
    # Return two-item list containing bin one and bin two
    return [binONE, binTWO]

def buildRoomAvailList(roomList):
    ''' Dict with roomName as key containing:
            Dict with day as key containing:
                List with occupied slots, containing:
                    Three-item lists of class-name, start-time
                    and end-time of occupied slot. '''
    global roomAvailList    # since mutating
    roomAvailList = {roomName : {day : [] for day in range(1,6)} for roomName in roomList}

def blockRoom (className, roomName, day, startT, endT):
    ''' If room is available for the time slot for the specific day,
        block the room in the roomAvail dict and return the updated
        roomAvail dict. Otherwise, return FALSE. '''
    if roomIsAvailable (roomName, day, startT, endT):
        global roomAvailList    # since mutating
        roomAvailList[roomName][day].append([className, startT, endT])
        return True
    else:
        # randomizeRoom(className, roomName, day, startT, endT)
        return False

# def randomizeRoom(className, roomName, day, startT, endT):
#     ''' Two ways: (1) Look for next available room that fits size and schedule
#         (brute force). (2) Get list of available rooms, order in decreasing size,
#         order outstanding rooms in decreasing size, then do optimal allocation.
#         Stick with way (1) for now. '''
#     for room in parseRooms():
#         if roomIsAvailable(room, day)
#     availableRooms=[]
#     for room in parseRooms():
#         print(room['BC 204'])
#         #print a room that is available during this time slot,and has the room cap
#         # if roomIsAvailable (room, day, startT, endT) and size>= sizeRoom:
#         #     p
#         #     print()
#         # else:
#         #     pass
#
#     print('failed to schedule')

def nextFreeRoom():
    pass
    # for room in parseRooms


def roomIsAvailable(roomName, day, startT, endT):
    ''' Check availability from the roomAvail dict
        for roomName on day between startT and endT.
        This is done by checking if either the specified
        startTime or endTime within an existing occupied slot. '''
    for occupiedSlot in roomAvailList[roomName][day]:
        slotStartT, slotEndT = occupiedSlot[1], occupiedSlot[2]
        if (startT >= slotStartT and startT <= slotEndT) or (endT >= slotStartT and endT <= slotEndT):
            return False

    # Reached here, so not False
    return True


def features(roomID):
    ''' Probably not required until we use the database. '''
    ''' Queries database for roomFeaturesCode then decodes into
        the room features it represents, then returns a list of
        those features '''

    # Query database for list of room features
        # TODO : (return list from curson)

    # Query database for roomfeaturesCode
        # TODO : (returns int)

    # Convert roomFeaturesCode to binary


if __name__=="__main__":
    app.run(debug=True)
