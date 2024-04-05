#!/usr/bin/env python3

import json, os, re, sys
from datetime import date, timedelta
from pysensorpush import PySensorPush
from pysensorpush.const import (
    QUERY_SAMPLES_ENDPOINT,
)

def readJSONFile (fileName, defaultDictionary = None, directoryName = ""):
    try:
        file = open(os.path.join(directoryName, fileName), 'r')
    except IOError as error:
        if defaultDictionary is None:
            print (error)
            sys.exit()
        else:
            writeJSONFile(fileName, defaultDictionary, directoryName)
            return defaultDictionary

    try:
        dictionary = json.load(file)
    except json.decoder.JSONDecodeError as error:
        print (f"Couldn't decode JSON file: '{fileName}'; error: {error.msg}.")
        sys.exit()
    return dictionary

def writeJSONFile (fileName, dictionary, directoryName = ""):
    try:
        theFile = open(os.path.join(directoryName, fileName), 'w')
        json.dump(dictionary, theFile, indent=2)
    except IOError as theError:
        print(theError)
        sys.exit()

def createDegreesForDay (fileName, dateAsDate):
    timeZoneOffset = settings['timeZoneOffset']
    startTime = dateAsDate.strftime('%Y-%m-%dT%H:%M:%S') + timeZoneOffset # Pacific Time Zone is -8 hours from UTC
    endDateAsDate = dateAsDate + timedelta (days=1)
    stopTime = endDateAsDate.strftime('%Y-%m-%dT%H:%M:%S') + timeZoneOffset
    params = {
        'limit': 2000, # we typically get one sample a second so this should be enough
        'startTime': startTime,
        'stopTime': stopTime,
        'sensors': [sensorId]
    }
    samples = sensorPush.query(QUERY_SAMPLES_ENDPOINT, extra_params=params)
    truncated = samples['truncated']
    status = samples['status']
    if (samples['truncated'] != False or samples['status'] != 'OK'):
        print(f"An unexpected error occurred reading the data. truncated:'{truncated}'; status:'{status}'.")
        sys.exit()

    temperatureData = samples['sensors'].get(sensorId, {})
    for sample in temperatureData:
        del sample['gateways']
    temperatureData = sorted(temperatureData, key=lambda x: x['observed'])
    writeJSONFile(fileName, temperatureData, dataDirectoryName)
    print (f'Read {len(temperatureData)} temperature samples from {dateAsDate}')
    return (temperatureData)

def calculateDegreeDaysforDay (temperatureData):
    totalDegrees = 0
    numberOfSamples = len(temperatureData)
    if numberOfSamples != 0:
        lowerThreshold = float (settings['lowerThreshold'])
        upperThreshold = float (settings['upperThreshold'])
        for sample in temperatureData:
            temperature = float (sample['temperature'])
            if temperature > upperThreshold:
                temperature = upperThreshold
            temperature -= lowerThreshold
            if temperature < 0:
                temperature = 0
            totalDegrees += temperature
        totalDegrees = totalDegrees / numberOfSamples
    return totalDegrees

settings = readJSONFile ('Settings.json')
dateAsDate = date.fromisoformat(settings['biofixDate'])

if dateAsDate < date.today():
    sensorPush = PySensorPush(settings['userName'], settings['password'])
    if not sensorPush.is_connected:
        print ("Couldn't login to sensorPush. Check your login and password in the settings file.")
        sys.exit()

    degreeDays = readJSONFile('DegreeDays.json', defaultDictionary={})
    totalDegreeDays = 0
    sensorId = None
    sensors = sensorPush.sensors
    sensorName = settings.get('sensorName', None)

    #Find the sensorId
    if sensorName is None:
        if len(sensors) == 1:
            sensorId = list(sensors.keys())[0]
            sensorName = sensors[sensorId]['name']
    else:
        for key, value in sensors.items():
            if value['name'] == sensorName:
                sensorId = key
                break

    if sensorId is None:
        print('You need to specify the name of the sensor you want to use as "sensorName" in the settings file.')
        if len(sensors) > 0:
            names = []
            for key, value in sensors.items():
                names.append(value['name'])
            names = ', '.join(f'"{name}"' for name in names)
            print(f'available names are: {names}.')
        sys.exit()

    if sensorName == "":
        sensorName = 'data'

    #Convert sensorName into valid directory name and create it if it doesn't exist
    illegalDirectoryCharacters = r'[^A-Za-z0-9()_ -]'
    dataDirectoryName = re.sub(illegalDirectoryCharacters, '', sensorName)
    if dataDirectoryName == "":
        dataDirectoryName = 'data'
    dataDirectoryName = dataDirectoryName[:255] #limit to 255 characters
    if (not os.path.exists(dataDirectoryName)):
        os.makedirs(dataDirectoryName)
        degreeDays = {} #existing data is invalid so delete it

    # Delete all data before the biofixDate because we no longer need it
    biofixDateAsString = dateAsDate.isoformat()
    startingLength = len(degreeDays)
    degreeDays = {key: value for key, value in degreeDays.items() if key >= biofixDateAsString}
    degreeDaysModified = len(degreeDays) != startingLength

    try:
        files = os.listdir(dataDirectoryName)
    except FileNotFoundError:
        pass
    else:
        for fileName in files:
            if fileName < biofixDateAsString:
                os.remove(os.path.join(dataDirectoryName, fileName))


    while dateAsDate < date.today():
        dateAsString = dateAsDate.isoformat()
        if dateAsString not in degreeDays:
            fileName = dateAsString + '.json'
            try:
                file = open(os.path.join(dataDirectoryName, fileName), 'r')
            except IOError as error:
                temperatureData = createDegreesForDay (fileName, dateAsDate)
            else:
                try:
                    temperatureData = json.load(file)
                except json.decoder.JSONDecodeError as error:
                    print(f"Couldn't decode JSON file: '{fileName}'; error: {error.msg}.")
                    sys.exit()

            degreeDays[dateAsString] = calculateDegreeDaysforDay (temperatureData)
            degreeDaysModified = True

        totalDegreeDays += degreeDays[dateAsString]
        dateAsDate += timedelta (days=1)

    if settings.get('totalDegreeDays', None) != totalDegreeDays:
        settings['totalDegreeDays'] = totalDegreeDays
        settings = dict(sorted(settings.items())) #sort by keys
        writeJSONFile('Settings.json', settings)

    if degreeDaysModified:
        degreeDays = dict(sorted(degreeDays.items())) #sort by keys
        writeJSONFile('DegreeDays.json', degreeDays)

    print (f'{"{:.2f}".format(totalDegreeDays)} total degree days as of {dateAsDate - timedelta(days=1)} for a biofix date of {biofixDateAsString}')


