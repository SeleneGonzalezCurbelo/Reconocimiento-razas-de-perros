# -*- coding: utf-8 -*-
"""Reconocimiento Perros

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rlrQY-oFnTD6oQOrQ5PWG2gRFW21Mpzv

# Reconocedor de Razas de Perros
"""

from google.colab import drive
drive.mount('/content/drive')

"""Ahora ya es accesible

¿Estoy realmente utilizando una GPU? Compruébalo en **Editar / Configuración del cuaderno** o **Entorno de ejecución / Cambiar tipo de entorno de ejecución**
"""

import tensorflow as tf
tf.test.gpu_device_name()

"""Veamos una imagen de ejemplo."""

# Commented out IPython magic to ensure Python compatibility.
!ls "/content/drive/My Drive/Prueba FSI/dataSets5/training/GoldenRetriever"

from matplotlib.pyplot import imshow
import numpy as np
from PIL import Image

# %matplotlib inline
pil_im = Image.open('/content/drive/My Drive/Prueba FSI/dataSets5/training/GoldenRetriever/Golden Retriever_20.jpeg', 'r')
imshow(np.asarray(pil_im))

"""## Primer modelo"""

# DATA SOURCE --------------------------------------------------
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import RMSprop
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
from keras.callbacks import EarlyStopping
import keras
from time import time


# DATA SOURCE --------------------------------------------------

image_size = (150, 150)
batch_size = 32
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    "/content/drive/My Drive/Prueba FSI/dataSets5//training",
    validation_split=0.1, #Porcentaje de validacion, cuando tenemos conjuntos de datos pequeños, tenemos que ponerlo pequeño. Para la nuestra debe de ser entre un 0.1-0.2
    labels='inferred',
    subset="training", #indicamos si es el conjunto de entrenamiento o el de validación, cuando lo delcaramos, hace el inverso del validation_splint, es decir, acabaría empleando el 80% del conjunto
    seed=1337, #este número es arbitrario, es para que se aleatorice lo que he explicado en el batch_size
    image_size=image_size,
    batch_size=batch_size, #esto se explica en teoría, son para poner el tamaño que tienen los diferentes bloques de datos, por lo que enteindo, se aleatoriza el conjunto de datos para que no tenga muestras de una sola clase en un único bloque de datos
    label_mode='categorical' #si son dos únicas clases, se pone binary, si son varias, categorical
   
)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    "/content/drive/My Drive/Prueba FSI/dataSets5/validation",
    labels='inferred',
    validation_split=0.2,
    subset="validation",
    seed=1337,
    image_size=image_size,
    batch_size=batch_size,
    label_mode='categorical'
)

train_ds = train_ds.prefetch(buffer_size=32)
val_ds = val_ds.prefetch(buffer_size=32)

"""# Nueva sección"""

# MODEL --------------------------------------------------

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Dense, Rescaling, Flatten
from tensorflow.keras.callbacks import EarlyStopping

model = keras.Sequential()
model.add(Rescaling(scale=(1./127.5),#el 127.5 "rescala" para que el rango de valores de las matrices sea [0:2] 
                    offset=-1, #le restamos a los valores 1, así el rango quedaría [-1:1]
                    input_shape=(150, 150, 3))) #el tamaño de las imagenes de entrada (ancho, alto y num de canales)
##Sustituir por arquitecturas diferentes
model.add(Conv2D(32, kernel_size=(3, 3), activation='relu')) #el primer valor representa el número de filtros creados, cada filtro crea una matriz con los valores creados por él. El kernel size representa el tamaño de nuestro filtro (el que va recorriendo la imagen (es decir, el tensor), recorre en profundidad de forma simutanea), se puede cambiar. Valores recomendados: 1,1-5,5. Sobre las 32 matrices que han creado los filtros, aplicamos el relu ese
model.add(MaxPooling2D(pool_size=(2, 2))) #mitiga lo del sobreajuste, modifica el tamaño de las matrices del filtro para dificultar a la red que memorice patrones muy definidos, "maxpooling" 
model.add(Conv2D(64, (3, 3), activation='relu'))#hacemos otra capa, las 32 matrices creadas anteriormente hacen de entrada para estos 64
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))#porcentaje de desconexion de neuronas con respecto a la capa anterior, es decir, neuronas que no van a ser tenidas en cuenta para la actualizacion de los pesos que tengamos. Valores que van desde un 10% al 50%

model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(256, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25)) 


#hasta aquí se puede tocar
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(8, activation='softmax'))#hace que todos los elementos del vector, sumados, den 1 (¿¿??) así conseguimos que para cada una de las distintas clases, tengamos una probabilidad, entre 0 y 1, que nos sirve para compararlo con la etiqueta real de las muestras

model.compile(loss=tf.keras.losses.categorical_crossentropy,
              optimizer=tf.keras.optimizers.Adam(1e-3),
              metrics=['accuracy'])

model.summary() #añadido por nosotros, te da una especie de resumen de toda la movida

# TRAINING --------------------------------------------------

epochs = 200

es = EarlyStopping(monitor='val_accuracy', mode='max', verbose=1, patience=10, restore_best_weights=True)

h = model.fit(
        train_ds,
        epochs=epochs, 
        validation_data=val_ds,
        callbacks = [es]
)

import matplotlib.pyplot as plt

plt.plot(h.history['accuracy'])
plt.plot(h.history['val_accuracy'])
plt.plot(h.history['loss'])
plt.title('Model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['training', 'validation','loss'], loc='upper right')
plt.show()

"""## Evaluación de los resultados"""

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

results = np.concatenate([(y, model.predict(x=x)) for x, y in val_ds], axis=1)

predictions = np.argmax(results[0], axis=1)
labels = np.argmax(results[1], axis=1)
names = np.array(["Beagle", "Boxer", "Doberman", "Golden Retriever", "Husky", "Pastor Aleman", "Perro Salchicha", "Pomeranian"])

cf_matrix = confusion_matrix(labels, predictions)

sns.heatmap(cf_matrix, annot=True, fmt="d", cmap="Blues", xticklabels=names, yticklabels=names)

print(classification_report(labels, predictions, digits = 4, target_names = names))

img = keras.preprocessing.image.load_img(
    '/content/drive/My Drive/Prueba FSI/dataSets5/training/GoldenRetriever/Golden Retriever_20.jpeg', target_size=image_size
)
img_array = keras.preprocessing.image.img_to_array(img)
img_array = tf.expand_dims(img_array, 0)  # Create batch axis

predictions = model.predict(img_array)
print(np.argmax(predictions[0]))