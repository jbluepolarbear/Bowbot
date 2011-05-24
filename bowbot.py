import time
import math
import Queue
import pythoncom
import pyHook

from win32com.client import Dispatch
import win32api
import win32con

import ScreenScrapper

keys = {}
running = True
space = False

def OnKeyboardEvent(event):
    global keys
    global running
    global space
##    print 'MessageName:',event.MessageName
##    print 'Message:',event.Message
##    print 'Time:',event.Time
##    print 'Window:',event.Window
##    print 'WindowName:',event.WindowName
##    print 'Ascii:', event.Ascii, chr(event.Ascii)
##    print 'Key:', event.Key
##    print 'KeyID:', event.KeyID
##    print 'ScanCode:', event.ScanCode
##    print 'Extended:', event.Extended
##    print 'Injected:', event.Injected
##    print 'Alt', event.Alt
##    print 'Transition', event.Transition
##    print '---'

    if event.Key == 'Escape':
        running = False

    if event.Key == 'Space':
        space = True

    keys[event.Key] = True

# return True to pass the event to other handlers
    return True

"""
these four functions borrowed from slowfrog (aka Laurent Vaucher)
"""
def move_to(x1, y1):
    """Moves the mouse pointer to a given position on screen"""
    win32api.SetCursorPos((x1, y1))

def slide_to(x1, y1, delta_t=1, step_t=0.05):
    """Gently slides the mouse pointer from its current position to a new destination"""
    count = int(math.floor(delta_t / step_t))
    count = 1 if count < 1 else count
    (x, y) = win32api.GetCursorPos()
    for i in xrange(count + 1):
        ratio = i / count
        xi = int(x + (x1 - x) * ratio)
        yi = int(y + (y1 - y) * ratio)
        win32api.SetCursorPos((xi, yi))
        time.sleep(step_t)

def click_at(x=None, y=None, delta_t=0.02):
    """Generates a click at a given position by sending a left-button down event, followed after a
    small delay by a left-button up event"""
    if ((x is not None) and (y is not None)):
        win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(delta_t)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def drag_drop(x0, y0, x1, y1, delta_t=0.1):
    """Does a drag and drop, which is essentially the same as a click, but with the mouse pointer
    changing position between the button-down and button-up event"""
    win32api.SetCursorPos((x0, y0))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    #time.sleep(delta_t)
    #win32api.SetCursorPos((x1, y1))
    slide_to(x1,y1,0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    time.sleep(delta_t)



def Rad2Deg( x ):
    return x * 57.295779
def Deg2Rad( x ):
  return 0.017453 * x

class BowBot(object):
    def __init__(self):
        self.running = True
        self.runGrouping = False
        self.eventQueue = Queue.Queue()
        self.screenScrapper = ScreenScrapper.ScreenScraper(True)
        self.timerStart = 0
        self.timerEnd = 0
        self.entities = None
        self.log = file('log.txt','w')
        self.toggle = True

    def update(self):
        global keys
        global space

        keys = {}
        pythoncom.PumpWaitingMessages()

        try:
            if space:
                self.screenScrapper.CreateBase()
                self.runGrouping = True
                self.timerStart = time.clock()
                space = False
        except:
            pass

        if self.runGrouping:
            self.timerEnd = time.clock()

            if self.timerEnd - self.timerStart > 0.3:
                self.screenScrapper.CreateContrast()
                self.entities = self.screenScrapper.CreateEntities()
                self.timerStart = time.clock()

        if self.entities is not None and len(self.entities) > 0:
            closestEntity = self.entities[0]
            for x in self.entities:
                if x.center[0] < closestEntity.center[0]:
                    closestEntity = x

            g = 23
            v = 408 / math.sqrt( 2 * 107 / g )
            y = closestEntity.center[1]-405
            x = closestEntity.center[0]-210

            self.log.write('y: '+str(y)+'\n')
            print 'y: '+str(y)
            self.log.write('x: '+str(x)+'\n')
            print 'x: '+str(x)

            #l = math.sqrt(y**2 + x**2)

            v2 = v**2
            temp = v2**2 - g*(g*x**2 + 2*y*v2)
            if temp < 1:
                temp = 1
            sqp = math.sqrt(temp)
            tm = math.atan((v2 + sqp)/(g*x))
            tm2 = math.atan((v2 - sqp)/(g*x))

            self.log.write('tm: '+str(tm)+'\n')
            self.log.write('angle: '+str(Rad2Deg(tm))+'\n')
            self.log.write('tm2: '+str(tm2)+'\n')
            self.log.write('angle2: '+str(Rad2Deg(tm2))+'\n')
            self.log.write('\n')

##            if self.toggle:
##                drag_drop(210, 405, 210-84*math.cos(tm), 405-84*math.sin(-tm), 0.25)
##            else:
            #angleSub = 12 #level 1
            #angleSub = 27 #level 2
            angleSub = 17
            drag_drop(210, 405, 210-84*math.cos(tm2-Deg2Rad(angleSub)), 405-84*math.sin(-tm2-Deg2Rad(angleSub)), 0.25)
            self.toggle = not self.toggle
            #drag_drop(210, 405, 210-84*(x/l), 405-84*(y/l)+x**2/100, 0.25)


if __name__ == '__main__':
    # create a hook manager
    hm = pyHook.HookManager()
    # watch for all mouse events
    hm.KeyAll = OnKeyboardEvent
    # set the hook
    hm.HookKeyboard()

    bowbot = BowBot()

    while running:
        bowbot.update()
