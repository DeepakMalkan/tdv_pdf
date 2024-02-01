import fitz
from functools import cmp_to_key

DELTA = 5
def equal (num1, num2):
    return abs (num1 - num2) < DELTA

def compare (block1, block2):
    if block1.rect.top_left.y - block2.rect.top_left.y < -DELTA:
        return -1
    if block1.rect.top_left.y - block2.rect.top_left.y > DELTA:
        return 1
    if block1.rect.top_left.x - block2.rect.top_left.x < -DELTA:
        return -1
    if block1.rect.top_left.x - block2.rect.top_left.x > DELTA:
        return 1
    return 0

class PdfPage ():
    def __init__(self, expected_factor) -> None:
        self.expected_factor = expected_factor
        self.block_list = []            # Consists of a list of PdfBlock(s)
        self.missing_blocks_list = []   # Consists of a list of boolean values T/F

    def generate_blocks_from_rects (self, page):
        paths = page.get_drawings ()  # extract existing drawings

        for path in paths:
            fill_color = path['fill']   # Remember fill used for path. We use this later.

            # ------------------------------------
            # draw each entry of the 'items' list
            # ------------------------------------
            item_index = 0
            for item in path["items"]:  # these are the draw commands
                item_index = item_index + 1
                if item[0] == "re":  # rectangle
                    rect = item[1]
                    top_left = rect.top_left
                    bottom_right = rect.bottom_right
                    if bottom_right.y - top_left.y > 2 and bottom_right.x - top_left.x > 2: # do not process Small horizontal/vertical rectangle
                        x_length = bottom_right.x - top_left.x
                        y_length = bottom_right.y - top_left.y

                        if x_length < y_length:
                            aspect_ratio = y_length / x_length
                        else:
                            aspect_ratio = x_length / y_length
                        area = rect.get_area ()

                        process = True
                        if area < 1000 or area > 100000: # do not process very Small or very Large rectangles
                            process = False
                        elif aspect_ratio > 7: # do not process very Long rectangles
                            process = False
                        elif aspect_ratio > 3 and area < 10000: # do not process somewhat long rectangles which are also somewhat small
                            process = False

                        if process:
                            # print (f"Area is {area}, Aspect Ratio is {aspect_ratio}")
                            block = PdfBlock (rect, fill_color)
                            self.block_list.append (block)

        # sort the blocks
        self.block_list = sorted (self.block_list, key=cmp_to_key (compare))

    def draw_shapes_for_blocks (self, page, page_index, outpdf):
        outpage = outpdf.new_page (width = page.rect.width, height = page.rect.height)
        shape = outpage.new_shape ()  # make a drawing canvas for the output page

        block_index = 0
        for block in self.block_list:
            shape.draw_rect (block.rect)
            shape.finish (fill = block.fill_color)

            text_point = fitz.Point ()
            text_point.x = (block.rect.top_left.x + block.rect.bottom_right.x) / 2
            text_point.y = (block.rect.top_left.y + block.rect.bottom_right.y) / 2
            text = f"{page_index}:{block_index}"
            shape.insert_text (text_point, text)

            block_index += 1

        shape.commit()

    def check_and_update_expected_factor (self):
        num_blocks = len (self.block_list)
        if num_blocks % self.expected_factor == 0:
            return

        # Expected_factor represents the number of unique columns. This is either 3 or 7.
        # When expected_factor is 7, then check if actual factor is 3. This happens sometimes.
        # Normally when the factor is 3, we expect upto 3 rows. So if num_blocks is <= 9, we assume that expected_factor is 3
        if self.expected_factor == 7 and num_blocks <= 9 and num_blocks % 3 == 0:
            self.expected_factor = 3

    def check_block (self, block_list, block, block_index, check_block_index):
        block_missing = False
        if check_block_index == 0 or check_block_index == 7:
            if not equal (block.rect.top_left.x, 0):
                block_missing = True
        elif check_block_index == 1 or check_block_index == 8:
            # if we are still at the first block (of the row), then we assume that the second block is at the correct position.
            # The second and third conditions are to cater for two cases.
            #   (1) The first block of first row is missing, but first block of second row is not missing (block_index is 6)
            #   (2) The first block of first row is missing, and first block of second row is missing (block_index is 7)
            if block_index != 0 and block_index != 6 and block_index != 7:
                prev_block = block_list[block_index - 1]
                if not equal (prev_block.rect.bottom_right.x, block.rect.top_left.x):
                    block_missing = True

        if block_missing:
            self.missing_blocks_list.append (True)
            check_block_index += 1
            return self.check_block (block_list, block, block_index, check_block_index)

        self.missing_blocks_list.append (False)
        check_block_index += 1
        return check_block_index

    def check_for_missing_blocks (self):
        # The function works when the expected_factor is 7
        # It updates self.missing_blocks_list .. boolean list. Approriate list position is T/F based on expected position of the missing block.
        if self.expected_factor != 7:
            return

        num_blocks = len (self.block_list)
        if num_blocks % self.expected_factor == 0:
            return

        check_block_index = 0
        block_index = 0
        for block in self.block_list:
            check_block_index = self.check_block (self.block_list, block, block_index, check_block_index)
            block_index += 1

