#!/usr/bin/env python3

import sys
import socket
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import matplotlib as mpl
from geolite2 import geolite2
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import networkx as nx

class GUI():
	def __init__(self, data):
		mpl.rcParams['toolbar'] = 'None'
		mpl.rcParams.update({'font.size': 14})
		self.rows = ["Dns", "Minimum latency", "Average latency","Maximum latency", "errors"]
		self.data = data
		self.cellsText = []
		self.columns = ()
		self.corners = (data["header"]["lowCorner"], data["header"]["highCorner"])

	def addGraph(self):
		a = plt.figure(num="QuarksrouteGraph")
		self.columns = tuple([(hop["responses"][0]["ip"]) for hop in self.data["hops"] if "ip" in hop["responses"][0]])
		minimumLat = [hop["responses"][0]["min"] for hop in self.data["hops"] if "min" in hop["responses"][0]]
		maximumLat = [hop["responses"][0]["max"]  for hop in self.data["hops"] if "max" in hop["responses"][0]]
		diff = [hop["responses"][0]["max"] - hop["responses"][0]["min"] + (max(maximumLat) / 20) for hop in self.data["hops"] if "max" in hop["responses"][0] and "min" in hop["responses"][0]]
		b_color  = ['b'] * len(self.rows)
		index = np.arange(len(self.columns))
		plt.bar(index, diff,  0.3, bottom=minimumLat, color=b_color)

		plt.subplots_adjust(left=0.09, bottom=0.57, right=0.99, top=0.93)
	def addTable(self):
		a = plt.figure(num="QuarksrouteGraph")
		if self.columns:
			plt.title('Results for: {}.\n{} device(s) did not responded'.format(self.data["header"]["target"], self.data["header"]["timeouts"]))
			self.cellsText.append([hop["responses"][0]["dns"][:16] for hop in self.data["hops"]])

			self.cellsText.append(["{:.2f}".format(float(hop["responses"][0]["min"])) for hop in self.data["hops"]])
			self.cellsText.append(["{:.2f}".format(float(hop["responses"][0]["avg"])) for hop in self.data["hops"]])
			self.cellsText.append(["{:.2f}".format(float(hop["responses"][0]["max"])) for hop in self.data["hops"]])
			self.cellsText.append(["{}".format(hop["responses"][0]["errors"]) for hop in self.data["hops"]])
			c_color  = ['c'] * len(self.rows)
			table = plt.table(cellText=self.cellsText,
			                      rowLabels=self.rows,
			                      rowColours=c_color,
			                      colLabels=self.columns,
			                      cellLoc='center',
			                      bbox=[0, -1.50, 1., 1.5],
			                      loc='bottom')

			for cell in table._cells:
				if cell[1] != -1:
					table._cells[cell].get_text().set_rotation(50)
					table._cells[cell].get_text().set_wrap(True)
			table.auto_set_font_size(False)
			table.set_fontsize(9)
			maximumLat = [res["max"]  for hop in self.data["hops"] for hop in self.data["hops"] for res in hop["responses"]]		
			plt.ylabel("Latency")
			plt.yticks(np.arange(0, max(maximumLat) * 1.1, step=max(maximumLat) / 10))
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

	def addTree(self):
		plt.figure(num="QuarksrouteTree")
		G = nx.Graph()
		lightData = []
		for hops in self.data["hops"]:
			hop = []
			for resp in hops["responses"]:
				if resp["ip"] and not [True for h in hop if h["ip"] == resp["ip"]]:
					hop.append(resp)
			if hop: lightData.append(hop)
		cpt = 0
		tmp = {}
		edgeLabels = {}

		for hop in lightData:
			first = True
			for resp in hop:
				if not tmp:
					tmp = resp
				if first:
					if cpt == 0 or cpt == len(lightData) - 1:
						G.add_node(resp["ip"], ends=False, start=True)
					else:
						G.add_node(resp["ip"], ends=True, start=False,)
					first = False
					if tmp:
						G.add_edge(resp["ip"], tmp["ip"], path=True, label="toto")
						edgeLabels[(tmp["ip"],resp["ip"])] = resp["avg"]
						tmp = resp
				else:
					G.add_node(resp["ip"], ends=False, start=False,)
					if tmp:
						G.add_edge(tmp["ip"], resp["ip"], path=False, label="toto")
						edgeLabels[(tmp["ip"],resp["ip"])] = resp["avg"]
			cpt = cpt + 1
		pos = nx.spring_layout(G,k=0.2)
		startNodes = [node[0] for node in G.nodes(data=True) if node[1]["start"]]
		endsNodes = [node[0] for node in G.nodes(data=True) if node[1]["ends"] and not node[1]["start"]]
		otherNodes = [node[0] for node in G.nodes(data=True) if not node[1]["ends"] and not node[1]["start"]]
		pathEdges = [(u, v) for (u, v, d) in G.edges(data=True) if d['path']]
		otherEdges = [(u, v) for (u, v, d) in G.edges(data=True) if not d['path']]
		nx.draw_networkx_nodes(G, pos, nodelist=endsNodes, node_color='g',node_shape='.')
		nx.draw_networkx_nodes(G, pos, nodelist=otherNodes, node_color='r', node_shape='.')
		nx.draw_networkx_nodes(G, pos, nodelist=startNodes, node_color='g', node_shape='s')
		nx.draw_networkx_edges(G, pos, edgelist=pathEdges, width=1)
		nx.draw_networkx_edges(G, pos, edgelist=otherEdges, alpha=0.5, edge_color='b', style='dashed')

		pos_higher = {}
		y_off = 0.06
		for k, v in pos.items():
			pos_higher[k] = (v[0], v[1]+y_off)
		plt.axis('off')
		nx.draw_networkx_labels(G, pos_higher, font_size=10, font_family='sans-serif')


	def render(self):
		self.addMap()
		self.addTree()
		self.addGraph()
		self.addTable()
		


		#mng = plt.get_current_fig_manager()
		#mng.resize(*mng.window.maxsize())
		
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
		data["header"]["target"] = header.get('target')
		for entry in root.findall('hops/entry'):
			hop = {"responses":[], "id": entry.get("id")}
			responseData = {"queries": []}
			for response in entry.findall('response'):
				responseData = {"queries": []}
				responseData["ip"] = response.get("ip") if response.get("ip") else ""
				responseData["dns"] = response.get("dns") if response.get("dns") else ""
				responseData["errors"] = response.get("errors") if response.get("errors") else ""
				queries = []
				for query in response.findall('queries/query'):
					queryData = {}
					queryData["value"] = query.get("value")
					queryData["unit"] = query.get("unit")
					queries.append(queryData)
				responseData["queries"] = queries
				hop["responses"].append(responseData)
			data["hops"].append(hop)
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

