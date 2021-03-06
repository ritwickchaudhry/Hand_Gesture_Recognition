import cv2
import numpy as np
from math import sqrt
def distance(point1, point2):
    return sqrt((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)
def thresh_det(x1,y1,x2,y2,img):
    averageB = 0
    averageG = 0
    averageR = 0
    sumB = 0
    sumG = 0
    sumR = 0
    for i in range(x1, x2):
        for j in range(y1, y2):
            sumB+=img[i, j, 0]
            sumG+=img[i, j, 1]
            sumR+=img[i, j, 2]
    averageB = sumB/400
    averageG = sumG/400
    averageR = sumR/400
    varB , varG, varR = 0,0,0
    for i in range(x1, x2):
        for j in range(y1, y2):
            varB += (averageB - img[i,j,0])**2
            varG += (averageG - img[i,j,1])**2
            varR += (averageR - img[i,j,2])**2
    sdB = int(sqrt(varB/400))
    sdG = int(sqrt(varG/400))
    sdR = int(sqrt(varR/400))
    factor = 1
    lowerb= np.array([averageB-sdB*factor, averageG-sdG*factor, averageR-sdR*factor])
    upperb= np.array([averageB+sdB*factor, averageG+sdG*factor, averageR+sdR*factor])
    return [cv2.inRange(img,lowerb,upperb), averageB, averageG, averageR, [sdB, sdG, sdR]]

def my_thresh(img, res, error):
    factor = 1
    lowerb = np.array([res[0]-error[0]*factor, res[1]-error[1]*factor, res[2]-error[2]*factor])
    upperb = np.array([res[0]+error[0]*factor, res[1]+error[1]*factor, res[2]+error[2]*factor])
    return cv2.inRange(img, lowerb, upperb)

def distance(point1, point2):
    return sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def find_fingers(centre, radius, poly_points):
    error_margin = radius*0.25
    finger_points = []
    for i in range(len(poly_points)):
        if distance(centre, poly_points[i][0]) > radius+error_margin:
            finger_points.append(poly_points[i][0])
    return finger_points

cap = cv2.VideoCapture(1)
res1, res2, res3, res4, res5, res6 = [], [], [], [], [], []
sd1, sd2, sd3, sd4, sd5, sd6 =[], [], [], [], [], []
hull = []
while (1):
    _, img1=cap.read()

    cv2.rectangle(img1, (241, 230), (263, 208), (0, 255, 0), 0)
    cv2.rectangle(img1, (219, 281), (241, 259), (0, 255, 0), 0)
    cv2.rectangle(img1, (271, 285), (293, 263), (0, 255, 0), 0)
    cv2.rectangle(img1, (263, 185), (285, 163), (0, 255, 0), 0)
    cv2.rectangle(img1, (281, 215), (301, 235), (0, 255, 0), 0)
    cv2.rectangle(img1, (309, 172), (329, 192), (0, 255, 0), 0)



    images = []
    images.append(thresh_det(242, 209, 262, 229, img1)[0])
    images.append(thresh_det(220, 260, 240, 280, img1)[0])
    images.append(thresh_det(272, 264, 292, 284, img1)[0])
    images.append(thresh_det(264, 164, 284, 184, img1)[0])
    images.append(thresh_det(281, 215, 301, 235, img1)[0])
    images.append(thresh_det(309, 172, 329, 192, img1)[0])

    img2 = np.zeros((480,640), np.uint8)
    for i in range(6):
        img2 += images[i]

    res1 = thresh_det(242, 209, 262, 229, img1)[1:4]
    res2 = thresh_det(220, 260, 240, 280, img1)[1:4]
    res3 = thresh_det(272, 264, 292, 284, img1)[1:4]
    res4 = thresh_det(264, 164, 284, 184, img1)[1:4]
    res5 = thresh_det(281, 215, 301, 235, img1)[1:4]
    res6 = thresh_det(309, 172, 329, 192, img1)[1:4]



    sd1 = thresh_det(242, 209, 262, 229, img1)[4]
    sd2 = thresh_det(220, 260, 240, 280, img1)[4]
    sd3 = thresh_det(272, 264, 292, 284, img1)[4]
    sd4 = thresh_det(264, 164, 284, 184, img1)[4]
    sd5 = thresh_det(281, 215, 301, 235, img1)[4]
    sd6 = thresh_det(309, 172, 329, 192, img1)[4]

    blur = cv2.medianBlur(img2, 13)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(blur, kernel)
    cv2.imshow("dst", dilated)
    cv2.imshow("img", img1)


    k = cv2.waitKey(5)
    if k == 27:
        break
cv2.destroyAllWindows()


while 1:
    _, im = cap.read()
    ims=[]
    ims.append(my_thresh(im, res1, sd1))
    ims.append(my_thresh(im, res2, sd2))
    ims.append(my_thresh(im, res3, sd3))
    ims.append(my_thresh(im, res4, sd4))
    ims.append(my_thresh(im, res5, sd5))
    ims.append(my_thresh(im, res6, sd6))

    img_add = np.zeros((480,640), np.uint8)
    for i in range(6):
        img_add += ims[i]

    blur = cv2.medianBlur(img_add, 15)

    blur_copy = blur.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(blur, kernel)

    contours, hierarchy = cv2.findContours(blur.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    maxarea = 0
    pos = -1
    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])
        if area > maxarea:
            maxarea = area
            pos = i

    contour = cv2.drawContours(im, contours, pos, (0, 0, 255), 3)
    cnt = contours[pos]
    cv2.drawContours(im, cv2.convexHull(cnt, True, True), -1, (255, 0, 0), 3)
    hull = cv2.convexHull(cnt, returnPoints=False)
    hull1 = cv2.convexHull(cnt, returnPoints=True)

    M = cv2.moments(cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    radius = 0
    for i in range(len(cnt)):
        radius += distance((cx, cy), cnt[i][0])

    radius /= len(cnt)

    pts = np.array(hull1, np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.polylines(im, [pts], True, (255, 0, 0))
    poly = cv2.approxPolyDP(pts, 20, True)

    for i in range(len(poly)):
        cv2.circle(im, tuple(poly[i][0]), 10, [255, 0, 255], 1)
        cv2.line(im, (cx, cy), tuple(poly[i][0]), [0,0,0], 2 )

    cv2.drawContours(im, poly, -1, (0, 0, 0), 3)

    validPoints=[]
    defects = cv2.convexityDefects(cnt, hull)
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        far = tuple(cnt[f][0])
        cv2.circle(im, far, 20, [255, 255, 0], 1)
        dis = distance(far, (cx,cy)) 
        if dis < 1.25*radius:
            validPoints.append(far)

    cxNew = 0
    cyNew = 0
    for point in validPoints:
        cxNew += point[0]
        cyNew += point[1]

    cxNew /= len(validPoints)
    cyNew /= len(validPoints)

    radiusNew = 0
    for point in validPoints:
        radiusNew += distance((cxNew, cyNew), point)

    radiusNew /= len(validPoints)

    cv2.circle(im, (cx, cy), int(radiusNew), [255, 255, 255], 1)
    cv2.circle(im, (cxNew, cyNew), int(radiusNew), [0, 0, 0], 5)

    numberOfCircles = len(find_fingers((cxNew, cyNew), radiusNew, poly))
    print numberOfCircles
    for point in find_fingers((cxNew, cyNew), radiusNew, poly):
        cv2.circle(im, tuple(point), 10, [0, 255, 0], -1)

    cv2.imshow("blur", blur)
    cv2.imshow("dilate", dilated)
    cv2.imshow("im", im)

    k=cv2.waitKey(5)
    if k==27:
        break
cv2.destroyAllWindows()
