import ujson as json
import uos
import sys
import util
import network
import utime as time
import urequests
import ugfx

from dustapp import gp2y1014au

from home import styles

class DustMain():

    # Config
    IS_PM2_5 = False
    IS_AUTOSCALE = False
    REFRESH_RATE = 1000 # 200

    # Levels
    X_RESOLUTION = 40 # 320
    volist = [(0, 0)] * X_RESOLUTION
    idx = 0
    
    # scale_factor
    scale_factor = 1 if IS_AUTOSCALE else 10
    p_scale = scale_factor
    y_offset = 200 # 120


    # PM 10
    PM10_KR_STANDARD = {'GOOD': 0, 'NORMAL': 31, 'BAD': 81, 'VERY_BAD': 151}
    PM10_WHO_STANDARD = {'GOOD': 0, 'NORMAL': 31, 'BAD': 51, 'VERY_BAD': 101}

    # PM 2.5
    PM2_5_KR_STANDARD = {'GOOD': 0, 'NORMAL': 16, 'BAD': 36, 'VERY_BAD': 76}
    PM2_5_WHO_STANDARD = {'GOOD': 0, 'NORMAL': 16, 'BAD': 26, 'VERY_BAD': 51}

    # 미세미세
    MISE8_PM10 = [0, 16, 31, 41, 51, 76, 101, 151]
    MISE8_PM2_5 = [0, 9, 16, 21, 26, 38, 51, 76]

    PM10_LEVELS = [
        ('UNKNOWN',  sys.maxsize, ugfx.HTML2COLOR(0x654c9d)),
        ('HELL',     151, ugfx.BLACK),
        ('VERY BAD', 101, ugfx.HTML2COLOR(0xd3312e)),
        ('QUITE BAD', 76, ugfx.HTML2COLOR(0xe35225)),
        ('BAD',       51, ugfx.HTML2COLOR(0xf78d1d)),
        ('MODERATE',  41, ugfx.HTML2COLOR(0x329042)),
        ('GOOD',      31, ugfx.HTML2COLOR(0x12afc0)),
        ('VERY GOOD', 16, ugfx.HTML2COLOR(0x299cd5)),
        ('BEST',       0, ugfx.HTML2COLOR(0x2b75c0)),
    ]

    PM2_5_LEVELS = [
        ('UNKNOWN',   sys.maxsize, ugfx.HTML2COLOR(0x654c9d)),
        ('HELL',      76, ugfx.BLACK),
        ('VERY BAD',  51, ugfx.HTML2COLOR(0xd3312e)),
        ('QUITE BAD', 38, ugfx.HTML2COLOR(0xe35225)),
        ('BAD',       26, ugfx.HTML2COLOR(0xf78d1d)),
        ('MODERATE',  21, ugfx.HTML2COLOR(0x329042)),
        ('GOOD',      16, ugfx.HTML2COLOR(0x12afc0)),
        ('VERY GOOD',  9, ugfx.HTML2COLOR(0x299cd5)),
        ('BEST',       0, ugfx.HTML2COLOR(0x2b75c0)),
    ]

    DENSITY_LEVELS = PM2_5_LEVELS if IS_PM2_5 else PM10_LEVELS

    def getDensityInfo(self, density):
        for lb, lv, color in self.DENSITY_LEVELS:
            if density > lv:
                #print('{}-{}-{}'.format(lb, lv, color))
                return {
                    'label': lb,
                    'level': lv,
                    'color': color
                }

        lb, lv, color = self.DENSITY_LEVELS[0]
        return {
            'label': lb,
            'level': lv,
            'color': color
        }

    def getLevelColor(self, density):
        return self.getDensityInfo(density)['color']

    def __init__(self):
        # initialize ugfx
        ugfx.init()
        ugfx.clear(ugfx.WHITE)

        # Container
        width = ugfx.width()
        height = ugfx.height()
        self.container = ugfx.Container(0, 0, width, height, style=styles.ibm_st)

        # Sensor
        self.dust_sensor = gp2y1014au.GP2Y1014AU(iled=32, vo=36, K=0.5, Voc=0.6)

        # Smooth
        self.Vos = 0.8

    def run(self):

        # Show container
        self.container.show()

        stime = time.ticks_ms()

        while True:
            Vo = self.dust_sensor.readVo(280, 40)

            # Exponential Moving Average
            # https://www.investopedia.com/terms/e/ema.asp
            # EMA(t) = Value(t)*k + EMA(y) * (1-k)
            # k = 2 / (N+1)
            # k = 0.005 where N = 399
            self.Vos = Vo * 0.005 + self.Vos * 0.995

            #time.sleep_ms(10)
            time.sleep_ms(5)

            if self.REFRESH_RATE < (time.ticks_ms() - stime):
                stime = time.ticks_ms()
                self.refresh_screen()
    
    def y_scale(self, v):
        return int(v / self.scale_factor)

    def refresh_screen(self):
        # Input
        vos = self.Vos * 1000.0
        density = int(self.dust_sensor.computeDensity(self.Vos))
        self.volist[self.idx] = (vos, density)
        
        avos = abs(max(self.volist, key=lambda item:item[0])[0])

        # Scale
        if self.IS_AUTOSCALE:
            limits = self.y_offset - 10
            if avos > limits:
                self.scale_factor = int(avos / limits)+1
                if self.scale_factor != self.p_scale:
                    ugfx.clear(ugfx.WHITE)
                self.p_scale = self.scale_factor

        # Clear
        #ugfx.clear(ugfx.WHITE)

        # Indicator
        ind_y = self.y_offset+10
        status = self.getDensityInfo(density)
        ugfx.area(0, ind_y, 320, 240, status['color'])
        ugfx.text(0, ind_y+6, '[1/{}] {}mV {} ({}ug/m3)'.format(self.scale_factor, int(self.Vos * 1000.0), status['label'], '-' if density < 0 else density), ugfx.WHITE)

        # draw
        py = self.y_offset
        px = 0
        for i, (v, d) in enumerate(self.volist):
            x = int (i / self.X_RESOLUTION * 320 )
            y = self.y_offset - self.y_scale(v)

            # Color
            lvcolor = self.getLevelColor(d)

            # draw
            if i == self.idx+1:
                # clear oldest
                ugfx.area(px, 0, x, self.y_offset, ugfx.WHITE)
            else:
                # previous
                #ugfx.thickline(px, py, x, y, lvcolor, 5, True)
                ugfx.line(px, py, x, y, lvcolor)
            
            px = x
            py = y

        # baseline
        ugfx.line(0, self.y_offset, 320, self.y_offset, ugfx.BLACK)

        # ruler
        y = 0
        maxy = self.y_offset * self.scale_factor

        while y < maxy:
            sy = self.y_offset  - self.y_scale(y)
            ugfx.line(0, sy, 20 if y%500 == 0 else 10, sy, ugfx.BLACK)
            y += 100

        # increase
        self.idx += 1
        if self.idx == self.X_RESOLUTION:
            self.idx = 0

    def restart(self):
        util.run('dustapp')

    def exit(self):
        util.reboot()

