import board
import digitalio
    
PIR_PIN = board.D2   # Pin number connected to PIR sensor output wire.
    
# Setup digital input for PIR sensor:
pir = digitalio.DigitalInOut(PIR_PIN)
pir.direction = digitalio.Direction.INPUT

def main():
    old_value = pir.value
    while(True):
        pir_value = pir.value
        if pir_value:
            if not old_value:
                print('Motion detected!')
        else:
            if old_value:
                print('Motion ended!')
        old_value = pir_value


if __name__ == "__main__":
    main()
