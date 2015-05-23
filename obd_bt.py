
#------------------  OBD Bluetooth module - v1.0  ----------------------#
#																		#
# Author: Júlio Ribeiro	- ISCTE/IUL - Engineering Master Degrees        #
# Date: 23/05/2015, Lisbon												#
# License: GPL															#
# Description: This module intent to implement a gateway for issuing AT # 
#              commands in order to communicate with an "OBD-II ELM327" #
#              bluetooth adaptater.It sends and receives normalized data#
#																		#
#-----------------------------------------------------------------------#
 

from bluetooth import *
import os
import sys
import time
import variables
import bluetooth
import ConfigParser



# Class OBDCom() should be instantiated with a;
# 	host: Bluetooth MAC Address of the ELM327
#	port: Bluetooth serial port (Serial Port profile)
#   wait: Interval in seconds, for reading incoming BT data (results) after sent an AT Command.
class OBDCom():

	retryLimit = 0
		
	def __init__(self, host=None, port=None, wait=None):
		
		# Bluetooth OBD Server adapter parameters
		self.host = host
		self.port = port
		self.wait = wait
		
		try:
			self.bt = BluetoothSocket(RFCOMM)
			self.bt.connect((self.host,self.port))
			print('Bluetooth connected')
			OBDCom.retryLimit =0
			
		except:
			print('Failed to connecto to bluetooth')
			self.__retryConnect(self.host, self.port, self.wait)
			
	def __retryConnect(self, host, port, wait):
		if OBDCom.retryLimit <= 3:
			print('Retrying',OBDCom.retryLimit)
			OBDCom.retryLimit +=1
			self.__init__(host, port, wait)
		print('Bluetooth connection not possible')
		OBDCom.retryLimit =0
		quit()
		
			
### FUNCTION: Generic send command to OBD
### Description: Send a string as a command to bluetooth
###		cmd: command (string) to send
###     timeout: wait time to start reading returned data (buffer lenght of 512 bytes)
###     data: response received after issued the command. List of bytes.
	def sendCmd(self, cmd, timeout=self.wait):
		try:
			self.bt.send(cmd)
			time.sleep(timeout)
			data = self.bt.recv(512)
			data = str(data)[2:].replace('\\r',' ').split()
			return data
		except:
			print('Error issuing command:',cmd)
			return False
