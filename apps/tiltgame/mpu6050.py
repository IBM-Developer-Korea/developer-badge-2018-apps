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

from machine import I2C, Pin
import time
import ustruct
import math
import sys

class MPU6050():

    # Registers
    MPU6050_CONFIG       = 0x1a
    MPU6050_GYRO_CONFIG  = 0x1b
    MPU6050_ACCEL_CONFIG = 0x1c
    MPU6050_SMPLRT_DIV = 0x19

    MPU6050_I2C_MST_STATUS = 0x36
    MPU6050_INT_STATUS = 0x3a
    MPU6050_ACCEL_XOUT_H = 0x3b
    MPU6050_ACCEL_XOUT_L = 0x3c
    MPU6050_ACCEL_YOUT_H = 0x3d
    MPU6050_ACCEL_YOUT_L = 0x3e
    MPU6050_ACCEL_ZOUT_H = 0x3f
    MPU6050_ACCEL_ZOUT_L = 0x40
    MPU6050_TEMP_OUT_H = 0x41
    MPU6050_TEMP_OUT_L = 0x42
    MPU6050_GYRO_XOUT_H = 0x43
    MPU6050_GYRO_XOUT_L = 0x44
    MPU6050_GYRO_YOUT_H = 0x45
    MPU6050_GYRO_YOUT_L = 0x46
    MPU6050_GYRO_ZOUT_H = 0x47
    MPU6050_GYRO_ZOUT_L = 0x48
    MPU6050_PWR_MGMT_1 = 0x6b
    MPU6050_PWR_MGMT_2 = 0x6c
    MPU6050_WHO_AM_I = 0x75

    # Full scale range & sensitivity
    MPU6050_AFS_SEL = {
        0: (2, 16384),
        1: (4, 8192),
        2: (8, 4096),
        3: (16, 2048),
    }

    MPU6050_FS_SEL = {
        0: (250, 131),
        1: (500, 65.5),
        2: (1000, 32.8),
        3: (2000, 16.4),
    }

    RADIANS_TO_DEGREES = 57.29578 # 180/math.pi

    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.sl_addr = addr

        self.i2c.writeto_mem(self.sl_addr, self.MPU6050_PWR_MGMT_1, bytearray([0x00]))
        data = self.i2c.readfrom_mem(self.sl_addr, self.MPU6050_WHO_AM_I, 1)[0]
        if data != 0x68:
            raise Exception('MPU6050 initialize failure')

        self.afs_range, self.afs_sensitivity = self.MPU6050_AFS_SEL[0]
        self.gfs_range, self.gfs_sensitivity = self.MPU6050_FS_SEL[0]

    def calc_fullscale_factor(self):

        # Accel Config
        accel_config = self.i2c.readfrom_mem(self.sl_addr, self.MPU6050_ACCEL_CONFIG, 1)[0]
        self.afs_range, self.afs_sensitivity = self.MPU6050_AFS_SEL.get((accel_config >> 3) & 0x03, self.MPU6050_AFS_SEL[0])

        # Gyro Config
        gyro_config = self.i2c.readfrom_mem(self.sl_addr, self.MPU6050_GYRO_CONFIG, 1)[0]
        self.gfs_range, self.gfs_sensitivity = self.MPU6050_FS_SEL.get((gyro_config >> 3) & 0x03, self.MPU6050_FS_SEL[0])

    # functions
    def measure(self):
        data = self.i2c.readfrom_mem(self.sl_addr, self.MPU6050_ACCEL_XOUT_H, 14)
        acc_x, acc_y, acc_z, tp, gyro_x, gyro_y, gyro_z = ustruct.unpack('>hhhhhhh', data)

        # Convert in degrees C
        tp = tp/340 + 36.53

        return (acc_x, acc_y, acc_z, tp, gyro_x, gyro_y, gyro_z)

    def measure_scaled(self):
        data = self.i2c.readfrom_mem(self.sl_addr, self.MPU6050_ACCEL_XOUT_H, 14)
        measured = list(ustruct.unpack('>hhhhhhh', data))
        measured[0:3] = [(m / self.afs_sensitivity) for m in measured[0:3]]
        measured[3] = measured[3]/340 + 36.53 # Convert in degrees C
        measured[4:] = [(m / self.gfs_sensitivity) for m in measured[4:]]

        return tuple(measured)

    def readAccelerometer(self):
        data = self.i2c.readfrom_mem(self.sl_addr, self.MPU6050_ACCEL_XOUT_H, 6)
        return ustruct.unpack('>hhh', data)

    def readTemperature(self):
        return self.reads16(self.MPU6050_TEMP_OUT_H)/340 + 36.53

    def readGyroscope(self):
        data = self.i2c.readfrom_mem(self.sl_addr, self.MPU6050_GYRO_XOUT_H, 6)
        return ustruct.unpack('>hhh', data)

    def read8(self, addr):
        data = self.i2c.readfrom_mem(self.sl_addr, addr, 1)
        return ustruct.unpack('>B', data)[0]

    def read16(self, addr):
        data = self.i2c.readfrom_mem(self.sl_addr, addr, 2)
        return ustruct.unpack('>H', data)[0]

    def reads8(self, addr):
        data = self.i2c.readfrom_mem(self.sl_addr, addr, 1)
        return ustruct.unpack('>b', data)[0]

    def reads16(self, addr):
        data = self.i2c.readfrom_mem(self.sl_addr, addr, 2)
        return ustruct.unpack('>h', data)[0]
    
    def calc_acc_angles(self, acc_x, acc_y, acc_z):
        angle_x = math.atan(acc_x / math.sqrt(math.pow(acc_y, 2) + math.pow(acc_z, 2))) * self.RADIANS_TO_DEGREES
        angle_y = math.atan(acc_y / math.sqrt(math.pow(acc_x, 2) + math.pow(acc_z, 2))) * self.RADIANS_TO_DEGREES
        angle_z = math.atan(math.sqrt(math.pow(acc_x, 2) + math.pow(acc_y, 2)) / acc_z) * self.RADIANS_TO_DEGREES

        return (angle_x, angle_y, angle_z)
