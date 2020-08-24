
# Multiprocessing Challenge

This is a hackathon challenge to understand and learn the multiprocessing functionality in Python


## Usage

```python

python3 MultiProc.py

```
The terminal will then ask for the following:
```terminal
Enter the width of the images ->

Enter the height of the images ->

Enter the number of images ->

Press <ENTER> for next image or type END
```

1. We first start the program with python3 MultiProc.py
2. The program then asks to enter the width of the images
3. The program then asks to enter the height of the images
4. The program then asks for the total number of images that have to be displayed
5. For each of the images to display, you should keep hitting <ENTER> after each image or type END to exit

## Walk-through the code

**Process# 1**

```python
def worker1(queue_a, width, height, num_images):

    for i in range(num_images.value):

        color = color_chart[random.randrange(1, len(color_chart))]
        img = np.zeros([height.value, width.value, 3], dtype=np.uint8)
        img[:, :] = color
        queue_a.put(img)

    return
```

1. Generates the random number and picks up the color from the chart as per the index
2. Generates a numpy array with zeroes and height/width as specified by user. The third dimension is always 3 since this is  RGB regime
3. We fill the numpy array with the corresponding selected color value. The image is then transferred over to the queueA


**Process# 2**

```python

def worker2(queue_a,queue_b,event_quit):

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
```

1. If the queueA is filled with even a single element, this process picks it up
2. IT first determines what color is the original picked image from queueA
3. Then determines the corresponding complementary color using the function complementary(r,b,g)
4. According to the complementary color, it draws a circle of that same color at the center
5. IT then puts the corresponding color as a watermark at a certain location on the modified image
6. This image is then placed on a queueB
7. Note that the process also checks for the event_quit signal for when we want to forcefully stop all the processes and exit


**Process# 3**

```python
def worker3(array_a, width, height, event_array_updated, event_quit):

    while True:

        if event_quit.is_set():

            break

        if event_array_updated.is_set():

            event_array_updated.clear()

            arr = list(array_a[:])
            arr = np.reshape(arr, (height.value, width.value, 3))
            Image.fromarray(np.uint8(arr), 'RGB').show()

    return

```

1. Whenever the main application signals that the arrayA has been updated through 'event_array_updated', this process simply picks up the image from the updated array
2. The array is then reshaped to the appropriate shape using numpy function
3. The resulting image is then displayed using PIL function ***Image.fromarray()***
4. Note that even this function checks for 'event_quit' signal from the main application to stop all the processes and exit


**Main Application**



1. Here we first initialize all the necessary variables and start the processes. Below code follows after that

```python

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
```

2. Since we have already started the processes, the process# 1 has already started generating the images and putting them onto the queueA
3. And process# 2 has also started picking up these images, processing them and putting them onto the queueB
4. Here the main application waits for the user input and if he has asked for the next image, main application simply puts the available image from queueB onto the array
5. It then initiates the process# 3 to pick the image from this array and display it

## Sample Output

## Unit Testing

Hit the following in the file to run the tests

```python
py.test test_YOUR_SCRIPT.py

```

Below shows the sample output generated

```

============================= test session starts ==============================
platform darwin -- Python 3.7.4, pytest-2.9.1, py-1.9.0, pluggy-0.3.1
rootdir: /Users/kedjoshi/Desktop/venv, inifile:
collected 4 items

test_YOUR_SCRIPT.py ....

=========================== 4 passed in 1.10 seconds ===========================



