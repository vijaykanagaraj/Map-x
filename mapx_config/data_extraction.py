import asyncio

import camelot
import pandas as pd

from .property import BasicInformation

is_df_with_multiple_columns = lambda table,threshold: True if any([True for row in table if len(row) > threshold]) or len([True for row in table if len(row) > 1]) > threshold else False

def content_within_bounding_box_camelot(basic_info:BasicInformation, coordinates_percent):
    pdf = basic_info.pdf_property.plumber_pdf
    page = pdf.pages[int(basic_info.pdf_property.page_no) - 1]
    width , height = float(page.width) , float(page.height)
    w0, h0, w1, h1 = coordinates_percent
    coordinates = (width / w0, height / h0, width / w1,height / h1)
    coordinates = [coordinate if coordinate > 0 else float(0.0) for coordinate in coordinates]
    # for camelot
    coordinates_int = [int(value) for value in coordinates]
    coordinates_int = [coordinates_int[0], int(height) - coordinates_int[1], coordinates_int[2],
                       int(height) - coordinates_int[3]]
    try:
        # camelot_table = camelot.read_pdf(basic_info.pdf_property.input_pdf, pages=str(basic_info.pdf_property.page_no), flavor="stream",row_tol=basic_info.default_config.Camelot.Settings.Stream.row_tol,
        #                                  table_areas=[f'{coordinates_int[0]},{int(coordinates_int[1])},{coordinates_int[2]},{coordinates_int[3]}'])
        print("camelot_settings----->",basic_info.default_config.Camelot.Settings.Stream)
        try:
            camelot_table = camelot.read_pdf(filepath=basic_info.pdf_property.input_pdf, pages=str(basic_info.pdf_property.page_no),table_areas=[f'{coordinates_int[0]},{int(coordinates_int[1])},{coordinates_int[2]},{coordinates_int[3]}'],**basic_info.default_config.Camelot.Settings.Stream)
            print("inside try block")
        except:
            print("inside except block")
            camelot_table = camelot.read_pdf(basic_info.pdf_property.input_pdf,
                                             pages=str(basic_info.pdf_property.page_no), flavor="stream",
                                             row_tol=basic_info.default_config.Camelot.Settings.Stream.row_tol,
                                             table_areas=[
                                                 f'{coordinates_int[0]},{int(coordinates_int[1])},{coordinates_int[2]},{coordinates_int[3]}'])
        # print(len(camelot_table))
    except Exception as E:
        print("error---->", E)
        print("camelot content not available")
        yield ("", "content")
    else:
        df = camelot_table[0].df
        if is_df_with_multiple_columns(df.values.tolist(), basic_info.default_config.Camelot.Table_filter.min_columns):
            content = [df.values.tolist()]
            yield (content, "table")
        else:
            # ROI = page.within_bbox(coordinates, relative=False)
            # content = ROI.extract_text()
            # print("content_extracted---->", content)
            # yield (content, 'content')
            # content = "\n".join(df.loc[:, 0].to_list())
            content = []
            for row in list(df.index):
                content.append(" ".join([value for value in df.loc[row].tolist() if value]))
            content = "\n".join(content)
            print("content_extracted- new---->", content)
            yield (content, "content")
        '''
        for table in camelot_table:
            df = table.df
            print(df)
            print("-----"*10)
            if is_df_with_multiple_columns(df.values.tolist()):
                content = [df.values.tolist()]
                yield (content, "table")
            else:
                content = "\n".join(df.loc[:,0].to_list())
                yield (content, "content")
        '''

