import time
import machine
import ugfx
from machine import Pin
from machine import ADC

class GP2Y1014AU():

    # Output volate at no dust in V
    Voc = 0.6 # 0.1 to 1.1

    # Sensitivity in units of V per 100ug/m3.
    K = 0.5 # 0.425 to 0.575

    # ADC Resoultion
    resolution = float(4096 - 1)

    def __init__(self, iled=32, vo=36, K=0.5, Voc=0.6):
        # initialize I/O
        self.sharpLEDPin = Pin(iled, Pin.OUT)
        self.sharpVoPin = ADC(Pin(vo))
        self.sharpVoPin.atten(ADC.ATTN_11DB)

        self.K = K
        self.Voc = Voc

    def readVo(self, samplingTime=280, deltaTime=40):
        VoRaw = self.readVoRaw(samplingTime, deltaTime)

        # Compute the output in Volts.
        return VoRaw / self.resolution * 5.0

    def readVoRaw(self, samplingTime=280, deltaTime=40):
        # Turn on ILED
        self.sharpLEDPin.value(0)

        # Wait 0.28ms 
        time.sleep_us(samplingTime)

        VoRaw = self.sharpVoPin.read()

        # Wait 0.04ms
        time.sleep_us(deltaTime)

        # Turn off ILED
        self.sharpLEDPin.value(1)

        return VoRaw

    def computeDensity(self, Vo, Voc = 0.6):
        
        # Convert to Dust Density in units of ug/m3.
        dV = Vo - Voc
        if dV <= 0:
            dV = 0
            return -1.0

        return dV / self.K * 100.0

