
# OBD Python - Test program 
# Julio Ribeiro  26/11/2014

from bluetooth import *
import os
import sys
import time
import variables
import reporter
import bluetooth

### ----------------------------------- CLASS OF OBD COMMUNICATION ------------------------------------
class OBDCom():

	retryLimit = 0
		
	def __init__(self):
		
		# Bluetooth OBD Server adapter parameters
		host = '00:0D:18:00:00:01'
		#host = '18:1E:B0:0D:C0:6B' 
		port = 1
		self.wait = 0.2
		
		try:
			self.bt = BluetoothSocket(RFCOMM)
			self.bt.connect((host,port))
			print('Bluetooth connected')
			OBDCom.retryLimit =0
			self.log = reporter.Report()
		
		except:
			print('Failed to connecto to bluetooth')
			self.__retryConnect()
			
	def __retryConnect(self):
		if OBDCom.retryLimit <= 3:
			print('Retrying',OBDCom.retryLimit)
			OBDCom.retryLimit +=1
			self.__init__()
		print('Bluetooth connection not possible')
		OBDCom.retryLimit =0
		quit()
		
			
### FUNCTION: Generic send command to OBD		
	def sendCmd(self, cmd, timeout):
		try:
			self.bt.send(cmd)
			time.sleep(timeout)
			data = self.bt.recv(512)
			data = data.split()
			return data
		except:
			print('Error issuing command',cmd)
			self.log.error('CRITICAL','Issue Command error',cmd)
			return False


### FUNCTION: Get vehicle ID
### Get the vehicle chassi number
### It is a string
	def getID(self):
		try:
			data = self.sendCmd('0902\r',2)				
			bytes = int(data[1],16)										
			first = data.index('0:')									# fix position index of start reading 1st line
			vin = ''
			for i in range(bytes-1):									# scan from byte 0 up to 19
				try:
					vin += chr( int(data[first+4+i],16) )				# the first 3 bytes after '0:' is a metadata 
				except:
					i+=1												#  non-hexa symbols (ex: '1:'),ignore it
					pass
			return vin
		except:
			self.log.error('MAJOR','Vehicle ID Error','getID() function failure')

		


### FUNCTION: Setup ELM327
### Set configuration of ELM327
### Initialize basic AT commands
	def setupELM(self):
		try:
			results = []
			for at in ['ATI\r','ATE1\r', 'ATH0\r','ATS1\r', 'ATTP0\r','ATDPN\r','0100\r']:   # init AT MUST HAVE 7 valids AT 
				data = self.sendCmd(at,0.5)    
				results.append(data[1])									
				#print(at[:5],':',data[1])
		except:
			self.log.error('CRITICAL','Setup ELM327 failure',len(results))
		return results




### FUNCTION: Start session
### Set a start point
### Writes initial state of a sample collection
	def startSession(self, targetFlag=False, targetPid=['04','0C','0D'] ):
		print('Initialization sequence...')
		try:
			results = {}
			results['ID'] = str(hex(int(time.time()))).upper()		#0=Session ID
			results['ELM'] = self.setupELM()						#1=ELM Setup (list)
			results['VIN'] = self.getID()      						#2=VIN 
			results['Login']= time.ctime()             				#3=Datetime
			results['PID']= self.getListPids()	 					#4=Pids (list)
			results['KM']='Not Supported'
			if '31'in results['PID']:                  				#[5]=Km if supported
				data=(self.sendCmd('0131\r',0.3))	
				km=int(data[3],16)*256 + int(data[4],16)
				results['KM']= km
			results['Target_Flag'] = targetFlag								 #6=Flag targetpid
			results['Target_PID'] = self.__mapPids(results['PID'],targetPid) #7=Target Pids (list)
			return results												
		except:
			print('Session Initialization Error')
			self.log.error('CRITICAL','Session Initialization Error','startSession() function')
			return False



### FUNCTION: Get all supported PIDs
### Get a list of supported PIDs
### Return a full list or only target PIDs (defined in Config.cfg) or a default mask
	def getListPids(self, map=False, mask=['04','0C','0D']):
		pids = []
		OBD_PID_LIST = ['0100\r', '0120\r', '0140\r', '0160\r','0180\r']
		for cmd in OBD_PID_LIST:
			binario =''	
			try:
				self.bt.send(cmd)
				time.sleep(self.wait)
				data = self.bt.recv(128).split()[3:7]
				for i in range(len(data)):
					binario +=bin(int(data[i],16))[2:].zfill(8)	 
				for b in range(len(binario)):
					if int(binario[b]) == 1:
						pid = hex( int(b+1)+ int(cmd[2:4],16) )[2:].zfill(2).upper()
						pids.append(pid)
			except:
				print('An error has occurred gathering list of supported PIDs')
				self.log.error('CRITICAL','Error getting supported PIDs','getListPids() function failure.')
				
		print('There are a total of',len(pids),'supported PIDs:')
		for i in pids:
			print('PID:',i,'\t',variables.dicpid['01'][3][i])
		if map == True:
			mapedPids = self.__mapPids(pids,mask)
			print(' *** Mapped PIDs enabled ***')
			for i in mapedPids:
				print('PID:',i,'\t',variables.dicpid['01'][3][i])
			return mapedPids
		return pids



