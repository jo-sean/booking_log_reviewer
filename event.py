class Event:
    def __init__(self, name, startTime, endTime):
        self.name = name
        self.startTime = startTime
        self.endTime = endTime
        self.hasBeenReminded = False
    
    def sendReminder(self):
        print(f'{self.name} reminder')
        self.hasBeenReminded = True