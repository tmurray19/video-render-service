import json


def getprojectid(jsonfile):
    retproject = 0
    try:
        # Read The JSON File

        with open(jsonfile) as json_file:
            templatedets = json.load(json_file)
            retproject = str(templatedets['projectid'])

    except Exception as e:
        retproject = str(e)

    return retproject

def getprojectstatus(jsonfile):
    retproject = 0
    try:
        # Read The JSON File

        with open(jsonfile) as json_file:
            templatedets = json.load(json_file)
            retproject = str(templatedets['status'])

    except Exception as e:
        retproject = str(e)

    return retproject


def fontsize(sizetext):
    if not sizetext.isdigit():
        fsize = 20
        if sizetext == "Small":
            fsize = "40"
        elif sizetext == "Medium":
            fsize = "60"
        elif sizetext == "Large":
            fsize = "100"
        elif sizetext == "X-Large":
            fsize = "200"
        elif sizetext == "XX-Large":
            fsize = "300"
    else:
        fsize = sizetext
    return fsize


