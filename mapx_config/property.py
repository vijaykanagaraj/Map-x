import cv2
import pdfplumber
from dataclasses import dataclass , field
from config.config_property import default_config

class ImageProperty:
    '''
        returns basic image properties
        width and height has to be the width and height of the pdf page
    '''
    def __init__(self,image,width=None,height=None):
        self.__img = cv2.imread(image)
        self.__img = self.reshape(width=width,height=height)
        self.__img_temp = self.__img.copy()

    @property
    def height(self):
        '''returns height of the image'''
        return self.__img.shape[0]

    @property
    def width(self):
        '''returns width of the image'''
        return self.__img.shape[1]

    @property
    def img(self):
        '''returns copy of original image'''
        return self.__img.copy()

    @property
    def img_temp(self):
        '''returns copy of original image which will be overwritten by setter'''
        return self.__img_temp

    @img_temp.setter
    def img_temp(self,img):
        '''replaces temp image with processed image'''
        self.__img_temp = img

    def reshape(self,width,height):
        if width and height:
            return cv2.resize(self.img,(int(width),int(height)),interpolation= cv2.INTER_AREA)
        else:
            return self.__img


class PdfProperty:
    '''returns basic pdf properties like pdf , page_no , width and height of the page'''
    def __init__(self,input_pdf:str,page_no:int):
        self.__input_pdf = input_pdf
        self.__page_no = page_no

    @property
    def input_pdf(self):
        '''returns input_pdf'''
        return self.__input_pdf

    @property
    def page_no(self):
        '''returns page number'''
        return self.__page_no

    @property
    def plumber_pdf(self):
        '''returns pdfplumber object'''
        return pdfplumber.open(self.__input_pdf)

    @property
    def pages(self) -> list:
        '''returns page number in list'''
        return list(range(1,len(self.plumber_pdf.pages)+1))


    @property
    def height(self):
        '''returns height of the page'''
        return self.plumber_pdf.pages[int(self.__page_no)-1].height

    @property
    def width(self):
        '''returns width of the page'''
        return self.plumber_pdf.pages[int(self.__page_no)-1].width

@dataclass
class SelectedPoints:
    '''contains user provided settings for extraction'''
    # horizontal_buffer:int
    # vertical_buffer:int
    # area_filter:[tuple,int]
    # kind:str
    # mode:str
    # method:str
    # check_for_inner_tables:bool
    selected_points:list = field(default_factory=list)

@dataclass
class GlobalContentHolder:
    '''Holds global variables'''
    contour_points:list = field(default_factory=list)   # hold all the contour points extracted for annotation
    table_contours:list = field(default_factory=list)      # hold all table contours to find inner tables
    paragraph_contours:list = field(default_factory=list)  # hold all the extracted paragrah contours
    table_content:dict = field(default_factory=dict)      # hold extracted table content with its uniue key
    paragraph_content:dict = field(default_factory=dict)    # hold extracted paragraph content with its uniue key

@dataclass
class BasicInformation:
    '''contains all the information needed for data extration for a single page'''
    pdf_property:PdfProperty
    image_property:ImageProperty
    extraction_filter: SelectedPoints
    content_holder:GlobalContentHolder
    default_config:default_config


