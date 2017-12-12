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
    print(analyzeRooms())
    buildRoomAvailList(analyzeRooms())


    #TEST binClasses() function:
    classList = [{'className':'MATH151C','days':[1, 3],'startTime':time(12,25),'endTime':time(13,30),'size':8, 'roomPrefs':'ARTS 102'},
                {'className':'MCOM201KZ','days':[1, 3],'startTime':time(14,00),'endTime':time(15,30),'size':8, 'roomPrefs':'ARTS 121'},
                {'className':'CSCI150','days':[1, 3],'startTime':time(14,00),'endTime':time(15,30),'size':8, 'roomPrefs':'ARTS 121'}]
    bins=binClasses(classList)
    bin1=binClasses(classList)[0]
    bin2=binClasses(classList)[1]


    # print(bins)

    # print(roomAvailList)
        # TEST blockRoom() function:
    for rooms in bin1:
        count=0
        # print(rooms,rooms['days'][0],rooms['days'][1], len(rooms['days']))
        for x in range(len(rooms['days'])):
            blockRoom (rooms['className'],rooms['roomPrefs'],rooms['days'][count], rooms['startTime'], rooms['endTime'])
            count+=1

    for rooms in bin2:
        pass


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
    # analyzeCourseOffering()


    return("Anaylzed")

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
    binTWO = sorted(binTWO, key=lambda classDetail: len(classDetail['classPrefs']))
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
        randomizeRoom(className, roomName, day, startT, endT)
        return False

def randomizeRoom(className, roomName, day, startT, endT):
    availableRooms=[]
    for room in analyzeRooms():
        print(room['BC 204'])
        #print a room that is available during this time slot,and has the room cap
        # if roomIsAvailable (room, day, startT, endT) and size>= sizeRoom:
        #     p
        #     print()
        # else:
        #     pass

    print('failed to schedule')


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
