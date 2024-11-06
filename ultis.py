import math
from csv import reader
def rectangle_collision(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)


def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def line_rectangle_collision(line, rect):
    (x1, y1), (x2, y2) = line
    rx, ry, rw, rh = rect
    
    rect_corners = [
        (rx, ry), (rx + rw, ry),      # Top-left to top-right
        (rx + rw, ry + rh), (rx, ry + rh)  # Bottom-right to bottom-left
    ]
    
    # Define rectangle edges as pairs of points
    rect_edges = [
        (rect_corners[0], rect_corners[1]),  # Top edge
        (rect_corners[1], rect_corners[2]),  # Right edge
        (rect_corners[2], rect_corners[3]),  # Bottom edge
        (rect_corners[3], rect_corners[0])   # Left edge
    ]
    
    # Helper function to check if two lines (p1, p2) and (q1, q2) intersect
    def do_intersect(p1, p2, q1, q2):
        # Calculate the direction of the points
        def direction(a, b, c):
            return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        
        d1 = direction(q1, q2, p1)
        d2 = direction(q1, q2, p2)
        d3 = direction(p1, p2, q1)
        d4 = direction(p1, p2, q2)

        # General case
        if d1 * d2 < 0 and d3 * d4 < 0:
            return True
        # Special case when points are collinear
        if d1 == 0 and on_segment(q1, q2, p1): return True
        if d2 == 0 and on_segment(q1, q2, p2): return True
        if d3 == 0 and on_segment(p1, p2, q1): return True
        if d4 == 0 and on_segment(p1, p2, q2): return True
        return False

    # Helper function to check if point p lies on segment ab
    def on_segment(a, b, p):
        return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])
    
    # Check intersection between the line and each rectangle edge
    for edge in rect_edges:
        if do_intersect((x1, y1), (x2, y2), edge[0], edge[1]):
            return True
    return False


def import_csv_layout(file_path, tiles_index = []):
    terain_map = []
    with open(file_path) as level_map:
        layout = reader(level_map, delimiter=",")
        for row in layout:
            if tiles_index == []:
                terain_map.append(list(row))
                continue
            filltered_row = []
            for tile in row:
                if int(tile) in tiles_index:
                    filltered_row.append(int(tile))
                else:
                    filltered_row.append(-1)
            terain_map.append(filltered_row)
                    
    return terain_map



