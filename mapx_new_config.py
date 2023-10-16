import pathlib

from mapx_config import *
from config.load_config import get_config
import fitz

default_configuration = get_config()

def is_form_pdf(input_pdf):
    doc = fitz.Document(f"{default_configuration.Path.location_to_save}{input_pdf}")
    if doc.is_form_pdf:
        return True
    else:
        return False

def is_pdf(input_pdf):
    doc = fitz.Document(f"{default_configuration.Path.location_to_save}{input_pdf}")
    if doc.is_pdf:
        return True
    else:
        return False

def get_pages_count(input_pdf):
    doc = fitz.Document(f"{default_configuration.Path.location_to_save}{input_pdf}")
    return doc.page_count

def streamlit_main(**kwargs):

    input_pdf = kwargs.get("input_pdf",None)
    page = kwargs.get("page",None)

    try:
        default_configuration = get_config(account=kwargs.get("account",None))
    except:
        raise Exception("Setting not available")

    print(colored(default_configuration,"red"))

    if not input_pdf or not page:
        raise ValueError("Please provide proper inputs")

    if kwargs.get("camelot_settings",None):
        for key , value in kwargs.get("camelot_settings").items():
            default_configuration.Camelot.Settings.Stream[key] = value

    if kwargs.get("annotation_colour",None):
        default_configuration.Display_settings.annotation_colour = kwargs.get("annotation_colour")

    if kwargs.get("extraction_settings",None):
        for key , value in kwargs.get("extraction_settings").items():
            default_configuration.Extraction_settings[key] = value

        ##End##
        # print("default_extraction_settings manual----->",default_configuration.Extraction_settings)

    ##########
    pdf_property = PdfProperty(f"{default_configuration.Path.location_to_save}{input_pdf}", page_no=page)
    filter_property = SelectedPoints(selected_points=kwargs.get("filter_settings",{}).get("selected_points",[]))
    content_holder = GlobalContentHolder()
    image = f"{default_configuration.Path.location_to_save}{pathlib.Path(input_pdf).stem}_{str(page)}.png"
    if not os.path.exists(image):
        convert_pdf_to_image(input_pdf=input_pdf,location_to_save=default_configuration.Path.location_to_save)
    image_property = ImageProperty(image=image)     # need to add pdf file name and page name to work dynamically
    basic_info = BasicInformation(pdf_property=pdf_property,image_property=image_property,content_holder=content_holder,default_config=default_configuration,extraction_filter=filter_property)
    annotated,final_json = visual_debug(basic_info)
    return [annotated, final_json]

def form_pdf_main(**kwargs):
    input_pdf = kwargs.get("input_pdf", None)
    # input_image = f"{default_configuration.Path.location_to_save}{str(params.get('page',None))}.png"
    page = kwargs.get("page", None)
    default_configuration = get_config(account=kwargs.get("account", None))
    if kwargs.get("annotation_colour",None):
        default_configuration.Display_settings.annotation_colour = kwargs.get("annotation_colour")
    if kwargs.get("extraction_settings",None):
        for key , value in kwargs.get("extraction_settings").items():
            default_configuration.Extraction_settings[key] = value

    selected_points = kwargs.get("filter_settings",{}).get("selected_points", [])

    if not input_pdf or not page:
        raise ValueError("Please provide proper inputs")

    input_image = f"{default_configuration.Path.location_to_save}{pathlib.Path(input_pdf).stem}_{str(page)}.png"
    if not os.path.exists(input_image):
        convert_pdf_to_image(input_pdf=input_pdf,location_to_save=default_configuration.Path.location_to_save)
    kwargs["config"] = default_configuration
    kwargs["selected_points"] = selected_points
    return FormROIExtractor(**kwargs).visual_debug()


def main(**params):
    input_pdf = params.get("input_pdf",None)
    if is_form_pdf(input_pdf):
        print(colored("form pdf","yellow"))
        images,final_json = form_pdf_main(**params)
        # images, final_json = streamlit_main(**params)
    else:
        images , final_json = streamlit_main(**params)
    return images , final_json