### FUNCTION: Maps a obtained PID list to a desirable PID list using a pre-defined filter (target)
### Private Function
### Return a resultant list of PID
	def __mapPids(self,pids,target):
		resultPids = []
		for t in range(len(target)):
			for p in range(len(pids)):
				if target[t]==pids[p]:
				 	resultPids.append(pids[p])
		return resultPids


### FUNCTION: Get PID readings from OBD-II
### Receive individual PID request or list of 4 PIDs (TO BE IMPLEMENTED)
### Return a dictionary (key-value pairs)
	def getOBD(self, multiple=False,cmd=''):
		dicpid = variables.dicpid
		values={}
		if (multiple==False and type(cmd) != list):	
			data = self.sendCmd(cmd,self.wait)
			mode = data[0][0:2]							# can be changed to '01' once mode is a constant
			pid = data[0][2:4] 							# can be change to 'id' once pid is a variable already known
			bytesToRead = dicpid[mode][1][pid]
			bytes = data[3:(3+bytesToRead)]
			label,result = self.getValue(mode,pid,bytes)
			values.append('%.4f' % result)
			print(pid,'%.4f' % result)



### FUNCTION: Extract, convert and return decimal PID value
### Convert value according PID formula
### Return decimal value
	def getValue(self,mode,pid,bytes):
		dicpid = variables.dicpid
		try:
			if len(bytes)==1:
				A = int(bytes[0],16)
			elif len(bytes)==2:
				A = int(bytes[0],16)
				B = int(bytes[1],16)
			elif len(bytes)==3:
				A = int(bytes[0],16)
				B = int(bytes[1],16)
				C = int(bytes[2],16)
			elif len(bytes)==4:
				A = int(bytes[0],16)
				B = int(bytes[1],16)
				C = int(bytes[2],16)
				D = int(bytes[3],16)
			elif len(bytes)==5:
				A = int(bytes[0],16)
				B = int(bytes[1],16)
				C = int(bytes[2],16)
				D = int(bytes[3],16)
				E = int(bytes[4],16)
			else:
				label = 'Raw data'
				return label, bytes
		except:
			label = 'No data'
			self.log.error('CRITICAL','getValue() function error ', bytes)
			return label,'Error'
		return dicpid[mode][3][pid],eval(dicpid[mode][2][pid])
	

### FUNCTION: Get voltage value
### Read battery voltage through ELM327
### Optionally return True or False for LOW_BAT
	def getVoltage(self, isLow=False, value=13.0, setSleep=False):
		try:
			vbat = self.sendCmd('ATRV\r',0.5)		# return a list like '['ATRV','12.8V','>']
			vbat = float(vbat[1][: (vbat[1].index('V'))])   # get voltage ([1]), but only number
			if isLow==True and vbat <= value:
				print('Power supply under ', value,'(V).')
				self.log.error('MAJOR','ELM 12V power supply below limit ',vbat)
				if setSleep==True:
					self.log.error('MAJOR','ELM entered in sleep mode ',vbat)
					print('Entering in sleep mode right now')
					self.sendCmd('ATLP\r',0.1)
				return True
			return vbat
		except:	
			self.log.error('CRITICAL','getVoltage() function exception ',' Returned False')
			return False


### FUNCTION: Close bluetooth communication
	def close(self):
		print('Closing bluetooth socket...')
		try:
			self.bt.close()
			print('Bluetooth socket are closed!')
		except:
			print('Error closing bluetooth')






### ----------------- Raspberry Server Bluetooth for Android dashboard (TO be implemented!!)----------------------------
class BTServer():

	def __init__(self):
		port = 0
		self.server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
		self.server_sock.bind(("",port))
		self.server_sock.listen(1)
		
	def acceptConnection(self):
		print('Waiting for client connection...')
		self.client_sock,address = self.server_sock.accept()
		print('Accepted connection from ',address)	
		
	def getData(self):
		data = self.client_sock.recv(1024)
		print('received [%s]' % data)
		return data
	def close(self):
		print('Closing bluetooth socket...')
		self.client_sock.close()
		self.server_sock.close()
		print('Bluetooth socket are closed!')
		
