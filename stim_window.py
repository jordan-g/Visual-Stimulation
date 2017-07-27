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

from perlin_noise import pnoise1

class StimWindow(GameWindow):
    def __new__(self, controller, window_name="Stimulus", display_index=1):
        self.controller = controller

        if display_index == 1:
            # try to use a second display (projector)
            display = DisplayDevice.GetDisplay(DisplayIndex.Second)
        else:
            display = None

        if display == None:
            # fall back to the primary display (monitor)
            display_width = 1280
            display_height = 800
            window_flag = GameWindowFlags.Default

            display = DisplayDevice.GetDisplay(DisplayIndex.Default)
        else:
            display_width = 1280
            display_height = 800
            window_flag = GameWindowFlags.Fullscreen

            # set resolution, bits/pixel, refresh rate
            display.ChangeResolution(display_width, display_height, 16, 60)

        return GameWindow.__new__(self, display_width,
                                        display_height,
                                        GraphicsMode(16, 24, 0, 4), #  bits/pixel, depth bits, stencil bits, FSAA samples
                                        window_name,
                                        window_flag,
                                        display)

    def OnLoad(self, e):
        GameWindow.OnLoad(self, e)

        self.stim = None

        # set target frequency
        self.TargetUpdateFrequency = 60
        self.TargetRenderFrequency = 60

        # set window's background color
        GL.ClearColor(0, 0, 0, 0) 

        # initialize time variable
        self.t = 0

        # initialize started bool
        self.started = False

        # update stim params
        self.update_params()

    def update_params(self):
        print("StimWindow: Updating params.")

        # stop running stim & initialize time variable
        self.controller.running_stim = False
        self.t = 0

        self.distance = self.controller.experiment_params['distance']
        self.resolution = self.controller.experiment_params['resolution']
        self.px_width = int(self.controller.experiment_params['width']*self.ClientRectangle.Width)
        self.px_height = int(self.controller.experiment_params['height']*self.ClientRectangle.Height)
        self.x_offset = int((self.controller.experiment_params['x_offset'])*(self.ClientRectangle.Width - self.px_width))
        self.y_offset = int((1.0 - self.controller.experiment_params['y_offset'])*(self.ClientRectangle.Height - self.px_height))
        self.durations_list = self.controller.config_params['durations_list']
        self.t_total = sum(self.durations_list)
        self.n_stim = len(self.durations_list)

        # reset stim
        self.switch_to_stim(0)

    def change_param(self, param_dimension, change_in_param):
        if self.stim_type == "Grating":
            self.stim.change_velocity(change_in_param)
        ##!! change param for self.stim_type to OKR or use grating
        elif self.stim_type == "Moving Dot":
            if param_dimension == "x":
                self.stim.change_v_x(change_in_param)
            elif param_dimension == "y":
                self.stim.change_v_y(change_in_param)

    def switch_to_stim(self, index):
        self.stim_index = index

        self.get_stim_params(self.stim_index)

        print(self.params)

        print("StimWindow: Switching to {} stim.".format(self.stim_type))

        self.create_stim()

    def get_stim_params(self, index):
        self.stim_type = self.controller.config_params['types_list'][index]
        self.duration = self.controller.config_params['durations_list'][index]
        self.params = self.controller.config_params['parameters_list'][index]

    def create_stim(self):
        if self.n_stim > 0:
            if self.stim_type == "Looming Dot":
                self.stim = LoomingDotStim(self)
            elif self.stim_type == "Moving Dot":
                self.stim = MovingDotStim(self)
            elif self.stim_type == "Grating":
                self.stim = GratingStim(self)
            elif self.stim_type == "Delay":
                self.stim = DelayStim(self)
            elif self.stim_type == "Black Flash":
                self.stim = BlackFlashStim(self)
            elif self.stim_type == "White Flash":
                self.stim = WhiteFlashStim(self)
            elif self.stim_type == "Combined Dots":
                self.stim = CombinedDotStim(self)
            ##!! add a stim type for OKR 
        else:
            self.stim = None

    def OnUpdateFrame(self, e):
        GameWindow.OnUpdateFrame(self, e)

        if self.stim != None:
            if self.controller:
                if self.controller.running_stim:
                    # stim sequence is running
                    if self.controller.begin_stim == True:
                        # beginning of stim sequence
                        print("StimWindow: Begin signal received.")

                        # reset begin stim bool
                        self.controller.begin_stim = False

                        # reset started bool
                        self.started = False

                        # reset stim
                        self.switch_to_stim(0)

                    if self.started == False:
                        # beginning of a new stim
                        print("StimWindow: Starting stim.")

                        # update started bool
                        self.started = True

                        # reset time variable
                        self.t = 0

                        # run stim's start function
                        if self.stim != None:
                            self.stim.start_func()
                    else:
                        # stim has started
                        if self.t < self.stim.duration:
                            # get time since last frame
                            elapsed_time = e.Time*1000.0

                            # update time variable
                            self.t += elapsed_time

                            # run stim's update function
                            if self.stim != None:
                                self.stim.update_func(elapsed_time)
                        else:
                            # stim's duration has finished

                            # run stim's end func
                            if self.stim != None:
                                self.stim.end_func()

                            if self.stim_index != self.n_stim - 1:
                                # we haven't reached the end of the sequence; switch to the next stim
                                self.switch_to_stim(self.stim_index + 1)

                                # reset started bool to trigger the start of the next stim
                                self.started = False
                            else:
                                # we've reached the end; stop the stim sequence
                                self.controller.param_window.start_stop_stim(None, None)
                else:
                    # stim sequence is not running; reset stim if necessary
                    if self.stim_index != 0:
                        self.switch_to_stim(0)

    def OnRenderFrame(self, e):
        if self.stim != None:
            if self.stim_type != "Delay":
                if self.t < self.stim.duration:
                    # stim has started

                    self.MakeCurrent()

                    # clear buffers
                    GL.Clear(ClearBufferMask.ColorBufferBit | ClearBufferMask.DepthBufferBit)

                    # run stim's render function
                    if self.stim != None:
                        self.stim.render_func()

                    # swap buffers
                    self.SwapBuffers()

                    # set the viewport
                    GL.Viewport(self.x_offset, self.y_offset, self.px_width, self.px_height)

