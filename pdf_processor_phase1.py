import time
import datetime
import re
from extract_blocks import PdfBlockGenerator
from pypdf import PdfReader
from pathlib import Path
from pypdf import PdfReader
from sqlite_processor import Phase1Db
from sqlite_processor import Phase1PdfData
from sqlite_processor import DealsSection

class PdfProcessorPhase1 ():
    """A class that processes the first phase of the data of a single PDF file"""
    """In this phase we identify all pages associated with Priority Active / Active / Other Active Deals / etc. """
    """The pages thus identified are stored in an sqlite db file"""

    PRIORITY_ACTIVE_DEALS1 = "Priority Active Deals (1"
    ACTIVE_DEALS1 = "Active Deals (1"
    NEW_ACTIVE_DEALS1 = "New Active Deals (1"
    OTHER_ACTIVE_DEALS1 = "Other Active Deals (1"
    CURRENT_ACTIVATE_COMPANIES1 = "Current iTwin Activate Companies (1"
    ACTIVATE_COMPANIES1 = "iTwin Activate Companies (1"
    COMMERCIAL_PARTNERSHIP = "Commercial Partnership Opportunities (1"
    PASS_TRACK_DEALS1 = "Pass/ Track Deals (1"

    def __init__ (self, path) -> None:
        super ().__init__ ()

        self.path = path
        self.basepath, self.file_key = Phase1Db.generate_basepath_and_file_key (self.path)

        self.reader = PdfReader (path)

        metadata = self.reader.metadata
        self.author = metadata.author
        self.creator = metadata.creator
        self.subject = metadata.subject
        self.title = metadata.title
        self.number_of_pages = len (self.reader.pages)

        self.priority_deals = DealsSection.CreatePriorityDealsSection ()
        self.new_deals = DealsSection.CreateNewDealsSection ()
        self.other_deals = DealsSection.CreateOtherDealsSection ()
        self.activate_potential = DealsSection.CreateActivatePotentialSection ()
        self.commercial_partnership = DealsSection.CreateCommercialPartnershipsSection ()
        self.pass_track_deals = DealsSection.CreatePassTrackDealsSection ()
        self.deals_section_list = [self.priority_deals, self.new_deals, self.other_deals, self.activate_potential, self.commercial_partnership, self.pass_track_deals]

        self.page_text_dict = {}

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
        processed = False
        if (deals_section.first_page == 0):
            if check_text in page_text:
                deals_section.first_page = page_number
                start_index_position = page_text.find (check_text)

                open_bracket_position = page_text.find ('(', start_index_position)
                of_position = page_text.find ('of', start_index_position)
                close_bracket_position = page_text.find (')', open_bracket_position)

                deals_section.number_of_pages = int (page_text[of_position + 2:close_bracket_position])
                deals_section.page_list.append (page_number)
                processed = True
        elif deals_section.number_of_pages > len (deals_section.page_list):
            search_page = len (deals_section.page_list) + 1
            search_text = f"{search_page}[ ]*of[ ]*{deals_section.number_of_pages}"

            if re.search (search_text, page_text):
                deals_section.page_list.append (page_number)
                processed = True
        return processed

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

        activate_potential_processed = False
        for page_number in self.page_text_dict:
            page_text = self.page_text_dict[page_number]
            processed = self.process_for_deals_section (self.priority_deals, PdfProcessorPhase1.PRIORITY_ACTIVE_DEALS1, page_text, page_number)
            if False == processed:
                processed = self.process_for_deals_section (self.new_deals, PdfProcessorPhase1.NEW_ACTIVE_DEALS1, page_text, page_number)
            if False == processed:
                processed = self.process_for_deals_section (self.other_deals, PdfProcessorPhase1.OTHER_ACTIVE_DEALS1, page_text, page_number)
            if False == processed: # if not PRIORITY, NEW, or OTHER, but just ACTIVE_DEAL then process as a Priority Deal
                processed = self.process_for_deals_section (self.priority_deals, PdfProcessorPhase1.ACTIVE_DEALS1, page_text, page_number)
            if False == processed:
                processed = self.process_for_deals_section (self.activate_potential, PdfProcessorPhase1.CURRENT_ACTIVATE_COMPANIES1, page_text, page_number)
                if processed:
                    activate_potential_processed = True
            if False == processed:
                processed = self.process_for_deals_section (self.commercial_partnership, PdfProcessorPhase1.COMMERCIAL_PARTNERSHIP, page_text, page_number)
            if False == processed:
                processed = self.process_for_deals_section (self.pass_track_deals, PdfProcessorPhase1.PASS_TRACK_DEALS1, page_text, page_number)

        # if Activate Potential Pages not found with CURRENT_ACTIVATE_COMPANIES1 token, then try to find with ACTIVATE_COMPANIES1 token
        if activate_potential_processed == False:
            for page_number in self.page_text_dict:
                page_text = self.page_text_dict[page_number]
                self.process_for_deals_section (self.activate_potential, PdfProcessorPhase1.ACTIVATE_COMPANIES1, page_text, page_number)

        time_end = time.perf_counter ()
        print (f"Extracted deal pages in {time_end - time_start:0.4f} seconds")

    def check_data (self):
        for deals_section in self.deals_section_list:
            deals_section.check_data ()

    def save (self):
        phase1_db = Phase1Db ()
        phase1_pdf_data = Phase1PdfData (self.file_key, self.basepath, self.number_of_pages, self.deals_section_list)
        phase1_db.save (phase1_pdf_data)

    def extract_blocks (self):
        if self.file_key <= '220706':
            priority_expected_factor = 3
        else:
            priority_expected_factor = 7

        out_path ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata"
        block_generator = PdfBlockGenerator ()
        if self.priority_deals.number_of_pages > 0:
            out_file = f"{out_path}/priority_{self.basepath}"
            block_generator.generate_blocks_for_pages (self.path, f"{self.basepath}:Priority", self.priority_deals.page_list, out_file, priority_expected_factor)
        if self.new_deals.number_of_pages > 0:
            out_file = f"{out_path}/new_{self.basepath}"
            block_generator.generate_blocks_for_pages (self.path, f"{self.basepath}:New", self.new_deals.page_list, out_file, priority_expected_factor)
        if self.other_deals.number_of_pages > 0:
            out_file = f"{out_path}/other_{self.basepath}"
            block_generator.generate_blocks_for_pages (self.path, f"{self.basepath}:Other", self.other_deals.page_list, out_file, priority_expected_factor)
        if self.activate_potential.number_of_pages > 0:
            out_file = f"{out_path}/activate_{self.basepath}"
            block_generator.generate_blocks_for_pages (self.path, f"{self.basepath}:Activate", self.activate_potential.page_list, out_file, 3)
        if self.commercial_partnership.number_of_pages > 0:
            out_file = f"{out_path}/commercial_{self.basepath}"
            block_generator.generate_blocks_for_pages (self.path, f"{self.basepath}:Commercial", self.commercial_partnership.page_list, out_file, 3)
        if self.pass_track_deals.number_of_pages > 0:
            out_file = f"{out_path}/pass_track_{self.basepath}"
            block_generator.generate_blocks_for_pages (self.path, f"{self.basepath}:Pass_Track", self.pass_track_deals.page_list, out_file, 3)

    def print_info (self):
        print (f"Path = {self.path}")
        print (f"Base Path = {self.basepath}")
        print (f"File Key = {self.file_key}")
        print (f"Author = {self.author}")
        print (f"Creator = {self.creator}")
        print (f"Subject = {self.subject}")
        print (f"Title = {self.title}")
        print (f"Number of Pages = {self.number_of_pages}")
        for deals_section in self.deals_section_list:
            deals_section.print ()

    def process (self):
        self.extract_page_text ()
        self.extract_deals_pages ()
        self.extract_blocks ()

        self.save ()

        self.check_data ()
        # self.print_info ()
