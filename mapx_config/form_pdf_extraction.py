import cv2
import pdfplumber
import pdfminer
from functools import singledispatch
import matplotlib.pyplot as plt
from config.load_config import get_config
import pathlib
import fitz
from termcolor import colored

# document_location = r"/Users/vijaykanagaraj/PycharmProjects/testing/"

# temp_location = r"/Users/vijaykanagaraj/PycharmProjects/mapx_image/"

# output_image = f'{temp_location}/annotated.png'

@singledispatch
def pdfminer_object_decode(obj):  # pdfminer object's input
    if isinstance(obj,pdfminer.pdftypes.PDFObjRef):
        print("obj---->",obj.resolve())
        if isinstance(obj.resolve(),bytes):
            return str(obj.resolve(),"latin")
        return obj.resolve()
    elif isinstance(obj,pdfminer.psparser.PSLiteral):
        return obj.name

@pdfminer_object_decode.register(str)
def _string(obj) -> str:
    # print("this is string object")
    return obj

@pdfminer_object_decode.register(bytes)
def _bytes(obj) -> str:
    # print("this is bytes object")
    return obj.decode("latin")

@pdfminer_object_decode.register(list)
def _list(obj) -> list:
    # print("this is list object")
    temp_list = []
    for kid in obj:
        kid_dict = pdfminer_object_decode(kid)
        annotation_points = kid_dict.get("Rect", None)
        unique_key = pdfminer_object_decode(kid_dict.get("T", None))
        # print("unique_key------>",unique_key)
        # print("unique_key_type------>",type(unique_key))
        unique_value = pdfminer_object_decode(kid_dict.get("V", None))
        # print("unique_value------>",unique_value)
        # print("unique_value_type------>",type(unique_value))
        temp_list.append({"rect":annotation_points,"key":unique_key,"value":unique_value})
    return temp_list

@pdfminer_object_decode.register(dict)
def _dict(obj) -> list:
    # print("this is dict object")
    kids = obj.get("Kids", None)
    if kids:
        return pdfminer_object_decode(kids)
    else:
        annotation_points = obj.get("Rect", None)
        unique_key = pdfminer_object_decode(obj.get("T", None))
        unique_value = pdfminer_object_decode(obj.get("V", None))
        return [{"rect":annotation_points,"key":unique_key,"value":unique_value}]

