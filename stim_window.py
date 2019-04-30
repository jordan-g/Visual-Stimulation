from __future__ import division

import clr
clr.AddReferenceToFile("OpenTK.dll")
clr.AddReference("System.Drawing")

import math
import random
import time
import array

from System import Array, Byte, Int32, IO
from System.Drawing import Bitmap, Rectangle, Color

from OpenTK import *
from OpenTK.Graphics import *
from OpenTK.Graphics.OpenGL import *
from OpenTK.Input import *

import threading

from perlin_noise import pnoise1

def warp(x, r1, r3):
    # print("ho", x)
    # print("hi", (1.0/r3)*math.copysign(1, x)*(-math.sqrt(x**2*((r3**2)*(r1-r3)**2 - (r1**2-r3**2)*(x**2))) + abs(x)*r1*(r1-r3))/((r1-r3)**2+x**2))
    return 1/r3*math.copysign(1, x)*(-math.sqrt(x**2 * ((r3**2)*(r1-r3)**2 - (r1**2-r3**2)*x**2)) + abs(x)*r1*(r1-r3))/((r1-r3)**2+x**2)

class StimWindow(GameWindow):
    def __new__(self, controller, window_name="Stimulus", display_index=1):
        self.controller = controller

        print("Display index: {}.".format(display_index))

        if display_index == 1:
            # try to use a second display (projector)
            display = DisplayDevice.GetDisplay(DisplayIndex.Second)
        else:
            display = None

        if display == None:
            # fall back to the primary display (monitor)
            self.display_width = 1280
            self.display_height = 800
            window_flag = GameWindowFlags.Default

            display = DisplayDevice.GetDisplay(DisplayIndex.Default)
        else:
            self.display_width = 1280
            self.display_height = 800
            window_flag = GameWindowFlags.Fullscreen

            # set resolution, bits/pixel, refresh rate
            display.ChangeResolution(self.display_width, self.display_height, 8, 60)

        return GameWindow.__new__(self, self.display_width,
                                        self.display_height,
                                        GraphicsMode(8, 24, 0, 0), #  bits/pixel, depth bits, stencil bits, FSAA samples
                                        window_name,
                                        window_flag,
                                        display)

    def OnLoad(self, e):
        GameWindow.OnLoad(self, e)

        self.stim = None

        # set target frequency
        self.TargetUpdateFrequency = 60
        self.TargetRenderFrequency = 60

        # update display width and height
        self.display_width  = self.ClientRectangle.Width
        self.display_height = self.ClientRectangle.Height

        # set window's background color
        GL.ClearColor(0, 0, 0, 1)

        self.create_frame_buffer()

        # initialize time variable
        self.t = 0

        # initialize started bool
        self.started = False

        self.reset_stim = False

        # update stim params
        self.update_params()

        self.switch_to_stim(0)

    def create_frame_buffer(self):
        print("Creating frame buffer.")

        GL.Clear(ClearBufferMask.ColorBufferBit | ClearBufferMask.DepthBufferBit)

        texture = Array.CreateInstance(Byte, Array[int]([self.display_width, self.display_height, 3]))

        self.texture = GL.GenTexture()
        GL.BindTexture(TextureTarget.Texture2D, self.texture)

        GL.TexImage2D(TextureTarget.Texture2D, 0, PixelInternalFormat.Rgb, self.display_width, self.display_height, 0, PixelFormat.Rgb, PixelType.UnsignedByte, texture)

        GL.TexEnv( TextureEnvTarget.TextureEnv, TextureEnvParameter.TextureEnvMode,  int(TextureEnvMode.Replace) )
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMagFilter, int(TextureMagFilter.Linear))
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMinFilter, int(TextureMagFilter.Linear))
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapS, int(TextureWrapMode.Repeat))
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapT, int(TextureWrapMode.Repeat))

        self.frame_buffer = GL.GenFramebuffer()
        GL.BindFramebuffer(FramebufferTarget.Framebuffer, self.frame_buffer)
        GL.FramebufferTexture2D(FramebufferTarget.Framebuffer, FramebufferAttachment.ColorAttachment0, TextureTarget.Texture2D, self.texture, 0)

        GL.BindTexture(TextureTarget.Texture2D, 0)

    def update_params(self):
        print("StimWindow: Updating params.")

        # stop running stim & initialize time variable
        self.controller.running_stim = False
        self.t = 0

        self.distance = self.controller.experiment_params['dish_radius']
        self.resolution = self.display_width/self.controller.experiment_params['screen_cm_width']
        self.px_width = int(self.controller.experiment_params['width']*self.ClientRectangle.Width)
        self.px_height = int(self.controller.experiment_params['height']*self.ClientRectangle.Height)
        self.x_offset = int((self.controller.experiment_params['x_offset'])*(self.ClientRectangle.Width - self.px_width))
        self.y_offset = int((1.0 - self.controller.experiment_params['y_offset'])*(self.ClientRectangle.Height - self.px_height))
        self.durations_list = self.controller.config_params['durations_list']
        self.t_total = sum(self.durations_list)
        self.n_stim = len(self.durations_list)
        self.warp_perspective = self.controller.experiment_params['warp_perspective']
        self.dish_radius = self.controller.experiment_params['dish_radius']

        # warping parameters
        self.n_cylinder_segments = 100
        dish_radius = self.dish_radius*self.resolution
        print("dish radius", dish_radius)
        self.thetas = [ (i/float(self.n_cylinder_segments))*math.pi - (math.pi/2.0) for i in range(1, self.n_cylinder_segments) ]
        self.vertex_xs = [ (dish_radius*math.sin(theta)) for theta in self.thetas ]

        # reset stim
        if self.stim is not None:
            self.reset_stim = True

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
        self.stim_name = self.controller.config_params['stim_list'][index]
        self.duration = self.controller.config_params['durations_list'][index]
        self.params = self.controller.config_params['parameters_list'][index]

    def current_stim_state(self):
        keys_list = ["stim #", "stim name", "stim type"]

        stim_dict = {"stim #": self.stim_index,
                     "stim name": self.stim_name,
                     "stim type": self.stim_type}

        stim_dict_2, keys_list_2 = self.stim.current_state()

        if stim_dict_2 is not None:
            stim_dict.update(stim_dict_2)

        if keys_list_2 is not None:
            keys_list += keys_list_2

        return stim_dict, keys_list

    def create_stim(self):
        # run stim's end func
        if self.stim != None:
            self.stim.end_func()
            
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
            elif self.stim_type == "Optomotor Grating":    ##!! add a stim type for OKR
                self.stim = OptomotorGratingStim(self)
            elif self.stim_type == "BroadbandGrating":
                self.stim = BroadbandGratingStim(self)
        else:
            self.stim = None

    def OnUpdateFrame(self, e):
        GameWindow.OnUpdateFrame(self, e)

        if self.stim != None:
            if self.reset_stim:
                # reset stim
                self.switch_to_stim(0)

                self.reset_stim = False

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

                            if self.stim_index != self.n_stim - 1:
                                # we haven't reached the end of the sequence; switch to the next stim
                                self.switch_to_stim(self.stim_index + 1)

                                # reset started bool to trigger the start of the next stim
                                self.started = False
                            else:
                                # we've reached the end; stop the stim sequence
                                self.controller.param_window.start_stop_stim(None, None)
                else:
                    # # stim sequence is not running; reset stim if necessary
                    # if self.stim_index != 0:
                    #     self.switch_to_stim(0)
                    pass

    def OnRenderFrame(self, e):
        if self.stim != None:
            if self.stim_type != "Delay":
                if self.t < self.stim.duration:
                    # stim has started
                    self.MakeCurrent()

                    # clear buffers
                    GL.Clear(ClearBufferMask.ColorBufferBit | ClearBufferMask.DepthBufferBit)

                    if self.frame_buffer is not None:
                        GL.BindFramebuffer(FramebufferTarget.Framebuffer, self.frame_buffer)

                    GL.Viewport(0, 0, self.display_width, self.display_height)

                    # run stim's render function
                    if self.stim != None:
                        self.stim.render_func()

                    GL.BindFramebuffer(FramebufferTarget.Framebuffer, 0)

                    # set the viewport
                    GL.Viewport(self.x_offset, self.y_offset, self.px_width, self.px_height)

                    GL.LoadIdentity()

                    GL.MatrixMode(MatrixMode.Projection)
                    GL.Ortho(0.0, self.px_width, 0.0, self.px_height, -1.0, 1.0)

                    GL.BindTexture(TextureTarget.Texture2D, self.texture)

                    # enable texture mode
                    GL.Enable(EnableCap.Texture2D)

                    GL.Translate(self.px_width/2, self.px_height/2, 0)

                    if self.warp_perspective:
                        GL.Begin(BeginMode.QuadStrip)

                        dish_radius = self.dish_radius*self.resolution
                        dish_arc = dish_radius*math.pi/4

                        x = (self.px_width/2 - dish_arc)/self.px_width

                        GL.TexCoord2(x, 0.25)
                        GL.Vertex2(-dish_radius, -self.px_height/2)
                        GL.TexCoord2(x, 0.75)
                        GL.Vertex2(-dish_radius, self.px_height/2)

                        for i in range(1, self.n_cylinder_segments):
                            tc = i/float(self.n_cylinder_segments)

                            theta = self.thetas[i-1]
                            vertex_x = self.vertex_xs[i-1]

                            x = (self.px_width/2 - dish_arc + tc*2*dish_arc)/self.px_width

                            GL.TexCoord2(x, 0.25)
                            GL.Vertex2(vertex_x, -self.px_height/2)
                            GL.TexCoord2(x, 0.75)
                            GL.Vertex2(vertex_x, self.px_height/2)

                        x = 1.0 - (self.px_width/2 - dish_arc)/self.px_width

                        GL.TexCoord2(x, 0.25)
                        GL.Vertex2(dish_radius, -self.px_height/2)
                        GL.TexCoord2(x, 0.75)
                        GL.Vertex2(dish_radius, self.px_height/2)

                        GL.End()
                    else:
                        GL.Begin(BeginMode.Quads)
                        GL.TexCoord2(0.75, 0.75)
                        GL.Vertex2(self.px_width/2, self.px_height/2)
                        GL.TexCoord2(0.25, 0.75)
                        GL.Vertex2(-self.px_width/2, self.px_height/2)
                        GL.TexCoord2(0.25, 0.25)
                        GL.Vertex2(-self.px_width/2, -self.px_height/2)
                        GL.TexCoord2(0.75, 0.25)
                        GL.Vertex2(self.px_width/2, -self.px_height/2)
                        GL.End()

                    # disable texture mode
                    GL.Disable(EnableCap.Texture2D)

                    # swap buffers
                    self.SwapBuffers()

