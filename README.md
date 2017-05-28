# NMEAtoGPX

Convert NMEA sentences to a GPX file for use in Google Earth.

This code was written in support of a GPS logger I built using an Arduino, a data logging shield that writes to a SD card and a USB host shield for the GSP receiver.

Plug in a GPS receiver and it immediately starts spitting out data, lots of it.  Every piece of information is in a NMEA sentence.  Each sentence reveals the status of the GPS such as how many satellites are in view, current date and time or the current geographic coordinates.

After carrying the logger while walking, biking, boating or skiing I would have a SD card loaded with data telling the tale of where I traveled.  If the data is formatted as a GPX file Google Earth can show it on 3D imagery of the earth.  A “flyover” can be started at the push of a button, plying back the recorded route.

Since my receiver uses a SiRFstarIII chipset I called the program sirf2earth.  It should work with data from any reciever, though, since it only pays attention to standard NMEA sentences, not any manufacturer specific propietary sentences.

The image below is a screen grab of Google Earth with blue lines displaying data from a GPS logger recording.  The files corresponing to this image are in the samples folder, take a look at the TXT file to see what the raw GPS data looks like and download the GPX file and open it in Google Earth to get the full experience.

![gps](https://cloud.githubusercontent.com/assets/318132/26525797/bdbd986c-4330-11e7-8a44-f430d8ed47f6.jpg)
