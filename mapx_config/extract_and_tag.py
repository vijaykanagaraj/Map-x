import cv2
from .data_extraction import extract_content_from_bounding_rect , is_df_with_multiple_columns
from .property import BasicInformation

class ExtractAndTagUsingContours:
    def __init__(self,basic_info:BasicInformation,bounding_rects):
        self.basic_info = basic_info
        self.contours = bounding_rects

    def extract(self):
        table_count, paragraph_count = 0, 0
        for index, contour in enumerate(self.contours):
            bounding_rect = cv2.boundingRect(contour)
            x, y, w, h = bounding_rect
            cnt_original_pts = (x, y, x + w, y + h)
            type, content = extract_content_from_bounding_rect(basic_info=self.basic_info,bounding_rect=bounding_rect)
            # if type == "table" and is_df_with_multiple_columns(content[0], 5):
            #     if self.basic_info.extraction_filter.check_for_inner_tables and self.basic_info.extraction_filter.kind in ("ALL", "TABLE"):
            #         print("appending_contour for inner contour search")
            #         # self.basic_info.content_holder.table_contours.append(contour)
                    # find_inner_contour(can_img, bounding_rect, table_no=table_count, method=method, area=area)
                    # self.draw_contour(inner_cnts)
            center = ((cnt_original_pts[0] + (cnt_original_pts[0] + cnt_original_pts[2]) // 2) // 2,
                      (cnt_original_pts[1] + (cnt_original_pts[1] + cnt_original_pts[3]) // 2) // 2)
            if content:
                if type == "table":
                    self.basic_info.content_holder.table_contours.append(contour)
                    if self.basic_info.default_config.Extraction_settings.kind in ("TABLE", "ALL") or (self.basic_info.default_config.Extraction_settings.kind in ("TABLE", "ALL") and self.basic_info.default_config.Extraction_settings.check_for_table_in_paragraph):
                        key = "-".join(("T", f"{int(self.basic_info.pdf_property.page_no)}#{table_count}", f"{center[0]}#{center[1]}"))
                        self.basic_info.content_holder.table_content[key] = content[0]
                        # for visual annotation
                        self.basic_info.content_holder.contour_points.append((x, y, x + w, y + h))
                        table_count = table_count + 1
                elif type == "content":
                    self.basic_info.content_holder.paragraph_contours.append(contour)
                    if self.basic_info.default_config.Extraction_settings.kind in ("PARAGRAPH", "ALL"):
                        key = "-".join(("P", f"{int(self.basic_info.pdf_property.page_no)}#{paragraph_count}", f"{center[0]}#{center[1]}"))
                        self.basic_info.content_holder.paragraph_content[key] = content
                        # for visual annotation
                        self.basic_info.content_holder.contour_points.append((x, y, x + w, y + h))
                        paragraph_count = paragraph_count + 1
        return

