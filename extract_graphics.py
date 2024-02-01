import fitz

inpath1 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 111723 vF.pdf"
inpath2 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 011222 vF.pdf"
inpath3 = "C:/Users/Deepak.Malkan/OneDrive - Bentley Systems, Inc/Documents/iTwin Ventures/Bentley Biweekly/Bentley Biweekly 011223 vF.pdf"
doc = fitz.open(inpath3)
page = doc[20]
paths = page.get_drawings()  # extract existing drawings
# this is a list of "paths", which can directly be drawn again using Shape
# -------------------------------------------------------------------------
#
# define some output page with the same dimensions
outpdf = fitz.open()
outpage = outpdf.new_page(width=page.rect.width, height=page.rect.height)
shape = outpage.new_shape()  # make a drawing canvas for the output page
# --------------------------------------
# loop through the paths and draw them
# --------------------------------------
rect_index = 0
line_index = 0
path_index = 0
for path in paths:
    fill_color = path['fill']
    color = path["color"]
    stroke_opacity=path.get("stroke_opacity", 1)
    fill_opacity=path.get("fill_opacity", 1)
    print (f"Path_index = {path_index} Path color = {color}, fill_color = {fill_color}")
    path_index = path_index + 1

    # ------------------------------------
    # draw each entry of the 'items' list
    # ------------------------------------
    item_index = 0
    for item in path["items"]:  # these are the draw commands
        print (f"   Item_index = {path_index}:{item_index}")
        item_index = item_index + 1
        if item[0] == "l":  # line
            start_point = item[1]
            end_point = item[2]

            if start_point.y == end_point.y:    # horizontal line
                length = end_point.x - start_point.x
                offset = 0 #length / 10
                start_point.x = start_point.x + offset
                end_point.x = end_point.x - offset
            if start_point.x == end_point.x:    # vertical line
                length = end_point.y - start_point.y
                offset = 0 #length / 20
                start_point.y = start_point.y + offset
                end_point.y = end_point.y - offset
                start_point.x = start_point.x + offset
                end_point.x = end_point.x - offset

            print (f"       Line {line_index}, start point = {start_point}, end point = {end_point}")
            shape.draw_line(start_point, end_point)

            text_point = fitz.Point ()
            text_point.x = (start_point.x + end_point.x) / 2
            text_point.y = (start_point.y + end_point.y) / 2
            text = f"L{line_index}"
            shape.insert_text (text_point, text)
            line_index += 1
        elif item[0] == "re":  # rectangle
            rect = item[1]
            top_left = rect.top_left
            bottom_right = rect.bottom_right
            if bottom_right.y - top_left.y < 5:
                print ("Small horizontal rectangle")
                shape.draw_line(rect.top_left, rect.bottom_right)
            elif bottom_right.x - top_left.x < 5:
                print ("Small vertical rectangle")
            else:
                x_length = bottom_right.x - top_left.x
                y_length = bottom_right.y - top_left.y
                if x_length < y_length:
                    aspect_ratio = y_length / x_length
                else:
                    aspect_ratio = x_length / y_length
                area = rect.get_area ()
                print (f"Rectangle aspect ratio = {aspect_ratio}, area = {area}")
                if aspect_ratio > 4:
                    print (f"Long rectangle")
                # elif area > 100000:
                    # print (f"Rectangle too large")
                else:
                    offset = 0 #(x_length + y_length) / 20
                    new_top_left = fitz.Point(top_left.x + offset, top_left.y + offset)
                    new_bottom_right =  fitz.Point (bottom_right.x - offset, bottom_right.y - offset)
                    shape.draw_rect (fitz.Rect (new_top_left, new_bottom_right))

                    text_point = fitz.Point ()
                    text_point.x = (top_left.x + bottom_right.x) / 2
                    text_point.y = (top_left.y + bottom_right.y) / 2
                    text = f"R{rect_index}"
                    print (f"Rectangle {rect_index}, top_left = {top_left}, bottom_right = {bottom_right}")
                    shape.insert_text (text_point, text)
                    rect_index += 1
        elif item[0] == "qu":  # quad
            shape.draw_quad(item[1])
        elif item[0] == "c":  # curve
            shape.draw_bezier(item[1], item[2], item[3], item[4])
        else:
            raise ValueError("unhandled drawing", item)
    # ------------------------------------------------------
    # all items are drawn, now apply the common properties
    # to finish the path
    # ------------------------------------------------------
    shape.finish (
        # fill = path["fill"],
        color=path["color"],
    )

    # shape.finish(
    #     fill=path["fill"],  # fill color
    #     color=path["color"],  # line color
    #     dashes=path["dashes"],  # line dashing
    #     even_odd=path.get("even_odd", True),  # control color of overlaps
    #     closePath=path["closePath"],  # whether to connect last and first point
    #     lineJoin=path["lineJoin"],  # how line joins should look like
    #     lineCap=path["lineCap"],  # how line ends should look like
    #     width=path["width"],  # line width
    #     stroke_opacity=path.get("stroke_opacity", 1),  # same value for both
    #     fill_opacity=path.get("fill_opacity", 1),  # opacity parameters
    #     )
# all paths processed - commit the shape to its page
shape.commit()

# Process Text
# textBlocks = page.get_text ("blocks")

# for textBlock in textBlocks:
#     text = textBlock[4]
#     outpage.insert_text (fitz.Point(textBlock[0], textBlock[1]), text)

outpath1 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Graphics 111723.pdf"
outpath2 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Graphics 011222.pdf"
outpath3 ="D:/Deepak/source/learn-python/tdv_pdf/tmpdata/Graphics 011223.pdf"
outpdf.save(outpath3)