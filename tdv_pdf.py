import sys
import os
from pdf_processor_phase1 import PdfProcessorPhase1
from pdf_processor_phase2 import PdfProcessorPhase2

class TdvPdf ():
    """A class that holds key information about the processing of TDV PDF files"""

    def __init__ (self):
        super ().__init__ ()

        self.phase1 = False
        self.phase2 = False

    def process_arguments (self):
        num_args = len (sys.argv)
        print (f"Arguments count: {num_args}")
        if (num_args == 1):
            self.phase1 = True
            self.phase2 = True
        elif num_args > 1:
            for i, arg in enumerate (sys.argv):
                if (arg == "--phase1"):
                    self.phase1 = True
                elif (arg == "--phase2"):
                    self.phase2 = True

    def process_phase1 (self, path):
        if (self.phase1):
            pdf_processor_phase1 = PdfProcessorPhase1 (path)
            pdf_processor_phase1.process ()

    def process_phase2 (self, path):
        if (self.phase2):
            pdf_processor_phase2 = PdfProcessorPhase2 (path)
            pdf_processor_phase2.load_phase1_pdf_data ()
            pdf_processor_phase2.read_pdf_deal_pages ()
            pdf_processor_phase2.write_deals_data ()
            # pdf_processor_phase2.process_company_data ()
            # pdf_processor_phase2.save_company_data ()
            # pdf_processor_phase2.print_company_data ()

"""Main entry point to handling TDV PDF files."""
if __name__ == '__main__':
    tdv_pdf = TdvPdf ()
    tdv_pdf.process_arguments ()

#    path = 'D:/Deepak/source/learn-python/tdv_pdf/test2.pdf'
    path1 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 030222 vF.pdf"
    path2 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 011223 vF.pdf"
    path3 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 012721 vF.pdf"
    path4 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 101922 vF.pdf"
    path5 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 050422 vF.pdf"
    dir_path1 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly"
    dir_path2 = "D:/Deepak/Personal/Bentley Biweekly"

    tdv_pdf.process_phase1 (path5)
    # tdv_pdf.process_phase1 (path4)

    # tdv_pdf.process_phase2 (path4)

    # directory = os.fsencode (dir_path2)
    # for file in os.listdir (directory):
    #     filename = os.fsdecode (file)
    #     filepath = f"{dir_path2}/{filename}"
    #     if filename.endswith (".pdf"):
    #         tdv_pdf.process_phase1 (filepath)

