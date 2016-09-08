import random
import pygame
import time
import socket
import numpy as np


# import gtk to get Dual Screen info
# import gtk


from FeedbackBase.PygameFeedback import PygameFeedback
from utils import StimulationsCodes


class CalibrationCursorArrow(PygameFeedback):

    TRIAL_START = 'T0' #beginning of a trial at 0 sec
    CUE_START = 'S0' #beginning of cue presentation at 2 sec
    CUE_LEFT = 'S1' #class of imagery: left arrow for left hand
    CUE_RIGHT = 'S2' #class of imagery: right arrow for right hand
    CUE_FOOT = 'S3' #class of imagery: up arrow for right foot
    CUE_TONGUE = 'S4' #class of imagery: down arrow for tongue
    BREAK_START = 'T1' #beginning fo break at 6 sec

    INIT_CALIBRATION = 200 #init of the feedback
    CALIBRATION_STATUS_PLAY = 210 #feedback status changed to play
    CALIBRATION_STATUS_PAUSE  = 211 #feedback status changed to pause
    CALIBRATION_STATUS_QUIT  = 254 #quit feedback

    PRERUN_COUNTDOWN = 300

    def init(self):
        #print "Feedback successfully loaded."
        self.logger.debug('Feedback successfully loaded')

        # self._ov_tcp_tag_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self._ov_tcp_tag_socket.connect((self.ov_tcp_tag_host, self.ov_tcp_tag_port))

        # PyGame init style
        PygameFeedback.init(self)

        self.screenPos = [1400,20]
        self.screenSize = [1000,800]
        # screen = gtk.window()
        # if screen.get_n_monitors == 2 :
        #     second_monitor_info = screen.get_monitor_geometry(1)
        #     self.screenPos = [second_monitor_info.x,second_monitor_info.y]
        #     self.screenSize = [second_monitor_info.width,second_monitor_info.height]
        #socket init for send udp
        #self._udp_markers_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


        self.logger.debug("on_init")
        self.caption = 'Motor Imagery Calibration'
        # self.send_udp(str(self.INIT_CALIBRATION))

        # events Durations
        self.durationPerTrial = 8000 #8 seconds
        self.trials = 75 #Number of trials per run / class
        self.pauseAfter = 15 #Number of trials required before a pause
        self.pauseDuration = 20000 #20 seconds
        self.cueDuration = 4000 #4seconds
        self.preCueDuration = 2000 #2 seconds
        self.postCueDuration = 2000 #2 seconds
        self.countdownFrom = 2  # PRE_RUN Duration in seconds
        self.stopAt = 5 #Number of blocks per run
        self.blocks = 0


        #pygame feedback attiributes
        self.availableDirections = ['left', 'right','foot']
        self.FPS = 50
        self.fullscreen = False
        self.screenWidth = 1000
        self.screenHeight = 700

        self.pause = False
        self.quit = False
        self.quitting = False

        #ticks boolean variables
        self.countdown = True
        self.fixationCross = False
        self.cue = False
        self.postCue = False

        self.showsPause, self.showsShortPause = False, False

        self.elapsed, self.cueElapsed, self.countdownElapsed, \
        self.preCueElapsed, self.postCueElapsed,self.pauseElapsed = 0, 0, 0, 0, 0, 0
        self.completedTrials = 0

        self.f = 0

        self.resized = False
        self.pos = 0
        self.targetDirection = 0

        self.arrowPointlist = [(.5, 0), (.5, .33), (1, .33), (1, .66), (.5, .66), (.5, 1), (0, .5)]
        self.arrowColor = (127, 127, 127)
        self.borderColor = self.arrowColor
        self.backgroundColor = (64, 64, 64)
        self.cursorColor = (100, 149, 237)
        self.fontColor = self.cursorColor
        self.countdownColor = (237, 100, 148)

        self.borderWidthRatio = 0.4

                # How many degrees counter clockwise to turn an arrow pointing to the
        # left to point at left, right and foot
        self.LEFT, self.RIGHT, self.UP, self.DOWN = 'left', 'right', 'foot', 'tonge'
        self.directions = {self.LEFT: 0, self.RIGHT: 180, self.UP: 270, self.DOWN: 90}

        #Random sequence of cues
        self.cueSequence = list(np.repeat([0,1,2],self.pauseAfter / len(self.availableDirections)))
        random.shuffle(self.cueSequence)

    def pre_mainloop(self):
        PygameFeedback.pre_mainloop(self)
        self.logger.debug("on_play")
        # self.send_udp(str(self.CALIBRATION_STATUS_PLAY))
        #self.send_ov_tcp_tag(StimulationsCodes.OpenViBE_stimulation['OVTK_StimulationId_ExperimentStart'])

    def post_mainloop(self):
        self.logger.debug("on_quit")
        PygameFeedback.post_mainloop(self)
        self.send_udp(str(self.CALIBRATION_STATUS_QUIT))

    def init_graphics(self):
        """
        Initialize the surfaces and fonts depending on the screen size

        """

        #screen
        self.screen = pygame.display.get_surface()

        (self.screenWidth, self.screenHeight) = (self.screen.get_width(), self.screen.get_height())
        self.size = min(self.screen.get_height(), self.screen.get_height())
        self.borderWidth = int(self.size * self.borderWidthRatio/2)
        self.offsetX = (self.screenWidth-self.size)/2
        self.s1 = self.size/2-self.borderWidth
        self.s2 = self.borderWidth

        # arrow
        scale = self.size / 3
        scaledArrow = [(P[0]*scale, P[1]*scale) for P in self.arrowPointlist]
        self.arrow = pygame.Surface((scale,scale))
        self.arrowRect = self.arrow.get_rect(center=self.screen.get_rect().center)
        self.arrow.fill(self.backgroundColor)
        pygame.draw.polygon(self.arrow, self.arrowColor, scaledArrow)
        print 'Trial # %s' %(self.completedTrials)
        print '////INIT DIRECTION %s' %( self.directions[self.availableDirections[
                self.cueSequence[self.completedTrials]]])
        self.arrow = pygame.transform.rotate(self.arrow, self.directions[self.availableDirections[
                self.cueSequence[self.completedTrials]]])

        # curosr
        scale = self.size / 5
        self.cursor = pygame.Surface((scale,scale))
        self.cursorRect = self.cursor.get_rect(center = self.screen.get_rect().center)
        self.cursor.set_colorkey((0,0,0))
        pygame.draw.line(self.cursor, self.cursorColor,(0,scale/2), (scale,scale/2),10)
        pygame.draw.line(self.cursor, self.cursorColor,(scale/2,0), (scale/2,scale),10)


        #background + border
        self.background = pygame.Surface((self.screen.get_width(),self.screen.get_height()))
        self.backgroundRect = self.background.get_rect(center = self.screen.get_rect().center)
        self.background.fill(self.borderColor)
        self.border = pygame.Surface((self.size,self.size))
        self.border.fill(self.borderColor)
        self.borderRect = self.border.get_rect(center=self.screen.get_rect().center)
        self.inner = pygame.Surface((self.size-2*self.borderWidth, self.size-2*self.borderWidth))
        self.inner.fill(self.backgroundColor)
        self.innerRect = self.inner.get_rect(center=self.screen.get_rect().center)

        # if self.resized :
        #     self.resized = False
        #     target = self.availableDirections[self.targetDirection]
        #     self.pos = (1.0*self.size/self.size_old) * self.pos
        #     #self.update_cursor()
        #     self.myarrow = pygame.transform.rotate(self.arrow, self.directions[target])
        #     self.myarrowRect = self.myarrow.get_rect(center=self.screen.get_rect().center)
        #     self.draw_all()

    def pre_run(self):
        """
        pre run tick:
        """
        if self.countdownElapsed == 0:
            self.send_udp(str(self.PRERUN_COUNTDOWN))

        self.countdownElapsed += self.elapsed

        if self.countdownElapsed >= self.countdownFrom * 1000:
            self.countdown = False
            self.fixationCross = True
            self.countdownElapsed = 0
            # self.arrow = pygame.transform.rotate(self.arrow, self.directions[self.availableDirections[
            #          self.cueSequence[self.completedTrials]]])
            return

        t = (self.countdownFrom * 1000 - self.countdownElapsed) / 1000
        self.draw_init()
        self.do_print(str(t),self.countdownColor, self.size/3, True)

    def pre_cue(self):

        self.fixationCross = True

        if self.preCueElapsed == 0 :
            self.send_udp(str(self.TRIAL_START))

        self.preCueElapsed += self.elapsed
        if self.preCueElapsed >= self.preCueDuration :
            self.fixationCross = False
            self.cue = True
            self.postCue = False
            self.preCueElapsed = 0

            # print 'Current DIRECTION %s --- Current TRIAL %s' % (self.directions[self.availableDirections[
            #         self.cueSequence[self.completedTrials]]], self.completedTrials)
            # # self.arrow = pygame.transform.rotate(self.arrow, self.directions[self.availableDirections[
            # #         self.cueSequence[self.completedTrials]]]
            # #                                      )
            return

        self.screen.blit(self.background, self.backgroundRect)
        self.screen.blit(self.border, self.borderRect)
        self.screen.blit(self.inner, self.innerRect)
        self.screen.blit(self.cursor, self.cursorRect)
        pygame.display.update()

    def on_cue(self):

        self.cue = True
        self.draw_all()

        if self.cueElapsed == 0 :
            print "MARKER SENT: %s" %(self.directions[self.availableDirections[self.cueSequence[self.completedTrials]]])
            if self.cueSequence[self.completedTrials] == 0:
                self.send_udp(str(self.CUE_LEFT))

            elif self.cueSequence[self.completedTrials] == 1:
                self.send_udp(str(self.CUE_RIGHT))

            elif self.cueSequence[self.completedTrials] == 2:
                self.send_udp(str(self.CUE_FOOT))

        self.cueElapsed += self.elapsed
        if self.cueElapsed >= self.cueDuration :
            self.cue = False
            self.postCue = True
            self.fixationCross = False
            self.cueElapsed = 0
            self.completedTrials += 1
            return

        if self.cueElapsed == 0 :
            print "MARKER SENT: %s" %(self.directions[self.availableDirections[self.cueSequence[self.completedTrials]]])
            if self.cueSequence[self.completedTrials] == 0:
                self.send_udp(str(self.CUE_LEFT))

            elif self.cueSequence[self.completedTrials] == 1:
                self.send_udp(str(self.CUE_RIGHT))

            elif self.cueSequence[self.completedTrials] == 2:
                self.send_udp(str(self.CUE_FOOT))

    def post_cue(self):

        self.postCue = True
        self.draw_init()
        pygame.display.update()

        if self.postCueElapsed == 0 :
            self.send_udp(str(self.BREAK_START))

        self.postCueElapsed += self.elapsed

        if self.postCueElapsed >= self.postCueDuration and self.completedTrials < self.pauseAfter :
            self.postCue = False
            self.cue = False
            self.fixationCross = True
            self.postCueElapsed = 0


            print 'Completed Trials %s ' %(self.completedTrials)
            print '-------'
            print 'CueSequence %s' %(self.cueSequence[self.completedTrials])
            print 'Avaible direction %s' %(self.availableDirections[self.cueSequence[self.completedTrials]])
            print 'Current Direction %s' %(self.directions[self.availableDirections[self.cueSequence[self.completedTrials]]])
            print '************'
            #Rotate Arrow
            #directions[availbeDirection[targetdirection]]
            currenctDirection = self.directions[self.availableDirections[
                self.cueSequence[self.completedTrials-1]]]

            self.arrow = pygame.transform.rotate(self.arrow, self.directions[self.availableDirections[
                self.cueSequence[self.completedTrials]]]-currenctDirection)

        elif self.completedTrials == self.pauseAfter :
                #print 'prepare for pause'
                self.postCue = False
                self.pause = True
                self.fixationCross = False


                return

    def post_run(self):
        pass

    def short_pause(self):


        if self.pauseElapsed == 0 :
            self.send_udp(str(self.CALIBRATION_STATUS_PAUSE))

        self.pauseElapsed += self.elapsed

        if self.pauseElapsed >= self.pauseDuration :
            self.fixationCross = True
            self.cue = False
            self.postCue = False
            self.pauseElapsed = 0
            self.completedTrials = 0
            self.blocks += 1
            random.shuffle(self.cueSequence)
            self.init_graphics()
            self.quit = True
            if self.blocks >= self.stopAt :
                self.quit = True
            return


        self.do_print("Short Break...", self.fontColor)

    def draw_all(self):
        """
        Executes the drawing of all feedback components
        """
        self.screen.blit(self.background, self.backgroundRect)
        self.screen.blit(self.border, self.borderRect)
        self.screen.blit(self.inner, self.innerRect)
        self.screen.blit(self.arrow, self.arrowRect)
        self.screen.blit(self.cursor, self.cursorRect)
        pygame.display.update()

    def draw_init(self):
        """
        Draws the initial screens
        """
        self.screen.blit(self.background, self.backgroundRect)
        self.screen.blit(self.border, self.borderRect)
        self.screen.blit(self.inner, self.innerRect)

    def play_tick(self):

        if self.countdown:
            #print "PRE_RUN()"
            self.pre_run()
        elif self.fixationCross :
            #print "PRE_CUE()"
            self.pre_cue()
        elif self.cue :
            #print "CUE()"
            self.on_cue()
        elif self.postCue :
            #print "POST_CUE()"
            self.post_cue()
        elif self.pause:
            #print "SHORT_PAUSE()"
            self.short_pause()

        elif self.quit :
            self.send_udp(str(self.CALIBRATION_STATUS_PAUSE))
            self.quit_pygame()

    def do_print(self, text, color=None, size=None, superimpose=False):
        """
        Print the given text in the given color and size on the screen.
        If text is a list, multiple items will be used, one for each list entry.
        """
        if not color:
            color = self.fontColor
        if not size:
            size = self.size/10

        font = pygame.font.Font(None, size)
        if not superimpose:
            self.draw_init()

        if type(text) is list:
            height = pygame.font.Font.get_linesize(font)
            top = -(2*len(text)-1)*height/2
            for t in range(len(text)):
                surface = font.render(text[t], 1, color)
                self.screen.blit(surface, surface.get_rect(midtop=(self.screenWidth/2, self.screenHeight/2+top+t*2*height)))
        else:
            surface = font.render(text, 1, color)
            self.screen.blit(surface, surface.get_rect(center=self.screen.get_rect().center))
        pygame.display.update()


if __name__ == '__main__':
    ca = CalibrationCursorArrow(None)
    ca.on_init()
    ca.on_play()