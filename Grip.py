import time
import board
import analogio
import digitalio
import random

# --- Setup FSR ---
fsr = analogio.AnalogIn(board.A0)

# --- Setup LEDs (reversed order) ---
led_pins = [board.D11, board.D10, board.D9, board.D8, board.D7,board.D6, board.D5, board.D4, board.D3, board.D2]

leds = []
for pin in led_pins:
    led = digitalio.DigitalInOut(pin)
    led.direction = digitalio.Direction.OUTPUT
    leds.append(led)

# --- Setup button ---
button = digitalio.DigitalInOut(board.D12)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# --- Helper Functions ---

def read_force():
    """Read and return analog value from the force sensor."""
    return fsr.value  # Range: 0–65535

def map_force_to_leds(force_value, max_value=65535):
    """Map force sensor value to number of LEDs to light up."""
    num_leds = int((force_value / max_value) * len(leds))
    return max(0, min(num_leds, len(leds)))

def update_leds(num_on):
    """Turn on a number of LEDs from the start (red end)."""
    for i, led in enumerate(leds):
        led.value = i < num_on

def all_leds_on(state=True):
    """Turn all LEDs on or off."""
    for led in leds:
        led.value = state

def celebration_confetti(duration=10, flash_delay=0.1):
    """Confetti celebration: randomly flash LEDs."""
    start_time = time.monotonic()
    while time.monotonic() - start_time < duration:
        for led in leds:
            led.value = random.choice([True, False])
        time.sleep(flash_delay)
    all_leds_on(False)

def fail_animation():
    """Fail animation: blink all LEDs then turn off one by one from right to left."""
    for _ in range(3):
        all_leds_on(False)
        time.sleep(0.2)
        all_leds_on(True)
        time.sleep(0.2)

    time.sleep(0.5)
    for led in reversed(leds):
        led.value = False
        time.sleep(0.2)

def morse_go_countdown():
    """Blink LEDs in Morse code for 'GO' before starting the test, lighting all parts together."""

    def light_leds(led_indices, duration=1.8):
        # Turn on all specified LEDs at once
        for i in range(len(leds)):
            leds[i].value = i in led_indices
        time.sleep(duration)
        # Turn all LEDs off
        for led in leds:
            led.value = False
        time.sleep(0.5)

    # G = --. (dash dash dot)
    # LEDs: 0&1 (dash 1), 3&4 (dash 2), 5 (dot)
    g_leds = [8,7,5,4,2]  # dot (5), gap(6) OFF, dashes (0,1,3,4)
    light_leds(g_leds)

    # O = --- (dash dash dash)
    # LEDs: 1&2 (dash 1), 4&5 (dash 2), 7&8 (dash 3)
    o_leds = [1, 2, 4, 5, 7, 8]
    light_leds(o_leds)


# --- Main Program Variables ---

testing = False
peak_force = 0
last_button_state = True
debounce_time = 0.2

trial_number = 1
trial1_peak = 0
trial2_peak = 0

# --- Main Loop ---
while True:
    current_button = button.value

    # Detect button press event (press = transition from True to False)
    if last_button_state and not current_button:
        if not testing:
            morse_go_countdown()   # Show Morse "GO" before starting test
            peak_force = 0
            testing = True
        else:
            final_leds = map_force_to_leds(peak_force)
            update_leds(final_leds)

            if trial_number == 1:
                trial1_peak = peak_force
                trial_number = 2
            else:
                trial2_peak = peak_force
                if trial2_peak > trial1_peak:
                    celebration_confetti()
                else:
                    fail_animation()

                trial_number = 1
                trial1_peak = 0
                trial2_peak = 0

            testing = False
            time.sleep(debounce_time)

    last_button_state = current_button

    if testing:
        current_force = read_force()
        if current_force > peak_force:
            peak_force = current_force

        num_on = map_force_to_leds(current_force)
        update_leds(num_on)

    time.sleep(0.05)
