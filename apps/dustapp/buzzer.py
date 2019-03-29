from machine import Pin
from machine import PWM
import time

class Buzzer():

    B0  = 31; C1  = 33; CS1 = 35; D1  = 37; DS1 = 39; E1  = 41; F1  = 44; FS1 = 46; G1  = 49; GS1 = 52; A1  = 55; AS1 = 58; B1  = 62;
    C2  = 65; CS2 = 69; D2  = 73; DS2 = 78; E2  = 82; F2  = 87; FS2 = 93; G2  = 98; GS2 = 104; A2  = 110; AS2 = 117; B2  = 123; C3  = 131;
    CS3 = 139; D3  = 147; DS3 = 156; E3  = 165; F3  = 175; FS3 = 185; G3  = 196; GS3 = 208; A3  = 220; AS3 = 233; B3  = 247; C4  = 262; CS4 = 277;
    D4  = 294; DS4 = 311; E4  = 330; F4  = 349; FS4 = 370; G4  = 392; GS4 = 415; A4  = 440; AS4 = 466; B4  = 494; C5  = 523; CS5 = 554; D5  = 587;
    DS5 = 622; E5  = 659; F5  = 698; FS5 = 740; G5  = 784; GS5 = 831; A5  = 880; AS5 = 932; B5  = 988; C6  = 1047; CS6 = 1109; D6  = 1175; DS6 = 1245;
    E6  = 1319; F6  = 1397; FS6 = 1480; G6  = 1568; GS6 = 1661; A6  = 1760; AS6 = 1865; B6  = 1976; C7  = 2093; CS7 = 2217; D7  = 2349; DS7 = 2489; E7  = 2637;
    F7  = 2794; FS7 = 2960; G7  = 3136; GS7 = 3322; A7  = 3520; AS7 = 3729; B7  = 3951; C8  = 4186; CS8 = 4435; D8  = 4699; DS8 = 4978;

    def __init__(self):
        self.notes = {
            'cdef': [
                self.C6, self.D6, self.E6, self.F6, self.G6, self.A6, self.B6, self.C7, self.D7, self.E7, self.F7, self.G7, self.A7, self.B7, self.C8, 0
            ],
            'mario': [
                self.E7, self.E7,  0, self.E7,  0, self.C7, self.E7,  0, self.G7,  0,  0,  0, self.G6,  0,  0,  0,
                self.C7,  0,  0, self.G6,  0,  0, self.E6,  0,  0, self.A6,  0, self.B6,  0, self.AS6, self.A6, 0,
                self.G6, self.E7,  0, self.G7, self.A7,  0, self.F7, self.G7,  0, self.E7,  0, self.C7, self.D7, self.B6,  0,  0,
                self.C7,  0,  0, self.G6,  0,  0, self.E6,  0,  0, self.A6,  0, self.B6,  0, self.AS6, self.A6, 0,
                self.G6, self.E7,  0, self.G7, self.A7,  0, self.F7, self.G7,  0, self.E7,  0, self.C7, self.D7, self.B6,  0,  0
            ],
            'starwars': [
                self.A4,  0,  0,  0, self.A4,  0,  0,  0, self.A4,  0,  0,  0, self.F4,  0,  0, self.C5,
                self.A4,  0,  0,  0, self.F4,  0,  0, self.C5, self.A4,  0,  0,  0,  0,  0,  0,  0,
                self.E5,  0,  0,  0, self.E5,  0,  0,  0, self.E5,  0,  0,  0, self.F5,  0,  0, self.C5,
                self.GS4, 0,  0,  0, self.F4,  0,  0, self.C5, self.A4,  0,  0,  0,  0,  0,  0,  0,
            ],
        }

    def playnotes(self, title, length=150, duty=64):
        # Init
        p = Pin(27, Pin.OUT)
        self.pwm = PWM(p)
        self.pwm.duty(0)

        if title not in self.notes:
          print('unknown title: {}'.format(title))
          return

        melody = self.notes[title]
        print('Play', title)
        for i in melody:
            if i == 0:
                self.pwm.duty(0)
            else:
                self.pwm.freq(i)
                self.pwm.duty(duty)
            time.sleep_ms(length)

        # deinit
        self.pwm.deinit()