import os
os.environ["KERAS_BACKEND"] = "jax"
import cv2
# import shutil
import numpy as np
import keras
import matplotlib.pyplot as plt
# from keras.preprocessing.image import ImageDataGenerator
# from keras.models import Sequential
# from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
# from keras.preprocessing.image import ImageDataGenerator
from keras.applications import EfficientNetV2B0, MobileNetV2
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten
from keras.models import load_model
import tensorflow as tf
import pandas as pd

# tf.keras.backend.clear_session()
# print("TensorFlow version:", tf.__version__)
# print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

def initialize_MobilenetModel(path):
    # EfficientNetV2B0
    model = MobileNetV2(
        include_top=True,
        weights=None,
        classes=2,
        input_shape=(224, 224, 3),
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    # model.summary()

    # Create a checkpoint object
    checkpoint = tf.train.Checkpoint(model=model)

    # Restore the model weights from the checkpoint
    checkpoint_dir = path
    checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir)).expect_partial()

    return model

def initialize_EfficientNetModel(path):
    # EfficientNetV2B0
    model = EfficientNetV2B0(
        include_top=True,
        weights=None,
        classes=2,
        input_shape=(256, 256, 3),
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    # model.summary()

    # Create a checkpoint object
    checkpoint = tf.train.Checkpoint(model=model)

    # Restore the model weights from the checkpoint
    checkpoint_dir = path
    checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir)).expect_partial()

    return model

def initialize_NN():
    new_model = load_model('.\\weight\\pmfinal.h5')
    # new_model = load_model('.\\weight\\pmfinal.h5', compile=False)
    return new_model

def initialize_NNpt(path, input_size):
    model = Sequential()
    model.add(Conv2D(16, (3,3), 1, activation='relu', input_shape=(input_size,input_size,3)))
    model.add(MaxPooling2D())
    model.add(Conv2D(32, (3,3), 1, activation='relu'))
    model.add(MaxPooling2D())
    model.add(Conv2D(16, (3,3), 1, activation='relu'))
    model.add(MaxPooling2D())
    model.add(Flatten())
    model.add(Dense(256, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    # Create a checkpoint object
    checkpoint = tf.train.Checkpoint(model=model)

    # Restore the model weights from the checkpoint
    checkpoint_dir = path
    checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir)).expect_partial()

    return model



# C:\Users\User\water_inspection\weight
def createDF(model, camPosmodel, date):
    name_list = []
    id_list = []
    tank_name_list = []
    tank_list = []
    camPos_list = []
    predict_list = []
    shopBranch_list = []
    excel = pd.read_csv(f".\\dataframe\\{date}.csv")
    i = 0
    for id in os.listdir(f".\\images\\{date}\\"):
        for tank in os.listdir(f".\\images\\{date}\\" + id):
            if 'ถังน้ำดื่ม' in tank:
                j = 1
            elif 'ถังน้ำใช้' in tank:
                j = 2
            else:
                j = 0
            for time in os.listdir(f".\\images\\{date}\\" + id + "\\" + tank):
                for img in os.listdir(f".\\images\\{date}\\" + id + "\\" + tank + "\\" + time):
                    os.chdir(f".\\images\\{date}\\" + id + "\\" + tank + "\\" + time)
                    # os.rename(current_file_name, new_file_name)
                    new_name = f"{date}_{excel[excel['หมายเลขงาน'] == int(id)].iloc[0,2]}_tank{j}_{i}.jpg".replace(" ", "")
                    os.rename(img, new_name)
                    print(f".\\images\\{date}\\" + id + "\\" + tank + "\\" + time)
                    print(new_name)
                    pic = cv2.imread(new_name)    
                    pic = cv2.resize(pic, (256,256))
                    # pic = cv2.resize(pic, (224,224))
                    pic2 = cv2.resize(pic, (256,256))
                    # pic2 = cv2.resize(pic, (224,224))
                    pic = np.array([pic])
                    pic2 = np.array([pic2])

                    camPos_predict = camPosmodel.predict(pic)
                    print(camPos_predict)
                    if (time == 'after') and (('ถังน้ำดื่ม' in tank) or ('ถังน้ำใช้' in tank)):
                        if camPos_predict[0][0] >= 0.5:
                            # ['ไม่ถูกต้อง', 'ถูกต้อง']
                            predict = model.predict(pic2)
                            anss = predict.argmax(axis=-1)
                            print(predict, anss)
                            if predict[0] >= 0.5:
                            # if anss >= 0.5:
                                ans = "ไม่ถูกต้อง"
                            else:
                                ans = "ถูกต้อง"
                            print(f".\\images\\{date}\\" + id + "\\" + tank + "\\" + time + "\\" + img.strip(), f" : {ans}")

                            # if ('ถังน้ำดื่ม' in tank) or ('ถังน้ำใช้' in tank):
                            predict_list.append(ans)
                            name_list.append(new_name)
                            id_list.append(id)
                            shopBranch_list.append(excel[excel['หมายเลขงาน'] == int(id)].iloc[0,3])
                            if 'ถังน้ำดื่ม' in tank:
                                tank_list.append('ถังน้ำดื่ม')
                            if 'ถังน้ำใช้' in tank:
                                tank_list.append('ถังน้ำใช้')
                            tank_name_list.append(tank)
                            camPos_list.append('+')
                        else:
                            predict_list.append('มุมกล้องไม่ถูกต้อง')
                            name_list.append(new_name)
                            id_list.append(id)
                            shopBranch_list.append(excel[excel['หมายเลขงาน'] == int(id)].iloc[0,3])
                            if 'ถังน้ำดื่ม' in tank:
                                tank_list.append('ถังน้ำดื่ม')
                            if 'ถังน้ำใช้' in tank:
                                tank_list.append('ถังน้ำใช้')
                            tank_name_list.append(tank)
                            camPos_list.append('-')
                    os.chdir(f"..\\..\\..\\..\\..\\")
                    i += 1
                # j += 1

    data = pd.DataFrame({
        'name': name_list,
        'id': id_list,
        'branch': shopBranch_list,
        'tank': tank_list,
        'tank_name': tank_name_list,
        'Camera Position': camPos_list,
        "predict": predict_list
    })

    data.to_csv(f".\\dataframe\\{date}_predict.csv", index=False)

if __name__ == "__main__":
    # '.\\weight\\waterWeight50epochsEffNet.pt'

    # model = initialize_model()
    model = initialize_NN()
    camPos_model = initialize_NNpt('.\\weight\\camPosweightv3.pt', 256)
    # camPos_model = initialize_NN()
    date = "1_June_2024"

    createDF(model,camPos_model, date)
    
    tf.keras.backend.clear_session()