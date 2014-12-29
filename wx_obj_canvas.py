import wx
#import sys

from wx import glcanvas

# The Python OpenGL package can be found at
# http://PyOpenGL.sourceforge.net/
from OpenGL.GL import * #@UnusedWildImport
from OpenGL.GLU import * #@UnusedWildImport

# IMPORT OBJECT LOADER
from objloader import OBJ

class MyCanvasBase(glcanvas.GLCanvas):

    def __init__(self, parent):

        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.init = False
        # initial mouse position
        self.rx, self.ry = self.last_rx,self.last_ry = (0,0)
        self.tx, self.ty = self.last_tx, self.last_ty = (0,0)
        self.size = None
        self.zpos = -3
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLMouseUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnScroll)
        
    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def OnScroll(self, event):
        if event.GetWheelRotation() > 0:
            self.zpos += 1
        else:
            self.zpos -= 1
        self.Refresh(True)
        
    def OnSize(self, event):
        size = self.size = self.GetClientSize()
        '''
        if self.GetContext():
            self.SetCurrent()
        '''
        if self.init == True:
            glViewport(0, 0, size.width, size.height)
        event.Skip()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()
        
    def OnLMouseDown(self, evt):
        self.SetFocus()
        self.CaptureMouse()
        self.last_rx, self.last_ry = evt.GetPosition()

    def OnLMouseUp(self, evt):
        self.Refresh(True)
        if self.HasCapture():
            self.ReleaseMouse() 
            
    def OnRMouseDown(self, evt):
        self.SetFocus()
        self.CaptureMouse()
        self.last_tx, self.last_ty = evt.GetPosition()

    def OnRMouseUp(self, evt):
        self.Refresh(True)
        if self.HasCapture():
            self.ReleaseMouse() 

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            i,j= evt.GetPosition()
            self.rx += i-self.last_rx
            self.ry += j-self.last_ry
            self.last_rx,self.last_ry= (i,j)
            self.Refresh(False)
        elif evt.Dragging() and evt.RightIsDown():
            i,j= evt.GetPosition()
            self.tx += i-self.last_tx
            self.ty -= j-self.last_ty
            self.last_tx,self.last_ty= (i,j)
            self.Refresh(False)

class GL_Canvas(MyCanvasBase):    
    def InitGL(self):
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  (1,1,1))
        glLightfv(GL_LIGHT0, GL_AMBIENT,  (0.2,0.2,0.2))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0,1.0,1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, (3,3, 0.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded
        
        self.obj = OBJ("small_sphere.obj", swapyz=True)
              
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluPerspective(90, 800.0/600.0, 1, 100.0)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        
    def load_obj(self, obj_file):  
        self.obj = OBJ(obj_file, swapyz=True)
        self.Refresh(True)
        
    def adj_amb_light(self, v):
        glLightfv(GL_LIGHT0, GL_AMBIENT,  (v,v,v))
        self.Refresh(True)
        
    def adj_light_pos(self, v):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glLightfv(GL_LIGHT0, GL_POSITION, (3, 3,-v))
        self.Refresh(True)
    
    def adj_dif_light(self, v):
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  (v,v,v))
        self.Refresh(True)
        
    def OnDraw(self):
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        if self.size is None:
            self.size = self.GetClientSize()
        w, h = self.size
        w = max(w, 1.0)
        h = max(h, 1.0)
        xScale = 180.0 / w
        yScale = 180.0 / h
        
        glTranslate(float(self.tx*xScale)/20.0, float(self.ty*yScale)/20.0, self.zpos)
        glRotatef(float(self.rx*xScale), 0.0, 1.0, 0.0);
        glRotatef(float(self.ry*yScale), 1.0, 0.0, 0.0);
        
        glCallList(self.obj.gl_list)
        self.SwapBuffers()

