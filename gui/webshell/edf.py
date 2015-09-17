import cv2
import mahotas as mh
import datetime, uuid
import numpy as np

def edf(jpegs, user):
    def stack(image):
        stack,h,w = image.shape
        focus = np.array([mh.sobel(t, just_filter=True) for t in image])
        best = np.argmax(focus, 0)

        image = image.reshape((stack,-1))
        image = image.transpose()
        r = image[np.arange(len(image)), best.ravel()]
        r = r.reshape((h,w))
        return r

    dat = []
    for jpeg in jpegs:
        jpeg = np.fromstring(jpeg, dtype=np.uint8)
        dat.append(cv2.imdecode(jpeg, cv2.IMREAD_COLOR))

    r = cv2.merge(tuple(stack(np.array([im[:,:,channel] for im in dat])) for channel in range(3)))

    fname = "%s/%s.%s.EDF.png" % (user.replace('/', '').replace('..', ''), str(datetime.datetime.now()), str(uuid.uuid4()))
    cv2.imwrite("/home/pi/igem15-sw/captured/%s" % fname, r)

    return "/captured/%s" % fname
