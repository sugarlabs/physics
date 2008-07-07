#==================================================================
#                           Physics.activity
#                     Helper classes and functions
#                           By Alex Levenson
#==================================================================
import math
# distance calculator, pt1 and pt2 are ordred pairs
def distance(pt1, pt2):
        return math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] -pt2[1]) ** 2)

# returns the angle between the line segment from pt1 --> pt2 and the x axis, from -pi to pi
def getAngle(pt1,pt2):
    xcomp = pt2[0] - pt1[0]
    ycomp = pt1[1] - pt2[1]
    return math.atan2(ycomp,xcomp)

# returns a list of ordered pairs that describe an equilteral triangle around the segment from pt1 --> pt2
def constructTriangleFromLine(p1,p2):
    halfHeightVector = (0.57735*(p2[1] - p1[1]), 0.57735*(p2[0] - p1[0]))
    p3 = (p1[0] + halfHeightVector[0], p1[1] - halfHeightVector[1])
    p4 = (p1[0] - halfHeightVector[0], p1[1] + halfHeightVector[1])
    return [p2,p3,p4]
