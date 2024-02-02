import fitz
from functools import cmp_to_key

DELTA = 5
def equal (num1, num2):
    return abs (num1 - num2) < DELTA

def rect_compare (rect1, rect2):
    if rect1.y0 - rect2.y0 < -DELTA:
        return -1
    if rect1.y0 - rect2.y0 > DELTA:
        return 1
    if rect1.x0 - rect2.x0 < -DELTA:
        return -1
    if rect1.x0 - rect2.x0 > DELTA:
        return 1
    return 0

def block_compare (block1, block2):
    return rect_compare (block1.rect, block2.rect)

def generate_bounding_box_for_rects (rects):
    '''Generate a bounding box that represents the detail area of the page's data. Ignore the first rect, since it is the title rectangle'''
    bounding_box = fitz.Rect ()

    rect_index = 0
    for rect in rects:
        if rect_index == 1:
            bounding_box.x0 = rect.x0
            bounding_box.y0 = rect.y0
            bounding_box.x1 = rect.x1
            bounding_box.y1 = rect.y1
        elif rect_index != 0: # Ignore the first rect - its the title rect
            if rect.x0 < bounding_box.x0:
                bounding_box.x0 = rect.x0
            if rect.y0 < bounding_box.y0:
                bounding_box.y0 = rect.y0
            if rect.x1 > bounding_box.x1:
                bounding_box.x1 = rect.x1
            if rect.y1 > bounding_box.y1:
                bounding_box.y1 = rect.y1
        rect_index += 1

    return bounding_box

class Line:
    def __init__(self, x1, y1, x2, y2) -> None:
        self.start_point = fitz.Point (x1, y1)
        self.end_point = fitz.Point (x2, y2)

def line_touches_rect_horizontal (cross_line, bounding_box, path_rects):
    y0 = cross_line.start_point.y
    y1 = cross_line.end_point.y
    if abs (y0 - bounding_box.y0) < DELTA or abs (bounding_box.y1 - y1) < DELTA:   # touching bounding_box
        return True

    for rect in path_rects:
        if abs (y0 - rect.y0) < DELTA or abs (rect.y1 - y1) < DELTA: # touching rect
            return True
        
    return False

def line_touches_rect_vertical (cross_line, bounding_box, path_rects):
    x0 = cross_line.start_point.x
    x1 = cross_line.end_point.x
    if abs (x0 - bounding_box.x0) < DELTA or abs (bounding_box.x1 - x1) < DELTA:   # touching bounding_box
        return True

    for rect in path_rects:
        if abs (x0 - rect.x0) < DELTA or abs (rect.x1 - x1) < DELTA: # touching path rect
            return True
        
    return False

def line_spans_and_in_rect_vertical (cross_line, bounding_box, path_rects):
    min_y = min (cross_line.start_point.y, cross_line.end_point.y)
    max_y = max (cross_line.start_point.y, cross_line.end_point.y)

    if line_touches_rect_vertical (cross_line, bounding_box, path_rects):
        return False

    # Check that line points span across the bounding_box.
    if abs (bounding_box.y0 - min_y) < DELTA and abs (bounding_box.y1 - max_y) < DELTA:
        return True

    for rect in path_rects:
        if abs (rect.y0 - min_y) < DELTA or abs (rect.y1 - max_y) < DELTA:
            return True

    return False
        

