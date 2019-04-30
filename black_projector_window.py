from __future__ import division

import clr
clr.AddReferenceToFile("OpenTK.dll")
clr.AddReference("System.Drawing")

import math
import random
import time
import array

from System import Array, Byte, Int32
from System.Drawing import Bitmap, Rectangle, Color

from OpenTK import *
from OpenTK.Graphics import *
from OpenTK.Graphics.OpenGL import *
from OpenTK.Input import *

import threading

class BlackProjectorWindow(GameWindow):
    def __new__(self, controller):
        self.controller = controller

        # try to use a second display (projector)
        display = DisplayDevice.GetDisplay(DisplayIndex.Second)

        if display is not None:
            display_width = 1280
            display_height = 800
            window_flag = GameWindowFlags.Fullscreen

            # set resolution, bits/pixel, refresh rate
            display.ChangeResolution(display_width, display_height, 8, 60)

            return GameWindow.__new__(self, display_width,
                                            display_height,
                                            GraphicsMode(8, 24, 0, 0), #  bits/pixel, depth bits, stencil bits, FSAA samples
                                            "",
                                            window_flag,
                                            display)

    def OnLoad(self, e):
        GameWindow.OnLoad(self, e)

        # set target frequency
        self.TargetUpdateFrequency = 60
        self.TargetRenderFrequency = 60

        # set window's background color
        GL.ClearColor(0, 0, 0, 0) 

    def OnUpdateFrame(self, e):
        GameWindow.OnUpdateFrame(self, e)

    def OnRenderFrame(self, e):
        # clear buffers
        GL.Clear(ClearBufferMask.ColorBufferBit | ClearBufferMask.DepthBufferBit)

        # swap buffers
        self.SwapBuffers()