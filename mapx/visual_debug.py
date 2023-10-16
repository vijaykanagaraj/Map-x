from .property import *
from .pre_processing import find_boxes_preprocessing , find_paragraph_preprocessing , convert_pdf_to_image , find_vertical_lines, find_horizontal_lines,find_horizontal_lines_v2,find_vertical_lines_v2 , remove_lines
from .contour_operations import FindContourOperations , FilterContourOperations , DrawOperations , MaskOperations
from .extract_and_tag import ExtractAndTagUsingContours
import numpy as np
from .find_inner_contours import find_inner_contour
from termcolor import colored


def visual_debug(basic_info:BasicInformation):
    final_json = {}
    basic_info.content_holder.contour_points = []
    table_preprocessed_image = None
    if basic_info.default_config.Extraction_settings.kind in ("TABLE","ALL"):
        table_preprocessed_image = basic_info.image_property.img_temp = find_boxes_preprocessing(basic_info)
        contours = FindContourOperations.find_contours(basic_info.image_property.img_temp,area=basic_info.default_config.Extraction_settings.custom.Table.area_filter)
        bounding_rects = FilterContourOperations.filter_contour_using_location_tagger(contours,basic_info.extraction_filter.selected_points)
        ExtractAndTagUsingContours(basic_info,bounding_rects).extract()
        # contours = self.find_selected_contours(contours,selected_points=self.selected_points)
        # self.extract_and_tag_contours(table_preprocessed_image,contours,kind=kind,check_for_inner_tables=check_for_inner_tables,method=method)
        # if basic_info.default_config.Extraction_settings.kind in ("TABLE", "All") and basic_info.default_config.Extraction_settings.check_for_nested_tables:

        if basic_info.default_config.Extraction_settings.check_for_nested_tables:
            _ = [find_inner_contour(basic_info=basic_info, parent_contour=contour, table_no=index,
                                    can_img=basic_info.image_property.img_temp) for index, contour in
                 enumerate(basic_info.content_holder.table_contours)]

    # completely_masked_image = None
    if basic_info.default_config.Extraction_settings.kind in ("PARAGRAPH","ALL") or (basic_info.default_config.Extraction_settings.kind in ("TABLE","ALL") and basic_info.default_config.Extraction_settings.check_for_table_in_paragraph):
        if basic_info.default_config.Extraction_settings.check_for_paragraph_in_table:
            # horizontal_lines_image = find_horizontal_lines(basic_info)
            # horizontal_lines_image = find_horizontal_lines_v2(basic_info.image_property.img)
            # contours = FindContourOperations.find_contours(horizontal_lines_image)
            # horizontal_lines_masked_image = MaskOperations(basic_info=basic_info).mask_contour_using_bounding_rects(img=basic_info.image_property.img,contours=contours)
            #
            # # vertical_lines_image = find_vertical_lines(basic_info)
            # vertical_lines_image = find_vertical_lines_v2(horizontal_lines_masked_image)
            # contours = FindContourOperations.find_contours(vertical_lines_image)
            # completely_masked_image = MaskOperations(basic_info=basic_info).mask_contour_using_bounding_rects(img=horizontal_lines_masked_image,contours=contours)

            completely_masked_image = remove_lines(basic_info.image_property.img)

            # table_preprocessed_image = find_boxes_preprocessing(basic_info)  # finding table or box area
            # # cv2.imwrite(f"{basic_info.default_config.Path.location_to_save}table_camelot_processed.png",table_preprocessed_image)
            # contours = FindContourOperations.find_contours(table_preprocessed_image,area=basic_info.default_config.Extraction_settings.custom.Table.area_filter)
            # # thick_lines_contour = self.find_thick_lines(table_preprocessed_image)  # only for table to detect thick lines and mask them
            # # _ = [self.mask_contour_using_bounding_rect(t_c) for t_c in thick_lines_contour]
            # bounding_rects = FilterContourOperations.filter_contour_using_location_tagger(contours,basic_info.extraction_filter.selected_points)
            # ExtractAndTagUsingContours(basic_info, bounding_rects).extract()
            # # basic_info.image_property.img_temp = MaskOperations(basic_info=basic_info).mask_contour_using_bounding_rects(basic_info.image_property.img,basic_info.content_holder.table_contours)
            # basic_info.image_property.img_temp = MaskOperations(basic_info=basic_info).mask_contour_using_bounding_rects(completely_masked_image,basic_info.content_holder.table_contours)
            # cv2.imwrite(f"{basic_info.default_config.Path.location_to_save}table_masked.png",basic_info.image_property.img_temp)
            # _ = self.find_contour_and_extract_content(table_preprocessed_image,area=area,mask=True,save_coordinates=False)   # mask table or box area so we can have normal text seperately
            basic_info.image_property.img_temp = find_paragraph_preprocessing(basic_info,img=completely_masked_image)
            cv2.imwrite(f"{basic_info.default_config.Path.location_to_save}para_processed.png",basic_info.image_property.img_temp)
            contours = FindContourOperations.find_contours(basic_info.image_property.img_temp,area=basic_info.default_config.Extraction_settings.custom.Paragraph.area_filter)
            bounding_rects = FilterContourOperations.filter_contour_using_location_tagger(contours,basic_info.extraction_filter.selected_points)
            ExtractAndTagUsingContours(basic_info, bounding_rects).extract()
        else:
            table_preprocessed_image = find_boxes_preprocessing(basic_info)  # finding table or box area
            # cv2.imwrite(f"{basic_info.default_config.Path.location_to_save}table_processed.png",table_preprocessed_image)
            contours = FindContourOperations.find_contours(table_preprocessed_image,area=basic_info.default_config.Extraction_settings.custom.Table.area_filter)
            # thick_lines_contour = self.find_thick_lines(table_preprocessed_image)  # only for table to detect thick lines and mask them
            # _ = [self.mask_contour_using_bounding_rect(t_c) for t_c in thick_lines_contour]
            bounding_rects = FilterContourOperations.filter_contour_using_location_tagger(contours,basic_info.extraction_filter.selected_points)
            ExtractAndTagUsingContours(basic_info,bounding_rects).extract()
            basic_info.image_property.img_temp = MaskOperations(basic_info=basic_info).mask_contour_using_bounding_rects(basic_info.image_property.img,basic_info.content_holder.table_contours)
            # cv2.imwrite(f"{basic_info.default_config.Path.location_to_save}table_masked.png",basic_info.image_property.img_temp)
            # _ = self.find_contour_and_extract_content(table_preprocessed_image,area=area,mask=True,save_coordinates=False)   # mask table or box area so we can have normal text seperately
            basic_info.image_property.img_temp = find_paragraph_preprocessing(basic_info)
            # cv2.imwrite(f"{basic_info.default_config.Path.location_to_save}para_processed.png",basic_info.image_property.img_temp)
            contours = FindContourOperations.find_contours(basic_info.image_property.img_temp,area=basic_info.default_config.Extraction_settings.custom.Paragraph.area_filter)
            bounding_rects = FilterContourOperations.filter_contour_using_location_tagger(contours,basic_info.extraction_filter.selected_points)
            ExtractAndTagUsingContours(basic_info,bounding_rects).extract()

    basic_info.content_holder.table_content = FilterContourOperations.filter_content_using_child_and_bucket(basic_info=basic_info)

    print(basic_info.content_holder.table_content)
    print(basic_info.content_holder.paragraph_content)
    annotated_image = DrawOperations(basic_info=basic_info).draw_contour_from_points(img=basic_info.image_property.img,contour_points=basic_info.content_holder.contour_points)
    print("type---->", type(annotated_image))
    if basic_info.content_holder.paragraph_content:
        final_json["paragraph"] = {"is_available": 1, "content": basic_info.content_holder.paragraph_content}
    if basic_info.content_holder.table_content:
        final_json["table"] = {"is_available": 1, "content": basic_info.content_holder.table_content}
    # return annotated_image,list(self.paragraph_content.values()),list(self.table_content.values())
    if basic_info.default_config.Extraction_settings.kind == "ALL":
        print("img_temp---shape---->",basic_info.image_property.img_temp.shape)
        print("table---shape---->",table_preprocessed_image.shape)
        # images = [image for image in [annotated_image, basic_info.image_property.img_temp] if isinstance(image, np.ndarray)]
        images = [image for image in [annotated_image, cv2.add(basic_info.image_property.img_temp,table_preprocessed_image)] if isinstance(image, np.ndarray)]
    else:
        images = [image for image in [annotated_image,basic_info.image_property.img_temp] if isinstance(image, np.ndarray)]
        # images = [image for image in [annotated_image,completely_masked_image] if isinstance(image, np.ndarray)]
    return images, final_json

