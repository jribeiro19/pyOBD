# OBD Python - Test program 
# Julio Ribeiro  26/11/2014

import os
import zipfile
import sys
import time
import variables

class Report():

	def __init__(self,output='OBD2Output.txt', error='OBDError.txt', session='OBDSession.txt', separator = ';'):
		self.o = output
		self.e = error
		self.s = session
		self.separator = separator
		self.dic = {}
		try:
			self.fho = open(self.o, 'a')
			self.fhe = open(self.e, 'a')
			self.fhs = open(self.s, 'a')
		except:
			print('Error: Is not possible to open output files. Check:',self.o,self.e, self.s)
				

	def addHeader(self, headers):
		hdr = 'Sample'+self.separator+'Datetime'+self.separator		
		for i in headers:
			hdr += i+self.separator
		try:
			self.fho.write(hdr+'\n')
		except:
			print('Error writing headers')
			out = str(time.ctime()) + self.separator + ' Error writing headers to the output file. Headers received: '+ str(headers)
			self.fhe.write(out +'\n')
		 
	
	def write(self,data='-'):
		self.data = data
		try:
			value = ''
			for i in range(len(self.data)):
				value += str(self.data[i])+self.separator
			out = str(time.time())+ self.separator + str(time.ctime()) + self.separator + value
			self.fho.write(out +'\n')
		except:
			print('Error writing data')
			self.error('CRITICAL','Error writing data to OBD2Output.txt , data ->',str(self.data))
			
		 
		 
	def login(self,session):
		try:
			if type(session) == dict:
				self.fhs.write('-'*80+str('\n'))
				self.fhs.write('Session Id : '+ str(session['ID'])+'\n')
				self.fhs.write('Login time : '+ str(session['Login']) + '\n')
				self.fhs.write('Initial Km : '+str(session['KM'])+'\n')
				self.fhs.write('Vehicle Id : '+ str(session['VIN'])+'\n')
				self.fhs.write('Protocol   : '+ str(variables.dicproto[session['ELM'][5]])+'\n')
				self.fhs.write('Supported  : '+ str(len(session['PID']))+' PIDs\n')
				for i in session['PID']:
					self.fhs.write('\tPID: ' +str(i) +'\t' +str(variables.dicpid['01'][3][i])+'\n')
				self.fhs.write('Use Target : '+str(session['Target_Flag'])+ '\n')
				for x in session['Target_PID']:
					self.fhs.write('\tPID: ' +str(x) +'\t' +str(variables.dicpid['01'][3][x])+'\n')					
		except:
			print('Failed to login')
			
			
	def appendLogin(self,content):
		try:
			self.fhs.write(content)
		except:
			print('Failed to append login')
			
		
			
	def error(self,type='INFO',description='',info=''):
		message = str(time.ctime())+ ':' + str(type) + ':'+ str(description) +':'+ str(info) + '\n'
		self.fhe.write(message)
					
					
	
	def close(self):
		if not os.path.exists(os.getcwd()+'/logs'):
			os.makedirs(os.getcwd()+'/logs')
			print 'Folder "logs" has been created'
		print('Closing report files....')
		zfile = str(time.gmtime()[2])+ str(time.gmtime()[1])+str(time.gmtime()[0])+'_'+str(time.gmtime()[3])+str(time.gmtime()[4])+str(time.gmtime()[5])+'.zip'
		zobj = zipfile.ZipFile(file = os.getcwd()+'/logs/'+zfile, mode = 'w', compression = (zipfile.ZIP_DEFLATED), allowZip64=True)
		try:
			self.fho.close()
			self.fhe.close()
			self.fhs.write('Logoff time: '+ str(time.ctime())+str('\n'))
			self.fhs.close()
			print('Report files are closed!')
			zobj.write(self.e)
			zobj.write(self.o)
			zobj.write(self.s)
			zobj.close()
			os.system('rm *.txt')
			print('.TXT files removed')
		except:
			print('Error closing report files')
			 
