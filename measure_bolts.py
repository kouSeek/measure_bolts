'''measure dimensions of Dorman bolts'''
import glob
from datetime import datetime
from measure_functions import *

def main(image, part_name):
    try:
        img = img_resize(image)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edge = cv2.Canny(blurred, 50, 100)
        # edge = auto_canny(blurred)

        ## Find contours
        contours, hierarchy = cv2.findContours(edge, 1, 2)
        ed_thres_edge = get_threshold(gray)
        cv2.imshow("ed", ed_thres_edge)
        contours_thres, hierarchy = cv2.findContours(ed_thres_edge, 1, 2)
        bolt_contour, coin_contour = get_bolt_coin(contours+contours_thres, img)
        
        ## calculate Coin diameter and bolt box
        px_per_mm = get_coin_dim(coin_contour)/coin_dia_mm
        x,y,w,h = cv2.boundingRect(bolt_contour)
        bolt_img = edge[y:y+h, x:x+w]

        # 20 mm box
        px_per_2cm = int(20*px_per_mm)
        crop_im = edge[int(y + h/3)+1:int(y + h/3)+px_per_2cm, x+1:x+w]

        ## All measurements
        head_diameter = round(w/px_per_mm, 4)
        overall_length = round(h/px_per_mm, 4)
        thread_diameter = round(get_thread_dia(bolt_img)/px_per_mm, 4)
        thread_per_2cm = thread_count(crop_im)


        ## write csv file
        write_csv([head_diameter, overall_length, thread_diameter, thread_per_2cm, part_name, datetime.now()])
        
        print("Head diameter:", head_diameter)
        print("Overall length:", overall_length)
        print("Thread diameter:", thread_diameter)
        print("Thread count per 2cm: ", thread_per_2cm)

        ## Show images
        cv2.rectangle(img, (x, int(y + h/3)), (x+w, int(y + h/3)+px_per_2cm), GREEN, 1)
        cv2.rectangle(edge, (x, int(y + h/3)), (x+w, int(y + h/3)+px_per_2cm), (255,255,255), 1)
        draw_contour_box(bolt_contour, img, RED)
        draw_contour_box(coin_contour, img, BLUE)  
        cv2.imshow("contours image", img)
        cv2.imshow("edges canny", edge)
        cv2.waitKey(0)

        return [{"head_diameter":head_diameter, "overall_length":overall_length, "thread_diameter":thread_diameter, "thread_per_2cm":thread_per_2cm, "part_name": part_name}]

    except:
        return [{"Error": "Unable to process the image."}]

if __name__ == "__main__":
    part_name = "ANU_A"
    for imagePath in glob.glob("images/bolts/"+part_name + "/*.*g"):
        # main(cv2.imread(imagePath))
        try:
            main(cv2.imread(imagePath), part_name)
        except:
            print("X: ",imagePath)
