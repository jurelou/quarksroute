#!/usr/bin/env python3

import sys
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

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
		#mpl.rcParams['toolbar'] = 'None'
		fig = plt.figure(num='lol')
		columns = ('Freeze', 'Wind', 'Flood', 'Quake', 'Hail')
		rows = ["1", "2", "3", "4", "435"]
		yerr = 2

		cell_text = []
		for row in range(5):
		    plt.errorbar(row, row + 2,  yerr=row, fmt='s')
		  
		    cell_text.append(['012', '123', '234', '345'])

		print(cell_text)
		the_table = plt.table(cellText=cell_text,
		                      rowLabels=rows,
		                      colLabels=columns,
		                      loc='bottom')



		plt.subplots_adjust(left=0.2, bottom=0.2)
		plt.ylabel("Loss in 's")
		plt.xticks([])
		plt.title('Loss by Disaster')

		plt.show()




if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: {} ./results.xml".format(sys.argv[0]))
	else:
		main(sys.argv[1])