def content_within_bounding_box_plumber(basic_info:BasicInformation, coordinates_percent):
    pdf = basic_info.pdf_property.plumber_pdf
    page = pdf.pages[int(basic_info.pdf_property.page_no) - 1]
    width , height = float(page.width) , float(page.height)
    w0, h0, w1, h1 = coordinates_percent
    coordinates = (width / w0, height / h0, width / w1,height / h1)
    print("plumber--coordinates---->", coordinates)
    print("plumber--height---->", height)
    print("plumber--width---->", width)
    try:
        ROI = page.within_bbox(coordinates, relative=False)
    except:
        print("coordinated are edited to enclose it with main page")
        print("coordinates_original------->",coordinates)
        # coordinates = [coordinate if index in (1,2) and coordinate > 0 else float(0.0) for index,coordinate in enumerate(coordinates)]
        coordinates_changed = []
        for index ,coordinate in enumerate(coordinates):
            if index == 0 and coordinate < 0:
                coordinate = float(0.0)
            if index == 1 and coordinate < 0:
                coordinate = float(0.0)
            if index == 2 and float(coordinate) > float(width):
                coordinate = width
            if index == 3 and float(coordinate) > float(height):
                coordinate = height
            coordinates_changed.append(coordinate)
        ROI = page.within_bbox(coordinates_changed, relative=False)
        print("coordinates_changed------->",coordinates_changed)
    table_custom = ROI.extract_tables(
        table_settings={"vertical_strategy": basic_info.default_config.Pdfplumber.Settings.vertical_strategy, "horizontal_strategy": basic_info.default_config.Pdfplumber.Settings.horizontal_strategy, "snap_tolerance": basic_info.default_config.Pdfplumber.Settings.snap_tolerance})
    table_normal = ROI.extract_tables()
    print("table_custom---->", table_normal)
    print("table_normal---->", table_custom)
    table = []
    if table_normal and table_custom:
        table_custom_shape = pd.DataFrame(table_custom[0]).shape[1]
        table_normal_shape = pd.DataFrame(table_normal[0]).shape[1]
        if table_normal_shape == table_custom_shape:
            table = table_custom
        elif table_normal_shape > table_custom_shape:
            table = table_normal
        else:
            table = table_custom
    elif table_normal and not table_custom:
        table = table_normal
    elif table_custom and not table_normal:
        table = table_custom

    if table:
        print("table----->", table)
        # table_cleaned = [[cell for cell in row if str(cell).strip() and cell] for row in table[0]]
        table_cleaned = table[0]
        print("table---cleaned---->", table_cleaned)
        if is_df_with_multiple_columns(table_cleaned, basic_info.default_config.Pdfplumber.Table_filter.min_columns):
            yield (table, 'table')
        else:
            content = ROI.extract_text()
            yield (content, 'content')
    else:
        content = ROI.extract_text()
        print("content_extracted---->", content)
        yield (content, 'content')

def extract_content_from_bounding_rect(basic_info:BasicInformation,bounding_rect,**kwargs):
    '''
    input -> pass single value from cv2.bounding_rect
    method should be one of ["pdfplumber","camelot"].
    output -> (type,content)
    '''
    check_for_nested_table = kwargs.get("nested_table",False)
    x, y, w, h = bounding_rect
    # normalized_contour = (self.width / (x - 10), self.height / (y - 10), self.width / (x + w + 20), self.height / (y + h + 20))
    if check_for_nested_table:
        if basic_info.default_config.Extraction_settings.custom.Nested_table.strategy == "camelot":
            extraction_method = content_within_bounding_box_camelot
            normalized_contour = (basic_info.image_property.width / (x - 4), basic_info.image_property.height / (y - 4), basic_info.image_property.width / (x + w), basic_info.image_property.height / (y + h))
        else:
            extraction_method = content_within_bounding_box_plumber
            normalized_contour = (basic_info.image_property.width / (x - 5), basic_info.image_property.height / (y - 5), basic_info.image_property.width / (x + w + 10), basic_info.image_property.height / (y + h + 10))
    elif basic_info.default_config.Extraction_settings.kind.lower() == "all":
        if basic_info.default_config.Extraction_settings.default_strategy == "camelot":
            extraction_method = content_within_bounding_box_camelot
            normalized_contour = (basic_info.image_property.width / (x - 4), basic_info.image_property.height / (y - 4), basic_info.image_property.width / (x + w), basic_info.image_property.height / (y + h))
            # normalized_contour = (basic_info.image_property.width / x, basic_info.image_property.height / y, basic_info.image_property.width / (x + w), basic_info.image_property.height / (y + h))
            # contour = (x-4, y-4, x + w, y + h)
        else:
            extraction_method = content_within_bounding_box_plumber
            # contour = (x - 5, y - 5, x + w + 10, y + h + 10)
            # normalized_contour = (basic_info.image_property.width / (x - 5), basic_info.image_property.height / (y - 5), basic_info.image_property.width / (x + w + 10), basic_info.image_property.height / (y + h + 10))
            normalized_contour = (basic_info.image_property.width / (x - 5), basic_info.image_property.height / (y - 5), basic_info.image_property.width / (x + w + 10), basic_info.image_property.height / (y + h + 10))
    elif basic_info.default_config.Extraction_settings.kind.lower() == "table":
        if basic_info.default_config.Extraction_settings.custom.Table.strategy == "camelot":
            extraction_method = content_within_bounding_box_camelot
            normalized_contour = (basic_info.image_property.width / (x - 4), basic_info.image_property.height / (y - 4), basic_info.image_property.width / (x + w), basic_info.image_property.height / (y + h))
        else:
            extraction_method = content_within_bounding_box_plumber
            normalized_contour = (basic_info.image_property.width / (x - 5), basic_info.image_property.height / (y - 5),basic_info.image_property.width / (x + w + 10),basic_info.image_property.height / (y + h + 10))
    else:
        if basic_info.default_config.Extraction_settings.custom.Paragraph.strategy == "camelot":
            extraction_method = content_within_bounding_box_camelot
            normalized_contour = (basic_info.image_property.width / (x - 4), basic_info.image_property.height / (y - 4), basic_info.image_property.width / (x + w), basic_info.image_property.height / (y + h))
        else:
            extraction_method = content_within_bounding_box_plumber
            normalized_contour = (basic_info.image_property.width / (x - 5), basic_info.image_property.height / (y - 5), basic_info.image_property.width / (x + w + 10),basic_info.image_property.height / (y + h + 10))

    for content, type in extraction_method(basic_info, normalized_contour):
        return (type , content)

