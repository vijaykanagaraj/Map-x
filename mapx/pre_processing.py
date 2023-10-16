import cv2
import numpy as np
from .property import BasicInformation

def find_boxes_preprocessing(basic_info:BasicInformation):
    # de_img = cv2.GaussianBlur(self.img, (7, 7), 0)
    # can_img = cv2.Canny(de_img, 8, 200, 100)
    gray = cv2.cvtColor(basic_info.image_property.img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    lap = np.uint8(np.absolute(cv2.Laplacian(thresh, cv2.CV_64F, ksize=1)))
    # lap = np.uint8(np.absolute(cv2.Laplacian(basic_info.image_property.img, cv2.CV_64F, ksize=1)))
    # intensify non black pixels to white
    # lap[np.any(lap != [0, 0, 0], axis=-1)] = [255, 255, 255]
    # horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
    horizontal_lines = cv2.morphologyEx(lap, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    # Vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))
    vertical_lines = cv2.morphologyEx(lap, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    table = cv2.add(horizontal_lines, vertical_lines)
    table = cv2.dilate(table,kernel=(1,5),iterations=5)
    table = cv2.erode(table,kernel=(1,5),iterations=5)
    table_gray = cv2.cvtColor(table, cv2.COLOR_BGR2GRAY)
    return table_gray

def find_paragraph_preprocessing(basic_info:BasicInformation):
    kernal_h = np.ones((1, basic_info.extraction_filter.horizontal_buffer), np.uint8)
    kernal_v = np.ones((basic_info.extraction_filter.vertical_buffer, 1), np.uint8)
    '''if isinstance(self.table_masked_image,np.ndarray):
        de_img = cv2.GaussianBlur(self.table_masked_image.copy(), (5, 5), 0)
    else:
        de_img = cv2.GaussianBlur(self.img.copy(), (5, 5), 0)'''
    de_img = cv2.GaussianBlur(basic_info.image_property.img_temp, (5, 5), 0)
    img_bin_h = cv2.morphologyEx(de_img, cv2.MORPH_OPEN, kernal_h)
    img_bin_v = cv2.morphologyEx(de_img, cv2.MORPH_OPEN, kernal_v)
    img = img_bin_v + img_bin_h
    lap = cv2.Laplacian(img, cv2.CV_16S, ksize=1)
    lap[np.any(lap != [0, 0, 0], axis=-1)] = [255, 255, 255]
    # gray_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshold = np.uint8(cv2.threshold(lap, 250, 255, cv2.THRESH_BINARY)[1])    # converted to int8 format
    # can_img = cv2.Canny(threshold, 8, 200, 100)
    gray_scale = cv2.cvtColor(threshold, cv2.COLOR_BGR2GRAY)
    return gray_scale