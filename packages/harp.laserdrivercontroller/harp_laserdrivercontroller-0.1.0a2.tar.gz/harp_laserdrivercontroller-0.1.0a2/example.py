import time

from harp.protocol import OperationMode

from harp.devices.laserdrivercontroller import LaserDriverController
from harp.devices.laserdrivercontroller.harpdevice import FrequencySelect

# Example usage of the LaserDriverController device
with LaserDriverController("/dev/ttyUSB0") as device:  # For Windows, use "COM8" or similar
    device.info()

    # Set the device to active mode
    device.set_mode(OperationMode.ACTIVE)
    device.write_operation_ctrl(OperationMode.ACTIVE)

    reply = device.write_spad_switch(0)  # Set the SPAD switch to 0
    print(f"SPAD switch set reply: {reply}")

    time.sleep(2)  # Wait for 2 seconds

    reply = device.write_spad_switch(1)  # Set the SPAD switch to 1
    print(f"SPAD switch set reply: {reply}")

    time.sleep(2)  # Wait for 2 seconds

    reply = device.write_spad_switch(0)  # Set the SPAD switch to 0
    print(f"SPAD switch set reply: {reply}")

    reply = device.read_laser_intensity()  # Read the laser intensity
    print(f"Laser intensity: {reply}")

    reply = device.write_laser_intensity(100)  # Set the laser intensity to 100
    print(f"Laser intensity set reply: {reply}")

    time.sleep(2)  # Wait for 2 seconds

    reply = device.write_laser_frequency_select(FrequencySelect.F2)  # Set the laser frequency to F2
    print(f"Laser frequency set reply: {reply}")

    # Get the events
    try:
        while True:
            for event in device.get_events():
                # Do what you need with the event
                print(event.payload)
    except KeyboardInterrupt:
        # Capture Ctrl+C to exit gracefully
        print("Exiting...")
    finally:
        # Do what you need to do to clean up. Disconnect is automatically called with the "with" statement.
        device.set_mode(OperationMode.STANDBY)
        pass
