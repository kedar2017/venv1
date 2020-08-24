import pytest
import numpy as np
import multiprocessing
import random
import queue
import cv2

color_chart = [[0,0,0],[255,255,255],[255,0,0],[255,255,0],[0,255,0],[0,255,255],[0,0,255],[255,0,255]]
color_map = {(0,0,0):'Black',(255,255,255):'White',(255,0,0):'Red',(255,255,0):'Yellow',(0,255,0):'Lime',(0,255,255):'Aqua',(0,0,255):'Blue',(255,0,255):'Fuschia'}

def hilo(a, b, c):

	if c < b: b, c = c, b
	if b < a: a, b = b, a
	if c < b: b, c = c, b

	return (int(a)+int(c))/2


def test_complement():

	r = 255
	g = 255
	b = 255

	k = hilo(r, g, b)

	assert tuple(k - u for u in (r, g, b)) == (0.0,0.0,0.0), "test failed"

def test_worker3():

	event_quit = multiprocessing.Event()
	event_array_updated = multiprocessing.Event()

	event_quit.set()
	event_array_updated.set()

	assert event_quit.is_set(), "test failed"
	assert event_array_updated.is_set(), "test failed"


def test_worker2():

	queue_a = queue.Queue(maxsize=100)
	queue_b = queue.Queue(maxsize=100)

	event_quit = multiprocessing.Event()
	event_quit.set()

	img = np.zeros([100, 100, 3], dtype=np.uint8)

	queue_a.put(img)

	if not queue_a.empty():

		img = queue_a.get()

		complement_color = [255,0,255]
		center_coordi = (len(img[0])//2, len(img)//2)
		radius = min(len(img), len(img[0]))//4
		cv2.circle(img, center_coordi, radius, complement_color, -11)
		cv2.putText(img, color_map[(img[0,0][0], img[0,0][1], img[0,0][2])], (0, len(img[0])//2),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, complement_color, 2)

		queue_b.put(img)

		assert queue_b.empty() == False, "test failed"

def test_worker1():

	queue_a = queue.Queue(maxsize=100)

	num_images = multiprocessing.Value('i', 8)
	height = multiprocessing.Value('i', 100)
	width = multiprocessing.Value('i', 100)

	for i in range(num_images.value):

		color = color_chart[random.randrange(1, len(color_chart))]
		img = np.zeros([height.value, width.value, 3], dtype=np.uint8)
		img[:, :] = color
		queue_a.put(img)

	assert queue_a.empty() == False, "test failed"