class LoomingDot():
    def __init__(self, stim):
        self.stim = stim

    def update_params(self, distance, resolution, params, window_width, window_height):
        self.redraw = False

        self.resolution = resolution # px/cm
        self.distance   = distance # cm
        self.window_width = window_width
        self.window_height = window_height
        self.max_radius = self.window_width*4 

        self.x        = math.tan(math.radians(params['looming_dot_init_x_pos']))*self.distance*self.resolution/(self.window_width/2)
        self.y        = math.tan(math.radians(params['looming_dot_init_y_pos']))*self.distance*self.resolution/(self.window_height/2)
        self.l_v      = params['l_v']
        self.brightness = params['looming_dot_brightness']
        self.contrast = 1

        self.A = self.distance*self.resolution*-self.l_v 

        self.radius_init = 1 # initial radius
        self.radius = self.radius_init

        self.angle = 0
        self.phase = 0
        self.frequency = 0.01

        self.texture = None

        self.checkered = params['checkered']
        self.texture_size = 100

        self.num_squares = params['num_squares']
        self.expand_checkered_pattern = params['expand_checkered_pattern']

        self.redraw = True

    def create_grating(self):
        # generate the grating texture
        for x in range(self.texture_size):
            for y in range(self.texture_size):
                if ((x // (self.texture_size/2)) % 2 == 0) ^ ((y // (self.texture_size/2)) % 2 == 1):
                    w = self.brightness*255.0
                else:
                    w = 0
                self.grating[self.texture_size*4*x + 4*y] = Byte(w)
                self.grating[self.texture_size*4*x + 4*y+1] = Byte(w)
                self.grating[self.texture_size*4*x + 4*y+2] = Byte(w)
                self.grating[self.texture_size*4*x + 4*y+3] = Byte(255)

    def create_texture(self):
        if self.texture is None:
            # create the texture
            self.texture = GL.GenTexture()

        # generate the texture
        self.grating = Array.CreateInstance(Byte, self.texture_size * self.texture_size * 4)
        self.create_grating()

        GL.BindTexture(TextureTarget.Texture2D, self.texture)

        # GL.TexEnv( TextureEnvTarget.TextureEnv, TextureEnvParameter.TextureEnvMode,  int(TextureEnvMode.Modulate) )
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMagFilter, int(TextureMagFilter.Linear))
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMinFilter, int(TextureMagFilter.Linear))
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapS, int(TextureWrapMode.Repeat))
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapT, int(TextureWrapMode.Repeat))

        GL.TexImage2D(TextureTarget.Texture2D, 0, PixelInternalFormat.Rgb, self.texture_size, self.texture_size, 0, PixelFormat.Rgba, PixelType.UnsignedByte, self.grating)

        GL.BindTexture(TextureTarget.Texture2D, 0)
    def update_func(self, time):
        if time < 0:
            # update radius
            self.radius = self.A/time
        else:
            self.radius = self.max_radius

    def draw_circle(self, n_vertices, radius):
        radius = min(2*(self.window_width/2.0), max(-2*(self.window_width/2.0), radius))
        radius_x = radius/(self.window_width/2.0)
        radius_y = radius/(self.window_height/2.0)

        if not self.checkered:
            GL.Begin(BeginMode.Polygon)
            for angle in linspace(0, 2*math.pi, n_vertices):
                GL.Vertex2(radius_x*math.sin(angle), radius_y*math.cos(angle))
            GL.End()
        else:
            GL.BindTexture(TextureTarget.Texture2D, self.texture)

            GL.Enable(EnableCap.Texture2D)

            GL.Begin(BeginMode.Polygon)
            for angle in linspace(0, 2*math.pi, n_vertices):
                if self.expand_checkered_pattern:
                    GL.TexCoord2((self.num_squares/2)*(0.5+0.5*math.sin(angle)), (self.num_squares/2)*(0.5+0.5*math.cos(angle)))
                else:
                    GL.TexCoord2((self.num_squares/2)*(radius_y/radius_x)*(0.5+0.5*radius_x*math.sin(angle)), (self.num_squares/2)*(0.5+0.5*radius_y*math.cos(angle)))
                GL.Vertex2(radius_x*math.sin(angle), radius_y*math.cos(angle))
            GL.End()

            GL.Disable(EnableCap.Texture2D)

            GL.BindTexture(TextureTarget.Texture2D, 0)

    def end_func(self):
        if self.checkered:
            GL.DeleteTextures(1, self.texture)
        pass

    def render_func(self):
        if self.redraw:
            # redraw the texture
            self.create_texture()

            # reset redraw bool
            self.redraw = False

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

        self.stim_index = self.stim_window.stim_index
        self.stim_name  = self.stim_window.stim_name
        self.stim_type  = self.stim_window.stim_type

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

    def current_state(self):
        return {"stim #": self.stim_index,
                "stim name": self.stim_name,
                "stim type": self.stim_type,
                "radius": self.looming_dot.radius}, ["radius"]

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

        # set dot color
        GL.Color3(self.brightness, self.brightness, self.brightness)

        for angle in linspace(0, 2*math.pi, n_vertices):
            GL.Vertex2(self.radius_x*math.sin(angle), self.radius_y*math.cos(angle))
        GL.End()

    def change_v_x(self, change_in_v_x):
        self.v_x = change_in_v_x*self.max_v_init

    def change_v_y(self, change_in_v_y):
        self.v_y += change_in_v_y*self.max_v_init

    def render_func(self):
        # set dot position
        GL.Translate(self.x, self.y, 0)

        # draw the dot
        self.draw_circle(30)