class LoomingDot():
    def __init__(self, stim):
        self.stim = stim

    def update_params(self, distance, resolution, params, window_width, window_height): 
        self.resolution = resolution # px/cm
        self.distance   = distance # cm
        self.window_width = window_width
        self.window_height = window_height
        self.max_radius = self.window_width*4 

        self.x        = math.tan(math.radians(params['looming_dot_init_x_pos']))*self.distance*self.resolution/(self.window_width/2)
        self.y        = math.tan(math.radians(params['looming_dot_init_y_pos']))*self.distance*self.resolution/(self.window_height/2)
        self.l_v      = params['l_v']
        self.brightness = params['looming_dot_brightness']

        self.A = self.distance*self.resolution*-self.l_v 

        self.radius_init = 1 # initial radius
        self.radius = self.radius_init

    def update_func(self, time):
        if time < 0:
            # update radius
            self.radius = self.A/time
        else:
            # dot has reached the screen; make sure it covers the whole viewport
            self.radius = self.max_radius

    def draw_circle(self, n_vertices, radius):
        radius_x = radius/(self.window_width/2.0)
        radius_y = radius/(self.window_height/2.0)

        GL.Begin(BeginMode.Polygon)
        for angle in linspace(0, 2*math.pi, n_vertices):
            GL.Vertex2(radius_x*math.sin(angle), radius_y*math.cos(angle))
        GL.End()

    def render_func(self):
        GL.PushMatrix()

        # set dot position
        GL.Translate(self.x, self.y, 0)

        # set dot color
        GL.Color3(self.brightness, self.brightness, self.brightness)

        # draw the dot
        self.draw_circle(30, self.radius)

        GL.PopMatrix()

class LoomingDotStim():
    def __init__(self, stim_window):
        self.stim_window = stim_window
        self.looming_dot = LoomingDot(self)

        # get parameters
        distance = self.stim_window.distance
        resolution = self.stim_window.resolution
        duration = self.stim_window.duration
        params = self.stim_window.params

        # update parameters
        self.update_params(distance, resolution, duration, params)

    def update_params(self, distance, resolution, duration, params):
        print("LoomingDotStim: Updating parameters.")

        self.duration   = duration*1000.0 # ms

        self.looming_dot.update_params(distance, resolution, params, self.stim_window.px_width, self.stim_window.px_height)

        # if a duration of 0 is given, calculate required duration for approaching dot to reach the screen
        if self.duration == 0:
            self.duration = -self.looming_dot.A/self.looming_dot.radius # ms

        print(self.duration)

        self.t_init = -self.duration
        self.t = self.t_init

        self.background_brightness = params['background_brightness']

    def start_func(self):
        pass

    def update_func(self, elapsed_time):    ## Keeps track of time for LoomingDot
        # update t
        self.t += elapsed_time

        self.looming_dot.update_func(self.t)

    def end_func(self):
        pass

    def render_func(self):
        GL.LoadIdentity()
        
        # draw in the viewport background
        GL.Begin(BeginMode.Quads)
        GL.Color3(self.background_brightness, self.background_brightness, self.background_brightness) 
        GL.Vertex2(-1, -1)
        GL.Vertex2(-1, 1)
        GL.Vertex2(1, 1)
        GL.Vertex2(1, -1)
        GL.End()

        self.looming_dot.render_func()

