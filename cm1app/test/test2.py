import requests


host = 'https://grogdata.soest.hawaii.edu'

url = 'https://grogdata.soest.hawaii.edu/data/2/node-020/ReceptionTime,t0,t1.json?time_col=ReceptionTime&begin=1506070000&end=1506079094'
r = requests.get(url).json()
print(len(r))
print(len(r[0]))
print(r)