class MovingDotStim():
    def __init__(self, stim_window):
        self.stim_window = stim_window

        self.moving_dot = MovingDot(self)

        # get parameters
        distance = self.stim_window.distance
        resolution = self.stim_window.resolution
        duration = self.stim_window.duration
        params = self.stim_window.params

        self.stim_index = self.stim_window.stim_index
        self.stim_name  = self.stim_window.stim_name
        self.stim_type  = self.stim_window.stim_type

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

    def current_state(self):
        return {"stim #": self.stim_index,
                "stim name": self.stim_name,
                "stim type": self.stim_type,
                "x": self.moving_dot.x,
                "y": self.moving_dot.y}, ["x", "y"]

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

        self.stim_index = self.stim_window.stim_index
        self.stim_name  = self.stim_window.stim_name
        self.stim_type  = self.stim_window.stim_type

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

    def current_state(self):
        return {"stim #": self.stim_index,
                "stim name": self.stim_name,
                "stim type": self.stim_type,
                "looming dot radius": self.looming_dot.radius,
                "moving dot x": self.moving_dot.x,
                "moving dot y": self.moving_dot.y}, ["looming dot radius", "moving dot x", "moving dot y"]

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

        self.stim_index = self.stim_window.stim_index
        self.stim_name  = self.stim_window.stim_name
        self.stim_type  = self.stim_window.stim_type

        # update parameters
        self.update_params(distance, resolution, duration, params)

        self.texture = None

        self.create_texture()

    def update_params(self, distance, resolution, duration, params):
        print("GratingStim: Updating parameters.")

        self.redraw = False

        self.resolution = resolution # px/cm
        self.distance = distance # cm
        self.duration = duration*1000.0 # ms

        self.rad_width = math.atan2(self.stim_window.display_width/2.0, self.distance*self.resolution)*2
        self.frequency = params['frequency']*(180.0/math.pi)*self.rad_width/(self.stim_window.display_width) # rad/px
        self.init_phase = params['init_phase']*(math.pi/180.0)*self.stim_window.display_width/self.rad_width
        self.velocity_init = params['velocity']*(math.pi/180.0)*self.stim_window.display_width/self.rad_width/1000.0
        self.velocity = self.velocity_init
        self.contrast = params['contrast']
        self.brightness = params['brightness']
        self.angle = params['angle']
        
        self.velocity *= math.cos(self.angle*math.pi/180.0)
        self.velocity_init *= math.cos(self.angle*math.pi/180.0)

        self.t_init = -self.duration*1000.0 # ms
        self.t = self.t_init

        self.phase = self.init_phase

        self.texture_width = int(self.stim_window.display_width/2)

        # set redraw bool
        self.redraw = True

    def create_grating(self):
        print("Creating grating.")
        self.grating = Array.CreateInstance(Byte, Array[int]([self.texture_width, 3]))

        # generate the grating texture
        for x in range(self.texture_width):
            x_2 = (x/self.texture_width)*(2*self.stim_window.display_width)
            w = int(round((self.contrast*math.sin(self.frequency*x_2*2*math.pi - self.phase*self.frequency*2*math.pi) + 1.0)*self.brightness*255.0/2.0))
            self.grating[x, 0] = Byte(w)
            self.grating[x, 1] = Byte(w)
            self.grating[x, 2] = Byte(w)

    def create_texture(self):
        # generate the texture
        self.create_grating()

        # create the texture
        if self.texture is None:
            print("Creating texture.")
            self.texture = GL.GenTexture()

            GL.BindTexture(TextureTarget.Texture2D, self.texture)

            GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMagFilter, int(TextureMagFilter.Linear))
            GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMinFilter, int(TextureMagFilter.Linear))
            GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapS, int(TextureWrapMode.Repeat))
            GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapT, int(TextureWrapMode.Repeat))

            GL.TexImage2D(TextureTarget.Texture2D, 0, PixelInternalFormat.Rgb, self.texture_width, 1, 0, PixelFormat.Rgb, PixelType.UnsignedByte, self.grating)
        else:
            print("Updating texture.")
            GL.BindTexture(TextureTarget.Texture2D, self.texture)

            GL.TexSubImage2D(TextureTarget.Texture2D, 0, 0, 0, self.texture_width, 1, PixelFormat.Rgb, PixelType.UnsignedByte, self.grating)

        GL.BindTexture(TextureTarget.Texture2D, 0)

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
        print("Ending.")

        GL.DeleteTextures(1, self.texture)

        print("Ended.")
        pass

    def current_state(self):
        return {"stim #": self.stim_index,
                "stim name": self.stim_name,
                "stim type": self.stim_type,
                "phase": self.phase}, ["phase"]

    def render_func(self):
        if self.redraw:
            # redraw the texture
            self.create_texture()

            # reset redraw bool
            self.redraw = False

        GL.BindTexture(TextureTarget.Texture2D, self.texture)

        GL.LoadIdentity()

        GL.MatrixMode(MatrixMode.Projection)
        GL.Ortho(0.0, self.stim_window.px_width, 0.0, self.stim_window.px_height, -1.0, 1.0)

        GL.Enable(EnableCap.Texture2D)

        GL.PushMatrix()
        GL.Translate(self.stim_window.px_width/2, self.stim_window.px_height/2, 0)
        GL.Rotate(self.angle, 0, 0, 1)
        GL.Scale(self.stim_window.display_width/self.stim_window.px_width, self.stim_window.display_width/self.stim_window.px_height, 1)

        # draw texture quad
        GL.Begin(BeginMode.Quads)
        GL.TexCoord2(1.0, 1.0)
        GL.Vertex2(self.stim_window.px_width/2, self.stim_window.px_height/2)
        GL.TexCoord2(0, 1.0)
        GL.Vertex2(-self.stim_window.px_width/2, self.stim_window.px_height/2)
        GL.TexCoord2(0, 0)
        GL.Vertex2(-self.stim_window.px_width/2, -self.stim_window.px_height/2)
        GL.TexCoord2(1.0, 0)
        GL.Vertex2(self.stim_window.px_width/2, -self.stim_window.px_height/2)
        GL.End()

        GL.PopMatrix()

        # disable texture mode
        GL.Disable(EnableCap.Texture2D)

        GL.BindTexture(TextureTarget.Texture2D, 0)

