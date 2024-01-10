import tabula
import json
import time
from pypdf import PdfReader
from pathlib import Path
from pypdf import PdfReader

class PdfInfo ():
    """A class that holds key information about the pdf file"""

    def __init__ (self):
        super ().__init__ ()

        self.author = ""
        self.creator = ""
        self.producer = ""
        self.subject = ""
        self.title = ""
        self.number_of_pages = 0
        self.priority_active_deals_start = 0
        self.priority_active_deals_end = 0
        self.other_active_deals_start = 0
        self.other_active_deals_end = 0

    def extract_information (self, reader):
        metadata = reader.metadata

        self.author = metadata.author
        self.creator = metadata.creator
        self.subject = metadata.subject
        self.title = metadata.title
        self.number_of_pages = len (reader.pages)

    def extract_sections (self, reader):
        time_start = time.perf_counter ()

        priority_active_deals = "Priority Active Deals"
        other_active_deals = "Other Active Deals"
        commercial_partnership = "Commercial Partnership Opportunities"

        page_number = 1
        for page in reader.pages:
            text = page.extract_text ()
            if text == priority_active_deals:
                self.priority_active_deals_start = page_number
            elif text == other_active_deals:
                self.priority_active_deals_end = page_number
                self.other_active_deals_start = page_number
            elif self.other_active_deals_start > 0 & self.other_active_deals_end == 0:
                if commercial_partnership in text:
                    self.other_active_deals_end = page_number

            page_number += 1

        time_end = time.perf_counter ()
        print (f"Extracted sections in {time_end - time_start:0.4f} seconds")

    def print_info (self):
        print (f"Author = {self.author}")
        print (f"Creator = {self.creator}")
        print (f"Subject = {self.subject}")
        print (f"Title = {self.title}")
        print (f"Number of Pages = {self.number_of_pages}")
        print (f"Priority Active Deals: {self.priority_active_deals_start},{self.priority_active_deals_end}")
        print (f"Other Active Deals: {self.other_active_deals_start},{self.other_active_deals_end}")

class PriorityActiveDeals ():
    """A class that holds data on Priority Active Deals"""
    def __init__ (self):
        super ().__init__ ()

        self.start_page = 0
        self.end_page = 0
        self.prefix = "PAD"
        self.data_frame_dict = {}

    def extract_data_frame (self, pdfProcessor):
        self.data_frame_dict = pdfProcessor.extract_data_frame_for_pages (self.prefix, self.start_page, self.end_page)

    def write_data_frame (self, pdfProcessor):
        basepath = pdfProcessor.path.rsplit ("/", 1)

        for key in self.data_frame_dict:
            outputfile = f"{basepath[0]}/json/{key}.json"
            with open (outputfile, "w") as text_file:
                data_frame = self.data_frame_dict[key]
                text_file.write (json.dumps (data_frame[0]))

    def extract_key_strings (self):
        for key in self.data_frame_dict:
            data_frame = self.data_frame_dict[key]
            data_dict = data_frame[0]

            overall_data_list = data_dict["data"]
            print (f"Length of overall_data_list = {len(overall_data_list)}")

            page_title_dict = overall_data_list[0][0]
            page_title = page_title_dict["text"]
            print (f"Page Title = {page_title}")

            #company_title_dict = overall_data_list[1][0]
            #company_title = company_title_dict["text"]
            #print (f"Company Title = {company_title}")

            company_dict = overall_data_list[2][0]
            company_details = company_dict["text"].partition ("\r")
            print (f"Company Name = {company_details[0]}")

            team_etc_list = overall_data_list[3]
            for dict_item in team_etc_list:
                title_text = dict_item["text"].partition ("\r")
                if len (title_text) <= 0:
                    continue;

                if title_text[0] == "Team":
                    print (f"Team Title = {title_text[0]}")
                elif title_text[0] == "Technology":
                    print (f"Technology Title = {title_text[0]}")
                elif title_text[0] == "Market & Execution":
                    print (f"Martet & Execution Title = {title_text[0]}")
                elif title_text[0] == "Strategic Synergies":
                    print (f"Stratigic Synergies Title = {title_text[0]}")

            if len (overall_data_list) < 8:
                continue

            company_dict = overall_data_list[4][0]
            company_details = company_dict["text"].partition ("\r")
            print (f"Company Name 2 = {company_details[0]}")

            team_etc_list = overall_data_list[5]
            for dict_item in team_etc_list:
                title_text = dict_item["text"].partition ("\r")
                if len (title_text) <= 0:
                    continue;

                if title_text[0] == "Team":
                    print (f"Team Title = {title_text[0]}")
                elif title_text[0] == "Technology":
                    print (f"Technology Title = {title_text[0]}")
                elif title_text[0] == "Market & Execution":
                    print (f"Martet & Execution Title = {title_text[0]}")
                elif title_text[0] == "Strategic Synergies":
                    print (f"Stratigic Synergies Title = {title_text[0]}")

class PdfProcessor ():
    """A class that processes the Pdf data"""
    def __init__ (self, path):
        super ().__init__ ()

        self.path = path
        self.reader = PdfReader (path)

        self.pdf_info = PdfInfo ()
        self.priority_active_deals = PriorityActiveDeals ()

    def extract_information (self):
        self.pdf_info.extract_information (self.reader)

    def extract_sections (self):
        self.pdf_info.extract_sections (self.reader)
        self.priority_active_deals.start_page = self.pdf_info.priority_active_deals_start
        self.priority_active_deals.end_page = self.pdf_info.priority_active_deals_end

    def print_info (self):
        self.pdf_info.print_info ()

    def extract_data_frame_for_pages (self, prefix, start, end):
        basename = Path (self.path).stem

        page_json_dict = {}
        for page_number in range (start + 1, end):
            page_data_frame = tabula.read_pdf (path, lattice=True, pages=page_number, output_format="json")

            key = f"{basename}_{prefix}_{page_number}"
            page_json_dict[key] = page_data_frame

        return page_json_dict

    def write_priority_active_deals_data (self):
        self.priority_active_deals.write_data_frame (self)

    def extract_priority_active_deals_data (self):
        self.priority_active_deals.extract_data_frame (self)

if __name__ == '__main__':
#    path = 'C:\Users\Deepak.Malkan\OneDrive - Bentley Systems, Inc\Documents\iTwin Ventures\Biweekly\Bentley Biweekly 121323 vF.pdf'
    path = 'D:/Deepak/source/learn-python/tdv_pdf/test2.pdf'

    pdf_processor = PdfProcessor (path)
    pdf_processor.extract_information ()
    pdf_processor.extract_sections ()

    pdf_processor.print_info ()

    pdf_processor.extract_priority_active_deals_data ()
    pdf_processor.write_priority_active_deals_data ()
    pdf_processor.priority_active_deals.extract_key_strings ()
