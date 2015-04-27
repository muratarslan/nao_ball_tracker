from gi.repository import Gtk
import config as c
import motion
import math
import time

from naoqi import ALBroker
from naoqi import ALProxy

class BallTracker:
        
    def __init__(self, glade_file_path=c.GLADE_FILE_PATH):
	self.glade_file_path = glade_file_path
            
	# Gtk Builder Init
	self.builder = Gtk.Builder()
	self.builder.add_from_file(self.glade_file_path)
	self.builder.connect_signals(self)

	# Add UI Components
	self.window = self.builder.get_object("ballWindow")

	# Show UI
	self.window.show_all()

	self.myBroker = ALBroker("myBroker","0.0.0.0",0,"10.0.2.3",9559)
        self.motion   = ALProxy("ALMotion")
        self.tracker  = ALProxy("ALRedBallTracker")
        self.vision   = ALProxy("ALVideoDevice")
        self.tts      = ALProxy("ALTextToSpeech")
        self.currentCamera = 0
        self.setTopCamera(self)
        self.tracker.setWholeBodyOn(False)
        self.tracker.startTracker()
        self.ballPosition = []
        self.targetPosition = []

    ### Destroy GUI
    def destroy(self, widget):
	print "destroyed"
	Gtk.main_quit()


    def __del__(self, widget):
	self.tracker.stopTracker(self)
	pass

    # If Nao has ball returns True
    def hasBall(self, widget):
        self.checkForBall(self)
        time.sleep(0.5)
        if self.checkForBall(self):
	    print "I see the Ball"
            return True
        else:
	    print "Sorry I cant find the ball"
            return False

    # Nao scans around for the redball
    def searchBall(self, widget):
        self.motion.stiffnessInterpolation("Body", 1.0, 0.1)
        self.motion.walkInit()
        for turnAngle in [0,math.pi/1.8,math.pi/1.8,math.pi/1.8]:
            if turnAngle > 0:
                self.motion.walkTo(0,0,turnAngle)
            if self.hasBall(self):
                self.turnToBall(self)
                return
            for headPitchAngle in [((math.pi*29)/180),((math.pi*12)/180)]:
                self.motion.angleInterpolation("HeadPitch", headPitchAngle,0.3,True)
                for headYawAngle in [-((math.pi*40)/180),-((math.pi*20)/180),0,((math.pi*20)/180),((math.pi*40)/180)]:
                    self.motion.angleInterpolation("HeadYaw",headYawAngle,0.3,True)
                    time.sleep(0.3)
                    if self.hasBall(self):
                        self.turnToBall(self)
                        return


    # Nao walks close to ball
    def walkToBall(self, widget):
        ballPosition = self.tracker.getPosition()
        headYawTreshold = ((math.pi*10)/180)
        x = ballPosition[0]/2 + 0.05
        self.motion.stiffnessInterpolation("Body", 1.0, 0.1)
        self.motion.walkInit()
        self.turnToBall(self)
        self.motion.post.walkTo(x,0,0)
        while True:
            headYawAngle = self.motion.getAngles("HeadYaw", False)
            if headYawAngle[0] >= headYawTreshold or headYawAngle[0] <= -headYawTreshold:
                self.motion.stopWalk()
                self.turnToBall(self)
                self.walkToBall(self)
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
    def turnToBall(self, widget):
        if not self.hasBall(self):
            return False
        self.ballPosition = self.tracker.getPosition()
        b = self.ballPosition[1]/self.ballPosition[0]
        z = math.atan(b)
        self.motion.stiffnessInterpolation("Body", 1.0, 0.1)
        self.motion.walkInit()
        self.motion.walkTo(0,0,z)


    # checks ball
    def checkForBall(self, widget):
        newdata = self.tracker.isNewData()
        if newdata == True:
            self.tracker.getPosition()
            return newdata
        if newdata == False:
            self.tracker.getPosition()
            return newdata


    # has to be called after walkToBall()
    def walkToPosition(self, widget):
        x = (self.targetPosition[0]/2)
        self.motion.walkTo(x,0,0)


    # Determine safe position
    def safePosition(self, widget):
        if self.hasBall():
            self.targetPosition = self.tracker.getPosition()
        else:
            return False


    # gets the distance from ball
    def getDistance(self, widget):
        if self.hasBall():
            ballPosition = self.tracker.getPosition()
            return math.sqrt(math.pow(ballPosition[0],2) + math.pow(ballPosition[1],2))


    # setting up top camera
    def setTopCamera(self, widget):
        self.vision.setParam(18,0)
        self.currentCamera = 0


    # setting up bottom camera
    def setBottomCamera(self, widget):
        self.vision.setParam(18,1)
        self.currentCamera = 1


    # protection off to move free
    def protectionOff(self, widget):
        self.motion.setExternalCollisionProtectionEnabled( "All", False )
        print "Protection Off"


    # protection on
    def protectionOn(self, widget):
        self.motion.setExternalCollisionProtectionEnabled( "All", True )
        print "Protection On"