class MovingDot():     
    def __init__(self,stim):
        self.stim = stim

    def update_params(self, distance, resolution, params, window_width, window_height): 
        self.resolution = resolution # px/cm   ## What does this and self.distance do?
        self.distance = distance # cm
        self.window_width = window_width
        self.window_height = window_height

        self.radius   = params['radius'] # px
        self.x_init   = math.tan(math.radians(params['moving_dot_init_x_pos']))*self.distance*self.resolution/(self.window_width/2) # rel units
        self.y_init   = math.tan(math.radians(params['moving_dot_init_y_pos']))*self.distance*self.resolution/(self.window_height/2) # rel units
        self.x = self.x_init
        self.y = self.y_init

        self.v_x = math.tan(math.radians(params['v_x']))*self.distance*self.resolution/((self.window_width/2)*1000.0)
        self.v_y = math.tan(math.radians(params['v_y']))*self.distance*self.resolution/((self.window_height/2)*1000.0)

        print(self.v_x, self.v_y)

        self.brightness = params['moving_dot_brightness']

        self.radius_x = self.radius/(self.window_width/2.0)
        self.radius_y = self.radius/(self.window_height/2.0)

    def update_func(self, elapsed_time):
        self.x += self.v_x*elapsed_time
        self.y += self.v_y*elapsed_time
        
    def draw_circle(self, n_vertices):
        GL.Begin(BeginMode.Polygon)
        for angle in linspace(0, 2*math.pi, n_vertices):
            GL.Vertex2(self.radius_x*math.sin(angle), self.radius_y*math.cos(angle))
        GL.End()

    def change_v_x(self, change_in_v_x):
        self.v_x = change_in_v_x*self.max_v_init

    def change_v_y(self, change_in_v_y):
        self.v_y += change_in_v_y*self.max_v_init

    def render_func(self):
        GL.PushMatrix()

        # set dot position
        GL.Translate(self.x, self.y, 0)

        # set dot color
        GL.Color3(self.brightness, self.brightness, self.brightness)

        # draw the dot
        self.draw_circle(30)

        GL.PopMatrix()


class MovingDotStim():
    def __init__(self, stim_window):
        self.stim_window = stim_window

        self.moving_dot = MovingDot(self)

        # get parameters
        distance = self.stim_window.distance
        resolution = self.stim_window.resolution
        duration = self.stim_window.duration
        params = self.stim_window.params

        # update parameters
        self.update_params(distance, resolution, duration, params)

    def update_params(self, distance, resolution, duration, params):
        print("MovingDotStim: Updating parameters.")

        self.duration = duration*1000.0 # ms

        self.moving_dot.update_params(distance, resolution, params, self.stim_window.px_width, self.stim_window.px_height)

        ## if a duration of 0 is given, calculates duration for moving dot to move across screen
        if self.duration == 0:
            if self.moving_dot.v_x != 0:
                if self.moving_dot.v_x > 0:
                    self.duration = (1.2 - self.moving_dot.x_init)/self.moving_dot.v_x
                else:
                    self.duration = (-1.2 - self.moving_dot.x_init)/self.moving_dot.v_x
            else:
                if self.moving_dot.v_y > 0:
                    self.duration = (1.2 - self.moving_dot.y_init)/self.moving_dot.v_y
                else:
                    self.duration = (-1.2 - self.moving_dot.y_init)/self.moving_dot.v_y
        
        self.t_init = -self.duration # ms
        self.t = self.t_init

        self.background_brightness = params['background_brightness']

    def start_func(self):
        pass

    def update_func(self, elapsed_time):
        # update t
        self.t += elapsed_time

        self.moving_dot.update_func(elapsed_time)

    def end_func(self):
        pass

    def render_func(self):
        GL.LoadIdentity()

        # draw in the viewport background
        GL.Begin(BeginMode.Quads)
        GL.Color3(self.background_brightness, self.background_brightness, self.background_brightness)   
        GL.Vertex2(-1, -1)
        GL.Vertex2(-1, 1)
        GL.Vertex2(1, 1)
        GL.Vertex2(1, -1)
        GL.End()

        self.moving_dot.render_func()

