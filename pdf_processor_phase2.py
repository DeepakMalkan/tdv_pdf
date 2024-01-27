import tabula
import json
from pathlib import Path
from company_data import CompanyData
from sqlite_processor import Phase1Db
from sqlite_processor import Phase2Db
from sqlite_processor import DealsSection

def simplify_text_in_string (text_string):
    text_string = text_string.replace ("\r", " ")
    text_string = text_string.replace ("\u2022", "*")
    text_string = text_string.replace ("\u2013", "-")
    return text_string

def process_description (text_string):
    text_string = simplify_text_in_string (text_string)
    text_partition = text_string.partition ("Next Step(s):")
    return text_partition[0], text_partition[2]

class DealsSectionFrames ():
    """A class that holds data associated with a section of pages - such as Priority Deals, New Deals, Other Deals, etc."""

    PRIORITY_ACTIVE_DEALS = "Priority Active Deals"
    ACTIVE_DEALS = "Active Deals"
    NEW_ACTIVE_DEALS = "New Active Deals"
    OTHER_ACTIVE_DEALS = "Other Active Deals"
    CURRENT_ACTIVATE_COMPANIES = "Current iTwin Activate Companies"
    COMMERCIAL_PARTNERSHIP = "Commercial Partnership Opportunities"
    PASS_TRACK_DEALS = "Pass/ Track Deals"

    def __init__ (self, file_key, deals_section):
        super ().__init__ ()

        self.file_key = file_key    # We should use the file_key as provenance .. to build up the company's history (done later .. when storing the phase2 data in its sqlite file)
        self.deals_section = deals_section
        self.data_frame_dict = {}   # A dictionary of data frames as read by Tabula. Each data frame consists of JSON data read from one PDF page
        self.company_list = []

    def write_data_frames_as_json (self, path):
        for key in self.data_frame_dict:
            outputfile = f"{path}/{key}.json"
            with open (outputfile, "w") as text_file:
                data_frame = self.data_frame_dict[key]
                text_file.write (json.dumps (data_frame[0]))

    def save_company_data (self):
        phase2_db = Phase2Db ()
        for company_data in self.company_list:
            phase2_db.save (company_data)

    def print_company_data (self):
        for company_data in self.company_list:
            company_data.print ()

    def process_one_company_data (self, deal_type, overall_data_list, start_index, process_short):
        company_dict = overall_data_list[start_index][0]
        company_text = company_dict["text"]

        if "" == company_text:
            return
        if "Touchdown" in company_text:
            # Do not process Touchdown Ventures as a company
            return

        company_text_partition = company_text.partition ("\r")
        company_name = company_text_partition[0]
        company_data = CompanyData (company_name, deal_type, self.file_key)
        self.company_list.append (company_data)

        company_data.attributes_dict[CompanyData.DETAILS_KEY] = simplify_text_in_string (company_text)

        description_dict = overall_data_list[start_index][1]
        description_text, next_step_text = process_description (description_dict["text"])
        company_data.attributes_dict[CompanyData.DESCRIPTION_KEY] = simplify_text_in_string (description_text)
        company_data.next_step = next_step_text

        stage_funding_dict = overall_data_list[start_index][2]
        stage_funding_text = stage_funding_dict["text"]
        company_data.attributes_dict[CompanyData.STAGE_FUNDING_KEY] = simplify_text_in_string (stage_funding_text)

        if process_short == True:
            return company_data

        team_etc_list = overall_data_list[start_index + 1]
        for dict_item in team_etc_list:
            title_text = dict_item["text"]
            title_text_partition = dict_item["text"].partition ("\r")
            if len (title_text_partition[0]) <= 0:
                continue;

            value_key = ""
            value_text = title_text_partition[2]
            if title_text_partition[0] == "Team":
                value_key = CompanyData.TEAM_KEY
            elif title_text_partition[0] == "Technology":
                value_key = CompanyData.TECHNOLOGY_KEY
            elif title_text_partition[0] == "Market & Execution":
                value_key = CompanyData.MARKET_EXECUTION_KEY
            elif title_text[0] == "Strategic Synergies":
                value_key = CompanyData.STRATEGIC_SYNERGIES

            if len (value_key) > 0:
                company_data.attributes_dict[value_key] = simplify_text_in_string (value_text)

        return company_data

    def process_two_companies_per_page (self, deal_type, overall_data_list):
        self.process_one_company_data (deal_type, overall_data_list, 2, False)

        # There can be upto two companies listed per page.
        # The heuristic is that if overall_data_list is < 7 then there is only one company
        if len (overall_data_list) < 7:
            return

        # process the second company data
        self.process_one_company_data (deal_type, overall_data_list, 4, False)

    def process_three_companies_per_page (self, deal_type, overall_data_list):
        self.process_one_company_data (deal_type, overall_data_list, 2, True)

        # process the second company data
        self.process_one_company_data (deal_type, overall_data_list, 3, True)

        # process the third company data
        self.process_one_company_data (deal_type, overall_data_list, 4, True)

    def process_company_data (self):
        for key in self.data_frame_dict:
            data_frame = self.data_frame_dict[key]
            data_dict = data_frame[0]

            overall_data_list = data_dict["data"]

            process_per_page = 0
            page_title_dict = overall_data_list[0][0]
            page_title = page_title_dict["text"]
            # Regenerate the 'deal_type' by looking at the page-title. Do not use the 'deal_type' from deal section
            if DealsSectionFrames.PRIORITY_ACTIVE_DEALS in page_title:
                deal_type = DealsSection.PRIORITY_DEALS_TYPE
                process_per_page = 2
            elif DealsSectionFrames.OTHER_ACTIVE_DEALS in page_title:
                deal_type = DealsSection.OTHER_DEALS_TYPE
                process_per_page = 2
            elif DealsSectionFrames.NEW_ACTIVE_DEALS in page_title:
                deal_type = DealsSection.NEW_DEALS_TYPE
                process_per_page = 2
            elif DealsSectionFrames.ACTIVE_DEALS in page_title:
                deal_type = DealsSection.PRIORITY_DEALS_TYPE
                process_per_page = 2
            elif DealsSectionFrames.CURRENT_ACTIVATE_COMPANIES in page_title:
                deal_type = DealsSection.ACTIVATE_POTENTIAL_TYPE
                process_per_page = 3
            elif DealsSectionFrames.COMMERCIAL_PARTNERSHIP in page_title:
                deal_type = DealsSection.COMMERCIAL_PARTNERSHIPS_TYPE
                process_per_page = 3
            elif DealsSectionFrames.PASS_TRACK_DEALS in page_title:
                deal_type = DealsSection.PASS_TRACK_DEALS_TYPE
                process_per_page = 3

            #company_title_dict = overall_data_list[1][0]
            #company_title = company_title_dict["text"]
            #print (f"Company Title = {company_title}")

            if process_per_page == 2:
                self.process_two_companies_per_page (deal_type, overall_data_list)
            elif process_per_page == 3:
                self.process_three_companies_per_page (deal_type, overall_data_list)

