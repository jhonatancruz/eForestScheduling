from flask import Flask, render_template, request, session, redirect, url_for
from datetime import time
from flask_uploads import UploadSet, configure_uploads, IMAGES, ALL
from pyexcel_xlsx import get_data
from operator import attrgetter, itemgetter
import json
from analyzeDoc import *
import math, os

from flask import Flask, render_template, session, redirect, request, url_for
from googleapiclient.discovery import build
import google_auth_oauthlib.flow, google.oauth2.credentials, oauth2client
import requests
import psycopg2
import os



app=Flask(__name__)
photos = UploadSet('photos', ALL)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)
app.secret_key = 'Random value'

def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
        # TEST binClasses() function:
    # classList = [{'size':8, 'classPrefs':[1, 2]}, {'size':10, 'classPrefs':[1, 2]}, {'size':5, 'classPrefs':[3,4,5]}, {'size':6, 'classPrefs':[1, 2]}]
    # print(binClasses(classList))
        # TEST buildRoomAvailList() function:
    # roomAvailList = buildRoomAvailList(['hello', 'hey', 'hi'])
    # print(roomAvailList)
        # TEST blockRoom() function:
    # roomAvailList = blockRoom (roomAvailList, 'hello', 2, time(12, 25), time(13, 30))
    # print(roomAvailList)
    # print(blockRoom(roomAvailList, 'hello', 2, time(13, 00), time(14,00)))
    return render_template("index.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        global filename
        filename = photos.save(request.files['photo'])
        #return show(filename)
        return(render_template('success.html'))
    return render_template('upload.html')

@app.route('/analyze', methods=['GET','POST'])
def analyze():
    # Import data from spreadsheet
    classesStuff = parseCourseDetails(parseRooms(),filename)
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

    return render_template('showRooms.html', roomAvailList=roomAvailList)

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


# Login landing page
@app.route('/identity')
def identity():
    return render_template('identityLanding.html')

# Process OAuth authorization
@app.route('/identity/login')
def login():
    if 'credentials' not in session:
        # No user session is active
        return redirect(url_for('authorize'))
    try:
        # Load credentials from the session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        # Build the service object for the Google OAuth v2 API:
        oauth = build('oauth2', 'v2', credentials=credentials)
        # Call methods on the service object to return a response with the user's info:
        userinfo = oauth.userinfo().get().execute()
        print(userinfo)
    except google.auth.exceptions.RefreshError:
        # Credentials are stale
        return redirect(url_for('authorize'))

    # Verify that the user signed in with a 'drew.ed' email address:
    if 'hd' in userinfo: validDomain = userinfo['hd'] == 'drew.edu'
    else:                validDomain = False
    if not validDomain:
        return redirect(url_for('domainInvalid'))



    username = userinfo['email'][:userinfo['email'].index('@')]

    print(username)
    return render_template("upload.html")


@app.route('/identity/logout')
def logout():
    if 'credentials' in session:
        # Load the credentials from the session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        # Request the auth server to revoke the specified credentials:
        requests.post('https://accounts.google.com/o/oauth2/revoke',
            params={'token': credentials.token},
            headers = {'content-type': 'application/x-www-form-urlencoded'})
        # Delete the credentials from the session cookie:
        del session['credentials']

    if 'doNext' in request.args and request.args['doNext'] == 'login':
        return redirect(url_for('login'))
    else:
        return render_template('logoutSuccess.html')

@app.route('/identity/login/authorize')
def authorize():
    # Construct the Flow object:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret_217930784500-l9noq9hdupkormpjoamplnvsp3078q88.apps.googleusercontent.com.json',
    scopes = ['profile', 'email'])

    # Set the Redirect URI:
    flow.redirect_uri = url_for('oauth2callback', _external = True)

    # Generate URL for request to Google's OAuth 2.0 server:
    authorization_url, state = flow.authorization_url(
        # Enable offline access so as to be able to refresh an access token withou re-prompting the user for permission
        access_type = 'offline',
        # Enable incremental authorization
        include_granted_scopes = 'true',
        # Specify the Google Apps domain so that the user can only login using a 'drew.edu' email address.
        # NOTE: This can be overridden by the user by modifying the request URL in the browser, which is why the login() view  double-checks the domain of the logged-in user's email to ensure it's a 'drew.edu' email address.
        hd = 'drew.edu'
        )

    # Store the state so the callback can verify the auth server response:
    session['state'] = state

    return redirect(authorization_url)

# Process the authorization callback
@app.route('/identity/login/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can verified in the authorization server response:
    state = session['state']

    # Reconstruct the flow object:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret_217930784500-l9noq9hdupkormpjoamplnvsp3078q88.apps.googleusercontent.com.json',
    scopes = ['profile', 'email'],
    state = state)
    flow.redirect_uri = url_for('oauth2callback', _external = True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens:
    authorization_response = request.url.strip()
    flow.fetch_token(authorization_response = authorization_response)

    # Store credentials in the session:
    session['credentials'] = credentials_to_dict(flow.credentials)

    return redirect(url_for('login'))

# Display invalid-sign-in page and prompt for re-login:
@app.route('/identity/domainInvalid')
def domainInvalid():
    return render_template('domainInvalid.html')


# HELPER FUNCTIONS

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


if __name__=="__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8080, debug=True)
