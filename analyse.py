#!/usr/bin/env python3

import sys
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl 
from matplotlib.backend_tools import ToolBase, ToolToggleBase
import matplotlib.patches as patches

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

def main(filename):
	data = parse(filename)
	if data is not None:
		print(data)
		mpl.rcParams['toolbar'] = 'None'
		fig = plt.figure(num='lol')
		#fig.set_facecolor("#00000F")

		"""
		df = pd.DataFrame({ 'from':['A', 'B', 'C','A'], 'to':['D', 'A', 'E','C'] })
		 
		G=nx.from_pandas_edgelist(df, 'from', 'to', create_using=nx.Graph() )
		nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_color='white')
		"""
		G = nx.Graph()
		i = 0
		while i <= 10:
			if i < 10:
				G.add_edge(i+1,i)
			G.add_node(i, pos=(i,2))
			i = i +1

		currentAxis = plt.gca()
		pos=nx.get_node_attributes(G,'pos')
		rect = patches.Rectangle((50,100),40,30,linewidth=1,edgecolor='r',facecolor='none')



		nx.draw(G, pos,with_labels=True,node_size=1500, node_color="skyblue", node_shape="s", alpha=0.5, linewidths=1)
		plt.show()







if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: {} ./results.xml".format(sys.argv[0]))
	else:
		main(sys.argv[1])