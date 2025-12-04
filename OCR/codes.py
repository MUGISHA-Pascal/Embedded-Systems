import cv2
import pytesseract
import numpy as np

# Load the image using OpenCV
image = cv2.imread('img-01.jpg')

# invert the colors
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
white_pixel_count = np.sum(mask == 255)
is_white_background = white_pixel_count > (mask.size / 2)
if is_white_background:
    inverted_image = cv2.bitwise_not(gray)
else:
    inverted_image = gray

# binarize the image
contrast = 255
exposure = 255
saturation = 0
binarized_image = cv2.convertScaleAbs(inverted_image, alpha=contrast/255, beta=0)
binarized_image = cv2.convertScaleAbs(binarized_image, alpha=exposure/255, beta=0)
binarized_image = cv2.cvtColor(binarized_image, cv2.COLOR_GRAY2BGR)
binarized_image = cv2.cvtColor(binarized_image, cv2.COLOR_BGR2HSV)
binarized_image[:, :, 1] = saturation
binarized_image = cv2.cvtColor(binarized_image, cv2.COLOR_HSV2BGR)
threshold_value = 75
_, binary_image = cv2.threshold(binarized_image, threshold_value, 255, cv2.THRESH_BINARY)

cv2.imwrite("output.jpg", binary_image)
# Perform OCR using Tesseract
text = pytesseract.image_to_string(binary_image)

# Print the extracted text
print(text)