def visual_debug_updated(basic_info:BasicInformation):
    final_json = {}
    basic_info.content_holder.contour_points = []
    table_preprocessed_image = None
    if "TABLE" == basic_info.default_config.Extraction_settings.kind:
        basic_info.image_property.img_temp = find_boxes_preprocessing(basic_info)
        contours = FindContourOperations.find_contours(basic_info.image_property.img_temp,area=basic_info.default_config.Extraction_settings.custom.Table.area_filter)
        bounding_rects = FilterContourOperations.filter_contour_using_location_tagger(contours,basic_info.extraction_filter.selected_points)
        ExtractAndTagUsingContours(basic_info,bounding_rects).extract()
        # contours = self.find_selected_contours(contours,selected_points=self.selected_points)
        # self.extract_and_tag_contours(table_preprocessed_image,contours,kind=kind,check_for_inner_tables=check_for_inner_tables,method=method)

    elif basic_info.default_config.Extraction_settings.kind in ("PARAGRAPH","ALL"):
        table_preprocessed_image = find_boxes_preprocessing(basic_info)  # finding table or box area
        contours = FindContourOperations.find_contours(table_preprocessed_image,area=basic_info.default_config.Extraction_settings.custom.Table.area_filter)
        # thick_lines_contour = self.find_thick_lines(table_preprocessed_image)  # only for table to detect thick lines and mask them
        # _ = [self.mask_contour_using_bounding_rect(t_c) for t_c in thick_lines_contour]
        bounding_rects = FilterContourOperations.filter_contour_using_location_tagger(contours,basic_info.extraction_filter.selected_points)
        ExtractAndTagUsingContours(basic_info,bounding_rects).extract()
        basic_info.image_property.img_temp = MaskOperations(basic_info=basic_info).mask_contour_using_bounding_rects(basic_info.image_property.img,basic_info.content_holder.table_contours)

        # _ = self.find_contour_and_extract_content(table_preprocessed_image,area=area,mask=True,save_coordinates=False)   # mask table or box area so we can have normal text seperately
        basic_info.image_property.img_temp = find_paragraph_preprocessing(basic_info)
        contours = FindContourOperations.find_contours(basic_info.image_property.img_temp,area=basic_info.default_config.Extraction_settings.custom.Paragraph.area_filter)
        bounding_rects = FilterContourOperations.filter_contour_using_location_tagger(contours,basic_info.extraction_filter.selected_points)
        ExtractAndTagUsingContours(basic_info,bounding_rects).extract()

    print(basic_info.content_holder.table_content)
    print(basic_info.content_holder.paragraph_content)
    annotated_image = DrawOperations(basic_info=basic_info).draw_contour_from_points(img=basic_info.image_property.img,contour_points=basic_info.content_holder.contour_points)
    print("type---->", type(annotated_image))
    if basic_info.content_holder.paragraph_content:
        final_json["paragraph"] = {"is_available": 1, "content": basic_info.content_holder.paragraph_content}
    if basic_info.content_holder.table_content:
        final_json["table"] = {"is_available": 1, "content": basic_info.content_holder.table_content}
    # return annotated_image,list(self.paragraph_content.values()),list(self.table_content.values())
    if basic_info.default_config.Extraction_settings.kind == "ALL":
        images = [image for image in [annotated_image, cv2.add(basic_info.image_property.img_temp,table_preprocessed_image)] if isinstance(image, np.ndarray)]
    else:
        images = [image for image in [annotated_image,basic_info.image_property.img_temp] if isinstance(image, np.ndarray)]
    return images, final_json




