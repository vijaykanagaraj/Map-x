"""Mapx framework to map pdf contents to unique keys similiar to Excel"""

__version__ = "1.0.0"

from .contour_operations import *

from .data_extraction import *

from .extract_and_tag import *

from .unique_key_decode import *

from .pre_processing import *

from .property import PdfProperty , ImageProperty , GlobalContentHolder , BasicInformation , ExtractionSettings

from .visual_debug import visual_debug
