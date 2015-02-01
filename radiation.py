#!/usr/bin/env python3
import os
import sys
import serial
import time
import re
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates

DEFAULT_TTY = '/dev/ttyUSB0'
BAUD = 9600
DATA_FILE = '/tmp/data'
PLOTFILE = '/tmp/plot'

class Radiation:
    def __init__(self,argv=sys.argv):
        try:
            self.tty = argv[1]
        except IndexError:
            self.tty = DEFAULT_TTY
        self.baud = BAUD
        self.ser = serial.Serial(self.tty,self.baud)
        self.data = []
        if os.path.exists(DATA_FILE):
            self.fd = open(DATA_FILE, "r+", buffering=1)
            for line in self.fd:
                d = tuple([ float(l) for l in line.split(',') ])
                self.data.append(d)
        else:
            self.fd = open(DATA_FILE, "w", buffering=1)
        # read data from file
        for d in self.data:
            print(d)
        while True:
            if len(self.data) > 0:
                # plot 
                self.plot(self.data)
            # get new data
            d = self.read_val()
            self.fd.write("{},{},{},{}\n".format(*d))
            self.data.append(d)

    """ 
        blocking read operation from serial
        @return: (time,CPM,uSv/h,V)
    """
    def read_val(self):
        valid = False
        while not valid:
            l = self.ser.readline()
            try:
                l = l.decode('utf-8')
                valid = True
            except UnicodeDecodeError:
                print('Failed decoding: {}'.format(l))
        data = re.findall("\s*([.0-9]+)V?,",l)
        data = [ float(d) for d in data ]
        data.insert(0 , time.time()) 
        return tuple(data)
            

    def plot(self, data):
        # generate data
        t = [ datetime.datetime.fromtimestamp(d[0]) for d in data ]
        c_m = [ d[1] for d in data ]
        uSv_h = [ d[2] for d in data ]
        v = [ d[3] for d in data ]
        # plot
        fig, (ax1,ax2) = plt.subplots(nrows = 2,sharex = True)
        ax1t = ax1.twinx()
        ax1.set_ylabel('c/m', color='b')
        ax1t.set_ylabel('uSv/h', color='r')
        ax1.grid(True)
        ax2.set_ylabel('V',color='g')
        ax2.grid(True)
        # x-axis
        ax1.xaxis_date()
        ax2.xaxis_date()
        ax2.xaxis.set_major_locator(dates.AutoDateLocator(maxticks=8))
        ax2.xaxis.set_major_formatter(dates.DateFormatter('%Y %m %d %H:%M:%S'))
        ax2.set_xlabel('datetime')
        # Make the y-axis label and tick labels match the line color.
        ax1.plot(t, c_m, 'bo')
        for tl in ax1.get_yticklabels():
            tl.set_color('b')
        ax1t.plot(t, uSv_h, 'r--')
        for tl in ax1t.get_yticklabels():
            tl.set_color('r')
        # voltage
        ax2.plot(t, v, 'g-o')
        # Make the y-axis label and tick labels match the line color.
        for tl in ax2.get_yticklabels():
            tl.set_color('g')
        # figure setup
        fig.set_size_inches(16,8)
        fig.savefig(PLOTFILE)
        #plt.show()

# Init a tester
def main(argv=sys.argv):
    radiation = Radiation(argv)

#run main function 
__name__="__main__" 
main()
