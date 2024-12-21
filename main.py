# *****************************************************************************
# * | File        :   epd4in2_V2.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2023-09-13
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:s
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from machine import Pin,I2C,RTC
import utime
from drivers.ahtx0 import AHT20
from drivers.bme280 import BME280
import uasyncio as asyncio
import private
import ujson as json
import urequests
from drivers.epaper_4in2 import EPD_4in2
import _thread
import struct
import usocket

epaper_info = False
epd = EPD_4in2(epaper_info)
DisplayMode,DisplayModeNum = 0,2
DisplayMode0,DisplayMode0Num = 0,2
DisplayActivity = False
NetworkActivity = False
sw0 = Pin(15,Pin.IN,Pin.PULL_UP)
sw1 = Pin(17,Pin.IN,Pin.PULL_UP)
i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
aht21 = AHT20(i2c)
bme = BME280(i2c = i2c)
send_interval_ms = 60000
WifiSsid = private.SSID
WifiPass = private.PASSWORD
rtc = RTC()
GmoPublicApiURL = "https://forex-api.coin.z.com/public/v1/ticker"
GmoPublicApi_json = {}
CoincheckApiURL = "https://coincheck.com/api/ticker"
CoincheckApi_json = {}
OpenWeatherApiKey = private.OpenWeatherApiKey
OpenWeatherApiCity = private.OpenWeatherCity
OpenWeatherURL = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&lang=ja&units=metric".format(OpenWeatherApiCity,OpenWeatherApiKey)
OpenWeatherApi_json = {}
host = "ntp.nict.jp"
JAPAN_TIME = 9*60*60
timeout = 2
latest_data = {"aht":-1,"bme":-1,"hum":-1,"prs":-1,"temp":-1}

def LoadingScreen(epd,I2C_status):
    global DisplayActivity
    DisplayActivity = True
    epd.image1Gray.fill_rect(0,0,400,300,epd.white)
    epd.image1Gray.large_text(str(I2C_status),100,138,3,epd.black)
    epd.EPD_4IN2_V2_PartialDisplay(epd.buffer_1Gray)
    print("Loading Screen is finished.")
    DisplayActivity = False

def wifi_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WifiSsid, WifiPass)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

def SetRTC():
    global rtc,host,JAPAN_TIME,NetworkActivity
    NetworkActivity = True
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    while True:
        try:
            addr = usocket.getaddrinfo(host, 123)[0][-1]
            s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
            s.settimeout(timeout)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
            s.close()
            val = struct.unpack("!I", msg[40:44])[0]

            EPOCH_YEAR = utime.gmtime(0)[0]
            if EPOCH_YEAR == 2000:
                # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
                NTP_DELTA = 3155673600
            elif EPOCH_YEAR == 1970:
                # (date(1970, 1, 1) - date(1900, 1, 1)).days * 24*60*60
                NTP_DELTA = 2208988800
            else:
                raise Exception("Unsupported epoch: {}".format(EPOCH_YEAR))
            t = val - NTP_DELTA
            tm = utime.gmtime(t + JAPAN_TIME)
            print("GET:",tm)
            RTC().datetime((tm[0], tm[1], tm[2],tm[6]+1, tm[3], tm[4], tm[5],  0))
            print("SetRTC is completed.")
            break
        except Exception as e:
            print("SetRTC_ERROR: {} Type: {}".format(e,type(e)))
            print(rtc.datetime())
            utime.sleep_ms(500)
            wifi_connect()
            utime.sleep_ms(500)
    NetworkActivity = False

def GetGmoPublic():
    global GmoPublicApi_json,NetworkActivity
    NetworkActivity = True
    while True:
        try:
            raw_res = urequests.get(GmoPublicApiURL)
            GmoPublicApi_json = raw_res.json()
            print("GetGmoPublic is completed.")
            break
        except Exception as e:
            print("GetGmoPublic_ERROR: {} Type: {}".format(e,type(e)))
            print(rtc.datetime())
            utime.sleep_ms(500)
            wifi_connect()
            utime.sleep_ms(500)
    NetworkActivity = False

def GetCoincheck():
    global CoincheckApi_json,NetworkActivity
    NetworkActivity = True
    while True:
        try:
            raw_res = urequests.get(CoincheckApiURL)
            CoincheckApi_json = raw_res.json()
            print("GetCoincheck is completed.")
            break
        except Exception as e:
            print("GetCoincheck_ERROR: {} Type: {}".format(e,type(e)))
            print(rtc.datetime())
            utime.sleep_ms(500)
            wifi_connect()
            utime.sleep_ms(500)
    NetworkActivity = False

