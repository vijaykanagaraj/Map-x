from dataclasses import dataclass

@dataclass
class path:
    location_to_save:str

@dataclass
class area_filter:
    min: int
    max: int

@dataclass
class custom:
    strategy: str
    area_filter: tuple

@dataclass
class custom_mode:
    All: custom
    Paragraph: custom
    Table: custom
    Nested_table: custom
    # Table_in_paragtaph: custom


@dataclass
class extraction_settings:
    horizontal_buffer: int
    vertical_buffer: int
    area_filter: area_filter
    kind: str
    mode: str
    default_strategy: str
    custom: custom_mode
    check_for_nested_tables: bool
    check_for_table_in_paragraph: bool
    check_for_paragraph_in_table: bool

@dataclass
class settings:
    Settings: dict
    Annotation_buffer: dict
    Table_filter: dict

@dataclass
class display_settings:
    annotation_colour: tuple  # orange
    annotation_thickness: int
    text_colour: tuple  # green
    text_thickness: [float,int]
    mask_colour: tuple

@dataclass
class kernel_settings:
    kernel: tuple
    iterations: int

@dataclass
class table_line_detection:
    Horizontal: kernel_settings
    Vertical: kernel_settings

@dataclass
class para_line_detection:
    horizontal: int
    vertical: int

@dataclass
class table_settings:
    Line_detection_kernel: table_line_detection
    Dilate: kernel_settings
    Erode: kernel_settings

@dataclass
class paragraph_settings:
    Gaussian: kernel_settings
    Buffer: para_line_detection

@dataclass
class Image_processing:
    Table_preprocessing: table_settings
    Paragraph_preprocessing: paragraph_settings

@dataclass
class default_config:
    Path: path
    Extraction_settings: extraction_settings
    Camelot: settings
    Pdfplumber: settings
    Display_settings: display_settings
    Image_preprocessing: Image_processing

