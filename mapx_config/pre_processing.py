import os
import pathlib
import cv2
import numpy as np
from pdf2image import convert_from_path
from .property import BasicInformation

def find_boxes_preprocessing_v1(basic_info:BasicInformation):
    table_config = basic_info.default_config.Image_preprocessing.Table_preprocessing
    # de_img = cv2.GaussianBlur(self.img, (7, 7), 0)
    # can_img = cv2.Canny(de_img, 8, 200, 100)
    # lap = np.uint8(np.absolute(cv2.Laplacian(basic_info.image_property.img, cv2.CV_64F, ksize=1)))
    lap = np.uint8(np.absolute(cv2.Laplacian(basic_info.image_property.img,ddepth=cv2.CV_64F,ksize=1)))
    # intensify non black pixels to white
    lap[np.any(lap != [0, 0, 0], axis=-1)] = basic_info.default_config.Display_settings.mask_colour
    # horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, tuple(table_config.Line_detection_kernel.Horizontal.kernel))
    horizontal_lines = cv2.morphologyEx(lap, cv2.MORPH_OPEN, horizontal_kernel, iterations=table_config.Line_detection_kernel.Horizontal.iterations)
    # Vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, tuple(table_config.Line_detection_kernel.Vertical.kernel))
    vertical_lines = cv2.morphologyEx(lap, cv2.MORPH_OPEN, vertical_kernel, iterations=table_config.Line_detection_kernel.Vertical.iterations)
    table = cv2.add(horizontal_lines, vertical_lines)
    table = cv2.dilate(table,kernel=tuple(table_config.Dilate.kernel),iterations=table_config.Dilate.iterations)
    table = cv2.erode(table,kernel=tuple(table_config.Erode.kernel),iterations=table_config.Erode.iterations)
    table_gray = cv2.cvtColor(table, cv2.COLOR_BGR2GRAY)
    return table_gray

def find_horizontal_lines(basic_info:BasicInformation) -> np.array: #
    lap = np.uint8(np.absolute(cv2.Laplacian(basic_info.image_property.img, ddepth=cv2.CV_64F, ksize=1)))
    # intensify non black pixels to white
    lap[np.any(lap != [0, 0, 0], axis=-1)] = basic_info.default_config.Display_settings.mask_colour
    # converting to gray (2 dimensional)
    lap_gray = cv2.cvtColor(lap, cv2.COLOR_BGR2GRAY)
    table_config = basic_info.default_config.Image_preprocessing.Table_preprocessing
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, tuple(table_config.Line_detection_kernel.Horizontal.kernel))
    horizontal_lines = cv2.morphologyEx(lap_gray, cv2.MORPH_OPEN, horizontal_kernel, iterations=table_config.Line_detection_kernel.Horizontal.iterations)
    return horizontal_lines

def find_vertical_lines(basic_info:BasicInformation) -> np.array:
    table_config = basic_info.default_config.Image_preprocessing.Table_preprocessing
    lap = np.uint8(np.absolute(cv2.Laplacian(basic_info.image_property.img, ddepth=cv2.CV_64F, ksize=1)))
    # intensify non black pixels to white
    lap[np.any(lap != [0, 0, 0], axis=-1)] = basic_info.default_config.Display_settings.mask_colour
    # converting to gray (2 dimensional)
    lap_gray = cv2.cvtColor(lap, cv2.COLOR_BGR2GRAY)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, tuple(table_config.Line_detection_kernel.Horizontal.kernel))
    horizontal_lines = cv2.morphologyEx(lap_gray, cv2.MORPH_OPEN, horizontal_kernel, iterations=table_config.Line_detection_kernel.Horizontal.iterations)
    return horizontal_lines

def find_boxes_preprocessing(basic_info:BasicInformation):
    table_config = basic_info.default_config.Image_preprocessing.Table_preprocessing
    lap = np.uint8(np.absolute(cv2.Laplacian(basic_info.image_property.img,ddepth=cv2.CV_64F,ksize=1)))
    # intensify non black pixels to white
    lap[np.any(lap != [0, 0, 0], axis=-1)] = basic_info.default_config.Display_settings.mask_colour
    # converting to gray (2 dimensional)
    lap_gray = cv2.cvtColor(lap, cv2.COLOR_BGR2GRAY)
    # horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, tuple(table_config.Line_detection_kernel.Horizontal.kernel))
    horizontal_lines = cv2.morphologyEx(lap_gray, cv2.MORPH_OPEN, horizontal_kernel, iterations=table_config.Line_detection_kernel.Horizontal.iterations)
    # Vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, tuple(table_config.Line_detection_kernel.Vertical.kernel))
    vertical_lines = cv2.morphologyEx(lap_gray, cv2.MORPH_OPEN, vertical_kernel, iterations=table_config.Line_detection_kernel.Vertical.iterations)
    table = cv2.add(horizontal_lines, vertical_lines)
    table = cv2.dilate(table,kernel=tuple(table_config.Dilate.kernel),iterations=table_config.Dilate.iterations)
    table = cv2.erode(table,kernel=tuple(table_config.Erode.kernel),iterations=table_config.Erode.iterations)
    return table

