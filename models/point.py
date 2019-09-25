class Point:
    def __init__(self, lat, long):
        self.lat=lat
        self.long=long
        #self.address = API(lat, long)

    def to_LatLong(self):
        return str(self.lat)+','+str(self.long)

    def to_LongLat(self):
        return str(self.long)+','+str(self.lat)

    ### TO DO : definir un point à partir d'une addresse