##!!Need class OKR
class OptomotorGratingStim():
    #taken from GratingStim in swim_window.py
    def __init__(self, stim_window):
        self.stim_window = stim_window

        # get parameters
        distance = self.stim_window.distance
        resolution = self.stim_window.resolution
        duration = self.stim_window.duration
        params = self.stim_window.params

        self.stim_index = self.stim_window.stim_index
        self.stim_name  = self.stim_window.stim_name
        self.stim_type  = self.stim_window.stim_type

        # update parameters
        self.update_params(distance, resolution, duration, params)

        self.texture = None

        self.create_texture()

    def update_params(self, distance, resolution, duration, params):
        print("OptomotorStim: Updating parameters.")

        self.redraw = False

        self.resolution = resolution # px/cm
        self.distance = distance # cm
        self.duration = duration*1000.0 # ms

        self.rad_width = math.atan2(self.stim_window.display_width/2.0, self.distance*self.resolution)*2
        self.frequency = params['frequency']*(180.0/math.pi)*self.rad_width/(self.stim_window.display_width) # rad/px
        self.init_phase = params['init_phase']*(math.pi/180.0)*self.stim_window.display_width/self.rad_width
        self.velocity_init = params['velocity']*(math.pi/180.0)*self.stim_window.display_width/self.rad_width/1000.0
        self.velocity = self.velocity_init
        self.contrast = params['contrast']
        self.brightness = params['brightness']
        self.angle = params['angle']
        self.merging_pos = int(params['merging_pos']*2*self.stim_window.display_width)
        self.merging_pos_deg = self.merging_pos*self.rad_width/self.stim_window.display_width

        print(self.merging_pos)

        print(self.stim_window.display_width)
        print("merging", self.merging_pos)

        self.t_init = -self.duration*1000.0 # ms
        self.t = self.t_init

        self.phase = self.init_phase

        self.texture_width = int(self.stim_window.display_width/2)

        # set redraw bool
        self.redraw = True

    def create_grating(self):
        # generate the grating texture
        for x in range(self.texture_width):
            x_2 = (x/self.texture_width)*(2*self.stim_window.display_width)
            if x_2 >= self.merging_pos:
                w = (0.5*self.contrast*math.sin((2*self.merging_pos - x_2)*2*math.pi*self.frequency - self.phase*self.frequency*2*math.pi + self.merging_pos_deg*self.frequency*2*math.pi) + 0.5)*self.brightness*255
            else:
                w = (0.5*self.contrast*math.sin(x_2*2*math.pi*self.frequency - self.phase*self.frequency*2*math.pi + self.merging_pos_deg*self.frequency*2*math.pi) + 0.5)*self.brightness*255

            self.grating[x, 0] = Byte(w)
            self.grating[x, 1] = Byte(w)
            self.grating[x, 2] = Byte(w)

    def create_texture(self):
        if self.texture is None:
            # create the texture
            self.texture = GL.GenTexture()

        # generate the texture
        self.grating = Array.CreateInstance(Byte, Array[int]([self.texture_width, 3]))
        self.create_grating()

        GL.BindTexture(TextureTarget.Texture2D, self.texture)

        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMagFilter, int(TextureMagFilter.Linear))
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMinFilter, int(TextureMagFilter.Linear))
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapS, int(TextureWrapMode.Repeat))
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureWrapT, int(TextureWrapMode.Repeat))

        GL.TexImage2D(TextureTarget.Texture2D, 0, PixelInternalFormat.Rgb, self.texture_width, 1, 0, PixelFormat.Rgb, PixelType.UnsignedByte, self.grating)

        GL.BindTexture(TextureTarget.Texture2D, 0)

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
        GL.DeleteTextures(1, self.texture)
        pass

    def current_state(self):
        return {"stim #": self.stim_index,
                "stim name": self.stim_name,
                "stim type": self.stim_type,
                "phase": self.phase}, ["phase"]

    def render_func(self):
        if self.redraw:
            # redraw the texture
            self.create_texture()

            # reset redraw bool
            self.redraw = False

        GL.BindTexture(TextureTarget.Texture2D, self.texture)

        GL.LoadIdentity()

        # set projection
        GL.MatrixMode(MatrixMode.Projection)
        GL.Ortho(0.0, self.stim_window.px_width, 0.0, self.stim_window.px_height, -1.0, 1.0)

        # enable texture mode
        GL.Enable(EnableCap.Texture2D)

        GL.PushMatrix()
        GL.Translate(self.stim_window.px_width/2, self.stim_window.px_height/2, 0)
        GL.Rotate(self.angle, 0, 0, 1)
        GL.Scale(self.stim_window.display_width/self.stim_window.px_width, self.stim_window.display_width/self.stim_window.px_height, 1)

        # draw texture quad
        GL.Begin(BeginMode.Quads)
        GL.TexCoord2(1.0, 1.0)
        GL.Vertex2(self.stim_window.px_width/2, self.stim_window.px_height/2)
        GL.TexCoord2(0, 1.0)
        GL.Vertex2(-self.stim_window.px_width/2, self.stim_window.px_height/2)
        GL.TexCoord2(0, 0)
        GL.Vertex2(-self.stim_window.px_width/2, -self.stim_window.px_height/2)
        GL.TexCoord2(1.0, 0)
        GL.Vertex2(self.stim_window.px_width/2, -self.stim_window.px_height/2)
        GL.End()

        GL.PopMatrix()

        # disable texture mode
        GL.Disable(EnableCap.Texture2D)

        GL.BindTexture(TextureTarget.Texture2D, 0)