class CombinedDotStim():
    def __init__(self, stim_window):
        self.stim_window = stim_window

        self.moving_dot = MovingDot(self)
        self.looming_dot = LoomingDot(self)

        # get parameters    ## I only need one get params because there is only one window
        distance = self.stim_window.distance
        resolution = self.stim_window.resolution
        duration = self.stim_window.duration
        params = self.stim_window.params

        # update parameters
        self.update_params(distance, resolution, duration, params)
        
    def update_params(self, distance, resolution, duration, params):
        print("CombinedDotStim: Updating parameters.")

        self.duration = duration*1000.0 # ms

        ## if a duration of 0 is given, calculates duration for moving dot to move across screen
        if self.duration == 0:
            if self.moving_dot.v_x != 0:
                if self.moving_dot.v_x > 0:
                    self.duration = (1.2 - self.moving_dot.x_init)/self.moving_dot.v_x
                else:
                    self.duration = (-1.2 - self.moving_dot.x_init)/self.moving_dot.v_x
            else:
                if self.moving_dot.v_y > 0:
                    self.duration = (1.2 - self.moving_dot.y_init)/self.moving_dot.v_y
                else:
                    self.duration = (-1.2 - self.moving_dot.y_init)/self.moving_dot.v_y

        self.background_brightness = params['background_brightness']

        print(self.duration)

        self.moving_dot.update_params(distance, resolution, params, self.stim_window.px_width, self.stim_window.px_height)
        self.looming_dot.update_params(distance, resolution, params, self.stim_window.px_width, self.stim_window.px_height)
        
        self.t_init = -self.duration # ms
        self.t = self.t_init

    def start_func(self):
        pass

    def update_func(self, elapsed_time):
        # update t
        self.t += elapsed_time

        self.looming_dot.update_func(self.t)
        self.moving_dot.update_func(elapsed_time)

    def end_func(self):
        pass

    def render_func(self):
        GL.LoadIdentity()

        # draw in the viewport background
        GL.Begin(BeginMode.Quads)
        GL.Color3(self.background_brightness, self.background_brightness, self.background_brightness)
        GL.Vertex2(-1, -1)
        GL.Vertex2(-1, 1)
        GL.Vertex2(1, 1)
        GL.Vertex2(1, -1)
        GL.End()

        self.looming_dot.render_func()
        self.moving_dot.render_func()

class GratingStim():
    def __init__(self, stim_window):
        self.stim_window = stim_window

        # get parameters
        distance = self.stim_window.distance
        resolution = self.stim_window.resolution
        duration = self.stim_window.duration
        params = self.stim_window.params

        # update parameters
        self.update_params(distance, resolution, duration, params)

    def update_params(self, distance, resolution, duration, params):
        print("GratingStim: Updating parameters.")

        self.redraw = False

        self.resolution = resolution # px/cm
        self.distance = distance # cm
        self.duration = duration*1000.0 # ms

        self.rad_width = math.atan2(self.stim_window.px_width/2.0, self.distance*self.resolution)*2

        print("rad width", self.rad_width)

        self.frequency = params['frequency']*(180.0/math.pi)*self.rad_width/self.stim_window.px_width
        self.init_phase = params['init_phase']*(math.pi/180.0)*self.stim_window.px_width/self.rad_width
        self.velocity_init = params['velocity']*(math.pi/180.0)*self.stim_window.px_width/self.rad_width/1000.0
        self.velocity = self.velocity_init
        self.contrast = params['contrast']
        self.brightness = params['brightness']
        self.angle = params['angle']

        self.t_init = -self.duration*1000.0 # ms
        self.t = self.t_init

        self.phase = self.init_phase

        # set redraw bool
        self.redraw = True

    def genTexture(self):
        # generate the grating texture
        for x in range(self.stim_window.px_width):
            w = int(round((self.contrast*math.sin(self.frequency*x*2*math.pi - self.phase*self.frequency*2*math.pi) + 1.0)*self.brightness*255.0/2.0))
            self.grating[4*x] = Byte(w)
            self.grating[4*x+1] = Byte(w)
            self.grating[4*x+2] = Byte(w)
            self.grating[4*x+3] = Byte(255)

    def initTexture(self):
        # generate the texture
        self.grating = Array.CreateInstance(Byte, self.stim_window.px_width * 4)
        self.genTexture()

        # create the texture
        self.texture = GL.GenTexture()
        GL.BindTexture(TextureTarget.Texture2D, self.texture)

        GL.TexEnv( TextureEnvTarget.TextureEnv, TextureEnvParameter.TextureEnvMode,  int(TextureEnvMode.Modulate) )
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMagFilter, int(TextureMagFilter.Linear))
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMinFilter, int(TextureMagFilter.Linear))

        GL.TexImage2D(TextureTarget.Texture2D, 0, PixelInternalFormat.Rgb, self.stim_window.px_width, 1, 0, PixelFormat.Rgba, PixelType.UnsignedByte, self.grating)

    def change_velocity(self, change_in_velocity):
        self.velocity = change_in_velocity*self.velocity_init

    def start_func(self):
        pass

    def update_func(self, elapsed_time):
        # update phase
        self.phase += self.velocity*elapsed_time
        self.t += elapsed_time

        # set redraw bool
        self.redraw = True

    def end_func(self):
        pass

    def render_func(self):
        GL.LoadIdentity()

        # set projection
        GL.MatrixMode(MatrixMode.Projection)
        GL.Ortho(0.0, self.stim_window.px_width, 0.0, self.stim_window.px_height, -1.0, 1.0)

        if self.redraw:
            # set color
            GL.Color4(Color.White)

            # redraw the texture
            self.initTexture()

            # reset redraw bool
            self.redraw = False

        # enable texture mode
        GL.Enable(EnableCap.Texture2D)

        GL.PushMatrix()
        GL.Translate(self.stim_window.px_width/2, self.stim_window.px_height/2, 0)
        GL.Rotate(self.angle, 0, 0, 1)

        # draw texture quad
        GL.Begin(BeginMode.Quads)
        GL.TexCoord2(1.0, 1.0)
        GL.Vertex2(self.stim_window.px_width, self.stim_window.px_height)
        GL.TexCoord2(0, 1.0)
        GL.Vertex2(-self.stim_window.px_width, self.stim_window.px_height)
        GL.TexCoord2(0, 0)
        GL.Vertex2(-self.stim_window.px_width, -self.stim_window.px_height)
        GL.TexCoord2(1.0, 0)
        GL.Vertex2(self.stim_window.px_width, -self.stim_window.px_height)
        GL.End()

        GL.PopMatrix()

        # disable texture mode
        GL.Disable(EnableCap.Texture2D)

