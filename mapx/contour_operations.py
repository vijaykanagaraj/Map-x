import numpy as np
import imutils
from collections import namedtuple
from .unique_key_decode import UniqueKeyDecoder

import cv2

class DrawOperations:
    def draw_contour(self,img:np.ndarray,contours:list) -> np.ndarray:
        '''
        draw multiple contour regions and annotate index values
        input --> contour
        output --> image
        '''
        i = 0
        img_copy = img.copy()
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), (255,140,0), 5)      # orange colour
            cv2.putText(img_copy, str(i), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 10)  # Green colour
            i = i + 1
        return img_copy

    def draw_contour_from_points(self,img:np.ndarray,contour_points:list) -> np.ndarray:
        '''
        draw multiple contour points and annotate index values
        input --> [(x,y,x1,y1)]
        output --> image
        '''
        i = 0
        img_copy = img.copy()
        for x,y,x1,y1 in contour_points:
            cv2.rectangle(img_copy, (x-5, y-5), (x1, y1), (0, 255, 0), 5)     # green colour
            cv2.putText(img_copy, str(i), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)  #red colour
            i = i + 1
        return img_copy

    def draw_point(self,img,point) -> np.ndarray:
        '''draw a point over the image
        input -> img , (x,y)
        output --> image'''
        img_copy = img.copy()
        cv2.circle(img_copy, point, radius=5, color=(255,140,0), thickness=10)     # orange colour
        return img_copy

class MaskOperations:
    def mask_contour(self,img:np.ndarray,contour:list) -> np.ndarray:
        '''mask the contour region using contour'''
        img_copy = img.copy()
        cv2.drawContours(img_copy, [contour], 0, (255,255,255), -1)    # white colour ...-1 implies to fill the region with white colour)
        return img_copy

    def mask_contours(self,img:np.ndarray,contours:list) -> np.ndarray:
        '''mask the contour region using contour'''
        img_copy = img.copy()
        for contour in contours:
            cv2.drawContours(img_copy, [contour], 0, (255,255,255), -1)    # white colour ...-1 implies to fill the region with white colour)
        return img_copy

    def mask_contour_using_bounding_rect(self,img:np.ndarray,bounding_rect:tuple) -> np.ndarray:
        '''mask the contour region by finding the bounding_rect'''
        img_copy = img.copy()
        x,y,w,h = bounding_rect
        cv2.rectangle(img_copy, (x-5, y-5), (x+w+5, y+h+5), (255,255,255), -1)  # white colour
        return img_copy

    def mask_contour_using_bounding_rects(self,img:np.ndarray,contours:list) -> np.ndarray:
        '''mask the contour region by finding the bounding_rects'''
        img_copy = img.copy()
        for contour in contours:
            x,y,w,h = cv2.boundingRect(contour)
            cv2.rectangle(img_copy, (x-5, y-5), (x+w+5, y+h+5), (255,255,255), -1)  # white colour
        return img_copy

class FindContourOperations:
    @staticmethod
    def find_contours(can_img:np.ndarray,area:tuple=(0,),tree:bool=False) -> list:    # returns list of contour
        '''
        Finding contour by area
        area should be in tuple
        Tree = boolean
        Notes : For detecting thick(bold) lines use area = (1000,4000)
        '''
        area_filter = namedtuple('area_filter', ['min', 'max'], defaults=[0, np.inf])
        area = area_filter(*area)
        print(area.min,area.max)
        if tree:
            cnts = cv2.findContours(can_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            cnts = cv2.findContours(can_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts1 = imutils.grab_contours(cnts)
        cnts2 = [cnt for cnt in cnts1 if area.min < cv2.contourArea(cnt) < area.max]  # 4000 for last footer subject localization ...normal : 50000
        return cnts2

    def find_bounding_rects(self,can_img:np.ndarray,area:tuple=(0,),tree:bool=False):
        contour_to_bounding_rect = lambda contour: cv2.boundingRect(contour)   # lambda function
        contours = self.find_contours(can_img,area,tree=tree)
        return map(contour_to_bounding_rect,contours)

class FilterContourOperations:
    '''Filter contour using selected points'''
    @staticmethod
    def filter_contour_using_selected_points(contours:list,selected_points:[list,None]) -> list:
        '''input -> contours and selected points
        output -> list of contour'''
        if not selected_points:
            return contours
        selected_contours = []
        for contour in contours:
            for key in selected_points:
                unique_key = UniqueKeyDecoder(key)
                result = cv2.pointPolygonTest(contour, unique_key.location_tagger,False)  # if false , it will tell 1,-1,0 .if true it measuure distance bw point and contour
                if int(result) >= 0:
                    selected_contours.append(contour)
        return selected_contours




