import time
import datetime
from pypdf import PdfReader
from pathlib import Path
from pypdf import PdfReader
from sqlite_processor import SqliteProcessor

class PdfProcessorPhase1 ():
    """A class that processes the first phase of the Pdf data"""
    def __init__ (self, path):
        super ().__init__ ()

        self.PRIORITY_ACTIVE_DEALS1 = "Priority Active Deals (1"
        self.ACTIVE_DEALS1 = "Active Deals (1"
        self.NEW_ACTIVE_DEALS1 = "New Active Deals (1"

        self.path = path
        self.basepath = ""
        self.reader = PdfReader (path)

        self.author = ""
        self.creator = ""
        self.producer = ""
        self.subject = ""
        self.title = ""
        self.number_of_pages = 0
        self.priority_deals_first_page = 0
        self.priority_deals_number_of_pages = 0
        self.priority_deals_page_list = []
        self.new_deals_first_page = 0
        self.new_deals_number_of_pages = 0
        self.new_deals_page_list = []

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

    def extract_deals_pages (self):
        time_start = time.perf_counter ()

        for page_number in self.page_text_dict:
            page_text = self.page_text_dict[page_number]
            if (self.priority_deals_first_page == 0):
                if self.PRIORITY_ACTIVE_DEALS1 in page_text or self.ACTIVE_DEALS1 in page_text:
                    self.priority_deals_first_page = page_number
                    start_index_position = page_text.find (self.PRIORITY_ACTIVE_DEALS1)
                    if start_index_position == -1:
                        start_index_position = page_text.find (self.ACTIVE_DEALS1)

                    open_bracket_position = page_text.find ('(', start_index_position)
                    close_bracket_position = page_text.find (')', open_bracket_position)

                    self.priority_deals_number_of_pages = int (page_text[open_bracket_position + 6:close_bracket_position])
                    self.priority_deals_page_list.append (page_number)
            else:
                search_page = len (self.priority_deals_page_list) + 1
                search_text = f"{search_page} of {self.priority_deals_number_of_pages}"
                if (search_text in page_text):
                    self.priority_deals_page_list.append (page_number)

            if (self.new_deals_first_page == 0):
                if self.NEW_ACTIVE_DEALS1 in page_text:
                    self.new_deals_first_page = page_number
                    start_index_position = page_text.find (self.NEW_ACTIVE_DEALS1)

                    open_bracket_position = page_text.find ('(', start_index_position)
                    close_bracket_position = page_text.find (')', open_bracket_position)

                    self.new_deals_number_of_pages = int (page_text[open_bracket_position + 6:close_bracket_position])
                    self.new_deals_page_list.append (page_number)
            else:
                search_page = len (self.new_deals_page_list) + 1
                search_text = f"{search_page} of {self.new_deals_number_of_pages}"
                if (search_text in page_text):
                    self.new_deals_page_list.append (page_number)

        time_end = time.perf_counter ()
        print (f"Extracted deal pages in {time_end - time_start:0.4f} seconds")

    def save (self):
        sqlite_processor = SqliteProcessor ()
        sqlite_processor.savePhase1 (self.yymmdd_date, self.basepath, self.number_of_pages, self.priority_deals_number_of_pages, self.priority_deals_page_list, self.new_deals_number_of_pages, self.new_deals_page_list)

    def print_info (self):
        print (f"Path = {self.path}")
        print (f"Base Path = {self.basepath}")
        print (f"File Date = {self.yymmdd_date}")
        print (f"Author = {self.author}")
        print (f"Creator = {self.creator}")
        print (f"Subject = {self.subject}")
        print (f"Title = {self.title}")
        print (f"Number of Pages = {self.number_of_pages}")
        print (f"Number of Priority Deal Pages = {self.priority_deals_number_of_pages}")
        print (f"Priority Deal Pages = {self.priority_deals_page_list}")
        print (f"Number of New Deal Pages = {self.new_deals_number_of_pages}")
        print (f"New Deal Pages = {self.new_deals_page_list}")

    def process (self):
        self.extract_date_from_path ()

        self.extract_information ()
        self.extract_page_text ()
        self.extract_deals_pages ()

        self.save ()

        self.print_info ()