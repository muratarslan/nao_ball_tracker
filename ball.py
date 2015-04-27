import motion
import math
import time

from naoqi import ALBroker
from naoqi import ALProxy

class Nao():

    # Usage
    # Nao().searchBall()
    # Nao().hasBall()
    # Nao().walkToBall()
    # Nao().protectionOff()  should call before moves
    
    def __init__(self):
        self.myBroker = ALBroker("myBroker","0.0.0.0",0,"10.51.5.167",9559)
        self.motion   = ALProxy("ALMotion")
        self.tracker  = ALProxy("ALRedBallTracker")
        self.vision   = ALProxy("ALVideoDevice")
        self.tts      = ALProxy("ALTextToSpeech")
        self.currentCamera = 0
        self.setTopCamera()
        self.tracker.setWholeBodyOn(False)
        self.tracker.startTracker()
        self.ballPosition = []
        self.targetPosition = []


    def __del__(self):
        self.tracker.stopTracker()
        pass


    # If Nao has ball returns True
    def hasBall(self):
        self.checkForBall()
        time.sleep(0.5)
        if self.checkForBall():
            return True
        else:
            return False


    # Nao scans around for the redball
    def searchBall(self):
        self.motion.stiffnessInterpolation("Body", 1.0, 0.1)
        self.motion.walkInit()
        for turnAngle in [0,math.pi/1.8,math.pi/1.8,math.pi/1.8]:
            if turnAngle > 0:
                self.motion.walkTo(0,0,turnAngle)
            if self.hasBall():
                self.turnToBall()
                return
            for headPitchAngle in [((math.pi*29)/180),((math.pi*12)/180)]:
                self.motion.angleInterpolation("HeadPitch", headPitchAngle,0.3,True)
                for headYawAngle in [-((math.pi*40)/180),-((math.pi*20)/180),0,((math.pi*20)/180),((math.pi*40)/180)]:
                    self.motion.angleInterpolation("HeadYaw",headYawAngle,0.3,True)
                    time.sleep(0.3)
                    if self.hasBall():
                        self.turnToBall()
                        return


    # Nao walks close to ball
    def walkToBall(self):
        ballPosition = self.tracker.getPosition()
        headYawTreshold = ((math.pi*10)/180)
        x = ballPosition[0]/2 + 0.05
        self.motion.stiffnessInterpolation("Body", 1.0, 0.1)
        self.motion.walkInit()
        self.turnToBall()
        self.motion.post.walkTo(x,0,0)
        while True:
            headYawAngle = self.motion.getAngles("HeadYaw", False)
            if headYawAngle[0] >= headYawTreshold or headYawAngle[0] <= -headYawTreshold:
                self.motion.stopWalk()
                self.turnToBall()
                self.walkToBall()
                break
            #dist = self.getDistance()
            # if dist < 0.1:
            #     self.motion.stopWalk()
            #     self.turnToBall()
            #     self.safePosition()
            #     time.sleep(1)
            #     self.tts.say("You have 5 seconds to move the ball")
            #     time.sleep(5)
            #     # naoWalkToPosition()
            #     self.walkToPosition()
            #     self.setTopCamera()
            #     break
                return


    # nao turns to ball 
    def turnToBall(self):
        if not self.hasBall():
            return False
        self.ballPosition = self.tracker.getPosition()
        b = self.ballPosition[1]/self.ballPosition[0]
        z = math.atan(b)
        self.motion.stiffnessInterpolation("Body", 1.0, 0.1)
        self.motion.walkInit()
        self.motion.walkTo(0,0,z)


    # checks ball
    def checkForBall(self):
        newdata = self.tracker.isNewData()
        if newdata == True:
            self.tracker.getPosition()
            return newdata
        if newdata == False:
            self.tracker.getPosition()
            return newdata


    # has to be called after walkToBall()
    def walkToPosition(self):
        x = (self.targetPosition[0]/2)
        self.motion.walkTo(x,0,0)


    # Determine safe position
    def safePosition(self):
        if self.hasBall():
            self.targetPosition = self.tracker.getPosition()
        else:
            return False


    # gets the distance from ball
    def getDistance(self):
        if self.hasBall():
            ballPosition = self.tracker.getPosition()
            return math.sqrt(math.pow(ballPosition[0],2) + math.pow(ballPosition[1],2))


    # setting up top camera
    def setTopCamera(self):
        self.vision.setParam(18,0)
        self.currentCamera = 0


    # setting up bottom camera
    def setBottomCamera(self):
        self.vision.setParam(18,1)
        self.currentCamera = 1


    # protection off to move free
    def protectionOff(self):
        self.motion.setExternalCollisionProtectionEnabled( "All", False )
        print "Protection Off"


    # protection on
    def protectionOn(self):
        self.motion.setExternalCollisionProtectionEnabled( "All", True )
        print "Protection On"
