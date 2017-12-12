from pyexcel_xlsx import get_data
import json


def analyzeCourseOffering():
    classes={}
    allClassses= "static/img/ALL.Spring2018CourseOfferingGrid.xlsx"

    data= get_data(allClassses)
    s1=json.dumps(data)
    d2=json.loads(s1)
    cla= d2["CLA"][5:-4]
    count=0
    for x in cla:
        className= str(cla[count][2])+str(cla[count][3])+str(cla[count][4])
        try:
            times= cla[count][12].split('-')
            startTime= times[0]
        except:
            times= cla[count][12]
        try:
            endTime= times[1]
        except:
            endTime = cla[count][12]
        try:
            days= cla[count][11]
        except:
            days=0
        try:
            classSize= cla[count][14]
        except:
            classSize= 0
        try:
            if cla[count][16] in joinedRooms:
                classPref= cla[count][16]
                classNeeds=0
            else:
                classNeeds= cla[count][16]
                classNeeds=0
        except:
            classNeeds=0
            classPref= 0

        # Process and put into list of dictionaries:


        # print(className, startTime, endTime, days, classSize, classNeeds, claasPref)
        classes[className]=[startTime, endTime, days, classSize, classNeeds, classPref]
        count+=1
    print(classes)

def analyzeRooms():
    global joinedRooms
    joinedRooms=[]
    rooms={}
    allRooms= "static/img/Room_Sizes.xlsx"
    data= get_data(allRooms)
    s1=json.dumps(data)
    d2=json.loads(s1)
    room= d2["rooms"][1:]
    counter=0
    for x in room:
        # nameRoom="".join(room[counter][0].split(" "))
        nameRoom=room[counter][0]
        joinedRooms.append(nameRoom)
        try:
            capacity= room[counter][1]
        except:
            capacity=0
        try:
            features= room[counter][2]
        except:
            features= 0
        counter+=1
        rooms[nameRoom]=[capacity,features]
    # print(rooms)
    return rooms

analyzeRooms()
analyzeCourseOffering()
