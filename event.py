class Event:
    def __init__(self, name, startTime, finishTime):
        self._name = name
        self._bookingStartTime = startTime
        self._bookingFinishTime = finishTime
        self._actualStartTime = startTime
        self._actualFinishTime = finishTime
        self._billableTime = finishTime - startTime
    
    def setBookingStartTime(self, startTime):
        self._bookingStartTime = startTime
    
    def setBookingFinishTime(self, finishTime):
        self._bookingFinishTime = finishTime
    
    def setActualStartTime(self, startTime):
        self._actualStartTime = startTime
    
    def setActualFinishTime(self, finishTime):
        self._actualFinishTime = finishTime
    
    def getName(self):
        return self._name
    
    def getBookingStartTime(self):
        return self._bookingStartTime
    
    def getBookingFinishTime(self):
        return self._bookingFinishTime
    
    def getActualStartTime(self):
        return self._actualStartTime
    
    def getActualFinishTime(self):
        return self._actualFinishTime

    
    

