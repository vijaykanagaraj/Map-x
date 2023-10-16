class UniqueKeyDecoder:
    def __init__(self,key):
        self.__key = key

    @property
    def identifier(self):
        '''gives information ---> whether this key is for table (T)  or paragrapg content (P)'''
        value = self.__key.split("-")[0]
        return value

    @property
    def page_no(self):
        '''gives information about in which page number the corresponding information os present'''
        value = self.__key.split("-")[1]
        return value.split("#")[0]

    @property
    def id(self):
        '''prodides sequence number of the content based on buffer value adjustments'''
        value = self.__key.split("-")[1]
        return value.split("#")[-1].lower().strip("c")

    @property
    def is_child(self):
        value = self.__key.split("-")[1]
        if "c" in value.split("#")[-1].lower():
            return True
        else:
            return False

    @property
    def location_tagger(self):
        '''provides location information of the content'''
        if len(self.__key.split("-")) == 3:
            value = self.__key.split("-")[-1]
            return list(map(lambda x: int(x), value.split("#")))
        elif len(self.__key.split("-")) == 4:
            value = self.__key.split("-")[-2]
            return list(map(lambda x: int(x), value.split("#")))

    @property
    def table_cell(self):
        '''provides location information of the content'''
        if len(self.__key.split("-")) == 4:
            value = self.__key.split("-")[-1]
            return list(map(lambda x: int(x),value.split("#")))
        else:
            return []
