from gi.repository import Gtk
import config as c
import ball as b


class BallTracker:
        
        """Represents Nao Controller GUI

        params: glade_file_path - path:string
        """
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

        ### Destroy GUI
        def destroy(self, widget):
            print "destroyed"
            Gtk.main_quit()

        ### Protection On
        def protectionOn(self, widget):
            print "Protection On"
            b.Nao().protectionOn()

        ### Protection Off
        def protectionOff(self, widget):
            print "Protection Off"
            b.Nao().protectionOff()

        ### Nao Search Ball
        def searchBall(self, widget):
            print "Searching ball..."
            b.Nao().searchBall()

        ### Nao Has Ball?
        def hasBall(self, widget):
            b.Nao().hasBall()

        ### Nao Move to Ball
        def moveToBall(self, widget):
            print "go go go"
            b.Nao().walkToBall()

