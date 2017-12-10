from flask import Flask, render_template, request
from datetime import time
from flask_uploads import UploadSet, configure_uploads, IMAGES, ALL
from pyexcel_xlsx import get_data
import json

app=Flask(__name__)
photos = UploadSet('photos', ALL)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

@app.route("/")
def index():
    roomAvailList = buildRoomAvailList(['hello', 'hey', 'hi'])
    print(roomAvailList)
    roomAvailList = blockRoom (roomAvailList, 'hello', 2, time(12, 25), time(13, 30))
    print(roomAvailList)
    print(blockRoom(roomAvailList, 'hello', 2, time(13, 00), time(14,00)))
    return render_template("index.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        return anaylze(filename)
    return render_template('upload.html')

def anaylze(filename):
    filePosition= "static/img/"+filename
    # files= open(filePosition, "r")
    # wb = load_workbook(filename=filePosition, read_only=True)
    # ws = wb['Summary']
    #
    # for row in ws.rows:
    #     print(row)
    # return("opened file")

    data = get_data(filePosition)
    s1=json.dumps(data)
    d2=json.loads(s1)
    d2= d2["Summary"]
    s2=json.dumps(d2)
    return s2
    # return(jsonDict)

    # return jsonDict['Summary']


def buildRoomAvailList(roomList):
    ''' Dict with roomName as key containing:
            Dict with day as key containing:
                List with occupied slots, containing:
                    Two-item lists of start-time
                    and end-time of occupied slot. '''
    return {roomName : {day : [] for day in range(1,6)} for roomName in roomList}

def blockRoom (roomAvail, roomName, day, startT, endT):
    ''' If room is available for the time slot for the specific day,
        block the room in the roomAvail dict and return the updated
        roomAvail dict. Otherwise, return FALSE. '''
    if roomIsAvailable (roomAvail, roomName, day, startT, endT):
        roomAvail[roomName][day].append([startT, endT])
        return roomAvail
    else:
        return False

def roomIsAvailable(roomAvail, roomName, day, startT, endT):
    ''' Check availability from the roomAvail dict
        for roomName on day between startT and endT.
        This is done by checking if either the specified
        startTime or endTime within an existing occupied slot. '''
    for occupiedSlot in roomAvail[roomName][day]:
        slotStartT, slotEndT = occupiedSlot[0], occupiedSlot[1]
        if (startT > slotStartT and startT < slotEndT) or (endT > slotStartT and endT < slotEndT):
            return False

    # Reached here, so not False
    return True


def features(roomID):
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
