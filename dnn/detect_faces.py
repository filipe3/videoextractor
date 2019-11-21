# python detect_faces.py --image rooster.jpg --prototxt deploy.prototxt.txt --model res10_300x300_ssd_iter_140000.caffemodel

import os
import numpy as np
import argparse
import cv2
import torch 
import random
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,	help="path to input image")
ap.add_argument("-p", "--prototxt", required=True, help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True, help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.5, help="minimum probability to filter weak detections")
args = vars(ap.parse_args())


def input_for_ssd(image):
	return cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

def input_for_retinaface(image):
	return cv2.dnn.blobFromImage(cv2.resize(image, (640, 640)), 1.0, (640, 640), (104.0, 117.0, 123.0))
	
def get_scores_ssd(img, detections):
	# loop over the detections
	for i in range(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with the prediction
		confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the `confidence` is greater than the minimum confidence
		if confidence > args["confidence"]:
			print (confidence)
			# compute the (x, y)-coordinates of the bounding box for the object
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")


			refPoint = [(startX, startY), (endX, endY)]
			cropped = img[refPoint[0][1]:refPoint[1][1], refPoint[0][0]:refPoint[1][0]]

			count_face = 0
			file_exists = True
			output_path = None

			while (file_exists):
				output_path = "{}\\{}_face{}.jpg".format(Path(args["image"]).parent, Path(args["image"]).stem, count_face)
				print ("Output Path: {}".format(output_path))
				file_exists = os.path.exists(output_path)
				count_face += 1

			cv2.imwrite(output_path, cropped)

			# draw the bounding box of the face along with the associated probability
			text = "{:.2f}%".format(confidence * 100)
			y = startY - 10 if startY - 10 > 10 else startY + 10
			cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
			cv2.putText(image, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

	#show the output image
	#cv2.imshow("Output", image)
	#cv2.waitKey(0)

      
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

image = cv2.imread(args["image"])
(h, w) = image.shape[:2]
blob = input_for_ssd(image)

net.setInput(blob)

getLayer = net.getLayerNames()
out_layer_names = [getLayer[i[0] - 1] for i in net.getUnconnectedOutLayers()]
print (out_layer_names)

print("[INFO] computing object detections...")
detections = net.forward()

get_scores_ssd(image, detections)