def calcGeopos(data):
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
	data["header"]["lowCorner"] = (lowCorner[0] + ((-180 + lowCorner[0]) / 5), lowCorner[1] + ((-85 + lowCorner[1]) / 1.5) )
	data["header"]["highCorner"] = (highCorner[0] + ((180 - highCorner[0]) / 5),  highCorner[1] + ((85 - highCorner[1]) / 1.5)) 
	return data

def findTimeouts(data):
	cpt = 0
	for hop in data["hops"]:
		for response in hop["responses"]:
			if not response["ip"] and not response["dns"] and not response["queries"]: cpt = cpt + 1
	data["header"]["timeouts"] = str(cpt)
	return data

def calcStats(data):
	data = findTimeouts(data)
	#data["hops"] = [hop for hop in data["hops"] if hop["ip"]]
	reader = geolite2.reader()
	for hop in data["hops"]:
		hop["geo"] = None
		if hop["id"] == "1":
			hop["geo"] = reader.get(getHostAddress()) 
		elif hop["responses"][0]["ip"]:
			hop["geo"] = reader.get(hop["responses"][0]["ip"])
		for response in hop["responses"]:
			response["min"] = response["delta"] = response["max"] = response["avg"] = response["unit"] = sum = 0.
			for query in response["queries"]:
				if response["max"] == 0 or float(query["value"]) > response["max"]: response["max"] = float(query["value"])
				if response["min"] == 0 or float(query["value"]) < response["min"]: response["min"] = float(query["value"])
				sum = sum + float(query["value"])
				response["unit"] = query["unit"]
			if len(response["queries"]) > 0: response["avg"] = "{0:.2f}".format(sum / len(response["queries"]))
			response["delta"] = (response["max"] - response["min"])  / 2
	return(calcGeopos(data))

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