class FormROIExtractor:
    def __init__(self,**params):
        self.input_pdf = params.get("input_pdf",None)
        self.page = params.get("page",None)
        #------------------------#
        # loading custom config files
        # self.config = get_config(account=params.get("account",None))
        self.config = params.get("config",None)
        if not self.config:
            self.config = get_config(account=params.get("account", None))
        self.selected_points = params.get("selected_points",None)
        if self.selected_points:
            self.selected_points = [str(selected_point).strip() for selected_point in self.selected_points]

        #------------------------#
        self.plumb_pdf = pdfplumber.open(f"{self.config.Path.location_to_save}{self.input_pdf}")
        self.page_plumb_pdf = self.plumb_pdf.pages[int(self.page)-1]
        self.height_page_plumb_pdf = self.page_plumb_pdf.height
        self.width_page_plumb_pdf = self.page_plumb_pdf.width
        #------------------------#
        self.input_image = f"{self.config.Path.location_to_save}{pathlib.Path(self.input_pdf).stem}_{str(self.page)}.png"
        img_read = cv2.imread(self.input_image)
        self.img = cv2.resize(img_read,(int(self.width_page_plumb_pdf),int(self.height_page_plumb_pdf)),interpolation= cv2.INTER_LINEAR)
        self.img_copy = self.img.copy()
        self.contour_points = {}
        self.final_json = {}

    def extract(self):
        '''Extract content and contour points from plumber pdf'''
        field_mapping_dictionary = {"paragraph": "Tx", "checkbox": "Btn", "dropdown": "Ch"}
        location_tagger_mapping = {"paragraph": "P", "checkbox": "C", "dropdown": "D"}
        fields = self.plumb_pdf.doc.catalog["AcroForm"].resolve()["Fields"]
        form_dict = {}
        for index,field in enumerate(fields):
            mapping_key, mapping_field = None, None
            field_dict = pdfminer_object_decode(field)
            print("---------" * 5)
            print("field dict---------->", field_dict)
            print("---------" * 5)
            # field_mapping_variable = field.resolve().get("FT", None)  # PSLiteral datatype
            field_mapping_variable = pdfminer_object_decode(field_dict.get("FT", None))
            # initializing form dict with available content variable
            if field_mapping_variable:
                print("field_mapping_variable------>", field_mapping_variable)
                for mapping_key, mapping_field in field_mapping_dictionary.items():
                    if field_mapping_variable == mapping_field:
                        if not form_dict.get(mapping_key, None):
                            form_dict[mapping_key] = {}
                            if not form_dict[mapping_key].get("is_available", None):
                                form_dict[mapping_key]["is_available"] = 1
                            if not form_dict[mapping_key].get("content", None):
                                # form_dict[mapping_key]["content"] = []
                                form_dict[mapping_key]["content"] = {}
                        break
                # initializing form dict end
                print("mapping_key---->", mapping_key)
                list_of_dict = pdfminer_object_decode(field.resolve())          # custom function (single dispatch)- Input {dict} - output{"rect":list,"key":str,"value":str}
                for extracted_dict in list_of_dict:
                    unique_key = extracted_dict.get("key")
                    field_value = extracted_dict.get("value")
                    contour_points = extracted_dict.get("rect")
                    if field_value not in (None,"Off") and unique_key:
                        # single_data_dict[unique_key] = field_value
                        self.contour_points.setdefault(mapping_key, []).append(contour_points)
                        # form_dict[mapping_key]["content"].append(single_data_dict)
                        x, y, x1, y1 = contour_points
                        cnt_original_pts = (int(x), int(self.height_page_plumb_pdf)-int(y1), int(x1), int(self.height_page_plumb_pdf)-int(y))
                        center = ((cnt_original_pts[0] + (cnt_original_pts[0] + cnt_original_pts[2]) // 2) // 2,
                                  (cnt_original_pts[1] + (cnt_original_pts[1] + cnt_original_pts[3]) // 2) // 2)
                        location_tagger = "-".join((location_tagger_mapping[mapping_key], f"{int(self.page) + 1}#{index}", f"{center[0]}#{center[1]}"))
                        form_dict[mapping_key]["content"][unique_key] = field_value
                    else:
                        self.contour_points.setdefault("other", []).append(contour_points)
            else:
                '''
                list_of_dict = pdfminer_object_decode(field_dict)
                for extracted_dict in list_of_dict:
                    contour_points = extracted_dict.get("rect")
                    self.contour_points.setdefault("art", []).append(contour_points)
                '''
                print("field mapping variable not present for {}".format(field_dict))
            print("-------" * 5)
        return form_dict

    def extract_fitz(self):
        location_tagger_mapping = {"text": "P", "checkbox": "C", "combobox": "D","radiobutton":"R"}
        fitz_pdf = fitz.Document(f'{self.config.Path.location_to_save}{self.input_pdf}')
        page = fitz_pdf[int(self.page)-1]
        form_dict = {}
        for index,obj in enumerate(page.widgets()):
            obj = obj.__dict__
            mapping_key = obj.get("field_type_string",None)
            unique_key = obj.get("field_name",None)
            field_value = obj.get("field_value",None)
            contour_points = obj.get("rect",None)
            # print(colored("mapping key","red"),"-------->",colored(mapping_key,"yellow"))
            if self.selected_points:
                # print(colored(unique_key, "red"))
                if unique_key not in self.selected_points:
                    # print(colored(self.selected_points, "blue"))
                    continue
            if mapping_key and mapping_key.lower() in location_tagger_mapping and field_value:
                form_dict[mapping_key] = form_dict.get(mapping_key,{})
                # if not form_dict[mapping_key].get("is_available", None):
                #     form_dict[mapping_key]["is_available"] = 1
                if not form_dict[mapping_key].get("content", None):
                    # print(colored("hello","blue"))
                    form_dict[mapping_key]["content"] = {}
                self.contour_points.setdefault(mapping_key, []).append(contour_points)
                x, y, x1, y1 = contour_points
                cnt_original_pts = (int(x), int(self.height_page_plumb_pdf) - int(y1), int(x1), int(self.height_page_plumb_pdf) - int(y))
                # cnt_original_pts = (int(x),int(y1), int(x1), int(y))
                center = ((cnt_original_pts[0] + (cnt_original_pts[0] + cnt_original_pts[2]) // 2) // 2,
                          (cnt_original_pts[1] + (cnt_original_pts[1] + cnt_original_pts[3]) // 2) // 2)
                location_tagger = "-".join((location_tagger_mapping[mapping_key.lower()], f"{int(self.page) + 1}#{index}", f"{center[0]}#{center[1]}"))
                form_dict[mapping_key]["content"][unique_key] = field_value
            else:
                self.contour_points.setdefault("other", []).append(obj.get("rect"))
        return form_dict

    def draw_contour_from_points(self):
        i = 0
        for key , contour_point_list in self.contour_points.items():
            for contour_point in contour_point_list:
                x,y,x1,y1 = contour_point      # diagonal points (x,y1) (x1,y)
                if key == "other":
                    pass
                    # cv2.rectangle(self.img_copy, (int(x), int(self.height_page_plumb_pdf)-int(y1)), (int(x1), int(self.height_page_plumb_pdf)-int(y)), (255, 0, 0), 5)
                else:
                    # cv2.rectangle(self.img_copy, (int(x), int(self.height_page_plumb_pdf)-int(y1)), (int(x1), int(self.height_page_plumb_pdf)-int(y)), (0, 255, 0), 5)
                    # cv2.rectangle(self.img_copy, (int(x), int(self.height_page_plumb_pdf)-int(y1)), (int(x1), int(self.height_page_plumb_pdf)-int(y)), color=self.config.Display_settings.annotation_colour, thickness=int(self.config.Display_settings.annotation_thickness))
                    cv2.rectangle(self.img_copy, (int(x), int(y1)), (int(x1), int(y)), color=self.config.Display_settings.annotation_colour, thickness=int(self.config.Display_settings.annotation_thickness))
                    # cv2.rectangle(self.img_copy, (int(x), int(self.height_page_plumb_pdf)-int(y1)), (int(x1), int(self.height_page_plumb_pdf)-int(y)), color=self.config.Display_settings.annotation_colour, thickness=3)
                # cv2.putText(sss, str(i), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 10)
                i = i + 1
        return self.img_copy

    def visual_debug(self):
        self.contour_points.clear()
        self.img_copy = self.img.copy()
        self.final_json = self.extract_fitz()
        annotated_image = self.draw_contour_from_points()
        return [annotated_image] , self.final_json



