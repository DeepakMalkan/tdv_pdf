import os.path
import apsw
import deal_page as DealPage
import company_data as CompanyData

class DealsSection ():
    """A class that holds data associated with a section of pages - such as Priority Deals, New Deals, Other Deals, etc."""

    PRIORITY_DEALS_TYPE = "Priority_Deals"
    NEW_DEALS_TYPE = "New_Deals"
    OTHER_DEALS_TYPE = "Other_Deals"
    ACTIVATE_POTENTIAL_TYPE = "Activate_Potential"
    COMMERCIAL_PARTNERSHIPS_TYPE = "Commercial_Partnerships"
    PASS_TRACK_DEALS_TYPE = "Pass_Track_Deals"

    DEALS_LIST = [PRIORITY_DEALS_TYPE, NEW_DEALS_TYPE, OTHER_DEALS_TYPE, ACTIVATE_POTENTIAL_TYPE, COMMERCIAL_PARTNERSHIPS_TYPE, PASS_TRACK_DEALS_TYPE]

    def __init__(self, deal_type) -> None:
        self.deal_type = deal_type
        self.first_page = 0
        self.number_of_pages = 0
        self.page_list = []
        self.deal_page_list = []

    def save (self, connection, table_name, file_key):
        if self.number_of_pages > 0:
            page_list_str = " ".join (str (x) for x in self.page_list)
            query = f"insert into {table_name} values({file_key}, '{self.deal_type}', {self.number_of_pages}, '{page_list_str}')"
            connection.execute (query)

    def print (self):
        print (f"Number of {self.deal_type} Pages = {self.number_of_pages}")
        print (f"{self.deal_type} Pages = {self.page_list}")

    def check_data (self):
        assert (self.number_of_pages == len (self.page_list))

    @classmethod
    def CreatePriorityDealsSection (cls):
        return DealsSection (cls.PRIORITY_DEALS_TYPE)

    @classmethod
    def CreateNewDealsSection (cls):
        return DealsSection (cls.NEW_DEALS_TYPE)

    @classmethod
    def CreateOtherDealsSection (cls):
        return DealsSection (cls.OTHER_DEALS_TYPE)

    @classmethod
    def CreateActivatePotentialSection (cls):
        return DealsSection (cls.ACTIVATE_POTENTIAL_TYPE)

    @classmethod
    def CreateCommercialPartnershipsSection (cls):
        return DealsSection (cls.COMMERCIAL_PARTNERSHIPS_TYPE)

    @classmethod
    def CreatePassTrackDealsSection (cls):
        return DealsSection (cls.PASS_TRACK_DEALS_TYPE)
