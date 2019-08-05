#!/usr/bin/env python3
# -*- coding：utf-8 -*-
"""
This code is an example to train data collected from car camera.
The train data is located in the directory of "training_data"
containing images and npz.
The original images are saved in the sub-directory "images" with pre-defined
name (seq_movement) while the model input data are saved in the sub-directory "npz" .
The files in npz are generated by np.savez() with "train_data" and "train_labels".
The file name of npz indicates the image resolution. For example, "train_320_240.npz"
tells us the file contains a series of 320*240 images.
"""
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.optimizers import SGD    # 梯度下降的优化器
from keras.utils import np_utils
from keras import backend as K
from keras.models import load_model
from sklearn.model_selection import train_test_split
import numpy as np
import os
import cv2
from PIL import Image


# params for CNN training
epochs = 400                        # train epochs
batch_size = 8                      # sample numbers for one batch
img_rows, img_cols = 240, 320       # image height and width after resizing
nb_filters1, nb_filters2 = 4, 8     # filter numbers
n_classes = 4                       # class numbers
update = True                       # update npz file(train_320_240.npz) according to images if true


def get_load_data(dataset_path, update=False):
    """Load npz file directly if update is true, otherwise load images first"""
    npz_path = os.path.join(dataset_path, 'npz')
    if update:
        image_path = os.path.join(dataset_path, 'images')
        image_name_list = os.listdir(image_path)
        data = []
        labels = []
        label_one_hot = np.zeros((n_classes, n_classes), 'float')
        for i in range(n_classes):
            label_one_hot[i, i] = 1
        for name in image_name_list:
            img = cv2.imread(os.path.join(image_path, name), 0)
            img = cv2.resize(img, (img_cols, img_rows), interpolation=cv2.INTER_CUBIC)
            img_ndarray = np.asarray(img, dtype='float64') / 255
            data.append(img_ndarray)
            name, _ = name.split('.')
            _, label = name.split('_')
            labels.append(label_one_hot[int(label)])
            # cv2.imshow(name, img)
            # cv2.waitKey(1)
        train_data = np.asarray(data, dtype='float64')
        train_labels = np.asarray(labels, dtype='float64')
        np.savez(os.path.join(npz_path, 'train_%d_%d.npz' % (img_cols, img_rows)),
                 train_data=train_data, train_labels=train_labels)
    else:
        data = np.load(os.path.join(npz_path, 'train_%d_%d.npz' % (img_cols, img_rows)))
        train_data = data['train_data']
        train_labels = data['train_labels']

    X_train, X_test, Y_train, Y_test = train_test_split(train_data, train_labels, test_size=0.20)
    result = [(X_train, Y_train), (X_test, Y_test)]
    return result


def get_set_model(lr=0.0001, decay=4e-6, momentum=0.9):
    """Construct a CNN model"""
    model = Sequential()
    # The first convolutional layer and maxpooling layer
    if K.image_data_format() == 'channels_first':
        model.add(Conv2D(nb_filters1, kernel_size=(3, 3), input_shape=(1, img_rows, img_cols)))
    else:
        model.add(Conv2D(nb_filters1, kernel_size=(2, 2), input_shape=(img_rows, img_cols, 1)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # The second convolutional layer and maxpooling layer
    model.add(Conv2D(nb_filters2, kernel_size=(3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    # Fully connected network
    model.add(Flatten())
    model.add(Dense(256))
    model.add(Activation('tanh'))
    model.add(Dropout(0.5))
    model.add(Dense(n_classes))
    model.add(Activation('softmax'))

    # Optimizer
    sgd = SGD(lr=lr, decay=decay, momentum=momentum, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    return model


def get_train_model(model, X_train, Y_train, X_val, Y_val):
    """ Train and save model"""
    model.fit(X_train, Y_train, batch_size=batch_size, epochs=epochs,
              verbose=1, validation_data=(X_val, Y_val))
    model.save('model/cnn_%d_%d.h5' % (img_cols, img_rows), overwrite=True)
    print("Save model: model/cnn_%d_%d.h5" % (img_cols, img_rows))
    return model


def get_test_model(X, Y):
    """Test an load model"""
    model = load_model('model/cnn_%d_%d.h5' % (img_cols, img_rows))
    score = model.evaluate(X, Y, verbose=0)
    return score

def display_prediction(model, imgs, labels):
    """Display the prediction for specific image"""
    for img, label in zip(imgs, labels):
        img_processed = cv2.resize(img, (img_cols, img_rows), interpolation=cv2.INTER_CUBIC)
        img_ndarray = np.asarray(img_processed, dtype='float64') / 255
        img_ndarray = img_ndarray.reshape(-1, img_rows, img_cols, 1)
        resp = model.predict(img_ndarray)
        prediction = int(resp.argmax(-1))
        real = int(label.argmax(-1))
        cv2.imshow("Pre:%d, Real: %d" % (prediction, real), (img.reshape(img_rows, img_cols) * 255).astype('uint8'))
        cv2.waitKey(0)


if __name__ == '__main__':
    (X_train, Y_train), (X_test, Y_test) = get_load_data('training_data', update=update)

    if K.image_data_format() == 'channels_first':
        X_train = X_train.reshape(X_train.shape[0], 1, img_rows, img_cols)
        X_val = X_test.reshape(X_test.shape[0], 1, img_rows, img_cols)
        X_test = X_test.reshape(X_test.shape[0], 1, img_rows, img_cols)
        input_shape = (1, img_rows, img_cols)
    else:
        X_train = X_train.reshape(X_train.shape[0], img_rows, img_cols, 1)
        X_val = X_test.reshape(X_test.shape[0], img_rows, img_cols, 1)
        X_test = X_test.reshape(X_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)
    print('X_train shape:', X_train.shape)
    model = get_set_model()
    X_train_processed = X_train #/ 255.
    X_test_processed = X_test #/ 255.
    get_train_model(model, X_train_processed, Y_train, X_test, Y_test)
    score = get_test_model(X_test_processed, Y_test)
    print(score)
    display_prediction(model, X_test, Y_test)