from PyQt5.QtCore import pyqtSignal, QThread

from com_formate_computervision.FormateOCR import FormateOCR
import numpy
from PIL import ImageGrab
from imutils.object_detection import non_max_suppression
import numpy as np
import pytesseract
import cv2
import math
import time
import json
import re
import pyautogui
import sys

from com_formate_glass.FormateButton import FormateButton
from com_formate_glass.FormateRect import FormateRect


class FormateTesseract(QThread):
    shoot_text_to_glass_signal = pyqtSignal(FormateRect)

    def __init__(self, window):
        QThread.__init__(self)
        pytesseract.pytesseract.tesseract_cmd = r'tesseract'
        self.parent = window
        # load the pre-trained EAST text detector
        # print("[INFO] loading EAST text detector...")

        start = time.time()
        self.net = cv2.dnn.readNet('frozen_east_text_detection.pb')
        end = time.time()
        print("Time READ neural network detector training file: " + str(end - start))
        self.rect_ocr_reading_scheduler = []

    def decode_predictions(self, scores, geometry):
        # grab the number of rows and columns from the scores volume, then
        # initialize our set of bounding box rectangles and corresponding
        # confidence scores
        (numRows, numCols) = scores.shape[2:4]
        rects = []
        confidences = []

        # loop over the number of rows
        for y in range(0, numRows):
            # extract the scores (probabilities), followed by the
            # geometrical data used to derive potential bounding box
            # coordinates that surround text
            scoresData = scores[0, 0, y]
            xData0 = geometry[0, 0, y]
            xData1 = geometry[0, 1, y]
            xData2 = geometry[0, 2, y]
            xData3 = geometry[0, 3, y]
            anglesData = geometry[0, 4, y]

            # loop over the number of columns
            for x in range(0, numCols):
                # if our score does not have sufficient probability,
                # ignore it
                if scoresData[x] < 0.5:  # 0.5 is min confidence, confidence range is 0 ~ 1.
                    continue

                # compute the offset factor as our resulting feature
                # maps will be 4x smaller than the input image
                (offsetX, offsetY) = (x * 4.0, y * 4.0)

                # etract the rotation angle for the prediction and
                # then compute the sin and cosine
                angle = anglesData[x]
                cos = np.cos(angle)
                sin = np.sin(angle)

                # use the geometry volume to derive the width and height
                # of the bounding box
                h = xData0[x] + xData2[x]
                w = xData1[x] + xData3[x]

                # compute both the starting and ending (x, y)-coordinates
                # for the text prediction bounding box
                endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
                endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
                startX = int(endX - w)
                startY = int(endY - h)

                # add the bounding box coordinates and probability score
                # to our respective lists
                rects.append((startX, startY, endX, endY))
                confidences.append(scoresData[x])

            # return a tuple of the bounding boxes and associated confidences
        return (rects, confidences)

    # def optimize_image_for_ocr(self,image):

    def shoot_around_mouse(self, window):

        rows_per_screen = 8
        screenWidth, screenHeight = pyautogui.size()  # Get the size of the primary monitor.

        def to_global_coordinates(button_rect, mouse_x=None, mouse_y=None):
            row_height = int(screenHeight / rows_per_screen)
            current_row_number = int(screenHeight / mouse_y)
            previous_rows_sum_height = int(current_row_number * row_height)
            button_rect[0][1] = button_rect[0][1] + previous_rows_sum_height
            return button_rect;

        def row_number_to_global_coordinates(rownumber):
            row_height_in_pixels = screenHeight / rows_per_screen
            return (0, row_height_in_pixels * rows_per_screen)

        while True:
            currentMouseX, currentMouseY = pyautogui.position()  # Get the XY position of the mouse.
            print("Mouse position:" + str(currentMouseX) + "," + str(currentMouseY))
            screen_row_number = int(currentMouseY / (
                    screenHeight / rows_per_screen))  # We divide the screen in 8 rows and have priority to update the row where the mouse is present and the one before and the one after
            print("Screen row number: " + str(screen_row_number))
            area_around_mouse_width = screenWidth * 2
            area_around_mouse_height = (screenHeight * 2 / rows_per_screen)

            area_around_mouse_centered_position = row_number_to_global_coordinates(screen_row_number)
            area_around_mouse_bbox = (
                area_around_mouse_centered_position[0], area_around_mouse_centered_position[1], area_around_mouse_width,
                area_around_mouse_height)
            image_around_mouse = pyautogui.screenshot(region=area_around_mouse_bbox)
            # image_around_mouse.show()
            start = time.time()
            content_to_buttonize = self.shoot(image=image_around_mouse)
            content_to_buttonize_parsed_json = json.loads(content_to_buttonize)
            content_to_buttonize_parsed_json_global_coordinates = list(map(
                lambda button_rect: to_global_coordinates(button_rect=button_rect, mouse_x=currentMouseX,
                                                          mouse_y=currentMouseY), content_to_buttonize_parsed_json))
            end = time.time()
            print("Time OCR: " + str(end - start))
            window.buttonize(content_to_buttonize)

    def shoot(self, image=None):
        currentMouseX, currentMouseY = pyautogui.position()
        print("Current mouse position,"+str(currentMouseX),str(currentMouseY))
        start = time.time()
        self.rect_ocr_reading_scheduler = self.find_rectangles_where_there_is_text(image)
        end = time.time()
        print("Find rectangles from screenshot time, " + str(end - start))

        self.rect_ocr_reading_scheduler.sort(key=lambda image_rect: ((abs(image_rect.x - currentMouseX) + abs(image_rect.y - currentMouseY))+((image_rect.x - image_rect.w) * (image_rect.y - image_rect.h))), reverse=False)   # Sort image pieces by distance to the mouse pointer and by rectangle size
        for each_target_rectangle in self.rect_ocr_reading_scheduler:
            each_target_rectangle.text = self.normalize_text(self.get_text_at_position(each_target_rectangle.im))
            self.shoot_text_to_glass_signal.emit(each_target_rectangle)





    def find_rectangles_where_there_is_text(self, image=None):
        # load the input image and grab the image dimensions

        if (image is None):
            start = time.time()
            if ("Windows" in sys.platform):
                im = ImageGrab.grab(all_screens=True)
            else:
                im = ImageGrab.grab(all_screens=False)
            end = time.time()
            print("Take Screenshot() time, " + str(end - start))
            # im.save("result.png")
            # print("my size is" + str(im.size))
            im_size_width, im_size_height = im.size
            new_size = (int(im_size_width / 1), int(im_size_height / 1))
            im_resized = im.resize(new_size)
            # im_resized.save("result_half_size.png")
            start = time.time()
            im = im_resized.convert(mode="L")
            end = time.time()
            print("Convert Image to grayscale, " + str(end - start))

        # im.save("resultL.png")
        # im = im_resized.convert(mode="1")
        # im.save("result1.png")
        else:
            im = image

        image_bytes_array = numpy.array(im).copy()

        # image = cv2.imdecode(np.fromstring(image_bytes_array, np.uint8), cv2.IMREAD_GRAYSCALE)

        image = cv2.cvtColor(image_bytes_array, cv2.COLOR_GRAY2BGR)

        orig = image.copy()

        (origH, origW) = image.shape[:2]
        # print(origH, origW)
        # set the new width and height and then determine the ratio in change
        # for both the width and height
        # (newW, newH) = (args["width"], args["height"])
        (newW, newH) = (math.ceil(origW / 32) * 32, math.ceil(origH / 32) * 32)
        rW = origW / float(newW)
        rH = origH / float(newH)

        # resize the image and grab the new image dimensions
        image = cv2.resize(image, (newW, newH))
        (H, W) = image.shape[:2]

        # define the two output layer names for the EAST detector model that
        # we are interested -- the first is the output probabilities and the
        # second can be used to derive the bounding box coordinates of text
        layerNames = [
            "feature_fusion/Conv_7/Sigmoid",
            "feature_fusion/concat_3"]

        # construct a blob from the image and then perform a forward pass of
        # the model to obtain the two output layer sets
        blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
                                     (123.68, 116.78, 103.94), swapRB=True, crop=False)
        self.net.setInput(blob)
        (scores, geometry) = self.net.forward(layerNames)

        # decode the predictions, then  apply non-maxima suppression to
        # suppress weak, overlapping bounding boxes
        (rects, confidences) = self.decode_predictions(scores, geometry)
        boxes = non_max_suppression(np.array(rects), probs=confidences)
        # print(boxes)
        # initialize the list of results

        # loop over the bounding boxes
        for (startX, startY, endX, endY) in boxes:
            # scale the bounding box coordinates based on the respective
            # ratios
            startX = int(startX * rW)
            startY = int(startY * rH)
            endX = int(endX * rW)
            endY = int(endY * rH)
            dX = 2
            dY = 4

            # apply padding to each side of the bounding box, respectively
            startX = max(0, startX - dX)
            startY = max(0, startY - dY)
            endX = min(origW, endX + (dX * 2))
            endY = min(origH, endY + (dY * 2))

            # extract the actual padded ROI
            roi = orig[startY:endY, startX:endX]

            self.rect_ocr_reading_scheduler.append(FormateRect(startX, startY, endX, endY, "text_to_detect", roi))

        return self.rect_ocr_reading_scheduler

    def normalize_text(self, str):
        return re.sub(r'\W+', '', str)

    def get_text_at_position(self, roi):
        start = time.time()
        text = pytesseract.image_to_string(roi, config='-l eng --oem 1 --psm 7')
        end = time.time()
        print("Decode text from rect," + str(end - start) + "," + text)
        return text

    def run(self):
        while True:
            print("i am running from a QT thread")
            start = time.time()
            self.shoot()
            end = time.time()
            print("Time to read text from screenshot shoot(): " + str(end - start))

# cv2.imshow("Text Detection", output)
# cv2.waitKey(0)
