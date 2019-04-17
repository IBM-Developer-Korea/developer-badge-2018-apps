import ujson as json
import uos
import sys
import util
import network
import utime as time
import urequests
import ugfx

from machine import Pin, ADC, PWM

from gasapp.buzzer import Buzzer

from home import styles


class GasMain():

    # Config
    IS_PM2_5 = True
    IS_GRAPH_MODE = True # False
    IS_AUTOSCALE = True
    REFRESH_RATE = 1000 # 200

    STABILIZATION_TIME = 5000
    SAMPLING_TIME = 200 # 280
    threshold = 1000

    # Levels
    X_RESOLUTION = 40 # 320
    volist = [(0, 0)] * X_RESOLUTION

    # scale_factor
    scale_factor = 1 if IS_AUTOSCALE else 10
    p_scale = scale_factor

    def getDensityInfo(self, density):
        # TODO: Implement density info
        return {
            'label': 'Label',
            'level': 'Level',
            'color': ugfx.HTML2COLOR(0x2b75c0)
        }

    def getLevelColor(self, density):
        return ugfx.HTML2COLOR(0x2b75c0)
    
    def select_up_cb(self, pressed=True):
        if pressed:
            self.threshold += 100

    def select_down_cb(self, pressed=True):
        if pressed:
            self.threshold -= 100

    
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
        self.gas_sensor = ADC(Pin(34))
        self.gas_sensor.atten(ADC.ATTN_11DB)
        self.gas_sensor.width(ADC.WIDTH_12BIT)
        
        # Smooth
        self.Vos = 0

        # Buzzer
        self.buzzer = Buzzer()

    def showTitleText(self, text):
        self.indicator.area(0, 0, self.indicator.width(), self.indicator.height(), ugfx.BLACK)
        ugfx.string_box(0, 0, self.indicator.width(), self.indicator.height(), text, 'IBMPlexMono_Bold24', ugfx.WHITE, ugfx.justifyCenter)

    def run(self):

        # Show window
        self.indicator.show()
        self.container.show()

        # Title
        # self.indicator.area(0, 0, self.indicator.width(), self.indicator.height(), ugfx.BLACK)
        # ugfx.string_box(0, 0, self.indicator.width(), self.indicator.height(), 'AQI Gas Monitor', 'IBMPlexMono_Bold24', ugfx.WHITE, ugfx.justifyCenter)
        self.showTitleText('AQ Gas Monitor')

        time.sleep(1)
        self.showTitleText('Intializing...')

        stime = time.ticks_ms()

        idx = 0
        sleep_time = 8000
        isStable = False
        begin_time = time.ticks_ms()
        while True:

            VoRaw = self.gas_sensor.read()

            # Exponential Moving Average
            # https://www.investopedia.com/terms/e/ema.asp
            # EMA(t) = Value(t)*k + EMA(y) * (1-k)
            # k = 2 / (N+1)
            # k = 0.005 where N = 399
            self.Vos = VoRaw * 0.005 + self.Vos * 0.995

            # TODO: Convert to Gas Density in units of ug/m3.
            gasDensity = 0

            elapsed = (time.ticks_ms() - stime)

            stime = time.ticks_ms()
            if elapsed > 10:
                sleep_time -= 100
            elif elapsed < 10:
                sleep_time += 100

            time.sleep_us(sleep_time)
            
            # Next
            idx += 1

            # Not stable before 10 secs
            if not isStable:
                if (time.ticks_ms() - begin_time) < self.STABILIZATION_TIME:
                    # Wait...
                    if idx%6==0:
                        # self.showTitleText('Intializing...')
                        x = 240
                        self.indicator.area(x, 0, self.indicator.width()-x, self.indicator.height(), ugfx.BLACK)
                    else:
                        # self.showTitleText('Intializing...')
                        ugfx.string_box(0, 0, self.indicator.width(), self.indicator.height(), 'Intializing...', 'IBMPlexMono_Bold24', ugfx.WHITE, ugfx.justifyCenter)

                    sys.stdout.write(".")
                    if idx%80==0:
                        print('')
                    continue
                print('')
                isStable = True

            if idx % 100 == 0:
                idx = 0
                self.refresh_screen(int(self.Vos), self.threshold, gasDensity)
                if self.Vos > self.threshold:
                    self.buzzer.beep(int(self.Vos))
                    pass
                else:
                    self.buzzer.mute()
                    pass
    
    def y_scale(self, v):
        return int(v / self.scale_factor)

    def refresh_screen(self, VoRaw, threshold, gasDensity):

        # volist runs as ring buffer
        self.volist.append((VoRaw, gasDensity))
        self.volist.pop(0)

        # Indicator
        status = self.getDensityInfo(gasDensity)
        
        self.indicator.area(0, 0, self.indicator.width(), self.indicator.height(), status['color'])
        self.indicator.text(3, 6, 'VoRaw: {} threshold: {}'.format(VoRaw, threshold), ugfx.WHITE)
        self.indicator.text(3, 26, 'Density: {}ug/m3'.format(round(gasDensity, 1)), ugfx.WHITE)

        # Graph
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
        steps = 5
        step = int(maxy/steps/50)*50
        if step < 100:
            step = 100

        while y < maxy:
            scaled_y = self.y_scale(y)
            sy = self.graph_basepos  - scaled_y
            #self.container.line(0, sy, 20 if y%500 == 0 else 10, sy, ugfx.BLACK)
            self.container.line(width, sy, width-10, sy, ugfx.BLACK)
            if not y==0:
                tw = 42 if y >=1000 else 32
                self.container.text(width-tw, sy, str(y), ugfx.RED)
            y += step

    def restart(self):
        util.run('gasapp')

    def exit(self):
        util.reboot()

