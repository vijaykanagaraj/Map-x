import numpy as np
import imutils
import os
from collections import namedtuple

import pandas as pd
from termcolor import colored

from .unique_key_decode import UniqueKeyDecoder

from config.load_config import get_config

import cv2
from .property import BasicInformation


# account = os.environ.get("account",None)
# config = get_config(account=account)

class DrawOperations:
    def __init__(self,basic_info:BasicInformation):
        self.config = basic_info.default_config

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
            cv2.rectangle(img_copy, (x, y), (x + w, y + h),self.config.Display_settings.annotation_colour, int(self.config.Display_settings.annotation_thickness))      # orange colour
            cv2.putText(img_copy, str(i), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, self.config.Display_settings.text_colour, 10)  # Green colour
            i = i + 1
        return img_copy

    def draw_contour_from_points(self,img:np.ndarray,contour_points:list) -> np.ndarray:
        '''
        draw multiple contour points and annotate index values
        input --> [(x,y,x1,y1)]
        output --> image
        '''
        print("inside annot------",self.config.Display_settings.annotation_colour)
        i = 0
        img_copy = img.copy()
        for x,y,x1,y1 in contour_points:
            cv2.rectangle(img_copy, (x-5, y-5), (x1, y1), self.config.Display_settings.annotation_colour, self.config.Display_settings.annotation_thickness)     # green colour
            cv2.putText(img_copy, str(i), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, self.config.Display_settings.text_thickness, self.config.Display_settings.text_colour, 2)  #red colour
            i = i + 1
        return img_copy

    def draw_point(self,img,point) -> np.ndarray:
        '''draw a point over the image
        input -> img , (x,y)
        output --> image'''
        img_copy = img.copy()
        cv2.circle(img_copy, point, radius=5, color=self.config.Display_settings.annotation_colour, thickness=self.config.Display_settings.annotation_colour)     # orange colour
        return img_copy

class MaskOperations:
    def __init__(self,basic_info:BasicInformation):
        self.config = basic_info.default_config

    def mask_contour(self,img:np.ndarray,contour:list) -> np.ndarray:
        '''mask the contour region using contour'''
        img_copy = img.copy()
        cv2.drawContours(img_copy, [contour], 0, self.config.Display_settings.mask_colour, -1)    # white colour ...-1 implies to fill the region with white colour)
        return img_copy

    def mask_contours(self,img:np.ndarray,contours:list) -> np.ndarray:
        '''mask the contour region using contour'''
        img_copy = img.copy()
        for contour in contours:
            cv2.drawContours(img_copy, [contour], 0, self.config.Display_settings.mask_colour, -1)    # white colour ...-1 implies to fill the region with white colour)
        return img_copy

    def mask_contour_using_bounding_rect(self,img:np.ndarray,bounding_rect:tuple) -> np.ndarray:
        '''mask the contour region by finding the bounding_rect'''
        img_copy = img.copy()
        x,y,w,h = bounding_rect
        cv2.rectangle(img_copy, (x-5, y-5), (x+w+5, y+h+5), self.config.Display_settings.mask_colour, -1)  # white colour
        return img_copy

    def mask_contour_using_bounding_rects(self,img:np.ndarray,contours:list) -> np.ndarray:
        '''mask the contour region by finding the bounding_rects'''
        img_copy = img.copy()
        for contour in contours:
            x,y,w,h = cv2.boundingRect(contour)
            cv2.rectangle(img_copy, (x-5, y-5), (x+w+5, y+h+5), self.config.Display_settings.mask_colour, -1)  # white colour
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
    # @staticmethod
    # def filter_contour_using_location_tagger(contours:list,selected_points:list) -> list:
    #     '''input -> contours and selected points
    #     output -> list of contour'''
    #     if not selected_points:
    #         return contours
    #     selected_contours = []
    #     for contour in contours:
    #         for key in selected_points:
    #             print("-------"*10)
    #             print("key------->",key)
    #             print("-------" * 10)
    #             unique_key = UniqueKeyDecoder(key)
    #             result = cv2.pointPolygonTest(contour, unique_key.location_tagger,False)  # if false , it will tell 1,-1,0 .if true it measuure distance bw point and contour
    #             result_distance = cv2.pointPolygonTest(contour, unique_key.location_tagger,True)  # if false , it will tell 1,-1,0 .if true it measuure distance bw point and contour
    #             print("-------"*10)
    #             print("point polygon test------->",colored(result,"red"))
    #             print("point polygon test------->",colored(result_distance,"red"))
    #             print("-------" * 10)
    #             if int(result) >= 0:
    #                 selected_contours.append(contour)
    #     return selected_contours

    @staticmethod
    def filter_contour_using_location_tagger(contours: list, selected_points: list) -> list:
        '''input -> contours and selected points
        output -> list of contour'''
        if not selected_points:
            return contours
        selected_contours = []
        for key in selected_points:
            distance = {}
            for index,contour in enumerate(contours):
                unique_key = UniqueKeyDecoder(key)
                result_distance = cv2.pointPolygonTest(contour, unique_key.location_tagger,True)  # if false , it will tell 1,-1,0 .if true it measuure distance bw point and contour
                print("-------" * 10)
                print("point polygon test------->", colored(result_distance, "red"))
                print("-------" * 10)
                distance[index] = result_distance
            if distance:
                print(distance[max(distance,key=distance.get)])
                selected_contours.append(contours[max(distance,key=distance.get)])
        return selected_contours

    @staticmethod
    def filter_content_using_child_and_bucket(basic_info:BasicInformation):
        final_table_content = {}
        selected_points = basic_info.extraction_filter.selected_points
        print(colored(selected_points, "blue"))
        if not selected_points:
            return basic_info.content_holder.table_content
        table_content = basic_info.content_holder.table_content
        selected_table_points = [selected_point for selected_point in selected_points if UniqueKeyDecoder(selected_point).identifier == "T"]  # filter using bucket
        for key , table in table_content.items():
            table_key = UniqueKeyDecoder(key)
            print(colored(table_key.page_no,"yellow"),"----->",colored(basic_info.pdf_property.page_no,"yellow"))
            if str(table_key.page_no) == str(basic_info.pdf_property.page_no):
                print(colored("page check pass","yellow"))
                for selected_table_point in selected_table_points:
                    print(colored(key,"yellow"),"----->",colored(selected_table_point,"yellow"))
                    selected_table_point_key = UniqueKeyDecoder(selected_table_point)
                    print(colored(table_key.id, "yellow"), "----->",colored(selected_table_point_key.id, "yellow"))
                    # if selected_table_point_key.id == table_key.id:    # filter using id
                    #     print(colored("id check pass", "yellow"))
                    if selected_table_point_key.is_child == table_key.is_child:   # filter using child
                        print(colored("child check pass", "yellow"))
                        if selected_table_point_key.table_cell:
                            print(colored("table cell check pass", "yellow"))
                            dataframe = pd.DataFrame(table)
                            final_table_content[selected_table_point] = [[dataframe.loc[selected_table_point_key.table_cell[0],selected_table_point_key.table_cell[1]]]]
                        else:
                            final_table_content[selected_table_point] = table
        return final_table_content