class BroadbandGratingStim():
    def __init__(self, stim_window):
        self.stim_window = stim_window

        # get parameters
        distance = self.stim_window.distance
        resolution = self.stim_window.resolution
        duration = self.stim_window.duration
        params = self.stim_window.params

        self.stim_index = self.stim_window.stim_index
        self.stim_name  = self.stim_window.stim_name
        self.stim_type  = self.stim_window.stim_type

        # update parameters
        self.update_params(distance, resolution, duration, params)

        self.texture = None

    def update_params(self, distance, resolution, duration, params):
        print("GratingStim: Updating parameters.")

        self.redraw = False

        self.resolution = resolution # px/cm
        self.distance = distance # cm
        self.duration = duration*1000.0 # ms

        self.rad_width = math.atan2(self.stim_window.display_width*2/2.0, self.distance*self.resolution)*2
        self.frequency = params['frequency']*(180.0/math.pi)*self.rad_width/(self.stim_window.display_width*2) # rad/px
        self.init_phase = params['init_phase']*(math.pi/180.0)*self.stim_window.display_width*2/self.rad_width
        self.velocity_init = params['velocity']*(math.pi/180.0)*self.stim_window.display_width*2/self.rad_width/1000.0
        self.velocity = self.velocity_init
        self.contrast = params['contrast']
        self.brightness = params['brightness']
        self.angle = params['angle']
        self.dish_radius = self.stim_window.dish_radius
        self.warp_perspective = self.stim_window.warp_perspective

        self.t_init = -self.duration*1000.0 # ms
        self.t = self.t_init

        self.phase = self.init_phase

        # set redraw bool
        self.redraw = True

    def rand_frequency(self, x):
        return 0.2*self.frequency*math.sin(self.frequency*x) + self.frequency

    def grating_profile(self, offset):
        return [ math.sin(self.rand_frequency((x - offset) % self.stim_window.display_width*2)*((x - offset) % self.stim_window.display_width*2)*2*math.pi) for x in range(4*self.stim_window.display_width*2) ]

    def create_grating(self):
        # generate the grating texture
        grating_profile = self.grating_profile(self.t*self.velocity)
        for x in range(2*self.stim_window.px_width):
            w = self.contrast*(grating_profile[x] + 1.0)*self.brightness*255.0/2.0
            self.grating[4*x] = Byte(w)
            self.grating[4*x+1] = Byte(w)
            self.grating[4*x+2] = Byte(w)
            self.grating[4*x+3] = Byte(255)

    def create_texture(self):
        if self.texture is not None:
            GL.DeleteTextures(1, self.texture)

        # generate the texture
        self.grating = Array.CreateInstance(Byte, 2*self.stim_window.display_width*2 * 4)
        self.create_grating()

        # create the texture
        self.texture = GL.GenTexture()
        GL.BindTexture(TextureTarget.Texture2D, self.texture)

        GL.TexEnv( TextureEnvTarget.TextureEnv, TextureEnvParameter.TextureEnvMode,  int(TextureEnvMode.Modulate) )
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMagFilter, int(TextureMagFilter.Linear))
        GL.TexParameter(TextureTarget.Texture2D, TextureParameterName.TextureMinFilter, int(TextureMagFilter.Linear))

        GL.TexImage2D(TextureTarget.Texture2D, 0, PixelInternalFormat.Rgb, self.stim_window.display_width*2, 1, 0, PixelFormat.Rgba, PixelType.UnsignedByte, self.grating)

    def change_velocity(self, change_in_velocity):
        self.velocity = change_in_velocity*self.velocity_init

    def start_func(self):
        pass

    def update_func(self, elapsed_time):
        # update phase
        self.phase += -self.velocity*elapsed_time
        self.t += elapsed_time

        # set redraw bool
        self.redraw = True

    def end_func(self):
        GL.DeleteTextures(1, self.texture)
        pass

    def current_state(self):
        return {"stim #": self.stim_index,
                "stim name": self.stim_name,
                "stim type": self.stim_type,
                "phase": self.phase}, ["phase"]

    def render_func(self):
        GL.LoadIdentity()

        # set projection
        GL.MatrixMode(MatrixMode.Projection)
        GL.Ortho(0.0, self.stim_window.px_width, 0.0, self.stim_window.px_height, -1.0, 1.0)

        if self.redraw:
            # set color
            GL.Color4(Color.White)

            # redraw the texture
            self.create_texture()

            # reset redraw bool
            self.redraw = False

        # enable texture mode
        GL.Enable(EnableCap.Texture2D)

        GL.PushMatrix()
        GL.Translate(self.stim_window.px_width/2, self.stim_window.px_height/2, 0)
        GL.Rotate(self.angle, 0, 0, 1)
        GL.Scale(2*self.stim_window.display_width/self.stim_window.px_width, 2*self.stim_window.display_height/self.stim_window.px_height, 1)

        # draw texture quad
        GL.Begin(BeginMode.Quads)
        GL.TexCoord2(1.0, 1.0)
        GL.Vertex2(self.stim_window.px_width/2, self.stim_window.px_height/2)
        GL.TexCoord2(0, 1.0)
        GL.Vertex2(-self.stim_window.px_width/2, self.stim_window.px_height/2)
        GL.TexCoord2(0, 0)
        GL.Vertex2(-self.stim_window.px_width/2, -self.stim_window.px_height/2)
        GL.TexCoord2(1.0, 0)
        GL.Vertex2(self.stim_window.px_width/2, -self.stim_window.px_height/2)
        GL.End()

        GL.PopMatrix()

        # disable texture mode
        GL.Disable(EnableCap.Texture2D)

