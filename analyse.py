#!/usr/bin/env python3

import sys
import socket
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import matplotlib as mpl
from geolite2 import geolite2
from mpl_toolkits.basemap import Basemap

class GUI():
	def __init__(self, data):
		mpl.rcParams['toolbar'] = 'None'
		mpl.rcParams.update({'font.size': 14})
		self.rows = ["Dns", "Minimum latency", "Average latency","Maximum latency", "qdfsl"]
		self.data = data
		self.cellsText = []
		self.columns = ()

	def addGraph(self):
		plt.figure(num="QuarksrouteGraph")
		self.columns = tuple([(element["ip"]) for element in self.data["hops"]])
		minimumLat = [hop["min"] for hop in self.data["hops"]]
		diff = [hop["max"] - hop["min"]  for hop in self.data["hops"]]
		b_color  = ['b'] * len(self.rows)
		index = np.arange(len(self.columns)) + 0.3
		plt.bar(index, diff, 0.2, bottom=minimumLat, color=b_color)


	def addTable(self):
		plt.figure(num="QuarksrouteGraph")
		if self.columns:
			plt.title('Results for: {}\n{} devices did not responded'.format(self.data["header"]["target"], self.data["header"]["queryTimeouts"]))
			self.cellsText.append([hop["dns"] for hop in self.data["hops"]])
			self.cellsText.append(["{} {}".format(str(hop["min"]), hop["unit"]) for hop in self.data["hops"]])
			self.cellsText.append(["{} {}".format(str(hop["avg"]), hop["unit"]) for hop in self.data["hops"]])
			self.cellsText.append(["{} {}".format(str(hop["max"]), hop["unit"]) for hop in self.data["hops"]])
			self.cellsText.append(["jesaispasencoreqsuoimùettre" for hop in self.data["hops"]])	
			c_color  = ['c'] * len(self.rows)
			table = plt.table(cellText=self.cellsText,
			                      rowLabels=self.rows,
			                      rowColours=c_color,
			                      colLabels=self.columns,
			                      loc='bottom')
			table.auto_set_font_size(False)
			table.set_fontsize(12)
			maximumLat = [hop["max"]  for hop in self.data["hops"]]		
			plt.subplots_adjust(left=0.2, bottom=0.2)
			plt.ylabel("Latency")
			plt.yticks(np.arange(0, max(maximumLat) + (max(maximumLat) / 10), max(maximumLat) / 10))
			plt.xticks([])		
		else:
			plt.title('No results found for: {}'.format(self.data["header"]["target"]))

	def addMap(self):
		pass
	def render(self):
		self.addGraph()
		self.addTable()
		plt.show()

def parseFile(filename):
	try:
		with open(filename, "r") as file: 
			root = ET.parse(file).getroot()
	except IOError as e:
		print(e)
	except:
		print("Your file is probably not a correct XML file")
	else:
		data = {"header":{}, "hops":[]}
		header = root.find('header')
		data["header"]["numQueries"] = header.get('numQueries')
		data["header"]["queryTimeouts"] = header.get('queryTimeouts')
		data["header"]["target"] = header.get('target')
		for entry in root.findall('hops/entry'):
			entryData = {}
			entryData["id"] = entry.get("id")
			entryData["ip"] = entry.get("ip")
			entryData["dns"] = entry.get("dns")
			queries = []
			for query in entry.findall('queries/query'):
				queryData = {}
				queryData["value"] = query.get("value")
				queryData["unit"] = query.get("unit")
				queries.append(queryData)
			entryData["queries"] = queries
			data["hops"].append(entryData)
		return data
	return None

def getHostAddress():
	target_host = "api.ipify.org"
	request = "GET / HTTP/1.1\r\nHost:%s\r\n\r\n" % target_host
	target_port = 80
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.settimeout(3.0) 
	try:
		client.connect((target_host,target_port))  
		client.send(request.encode())  
		response = client.recv(4096)
	except:
		return None
	finally:
		client.close()
	return response.decode().split("\r\n\r\n")[1]

def calcStats(data):
	reader = geolite2.reader()
	for hop in data["hops"]:
		hop["geo"] = reader.get(getHostAddress()) if int(hop["id"]) is 1 else reader.get(hop["ip"])
		hop["min"] = hop["delta"] = hop["max"] = hop["avg"] = sum = 0
		for query in hop["queries"]:
			if hop["max"] == 0 or float(query["value"]) > hop["max"]: hop["max"] = float(query["value"])
			if hop["min"] == 0 or float(query["value"]) < hop["min"]: hop["min"] = float(query["value"])
			sum = sum + float(query["value"])
			hop["unit"] = query["unit"]
		if len(hop["queries"]) > 0: hop["avg"] = "{0:.2f}".format(sum / len(hop["queries"]))
		hop["delta"] = (hop["max"] - hop["min"])  / 2
	a = (data["hops"][0]["geo"]["location"]["longitude"], data["hops"][0]["geo"]["location"]["latitude"]) if len(data["hops"]) > 0 else ()
	b = (data["hops"][1]["geo"]["location"]["longitude"], data["hops"][1]["geo"]["location"]["latitude"]) if len(data["hops"]) > 1 else ()
	if a and b:
		for hop in range(2, len(data["hops"])):
			print(hop["geo"]["location"]["longitude"], ";;", hop["geo"]["location"]["latitude"])
	print("------------",data["header"])
	return(data)

def main(filename):
	data = parseFile(filename)
	if data is not None:
		data = calcStats(data)	
		gui = GUI(data)
		gui.render()


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: {} ./results.xml".format(sys.argv[0]))
	else:
		main(sys.argv[1])