class DealPage ():
    '''A DealPage class consists of a set of sorted PageBlocks associated with a single page of a Deal'''
    def __init__(self, expected_factor) -> None:
        self.expected_factor = expected_factor
        self.block_list = []            # A list of sorted PageBlock(s)
        self.missing_blocks_list = []   # A list of boolean values T/F (currently unused)

    def generate_cross_line_from_path (self, path, path_rects, bounding_box):
        path_items = path["items"]
        num_items = len (path_items)
        if num_items != 1:
            return

        item_index = 0
        for item in path_items:
            if item[0] == "l":  # line
                start_point = item[1]
                end_point = item[2]

                # Potential cross line should be either vertical or horizontal
                if start_point.x == end_point.x or start_point.y == end_point.y:
                    # Check that start_point and end_point are not the same
                    if start_point.x == end_point.x and start_point.y == end_point.y:
                        return

                    # For horizontal line
                    if start_point.y == end_point.y:
                        # Check that line points touch the bounding_box.
                        min_x = min (start_point.x, end_point.x)
                        max_x = max (start_point.x, end_point.x)
                        
                        if abs (bounding_box.x0 - min_x) < DELTA and abs (bounding_box.x1 - max_x) < DELTA:
                            cross_line = Line (min_x, start_point.y, max_x, start_point.y)
                            return cross_line

                    # For vertical line
                    if start_point.x == end_point.x:
                        min_y = min (start_point.y, end_point.y)
                        max_y = max (start_point.y, end_point.y)
                        
                        cross_line = Line (start_point.x, min_y, start_point.x, max_y)

                        if line_spans_and_in_rect_vertical (cross_line, bounding_box, path_rects):
                            return cross_line

            elif item[0] == "re":  # rectangle
                rect = item[1]

                # Rectangle should be a denegerate line
                if rect.y1 - rect.y0 < DELTA: # Horizontal
                    # Line should span the bounding box
                    if abs (bounding_box.x0 - rect.x0) < DELTA and abs (bounding_box.x1 - rect.x1) < DELTA and \
                        rect.y0 - bounding_box.y0 > DELTA and bounding_box.y1 - rect.y1 > DELTA:    # Should be inside the bounding box
                        cross_line = Line (rect.x0, rect.y0, rect.x1, rect.y1)

                        if line_touches_rect_horizontal (cross_line, bounding_box, path_rects) == False:
                            return cross_line

                if rect.x1 - rect.x0 < DELTA: # Vertical
                    # Line should span the bounding box
                    if abs (bounding_box.y0 - rect.y0) < DELTA and abs (bounding_box.y1 - rect.y1) < DELTA and \
                        rect.x0 - bounding_box.x0 > DELTA and bounding_box.x1 - rect.x1 > DELTA:    # Should be inside the bounding box
                        cross_line = Line (rect.x0, rect.y0, rect.x1, rect.y1)
                        return cross_line

            elif item[0] == "qu":  # quad
                raise ValueError("unexpected quad")
            elif item[0] == "c":  # curve
                raise ValueError("unexpected curve")
            else:
                raise ValueError("unhandled drawing")

            item_index = item_index + 1

        return

    def generate_cross_lines_for_page (self, doc_page, path_rects, bounding_box):
        paths = doc_page.get_drawings()  # extract existing drawings

        cross_lines = []
        for path in paths:
            cross_line = self.generate_cross_line_from_path (path, path_rects, bounding_box)
            if cross_line != None:
                cross_lines.append (cross_line)

        return cross_lines

    def generate_rect_from_path (self, path):
        path_items = path["items"]
        num_items = len (path_items)
        # print (f"Number of items in path = {num_items}")
        if num_items < 4:
            return

        top_left = fitz.Point ()
        bottom_right = fitz.Point ()
        item_index = 0
        for item in path_items:
            if item[0] == "l":  # line
                start_point = item[1]
                end_point = item[2]

                if item_index == 0:
                    top_left.x = start_point.x
                    top_left.y = start_point.y
                    bottom_right.x = start_point.x
                    bottom_right.y = start_point.y
                else:
                    if start_point.x < top_left.x:
                        top_left.x = start_point.x
                    if start_point.y < top_left.y:
                        top_left.y = start_point.y
                    if start_point.x > bottom_right.x:
                        bottom_right.x = start_point.x
                    if start_point.y > bottom_right.y:
                        bottom_right.y = start_point.y

                if end_point.x < top_left.x:
                    top_left.x = end_point.x
                if end_point.y < top_left.y:
                    top_left.y = end_point.y
                if end_point.x > bottom_right.x:
                    bottom_right.x = end_point.x
                if end_point.y > bottom_right.y:
                    bottom_right.y = end_point.y

            elif item[0] == "re":  # rectangle
                raise ValueError("unexpected rectangle")
            elif item[0] == "qu":  # quad
                raise ValueError("unexpected quad")
            elif item[0] == "c":  # curve
                raise ValueError("unexpected curve")
            else:
                raise ValueError("unhandled drawing")

            item_index = item_index + 1

        return fitz.Rect (top_left, bottom_right)

    def generate_rects_from_path (self, doc_page):
        paths = doc_page.get_drawings()  # extract existing drawings

        path_rects = []
        for path in paths:
            path_rect = self.generate_rect_from_path (path)
            if path_rect != None:
                path_rects.append (path_rect)

        # sort the rects
        path_rects = sorted (path_rects, key = cmp_to_key (rect_compare))

        bounding_box = generate_bounding_box_for_rects (path_rects)
        cross_lines = self.generate_cross_lines_for_page (doc_page, path_rects, bounding_box)
        return path_rects, cross_lines

    def generate_blocks_from_rects (self, doc_page):
        paths = doc_page.get_drawings ()  # extract existing drawings

        for path in paths:
            fill_color = path['fill']   # Remember fill used for path. We use this later.

            # ------------------------------------
            # draw each entry of the 'items' list
            # ------------------------------------
            item_index = 0
            for item in path["items"]:
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

                        # print (f"Area is {area}, Aspect Ratio is {aspect_ratio}")
                        process = True
                        if area < 1000 or area > 100000: # do not process very Small or very Large rectangles
                            process = False
                        elif aspect_ratio > 7: # do not process very Long rectangles
                            process = False
                        elif aspect_ratio > 3 and area < 10000: # do not process somewhat long rectangles which are also somewhat small
                            process = False

                        if process:
                            block = PageBlock (rect, fill_color)
                            self.block_list.append (block)

        # sort the blocks
        self.block_list = sorted (self.block_list, key=cmp_to_key (block_compare))

    def draw_rects (self, doc_page, page_index, rects):
        shape = doc_page.new_shape()  # make a drawing canvas for the output page

        rect_index = 0
        for rect in rects:
            shape.draw_rect (rect)

            text_point = fitz.Point ()
            text_point.x = (rect.x0 + rect.x1) / 2
            text_point.y = (rect.y0 + rect.y1) / 2
            text = f"R{page_index}:{rect_index}"
            shape.insert_text (text_point, text)
            # print (f"Rectangle {rect_index}, top_left = {rect.top_left}, bottom_right = {rect.bottom_right}")
            rect_index += 1

        shape.finish ()

        # all paths processed - commit the shape to its page
        shape.commit()

    def draw_lines (self, doc_page, lines):
        shape = doc_page.new_shape()  # make a drawing canvas for the output page

        line_index = 0
        for line in lines:
            shape.draw_line(line.start_point, line.end_point)

            text_point = fitz.Point ()
            text_point.x = (line.start_point.x + line.end_point.x) / 2
            text_point.y = (line.start_point.y + line.end_point.y) / 2
            text = f"L{line_index}"
            shape.insert_text (text_point, text)
            # print (f"Line {line_index}, start_point = {line.start_point}, end_point = {line.end_point}")
            line_index += 1

        shape.finish ()

        # all paths processed - commit the shape to its page
        shape.commit()

    def draw_rects_and_lines (self, doc_page, page_index, outdoc, rects, lines):
        outpage = outdoc.new_page (width = doc_page.rect.width, height = doc_page.rect.height)

        self.draw_rects (outpage, page_index, rects)
        self.draw_lines (outpage, lines)


    def draw_shapes_for_blocks (self, doc_page, page_index, outdoc):
        outpage = outdoc.new_page (width = doc_page.rect.width, height = doc_page.rect.height)
        shape = outpage.new_shape ()  # make a drawing canvas for the output page

        block_index = 0
        for block in self.block_list:
            shape.draw_rect (block.rect)
            shape.finish (fill = block.fill_color)

            text_point = fitz.Point ()

            text_point.x = block.rect.top_left.x
            text_point.y = block.rect.top_left.y
            text = doc_page.get_text (sort = True, clip = block.rect)
            shape.insert_text (text_point, text)

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

class PageBlock ():
    '''A PageBlock Class consists of a single identified rectangle on the Page, with associated fill color'''

    def __init__ (self, rect, fill_color) -> None:
        super ().__init__ ()
        self.rect = rect
        self.fill_color = fill_color