class PdfProcessorPhase2 ():
    """A class that processes the data of a single PDF file."""
    """In this phase, we process the pages identified in phase1, identify the companies and their attributes. """
    """The data thus identified is stored in another sqlitedb file."""

    TMP_PATH ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata"

    def __init__ (self, path):
        super ().__init__ ()

        self.path = path
        self.deals_section_frame_list = []

    def load_phase1_pdf_data (self):
        phase1_db = Phase1Db ()

        basepath, self.file_key = Phase1Db.generate_basepath_and_file_key (self.path)
        self.phase1_pdf_data = phase1_db.load_phase1_pdf_data (self.file_key)

    def generate_data_frame_for_pages (self, deal_type, page_list):
        """Reads all the pages associated with a deal_type and generate one data-frame per page"""
        basename = Path (self.path).stem

        data_frame_dict = {}
        for page_number in page_list:
            # Extract the data_frame associated with one page
            data_frame = tabula.read_pdf (self.path, lattice=True, pages=page_number, output_format="json")

            # Build a dictionary of such data_frames
            key = f"{basename}_{deal_type}_{page_number}"
            data_frame_dict[key] = data_frame

        return data_frame_dict

    def read_pdf_deal_pages (self):
        for deals_section in self.phase1_pdf_data.deals_section_list:
            deals_section_frame = DealsSectionFrames (self.file_key, deals_section)
            deals_section_frame.data_frame_dict = self.generate_data_frame_for_pages (deals_section.deal_type, deals_section.page_list)
            self.deals_section_frame_list.append (deals_section_frame)

    def write_deals_data (self):
        """This write function write each deals_section as a JSON file. Used only for debugging purposes"""
        for deals_section_frames in self.deals_section_frame_list:
            deals_section_frames.write_data_frames_as_json (PdfProcessorPhase2.TMP_PATH)

    def process_company_data (self):
        for deals_section_frames in self.deals_section_frame_list:
            deals_section_frames.process_company_data ()

    def save_company_data (self):
        for deals_section_frames in self.deals_section_frame_list:
            deals_section_frames.save_company_data ()

    def print_company_data (self):
        for deals_section_frames in self.deals_section_frame_list:
            deals_section_frames.print_company_data ()