from flask import Flask, render_template, request, send_file
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
classList = None

# TODO: Rather than keeping the course info
#       in a dictionary, upgrade it to instances
#       of the below class
class Course:
    """ Holds all fields of data for a single course."""
    def __init__(self, className, days = None, startTime = None, endTime = None, size = None, roomPrefs = None, room = None):
        self.className = className
        self.days = days
        self.startTime = startTime
        self.endTime = endTime
        self.size = size
        self.roomPrefs = roomPrefs
        self.room = room

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        global filename
        filename = photos.save(request.files['photo'])
        return analyze()
    return render_template('upload.html')

def show(filename):
    filePosition= "static/img/"+filename

    data = get_data(filePosition)
    s1=json.dumps(data)
    # d2=json.loads(s1)
    # d2= d2["Summary"]
    # s2=json.dumps(d2)
    return s1

@app.route( "/export" )
def export():
    print( "Files files files" )
    outputFile = "static/RoomAssignments.csv"
    with open( outputFile, "w" ) as out:
        out.write( "This is Test Data" )
    return send_file( outputFile, attachment_filename="RoomAssignments.csv" )

@app.route('/analyze', methods=['GET','POST'])
def analyze():
    try:
        # Import data from spreadsheet
        global classList
        classList, invalidClasses = parseCourseDetails(parseRooms(), filename)
        # classesStuff = parseCourseDetails(parseRooms(),filename)
        # classList = classesStuff['classes']
        # invalidClasses = classesStuff['invalidClasses']

        buildRoomAvailList(parseRooms())
        bins = binClasses(classList)
        bin1 = bins[0]
        bin2 = bins[1]

        unscheduledClasses = []

        # PERFORM ACTUAL SCHEDULING
        # Step 1a : Bin 1
        unscheduledClasses.extend(DO_THE_ACTUAL_SCHEDULING(bin1, True))
        # Step 1b : Bin 2
        unscheduledClasses.extend(DO_THE_ACTUAL_SCHEDULING(bin2, True))
        # Step 2  : Classes that were not scheduled in Step 1
        fatalFailures = []
        fatalFailures.extend(DO_THE_ACTUAL_SCHEDULING(unscheduledClasses, False))

        # PREPPING LISTS FOR EASY TEMPLATING
        # Sort alphabetically by className
        classList = sorted(classList, key=itemgetter('className'))
        # Group into dictionaries by class Name regardless of section
        courseDict = {}
        for course in classList:
            courseAbbr, sectionAbbr = getCourseAbbrs(course['className'])
            course['section'] = sectionAbbr
            if courseAbbr not in courseDict.keys():
                courseDict[courseAbbr] = []
            courseDict[courseAbbr].append(course)

        # return render_template('showRooms.html', roomAvailList=roomAvailList)
        return render_template('showRooms.html', courseDict = courseDict)

    except Exception as e:
        print( e )
        return render_template( 'formatfailure.html' )

def DO_THE_ACTUAL_SCHEDULING(binOfClasses, attemptPreferenceBasedScheduling):
    unscheduledClasses = []
    for course in binOfClasses:
        # if course['className'] == "EAP101ZM":
            # import pdb; pdb.set_trace()
        if course['roomPrefs'] and attemptPreferenceBasedScheduling:
            # There is a preferred so cheeck if it is available for the course days
            roomAvailable = True
            for day in course['days']:
                if not roomIsAvailable(course['roomPrefs'], day, course['startTime'], course['endTime']):
                    roomAvailable = False
                    break;
            # IF room was found to be available, schedule the course:
            if roomAvailable:
                for day in course['days']:
                    blockRoom(course['className'], course['roomPrefs'], day, course['startTime'], course['endTime'])
            else:
                unscheduledClasses.append(course)
        else:
            # There are no preferred rooms so assign this course a RANDOM ROOM
            room = findAvailableRoom(course['days'], course['startTime'], course['endTime'])
            if room:
                # A room was found
                for day in course['days']:
                    blockRoom(course['className'], room, day, course['startTime'], course['endTime'])
            else:
                # No room could be found for the course
                unscheduledClasses.append(course)
    return unscheduledClasses



def getCourseAbbrs(courseName):
    """ Returns department abbreviation from course name by returning all characters
        up to the second set of alphabetical characters. The first set of alphabets
        is always the dept. abbr. and the following set of numbers is the course level,
        both of which make up the desired abbreviation. A series of alphabets always
        follows the course level.
    """
    deptAbbrFound = False
    courseLevelFound = False
    for index, char in enumerate(courseName):
        if char.lower() in 'abcdefghijklmnopqrstuvwxyz' and deptAbbrFound and courseLevelFound:
            courseAbbr = courseName[:index]
            sectionAbbr = courseName[index:]
            return courseAbbr, sectionAbbr
        elif char.lower() in 'abcdefghijklmnopqrstuvwxyz':
            deptAbbrFound = True
        elif char in '1234567890':
            courseLevelFound = True



def findAvailableRoom(days, startT, endT):
    # FOR EACH ROOM IN roomAvailList : For each of the days check if the timeslot is available,
        # otherwise check next room. Return first room that's found
    for room in roomAvailList:
        roomAvailable = True
        for day in days:
            if not roomIsAvailable(room, day, startT, endT):
                roomAvailable = False
                break
        # If roomAvailable is True at this line then the inner for loop was not broken out of
        if roomAvailable:
            return room
    # If execution reaches this point, a room hasn't been found
    return None



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
    # binTWO = sorted(binTWO, key=lambda classDetail: len(classDetail['roomPrefs']))
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
        block the room in the roomAvail dict and return TRUE. Otherwise,
        return FALSE. '''
    if roomIsAvailable (roomName, day, startT, endT):
        # Block the room in the roomAvailList:
        global roomAvailList    # since mutating
        roomAvailList[roomName][day].append([className, startT, endT])
        # Add the room assignment to the specific course in the classList:
        global classList    # since mutating
        for course in classList:
            if course['className'] == className:
                course['room'] = roomName
        # Return the confirmation
        return True
    else:
        return False



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
        # TODO : (return list from cursor)

    # Query database for roomfeaturesCode
        # TODO : (returns int)

    # Convert roomFeaturesCode from binary to dict


if __name__=="__main__":
    app.run()
