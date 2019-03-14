# 미세먼지 센서 사용해보기

Developer Day 2018 뱃지는 마이크로 파이썬이 포팅되어 다양하게 활용 될 수 있습니다. Developer Day 2018 행사와 meetup을 통해 나누어드린 각종 센서도 연결하여 사용 할 수 있습니다. 이 글에서는 다양한 센서중 미세먼지 센서를 어떻게 뱃지와 연결하고 또 소프트웨어는 어떻게 작성하는지에 대해 알려드리고자 합니다.

## 준비 사항

마이크로 파이썬 WebREPL 개발 환경이 준비되지 않은 경우 [REPL & WebREPL 가이드](../repl/README.md)를 참고하여 준비해 주어야 합니다.

Developer Badge Firmware v2.3을 기반으로 설명합니다. 하위 버젼인 경우 [IoT 뱃지 위에 ROM 설치하기](../firmware/README.md)를 참고하여 롬 업그레이드를 해 주셔야 합니다.

그리고, 미세먼지 센서를 Developer Day 2018 뱃지와 연결하려면 **실납(lead)** 과 이를 이용할 **납땜인두(iron)** 가 필요합니다. *인두 사용시 **화상**을 입을 수 있으므로 주의 하시기 바랍니다*.

## 센서 정보

미세먼지 센서는 Sharp 전자의 **GP2Y1014AU0F** 제품입니다. 같은 회사의 미세먼지 센서인 **GP2Y1010AU** 의 개선품이라고 합니다. 거의 동일한 특성을 가지고 있고 참고 자료는 더 많으므로 이를 활용하는 것도 좋습니다.

* http://www.sharp-world.com/products/device/lineup/data/pdf/datasheet/gp2y1010au_appl_e.pdf

GP2Y1014AU0F 센서는 PM2.5 까지 측정이 가능하며, 공기 중 적외선 투과도를 측정하여 대기 중 먼지 밀도를 측정하는 센서입니다. 센서에 대한 상세 규격 정보는 아래와 같이 각 제품 공급 홈페이지에서 확인 할 수 있으니 참고 하기 바랍니다.

