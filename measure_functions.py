import numpy as np
from scipy import signal
import cv2, csv

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
coin_dia_mm = 22.5
# coin_dia_mm = 24.26

def auto_canny(image, sigma=0.33):
    val = np.median(image)
    lower = int(max(0, (1.0 - sigma) * val)) - 5
    upper = int(min(255, (1.0 + sigma) * val)) + 20
    edged = cv2.Canny(image, lower, upper)

    return edged

def get_threshold(image):
    kernel = np.ones((5,5), np.uint8) 
    img_erosion = cv2.erode(image, kernel, iterations=1)
    img_ed = cv2.dilate(img_erosion, kernel, iterations=1)
    ret, thresh = cv2.threshold(img_ed, 128, 255, cv2.THRESH_BINARY_INV)
    # thresh = cv2.adaptiveThreshold(img_ed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 7)
    # thresh = cv2.bitwise_not(thresh)
    return thresh

def img_resize(img):
    width = 600
    height = int(img.shape[0] * width/img.shape[1])
    dim = (width, height)
    return cv2.resize(img, dim, interpolation = cv2.INTER_AREA) 

def get_coin_dim(contour):
    x,y,w,h = cv2.boundingRect(contour)
    return (w+h)/2

def get_bolt_coin(contours, img):
    top_contours = sorted(contours, reverse=True, key=cv2.contourArea)[:10]
    width = img.shape[1]

    circular_contours = []
    for contour in top_contours:
        approx = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour,True), True)
        area = cv2.contourArea(contour)
        x,y,w,h = cv2.boundingRect(contour)
        if ((len(approx) > 8) & (len(approx) < 23) & (area > 30)) and (abs(w-h)/w < 0.1) and (x < width/2):
            circular_contours.append(contour)
            # cv2.rectangle(img, (x,y), (x+w,y+h), GREEN, 1 )

    circular_contours = sorted(circular_contours, reverse=True, key=cv2.contourArea)

    rect_contours = []
    for contour in top_contours:
        approx = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour,True), True)
        area = cv2.contourArea(contour)
        x,y,w,h = cv2.boundingRect(contour)
        if ((len(approx) > 8) & (area > 30)) and (abs(w-h)/w > 0.2) and (x+w/2 > width/2):
            rect_contours.append(contour)
            # cv2.rectangle(img, (x,y), (x+w,y+h), RED, 1 )
    rect_contours = sorted(rect_contours, reverse=True, key=cv2.contourArea)

    return (rect_contours[0], circular_contours[0])

def draw_contour_box(contour, img, color):
    x,y,w,h = cv2.boundingRect(contour)
    cv2.rectangle(img, (x,y), (x+w,y+h), color, 1 )

def get_thread_dia(cropped_img):
    h = cropped_img.shape[0]
    w = cropped_img.shape[1]
    dia = []
    for y in range(h-5, h-65, -2):
        left, right = 0, 0
        for x in range(0, w):
            if cropped_img[y, x] == 255:
                left = x
                break
        for x in range(w-1, 0, -1):
            if cropped_img[y, x] == 255:
                right = x
                break
        if right == 0 or left == 0:
            continue
        dia.append(right - left)

    return sum(dia)/len(dia)

def get_thread_length(cropped_img):
    pass

def thread_count(image):
    h = image.shape[0]
    w = image.shape[1]
    thread_array = []
    for y in range(0, h):
        for x in range(0, int(w/2)):
            if image[y, x] == 255:
                thread_array.append(x)
                break
    fs = 1000
    fc = 120  # Cut-off frequency of the filter
    w = fc / (fs / 2) # Normalize the frequency
    b, a = signal.butter(5, w, 'low')
    output = signal.filtfilt(b, a, thread_array)
    peaks = len(np.diff(np.sign(np.diff(output))).nonzero()[0] + 1)
    if peaks%2 == 0:
        return peaks/2
    else:
        return peaks/2 +1
        
def write_csv(values):
    with open('measurements.csv', 'a+', newline="") as csvfile:
        feature_names = ['head_diameter', 'overall_length', "thread_diameter", "thread_per_2cm", "part_name"]
        writer = csv.writer(csvfile)
        # writer.writerow(feature_names)
        writer.writerow(values)
