#
# sirf2earth
#

# Convert text file with NMEA messages to a GPX file for use in Google Earch
# Tested with reciever that uses a SiRFstarIII chipset.
#
# command line:  python3 sirf2earth.py
# 
# The program will prompt for an input file and let you specify an output file name.
# Open the file in Google Earth.

import time
import datetime
import sys
import os
import inspect

from tkinter import *
from tkinter import messagebox
import tkinter.filedialog as tk_FileDialog


class GPXMaker:
    
    # constructor
    def __init__(self):
        
        # instance vars for xml elements
        self.currentDateStr = ' '        # date
        self.currentEleStr = ''          # elevation
        self.currentLatLonStr = ""       # latitude, longitude
        self.currentfixModeStr = ''      # 2D or 3D
        self.currentCourseStr = ''       # course
        self.currentSpeedStr = ''        # speed
        self.currentSatStr = ''          # sat used
        self.currentHdopStr = ''         # hdop
        self.currentVdopStr = ''         # vdop
        self.currentPdopStr = ''         # pdop
 
        # record level determines what data we will write
        #
        # 0 - > none
        # 1 -> Lat, Lon, Ele, Time, Fix, Sat, Hdop
        # 2 -> Lat, Lon, Ele, Time, Fix, Sat, Hdop, Vdop, Pdop
        # 3 -> Lat, Lon, Ele, Time, Course, Speed, Fix, Sat, Hdop, Vdop, Pdop
        #       
        self.currentRecordLevel = 0      # 0 - 3
        
        self.trackpointCount = 0;        # count of trackpoints written
     
    
    # passesChecksum
    #
    # Return true if passed sentence passes checksum or has no checksum
    #
    def passesChecksum(self,NMEAsentence):
        
        retVal = 1;
        
        # convert list to string
        line = ",".join(NMEAsentence)
        
        # find postion of *
        cPos = line.find('*')
        
        # if there is a checksum
        if( cPos > 0 ):
        
            # init checksum
            checkSumCalculated = 0
       
            # for each char in line
            for i in range(1, cPos):
                        
               # contribute to checksum calculation with XOR
               checkSumCalculated ^= ord(line[i])
                
            # read checksum from sentence
            checkSumRead = line[cPos+1:len(line)]
                               
            # return true if calculated chacksum matches checksum read from sentence    
            retVal = checkSumCalculated == int(checkSumRead,16)
        
        return(retVal)

            
    # latlonStr
    #
    # format <trkpt> tag begin with lattitude and longitude passed in dictionary
    #  dictionary must also contain North/South and East/West indicators
    #
    def latlonStr(self,pos):
        
            # multiplier for latitude and longitude
            if( pos['nsIndicator'] == 'S' ):
                latMult = -1
            else:
                latMult = 1
                
            if( pos['ewInidcator'] == 'W' ):
                lonMult = -1
            else:
                lonMult = 1
                
            # convert from Minute, Decimal to Degree Decimal dd(d)mm.mmmm -> dd(d).(mm.mmmm/60)
            dLatitude = (int(pos['mLatitude'][0:2])+float(pos['mLatitude'][2:])/60.0)* latMult
            dLongitide = (int(pos['mLongitude'][0:3])+float(pos['mLongitude'][3:])/60.0) * lonMult
        
            # format <trkpt>
            self.currentLatLonStr = "<trkpt lat=\"{0:-.9f}\" lon=\"{1:-.9f}\">".format(dLatitude,dLongitide)

    
    # tdStr
    #
    # format <time> tag with date and time strings from passed dictionary
    #
    def tdStr(self,timeDate):
     
             # pull date and time from dictionary
            theDate = time.strptime(timeDate['dateStr'],"%d%m%y")
            theTime = datetime.datetime.strptime(timeDate['timeStr'],"%H%M%S.%f")
            
            # format <time>
            retStr = "  <time>{0}-{1:02}-{2:02}T{3:02}:{4:02}:{5:02}.{6}Z</time>".format(theDate.tm_year,theDate.tm_mon,theDate.tm_mday,
                                                                          theTime.hour,theTime.minute,theTime.second,theTime.microsecond/1000)
            
            # remember this date
            self.currentDateStr = retStr
    
    # writeOut
    #
    # Write to output file
    def writeOut(self,str):
        
        self.fOut.write(str)
        
    # writeElement
    #
    # Write passed element if not blank
    #
    def writeElement(self,eStr):
        
        # skip blanks
        if( eStr != ''):
            self.writeOut(eStr)
    
    # writeTrackpoint
    #
    # GPS data has been read, write trackpoint info to GPX file
    #
    def writeTrackpoint(self):        
        
        # if no trackpoints written yet
        if( self.trackpointCount == 0 ):
            # start tags
            self.writeOut('<trk>')
            self.writeOut('<trkseg>')
            
        self.writeElement(self.currentLatLonStr)          # lattitude, longitude
        self.writeElement(self.currentEleStr)             # elevation
        self.writeElement(self.currentDateStr)            # date, time
            
        if( self.currentRecordLevel == 3 ):
            self.writeElement(self.currentCourseStr)      # course         
            self.writeElement(self.currentSpeedStr)       # speed
                
        self.writeElement(self.currentfixModeStr)         # fix (2d or 3d)
        self.writeElement(self.currentSatStr)             # satellite used
        self.writeElement(self.currentHdopStr)            # Horizontal
        
        if( (self.currentRecordLevel == 2) or (self.currentRecordLevel == 3) ):
                       
           self.writeElement(self.currentVdopStr)         # Tertical
           self.writeElement(self.currentPdopStr)         # Position
        
        
        # trackpoint end 
        self.writeOut('</trkpt>')
        
        # increment count
        self.trackpointCount = self.trackpointCount + 1
        
        # reset record level
        self.currentRecordLevel = 0
            
    
    # parseGPRMC
    #
    # Parse a GPRMC record
    #
    def parseGPRMC(self,NMEAsentence):


        # if checksum and data are both valid
        if( (self.passesChecksum(NMEAsentence)) and (NMEAsentence[2] == 'A') ):
    
            # build latitude and longitude string
            pos = {'mLatitude':NMEAsentence[3],'nsIndicator':NMEAsentence[4],'ewInidcator':NMEAsentence[6],'mLongitude':NMEAsentence[5]}
            self.latlonStr(pos)
            
            # build date and time string
            timeDate = {'dateStr':NMEAsentence[9],'timeStr':NMEAsentence[1]}
            self.tdStr(timeDate)
            
            # format <course>
            self.currentCourseStr = "  <course>{0:f}/</course>".format(float(NMEAsentence[8]))
             
            # format <speed>
            self.currentSpeedStr = "  <speed>{0:f}</speed>".format(float(NMEAsentence[7]) * 0.514444444)       
            
            # indicate full record
            self.currentRecordLevel = 3
            
            # print record
            self.writeTrackpoint()
            
    # parseGPGSA
    #
    # Parse GPGSA record
    #
    def parseGPGSA(self,NMEAsentence):
                            
        # if checksum and data are both valid  
        if( (self.passesChecksum(NMEAsentence)) and (NMEAsentence[2] != '1') ):
        
            # format <fix>
            if( NMEAsentence[2] == '2'):
                self.currentfixModeStr = '  <fix>2d</fix>'
            elif( NMEAsentence[2] == '3'):
                self.currentfixModeStr = '  <fix>3d</fix>'
                
           # format <pdop>
            self.currentPdopStr = "  <pdop>{0:f}</pdop>".format(float(NMEAsentence[15]))
    
           # format <hdop>
            self.currentHdopStr = "  <hdop>{0:f}</hdop>".format(float(NMEAsentence[16]))
                    
           # format <vdop>
            self.currentVdopStr = "  <vdop>{0:f}</vdop>".format(float(NMEAsentence[17].split('*')[0]))
            
            # indicate that we can write partial record at eof
            if( self.currentDateStr != ' ' ):
                self.currentRecordLevel = 2
    
    # parseGPGGA
    #
    # Parse a GPGSA record
    #
    def parseGPGGA(self,NMEAsentence):
                     
        #print("*********** in parseGPGGA ****************") #debug
                       
        # if checksum and data are both valid
        if( (self.passesChecksum(NMEAsentence)) and (NMEAsentence[6] != '0') ):
    
            # print latitude and longitude
            pos = {'mLatitude':NMEAsentence[2],'nsIndicator':NMEAsentence[3],'ewInidcator':NMEAsentence[5],'mLongitude':NMEAsentence[4]}
            latlonStr(pos)
              
            # format <ele>
            self.currentEleStr = "  <ele>{0:f}</ele>".format(float(NMEAsentence[9]))
                     
            # format <sat>
            self.currentSatStr = "  <sat>{0}</sat>".format(int(NMEAsentence[7]))
            
            # format <hdop>
            self.currentHdopStr = "  <hdop>{0:f}</hdop>".format(float(NMEAsentence[8]))
                 
            # indicate that we can write partial record at eof
            if( self.currentDateStr != ' ' ):
                self.currentRecordLevel = 1
    
    # gpxHeader
    #
    # Write file header
    #
    def gpxHeader(self):
        
        # gpx header
        self.writeOut('<?xml version=\"1.0\"?>')
        
        self.writeOut('<gpx xmlns=\"http://www.topografix.com/GPX/1/0" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd\">')
                            
    def convertNMEA(self,inFileName, outFileName):
                           
        # open file with NMEA sentences
        try:
            fIn = open(inFileName, 'r', errors='ignore')

        except:
             # show message and die
            print('cannot open {0}'.format(sys.argv[1]))
            sys.exit(1)
            
        # create gpx file
        try:
            self.fOut = open(outFileName,'w')
                      
        except:
             # show message and die
            print('cannot open {0}'.format(outFileName))
            sys.exit(1)
    
       
        # write header
        self.gpxHeader()
        
        # read each line in file
        for line in fIn:
                                     
            # build name of parsing method - parse + first element of string without $, e.g. parseGPGGA
            parseMethod = 'parse' + line.partition(',')[0].strip('$')
            #parseArgs = (str(line.split(',')))
            parseArgs = line.split(',')
            
            # call parsing function if it exists
            try:

                exec(getattr(self, parseMethod)(parseArgs))
            
            except:
                pass
                
        # if we have a partial record to write
        if( self.currentRecordLevel > 0):
            self.writeTrackpoint()
    
        # end tags
        self.writeOut("</trkseg>")
        self.writeOut("</trk>")
        self.writeOut("</gpx>")
        
        # close files
        self.fOut.close()
        fIn.close()
        
        return(self.trackpointCount)
    
