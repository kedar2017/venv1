import multiprocessing
import numpy as np
from multiprocessing.sharedctypes import RawArray
from PIL import Image
import random
import cv2
import ctypes
from copy import deepcopy
import sys

color_chart = [[0,0,0],[255,255,255],[255,0,0],[255,255,0],[0,255,0],[0,255,255],[0,0,255],[255,0,255]]
color_names = ['Black', 'White', 'Red', 'Yellow', 'Lime', 'Aqua', 'Blue', 'Fuschia']
color_map = {(0,0,0):'Black',(255,255,255):'White',(255,0,0):'Red',(255,255,0):'Yellow',(0,255,0):'Lime',(0,255,255):'Aqua',(0,0,255):'Blue',(255,0,255):'Fuschia'}

def hilo(a, b, c):

    '''
    Returns the median RBG value on the color map between the given color and it's complementary
    :param a:
    :param b:
    :param c:
    :return:
    '''

    if c < b: b, c = c, b
    if b < a: a, b = b, a
    if c < b: b, c = c, b
    return (int(a)+int(c))/2

def complement(r, g, b):

    '''
    Returns the complementary color for the input color
    :param r:
    :param g:
    :param b:
    :return:
    '''

    k = hilo(r, g, b)
    return tuple(k - u for u in (r, g, b))

def worker1(q1, width, height, num_images, event):

    '''
    Generates an RGB image of a random color from a given list of colors
    Stores the resulting image on a queueA
    :param q1:
    :param width:
    :param height:
    :param num_images:
    :param event:
    :return:
    '''

    for i in range(num_images.value):
        color = color_chart[random.randrange(1,len(color_chart))]
        array = np.zeros([height.value, width.value, 3], dtype=np.uint8)
        array[:,:] = color
        q1.put(array)

    event.wait()

    return

def worker2(q1,q2,event):

    '''
    Picks an image from the queueA. Determines the color of the image.
    Paints a circular region at the center with color complimentary to that of the input image. Adds watermark corresponding to that image color
    Adds the resulting image onto the queueB

    :param q1:
    :param q2:
    :param event:
    :return:
    '''

    while True:

        if event.is_set():

            break

        if not q1.empty():

            obj = q1.get()
            complement_color = complement(obj[0,0][0],obj[0,0][1],obj[0,0][2])
            center_coordi = (len(obj[0])//2,len(obj)//2)
            radius = min(len(obj),len(obj[0]))//4
            cv2.circle(obj, center_coordi, radius, complement_color, -11)
            cv2.putText(obj, color_map[(obj[0,0][0],obj[0,0][1],obj[0,0][2])], center_coordi,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            q2.put(obj)

    return

def worker3(q,e,width,height, event):

    '''
    Waits for the arrayA buffer to update. As soon as there is an update, it picks up the image and displays it

    :param q:
    :param e:
    :param width:
    :param height:
    :param event:
    :return:
    '''

    while True:

        if event.is_set():

            break

        if e.is_set():

            e.clear()

            a = list(q)
            a = np.reshape(a, (height.value, width.value, 3))
            Image.fromarray(np.uint8(a), 'RGB').show()

    return

if __name__ == '__main__':

    queue1 = multiprocessing.Queue()
    queue2 = multiprocessing.Queue()
    queue3 = multiprocessing.Queue()

    width = multiprocessing.Value('i',100)
    height= multiprocessing.Value('i',100)
    num_images = multiprocessing.Value('i',2)
    img_counter= 0

    raw_arr = multiprocessing.Array('i',width.value*height.value*3)

    e = multiprocessing.Event()
    event_quit = multiprocessing.Event()

    p1 = multiprocessing.Process(target=worker1, args=(queue1,width,height,num_images,event_quit,))
    p1.start()

    p2 = multiprocessing.Process(target=worker2, args=(queue1,queue2,event_quit,))
    p2.start()

    p3 = multiprocessing.Process(target=worker3, args=(raw_arr,e,width,height,event_quit,))
    p3.start()

    while True:


        inp = input("Press <ENTER> for next image or press END")

        if inp == "END" or img_counter == num_images.value:

            event_quit.set()

            break


        arr = queue2.get()
        arr = list(arr.flatten())

        for i in range(len(arr)):
            raw_arr[i] = arr[i]

        img_counter += 1

        e.set()

    # Wait for the worker to finish
    queue1.close()
    queue1.join_thread()
    p1.join()

    queue2.close()
    queue2.join_thread()
    p2.join()

    p3.join()

    sys.exit(0)

