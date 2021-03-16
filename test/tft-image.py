import board
import digitalio
import adafruit_rgb_display.ili9341 as ili9341
from PIL import Image

# Setup display
cs_pin = digitalio.DigitalInOut(board.C0)
dc_pin = digitalio.DigitalInOut(board.C1)
disp = ili9341.ILI9341(board.SPI(), cs=cs_pin, dc=dc_pin, baudrate=64000000)

# Load image and convert to RGB
image = Image.open('blinka.bmp').convert('RGB')

# Display it (rotated by 90 deg)
disp.image(image, 90)