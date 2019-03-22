import ujson as json
import uos
import sys
import util
import network
import utime as time
import urequests
import ugfx

from home import styles

try:
    gp2y1014au = __import__('gp2y1014au')
except ImportError:
    gp2y1014au = __import__('gp2y1014au', ['dustapp'])

class DustMain():

    # Config
    IS_PM2_5 = False
    IS_AUTOSCALE = True
    REFRESH_RATE = 1000 # 200

    AVG_NUM = 400
    SAMPLING_TIME = 200 # 280
    VOC = 0.0 # 0.6

    # Levels
    X_RESOLUTION = 40 # 320
    volist = [(0, 0)] * X_RESOLUTION
    idx = 0
    
    # scale_factor
    scale_factor = 1 if IS_AUTOSCALE else 10
    p_scale = scale_factor

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

    def getDensityInfo(self, density):
        levels = self.PM2_5_LEVELS if self.IS_PM2_5 else self.PM10_LEVELS
        for lb, lv, color in levels:
            if density > lv:
                #print('{}-{}-{}'.format(lb, lv, color))
                return {
                    'label': lb,
                    'level': lv,
                    'color': color
                }

        lb, lv, color = levels[0]
        return {
            'label': lb,
            'level': lv,
            'color': color
        }

    def getLevelColor(self, density):
        return self.getDensityInfo(density)['color']
    
    # Increase sampling time
    def select_up_cb(self, pressed=True):
        if pressed:
            self.SAMPLING_TIME = self.SAMPLING_TIME + 20

    # Decrease sampling time
    def select_down_cb(self, pressed=True):
        if pressed:
            self.SAMPLING_TIME = self.SAMPLING_TIME - 20

    # Decrease Voc
    def select_left_cb(self, pressed=True):
        if pressed:
            self.VOC = round(self.VOC - 0.1, 3)

    # Increase Voc
    def select_right_cb(self, pressed=True):
        if pressed:
            self.VOC = round(self.VOC + 0.1, 3)

    def select_a_cb(self, pressed=True):
        self.VOC = 0.0 # 0.6
        self.SAMPLING_TIME = 200 # 280

    # Back to home
    def select_b_cb(self, pressed=True):
        run('home')

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

        # Container
        width = ugfx.width()
        height = ugfx.height()
        ind_height = 40
        ind_pos = height - ind_height

        self.indicator = ugfx.Container(0, ind_pos, width, ind_height, style=styles.ibm_st)
        self.container = ugfx.Container(0, 0, width, ind_pos, style=styles.ibm_st)

        self.y_offset = ind_pos - 10
        
        # Sensor
        self.dust_sensor = gp2y1014au.GP2Y1014AU(iled=32, vo=36, K=0.5, Voc=self.VOC)
        
        # Smooth
        self.Vos = 0.1 # 0.8

    def run(self):

        # Show container
        self.container.show()
        self.indicator.show()

        stime = time.ticks_ms()

        cnt = 0
        sleep_time = 2000
        while True:
            #Vo = self.dust_sensor.readVo(280, 40)
            VoRaw = self.dust_sensor.readVoRaw(self.SAMPLING_TIME, 0)

            # Compute the output in Volts.
            Vo = VoRaw / 4095.0 * 5.0
            # Vo = self.dust_sensor.readVo(self.SAMPLING_TIME, 0)

            # Exponential Moving Average
            # https://www.investopedia.com/terms/e/ema.asp
            # EMA(t) = Value(t)*k + EMA(y) * (1-k)
            # k = 2 / (N+1)
            # k = 0.005 where N = 399
            self.Vos = Vo * 0.005 + self.Vos * 0.995

            # print('{}, {}'.format(VoRaw, self.Vos * 1000.0))

            # time.sleep_ms(10)
            time.sleep_us(sleep_time)
            cnt += 1

            if cnt == self.AVG_NUM:
                elapsed = (time.ticks_ms() - stime)
                stime = time.ticks_ms()
                if elapsed > self.REFRESH_RATE+50:
                    sleep_time -= 100
                elif elapsed < self.REFRESH_RATE-50:
                    sleep_time += 100

                self.refresh_screen()
                self.init_buttons()
                #print('{}, {}, {}, {}'.format(cnt, elapsed, sleep_time, self.Vos))
                cnt = 0
    
    def y_scale(self, v):
        return int(v / self.scale_factor)

    def refresh_screen(self):
        # Input
        vos = self.Vos * 1000.0
        density = int(self.dust_sensor.computeDensity(self.Vos, self.VOC))
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

        # Indicator
        status = self.getDensityInfo(density)
        #self.indicator.clear(status['color'])
        self.indicator.area(0, 0, self.indicator.width(), self.indicator.height(), status['color'])
        #self.indicator.text(0, 12, 'x1/{} {}mV {} ({}ug/m3)'.format(self.scale_factor, int(Vo * 1000.0), status['label'], '-' if density < 0 else density), ugfx.WHITE)
        self.indicator.text(0, 12, '{}us Voc:{} {}ug/m3 : {}'.format(self.SAMPLING_TIME, self.VOC, '-' if density < 0 else density, status['label']), ugfx.WHITE)

        # draw
        py = self.y_offset
        px = 0
        for i, (v, d) in enumerate(self.volist):
            x = int (i / self.X_RESOLUTION * self.container.width() )
            y = self.y_offset - self.y_scale(v)

            # Color
            lvcolor = self.getLevelColor(d)

            # draw
            if i == self.idx+1:
                # clear oldest
                self.container.area(px, 0, x, self.y_offset, ugfx.WHITE)
            else:
                # previous
                #container.thickline(px, py, x, y, lvcolor, 5, True)
                self.container.line(px, py, x, y, lvcolor)
            
            px = x
            py = y

        # baseline
        self.container.line(0, self.y_offset, self.container.width(), self.y_offset, ugfx.BLACK)

        # ruler
        y = 0
        maxy = self.y_offset * self.scale_factor

        while y < maxy:
            sy = self.y_offset  - self.y_scale(y)
            self.container.line(0, sy, 20 if y%500 == 0 else 10, sy, ugfx.BLACK)
            y += 100

        # increase
        self.idx += 1
        if self.idx == self.X_RESOLUTION:
            self.idx = 0

    def restart(self):
        util.run('dustapp')

    def exit(self):
        util.reboot()

