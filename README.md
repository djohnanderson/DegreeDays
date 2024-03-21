# DegreeDays for SensorPush
DegreeDays is a Python program  to calculate degree days for insect models used in pest management, such as determining optimal timing for spraying apple orchards to combat codling moths.

These models operate on the principle that an insect's development is closely tied to the ambient temperature. Typically, an insect trap is deployed to mark the biofix date, the date you catch the first adult insect signals the onset of egg-laying. Subsequently, temperature accumulation is monitored over time to compute total degree days. In the case of codling moths, hatching can be anticipated when approximately 250 degree days have accumulated post-egg laying, signaling the ideal time for intervention.

This program uses temperature data from a SensorPush gateway and sensors. For information about SensorPush hardware, visit SensorPush.com.

DegreeDays computes total degree days by summing the daily degree day values post-biofix date. Each degree day is derived from temperature samples taken at regular intervals throughout the day, typically every minute. Daily values are calculated by measuring the temperature variance between a predefined high and low threshold temperature for each sample and then averaging these variances across all samples taken that day. The standard thresholds used for codling moths are 50 and 88 degrees Fahrenheit, the range of temperature that insect development occurs.
## Installation
The program uses a Python package called pysensorpush to connect to the SensorPush gateway, which stores historical temperature data. The pysensorpush package can be accessed on the [Github SensorPush API](https://github.com/rsnodgrass/pysensorpush) page.

To install pysensorpush, follow the instructions provided on the Github pysensorpush project
```
pip3 install pysensorpush
```
Next create a directory and download the DegreeDays code into it. The code package includes two essential files: DegreeDays.py, the main program file, and Settings.json, which contains the configuration settings required for the program to operate."
## Configure Settings
The settings file is in JSON format, containing name-value pairs. For instance, 'biofixDate' represents the name with a corresponding date value of '2024-03-05' formated as YYYY-MM-DD for the date 5 March 2024:
```
{  
  "biofixDate": "2024-03-05",  
  "lowerThreshold": "50",  
  "password": "Password",  
  "sensorName": "Sensor Name",  
  "timeZoneOffset": "-0800",  
  "totalDegreeDays": 99.35848544440371,  
  "upperThreshold": "88",  
  "userName": "UserName"  
}
```
Update the values enclosed in quotes to match your specific requirements.

-   'UserName' and 'Password' are credentials for accessing the SensorPush database. Further details can be found on the pysensorpush Github page.
-   'lowerThreshold' and 'upperThreshold' define the temperature thresholds for degree day calculations described above.
-   'timeZoneOffset' indicates your time zone deviation from UTC. Common US time zone offsets include:
    
    -   Pacific: "-0800"
    -   Mountain: "-0700"
    -   Central: "-0600"
    -   Eastern: "-0600"
    

The program disregards daylight saving time adjustments.

-   'sensorName' should reflect the specific sensor name if multiple sensors are in use. If you have multiple sensors and don't know their names, run the program with any sensor name and it will list all available names.
-   'totalDegreeDays' represents the cumulative degree days calculated during the last program execution.

After configuring the parameters, you can execute the program in a shell, Terminal window, or DOS prompt based on your operating system. Begin by navigating to the directory containing DegreeDays.py. For Mac and Linux systems, input the following commands in the Terminal window or shell:
```
cd directoryContainingDegreeDays
./DegreeDays.py
```
Upon execution, the program retrieves all temperature data from the biofix date up to and including yesterday, the last complete day of data. Each day's data is stored in JSON files within a directory named after your sensor. Additionally, a JSON file named DegreeDays.json is generated, containing the degree days for each day. Upon completion, the total degree days will be displayed in the shell.

Subsequent program runs will automatically download any new temperature data, calculate additional degree days if necessary, and present the updated total.

If you delete any temperature data files in the sensor directory or any degree day entries in DegreeDays.json, the program will recalculate this information during its next run.