"""
# changing structure to async
async def async_content_within_bounding_box_plumber(basic_info:BasicInformation, coordinates_percent):
    pdf = basic_info.pdf_property.plumber_pdf
    page = pdf.pages[int(basic_info.pdf_property.page_no) - 1]
    width , height = float(page.width) , float(page.height)
    w0, h0, w1, h1 = coordinates_percent
    coordinates = (width / w0, height / h0, width / w1,height / h1)
    # print("plumber--coordinates---->", coordinates)
    # print("plumber--height---->", height)
    # print("plumber--width---->", width)
    try:
        ROI = page.within_bbox(coordinates, relative=False)
    except:
        # print("coordinated are edited to enclose it with main page")
        # print("coordinates_original------->",coordinates)
        # coordinates = [coordinate if index in (1,2) and coordinate > 0 else float(0.0) for index,coordinate in enumerate(coordinates)]
        coordinates_changed = []
        for index ,coordinate in enumerate(coordinates):
            if index == 0 and coordinate < 0:
                coordinate = float(0.0)
            if index == 2 and float(coordinate) > float(width):
                coordinate = width
            if index == 3 and float(coordinate) > float(height):
                coordinate = height
            coordinates_changed.append(coordinate)
        ROI = page.within_bbox(coordinates_changed, relative=False)
        # print("coordinates_changed------->",coordinates_changed)
    table_custom = ROI.extract_tables(
        table_settings={"vertical_strategy": basic_info.default_config.Pdfplumber.Settings.vertical_strategy, "horizontal_strategy": basic_info.default_config.Pdfplumber.Settings.horizontal_strategy, "snap_tolerance": basic_info.default_config.Pdfplumber.Settings.snap_tolerance})
    table_normal = ROI.extract_tables()
    # print("table_custom---->", table_normal)
    # print("table_normal---->", table_custom)
    table = []
    if table_normal and table_custom:
        table_custom_shape = pd.DataFrame(table_custom[0]).shape[1]
        table_normal_shape = pd.DataFrame(table_normal[0]).shape[1]
        if table_normal_shape == table_custom_shape:
            table = table_custom
        elif table_normal_shape > table_custom_shape:
            table = table_normal
        else:
            table = table_custom
    elif table_normal and not table_custom:
        table = table_normal
    elif table_custom and not table_normal:
        table = table_custom

    if table:
        # print("table----->", table)
        # table_cleaned = [[cell for cell in row if str(cell).strip() and cell] for row in table[0]]
        table_cleaned = table[0]
        # print("table---cleaned---->", table_cleaned)
        if is_df_with_multiple_columns(table_cleaned, basic_info.default_config.Pdfplumber.Table_filter.min_columns):
            yield (table, 'table')
        else:
            content = ROI.extract_text()
            yield (content, 'content')
    else:
        content = ROI.extract_text()
        print("content_extracted---->", content)
        yield (content, 'content')

async def async_content_within_bounding_box_camelot(basic_info:BasicInformation, coordinates_percent):
    pdf = basic_info.pdf_property.plumber_pdf
    page = pdf.pages[int(basic_info.pdf_property.page_no) - 1]
    width , height = float(page.width) , float(page.height)
    w0, h0, w1, h1 = coordinates_percent
    coordinates = (width / w0, height / h0, width / w1,height / h1)
    coordinates = [coordinate if coordinate > 0 else float(0.0) for coordinate in coordinates]
    # for camelot
    coordinates_int = [int(value) for value in coordinates]
    coordinates_int = [coordinates_int[0], int(height) - coordinates_int[1], coordinates_int[2],
                       int(height) - coordinates_int[3]]
    try:
        camelot_table = camelot.read_pdf(basic_info.pdf_property.input_pdf, pages=str(basic_info.pdf_property.page_no), flavor="stream",row_tol=basic_info.default_config.Camelot.Settings.Stream.row_tol,
                                         table_areas=[f'{coordinates_int[0]},{int(coordinates_int[1])},{coordinates_int[2]},{coordinates_int[3]}'])
        print(len(camelot_table))
    except Exception as E:
        # print("error---->", E)
        # print("camelot content not available")
        yield ("", "content")
    else:
        df = camelot_table[0].df
        if is_df_with_multiple_columns(df.values.tolist(), basic_info.default_config.Camelot.Table_filter.min_columns):
            content = [df.values.tolist()]
            yield (content, "table")
        else:
            # ROI = page.within_bbox(coordinates, relative=False)
            # content = ROI.extract_text()
            # print("content_extracted---->", content)
            # yield (content, 'content')
            # content = "\n".join(df.loc[:, 0].to_list())
            content = []
            for row in list(df.index):
                content.append(" ".join([value for value in df.loc[row].tolist() if value]))
            content = "\n".join(content)
            # print("content_extracted- new---->", content)
            yield (content, "content")
        '''
        for table in camelot_table:
            df = table.df
            print(df)
            print("-----"*10)
            if is_df_with_multiple_columns(df.values.tolist()):
                content = [df.values.tolist()]
                yield (content, "table")
            else:
                content = "\n".join(df.loc[:,0].to_list())
                yield (content, "content")
        '''


async def async_extract_content_from_bounding_rect(basic_info:BasicInformation,bounding_rect):
    '''
    input -> pass single value from cv2.bounding_rect
    method should be one of ["pdfplumber","camelot"].
    output -> (type,content)
    '''
    x, y, w, h = bounding_rect
    # normalized_contour = (self.width / (x - 10), self.height / (y - 10), self.width / (x + w + 20), self.height / (y + h + 20))
    if basic_info.default_config.Extraction_settings.default_strategy == "camelot":
        extraction_method = async_content_within_bounding_box_camelot
        normalized_contour = (basic_info.image_property.width / (x - 4), basic_info.image_property.height / (y - 4), basic_info.image_property.width / (x + w), basic_info.image_property.height / (y + h))
        # normalized_contour = (basic_info.image_property.width / x, basic_info.image_property.height / y, basic_info.image_property.width / (x + w), basic_info.image_property.height / (y + h))
        # contour = (x-4, y-4, x + w, y + h)
    else:
        extraction_method = async_content_within_bounding_box_plumber
        # contour = (x - 5, y - 5, x + w + 10, y + h + 10)
        # normalized_contour = (basic_info.image_property.width / (x - 5), basic_info.image_property.height / (y - 5), basic_info.image_property.width / (x + w + 10), basic_info.image_property.height / (y + h + 10))
        normalized_contour = (basic_info.image_property.width / (x - 5), basic_info.image_property.height / (y - 5), basic_info.image_property.width / (x + w + 10), basic_info.image_property.height / (y + h + 10))

    async for content, type in extraction_method(basic_info, normalized_contour):
        await asyncio.sleep(0.75)
        return (type , content)
        """