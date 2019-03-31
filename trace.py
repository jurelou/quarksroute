#!/usr/bin/env python3

import os
import sys
import socket
import argparse
import subprocess
import analyse
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

class XmlWriter():
	def __init__(self, filename, args):
		print("Writing to file: {}".format(filename))
		self.numQueries = args.queries
		self.hopsList = []
		self.file = open(filename, 'w')
		self.root = Element('root')
		self.rootHeader = SubElement(self.root, 'header')
		self.rootHeader.set("numQueries", str(args.queries))
		self.rootHeader.set("target", str(args.host))
	def prettify(self, elem):
	    string = ElementTree.tostring(elem, 'utf-8')
	    prettyString = minidom.parseString(string)
	    return prettyString.toprettyxml(indent="  ")

	def push(self, data):
		self.hopsList.append(data)

	def flush(self):
		rootHops = SubElement(self.root, "hops")
		for item in self.hopsList:
			entry = SubElement(rootHops, "entry")
			entry.set("id", item["id"])
			for response in item["responses"]:
				responseElem = SubElement(entry, "response")
				if "ip" in response: responseElem.set("ip", response["ip"])
				if "dns" in response: responseElem.set("dns", response["dns"])
				if "errors" in response: responseElem.set("errors", response["errors"])
				if "queries" in response:
					queries = SubElement(responseElem, "queries")				
					for queryData in response["queries"]:
						query = SubElement(queries, "query")
						query.set("value", queryData["value"])
						query.set("unit", queryData["unit"])
		self.file.write(self.prettify(self.root))
		self.file.close()

def parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument("host")
	parser.add_argument("--tcp", "-T", help="Use TCP SYN", action="store_true")
	parser.add_argument("--ipv6", "-6", help="use IPv6", action="store_true", default=False)
	parser.add_argument("--interface", "-i", help="Specify a network interface")
	parser.add_argument("--queries", "-q", help="Set the number of probes for each hop", default=3)
	parser.add_argument("--file", "-f", help="Save results to file, default file name is the host name")
	return parser.parse_args()

def isRoot():
	euid = os.geteuid()
	if euid != 0:
		print ("Script not started as root. Running sudo..")
		args = ['sudo', sys.executable] + sys.argv + [os.environ]
		os.execlpe('sudo', *args)
	return True

def resolve(name):
	try:
		socket.gethostbyname(name)
	except:
		print("Could not resolve address for: {}".format(name))
		return False
	return True

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

def generateCommand(args):
	cmd = ["traceroute", args.host]
	if args.tcp and isRoot():
		cmd = cmd + ["--tcp"]
	if args.ipv6:
		cmd = cmd + ["-6"]
	if args.interface:
			cmd = cmd + ["-i", args.interface]
	cmd = cmd + ["-q", str(args.queries)]
	return cmd

def parseTracerouteLine(writer, line):
	parseTracerouteLine.lineNumber += 1
	errors = ["*", "!N", "!P", "!H", "!T", "!Q", "!U", "?", "!A"]
	if parseTracerouteLine.lineNumber != 1:
		print(line, end="")
		words = line.split()
		if words == [] :return
		hop = {"responses": []}
		hop["id"] = words.pop(0)
		response = {"errors": ""}
		while (len(words)):
			token = words.pop(0)
			try:
				float(token)
				if len(words) > 0:
					query = {}
					query["value"] = token
					query["unit"] = words.pop(0)
					response["queries"].append(query)		
			except ValueError:
				if token in errors:  
					response["errors"] = response["errors"] + token
				else:
					if "dns" in response:
						hop["responses"].append(response)
					response = {"dns": token, "ip": words.pop(0)[1:-1], "queries": [], "errors": ""}

		hop["responses"].append(response)
		writer.push(hop)
parseTracerouteLine.lineNumber = 0

def execTraceroute(writer, cmd):
	print("Running command: {}".format(' '.join(cmd)))
	filepath = 'toto'  
	with open(filepath) as fp:  
		line = fp.readline()
		cnt = 1
		while line:
			parseTracerouteLine(writer, line)
			line = fp.readline()
			cnt += 1
	return True
	try:
		for line in execute(cmd):
			parseTracerouteLine(writer, line)
	except subprocess.CalledProcessError as e:
		print("Error from traceroute command.")
		return False
	except Exception as e:
		print("Error:", e)
		return False
	return True

def askAnalyse(filename):
	answer = None
	while answer not in ("y", "n"):
		try:
			answer = input("Do you want to analyse the results ? Press [y/n]")
		except: return
		if answer.lower()[0] == "y":
			return analyse.main(filename)
		elif answer.lower()[0] == "n":
			return

def main(args):
	cmd = generateCommand(args)
	filename = args.file if args.file else "results-{}.xml".format(args.host)
	writer = XmlWriter(filename, args)
	if execTraceroute(writer, cmd):
		writer.flush()
		askAnalyse(filename)

if __name__ == "__main__":
	args = parseArgs()
	if resolve(args.host):
		main(args)
