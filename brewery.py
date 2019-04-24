# Comments must be kept
import random
import pprint
import RPi.GPIO as GPIO
import dht11
import time
from slugify import UniqueSlugify

custom_slugify = UniqueSlugify()

class Element(object):
    """Element"""
    def __init__(self, name = "Element", **kwargs):
        super(Element, self).__init__()
        self.name = name
        self.slug = custom_slugify(kwargs.get("slug",name))


class Sensor(Element):
    """Sensor"""
    def __init__(self, name="GenericSensor", **kwargs):
        super(Sensor, self).__init__(name, **kwargs)
        self.kwargs = kwargs
        self.calibration = 1.0
        if "alarm" in kwargs:
            self.set_alarm(kwargs["alarm"])
        else:
            self.alarm = None

    def set_alarm(self, alarm):
        self.alarm = float(alarm)

    def get_value(self):
        self.update_value()
        return self.value * self.calibration

    def set_calibration(self, calibration):
        self.calibration = calibration

    def has_alarm(self):
        if self.alarm:
            return self.value >= self.alarm
        else:
            return False

    def register_command(self, command, callback, use_asterisk=False):
        if "factory" in self.kwargs:
            self.kwargs["factory"].register_command(command, callback, self.slug)
            if use_asterisk:
                self.kwargs["factory"].register_command(command, callback, "*")


class FlowSensor(Sensor):
    """FlowSensor"""
    def __init__(self, name="FlowSensor", **kwargs):
        super(FlowSensor, self).__init__(name, **kwargs)
        self.value = 0
        self.register_command("/flow", self.send_flow, use_asterisk=True)
        

    def update_value(self):
        self.value += 1
        if self.value > 1000:
            self.value = 0

    def send_flow(self, msg):
        return "Flow in "+str(self.name)+" is" + str(self.value)+" liters"

class TemperatureSensor(Sensor):
    """TemperatureSensor"""
    def __init__(self, name="TemperatureSensor", **kwargs):
        super(TemperatureSensor, self).__init__(name, **kwargs)
        self.register_command("/temp", self.send_temp, use_asterisk=True)
        # TODO: /setalarm <sensor> <value>
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        # read the pin off the sensor in the lleidabeer.yaml
        if "gpio" in kwargs:
            self.instance = dht11.DHT11(pin = int(kwargs["gpio"]))
            self.result= self.instance.read()
        else:
            self.instance = None
        self.value=-100


    def update_value(self):
        if self.instance:
            self.result= self.instance.read()
            
            if self.result.is_valid():
                self.value = self.result.temperature
                         
            else:
                #  print('no valid')
                #  print(self.result.error_code)
                pass
        else:
            self.value = -100
       

    def send_temp(self, msg):
        return str(self.name)+" temperature is " + str(self.value)

class CO2Sensor(Sensor):
    """CO2Sensor"""
    def __init__(self, name="CO2Sensor",  **kwargs):
        super(CO2Sensor, self).__init__(name, **kwargs)
        self.register_command("/co2", self.send_co2, use_asterisk=True)

    def update_value(self):
        self.value = random.random()*100.0

    def send_co2(self, msg):
        return str(self.name)+" CO2 is" + str(self.value)

# TODO: add kwargs and name to active elements
class ActiveElement(Element):
    """ActiveElement"""
    def __init__(self, name="GenericActiveElement", **kwargs):
        super(ActiveElement, self).__init__(name, **kwargs)
        self.kwargs = kwargs

    def turn_on(self):
        self.activate(True)
        self.state = True

    def turn_off(self):
        self.activate(False)
        self.state = False

    def get_state(self):
        return self.state
    
    def register_command(self, command, callback, use_asterisk=False):
        if "factory" in self.kwargs:
           self.kwargs["factory"].register_command(command, callback, self.slug)
           if use_asterisk:
                self.kwargs["factory"].register_command(command, callback, "*")

class Heater(ActiveElement):
    """Heater"""
    def __init__(self, name="HeaterElement", **kwargs):
        super(Heater, self).__init__(name, **kwargs)
        self.register_command("/onheater", self.activate, use_asterisk=True)
        self.register_command("/offheater", self.deactivate, use_asterisk=True)
        GPIO.setmode(GPIO.BCM)
        
        if "gpio" in kwargs:
            self.pinheater  = int(kwargs["gpio"])         
        else:
            self.instance = None
        
        GPIO.setup(self.pinheater, GPIO.OUT)                      
        
    def activate(self, msg):
            GPIO.output(self.pinheater, True)   
            return("The Heater relay is ON")

    def deactivate(self, msg):
            GPIO.output(self.pinheater, False)
            return("The Heater relay is OFF")

class Mixer(ActiveElement):
    """Mixer"""
    def __init__(self, name="MixerElement", **kwargs):
        super(Mixer, self).__init__(name, **kwargs)
        self.state = False

    def activate(self, new_state):
        if new_state:
            print("X")
        else:
            print(" ")

class Valve(ActiveElement):
    """Valve"""
    def __init__(self, name="ValveElement", **kwargs):
        super(Valve, self).__init__(name, **kwargs)
        self.state = False

    def activate(self, new_state):
        if new_state:
            print("O")
        else:
            print(".")






if __name__ == "__main__":
    t = TemperatureSensor()
    print(t.get_value())

    f = FlowSensor()
    f.set_calibration(2.0)
    print(f.get_value())

    v = Valve()
    v.turn_on()
    v.turn_off()
    v.turn_on()

    h = Heater()
    m = Mixer()