def find_paragraph_preprocessing(basic_info:BasicInformation,img=None):
    paragraph_config = basic_info.default_config.Image_preprocessing.Paragraph_preprocessing
    extraction_settings = basic_info.default_config.Extraction_settings
    kernal_h = np.ones((1, extraction_settings.horizontal_buffer), np.uint8)
    kernal_v = np.ones((extraction_settings.vertical_buffer, 1), np.uint8)
    '''if isinstance(self.table_masked_image,np.ndarray):
        de_img = cv2.GaussianBlur(self.table_masked_image.copy(), (5, 5), 0)
    else:
        de_img = cv2.GaussianBlur(self.img.copy(), (5, 5), 0)'''
    if isinstance(img,np.ndarray):
        de_img = cv2.GaussianBlur(img, tuple(paragraph_config.Gaussian.kernel), 0)
    else:
        de_img = cv2.GaussianBlur(basic_info.image_property.img_temp, tuple(paragraph_config.Gaussian.kernel), 0)
    img_bin_h = cv2.morphologyEx(de_img, cv2.MORPH_OPEN, kernal_h)
    img_bin_v = cv2.morphologyEx(de_img, cv2.MORPH_OPEN, kernal_v)
    img = img_bin_v + img_bin_h
    lap = cv2.Laplacian(img,ddepth=cv2.CV_16S,ksize=1)
    lap[np.any(lap != [0, 0, 0], axis=-1)] = basic_info.default_config.Display_settings.mask_colour
    # gray_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshold = np.uint8(cv2.threshold(lap, 250, 255, cv2.THRESH_BINARY)[1])    # converted to int8 format
    # can_img = cv2.Canny(threshold, 8, 200, 100)
    gray_scale = cv2.cvtColor(threshold, cv2.COLOR_BGR2GRAY)
    return gray_scale


def convert_pdf_to_image(input_pdf,location_to_save):
    path = pathlib.Path(input_pdf)
    for index , image in enumerate(convert_from_path(location_to_save+input_pdf)):
        image.save(f'{location_to_save}/{path.stem}_{index + 1}.png')
    return "success"


class Pdf2Image:
    _image_format = ".png"
    def __init__(self,input_pdf,path=None,image_format=None):
        self._input_pdf = input_pdf
        if path:
            self._temp_location = path
        else:
            self._temp_location = os.getcwd()
        self.set_image_format(image_format)
        self._images = self.read_pdf()
        self._no_of_pages = len(self._images)

    def __len__(self):
        return self._no_of_pages

    @property
    def location(self):
        return self._temp_location

    @location.getter
    def location(self):
        return self._temp_location

    @location.setter
    def location(self,x):
        self._temp_location = x

    def set_image_format(self,format):
        if format:
            if format == "PNG":
                self._image_format = ".png"
            elif format == "JPG" or format == "JPEG":
                self._image_format = ".jpg"
        return

    def read_pdf(self):
        return convert_from_path(self._input_pdf)

    def convert(self,path=None):
        if path:
            self.location = path
        try:
            for index, image in enumerate(self._images):
                image.save(f'{self._temp_location}/{index + 1}{self._image_format}')
        except:
            raise Exception("Cannot able to save!!")
        return self

def find_horizontal_lines_v2(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)
    horizontal = np.copy(bw)
    cols = horizontal.shape[1]
    horizontal_size = cols // 30
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)
    return horizontal

def find_vertical_lines_v2(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)
    vertical = np.copy(bw)
    rows = vertical.shape[0]
    verticalsize = rows // 30
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)
    return vertical

def remove_lines(img):
    from collections import namedtuple
    import imutils
    def find_contours(can_img: np.ndarray, area: tuple = (0,), tree: bool = False) -> list:  # returns list of contour
        '''
        Finding contour by area
        area should be in tuple
        Tree = boolean
        Notes : For detecting thick(bold) lines use area = (1000,4000)
        '''
        area_filter = namedtuple('area_filter', ['min', 'max'], defaults=[0, np.inf])

        area = area_filter(*area)
        print(area.min, area.max)
        if tree:
            cnts = cv2.findContours(can_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            cnts = cv2.findContours(can_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts1 = imutils.grab_contours(cnts)
        cnts2 = [cnt for cnt in cnts1 if
                 area.min < cv2.contourArea(
                     cnt) < area.max]  # 4000 for last footer subject localization ...normal : 50000
        return cnts2
    def mask_contour_using_bounding_rects(img: np.ndarray, contours: list) -> np.ndarray:
        '''mask the contour region by finding the bounding_rects'''
        img_copy = img.copy()
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img_copy, (x - 7, y - 7), (x + w + 7, y + h + 7), [255, 255, 255], -1)  # white colour
        return img_copy

    lap = np.uint8(np.absolute(cv2.Laplacian(img, ddepth=cv2.CV_64F, ksize=1)))
    # intensify non black pixels to white
    lap[np.any(lap != [0, 0, 0], axis=-1)] = [255, 255, 255]
    lap_gray = cv2.cvtColor(lap, cv2.COLOR_BGR2GRAY)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, tuple([30, 1]))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, tuple([1, 30]))
    horizontal_lines = cv2.morphologyEx(lap_gray, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    vertical_lines = cv2.morphologyEx(lap_gray, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    contours_h = find_contours(horizontal_lines)
    contours_v = find_contours(vertical_lines)
    iiiv = mask_contour_using_bounding_rects(img, contours_v)
    iiih = mask_contour_using_bounding_rects(img, contours_h)
    hhh = iiiv + iiih
    return hhh


