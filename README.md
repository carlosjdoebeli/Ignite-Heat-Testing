# Ignite-Heat-Testing

Script to collect and graph heating data from an Ignite instrument.

## Instructions of Use
An Adafruit Metro M4 must be connected to your computer. The files in the "Metro M4" subdirectory should be copied onto the Metro M4.

Run <b>temp_central_monitor.py</b> from the command line. There should only be one COM Port that registers as a "USB Serial Device", 
otherwise the code will not run. If you have more than one USB Serial Device connected to your computer, either remove the other USB 
Serial Device connections, or alter the code to input the COM Port and baudrate manually. 

Connect the temperature sensors that you are using to the appropriate places on the microcontroller's attached circuit board. Ensure that the switch connected to the microcontroller is OFF to start the test. 

Input a test description for the heating test that you are running, such as <b>"Inst6 Syringe Heating_75C Setpoint"</b>.

Input labels for the temperature sensors that you are using, and ignore the labels for temperature sensors you are not using on that run, 
or change the code to fit the right number of sensors. Example labels could be <b>"1mL Syringe"</b> and <b>"3mL Syringe"</b>.

Turn on the switch when you want to start taking data. Turn the switch off when you wish to end the test. 

The script will create data files for each sensor, as well as one graph overlaying the data from the sensors used onto one graph. From the 
root directory, the data files will be located in the folder:

<b>rootdir/Data/test_desc/sensor_label.txt</b>

The graph will be located in the folder:

<b>rootdir/Graphs/test_desc.png</b>

Where rootdir is the directory the script is being run from, test_desc is the inputted test description, and sensor_label refers to the 
labels assigned to each temperature sensor. 

The data files will have Force or Current appended to the file name, and the created files will have a timestamp in the file name. 

There are several commented-out print statements. For debugging, these may be useful when uncommented. 