##!!Need class OKR

class DelayStim():
    def __init__(self, stim_window):
        self.stim_window = stim_window

        # get parameters
        distance = self.stim_window.distance
        resolution = self.stim_window.resolution
        duration = self.stim_window.duration
        params = self.stim_window.params

        # update parameters
        self.update_params(distance, resolution, duration, params)

    def update_params(self, distance, resolution, duration, params):
        print("DelayStim: Updating parameters.")

        self.duration = duration*1000.0 # ms

    def start_func(self):
        pass

    def update_func(self, elapsed_time):
        pass

    def end_func(self):
        pass

    def render_func(self):
        pass

class BlackFlashStim():
    def __init__(self, stim_window):
        self.stim_window = stim_window

        # get parameters
        distance = self.stim_window.distance
        resolution = self.stim_window.resolution
        duration = self.stim_window.duration
        params = self.stim_window.params

        # update parameters
        self.update_params(distance, resolution, duration, params)

    def update_params(self, distance, resolution, duration, params):
        print("BlackFlashStim: Updating parameters.")

        self.duration = duration*1000.0 # ms

    def start_func(self):
        pass

    def update_func(self, elapsed_time):
        pass

    def end_func(self):
        pass

    def render_func(self):
        GL.LoadIdentity()

        # draw in the viewport background
        GL.Begin(BeginMode.Quads)
        GL.Color4(Color.Black)
        GL.Vertex2(-1, -1)
        GL.Vertex2(-1, 1)
        GL.Vertex2(1, 1)
        GL.Vertex2(1, -1)
        GL.End()

class WhiteFlashStim():
    def __init__(self, stim_window):
        self.stim_window = stim_window

        # get parameters
        distance = self.stim_window.distance
        resolution = self.stim_window.resolution
        duration = self.stim_window.duration
        params = self.stim_window.params

        # update parameters
        self.update_params(distance, resolution, duration, params)

    def update_params(self, distance, resolution, duration, params):
        print("WhiteFlashStim: Updating parameters.")

        self.duration = duration*1000.0 # ms

    def start_func(self):
        pass

    def update_func(self, elapsed_time):
        pass

    def end_func(self):
        pass

    def render_func(self):
        GL.LoadIdentity()

        # draw in the viewport background
        GL.Begin(BeginMode.Quads)
        GL.Color4(Color.White)
        GL.Vertex2(-1, -1)
        GL.Vertex2(-1, 1)
        GL.Vertex2(1, 1)
        GL.Vertex2(1, -1)
        GL.End()


# --- HELPER FUNCTIONS --- #

# generate a linspace
def linspace(start, stop, n):
    if n == 1:
        yield stop
        return
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i