class GetFileNames:
    
    def getInFileName(self):

        # show file dialog
        fileName = tk_FileDialog.askopenfilename(title='Choose a file')
        
        # if we got a filename
        if( fileName != ""):
            
            # record file name and show on screen
            self.inFileName = fileName
            self.inFileDisplay["state"] = NORMAL
            self.inFileDisplay.delete(0, END)
            self.inFileDisplay.insert(0, self.inFileName)
            self.inFileDisplay["state"] = DISABLED
            
            # set default for output file name
            
            # break out file name and add gpx extension
            inFilePathName = os.path.split(self.inFileName)
            inFileName = os.path.splitext(inFilePathName[1])[0]
 
            # build output file name with path
            self.outFileName = '{0}/{1}.gpx'.format(inFilePathName[0],inFileName)
            
            # show it on screen and leave it editable
            self.outFileDisplay["state"] = NORMAL
            self.outFileDisplay.delete(0, END)
            self.outFileDisplay.insert(0, self.outFileName)
            
            # enable GO button
            self.goButton["state"] = NORMAL
    
    # reset()
    #
    # Call after converting a file
    def reset(self):
        
            # reset file names to blank
            self.inFileName = ""
            self.inFileDisplay["state"] = NORMAL
            self.inFileDisplay.delete(0, END)
            self.inFileDisplay["state"] = DISABLED
            self.inFileDisplay.focus_set()
            
            self.outFileName = ""
            self.outFileDisplay["state"] = NORMAL
            self.outFileDisplay.delete(0, END)
            self.outFileDisplay["state"] = DISABLED

            # disable GO button 
            self.goButton["state"] = DISABLED
            
            # set focus to browse button
            self.inBrowseButton.focus_set()
            
    # GO
    #
    # The GO button was clicked
    #
    def go(self):
        
        # record output file name in case default was edited
        self.outFileName = self.outFileDisplay.get()
   
        # convert file
        gpx = GPXMaker()
        trackPointCnt = gpx.convertNMEA(self.inFileName, self.outFileName)
        
        # show how many trackpoints were converted
        msgStr = str("{0} trackpoints converted.".format(trackPointCnt))
        messagebox.showinfo("Conversion Complete", msgStr)
        
        # reset this object
        self.reset()
        
        del gpx


    def __init__(self):
    
        self.inFileName = ""
        self.outFileName = ""

        root = Tk()
        
        root.title("Sirf2Earth GPX Formatter")
        root["padx"] = 40
        root["pady"] = 20
        
        # size and postion window
        root.geometry("600x150+100-300")
            
        #Create a Label in textFrame
        inFileLabel = Label(root, text="NMEA file").grid(row=0, sticky=W)
    
        # Create an Entry Widget in textFrame
        self.inFileDisplay = Entry(root, state=DISABLED)
        self.inFileDisplay["width"] = 50
        self.inFileDisplay.grid(row=0, column=1)
    
        # Browse button for input file       
        self.inBrowseButton = Button(root, text="Browse", command=self.getInFileName)
        self.inBrowseButton.grid(row=0, column=2, sticky=W)

        #Create a Label in textFrame
        outFileLabel = Label(root, text="GPX    file").grid(row=1, sticky=W)
    
        # Create an Entry Widget in textFrame
        self.outFileDisplay = Entry(root, state=DISABLED)
        self.outFileDisplay["width"] = 50
        self.outFileDisplay.grid(row=1, column=1)

        # Go button       
        self.goButton = Button(root, text="GO", command=self.go, state=DISABLED)
        self.goButton.grid(row=2, column=2, sticky=W)
                      
        root.mainloop()
 
 # create getfilenames object       
g = GetFileNames()