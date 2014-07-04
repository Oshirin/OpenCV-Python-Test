#!/usr/local/bin/python
# -*- coding: utf-8 -*-
 
import cgi
import os, sys
import cv2
import time
import codecs
import numpy as np
 
print "Content-Type: text/html\n\n"


detector = cv2.FeatureDetector_create("SURF")
descriptor = cv2.DescriptorExtractor_create("SURF")
matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")

UPLOAD_DIR = "./cgi-bin/img/"

print "<html><body>"

form = cgi.FieldStorage()
fileitem = form["img"]
def save_upload_file (upload_dir):
	
	if form.has_key("img") :
		form_ok = 1
	if form_ok == 0 :
		print "<h1>ERROR</h1>"
	
	Path = os.path.join(upload_dir,str(int(time.time())) + os.path.basename(fileitem.filename))
	
	fout = file(Path, 'wb')
	while 1:
		chunk = fileitem.file.read(100000)
		if not chunk: break
		fout.write(chunk)
	fout.close()
	
	print("SAVE OK!")
	return Path
	
	

Path = save_upload_file(UPLOAD_DIR)

print "<br /> save path: ", Path, "<br /><br />"

radioitem = form.getfirst("area")
UPLOAD_PATH2 = "./cgi-bin/pic/" + os.path.basename(Path)
TMP_UP = "./cgi-bin/tmp/" + os.path.basename(Path)
MASK_UP = "./cgi-bin/mask/" + os.path.basename(Path)
if radioitem == "1" :
	cascade_path = "./haarcascade_frontalface_alt_tree.xml"
else:
	cascade_path = "./haarcascade_eye_tree_eyeglasses.xml"

def cv_picture(img_path) :
	color = (255, 255, 255)
	image = cv2.imread(img_path)
	image_gray = cv2.cvtColor(image, cv2.cv.CV_BGR2GRAY)
	cascade = cv2.CascadeClassifier(cascade_path)
	facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=1, minSize=(1, 1))
	
	i = 0
	
	
	if len(facerect) > 0 :
		for rect in facerect:
			
			cv2.rectangle(image, tuple(rect[0:2]),tuple(rect[0:2]+rect[2:4]), color, thickness=2)
#			print image[rect[0]:rect[0] + rect[3], rect[1]: rect[1] + rect[3]]
#			print "<br />"
			TMP_UP = "./cgi-bin/tmp/" + str(i) + os.path.basename(Path)
			i += 1
			#cv2.imwrite(TMP_UP, image_gray[rect[1]:rect[1] + rect[2], rect[0]: rect[0] + rect[3]])
			# ガウシアンフィルタ
			#img = cv2.GaussianBlur(image_gray[rect[1]:rect[1] + rect[2], rect[0]: rect[0] + rect[3]], (9, 9), 0)
			# 画像の2値化
#			img = cv2.adaptiveThreshold(image_gray[rect[1]:rect[1] + rect[2], rect[0]: rect[0] + rect[3]], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                  cv2.THRESH_BINARY,11,3)
#			cv2.imwrite(TMP_UP, img)
			
			im = image[rect[1]:rect[1] + rect[2], rect[0]: rect[0] + rect[3]]
			im_mask = im
			im_gray = image_gray[rect[1]:rect[1] + rect[2], rect[0]: rect[0] + rect[3]]
			# ガウシアンフィルタ
			im_gray = cv2.GaussianBlur(im_gray, (9, 9), 0)
			# 2値化
			ret, thresh = cv2.threshold(im_gray, 127, 255, 0)
			#cv2.imwrite(TMP_UP, thresh)
			# 角検出
			contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			cnt = contours[0]
			
			# 凸包を描く
			hull = cv2.convexHull(cnt)
			cv2.drawContours(im_mask, [hull], 0, (255, 255, 255), -2)
			cv2.imwrite(MASK_UP, im_mask)
			
			
			# 輪郭を描く
			cv2.drawContours(im, contours, -1, (0, 0, 255), 2)
			cv2.imwrite(TMP_UP, im)

#			vec = detector.detect(image[rect[1]:rect[1] + rect[2], rect[0]: rect[0] + rect[3]])
#			(vec, descriptors) = descriptor.compute(image_gray[rect[1]:rect[1] + rect[2], rect[0]: rect[0] + rect[3]], vec)
			# Draw a small red circle with the desired radius
#			for kp in vec:
#				x = int(kp.pt[0])
#				y = int(kp.pt[1])
#				cv2.circle(image[rect[1]:rect[1] + rect[2], rect[0]: rect[0] + rect[3]], (x, y), 2, (0, 0, 255))
	else :
		TMP_UP = "./cgi-bin/tmp/" + str(i) + os.path.basename(Path)
#		img = cv2.adaptiveThreshold(image_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#				cv2.THRESH_BINARY,11,3)
#		cv2.imwrite(TMP_UP, img)
		
		im = image
		im_gray = image_gray
		# ガウシアンフィルタ
		im_gray = cv2.GaussianBlur(im_gray, (9, 9), 0)
		# 2値化
		ret, thresh = cv2.threshold(im_gray, 127, 255, 0)
		# 角検出
		contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		cnt = contours[0]
		
		# 輪郭を描く
		cv2.drawContours(im, contours, 0, (0, 0, 255), 2)
		
		cv2.imwrite(TMP_UP, im)
		
	cv2.imwrite(UPLOAD_PATH2, image)

	
	print "CV OK! <br />"
	print "CV path: ", UPLOAD_PATH2, "<br /><br />"

	
cv_picture(Path)

os.remove(Path)
print "SAVE IMAGE REMOVE!<br /><br />"


print '<form id="Form2" name="Form2" method="POST" action="./cgi-bin/pic.py">'
print '<input type="text" value=', UPLOAD_PATH2, ' name="path"><br />'
print '<input type="submit" value="show image" name="submit">'
print '</form>'

#f = open(UPLOAD_PATH2, "rb")
#b = f.read()
#f.close()
#print "Content-type: image/png"
#print 
#print b


print "</body></html>"