def GetOpenWeather():
    global OpenWeatherApi_json,NetworkActivity
    NetworkActivity = True
    while True:
        try:
            raw_res = urequests.get(OpenWeatherURL)
            OpenWeatherApi_json=raw_res.json()
            print("GetOpenWeather is completed.")
            break
        except Exception as e:
            print("GetOpenweather_ERROR: {} Type: {}".format(e,type(e)))
            print(rtc.datetime())
            utime.sleep_ms(500)
            wifi_connect()
            utime.sleep_ms(500)
    NetworkActivity = False

def I2C_scanner():
    print("start debugging")
    print("scanning...")
    i2c_list = i2c.scan()
    print("scan ok")
    for i in range(len(i2c_list)):
        print("found device address is :",hex(i2c_list[i]))
    if len(i2c_list)==2:
        return "Loading..."
    else:
        print("couldn't find i2c device.({})".format(len(i2c_list)))
        return "I2C ERROR"

def GetSenserNum(data):
    if(data["aht"]==data["bme"] and data["bme"]==data["prs"] and data["prs"]==data["hum"] and data["hum"]==0):
        data["aht"]+=aht21.temperature
        data["bme"]+=bme.values[0]
        data["hum"]+=aht21.relative_humidity
        data["prs"]+=bme.values[1]
    data["aht"]+=aht21.temperature
    data["bme"]+=bme.values[0]
    data["hum"]+=aht21.relative_humidity
    data["prs"]+=bme.values[1]
    data["aht"]=round(data["aht"]/2,1)
    data["bme"]=round(data["bme"]/2,1)
    data["hum"]=round(data["hum"]/2,1)
    data["prs"]=round(data["prs"]/2,1)
    data["temp"]=round((data["aht"]+data["bme"])/2,1)

def Display_epaper(epd,data,first=False):
    global DisplayActivity
    DisplayActivity = True
    if epaper_info and not first:
        print("--- Start drawing to the screen... ---")
    time_now = rtc.datetime()
    h,m = str(time_now[4]),str(time_now[5])
    if len(h)==1:
        h="0"+h
    if len(m)==1:
        m="0"+m

    if DisplayMode == 0:
        epd.image1Gray.fill_rect(0,10,400,80,epd.white)
        epd.image1Gray.large_text(str(time_now[0]),5,10,2,epd.black)
        epd.image1Gray.large_text(str(time_now[1])+"/"+str(time_now[2]),5,50,2,epd.black)
        epd.image1Gray.large_text(h+":"+m,90,10,8,epd.black)
        epd.image1Gray.fill_rect(0,100,400,80,epd.white)
        if DisplayMode0 == 0:
            epd.image1Gray.large_text("USD/JPY:", 20, 105, 2,epd.black)
            epd.image1Gray.large_text("BTC/JPY:", 20, 145, 2,epd.black)
            if not str(GmoPublicApi_json["status"]) == "0":
                epd.image1Gray.large_text("-",187,105,2,epd.black)
            else:
                epd.image1Gray.large_text(str(round((float(GmoPublicApi_json["data"][0]["ask"])+float(GmoPublicApi_json["data"][0]["bid"]))/2,1)),155,105,2,epd.black)
            epd.image1Gray.large_text(str(round((float(CoincheckApi_json["ask"])+float(CoincheckApi_json["bid"]))/2)),155,145,2,epd.black)
        else:
            pass
        epd.image1Gray.fill_rect(100,200,110,100,epd.white)
        epd.image1Gray.large_text("Temp:", 10, 200, 2,epd.black)
        epd.image1Gray.large_text("Hum:", 10, 240, 2,epd.black)
        epd.image1Gray.large_text("Prs:", 10, 280, 2,epd.black)
        epd.image1Gray.large_text(str(data["temp"]), 100, 200, 2,epd.black)
        epd.image1Gray.large_text(str(data["hum"]), 100, 240, 2,epd.black)
        epd.image1Gray.large_text(str(data["prs"]), 100, 280, 2,epd.black)
        epd.image1Gray.fill_rect(210,200,190,200,epd.white)
        epd.image1Gray.large_text(str(OpenWeatherApi_json["weather"][0]["main"]),230,200,2,epd.black)
        epd.image1Gray.large_text("max: "+str(OpenWeatherApi_json["main"]["temp_max"]),230,240,2,epd.black)
        epd.image1Gray.large_text("min: "+str(OpenWeatherApi_json["main"]["temp_min"]),230,280,2,epd.black)
        epd.EPD_4IN2_V2_PartialDisplay(epd.buffer_1Gray)
    else:
        epd.image1Gray.fill_rect(0,10,400,80,epd.white)
        epd.image1Gray.large_text(str(time_now[0]),5,10,2,epd.black)
        epd.image1Gray.large_text(str(time_now[1])+"/"+str(time_now[2]),5,50,2,epd.black)
        epd.image1Gray.large_text(h+":"+m,90,10,8,epd.black)
        epd.image1Gray.fill_rect(0,90,400,400,epd.white)
        epd.image1Gray.hline(0,85,400,epd.black)
        epd.EPD_4IN2_V2_PartialDisplay(epd.buffer_1Gray)
        
    if epaper_info and not first:
        print("--- Display_epaper is finished. ---")
    DisplayActivity = False

