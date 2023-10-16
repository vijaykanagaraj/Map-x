import pandas as pd
# import pdfplumber
import streamlit as st
import os
# from mapx_new import roi_region_finder
from mapx_new_config import streamlit_main , main , is_pdf , get_pages_count
import cv2
import time
from streamlit_lottie import st_lottie , st_lottie_spinner
# import requests
import pathlib
import json
from termcolor import colored
from PIL import ImageColor
import matplotlib.pyplot as plt

# temp_location = "/Users/vijaykanagaraj/PycharmProjects/mapx_image/"

@st.experimental_memo
def load_lottie(path):
    with open(f"{pathlib.Path().absolute()}{path}") as f:
        return json.load(f)

def rescale_frame(frame, percent=75):
    # width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (frame.shape[1], height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_LINEAR)

st.set_page_config(
     page_title="Map-X",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="collapsed",
 )

st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 1.5rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
               .css-1d391kg {
                    padding-top: 0rem;
                    padding-right: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                }
                .css-10xlvwk {
                    width: 15rem
                } 
        </style>
        """, unsafe_allow_html=True)



loading_widget = load_lottie(f"/static_files/auto_mode_loader.json")
manual_widget = load_lottie(f"/static_files/manual_mode_loader.json")
mapx_logo_widget = load_lottie(f"/static_files/mapx_human_robot_logo.json")
error_loader = load_lottie(f"/static_files/oh_no_robot_loader.json")
success_loader = load_lottie(f"/static_files/oh_yes_robot_loader.json")

strategy_dict = {"LATTICE":0,"STREAM":1}

if "state" not in st.session_state:
    st.session_state.state = "LATTICE"
if "check_for_nested_tables" not in st.session_state:
    st.session_state.check_for_nested_tables = False
if "h_buffer" not in st.session_state:
    st.session_state.h_buffer = 50
if "v_buffer" not in st.session_state:
    st.session_state.v_buffer = 12
if "min_area" not in st.session_state:
    st.session_state.min_area = 100
if "max_area" not in st.session_state:
    st.session_state.max_area = 25000000
if "mode" not in st.session_state:
    st.session_state.mode = "Auto"
if "kind" not in st.session_state:
    st.session_state.all = "ALL"
if "camelot_settings" not in st.session_state:
    st.session_state.camelot_settings = None
if "check_for_table_in_paragraph" not in st.session_state:
    st.session_state.check_for_table_in_paragraph = False
if "check_for_paragraph_in_table" not in st.session_state:
    st.session_state.check_for_paragraph_in_table = False
if "selected_points" not in st.session_state:
    st.session_state.selected_points = []
if "output_mode" not in st.session_state:
    st.session_state.output_mode = "json"

# main_col1, main_col2, main_col3 = st.columns([1,1.9,1])
main_col1, main_col2, main_col3 = st.columns([0.75,1.9,0.75])

with main_col1:
    # current_mode = main_col1.header("Manual")
    logo_widget = st_lottie(mapx_logo_widget,height=100,width=250)
    left_side_stack = st.empty()

with main_col2:
    middle_stack = st.empty()
    with middle_stack.container():
        tab1, tab2, tab3 = st.tabs(["Annotated", "Preprocessed", "Output"])
        with tab1:
            annotated_image = st.empty()
        with tab2:
            pre_processed_image = st.empty()
        with tab3:
            json_data = st.empty()

with main_col3:
    right_side_stack = st.empty()

def sidebar():
    with st.sidebar:
        st.session_state.mode = st.radio("MODE",('Auto','Manual'),horizontal=True)
        st.session_state.output_mode = st.radio("OUTPUT",('Table','Json'),horizontal=True)
        annotation_colour = st.color_picker(label="Annotation Colour", value="#FF8C00")
        st.session_state.annotation_colour = ImageColor.getrgb(annotation_colour)
        st.session_state.rescale_ratio = st.slider(label="Zoom Image",min_value=60, max_value=140,step=3,value=63)
        with st.expander("Stream settings"):
            with st.form("Stream setting", clear_on_submit=False):
                # camelot_strategy = st.selectbox("STRATEGY",("stream","lattice"))
                row_tol = st.slider("ROW TOLERANCE",min_value=1,max_value=30,value=10,help="maximize to combine next row in table")
                edge_tol = st.slider("EDGE TOLERANCE",min_value=100,max_value=1000,value=10,help="maximize to combine multilple tables")
                column_seperator_position = st.text_input("Column seperator positions",help="optional column location marker -> list")
                submitted = st.form_submit_button("APPLY")
                if submitted:
                    # st.session_state.camelot_strategy = camelot_strategy
                    st.session_state.row_tol = row_tol
                    st.session_state.edge_tol = edge_tol
                    st.session_state.column_seperator_position = column_seperator_position
                    st.session_state.camelot_settings = dict(row_tol = row_tol,columns= [column_seperator_position] if column_seperator_position.strip() else None,
                                                             edge_tol = edge_tol)


def on_file_remove():
    dir = f"{pathlib.Path.cwd()}/mapx_temp_storage/"
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
    return

def left_side_ui():
    with left_side_stack.container():
        # st.session_state.input_pdf = st.text_input("PDF PATH")
        input_pdf_location = f"{pathlib.Path.cwd()}/mapx_temp_storage/"
        st.session_state.input_pdf = "input_pdf.pdf"
        uploaded_file = st.file_uploader("choose a file",type=["pdf"],accept_multiple_files=False,on_change=on_file_remove)
        if uploaded_file is not None:
            with open(f"{input_pdf_location}{st.session_state.input_pdf}","wb") as input_obj:
                input_obj.write(uploaded_file.getvalue())

        try:
            if is_pdf(st.session_state.input_pdf):
                pages = [None] + list(range(1, int(get_pages_count(st.session_state.input_pdf)) + 1))
        except:
            if st.session_state.input_pdf:
                with middle_stack:
                    st_lottie(error_loader,height=500,width=500)
                st.stop()
            else:
                # with middle_stack:
                #     st_lottie(success_loader,height=500,width=500)
                st.stop()

        # try:
        #     pdf = pdfplumber.open(f"{temp_location}{st.session_state.input_pdf}")
        #     pages = [None]+list(range(1,len(pdf.pages)+1))
        # except:
        #     if st.session_state.input_pdf:
        #         with middle_stack:
        #             st_lottie(error_loader,height=500,width=500)
        #     st.stop()

        st.session_state.page_no = st.selectbox("PAGE NUMBER", pages)
        if not st.session_state.page_no:
            st.stop()

        st.session_state.kind = st.radio("TARGET DATA", ('ALL', 'PARAGRAPH', 'TABLE'),horizontal=True)
        # st.session_state.mode = st.radio("MODE",('Auto','Manual'),horizontal=True)

def right_side_ui():
    with right_side_stack.container():
        st.metric(label="", value="", delta="")  # simply For space
        st.session_state.state = st.radio("EXTRACTION STRATEGY", ('LATTICE', 'STREAM'), horizontal=True)
        # st.session_state.check_for_nested_tables = st.checkbox(label="Nested Table", value=False)
        # st.session_state.check_for_table_in_paragraph = st.checkbox(label="Table in Paragraph", value=False)
        # search_for_content = st.multiselect("Search Table inside",options=["Table","Paragraph"],default=None)
        search_for_content = st.multiselect("Deep Search",options=["Table Inside Table","Table Inside Paragraph","Paragraph Inside Table"],default=None)
        # search_for_content = st.multiselect("Deep Search",options=["Table Inside Table","Paragraph Inside Table"],default=None)
        st.session_state.h_buffer = st.slider("H-spacing", 0, 250, value=50)
        st.session_state.v_buffer = st.slider("V-spacing", 0, 100, value=12)
        # st.session_state.min_area = st.slider("Min Area", 1, 25000000, value=100)
        # st.session_state.max_area = st.slider("Max Area", 1, 25000000, value=25000000)
        st.session_state.min_area = st.number_input("Min Area",min_value=1,max_value=25000000,value=100,step=100000)
        st.session_state.max_area = st.number_input("Max Area",min_value=1,max_value=25000000,value=25000000,step=1000000)
        if "Table Inside Table" in search_for_content:
            st.session_state.check_for_nested_tables = True
        else:
            st.session_state.check_for_nested_tables = False
        if "Table Inside Paragraph" in search_for_content:
            st.session_state.check_for_table_in_paragraph = True
        else:
            st.session_state.check_for_table_in_paragraph = False
        if "Paragraph Inside Table" in search_for_content:
            st.session_state.check_for_paragraph_in_table = True
        else:
            st.session_state.check_for_paragraph_in_table = False


        if int(st.session_state.min_area) > int(st.session_state.max_area):
            st.warning("Min area should be less than max area")

def reset_value():
    st.session_state.state = "LATTICE"
    st.session_state.check_for_nested_tables = False
    st.session_state.h_buffer = 50
    st.session_state.v_buffer = 12
    st.session_state.min_area = 100
    st.session_state.max_area = 25000000

def middle_stack_ui():
    # if st.session_state.kind == "TABLE":
    selected_points = st.text_input(label="select points to filter")
    if selected_points.strip():
        st.session_state.selected_points = selected_points.split(",")
    else:
        st.session_state.selected_points = []
    # else:
        # st.session_state.selected_points = st.multiselect(label="select points to filter",options=final_json["paragraph"]["content"].keys())
    # button = st.button(label="Apply")
    # if button:
    with annotated_image.container():
        with st_lottie_spinner(loading_widget,height=500,width=500):
            print(colored(st.session_state.selected_points,"red"))
            start_time = time.perf_counter()
            extraction_settings = dict(horizontal_buffer=st.session_state.h_buffer,vertical_buffer=st.session_state.v_buffer, area_filter=(int(st.session_state.min_area), int(st.session_state.max_area)), kind=st.session_state.kind, default_strategy= "pdfplumber" if st.session_state.state == "LATTICE" else "camelot" ,check_for_table_in_paragraph = st.session_state.check_for_table_in_paragraph,
                                        check_for_nested_tables=st.session_state.check_for_nested_tables,mode=st.session_state.mode,check_for_paragraph_in_table=st.session_state.check_for_paragraph_in_table)
            filter_settings = dict(selected_points = st.session_state.selected_points)
            Images, final_json = main(input_pdf=st.session_state.input_pdf, page=st.session_state.page_no, filter_settings=filter_settings, annotation_colour=st.session_state.annotation_colour,
                                                camelot_settings=st.session_state.camelot_settings,extraction_settings=extraction_settings)

    # annotated_image.image(rescale_frame(Images[0], st.session_state.rescale_ratio), caption=["Annotated Image"])
    # pre_processed_image.image(rescale_frame(Images[1], st.session_state.rescale_ratio), caption=["Preprocessed Image"])

    # st.write(st.session_state.selected_points)
    tabs = [annotated_image,pre_processed_image]
    tabs_caption = ["Annotated Image","Preprocessed Image"]
    for index,image in enumerate(Images):
        tabs[index].image(rescale_frame(Images[index], st.session_state.rescale_ratio), caption=[tabs_caption[index]])
        # tabs[index].pyplot(fig=plt.plot(rescale_frame(Images[index], st.session_state.rescale_ratio).transpose(2,0,1).reshape(3,-1)),clear_figure=True)
        # fig = plt.figure()
        # tabs[index].pyplot(fig=fig,clear_figure=True)
    if st.session_state.output_mode.lower() == "json":
        json_data.json(final_json, expanded=False)
    else:
        with json_data.container():
            if final_json:
                for key , bucket in final_json.items():
                    if key.lower() == "table":
                        st.write(key.upper())
                        for table_key, table in final_json[key]["content"].items():
                            st.write(table_key)
                            st.dataframe(data=table)
                    else:
                        _temp_dict = {}
                        for para_key, value in final_json[key]["content"].items():
                            _temp_dict[para_key] = [value]
                        st.write(key.upper())
                        st.dataframe(pd.DataFrame.from_dict(_temp_dict).T)

    # adding time bar
    with main_col1:
        empty_box = st.empty()
        with empty_box.container():
            time_taken = "{:.2f}".format(time.perf_counter() - start_time)
            st.metric(label="", value=time_taken, delta="Sec")

if __name__ == "__main__":
    sidebar()
    left_side_ui()
    if st.session_state.mode == "Manual":
        right_side_ui()
    else:
        reset_value()
    middle_stack_ui()

