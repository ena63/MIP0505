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
__version__ = "1.0.1"

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
		for regname, data in self.inputRegisters.items():
			if regname.upper() == register.upper():
				match_found = True
				parts = data.split('_')
				regaddr = int(parts[0])
				size = int(parts[1]) 
				try:
					if size == 16:
						val = self.MB.read_register(regaddr,signed=(parts[2] =='s'),functioncode=4)
					if size == 32:	
						val = self.MB.read_long(regaddr,byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,signed=(parts[2] =='s'),functioncode=4)
					return val
				except Exception as e:
					logging.error("Modbus Error: %s", e)
		for regname, data in self.holdingRegisters.items():
			if regname.upper() == register.upper():
				parts = data.split('_')
				regaddr = int(parts[0])
				size = int(parts[1]) 
				try:
					if size == 16:
						val = self.MB.read_register(regaddr,signed=(parts[2] =='s'),functioncode=3)
					if size == 32:	
						val = self.MB.read_long(regaddr,byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,signed=(parts[2] =='s'),functioncode=3)
					return val
				except Exception as e:
					logging.error("Modbus Error: %s", e)
		raise Exception(f"Could not find {register} in the dictionnary")
		return None

	"""
	écriture d'un registre (32bits obligatoire) avec recherche du nom dans le dictionnaire
	"""
	def write(self, register, value):
		for regname, data in self.holdingRegisters.items():
			if regname.upper() == register.upper():
				parts = data.split('_')
				regaddr = int(parts[0])
				size = int(parts[1]) 
				try:
					if size == 16:
						val = self.MB.write_register(registeraddress=regaddr,value=int(value),signed=(parts[2] =='s'),functioncode=6)
					if size == 32:	
						val = self.MB.write_long(registeraddress=regaddr,value=int(value),byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,signed=(parts[2] =='s'))
					return
				except Exception as e:
					logging.error("Modbus Error: %s", e)
		raise Exception(f"Could not find {register} in the dictionnary")
		return


"""
Exemple d'application
"""
if __name__ == '__main__':
	from time import sleep
	from random import randint
	
	mip = MIP0505(portCOM='COM1',modbusAddress=1)
	
	alim = mip.read('SUPPLY_VOLTAGE')
	print(f"Tension d'alim: {alim/100}V")
	stat = mip.read('STATUS_MOTOR')
	print(f"Status: 0x{stat:08x}")


	mip.write('DEFAULT',0)		#Reset du défaut "Flashage"
	mip.write('DEFAULT_MEM',0)	#Reset du défaut "Flashage"

	pos = mip.read('MOTOR_POS_ABS')
	print(f"Profile_Position Mode (relative {pos}->{pos+3000})")
	mip.write('MODES_OF_OP',1)	#Mode AutoPosition
	mip.write('PROFILE_ACCELERATION',1000)
	mip.write('TARGET_VELOCITY',1000)
	mip.write('TARGET_POSITION_REL',3000)

	for i in range(40):
		pos = mip.read('MOTOR_POS_ABS')
		print(f"{pos}",end=" ",flush=True)
		sleep(0.2)
	print("")
	
	pos = mip.read('MOTOR_POS_ABS')
	target = pos + 2000
	print(f"Profile_Position Mode (absolute {pos}->{target})")
	mip.write('TARGET_POSITION_ABS',target)

	for i in range(35):
		pos = mip.read('MOTOR_POS_ABS')
		print(f"{pos}",end=" ",flush=True)
		sleep(0.2)
	print("")
	
	print("Profile_Velocity Mode")		#Execution d'une séquence de segments à des vitesses différentes
	mip.write('MODES_OF_OP',3)	#Mode Profile_Velocity (les pas sont générés par une commande)
	for i in range(7):
		cns = randint(-1000, 1000)
		acc = randint(300, 3000)
		tempo = randint(1000, 10000)/1000
		print(f"seg:{i} cns:{cns} acc:{acc} tmp:{tempo}")
		mip.write('PROFILE_ACCELERATION',acc)
		mip.write('TARGET_VELOCITY',cns)
		sleep(tempo)

	print("end sequence")
	mip.write('TARGET_VELOCITY',0)	#Commande d'arret






