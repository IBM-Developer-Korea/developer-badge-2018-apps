import ujson as json
import uos
import sys
import util
import network
import utime as time
import urequests
import ugfx

from dustapp.iotfoundation import IoTFoundation
from dustapp.buzzer import Buzzer

from home import styles

try:
    gp2y1014au = __import__('gp2y1014au')
except ImportError:
    gp2y1014au = __import__('gp2y1014au', ['dustapp'])

class DustMain():

    # Config
    IS_PM2_5 = True
    IS_GRAPH_MODE = False # True
    IS_AUTOSCALE = True
    REFRESH_RATE = 1000 # 200

    SAMPLING_TIME = 200 # 280
    K = 0.5 #
    Voc = 0.270 # 0.6

    # Levels
    X_RESOLUTION = 40 # 320
    volist = [(0, 0)] * X_RESOLUTION

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
        ('Hell',     151, ugfx.BLACK),
        ('Severe',   101, ugfx.HTML2COLOR(0xd3312e)),
        ('Very bad',  76, ugfx.HTML2COLOR(0xe35225)),
        ('Bad',       51, ugfx.HTML2COLOR(0xf78d1d)),
        ('Moderate',  41, ugfx.HTML2COLOR(0x329042)),
        ('Good',      31, ugfx.HTML2COLOR(0x12afc0)),
        ('Very good', 16, ugfx.HTML2COLOR(0x299cd5)),
        ('Best',       0, ugfx.HTML2COLOR(0x2b75c0)),
    ]

    PM2_5_LEVELS = [
        ('Hell',      76, ugfx.BLACK),
        ('Severe',    51, ugfx.HTML2COLOR(0xd3312e)),
        ('Very bad',  38, ugfx.HTML2COLOR(0xe35225)),
        ('Bad',       26, ugfx.HTML2COLOR(0xf78d1d)),
        ('Morderate', 21, ugfx.HTML2COLOR(0x329042)),
        ('Good',      16, ugfx.HTML2COLOR(0x12afc0)),
        ('Very good',  9, ugfx.HTML2COLOR(0x299cd5)),
        ('Best',       0, ugfx.HTML2COLOR(0x2b75c0)),
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

        lb, lv, color = levels[-1]
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

    
    def select_left_cb(self, pressed=True):
        if pressed:
            self.Voc = self.Voc - 0.01

    def select_right_cb(self, pressed=True):
        # pass
        if pressed:
            self.Voc = self.Voc + 0.01

    def select_a_cb(self, pressed=True):
        if pressed:
            self.SAMPLING_TIME = 200 # 280

    # Toggle mode
    def select_b_cb(self, pressed=True):
        if pressed:
            self.IS_GRAPH_MODE = not(self.IS_GRAPH_MODE)
            
            if self.IS_GRAPH_MODE:
                self.draw_graph()
            else:
                self.draw_legend()

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
        ind_height = 66
        container_height = height - ind_height

        self.indicator = ugfx.Container(0, 0, width, ind_height, style=styles.ibm_st)
        self.container = ugfx.Container(0, ind_height, width, container_height, style=styles.ibm_st)

        self.graph_basepos = container_height - 5
        
        # Sensor
        self.dust_sensor = gp2y1014au.GP2Y1014AU(iled=32, vo=36, K=0.5, Voc=0.6)
        
        # Smooth
        self.Vos = 0

    def run(self):

        # Show window
        self.indicator.show()
        self.container.show()

        # Title
        self.indicator.area(0, 0, self.indicator.width(), self.indicator.height(), ugfx.BLACK)
        ugfx.string_box(0, 0, self.indicator.width(), self.indicator.height(), 'PM10 Dust Monitor', 'IBMPlexMono_Bold24', ugfx.WHITE, ugfx.justifyCenter)

        if not self.IS_GRAPH_MODE:
            self.draw_legend()

        # IoTF
        self.iotf = IoTFoundation()

        stime = time.ticks_ms()

        idx = 0
        sleep_time = 8000
        isStable = False
        begin_time = time.ticks_ms()
        while True:

            Vo = self.dust_sensor.readVo(self.SAMPLING_TIME, 40)
            # VoRaw = self.dust_sensor.readVoRaw(self.SAMPLING_TIME, 0)

            # Exponential Moving Average
            # https://www.investopedia.com/terms/e/ema.asp
            # EMA(t) = Value(t)*k + EMA(y) * (1-k)
            # k = 2 / (N+1)
            # k = 0.005 where N = 399
            self.Vos = Vo * 0.005 + self.Vos * 0.995

            dV = self.Vos - self.Voc
            if dV < 0:
                dV = 0
                if isStable:
                    self.Voc = self.Vos

            # Convert to Dust Density in units of ug/m3.
            dustDensity = dV / self.K * 100.0

            elapsed = (time.ticks_ms() - stime)
            #print('{}, {}, {}'.format(VoRaw, int(self.VosRaw), elapsed))

            stime = time.ticks_ms()
            if elapsed > 10:
                sleep_time -= 100
            elif elapsed < 10:
                sleep_time += 100

            time.sleep_us(sleep_time)

            # IoT
            self.iotf.process()

            # Next
            idx += 1

            # Not stable before 10 secs
            if not isStable:
                if (time.ticks_ms() - begin_time) < 10000:
                    # Wait...
                    sys.stdout.write(".")
                    if idx%80==0:
                        print('')
                    continue
                print('')
                isStable = True

            if idx % 400 == 0:
                idx = 0
                self.refresh_screen(self.Vos, self.Voc, dustDensity)
                # self.init_buttons()
                #print('{}, {}, {}, {}'.format(idx, elapsed, sleep_time, self.Vos))
    
    def y_scale(self, v):
        return int(v / self.scale_factor)

    def refresh_screen(self, Vo, Voc, dustDensity):

        # volist runs as ring buffer
        self.volist.append((int(Vo*1000), dustDensity))
        self.volist.pop(0)

        # Indicator
        status = self.getDensityInfo(dustDensity)
        
        self.indicator.area(0, 0, self.indicator.width(), self.indicator.height(), status['color'])
        self.indicator.text(3, 6, 'Vo: {}mV Voc:{}mV     {}us'.format(int(Vo*1000), int(Voc*1000), self.SAMPLING_TIME), ugfx.WHITE)
        self.indicator.text(3, 26, 'Density: {}ug/m3'.format(round(dustDensity, 1)), ugfx.WHITE)
        self.indicator.text(3, 46, '{} AQI: {}'.format('PM2.5' if self.IS_PM2_5 else 'PM10', status['label']), ugfx.WHITE)

        # IoT
                # self.iotf.send_dustinfo(int(Vo*1000), int(Voc*1000), round(dustDensity, 1))


        self.iotf.send_dustinfo({
            'vo': int(Vo*1000),
            'voc': int(Voc*1000), 
            'density': round(dustDensity, 1),
            'status': status['label'],
            'mode': 'PM2.5' if self.IS_PM2_5 else 'PM10'
        })

        # Graph
        if self.IS_GRAPH_MODE:
            self.draw_graph()

    def draw_graph(self):
        avos = abs(max(self.volist, key=lambda item:item[0])[0])
        width = self.container.width()
        height = self.container.height()

        # Scale
        if self.IS_AUTOSCALE:
            limits = self.graph_basepos - 10
            if avos > limits:
                self.scale_factor = int(avos / limits)+1
                if self.scale_factor != self.p_scale:
                    self.container.area(0, 0, width, height, ugfx.WHITE)
                self.p_scale = self.scale_factor

        # Graph
        # clear
        self.container.area(0, 0, width, height, ugfx.WHITE)
        py = self.graph_basepos
        px = 0
        for i, (v, d) in enumerate(self.volist):
            x = int (i / self.X_RESOLUTION * width )
            y = self.graph_basepos - self.y_scale(v)

            # Color
            lvcolor = self.getLevelColor(d)

            # draw
            # if i == self.idx+1:
            #     # clear oldest
            #     self.container.area(px, 0, x, self.graph_basepos, ugfx.WHITE)
            # else:
            #     # previous
            #     #container.thickline(px, py, x, y, lvcolor, 5, True)
            #     self.container.line(px, py, x, y, lvcolor)
            if i != 0:
                self.container.line(px, py, x, y, lvcolor)
            
            px = x
            py = y

        # baseline
        self.container.line(0, self.graph_basepos, width, self.graph_basepos, ugfx.BLACK)

        # ruler
        y = 0
        maxy = self.graph_basepos * self.scale_factor

        while y < maxy:
            scaled_y = self.y_scale(y)
            sy = self.graph_basepos  - scaled_y
            #self.container.line(0, sy, 20 if y%500 == 0 else 10, sy, ugfx.BLACK)
            self.container.line(width, sy, width-10, sy, ugfx.BLACK)
            if not y==0:
                self.container.text(width-32, sy, str(y), ugfx.RED)
            y += 100

    def draw_legend(self):
        self.container.area(0, 0, self.container.width(), self.container.height(), ugfx.BLACK)
        levels = self.PM2_5_LEVELS if self.IS_PM2_5 else self.PM10_LEVELS
        
        y_offset = self.container.height()
        h = 20
        pv = -1
        for i, (lb, lv, color) in enumerate(levels):
            self.container.area(0, y_offset-h, self.container.width(), h, color)
            self.container.text(3, y_offset-h+2, lb, ugfx.WHITE)

            if i != len(levels)-1:
                self.container.text(150, y_offset-h+2, str(lv), ugfx.WHITE)
            
            self.container.text(180, y_offset-h+2, " ~ ", ugfx.WHITE)

            if i != 0:
                self.container.text(200, y_offset-h+2, str(pv), ugfx.WHITE)
            else:
                self.container.text(270, y_offset-h+2, 'v1.0', ugfx.WHITE)

            pv = lv - 1            
            y_offset = y_offset - h

    def restart(self):
        util.run('dustapp')

    def exit(self):
        util.reboot()

