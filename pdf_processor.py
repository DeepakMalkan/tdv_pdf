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

class PdfProcessor ():
    """A class that processes the Pdf data"""

    def __init__ (self, path):
        super ().__init__ ()

        self.path = path
        self.reader = PdfReader (path)

        self.pdf_info = PdfInfo ()
        self.priority_active_deals_prefix = "PAD"
        self.priority_active_deals_json_dict = {}

    def extract_information (self):
        self.pdf_info.extract_information (self.reader)

    def extract_sections (self):
        self.pdf_info.extract_sections (self.reader)

    def print_info (self):
        self.pdf_info.print_info ()

    def extract_json_text_for_pages (self, prefix, start, end):
        basename = Path (self.path).stem

        page_json_dict = {}
        for page_number in range (start + 1, end):
            page_data_frame = tabula.read_pdf (path, lattice=True, pages=page_number, output_format="json")

            key = f"{basename}_{prefix}_{page_number}"
            page_json_dict[key] = json.dumps (page_data_frame[0])

        return page_json_dict

    def write_priority_active_deals_json_data (self):
        basepath = self.path.rsplit ("/", 1)

        for key in self.priority_active_deals_json_dict:
            outputfile = f"{basepath[0]}/json/{key}.json"
            with open (outputfile, "w") as text_file:
                text_file.write (self.priority_active_deals_json_dict[key])

    def extract_priority_active_deals_text (self):
        self.priority_active_deals_json_dict = self.extract_json_text_for_pages (self.priority_active_deals_prefix, self.pdf_info.priority_active_deals_start, self.pdf_info.priority_active_deals_end)

if __name__ == '__main__':
#    path = 'C:\Users\Deepak.Malkan\OneDrive - Bentley Systems, Inc\Documents\iTwin Ventures\Biweekly\Bentley Biweekly 121323 vF.pdf'
    path = 'D:/Deepak/source/learn-python/pdf/test2.pdf'

    pdf_processor = PdfProcessor (path)
    pdf_processor.extract_information ()
    pdf_processor.extract_sections ()

    pdf_processor.print_info ()

    pdf_processor.extract_priority_active_deals_text ()
    pdf_processor.write_priority_active_deals_json_data ()
