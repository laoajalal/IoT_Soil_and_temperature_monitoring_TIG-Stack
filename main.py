from machine import Pin, ADC
from time import sleep
import dht
import ujson


'''
Calibrated soil estimate:

3.3V output

usage of volt dividers of 20k(ohm) and 10 k(ohm) which generates
an output voltage of 1.1V

Max ~ 850mV (dry)

Low ~ 250mV (in water)

'''


MAX_VOLTAGE = 850
MIN_VOLTAGE = 250

def read_sensors_and_publish(mqqt_broker):
    sensor_dht11 = dht.DHT11(Pin(13, mode=Pin.OPEN_DRAIN))
    pin = Pin(32, mode=Pin.IN)
    adc = ADC(pin, atten=ADC.ATTN_2_5DB)
    adc.width(ADC.WIDTH_10BIT)
    soil_sensor = adc

    while True:
        try:
            sleep(2)
            sensor_dht11.measure()
            temp = sensor_dht11.temperature()
            hum = sensor_dht11.humidity()

            moisture_in_soil = (MAX_VOLTAGE - soil_sensor.read()) * 100 / (MAX_VOLTAGE - MIN_VOLTAGE)
            print('Soil value: '+ str(moisture_in_soil) + "%")
            print('Temperature: %3.1f C' %temp)
            print('Humidity: %3.1f %%' %hum)

            publish_sensor_data(mqqt_broker, create_json(temperature=temp, humidity=hum, soil_moisture=moisture_in_soil), "weather")
            sleep(60)
        except OSError as e:
            print(e)
            print('Failed to read sensor.')


def create_json(**kwargs):
    try:
        print(dict(kwargs))
        return ujson.dumps(dict(kwargs))
    except Exception as e:
        return None

def publish_sensor_data(broker, data, topic):
    try:
        print(data)
        broker.publish(topic=topic, msg=data)
    except Exception as e:
        print("failed sending sensor data..")
