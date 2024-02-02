import fitz
from deal_page import DealPage

def generate_rects_for_pages (inpath, outpath, page_number_list):
    indoc = fitz.open(inpath)
    outdoc = fitz.open()

    for page_num in page_number_list:
        doc_page = indoc[page_num]

        deal_page = DealPage (3)
        path_rects, cross_lines = deal_page.generate_rects_from_path (doc_page)
        deal_page.draw_rects_and_lines (doc_page, page_num, outdoc, path_rects, cross_lines)

    outdoc.save (outpath)
    outdoc.close ()
    indoc.close ()

"""Main entry point to test the extraction of blocks."""
if __name__ == '__main__':
    inpath1 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 111723 vF.pdf"
    inpath2 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 011222 vF.pdf"
    inpath3 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 011223 vF.pdf"
    inpath4 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 030222 vF.pdf"

    outpath1 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Rects 111723.pdf"
    outpath2 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Rects 011222.pdf"
    outpath3 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Rects 011223.pdf"
    outpath4 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Rects 030222.pdf"

    generate_rects_for_pages (inpath4, outpath4, [23])