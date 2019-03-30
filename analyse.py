#!/usr/bin/env python3

import sys
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import xml.etree.ElementTree as ET


class XmlReader():
	def __init__(self, filename):
		try:
			self.file = open(filename, 'r')
		except FileNotFoundError:
			raise Exception('File not found')

	def parse(self):
		data = {"header":{}, "hops":{}}
		root = ET.parse(self.file).getroot()
		header = root.find('header')
		data["header"]["numQueries"] = header.get('numQueries')
		data["header"]["queryTimeouts"] = header.get('queryTimeouts')
		for item in root.findall('hops/entry'):
			print(item)
			for i in item.findall('queries/query'):
				print("ll",i)
		return(data)

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
	pass
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: {} ./results.xml".format(sys.argv[0]))
	else:
		main(sys.argv[1])