def Display_epaper_first(epd):
    global latest_data
    if epaper_info:
        print("--- Start drawing to the screen... ---")
    data = {"aht":0,"bme":0,"hum":0,"prs":0,"temp":0}
    for i in range(3):
        GetSenserNum(data)
        utime.sleep_ms(100)
    latest_data = data
    Display_epaper(epd,data,True)
    if epaper_info:
        print("--- Display_epaper_first is finished. ---")

async def MainLoop():
    print("start MainLoop")
    global latest_data,epd
    epd.image1Gray.fill(0xff)
    epd.image4Gray.fill(0xff)
    GetOpenWeather()
    GetGmoPublic()
    GetCoincheck()
    SetRTC()
    while DisplayActivity or NetworkActivity:
        utime.sleep_ms(100)
    _thread.start_new_thread(Display_epaper_first,(epd,))
    data = {"aht":0,"bme":0,"hum":0,"prs":0,"temp":0}
    #print(rtc.datetime(),"\n")
    #print("now is {}s. wait for {}s".format(rtc.datetime()[6],60-int(rtc.datetime()[6])))
    await asyncio.sleep(60-int(rtc.datetime()[6]))
    RTC_time = rtc.datetime()
    while True:
        start = utime.ticks_ms()
        RTC_time_now = rtc.datetime()
        time_difference,get_senser_num = False,False
        if RTC_time_now[2] != RTC_time[2]:
            #毎日0時0分(前と日付が異なるとき)に実行
            pass
        if RTC_time_now[4] != RTC_time[4]:
            #毎時0分(前と時間が異なるとき)に実行
            time_difference = True
            GetOpenWeather()
            SetRTC()
        if (RTC_time_now[6]-RTC_time[6])%10==0:
            #十秒おき(前との時差を10で割った余りが0)に実行
            get_senser_num = True
            GetSenserNum(data)
        if RTC_time_now[5] != RTC_time[5]:
            #毎分0秒(前と何分かの値が異なるとき)に実行
            time_difference = True
            latest_data = data
            data = {"aht":0,"bme":0,"hum":0,"prs":0,"temp":0}
            if RTC_time_now[5]%10==0:
                GetGmoPublic()
                GetCoincheck()
        if time_difference:
            #print("refresh display",RTC_time_now,rtc.datetime())
            while DisplayActivity or NetworkActivity:
                await asyncio.sleep_ms(100)
            _thread.start_new_thread(Display_epaper,(epd,latest_data))
            RTC_time = RTC_time_now
            #print(str(utime.ticks_diff(utime.ticks_ms(), start))+"ms")
        if get_senser_num:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep_ms(100)
async def BottonGetLoop():
    print("start BottonGetLoop")
    global DisplayMode,DisplayMode0
    SW0,SW1 = [1 for i in range(3)],[1 for i in range(3)]
    SW0_diff,SW1_diff = [True,True],[True,True]
    while True:
        SW0.append(sw0.value())
        SW1.append(sw1.value())
        del SW0[0]
        del SW1[0]
        SW0_value,SW1_value = 1 in SW0,1 in SW1#反転
        SW0_diff.append(SW0_value)
        SW1_diff.append(SW1_value)
        del SW0_diff[0]
        del SW1_diff[0]
        if SW0[2] == 1:
            SW0_value = True
        if SW1[2] == 1:
            SW1_value = True

        if not SW0_value and SW1_value and SW0_diff[0]!=SW0_diff[1] and not SW0[2] and SW1[2]:
            print("SW0 が押されています")

        if SW0_value and not SW1_value and SW1_diff[0]!=SW1_diff[1] and SW0[2] and not SW1[2]:
            print("SW1 が押されています")
            if DisplayMode == 0:
                print("change mode0")
                DisplayMode0 = (DisplayMode0+1)%DisplayMode0Num
                while DisplayActivity or NetworkActivity:
                    await asyncio.sleep_ms(100)
                _thread.start_new_thread(Display_epaper,(epd,latest_data))

        if not SW0_value and not SW1_value and (SW0_diff[0]!=SW0_diff[1] or SW1_diff[0]!=SW1_diff[1]):
            print("SW0とSW1が同時押しされています")
            print("change mode")
            DisplayMode = (DisplayMode+1)%DisplayModeNum
            while DisplayActivity or NetworkActivity:
                await asyncio.sleep_ms(100)
            _thread.start_new_thread(Display_epaper,(epd,latest_data))

        await asyncio.sleep_ms(100)

if __name__=='__main__':
    epd.EPD_4IN2_V2_Init()
    LoadingScreen(epd,I2C_scanner())
    wifi_connect()
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(MainLoop())
    event_loop.create_task(BottonGetLoop())
    event_loop.run_forever()