class PdfBlock ():
    def __init__ (self, rect, fill_color) -> None:
        super ().__init__ ()
        self.rect = rect
        self.fill_color = fill_color

class PdfBlockGenerator ():

    def __init__ (self) -> None:
        super ().__init__ ()

    def generate_blocks_for_pages (self, inpath, basepath, pages, outpath, expected_factor):
        pdf_page_list = []

        doc = fitz.open(inpath)
        outpdf = None
        for page_index in pages:
            page = doc[page_index - 1]
            pdf_page = PdfPage (expected_factor)
            pdf_page.generate_blocks_from_rects (page)

            pdf_page_list.append (pdf_page)

            generated_blocks = pdf_page.block_list
            num_genenerated_blocks = len (generated_blocks)
            if num_genenerated_blocks == 0:
                print (f"NO blocks for page {basepath}:{page_index}, expected_factor {expected_factor}")
            else:
                if outpdf == None:
                    outpdf = fitz.open()
                pdf_page.draw_shapes_for_blocks (page, page_index, outpdf)

            self.expected_factor = pdf_page.check_and_update_expected_factor ()

            pdf_page.check_for_missing_blocks ()
            if len (pdf_page.missing_blocks_list) != 0:
                print (f"MISSING blocks for page {basepath}:{page_index}, expected_factor {expected_factor}, got {len (generated_blocks)}")
                print (f"Missing Blocks List for page {page_index} = {pdf_page.missing_blocks_list}")

        if outpdf != None:
            outpdf.save(outpath)

        return pdf_page_list

"""Main entry point to handling TDV PDF files."""
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
    pages1 = [8]
    pages2 = [13, 14, 15, 16]
    pages3 = [12]
    pages4 = [11]
    pages5 = [14]
    pages6 = [24]
    pages7 = [20]
    pages8 = [28]

    block_generator = PdfBlockGenerator ()
    # block_generator.generate_blocks_for_pages (inpath1, "030322", pages1, outpath1, 7)
    # block_generator.generate_blocks_for_pages (inpath2, "011222", pages2, outpath2, 7)
    # block_generator.generate_blocks_for_pages (inpath3, "121323", pages3, outpath3, 7)
    # block_generator.generate_blocks_for_pages (inpath4, "112923", pages4, outpath4, 7)
    # block_generator.generate_blocks_for_pages (inpath5, "080223", pages5, outpath5, 7)
    # block_generator.generate_blocks_for_pages (inpath6, "020222", pages6, outpath6, 7)
    # block_generator.generate_blocks_for_pages (inpath7, "101123", pages7, outpath7, 7)
    block_generator.generate_blocks_for_pages (inpath8, "011223", pages8, outpath8, 3)
