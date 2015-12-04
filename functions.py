# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import json
import sys


''' AWS DBR functions '''

class ProgressBar( object ):
	''' Progressbar class draw a simple progressbar in tty (if you redirect tty to file the output will be broken)
	Paramenters:
	  Barsize = the size of progressbar to draw. Default is 25 colums
	  Barmax = Total value of the progress bar, default is 100 but can be any number that will be evaluated from 0 to Total
	  Curval = Current value to start the progressbar. Default is 0 but can start with 50 for example
	  Name = String in the beggining of the ProgressBar
	  Empty = Empty string to fill the ProgressBar
	  Fill = Filled progress bar
	  Delim = start and end delimiter
	  Drawperc = Draw the percentage of the ProgressBar. Default is False
	  '''
	def __init__(self, barsize=25, barmax=100, curval=0, name='Processing', empty='-', fill='#', delim='[]', drawperc=False):
		self.barsize = barsize
		self.barmax = float(barmax)
		self.curval = float(curval)
		self.name = name
		self.empty = empty
		self.fill = fill
		self.delim = delim
		self.drawperc = drawperc

	def initialize(self):
		fullfill = self.fill * int( (self.curval / self.barmax) * self.barsize )
		emptyfill = self.empty * int(self.barsize - len(fullfill) )
		if self.drawperc:
			percentage = '{:.0%}'.format( self.curval / self.barmax)
		else:
			percentage = '   '
		sys.stdout.write( "\r{0}:{1}{2}{3}{4} {5}".format( self.name, self.delim[:1], fullfill, emptyfill, self.delim[1:], percentage) )
		sys.stdout.flush()

	def update(self,curval):
		self.curval = curval
		fullfill = self.fill * int( (self.curval / self.barmax) * self.barsize )
		emptyfill = self.empty * int(self.barsize - len(fullfill))
		if self.drawperc:
			percentage = '{:.0%}'.format( self.curval / self.barmax )
		else:
			percentage = '   '
		sys.stdout.write( "\r{0}:{1}{2}{3}{4} {5}".format( self.name, self.delim[:1], fullfill, emptyfill, self.delim[1:], percentage) )
		sys.stdout.flush()

	def done(self):
		fillsize = self.fill * self.barsize
		sys.stdout.write( "\r{0}:{1}{2}{3} Done".format( self.name, self.delim[:1], fillsize, self.delim[1:] ) )
		print("")

# Convert Unicode to ascii
def ascii_encode_dict(data):
	''' Convert Unicode to ascii 
	args: unicode
	return: ascii
	'''
	ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x 
	return dict(map(ascii_encode, pair) for pair in data.items())

#Find subkeys like 'key:subkey' inside the JSON structure and create new dict inside dict (nested dict)
def split_subkeys(json_string):
	'''
	Find jsoin keys like: "{ key.subkey : value }" and replace to "{ key : { subkey: value } }"
	args: json string
	return: jsoin string
	'''

	#json_key = json.loads( json_string ,object_hook=ascii_encode_dict )
	json_key = json.loads( json_string )
	temp_json = {}
	for key, value in json_key.items():
		index = key.find(":")
		if index > -1:
			if temp_json.get( key[ :index ], 1 ) == 1: 
				temp_json[ key[ :index ] ] = {}
			temp_json[ key[ :index ] ][ key[ index+1: ] ] =  value
		else:
			temp_json.update( { key : value } )

	return temp_json

def bulk_data(json_string, bulk):
	''' Check if json has bulk data / control messages
	the string to check are in format: { key : [strings] }
	return: True if found a control message and false if not found
	'''
	json_key = json.loads( json_string )
	for key, value in bulk.items():
		if key in json_key.keys():
			for v in bulk[key]:
				if json_key[key].find(v) > -1: return True
	return False
