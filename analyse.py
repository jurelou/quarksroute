#!/usr/bin/env python3

import sys
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import matplotlib as mpl

		
def parse(filename):
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

class GUI():
	def __init__(self, data):
		mpl.rcParams['toolbar'] = 'None'
		self.fig = plt.figure(num="salut")
		self.data = data
		self.cell_text = []
		self.rows = []
		self.columns = ()
		plt.ylabel("Loss in 's")
		plt.xticks([])
		plt.title('Loss by Disaster')

	def addGraph(self):
		self.columns = [hop["ip"] for hop in self.data["hops"]]
		self.rows = ["Domain name", "max latency", "min latency", "average latency"]
		
		yerr = 2
		#for row in range(len(self.columns)):
		plt.errorbar(1, 5,  yerr=2)
		plt.errorbar(2, 5,  yerr=2)
		plt.errorbar(3, 5,  yerr=2)

		self.cell_text.append([hop["min"] for hop in self.data["hops"]])
		self.cell_text.append([hop["max"] for hop in self.data["hops"]])
		self.cell_text.append([hop["avg"] for hop in self.data["hops"]])
		self.cell_text.append([hop["dns"] for hop in self.data["hops"]])
		

	def addTable(self):
		table = plt.table(cellText=self.cell_text,
		                      rowLabels=self.rows,
		                      colLabels=self.columns,
		                      loc='bottom')
		table.auto_set_font_size(False)
		table.set_fontsize(11)

	def render(self):
		self.addGraph()
		self.addTable()
		plt.subplots_adjust(left=0.2, bottom=0.2)
		plt.show()		

def calcStats(data):
	for hop in data["hops"]:
		hop["min"] = hop["delta"] = hop["max"] = hop["avg"] = sum = 0
		for query in hop["queries"]:
			if hop["max"] == 0 or float(query["value"]) > hop["max"]: hop["max"] = float(query["value"])
			if hop["min"] == 0 or float(query["value"]) < hop["min"]: hop["min"] = float(query["value"])
			sum = sum + float(query["value"])
		if len(hop["queries"]) > 0: hop["avg"] = "{0:.2f}".format(sum / len(hop["queries"]))
		hop["delta"] = (hop["max"] - hop["min"])  / 2
	return(data)

def main(filename):
	data = parse(filename)
	if data is not None:
		data = calcStats(data)	
		gui = GUI(data)
		gui.render()


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: {} ./results.xml".format(sys.argv[0]))
	else:
		main(sys.argv[1])