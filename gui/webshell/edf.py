import cv2
import mahotas as mh
import datetime, uuid
import numpy as np

def edf(files, user):
    dat = []
    for file in files:
        dat.append(cv2.imread(file, cv2.IMREAD_GRAYSCALE))
    image = np.array(dat)

    stack,h,w = image.shape
    focus = np.array([mh.sobel(t, just_filter=True) for t in image])
    best = np.argmax(focus, 0)

    image = image.reshape((stack,-1))
    image = image.transpose()
    r = image[np.arange(len(image)), best.ravel()]
    r = r.reshape((h,w))

    fname = "%s/%s.%s.EDF.png" % (user.replace('/', '').replace('..', ''), str(datetime.datetime.now()), str(uuid.uuid4()))
    cv2.imwrite("/home/pi/igem15-sw/captured/%s" % fname, r)

    return "/captured/%s" % fname
