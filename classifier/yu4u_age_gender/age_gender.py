import os

import cv2
import numpy as np

from classifier.yu4u_age_gender.wide_resnet import WideResNet

# Disable verbose tensorflow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # or any {'0', '1', '2'}

depth = 16
width = 8
weight_file = "./models/yu4u_age-gender-estimation/weights.29-3.76_utk.hdf5"
margin = 0.4

# load model and weights
img_size = 64
model = WideResNet(img_size, depth=depth, k=width)()
model.load_weights(weight_file)


def classify(frame, face):
    # TODO: the model works on multiple faces for some weird reason, we should support that

    # set colors to rgb
    input_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # cv2.imshow("face0", input_frame)

    # make image smaller and weird colors
    img_h, img_w, _ = np.shape(input_frame)
    face_small_weird = np.empty((1, img_size, img_size, 3))
    x1, y1, w, h = face
    x2, y2 = x1 + w, y1 + h
    xw1 = max(int(x1 - margin * w), 0)
    yw1 = max(int(y1 - margin * h), 0)
    xw2 = min(int(x2 + margin * w), img_w - 1)
    yw2 = min(int(y2 + margin * h), img_h - 1)
    face_small_weird[0, :, :, :] = cv2.resize(frame[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))
    # cv2.imshow("face small weird", face_small_weird)

    # predict age and gender
    results = model.predict(face_small_weird)

    # age
    ages = np.arange(0, 101).reshape(101, 1)
    age = int(results[1].dot(ages).flatten()[0])
    # print(np.sum(results[1][0]), np.max(results[1][0]))
    # TODO: it should be possible to determine the certainity too, but need statistics

    # gender
    gender = 'M' if results[0][0][0] < .5 else 'F'
    gender_certainty = np.amax(results[0][0])

    return age, gender, gender_certainty
