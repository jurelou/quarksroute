### This project is still in WIP
This software has been tested using ubuntu 16.04 and traceroute version 2.0.21
## INSTALL
`apt-get install python3-tk libgeos-dev`

`pip install https://github.com/matplotlib/basemap/archive/master.zip`
`pip3 install -r requirements.txt`

## Usage
`./trace.py www.example.com -f myresults.txt`

`./analyse.py myresults.txt`


## Reporting
The analysis script will parse the generated file and open three different Windows: QuarksGraph, QuarkTree and QuarksRoute

![Graph](https://github.com/jurelou/quarksroute/blob/master/examples/graph.png)
![Tree](https://github.com/jurelou/quarksroute/blob/master/examples/tree.png)
![Map](https://github.com/jurelou/quarksroute/blob/master/examples/map.png)
