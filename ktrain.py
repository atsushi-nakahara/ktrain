import math

#--------------------------------------------------------------------------------------------
def getDistance(lon_a, lat_a, lon_b, lat_b):

    #print str(lon_a) +' '+ str(lat_a) +' '+ str(lon_b) +' '+  str(lat_b)

    if lon_a == lon_b and lat_a == lat_b:
        return 0

    from_x = lon_a * math.pi / 180;
    from_y = lat_a * math.pi / 180;
    #to_x = lon_b * math.pi / 180;
    #to_y = lat_b * math.pi / 180;
    to_y = lon_b * math.pi / 180;
    to_x = lat_b * math.pi / 180;

    #print str(from_x) +' '+ str(from_y) +' '+ str(to_x) +' '+  str(to_y)

    deg = math.sin(from_y) * math.sin(to_y) + math.cos(from_y) * math.cos(to_y) * math.cos(to_x - from_x);
    dist = 6378140 * (math.atan( - deg / math.sqrt(-deg * deg + 1)) + math.pi / 2);
    return dist;#in m

#--------------------------------------------------------------------------------------------
def findPlace(lon, lat):
    places = open('./places.csv', 'r')
    for place in places:
        #print place
        pos = place.split(',')
        #print pos
        d = getDistance(float(lon), float(lat), float(pos[2]), float(pos[3]));
        #print d
        if d < 200:
            print pos[1]
    return
    

#--------------------------------------------------------------------------------------------
# entry point

log = open('./gps.log', 'r')

for line in log:
    #print line
    vals = line.split(',')
    #print vals
    findPlace(vals[0], vals[1])

    

