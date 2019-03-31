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
		self.rows = ["Dns", "Minimum latency", "Average latency","Maximum latency"]
		self.data = data
		self.cellsText = []
		self.columns = ()
		self.corners = (data["header"]["lowCorner"], data["header"]["highCorner"])

	def addGraph(self):
		plt.figure(num="QuarksrouteGraph")
		self.columns = tuple([(element["ip"]) for element in self.data["hops"]])
		minimumLat = [hop["min"] for hop in self.data["hops"]]
		diff = [hop["max"] - hop["min"] + 2  for hop in self.data["hops"]]
		b_color  = ['b'] * len(self.rows)
		index = np.arange(len(self.columns)) + 0.3
		plt.bar(index, diff, 0.2, bottom=minimumLat, color=b_color)


	def addTable(self):
		plt.figure(num="QuarksrouteGraph")
		if self.columns:
			plt.title('Results for: {}\n{} devices did not responded'.format(self.data["header"]["target"], self.data["header"]["queryTimeouts"]))
			self.cellsText.append([hop["dns"][:16] for hop in self.data["hops"]])
			self.cellsText.append(["{} {}".format(str(hop["min"]), hop["unit"]) for hop in self.data["hops"]])
			self.cellsText.append(["{} {}".format(str(hop["avg"]), hop["unit"]) for hop in self.data["hops"]])
			self.cellsText.append(["{} {}".format(str(hop["max"]), hop["unit"]) for hop in self.data["hops"]])
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
		plt.figure(num="QuarksrouteMap")
		m=Basemap(llcrnrlon=self.corners[0][0], llcrnrlat=self.corners[0][1],urcrnrlon=self.corners[1][0],urcrnrlat=self.corners[1][1])
		m.drawmapboundary(fill_color='#A6CAE0', linewidth=0)
		m.fillcontinents(color='grey', alpha=0.6, lake_color='blue')
		m.drawcountries(color="white")
		m.drawcoastlines(linewidth=0.1, color="white")
		head = ()
		index = 0
		for hop in self.data["hops"]:
			if hop["geo"]:
				if head is not ():
					m.drawgreatcircle(head[0], head[1], hop["geo"]["location"]["longitude"], hop["geo"]["location"]["latitude"], linewidth=2, color='blue')
				head = (hop["geo"]["location"]["longitude"], hop["geo"]["location"]["latitude"])
				m.plot(head[0], head[1], linestyle='none', marker="o", markersize=8, alpha=0.6, c="cyan", markeredgecolor="black", markeredgewidth=1)
				plt.annotate(index,  xy=(head[0], head[1] + 2))
				index=index+1
	def render(self):
		self.addMap()
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
		hop["geo"] = reader.get(getHostAddress()) if hop["id"] == "1" else reader.get(hop["ip"])
		hop["min"] = hop["delta"] = hop["max"] = hop["avg"] = sum = 0
		for query in hop["queries"]:
			if hop["max"] == 0 or float(query["value"]) > hop["max"]: hop["max"] = float(query["value"])
			if hop["min"] == 0 or float(query["value"]) < hop["min"]: hop["min"] = float(query["value"])
			sum = sum + float(query["value"])
			hop["unit"] = query["unit"]
		if len(hop["queries"]) > 0: hop["avg"] = "{0:.2f}".format(sum / len(hop["queries"]))
		hop["delta"] = (hop["max"] - hop["min"])  / 2
	lowCorner = highCorner = (None, None)
	for hop in data["hops"]:
		if hop["geo"] is not None:
			latitude = hop["geo"]["location"]["latitude"]
			longitude = hop["geo"]["location"]["longitude"]
			if lowCorner[0] is None or longitude < lowCorner[0]:
				lowCorner = (longitude, lowCorner[1])
			if lowCorner[1] is None or latitude < lowCorner[1]:
				lowCorner = (lowCorner[0], latitude)
			if highCorner[0] is None or longitude > highCorner[0]:
				highCorner = (longitude, highCorner[1])
			if highCorner[1] is None or latitude > highCorner[1]:
				highCorner = (highCorner[0], latitude)
	data["header"]["lowCorner"] = (lowCorner[0] - 5, lowCorner[1] - 2) 
	data["header"]["highCorner"] = (highCorner[0] + 5, highCorner[1] + 2) 
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