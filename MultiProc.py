import multiprocessing
import numpy as np
from PIL import Image
import random
import cv2
import sys

color_chart = [[0,0,0],[255,255,255],[255,0,0],[255,255,0],[0,255,0],[0,255,255],[0,0,255],[255,0,255]]
color_names = ['Black', 'White', 'Red', 'Yellow', 'Lime', 'Aqua', 'Blue', 'Fuschia']
color_map = {(0,0,0):'Black',(255,255,255):'White',(255,0,0):'Red',(255,255,0):'Yellow',(0,255,0):'Lime',(0,255,255):'Aqua',(0,0,255):'Blue',(255,0,255):'Fuschia'}

def get_user_width():

    '''
    Asks for user input on the width. Remember that the width has to be 100 at a minimum
    :return:
    '''

    while True:
        width = input("Enter the width for images (Min 100)")

        try:

            width = int(width)

            if width >= 100:
                break

            else:
                print("Width can't be lesser than 100")

        except ValueError:
            print("Width must be a number, try again")

    return width

def get_user_height():

    '''
    Asks for user input on the height. Remember that the height has to be 100 at a minimum
    :return:
    '''

    while True:
        height = input("Enter the height for images (Min 100)")

        try:

            height = int(height)

            if height >= 100:
                break

            else:
                print("Height can't be lesser than 100")

        except ValueError:
            print("Height must be a number, try again")

    return height

def get_user_num_images():

    '''
    Asks for user input on the num of images. Remember that the number has to be 1 at a minimum
    :return:
    '''

    while True:
        num_images = input("Enter the number of images")

        try:

            num_images = int(num_images)

            if num_images >= 1:
                break

            else:
                print("Number of images can't be lesser than 1")

        except ValueError:
            print("Number of images must be a number, try again")

    return num_images

def hilo(a, b, c):

    '''
    Returns the median RBG value on the color map between the given color and it's complementary
    :param a: Red component
    :param b: Green component
    :param c: Blue component
    :return:
    '''

    if c < b: b, c = c, b
    if b < a: a, b = b, a
    if c < b: b, c = c, b
    return (int(a)+int(c))/2

def complement(r, g, b):

    '''
    Returns the complementary color for the input color
    :param r: Red component
    :param g: Green component
    :param b: Blue component
    :return:
    '''

    k = hilo(r, g, b)
    return tuple(k - u for u in (r, g, b))

def worker1(queue_a, width, height, num_images):

    '''
    Generates an RGB image of a random color from a given list of colors
    Stores the resulting image on a queueA
    :param queue_a: Output queue for process# 1 where initial images are generated
    :param width: Width of the image
    :param height: Height of the image
    :param num_images: Number of total images to be generated as provided by the user
    :return:
    '''

    for i in range(num_images.value):

        color = color_chart[random.randrange(1, len(color_chart))]
        img = np.zeros([height.value, width.value, 3], dtype=np.uint8)
        img[:, :] = color
        queue_a.put(img)

    return

def worker2(queue_a,queue_b,event_quit):

    '''
    Picks an image from the queueA. Determines the color of the image.
    Paints a circular region at the center with color complimentary to that of the input image. Adds watermark corresponding to that image color
    Adds the resulting image onto the queueB
    :param queue_a: Queue for getting inputs from process# 1
    :param queue_b: Queue for outputting from process# 2
    :param event_quit: Event call to signal program completion for all the processes
    :return:
    '''

    while True:

        if event_quit.is_set():

            break

        if not queue_a.empty():

            img = queue_a.get()

            complement_color = complement(img[0,0][0], img[0,0][1], img[0,0][2])
            center_coordi = (len(img[0])//2, len(img)//2)
            radius = min(len(img), len(img[0]))//4
            cv2.circle(img, center_coordi, radius, complement_color, -11)
            cv2.putText(img, color_map[(img[0,0][0], img[0,0][1], img[0,0][2])], (0, len(img[0])//8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, complement_color, 2)

            queue_b.put(img)

    return

def worker3(array_a, width, height, event_array_updated, event_quit):

    '''
    Waits for the arrayA buffer to update. As soon as there is an update, it picks up the image and displays it

    :param array_a: Array that gets updated from the main application with the latest image to be displayed
    :param width: Width of the image
    :param height: Height of the image
    :param event_array_updated: Event call for when the array gets filled up with the latest image
    :param event_quit: Event call to signal program completion for all the processes
    :return:
    '''

    while True:

        if event_quit.is_set():

            break

        if event_array_updated.is_set():

            event_array_updated.clear()

            arr = list(array_a[:])
            arr = np.reshape(arr, (height.value, width.value, 3))
            Image.fromarray(np.uint8(arr), 'RGB').show()

    return

if __name__ == '__main__':

    queue_a = multiprocessing.Queue()
    queue_b = multiprocessing.Queue()

    inp_width = get_user_width()
    inp_height= get_user_height()
    inp_num = get_user_num_images()

    width = multiprocessing.Value('i', inp_width)
    height= multiprocessing.Value('i', inp_height)
    num_images = multiprocessing.Value('i', inp_num)
    hit_counter = 0

    array_a = multiprocessing.Array('i', width.value * height.value * 3)

    event_array_updated = multiprocessing.Event()
    event_quit = multiprocessing.Event()
    event_start = multiprocessing.Event()

    p1 = multiprocessing.Process(target= worker1, args=(queue_a, width, height, num_images,))
    p1.start()

    p2 = multiprocessing.Process(target= worker2, args=(queue_a, queue_b, event_quit,))
    p2.start()

    p3 = multiprocessing.Process(target= worker3, args=(array_a, width, height, event_array_updated, event_quit,))
    p3.start()

    while True:


        inp = input("Press <ENTER> for next image or type END")

        if inp == "END" or hit_counter == num_images.value:

            event_quit.set()

            while not queue_b.empty():

                a = queue_b.get()

            break

        event_start.set()

        img = queue_b.get()
        arr = list(img.flatten())
        array_a[:len(arr)] = arr

        hit_counter += 1

        event_array_updated.set()

    # Wait for the worker to finish
    queue_a.close()
    queue_a.join_thread()
    p1.join()

    queue_b.close()
    queue_b.join_thread()

    p2.join()

    p3.join()

    sys.exit(0)

