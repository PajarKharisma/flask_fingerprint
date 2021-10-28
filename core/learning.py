import numpy as np
from numpy import asarray
from numpy import savez_compressed
from matplotlib import pyplot as plt
import pandas as pd 
import numpy as np
import glob, os
import cv2
import keras
from keras import layers
from keras.models import Model
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from imgaug import augmenters as iaa
import tensorflow as tf
import random
import tensorflow_addons as tfa

from keras.applications.densenet import DenseNet201
from keras.applications.vgg16 import VGG16
from keras.layers import Dense, Flatten, Concatenate
from keras.activations import relu
from keras.callbacks import ModelCheckpoint

from config import *
from config.path import Path

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "3"

class CreatePatches(tf.keras.layers.Layer):
    def __init__(self , patch_size, cnn):
        super(CreatePatches , self).__init__()
        self.patch_size = patch_size
        self.cnn = cnn

    def call(self, inputs):
        patches = []
        #For square images only (as inputs.shape[1] = inputs.shape[2])
        input_image_size = inputs.shape[1]
        for i in range(0 ,input_image_size , self.patch_size):
            for j in range(0 ,input_image_size , self.patch_size):
                patches.append(self.cnn(inputs[ : , i : i + self.patch_size , j : j + self.patch_size , : ]))
        return patches
    def get_config(self):
        return {"patch_size": self.patch_size}

    @classmethod
    def from_config(cls, config):
        return cls(**config)

class Net():
    def init_nn(self):
        x1 = layers.Input(shape=(132, 132, 3))
        x2 = layers.Input(shape=(132, 132, 3))

        # share weights both inputs
        inputs = layers.Input(shape=(132, 132, 3))
        # CNN 
        cnn = VGG16(include_top= False , input_tensor= None ,
                    input_shape=(66, 66, 3))


        #output of 4 64z64 patches
        out48 = CreatePatches(patch_size=66, cnn = cnn)(inputs)

        # #average patches
        out48 = tf.keras.layers.Average()(out48)

        #combine features
        out_combined = tf.stack([out48], axis = 1)

        feature_model = Model(inputs=inputs, outputs=out48)
        # 2 feature models that sharing weights
        x1_net = feature_model(x1)
        x2_net = feature_model(x2)
        # subtract features
        net = layers.Subtract()([x1_net, x2_net])

        net = layers.Flatten()(net)

        net = layers.Dense(64, activation='relu')(net)

        net = layers.Dense(1, activation='sigmoid')(net)

        self.model = Model(inputs=[x1, x2], outputs=net)
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['acc'])
        self.model.summary()

    def __init__(self):
        self.init_nn()
        checkpoint = ModelCheckpoint(filepath=Path.v1_model_path, 
                             monitor='val_loss',
                             verbose=1, 
                             save_best_only=True,
                             mode='min')
        callbacks = [checkpoint]
        self.model.load_weights(Path.v1_model_path)

    def calculateMatching(self, template, query, claheFlag):
        template_img = cv2.imread(template)
        query_img = cv2.imread(query)
        template_img = cv2.resize(template_img, (132,132), interpolation = cv2.INTER_AREA)
        query_img = cv2.resize(query_img, (132,132), interpolation = cv2.INTER_AREA)
        if claheFlag == True:
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))

            template_img_gray = cv2.cvtColor(template_img,cv2.COLOR_RGB2GRAY)
            query_img_gray = cv2.cvtColor(query_img,cv2.COLOR_RGB2GRAY)

            template_img_gray = clahe.apply(template_img_gray)
            template_img = cv2.cvtColor(template_img_gray,cv2.COLOR_GRAY2RGB)

            query_img_gray = clahe.apply(query_img_gray)
            query_img = cv2.cvtColor(query_img_gray,cv2.COLOR_GRAY2RGB)
        
        template_img = template_img.reshape((1, 132, 132, 3)).astype(np.float32) / 255.
        query_img = query_img.reshape((1, 132, 132, 3)).astype(np.float32) / 255.
        
        pred_ux = self.model.predict([template_img, query_img])
        return pred_ux