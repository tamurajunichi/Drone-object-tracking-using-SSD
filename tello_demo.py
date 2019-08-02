import cv2
import tellopy
import numpy
import av
import math as m
from time import sleep



(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

def handler(event, sender, data, **args):
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        print(data)

def tracking(drone,d,dx,dy,key):
    if dx > 60:
        drone.counter_clockwise(25)
    elif dx < -60:
        drone.clockwise(25)
    elif dy > 60:
        drone.up(20)
    elif dy < -60:
        drone.down(30)
    else:
        drone.forward(22)

'''
def forward(drone,dx,dy,d,count):
    print(count)
    if dx < 100 and dx > -100 and dy < 100 and dy > -100:
        drone.clean(0)
        if d < 3000 and count <= 2:
            for i in range(3):
                drone.forward(20)
                count += 1
                print(count)
                sleep(5)
    return count
'''

def key_Operation(drone,key):
    if key == ord('n'):
        drone.down(15)
        sleep(1)
    elif key==ord('u'):
        drone.up(15)
        sleep(1)
    elif key==ord('h'):
        drone.left(15)
        sleep(1)
    elif key==ord('j'):
        drone.right(15)
        sleep(1)
    elif key==ord('b'):
        drone.backward(15)
        sleep(1)
    elif key==ord('f'):
        drone.forward(15)
        sleep(1)
    elif key==ord('c'):
        drone.clockwise(15)
        sleep(1)
    elif key==ord('p'):
        drone.clean(0)
        sleep(1)

def main():
    global S0
    tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
    tracker_type = tracker_types[2]
    if int(minor_ver) < 3:
        tracker = cv2.TrackerKCF_create()
    else:
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()
        if tracker_type == 'MOSSE':
            tracker = cv2.TrackerMOSSE_create()
        if tracker_type == "CSRT":
            tracker = cv2.TrackerCSRT_create()
    x = 200
    y = 200
    w = 224
    h = 224
    track_window=(x,y,w,h)

    L0 = 100
    LB = 100
    bbox = (x, y, w, h)

    drone = tellopy.Tello()
    drone.connect()

    container = av.open(drone.get_video_stream())

    drone.takeoff()

    drone.is_autopilot="False"

    count = 0

    while True:
        for frame in container.decode(video=0):


            image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
            height = image.shape[0]
            width = image.shape[1]
            depth = image.dtype

            timer = cv2.getTickCount()

            ok, bbox = tracker.update(image)

            timers = cv2.getTickFrequency()

            ffps = timers / (cv2.getTickCount() - timer);
            fps = (cv2.getTickCount() - timer) / timers

            #print("FPS:",fps)
            #print('FFPS',ffps)


            # Draw bounding box
            if ok:
                (x,y,w,h) = (int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3]))
                CX=int(bbox[0]+0.5*bbox[2])
                CY=int(bbox[1]+0.5*bbox[3])
                #print('bbox[2]', bbox[2])
                #print('bbox[3]', bbox[3])
                S0=int(bbox[2]*bbox[3])
                #print('S0', S0)

                #print("CX,CY,S0=",CX,CY,S0)
                p1 = (x, y)
                p2 = (x + w, y + h)
                cv2.rectangle(image, p1, p2, (0,255,0), 5, 1)
            else :
                cv2.putText(image, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
                drone.clean(0)

            cv2.putText(image, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
            #cv2.putText(image, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2)
            cv2.imshow('test',image)

            key = cv2.waitKey(1)
            if key == ord('a'):
                drone.is_autopilot="True"
            elif key == ord('s'):
                drone.is_autopilot="False"

            if drone.is_autopilot=="True":
                d = round(L0 * m.sqrt(S0 / (w * h)))

                #　表示される映像の中心とバインディングボックスの中心との差
                dx = (width/2) - CX
                dy = (height/2) - CY

                print("w * h:",w * h)
                print("dx,dy:",dx,dy)
                tracking(drone,d,dx,dy,key)
                #count = forward(drone,dx,dy,d,count)

            elif drone.is_autopilot=="False":
                key_Operation(drone,key)
                #print("key=",key,ord('q'))


            
            if key == ord('q'):
                cv2.destroyAllWindows()
                break
            elif key == ord('r'):
                bbox = cv2.selectROI(image, False)
                print(bbox)
                (x,y,w,h) = (int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3]))
                ok = tracker.init(image, bbox)

        break
    drone.down(50)
    sleep(5)
    drone.land()
    drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
    drone.quit()

if __name__ == '__main__':
    main()  