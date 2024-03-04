#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" -----------------------------------------
	Module de communication Modbus
	pour communiquer avec les cartes driver pas-à-pas MIP0505
	Midi Ingenierie (NS) 2023
	noe.serres@hensoldt.fr
	-----------------------------------------
""" 
__author__ = "Noe Serres"
__version__ = "1.0.0"

import minimalmodbus
import configparser
import logging


class MIP0505:
	"""
	initialisation du port série et du dictionnaire
	"""
	def __init__(self, portCOM='COM1', baudrate=115200, modbusAddress=1, dictionnaryFile='dictionnaireMIP.ini'):
		self.portCOM = portCOM
		self.baudrate = baudrate
		self.modbusAddress = modbusAddress
		self.dictionnaryFile = dictionnaryFile
		
		#instanciation de l'objet modbus
		try:
			self.MB = minimalmodbus.Instrument(port=self.portCOM,slaveaddress=self.modbusAddress,mode=minimalmodbus.MODE_RTU)
			self.MB.serial.baudrate = self.baudrate
		except:
			logging.error(f"Unreachable RS485 port")
		
		#instanciation du dictionnaire de registres		
		try:
			config = configparser.ConfigParser()
			config.read(self.dictionnaryFile)
			self.inputRegisters = dict(config['InputRegisters'])
			self.holdingRegisters = dict(config['HoldingRegisters'])
		except:
			logging.error("Error config file")		

	"""
	relecture d'un registre avec recherche du nom dans le dictionnaire
	"""
	def read(self, register):
		match_found = False
		for regname, regaddr in self.inputRegisters.items():
			if regname.upper() == register.upper():
				match_found = True
				try:
					val = self.MB.read_long(int(regaddr),byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,signed=True,functioncode=4)
				except Exception as e:
					logging.error("Modbus Error: %s", e)
				return val
		for regname, regaddr in self.holdingRegisters.items():
			if regname.upper() == register.upper():
				match_found = True
				try:
					val = self.MB.read_long(int(regaddr),byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,signed=True,functioncode=3)
				except Exception as e:
					logging.error("Modbus Error: %s", e)
				return val
		if not match_found:
			raise Exception(f"Could not find {register} in the dictionnary")
		return None

	"""
	écriture d'un registre (32bits obligatoire) avec recherche du nom dans le dictionnaire
	"""
	def write(self, register, value):
		match_found = False
		for regname, regaddr in self.holdingRegisters.items():
			if regname.upper() == register.upper():
				match_found = True
				try:
					val = self.MB.write_long(registeraddress=int(regaddr),value=int(value),byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,signed=True)
				except Exception as e:
					logging.error("Modbus Error: %s", e)
		if not match_found:
			raise Exception(f"Could not find {register} in the dictionnary")
		return


"""
Exemple d'application
"""
if __name__ == '__main__':
	from time import sleep
	from random import randint
	
	mip = MIP0505(portCOM='COM2',modbusAddress=1)
	
	alim = mip.read('SUPPLY_VOLTAGE')
	print(f"Tension d'alim: {alim}")


	mip.write('MODE',0x20000000)	#Mode AutoPosition
	sleep(0.2)						#Attente pendant le flashage
	mip.write('DEFAULT',0)			#Reset du défaut "Flashage"

	mip.write('PROFILE_ACCEL',1000)
	mip.write('TARGET_VELOCITY',1000)
	pos = mip.read('MOTOR_POSITION_ABS')
	target = pos + 2000
	print(f"AutoPosition Mode {pos} -> {target}")
	mip.write('TARGET_POSITION_ABS',target)

	sleep(5)

	mip.write('MODE',0x40000000)	#Mode AutoVelocity (les pas sont générés par une commande)
	sleep(0.2)						#Attente pendant le flashage
	mip.write('DEFAULT',0)			#Reset du défaut "Flashage"

	print("AutoVelocity Mode")		#Execution d'une séquence de segments à des vitesses différentes
	for i in range(7):
		cns = randint(-1000, 1000)
		acc = randint(300, 3000)
		tempo = randint(1000, 10000)/1000
		print(f"seg:{i} cns:{cns} acc:{acc} tmp:{tempo}")
		mip.write('PROFILE_ACCEL',acc)
		mip.write('TARGET_VELOCITY',cns)
		sleep(tempo)

	print("end sequence")
	mip.write('TARGET_VELOCITY',0)	#Commande d'arret






