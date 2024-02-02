import fitz
from functools import cmp_to_key

DELTA = 5
def equal (num1, num2):
    return abs (num1 - num2) < DELTA

def compare (rect1, rect2):
    if rect1.y0 - rect2.y0 < -DELTA:
        return -1
    if rect1.y0 - rect2.y0 > DELTA:
        return 1
    if rect1.x0 - rect2.x0 < -DELTA:
        return -1
    if rect1.x0 - rect2.x0 > DELTA:
        return 1
    return 0

class Line:
    def __init__(self, x1, y1, x2, y2) -> None:
        self.start_point = fitz.Point (x1, y1)
        self.end_point = fitz.Point (x2, y2)

def line_touches_rect_horizontal (cross_line, bounding_box, path_rects):
    y0 = cross_line.start_point.y
    y1 = cross_line.end_point.y
    if abs (y0 - bounding_box.y0) < DELTA or abs (bounding_box.y1 - y1) < DELTA:   # touching bounding_box
        return True

    for path in path_rects:
        if abs (y0 - path.y0) < DELTA or abs (path.y1 - y1) < DELTA: # touching path
            return True
        
    return False

def draw_lines (page, lines):
    shape = page.new_shape()  # make a drawing canvas for the output page

    line_index = 0
    for line in lines:
        shape.draw_line(line.start_point, line.end_point)

        text_point = fitz.Point ()
        text_point.x = (line.start_point.x + line.end_point.x) / 2
        text_point.y = (line.start_point.y + line.end_point.y) / 2
        text = f"L{line_index}"
        shape.insert_text (text_point, text)
        print (f"Line {line_index}, start_point = {line.start_point}, end_point = {line.end_point}")
        line_index += 1

    shape.finish ()

    # all paths processed - commit the shape to its page
    shape.commit()

def draw_rects (page, rects):
    shape = page.new_shape()  # make a drawing canvas for the output page

    rect_index = 0
    for rect in rects:
        shape.draw_rect (rect)

        text_point = fitz.Point ()
        text_point.x = (rect.x0 + rect.x1) / 2
        text_point.y = (rect.y0 + rect.y1) / 2
        text = f"R{rect_index}"
        shape.insert_text (text_point, text)
        print (f"Rectangle {rect_index}, top_left = {rect.top_left}, bottom_right = {rect.bottom_right}")
        rect_index += 1

    shape.finish ()

    # all paths processed - commit the shape to its page
    shape.commit()

def generate_cross_line_from_path (path, path_rects, bounding_box):
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
                    # Check that line points touch the bounding_box.
                    min_y = min (start_point.y, end_point.y)
                    max_y = max (start_point.y, end_point.y)
                    
                    if abs (bounding_box.y0 - min_y) < DELTA and abs (bounding_box.y1 - max_y) < DELTA:
                        cross_line = Line (start_point.x, min_y, start_point.x, max_y)
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

def generate_cross_lines_for_page (page, path_rects, bounding_box):
    paths = page.get_drawings()  # extract existing drawings

    cross_lines = []
    for path in paths:
        cross_line = generate_cross_line_from_path (path, path_rects, bounding_box)
        if cross_line != None:
            cross_lines.append (cross_line)

    return cross_lines

def generate_rect_from_path (path):
    path_items = path["items"]
    num_items = len (path_items)
    print (f"Number of items in path = {num_items}")
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

def generate_path_rects_for_page (page):
    paths = page.get_drawings()  # extract existing drawings

    path_rects = []
    for path in paths:
        path_rect = generate_rect_from_path (path)
        if path_rect != None:
            path_rects.append (path_rect)

    return path_rects

def generate_rects_for_pages (inpath, outpath, page_number_list):
    doc = fitz.open(inpath)

    outpdf = fitz.open()

    for page_num in page_number_list:
        page = doc[page_num]
        path_rects = generate_path_rects_for_page (page)

        # define some output page_num with the same dimensions
        outpage = outpdf.new_page (width=page.rect.width, height=page.rect.height)

        # sort the rects
        path_rects = sorted (path_rects, key = cmp_to_key (compare))

        draw_rects (outpage, path_rects)

        bounding_box = generate_bounding_box_for_rects (path_rects)

        cross_lines = generate_cross_lines_for_page (page, path_rects, bounding_box)
        draw_lines (outpage, cross_lines)

    outpdf.save(outpath)

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

    generate_rects_for_pages (inpath3, outpath3, [19])