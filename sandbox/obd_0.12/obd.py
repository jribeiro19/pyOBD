#!/usr/bin/env python

# OBD Python - Test program 
# Julio Ribeiro  26/11/2014

from bluetooth import *
import os
import sys
import time
import variables
import reporter
import obdlib

# Generic variables
WAIT = 0.2			# Wait time to read input bluetooth buffer after sending a command
LOW_BAT = 13.0		# Minimum car's battery voltage allowed to run the script


# OBD variables
dicpid = variables.dicpid
targetPids = ['04','0A','0B','0C','0D','10','11','1F','23','43','45','49','4A','4B','59','5A','5E','61','62','63']

# Log file
rep=reporter.Report()

# Initialization sequence
bt = obdlib.OBDCom()
session = bt.startSession(True, targetPids)
if session == False:
	rep.error('CRITICAL','startSession Failed','startSession() function returned False')
	fail_session = 'fail_'+str(hex(int(time.time()))).upper()
else:
	rep.login(session)


# Get PID list to query
if session['Target_Flag']== True:
	pids = session['Target_PID']
else:
	pids = session['PID']



# Setup headers of report OBD2Output.txt according to availables PIDs
lbl = []
for i in pids:
	lbl.append(dicpid['01'][3][i])
lbl.append('Session_ID')
rep.addHeader(lbl)


# Loop through all car PIDs available in "OBD MODE:01"
error = 0			# error count variable
last = 0			# last sample with error
sample = 0			# total samples counter
while 1:		
	sample +=1
	values = []
	try:
		for id in pids:
			cmd = '01'+id+'\r'
			data = bt.sendCmd(cmd,WAIT)
			mode = data[0][0:2]							# can be changed to '01' once mode is a constant
			pid = data[0][2:4] 							# can be change to 'id' once pid is a variable already known
			bytesToRead = dicpid[mode][1][pid]
			bytes = data[3:(3+bytesToRead)]
			label,result = bt.getValue(mode,pid,bytes)
			values.append('%.4f' % result)
			print(pid,'%.4f' % result)
		values.append(session['ID'])
		rep.write(values)

	except:												# error decoding
		print('Error decoding',error)
		rep.error('CRITICAL','obd.py decoding error ',values)
		if sample == (last+1):
			error +=1
			if error >= 5:
				error = 0
				sample = 0
				vbat = bt.getVoltage(False,LOW_BAT, True) # ignition if off and ELM is put in sleep mode ?
				if vbat < LOW_BAT:
					rep.error('CRITICAL','OBD decoding failure and ignition is off ','The system will shutdown')
					rep.close()
					bt.close()
					os.system('sudo poweroff')
					time.sleep(3)
				if vbat > LOW_BAT:
					rep.error('CRITICAL','OBD decoding data with too many errors ','The system will reboot')
					rep.close()
					bt.close()
					os.system('sudo reboot')
					time.sleep(3)
		else:
			error = 0
		last = sample	

	