class DelayStim():
    def __init__(self, stim_window):
        self.stim_window = stim_window

        # get parameters
        distance = self.stim_window.distance
        resolution = self.stim_window.resolution
        duration = self.stim_window.duration
        params = self.stim_window.params

        self.stim_index = self.stim_window.stim_index
        self.stim_name  = self.stim_window.stim_name
        self.stim_type  = self.stim_window.stim_type

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

    def current_state(self):
        return {"stim #": self.stim_index,
                "stim name": self.stim_name,
                "stim type": self.stim_type}, None

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

        self.stim_index = self.stim_window.stim_index
        self.stim_name  = self.stim_window.stim_name
        self.stim_type  = self.stim_window.stim_type

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

    def current_state(self):
        return {"stim #": self.stim_index,
                "stim name": self.stim_name,
                "stim type": self.stim_type}, None

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

        self.stim_index = self.stim_window.stim_index
        self.stim_name  = self.stim_window.stim_name
        self.stim_type  = self.stim_window.stim_type

        self.brightness = params['brightness']

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

    def current_state(self):
        return {"stim #": self.stim_index,
                "stim name": self.stim_name,
                "stim type": self.stim_type}, None

    def render_func(self):
        GL.LoadIdentity()

        # draw in the viewport background
        GL.Begin(BeginMode.Quads)
        GL.Color3(self.brightness, self.brightness, self.brightness)
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
