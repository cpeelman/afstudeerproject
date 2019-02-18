from pathlib import Path
import cv2
import dlib
import numpy as np
import argparse
from contextlib import contextmanager
from classifier.wide_resnet import WideResNet
import time
from keras.utils.data_utils import get_file

pre_trained_model = "https://github.com/yu4u/age-gender-estimation/releases/download/v0.5/weights.28-3.73.hdf5"
mod_hash = 'fbe63257a054c1c5466cfd7bf14646d6'


def start_classifier_images(path):
    print("hello")
    image_dir = path
    frames = []

    for image_path in image_dir.glob("*.*"):
        print(image_path)
        img = cv2.imread(str(image_path), 1)

        h, w, _ = img.shape
        r = 640 / max(w, h)
        cv2.resize(img, (int(w * r), int(h * r)))
        frames.append(img)
    return classify(frames)


def start_classifier_stream(frame):
    return classify(frame)


def classify(frame):
    depth = 16
    width = 8
    weight_file = "./models/yu4u_age-gender-estimation/weights.28-3.73.hdf5"
    margin = 0.4

    # for face detection
    detector = dlib.get_frontal_face_detector()

    # load model and weights
    img_size = 64
    model = WideResNet(img_size, depth=depth, k=width)()
    model.load_weights(weight_file)

    # Loads in images
    image = frame
    result_prediction = []

    input_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img_h, img_w, _ = np.shape(input_img)

    # detect faces using dlib detector
    detected = detector(input_img, 1)
    faces = np.empty((len(detected), img_size, img_size, 3))

    if len(detected) > 0:
        for i, d in enumerate(detected):
            x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
            xw1 = max(int(x1 - margin * w), 0)
            yw1 = max(int(y1 - margin * h), 0)
            xw2 = min(int(x2 + margin * w), img_w - 1)
            yw2 = min(int(y2 + margin * h), img_h - 1)
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
            # cv2.rectangle(img, (xw1, yw1), (xw2, yw2), (255, 0, 0), 2)
            faces[i, :, :, :] = cv2.resize(image[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))

        # predict ages and genders of the detected faces
        results = model.predict(faces)
        predicted_genders = results[0]
        ages = np.arange(0, 101).reshape(101, 1)
        predicted_ages = results[1].dot(ages).flatten()

        # draw results
        for i, d in enumerate(detected):
            label = [int(predicted_ages[i]),"M" if predicted_genders[i][0] < 0.5 else "F"]

            if(len(label) != 2):
                label[0] = -1
                label[1] = "U"

            result_prediction.append(label)

    return result_prediction
