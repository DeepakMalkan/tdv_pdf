import sys
import os
from pdf_processor_phase1 import PdfProcessorPhase1

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


"""Main entry point to handling TDV PDF files."""
if __name__ == '__main__':
    tdv_pdf = TdvPdf ()
    tdv_pdf.process_arguments ()

#    path = 'D:/Deepak/source/learn-python/tdv_pdf/test2.pdf'
#    path1 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 090121 vF.pdf"
#    path2 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 011223 vF.pdf"
    dir_path = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly"

    directory = os.fsencode (dir_path)

    for file in os.listdir (directory):
        filename = os.fsdecode (file)
        filepath = f"{dir_path}/{filename}"
        if filename.endswith (".pdf"):
            tdv_pdf.process_phase1 (filepath)

    #pdf_processor.extract_priority_active_deals_data ()
    #pdf_processor.write_priority_active_deals_data ()
    #pdf_processor.priority_active_deals.extract_key_strings ()
