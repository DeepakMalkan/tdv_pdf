import fitz
from deal_page import DealPage

class PdfBlockGenerator ():

    def __init__ (self) -> None:
        super ().__init__ ()

    def generate_blocks_for_pages (self, inpath, basepath, pages, outpath, expected_factor):
        pdf_page_list = []

        indoc = fitz.open(inpath)
        outdoc = fitz.open ()
        for page_index in pages:
            doc_page = indoc[page_index - 1]
            deal_page = DealPage (expected_factor)
            deal_page.generate_blocks_from_rects (doc_page)

            pdf_page_list.append (deal_page)

            generated_blocks = deal_page.block_list
            num_genenerated_blocks = len (generated_blocks)
            if num_genenerated_blocks == 0:
                deal_page.generate_blocks_from_path (doc_page)
                generated_blocks = deal_page.block_list
                num_genenerated_blocks = len (generated_blocks)

            if num_genenerated_blocks == 0:
                print (f"NO blocks for page {basepath}:{page_index}, expected_factor {expected_factor}")
                continue

            deal_page.draw_shapes_for_blocks (doc_page, page_index, outdoc)

            self.expected_factor = deal_page.check_and_update_expected_factor ()

            deal_page.check_for_missing_blocks ()
            if len (deal_page.missing_blocks_list) != 0:
                print (f"MISSING blocks for page {basepath}:{page_index}, expected_factor {expected_factor}, got {len (generated_blocks)}")
                print (f"Missing Blocks List for page {page_index} = {deal_page.missing_blocks_list}")

        outdoc.save(outpath)

        indoc.close ()

        return pdf_page_list

"""Main entry point to test the extraction of blocks."""
if __name__ == '__main__':
    inpath1 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 030222 vF.pdf"
    inpath2 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 011222 vF.pdf"
    inpath3 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 121323 vF.pdf"
    inpath4 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 112923 vF.pdf"
    inpath5 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 080223 vF.pdf"
    inpath6 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 020222 vF.pdf"
    inpath7 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 101123 vF.pdf"
    inpath8 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 011223 vF.pdf"

    outpath1 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Blocks 030222.pdf"
    outpath2 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Blocks 011222.pdf"
    outpath3 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Blocks 121323.pdf"
    outpath4 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Blocks 112923.pdf"
    outpath5 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Blocks 080223.pdf"
    outpath6 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Blocks 020222.pdf"
    outpath7 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Blocks 101123.pdf"
    outpath8 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Blocks 011223.pdf"

    # pages1 = [8, 9, 10, 15, 16]
    pages1 = [20]
    pages2 = [13, 14, 15, 16]
    pages3 = [12]
    pages4 = [11]
    pages5 = [14]
    pages6 = [24]
    pages7 = [20]
    pages8 = [28]

    block_generator = PdfBlockGenerator ()
    block_generator.generate_blocks_for_pages (inpath1, "030322", pages1, outpath1, 7)
    # block_generator.generate_blocks_for_pages (inpath2, "011222", pages2, outpath2, 7)
    # block_generator.generate_blocks_for_pages (inpath3, "121323", pages3, outpath3, 7)
    # block_generator.generate_blocks_for_pages (inpath4, "112923", pages4, outpath4, 7)
    # block_generator.generate_blocks_for_pages (inpath5, "080223", pages5, outpath5, 7)
    # block_generator.generate_blocks_for_pages (inpath6, "020222", pages6, outpath6, 7)
    # block_generator.generate_blocks_for_pages (inpath7, "101123", pages7, outpath7, 7)
    # block_generator.generate_blocks_for_pages (inpath8, "011223", pages8, outpath8, 3)
