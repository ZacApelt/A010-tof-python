import serial
import time
import numpy as np
import matplotlib.pyplot as plt


# Replace 'COMx' with the appropriate serial port (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux)
serial_port = 'COM12'  # Change this to the correct port for your system


#declare the height and width to be 100pixels
height = 100
width = 100

#header size is 20 bytes    
header_size = 20    #00FF + packet length + 16 bytes of meta data

#tail size is 2 bytes
tail_size = 2       #checksum and DD

#end of frame -  start and end
eof = b'\x00\xFF'

frame_size = header_size + (height * width) + tail_size     #10022

#Write prcessFrame function 
def displayImage(image):

    # Convert the image data to a list
    image_data = list(image)

    # Reshape the list to a 2D array (e.g., 100x100)
    depth_array = np.array(image_data).reshape(height, width)

    # Create a heatmap
    plt.clf()
    plt.imshow(depth_array, cmap='viridis', interpolation='nearest')
    plt.colorbar(label='Depth')
    plt.title('Depth Heatmap')
    plt.draw()
    plt.pause(0.01)


# Configure the serial connection
ser = serial.Serial(serial_port, baudrate=3000000, timeout=1)

# check if serial port is open
if ser.is_open:
    print(f"Serial port {serial_port} is open.")
else:
    print(f"Serial port {serial_port} is not open.")

try:
    # full list of commands:
    # https://wiki.sipeed.com/hardware/en/maixsense/maixsense-a010/at_command_en.html#Image-Packet-Description

    # turn sensor on
    ser.write("AT+ISP=1\r".encode('utf-8'))
    time.sleep(0.1)
    # set baud rate to 3000000
    ser.write("AT+BAUD=8\r".encode('utf-8'))
    time.sleep(0.1)
    # send data to screen and over usb
    ser.write("AT+DISP=3\r".encode('utf-8'))
    time.sleep(0.1)
    # set the image size to 100x100 - full resolution
    ser.write("AT+BINN=1\r".encode('utf-8'))
    time.sleep(0.1)
    # set the frame rate to 19
    ser.write("AT+FPS=19\r".encode('utf-8'))
    time.sleep(0.1)

    #declare a buffer to hold the data coming in from the serial port.
    #constantly scan it for the start of a frame and the end of the frame and then process it
    #if the start or end cannot be found then just get more data until they are found.
    data = bytearray()

    while True:

        incoming = ser.read(frame_size)   #read in the frame size + 100 bytes to make sure we get the first bytes of the next frame
        data.extend(incoming)

        while True:

            # Find the start of the frame and if not present then get more data
            frameStart = data.find(eof)

            if (frameStart == -1):
                break

            else:
                # Find the length of the entire frame by looking for the next 00ff and if not present then get more data
                frameLength = data[frameStart+header_size:].find(eof) # so skip forward over the header to avoid any 00ff that may be in the header

                if (frameLength == -1):
                    break
                
                else:
                    frameLength += header_size       # Add the length of the header back on because we skipped over it in the code above.

                    # Check if the frame length is the expected size
                    if frameLength != frame_size:
                        print('Invalid frame length:' + str(len(data)) + ' expected: ' + str(frame_size))

                    else:
                        print('Got frame of length: ' + str(frameLength))

                        # Get the image 
                        image = data[header_size:header_size + (height * width)]  

                        # Display the image - comment this out if not needed.
                        displayImage(image)

                    # Remove the frame from the data buffer to move on to the next frame
                    data = data[frameStart + frameLength:]



    
except KeyboardInterrupt:
    print("Exiting program.")
    ser.close()