* [DigiKey](https://www.digikey.kr/product-detail/ko/sharp-socle-technology/GP2Y1014AU0F/1855-1013-ND/7674923)
* [Mouser](https://kr.mouser.com/ProductDetail/Sharp-Microelectronics/GP2Y1014AU0F?qs=rrS6PyfT74eynj5J61tvwA%3D%3D)
* [LCSC](https://lcsc.com/product-detail/Sensor-Modules_Sharp-Microelectronics-GP2Y1014AU0F_C134069.html)
* [Device Mart](https://www.devicemart.co.kr/goods/view?no=1327422)

> ※ 참고 사항  
> Developer Day 2018 뱃지의 동작 전원은 3.3V이고 GP2Y1014AU0F는 5V입니다. 일반적인 경우라면 3.3-5V 레벨 변환 회로가 필요합니다. 그러나, 레벨 변환 회로 구성에 따른 전반적인 복잡도 증가 및 GP2Y1014AU0F가 3.3V 환경에서도 어느정도 일정한 결과가 나오는 것을 확인했기에, Developer Day 2018 뱃지에는 별도의 레벨 변환 회로 없이 구성 되었습니다.

## 하드웨어 구성

위의 제품 규격 문서에는 이 센서의 사용 방법과 테스트 조건 및 환경에 대한 정보가 있으므로 이를 참고합니다. 아래는 GP2Y1014AU0F의 내부 구성에 대한 그림입니다. 

![constitution diagram](img/diagram1.jpg)

간략히 설명하면, LED라는 모듈에서 전원을 공급하여 빛(LED)을 쏘면 대기중 먼지 밀도에 따른 빛 투과량을 `Light detector`가 감지하고 이를 전기적 신호로 변환하여 `Vo` 핀으로 내보냅니다. 이 `Vo`의 전압을 측정하여 대기중 먼지 밀도로 변환하는 방식으로 구성합니다.

다음과 같이 회로를 구성합니다. 회로 자체는 그리 복잡하지 않지만 미세먼지 센서 이외 150옴 저항, 220마이크로 패럿 콘덴서가 추가로 필요합니다. 

![circuit diagram](img/diagram2.jpg)

Developer Day 2018 뱃지에는 여러가지 센서를 바로 붙여서 사용 할 수 있도록 준비되어 있는데 미세먼지 센서용 저항 150이 내장되어 있으므로 먼지 센서 연결선 6개 핀과 콘덴서만 추가해 주면 됩니다.

![package](img/package.jpg)

아래 회로도는 먼지 센서와 콘덴서가 연결되는 부분입니다.

![badge dust port](img/dust-sch.jpg)

콘덴서는 J14, 6핀 커넥터는 J11로 연결됩니다.

![badge dust sensor port](img/badge-port.jpg)

패키지의 콘덴서는 아래 그림과 같이 회색 표시가 된 부분을 보이도록 하여 납땜 합니다.

![capacitor connection](img/capacitor.jpg)

그리고, 케이블은 다음과 같은 순서로 연결하여 땜질합니다.

![](img/cable-to-board.jpg)

케이블은 먼지 센서와 연결되는 케이블의 순서에 맞추어야 합니다. 

![](img/cable-pinout.jpg))

납땜으로 연결된 모습은 아래와 같습니다.

![](img/cabling.jpg))

이제 케이블 커넥터를 미세먼지 센서와 연결합니다. 커넥터의 방향이 있으나 아래와 같은 방향으로 연결합니다.

![](img/connector-to-sensor.jpg)

## 소프트웨어

소프트웨어도 하드웨어와 마찬가지로 센서 규격 문서의 내용을 참고합니다. 

### ILED 동작

문서에는 10ms 주기로 0.32ms 동안 LED를 점멸하는 펄스(Pulse) 방식으로 테스트 했다고 나와 있으므로 이를 활용하도록 합니다.

![](img/diagram3.jpg)

LED 회로는 Open Drain 방식으로 동작합니다. 따라서, ILED 값이 LOW면 LED가 켜지고, HIGH면 꺼지게 됩니다.

![](img/diagram4.jpg)

### Vo 값 확인

타이밍 정보를 보면 Vo 값의 안정화 된 값은 LED가 켜지고 0.28 ms 이후에 적정한 값이 나타나는 것을 볼 수 있습니다.

![](img/timing.jpg)

### 먼지 밀도 계산

출력된 Vo 값과 미세먼지 값의 관계는 센서의 규격 문서에 다음과 같이 나와 있습니다.

![](img/characteristics.jpg)

실제 그래프는 측정 값으로 만들어진 것으로 참고용이며, 전기 광학 특성에 대한 표는 다음과 같습니다.

![](img/electro-optical.jpg)

여기서 주목할만 부분은 민감도 `K` 값인데, 이 값이 0.5인 경우, 100 um/m3 당 0.5V씩 변하게 됩니다. 즉, 위 그래프에서 0~0.5 구간의 기울기로 볼 수 있습니다.

미세먼지 없음으로 판단할 `Voc` 값을 y축 절편으로 생각한다면 `Vo`와 `미세먼지 밀도 D`의 관계는 다음과 같은 식으로 볼 수 있습니다.

> Vo = K * D + Voc

그런데 K의 단위가 V/100ug/m3이므로 단위를 맞추려면 K 값에 100을 나누어야 합니다. 따라서,

> Vo = ( K / 100 ) * D + Voc

이를 Vo를 기준으로 변형하면

> D = ( Vo - Voc ) / ( K  / 100 )  

최종 수식은 다음과 같이 됩니다.

> D = ( Vo - Voc ) / K * 100


### 예제 코드

이를 종합한 Arduino 예제가 GitHub에 공개되어 있으므로 이를 참고합니다.

* https://github.com/sharpsensoruser/sharp-sensor-demos/blob/master/sharp_gp2y1014au0f_demo/sharp_gp2y1014au0f_demo.ino

위의 코드를 참고하여 Developer Day 2018 뱃지용 코드를 아래와 같이 작성 할 수 있습니다.

먼저, 센서가 연결된 Pin 정보를 입력합니다. LED On/Off용은 GPIO32번,센서의 Vo이 입력될 핀은 GPIO36번 입니다.

![badge dust port](img/dust-sch.jpg)

``` python
sharpLEDPin = Pin(32, Pin.OUT)
sharpVoPin = ADC(Pin(36))
```

그 다음은 ESP32용 Analog Digital Converter의 입력을 3.9V까지 입력 받을 수 있도록 11dB attenuation을 설정해 줍니다.

``` python
sharpVoPin.atten(ADC.ATTN_11DB)
```

ESP32는 ADC에 12비트를 사용하므로 최대 4095까지 검출됩니다. 따라서 이를 적용합니다.

``` python
Vo = VoRaw / 4095.0 * 5.0;
```

참고로, Vo 환산 시 3.3V이 아닌 5V를 기준으로 계산하는데 이는 이후 먼지 밀도 계산이 5V를 기준으로 되어 있기 때문에 이를 맞추기 위함입니다. 이렇게 얻어진 Vo 환산 값을 미세 먼지 밀도 변환식에 적용하여 최종 미세먼지 밀도 값을 얻게 됩니다.

완성된 예제 코드는 아래 소스 코드를 참고하시기 바랍니다.

* [예제 코드](dust.py)

그런데, 이 예제 코드로 실행하면 센서 측정 값이 안정되지 않고 들쭉 날쭉한 결과가 출력되는 것을 볼 수 있습니다. 이를 오실로스코프로 확인을 해 보면 Arduino 때와 보다 시간이 지연되는 현상이 발생하는 것을 볼 수 있습니다. 

![Sesnor signal](img/signal-upython.jpg)

더 확인해 보면 마이크로 파이쎤 코드가 실행되는 시간과 Vo 값을 읽기전 280us를 대기 시간이 실제로는 400us로 측정되는 것을 볼 수 있으며 이것이 원인이 됨을 알 수 있습니다.

결과적으로 마이크로 파이썬 특성상 마이크로초 단위 통제가 안되는 현상이라 어쩔 수 없지만, 약간의 트릭으로 지연 시간을 조정하여 일정한 값이 출력되도록 할 수 있습니다. 이는 다음 예제를 참고 하기 바랍니다.

* [예제 코드 - 타이밍 수정본](dust_adjusted.py)

그리고, GP2Y1014AU0F 센서의 특성으로 인해 고가의 센서에 비해서 안정된 값을 얻을 수 없는 것도 사실이다. 따라서, 영정 측정과 함께 이동 평균 값을 이용하여 노이즈를 제거한 값을 사용하면 보다 정확한 값을 얻을 수 있습니다. 이는 아래 링크의 정보를 참고 할 수 있습니다.

* [샤프 미세먼지 센서는 쓰레기가 아니었다 !!! - 새다리 종합 기록실
](https://m.blog.naver.com/twophase/221139319142)


* [예제 코드 - 이동 평균 적용본](dust_average.py)

그리고 Developer Day 2018 뱃지에 포팅된 마이크로 파이썬 펌웨어에 C언어로 구현된 미세먼지 센서 모듈을 추가하고 이를 python 코드에서 호출하여 타이밍을 안정화 하는 방법도 있는데 본 문서에서는 이 방법은 다루지 않으며 향후 펌웨어 업데이트에 맞춰 공개 할 예정입니다.


## 참고

* https://github.com/IBM-Developer-Korea/developer-badge-2018-pcb/blob/master/badge_schemetic_v1.0.pdf
* https://docs.micropython.org/en/latest/library/machine.ADC.html
* https://github.com/sharpsensoruser/sharp-sensor-demos/wiki/Application-Guide-for-Sharp-GP2Y1014AU0F-Dust-Sensor
* https://github.com/sharpsensoruser/sharp-sensor-demos/blob/master/sharp_gp2y1014au0f_demo/sharp_gp2y1014au0f_demo.ino
* https://docs.espressif.com/projects/esp-idf/en/latest/api-reference/peripherals/adc.html
* https://m.blog.naver.com/twophase/221139319142

* http://www.sharp-world.com/products/device/lineup/data/pdf/datasheet/gp2y1010au_appl_e.pdf
* http://www.sharp-world.com/products/device/lineup/data/pdf/datasheet/gp2y1010au_e.pdf
