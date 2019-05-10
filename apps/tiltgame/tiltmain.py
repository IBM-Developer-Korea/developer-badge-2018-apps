# -*- coding: utf-8 -*-
# Copyright 2019 IBM Corp. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the “License”)
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ujson as json
import uos
import sys
import util
import network
import utime as time
import urequests
import ugfx

from machine import I2C, Pin
from tiltgame.mpu6050 import MPU6050
from tiltgame.buzzer import Buzzer

from home import styles


class TiltMain():

    # Buttons
    def select_up_cb(self, pressed=True):
        if pressed:
            pass

    def select_down_cb(self, pressed=True):
        if pressed:
            pass

    
    def select_left_cb(self, pressed=True):
        if pressed:
            pass

    def select_right_cb(self, pressed=True):
        if pressed:
            pass

    def select_a_cb(self, pressed=True):
        if pressed:
            pass

    def select_b_cb(self, pressed=True):
        if pressed:
            pass

    def init_buttons(self):
        # JOY Buttons Handler
        ugfx.input_attach(ugfx.JOY_UP, self.select_up_cb)
        ugfx.input_attach(ugfx.JOY_DOWN, self.select_down_cb)
        ugfx.input_attach(ugfx.JOY_LEFT, self.select_left_cb)
        ugfx.input_attach(ugfx.JOY_RIGHT, self.select_right_cb)

        # A/B Button Handler
        ugfx.input_attach(ugfx.BTN_A, self.select_a_cb)
        ugfx.input_attach(ugfx.BTN_B, self.select_b_cb)

    def __init__(self):
        # initialize ugfx
        ugfx.init()
        ugfx.clear(ugfx.WHITE)
        
        # Buttons
        ugfx.input_init()
        self.init_buttons()

        # Container
        width = ugfx.width()
        height = ugfx.height()
        ind_height = 46
        container_height = height - ind_height

        self.indicator = ugfx.Container(0, 0, width, ind_height, style=styles.ibm_st)
        self.container = ugfx.Container(0, ind_height, width, container_height, style=styles.ibm_st)

        self.graph_basepos = container_height - 5
        
        # Sensor
        SCL = Pin(26) # SCL
        SDA  = Pin(25) # SDA
        self.sensor = MPU6050(I2C(scl=SCL, sda=SDA))

        # Buzzer
        self.buzzer = Buzzer()

    def showTitleText(self, text):
        self.indicator.area(0, 0, self.indicator.width(), self.indicator.height(), ugfx.BLACK)
        ugfx.string_box(0, 0, self.indicator.width(), self.indicator.height(), text, 'IBMPlexMono_Bold24', ugfx.WHITE, ugfx.justifyCenter)

    def ema(self, prev, curr):
        # Exponential Moving Average
        # https://www.investopedia.com/terms/e/ema.asp
        # EMA(t) = Value(t)*k + EMA(y) * (1-k)
        # k = 2 / (N+1)
        # k = 0.1 where N = 19
        return curr * 0.1 + prev * 0.9

    def run(self):

        # Show window
        self.indicator.show()
        self.container.show()

        # Title
        # self.indicator.area(0, 0, self.indicator.width(), self.indicator.height(), ugfx.BLACK)
        # ugfx.string_box(0, 0, self.indicator.width(), self.indicator.height(), 'AQI Gas Monitor', 'IBMPlexMono_Bold24', ugfx.WHITE, ugfx.justifyCenter)
        self.showTitleText('MPU6050 Demo')

        # Wait 3 seconds
        # for i in range(3):
        #     self.showTitleText('Intializing {}'.format('.'*i))
        #     time.sleep(1)

        width = self.container.width()
        height = self.container.height()

        px = width//2
        py = height//2
        cx = px; cy = py
        ax = 0;ay = 0;az = 0
        gx = 0;gy = 0;gz = 0
        while True:

            acc_x, acc_y, acc_z, temp, gyro_x, gyro_y, gyro_z = self.sensor.measure_scaled()
            
            ax = self.ema(ax, acc_x)
            ay = self.ema(ay, acc_y)
            az = self.ema(az, acc_z)

            gx = self.ema(gx, gyro_x)
            gy = self.ema(gy, gyro_y)
            gz = self.ema(gz, gyro_z)

            #print('{},{},{}'.format(ax, ay, az))
            # print('{},{},{}'.format(gx, gy, gz))
            # print('{},{},{},{},{},{}'.format(ax, ay, az, gx, gy, gz))

            pitch, roll, z = self.sensor.calc_acc_angles(ax, ay, az)
            pitch = int(pitch)
            roll = int(roll)
            
            # Move ball
            cx += roll//5
            cy += pitch//5
            
            # Border
            if cx < 0:
                cx = 0
            if cy < 0:
                cy = 0
            if cx >= width:
                cx = width-1
            if cy >= height:
                cy = height-1

            # Erase
            if px != cx or py != cy:
                #ugfx.pixel(px, py, ugfx.WHITE)
                #ugfx.area(px-5, py-5, 10, 10, ugfx.WHITE)
                self.container.fill_circle(px, py, 5, ugfx.WHITE)

            # Draw
            #ugfx.pixel(cx, cy, ugfx.BLACK)
            #ugfx.area(cx-5, cy-5, 10, 10, ugfx.RED)
            self.container.fill_circle(cx, cy, 5, ugfx.RED)

            # Renew
            px = cx; py = cy

            #time.sleep_ms(10)

    def restart(self):
        util.run('tiltgame')

    def exit(self):
        util.reboot()