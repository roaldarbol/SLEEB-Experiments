from belay import Device

class PicoBonn(Device):
    def __post_init__(self, *args, **kwargs):
        self._temperature = None

    # ---- Setup and teardown of device ----- #

    @Device.setup(autoinit=True)
    def setup():
        import time
        import random
        import machine
        from machine import Pin, PWM
        from neopixel import NeoPixel
        from pimoroni_i2c import PimoroniI2C
        from breakout_bme68x import BreakoutBME68X
        from breakout_bh1745 import BreakoutBH1745

        # Init on-board stuff
        led = Pin('LED', Pin.OUT)
        temp_sensor = machine.ADC(4)
        conv = 3.3 / 65535

        # Breakout setup
        PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}
        I2C = PimoroniI2C(**PINS_BREAKOUT_GARDEN)
        bh1745 = BreakoutBH1745(I2C)
        bme688 = BreakoutBME68X(I2C)
        
        # NeoPixel setup - adjust pin number and LED count as needed
        NEOPIXEL_GPIO = 'GP22'  # Change this to match your wiring
        NUM_PIXELS = 16    # Change this to match your ring size
        neo_pin = Pin(NEOPIXEL_GPIO, Pin.OUT)
        np = NeoPixel(neo_pin, NUM_PIXELS)

        # Fan PWM setup
        FAN_PIN = 28
        fan_pwm = PWM(Pin(FAN_PIN))
        fan_pwm.freq(25000)  # 25kHz to avoid audible whine
        fan_pwm.duty_u16(0)  # Start with fan off
        
        bh1745.leds(False)
        led.value(False)

    @Device.teardown
    def teardown():
        bh1745.leds(False)
        led.value(False)

    # ----- Device methods ----- #
    # NeoPixels
    @Device.task
    def set_all_neopixels(r, g, b):
        """Set all NeoPixels to the same RGB color."""
        NUM_PIXELS = 16
        for i in range(NUM_PIXELS):
            np[i] = (r, g, b)
        np.write()

    @Device.task
    def clear_neopixels():
        """Turn off all NeoPixels."""
        NUM_PIXELS = 16
        for i in range(NUM_PIXELS):
            np[i] = (0, 0, 0)
        np.write()

    @Device.task
    def rainbow_static():
        """Display a static rainbow across all 16 LEDs."""
        NUM_PIXELS = 16
        colors = [
            (255, 0, 0),    # Red
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (127, 255, 0),  # Yellow-green
            (0, 255, 0),    # Green
            (0, 255, 127),  # Cyan-green
            (0, 255, 255),  # Cyan
            (0, 127, 255),  # Light blue
            (0, 0, 255),    # Blue
            (127, 0, 255),  # Purple
            (255, 0, 255),  # Magenta
            (255, 0, 127),  # Pink
            (255, 0, 0),    # Red (back to start)
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (127, 255, 0),  # Yellow-green
        ]
        
        for i in range(NUM_PIXELS):
            np[i] = colors[i]
        np.write()

    @Device.task
    def rainbow_cycle(cycles=3, delay_ms=50):
        """Animate a rainbow that cycles around the ring."""
        NUM_PIXELS = 16
        
        def wheel(pos):
            """Generate rainbow colors across 0-255 positions."""
            if pos < 85:
                return (pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                return (255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                return (0, pos * 3, 255 - pos * 3)
        
        for cycle in range(cycles * 256):
            for i in range(NUM_PIXELS):
                pixel_index = (i * 256 // NUM_PIXELS) + cycle
                np[i] = wheel(pixel_index & 255)
            np.write()
            time.sleep(delay_ms / 1000.0)

    @Device.task
    def rainbow_pulse(brightness=100):
        """Pulse through rainbow colors on all LEDs."""
        NUM_PIXELS = 16
        
        def wheel(pos):
            if pos < 85:
                return (pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                return (255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                return (0, pos * 3, 255 - pos * 3)
        
        for j in range(256):
            r, g, b = wheel(j)
            # Scale by brightness
            r = int(r * brightness / 255)
            g = int(g * brightness / 255)
            b = int(b * brightness / 255)
            
            for i in range(NUM_PIXELS):
                np[i] = (r, g, b)
            np.write()
            time.sleep(0.02)

    @Device.task
    def set_fan_speed(speed):
        """Set fan speed as percentage (0-100)."""
        if speed < 0:
            speed = 0
        if speed > 100:
            speed = 100
        
        # Convert percentage to duty cycle (0-65535)
        duty = int(speed * 65535 / 100)
        fan_pwm.duty_u16(duty)
        return f"Fan set to {speed}%"

    @Device.task
    def fan_on(speed=100):
        """Turn fan on at specified speed (default 100%)."""
        duty = int(speed * 65535 / 100)
        fan_pwm.duty_u16(duty)

    @Device.task
    def fan_off():
        """Turn fan off."""
        fan_pwm.duty_u16(0)

    @Device.task
    def fan_ramp_test():
        """Ramp fan speed up and down for testing."""
        # Ramp up
        for speed in range(0, 101, 10):
            duty = int(speed * 65535 / 100)
            fan_pwm.duty_u16(duty)
            time.sleep(0.5)
        
        # Ramp down
        for speed in range(100, -1, -10):
            duty = int(speed * 65535 / 100)
            fan_pwm.duty_u16(duty)
            time.sleep(0.5)
        
        return "Ramp test complete"


    @Device.task
    def set_led(state):
        print(f"Printing from device; turning LED to {state}.")
        Pin('LED', Pin.OUT).value(state)

    @Device.task
    def led_toggle():
        led.toggle()

    @Device.task
    def led_off():
        led.value()

    @Device.task
    def ir_led_on():
        ioe.output(LED_PIN, 1)

    @Device.task
    def ir_led_off():
        ioe.output(LED_PIN, 0)

    @Device.task
    def bh_led_toggle(state):
        bh1745.leds(state)

    @Device.task
    def read_light():
        rgbc_raw = bh1745.rgbc_raw()
        rgb_clamped = bh1745.rgbc_clamped()
        rgb_scaled = bh1745.rgbc_scaled()
        print("Raw: {}, {}, {}, {}".format(*rgbc_raw))
        print("Clamped: {}, {}, {}, {}".format(*rgb_clamped))
        print("Scaled: #{:02x}{:02x}{:02x}".format(*rgb_scaled))
        return list(rgb_scaled)

    @Device.task
    def read_environment():
        temperature, pressure, humidity, gas_resistance, status, gas_index, meas_index = bme688.read()
        # print("Temp: {}".format(temperature))
        # print("Pressure: {}".format(pressure))
        # print("Humidity: {}".format(humidity))
        return temperature

    # ----- Local wrappers ----- #

    def measure_temperature(self):
        # Runs on your computer - this is a regular method
        self._temperature = self.read_environment()
        return self._temperature

    @property
    def latest_temperature(self):
        # Now you can just return the cached value
        return self._temperature