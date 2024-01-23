import time
import datetime
from pypdf import PdfReader
from pathlib import Path
from pypdf import PdfReader
from sqlite_processor import Phase1Db
from sqlite_processor import Phase1PdfData
from sqlite_processor import DealsSection

class PdfProcessorPhase1 ():
    """A class that processes the first phase of the Pdf data"""
    """In this phase we identify all pages associated with Priority Active / Active / Other Active Deals"""
    """The pages thus identified are stored in an sqlite db file"""

    def __init__ (self, path) -> None:
        super ().__init__ ()

        self.PRIORITY_ACTIVE_DEALS1 = "Priority Active Deals (1"
        self.ACTIVE_DEALS1 = "Active Deals (1"
        self.NEW_ACTIVE_DEALS1 = "New Active Deals (1"
        self.OTHER_ACTIVE_DEALS1 = "Other Active Deals (1"
        self.ACTIVATE_COMPANIES1 = "Current iTwin Activate Companies (1"
        self.COMMERCIAL_PARTNERSHIP = "Commercial Partnership Opportunities (1"
        self.PASS_TRACK_DEALS1 = "Pass/ Track Deals (1"

        self.path = path
        self.basepath = ""
        self.reader = PdfReader (path)

        self.author = ""
        self.creator = ""
        self.producer = ""
        self.subject = ""
        self.title = ""
        self.number_of_pages = 0
        self.priority_deals = DealsSection ("Priority Deal")
        self.new_deals = DealsSection ("New Deal")
        self.other_deals = DealsSection ("Other Deal")
        self.activate_potential = DealsSection ("Activate Potential")
        self.commercial_partnership = DealsSection ("Commercial Partnership")
        self.pass_track_deals = DealsSection ("Pass Track Deal")

        self.page_text_dict = {}

    def extract_date_from_path (self):
        '''The path file-name contains a date that we need to extract for provenance purposes'''
        '''For example, the path's file name is for the format: "Bentley Biweekly 011222 vF.pdf". We need to extract 011222 in format mmddyy'''
        splitpath = self.path.rsplit ("/", 1)
        self.basepath = splitpath[1]
        extracted_date = self.basepath[17:23]
        self.yymmdd_date = extracted_date[4:6]+extracted_date[0:2]+extracted_date[2:4]

    def extract_information (self):
        metadata = self.reader.metadata

        self.author = metadata.author
        self.creator = metadata.creator
        self.subject = metadata.subject
        self.title = metadata.title
        self.number_of_pages = len (self.reader.pages)

    def extract_page_text (self):
        time_start = time.perf_counter ()

        page_number = 1
        for page in self.reader.pages:
            text = page.extract_text ()
            self.page_text_dict[page_number] = text

            page_number += 1

        time_end = time.perf_counter ()
        print (f"Extracted page text in {time_end - time_start:0.4f} seconds")

    def process_for_deals_section (self, deals_section, check_text, page_text, page_number):
        if (deals_section.first_page == 0):
            if check_text in page_text:
                deals_section.first_page = page_number
                start_index_position = page_text.find (check_text)

                open_bracket_position = page_text.find ('(', start_index_position)
                close_bracket_position = page_text.find (')', open_bracket_position)

                deals_section.number_of_pages = int (page_text[open_bracket_position + 6:close_bracket_position])
                deals_section.page_list.append (page_number)
        else:
            search_page = len (deals_section.page_list) + 1
            search_text = f"{search_page} of {deals_section.number_of_pages}"
            if self.text_in_page (search_text, page_text):
                deals_section.page_list.append (page_number)

    def process_for_deals_section_2 (self, deals_section, check_text1, check_text2, page_text, page_number):
        processed = False
        if (deals_section.first_page == 0):
            if check_text1 in page_text or check_text2 in page_text:
                deals_section.first_page = page_number
                start_index_position = page_text.find (check_text1)
                if start_index_position == -1:
                    start_index_position = page_text.find (check_text2)

                open_bracket_position = page_text.find ('(', start_index_position)
                close_bracket_position = page_text.find (')', open_bracket_position)

                deals_section.number_of_pages = int (page_text[open_bracket_position + 6:close_bracket_position])
                deals_section.page_list.append (page_number)
                processed = True
        else:
            search_page = len (deals_section.page_list) + 1
            search_text = f"{search_page} of {deals_section.number_of_pages}"
            if self.text_in_page (search_text, page_text):
                deals_section.page_list.append (page_number)
                processed = True
        return processed


    def text_in_page (self, search_text, page_text):
        if (search_text in page_text):
            return True
        # Check search_text without blank space also. In certain cases, the page_text's matching string is without blank spaces.
        search_text = search_text.replace (" ", "")
        if (search_text in page_text):
            return True
        return False

    def extract_deals_pages (self):
        time_start = time.perf_counter ()

        for page_number in self.page_text_dict:
            page_text = self.page_text_dict[page_number]
            processed = self.process_for_deals_section_2 (self.priority_deals, self.PRIORITY_ACTIVE_DEALS1, self.ACTIVE_DEALS1, page_text, page_number)
            if False == processed:
                self.process_for_deals_section (self.new_deals, self.NEW_ACTIVE_DEALS1, page_text, page_number)
            if False == processed:
                self.process_for_deals_section (self.other_deals, self.OTHER_ACTIVE_DEALS1, page_text, page_number)
            if False == processed:
                self.process_for_deals_section (self.activate_potential, self.ACTIVATE_COMPANIES1, page_text, page_number)
            if False == processed:
                self.process_for_deals_section (self.commercial_partnership, self.COMMERCIAL_PARTNERSHIP, page_text, page_number)
            if False == processed:
                self.process_for_deals_section (self.pass_track_deals, self.PASS_TRACK_DEALS1, page_text, page_number)

        time_end = time.perf_counter ()
        print (f"Extracted deal pages in {time_end - time_start:0.4f} seconds")

    def check_data (self):
        self.priority_deals.check_data ()
        self.new_deals.check_data ()
        self.other_deals.check_data ()
        self.activate_potential.check_data ()
        self.commercial_partnership.check_data ()
        self.pass_track_deals.check_data ()

    def save (self):
        phase1_db = Phase1Db ()
        phase1_pdf_data = Phase1PdfData (self.yymmdd_date, self.basepath, self.number_of_pages, self.priority_deals, self.new_deals, self.other_deals, self.activate_potential, self.commercial_partnership, self.pass_track_deals)
        phase1_db.save (phase1_pdf_data)

    def print_info (self):
        print (f"Path = {self.path}")
        print (f"Base Path = {self.basepath}")
        print (f"File Date = {self.yymmdd_date}")
        print (f"Author = {self.author}")
        print (f"Creator = {self.creator}")
        print (f"Subject = {self.subject}")
        print (f"Title = {self.title}")
        print (f"Number of Pages = {self.number_of_pages}")
        self.priority_deals.print ()
        self.new_deals.print ()
        self.other_deals.print ()
        self.activate_potential.print ()
        self.commercial_partnership.print ()
        self.pass_track_deals.print ()

    def process (self):
        self.extract_date_from_path ()

        self.extract_information ()
        self.extract_page_text ()
        self.extract_deals_pages ()

        self.check_data ()
        self.save ()

        self.print_info ()