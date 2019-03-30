#!/usr/bin/env python3

import os
import sys
import socket
import argparse
import subprocess
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

class XmlWriter():
	def __init__(self, filename, numQueries):
		print("Writing to file: {}".format(filename))
		self.numQueries = numQueries
		self.hopsList = []
		self.queryTimeout = 0
		self.file = open(filename, 'w')
		self.root = Element('root')
		self.rootHeader = SubElement(self.root, 'header')
		self.rootHeader.set("numQueries", str(numQueries))

	def prettify(self, elem):
	    string = ElementTree.tostring(elem, 'utf-8')
	    prettyString = minidom.parseString(string)
	    return prettyString.toprettyxml(indent="  ")

	def push(self, data):
		self.hopsList.append(data)

	def flush(self):
		rootHops = SubElement(self.root, "hops")
		self.rootHeader.set("queryTimeouts", str(self.queryTimeout))		
		for item in self.hopsList:
			entry = SubElement(rootHops, "entry")
			entry.set("id", item["id"])
			entry.set("ip", item["ip"])
			entry.set("dns", item["dns"])
			queries = SubElement(entry, "queries")
			for queryData in item["queries"]:
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
	if parseTracerouteLine.lineNumber != 1:
		print(line, end="")
		words = line.split()
		hop = {}
		hop["id"] = words.pop(0)
		hop["dns"] = words.pop(0)
		hop["ip"] = words.pop(0)[1:-1]
		queries = []
		if len(words) == writer.numQueries * 2:
			while len(words) > 0:
				query = {}
				query["value"] = words.pop(0)
				query["unit"] = words.pop(0)
				queries.append(query)
			hop["queries"] = queries
			writer.push(hop)
		else:
			writer.queryTimeout = writer.queryTimeout + 1 


parseTracerouteLine.lineNumber = 0

def execTraceroute(writer, cmd):
	print("Running command: {}".format(' '.join(cmd)))
	try:
		for line in execute(cmd):
			parseTracerouteLine(writer, line)
	except subprocess.CalledProcessError as e:
		print("Error from traceroute command.")
	except:
		print("Error:")

def main(args):
	cmd = generateCommand(args)
	filename = args.file if args.file else "results-{}.xml".format(args.host)
	writer = XmlWriter(filename, args.queries)
	execTraceroute(writer, cmd)
	writer.flush()

if __name__ == "__main__":
	args = parseArgs()
	if resolve(args.host):
		main(args)
