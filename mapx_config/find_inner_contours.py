import cv2
import imutils
import time
from .property import BasicInformation
from collections import namedtuple
import numpy as np
from .data_extraction import extract_content_from_bounding_rect
import asyncio
from termcolor import colored

def find_inner_contour(basic_info:BasicInformation,can_img, parent_contour, table_no=0):
    print("inside inner contour")
    final_contours = []
    table_content = {}

    # decode_area_to_filter
    area_filter = namedtuple('area_filter', ['min', 'max'], defaults=[0, np.inf])
    area = area_filter(*basic_info.default_config.Extraction_settings.custom.Nested_table.area_filter)
    print("area----->vaada",area)
    # decode_area_to_filter end

    # find tree contour
    cnts = cv2.findContours(can_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts1 = imutils.grab_contours(cnts)
    print("no_off_contour----->", len(cnts1))
    start_time = time.perf_counter()
    cnts2 = [cnt for cnt in cnts1 if area.min < cv2.contourArea(cnt) < area.max]
    print("time taken by filtering contour area---->", time.perf_counter() - start_time)
    print("no_off_contour----->", len(cnts2))
    # find tree contour end

    # start_time = time.perf_counter()
    # for ind, contour in enumerate(cnts2):
    #     x, y, w, h = cv2.boundingRect(contour)
    #     if (x, y, w, h) == bounding_rect:
    #         parent_contour = cnts2.pop(ind)
    #         print("parent_contour----->", x, y, w, h)
    #         break
    # print("time taken to find parent contour---->", time.perf_counter() - start_time)
    # parent contour fetched directly from global content holder
    parent_bounding_rect = cv2.boundingRect(parent_contour)

    start_time = time.perf_counter()
    for contour in cnts2:
        x, y, w, h = cv2.boundingRect(contour)
        if parent_bounding_rect != (x, y, w, h):
            cnt_original_pts = (x, y, x + w, y + h)
            print("------" * 10)
            center = ((cnt_original_pts[0] + (cnt_original_pts[0] + cnt_original_pts[2]) // 2) // 2,
                      (cnt_original_pts[1] + (cnt_original_pts[1] + cnt_original_pts[3]) // 2) // 2)
            print("child_contour----->", cnt_original_pts)
            print("child_center----->", center)
            result = cv2.pointPolygonTest(parent_contour, center,False)  # if false , it will tell 1,-1,0 .if true it measuure distance bw point and contour
            print("point-polygon-test----->", result)
            if int(result) >= 0:
                type, content = extract_content_from_bounding_rect(basic_info=basic_info,bounding_rect=(x, y, w, h),nested_table=True)
                print(content)
                if type == "table":
                    final_contours.append(contour)
                    key = "-".join(("T", f"{int(basic_info.pdf_property.page_no)}#{table_no}C", f"{center[0]}#{center[1]}"))
                    table_content[key] = content[0]
                    # for visual annotation
                    # self.contour_points.append((x, y, x + w, y + h))
                    # self.normalized_contour_points.append((self.width / (x), self.height / (y),
                    #                                        self.width / (x + w),
                    #                                        self.height / (y + h)))
    # '''
    print("time taken to extract--content parent contour---->", time.perf_counter() - start_time)
    print("final_contours---->", len(final_contours))
    selected = []
    selected_index = []
    start_time = time.perf_counter()
    final_contours.sort(key=lambda cnt: cv2.contourArea(cnt), reverse=True)
    print("time taken to sort final contour---->", time.perf_counter() - start_time)
    # final_contours.sort(key=lambda cnt: cv2.contourArea(cnt))
    print([cv2.contourArea(cnt) for cnt in final_contours])
    # """
    start_time = time.perf_counter()
    index_to_ignore = []
    for index in range(len(final_contours)):
        status = []
        print("selected index----->", selected_index)
        print(index, "+++++++++++", index_to_ignore)
        if index not in index_to_ignore:
            x, y, w, h = cv2.boundingRect(final_contours[index])
            # center = (x0 + w0 // 2, y0 + h0 // 2)
            for ind, br in enumerate(final_contours):
                if ind != index:
                    print("ind----->", ind)
                    current_bounding_rect = cv2.boundingRect(br)
                    x0, y0, w0, h0 = current_bounding_rect
                    print(x0, y0, w0, h0)
                    center = (x0 + w0 // 2, y0 + h0 // 2)
                    # if cv2.boundingRect(br) != current_bounding_rect:
                    # self.draw_point((x0+(w0-20),y0+(h0-20)))
                    print("point to test inside point polygon test", (x0 + (w0 - 20), y0 + (h0 - 20)))
                    result = cv2.pointPolygonTest(final_contours[index], (x0 + (w0 - 20), y0 + (h0 - 20)), False)
                    print("point_polygon_test-----?", result)
                    if result > 0 or not (x0 in range(x - 5, x + 5) and x0 + w0 in range(x + w - 5, x + w + 5)):
                        index_to_ignore.append(ind)
                        status.append(True)

        else:
            status.append(False)
        print("length_of_status---->", status)
        if any(status) or not status:
            selected.append(final_contours[index])
            selected_index.append(index)
            continue
        print("selected index----->", selected_index)
    print("time taken to find selected contours---->", time.perf_counter() - start_time)
    for contour in selected:
        x, y, w, h = cv2.boundingRect(contour)
        cnt_original_pts = (x, y, x + w, y + h)
        center = ((cnt_original_pts[0] + (cnt_original_pts[0] + cnt_original_pts[2]) // 2) // 2,
                  (cnt_original_pts[1] + (cnt_original_pts[1] + cnt_original_pts[3]) // 2) // 2)
        key = "-".join(("T", f"{int(basic_info.pdf_property.page_no)}#{table_no}C", f"{center[0]}#{center[1]}"))
        print("king kong----->",key)
        basic_info.content_holder.table_content[key] = table_content[key]
        # for visual annotation
        basic_info.content_holder.contour_points.append((x, y, x + w, y + h))
        # self.normalized_contour_points.append((basic_info.image_property.width / (x), basic_info.image_property.height / (y),
        #                                        basic_info.image_property.width / (x + w),
        #                                        basic_info.image_property.height / (y + h)))
    print("selected_contours------>", len(selected))
    return final_contours

# def find_inner_contour_v2(basic_info:BasicInformation,can_img, parent_contour, table_no=0):
#     print("inside inner contour")
#     final_contours = []
#     table_content = {}
#
#     # decode_area_to_filter
#     area_filter = namedtuple('area_filter', ['min', 'max'], defaults=[0, np.inf])
#     area = area_filter(*basic_info.default_config.Extraction_settings.custom.Table.area_filter)
#     # decode_area_to_filter end
#
#     # find tree contour
#     cnts = cv2.findContours(can_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     cnts1 = imutils.grab_contours(cnts)
#     print("no_off_contour----->", len(cnts1))
#     start_time = time.perf_counter()
#     cnts2 = [cnt for cnt in cnts1 if area.min < cv2.contourArea(cnt) < area.max]
#     print("time taken by filtering contour area---->", time.perf_counter() - start_time)
#     print("no_off_contour----->", len(cnts2))
#     # find tree contour end
#
#     # parent contour fetched directly from global content holder
#     parent_bounding_rect = cv2.boundingRect(parent_contour)
#     # cnts2.remove(parent_contour)
#
#     start_time = time.perf_counter()
#     point_polygon_test = asyncio.run(find_contours_inside_parent_contour(basic_info,cnts2,parent_contour))
#     async_result = time.perf_counter()-start_time
#     print(colored("time taken to find point polygon test----->","red"),time.perf_counter()-start_time)
#     print(colored("time taken to find point polygon test results----->","red"),point_polygon_test)
#     start_time = time.perf_counter()
#     point_poly_gon_test = []
#     for contour in cnts2:
#         x, y, w, h = cv2.boundingRect(contour)
#         cnt_original_pts = (x, y, x + w, y + h)
#         print("------" * 10)
#         center = ((cnt_original_pts[0] + (cnt_original_pts[0] + cnt_original_pts[2]) // 2) // 2,
#                   (cnt_original_pts[1] + (cnt_original_pts[1] + cnt_original_pts[3]) // 2) // 2)
#         # print("child_contour----->", cnt_original_pts)
#         # print("child_center----->", center)
#         result = cv2.pointPolygonTest(parent_contour, center,False)  # if false , it will tell 1,-1,0 .if true it measuure distance bw point and contour
#         # print("point-polygon-test----->", result)
#         if int(result) >= 0:
#             type, content = extract_content_from_bounding_rect(basic_info=basic_info, bounding_rect=(x, y, w, h))
#             point_poly_gon_test.append(content)
#     print(colored("time taken to find point polygon original----->", "green"), time.perf_counter() - start_time)
#     print(colored("time taken to find point polygon test results original----->", "green"), point_polygon_test)
#     sync_result = time.perf_counter() - start_time
#     for contour in cnts2:
#         x, y, w, h = cv2.boundingRect(contour)
#         cnt_original_pts = (x, y, x + w, y + h)
#         print("------" * 10)
#         center = ((cnt_original_pts[0] + (cnt_original_pts[0] + cnt_original_pts[2]) // 2) // 2,
#                   (cnt_original_pts[1] + (cnt_original_pts[1] + cnt_original_pts[3]) // 2) // 2)
#         print("child_contour----->", cnt_original_pts)
#         print("child_center----->", center)
#         result = cv2.pointPolygonTest(parent_contour, center,False)  # if false , it will tell 1,-1,0 .if true it measuure distance bw point and contour
#         print("point-polygon-test----->", result)
#         if int(result) >= 0:
#             type, content = extract_content_from_bounding_rect(basic_info=basic_info,bounding_rect=(x, y, w, h))
#             print(content)
#             if type == "table":
#                 final_contours.append(contour)
#                 key = "-".join(("T", f"{int(basic_info.pdf_property.page_no) + 1}#{table_no}C", f"{center[0]}#{center[1]}"))
#                 table_content[key] = content[0]
#                 # for visual annotation
#                 # self.contour_points.append((x, y, x + w, y + h))
#                 # self.normalized_contour_points.append((self.width / (x), self.height / (y),
#                 #                                        self.width / (x + w),
#                 #                                        self.height / (y + h)))
# # '''
#     print("time taken to extract--content parent contour---->", time.perf_counter() - start_time)
#     print("final_contours---->", len(final_contours))
#     selected = []
#     selected_index = []
#     start_time = time.perf_counter()
#     final_contours.sort(key=lambda cnt: cv2.contourArea(cnt), reverse=True)
#     print("time taken to sort final contour---->", time.perf_counter() - start_time)
#     # final_contours.sort(key=lambda cnt: cv2.contourArea(cnt))
#     print([cv2.contourArea(cnt) for cnt in final_contours])
#     # """
#     start_time = time.perf_counter()
#     index_to_ignore = []
#     for index in range(len(final_contours)):
#         status = []
#         print("selected index----->", selected_index)
#         print(index, "+++++++++++", index_to_ignore)
#         if index not in index_to_ignore:
#             x, y, w, h = cv2.boundingRect(final_contours[index])
#             # center = (x0 + w0 // 2, y0 + h0 // 2)
#             for ind, br in enumerate(final_contours):
#                 if ind != index:
#                     print("ind----->", ind)
#                     current_bounding_rect = cv2.boundingRect(br)
#                     x0, y0, w0, h0 = current_bounding_rect
#                     print(x0, y0, w0, h0)
#                     center = (x0 + w0 // 2, y0 + h0 // 2)
#                     # if cv2.boundingRect(br) != current_bounding_rect:
#                     # self.draw_point((x0+(w0-20),y0+(h0-20)))
#                     print("point to test inside point polygon test", (x0 + (w0 - 20), y0 + (h0 - 20)))
#                     result = cv2.pointPolygonTest(final_contours[index], (x0 + (w0 - 20), y0 + (h0 - 20)), False)
#                     print("point_polygon_test-----?", result)
#                     if result > 0 or not (x0 in range(x - 5, x + 5) and x0 + w0 in range(x + w - 5, x + w + 5)):
#                         index_to_ignore.append(ind)
#                         status.append(True)
#
#         else:
#             status.append(False)
#         print("length_of_status---->", status)
#         if any(status) or not status:
#             selected.append(final_contours[index])
#             selected_index.append(index)
#             continue
#         print("selected index----->", selected_index)
#     print("time taken to find selected contours---->", time.perf_counter() - start_time)
#     for contour in selected:
#         x, y, w, h = cv2.boundingRect(contour)
#         cnt_original_pts = (x, y, x + w, y + h)
#         center = ((cnt_original_pts[0] + (cnt_original_pts[0] + cnt_original_pts[2]) // 2) // 2,
#                   (cnt_original_pts[1] + (cnt_original_pts[1] + cnt_original_pts[3]) // 2) // 2)
#         key = "-".join(("T", f"{int(basic_info.pdf_property.page_no) + 1}#{table_no}C", f"{center[0]}#{center[1]}"))
#         basic_info.content_holder.table_content[key] = table_content[key]
#         # for visual annotation
#         basic_info.content_holder.contour_points.append((x, y, x + w, y + h))
#         # self.normalized_contour_points.append((basic_info.image_property.width / (x), basic_info.image_property.height / (y),
#         #                                        basic_info.image_property.width / (x + w),
#         #                                        basic_info.image_property.height / (y + h)))
#     print("selected_contours------>", len(selected))
#     print("async------>", async_result)
#     print("sync------>", sync_result)
#     return final_contours
#
# async def find_bounding_rect(contour):
#     return cv2.boundingRect(contour)
#
# async def find_center_point(bounding_rect):
#     x, y, w, h = bounding_rect
#     cnt_original_pts = (x, y, x + w, y + h)
#     center = ((cnt_original_pts[0] + (cnt_original_pts[0] + cnt_original_pts[2]) // 2) // 2,
#               (cnt_original_pts[1] + (cnt_original_pts[1] + cnt_original_pts[3]) // 2) // 2)
#     await asyncio.sleep(0)
#     return center
#
# async def is_contour_inside_parent(parent_contour,child_contour_center):
#     point_polygon_test = cv2.pointPolygonTest(parent_contour, child_contour_center, False)
#     await asyncio.sleep(0)
#     return point_polygon_test
#
# from .data_extraction import async_extract_content_from_bounding_rect
#
# async def async_extract_content(basic_info:BasicInformation,bounding_rect,point_polygon_result):
#     if point_polygon_result:
#         type, content = await async_extract_content_from_bounding_rect(basic_info=basic_info, bounding_rect= bounding_rect)
#         if type == "table":
#             return content[0]
#         else:
#             return False
#     else:
#         return False
#
# async def find_contours_inside_parent_contour(basic_info:BasicInformation,contours,parent_contour):
#     bounding_rects = await asyncio.gather(*[find_bounding_rect(contour) for contour in contours])
#     contour_centers = await asyncio.gather(*[find_center_point(bounding_rect) for bounding_rect in bounding_rects])
#     point_polygon_test_results = await asyncio.gather(*[is_contour_inside_parent(parent_contour,contour_center) for contour_center in contour_centers])
#     # extracted_contents = await asyncio.gather(*[async_extract_content(basic_info,bounding_rects[index]) if point_polygon_test_result else False for index,point_polygon_test_result in enumerate(point_polygon_test_results)])
#     sta = time.perf_counter()
#     extracted_contents = await asyncio.gather(*[async_extract_content(basic_info,bounding_rects[index],point_polygon_test_result) for index,point_polygon_test_result in enumerate(point_polygon_test_results)])
#     print(colored("time takkkkkkkkkk---->","red"),time.perf_counter()-sta)
#     return extracted_contents