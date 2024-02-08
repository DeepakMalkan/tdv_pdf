import json
from sqlite_processor import Phase1Db
from sqlite_processor import Phase2Db

class PdfProcessorPhase2 ():
    """A class that processes the data of a single PDF file."""
    """In this phase, we process the pages identified in phase1, identify the companies and their attributes. """
    """The data thus identified is stored in another sqlitedb file."""

    TMP_PATH ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata"

    def __init__ (self, path):
        super ().__init__ ()

        self.path = path

    def load_phase1_db_data (self):
        phase1_db = Phase1Db ()

        basepath, self.file_key = Phase1Db.generate_basepath_and_file_key (self.path)
        self.phase1_pdf_data = phase1_db.load (self.file_key)

    def process_company_data (self):
        for deals_section in self.phase1_pdf_data.deals_section_list:
            deals_section.process_company_data (self.path, self.file_key)

    def save_company_data (self):
        phase2_db = Phase2Db ()
        for deals_section in self.phase1_pdf_data.deals_section_list:
            deals_section.save_company_data (phase2_db)

    def print_company_data (self):
        for deals_section in self.phase1_pdf_data.deals_section_list:
            deals_section.print_company_data ()

    def process (self):
        self.load_phase1_db_data ()
        self.process_company_data ()
        self.save_company_data ()
        self.print_company_data ()