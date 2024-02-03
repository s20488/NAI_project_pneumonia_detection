"""
Model VGG19

Potężny model głębokiego uczenia zaprojektowany dla zadań klasyfikacji obrazów. Wykorzystuje architekturę VGG19,
która jest głęboką siecią konwolucyjną. Model ten jest wstępnie wytrenowany na zbiorze danych ImageNet,
co umożliwia mu skuteczną klasyfikację obrazów w różnych scenariuszach.

"""

import json
import tensorflow as tf
from evaluation.metrics import MyF1Score
from mpld3._display import NumpyEncoder  # Import NumpyEncoder do obsługi serializacji obiektów NumPy w JSON
from tensorflow.keras.metrics import Precision, Recall

from models.callback.test_callback import TestCallback


def train_model_vgg19(train, validation, test):
    """
    Szkolenie modelu VGG19 do klasyfikacji obrazów.

    Parametry:
    - train: Zbiór danych treningowych.
    - validation: Zbiór danych do walidacji.
    - test: Zbiór danych testowych.

    Zwraca:
    - Wytrenowany model na podanych danych.
    """

    # Wczytanie wstępnie wytrenowanego modelu VGG19
    vgg19_model = tf.keras.applications.VGG19(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3)
    )

    # Zamrożenie wszystkich warstw w wstępnie wytrenowanym modelu
    for layer in vgg19_model.layers:
        layer.trainable = False

    # Dodanie warstw do transfer learning
    x = vgg19_model.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(128, activation='relu')(x)

    predictions = tf.keras.layers.Dense(1, activation='sigmoid')(x)

    # Stworzenie ostatecznego modelu do treningu
    model = tf.keras.Model(inputs=vgg19_model.input, outputs=predictions)

    # Konfiguracja funkcji zwrotnej dla wczesnego zatrzymywania i redukcji learning rate
    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)
    lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', patience=8)

    # Kompilacja modelu
    model.compile(loss='binary_crossentropy', optimizer='adam',
                  metrics=[Precision(name='precision'), Recall(name='recall'), MyF1Score()])

    # Szkolenie modelu
    history = model.fit(train, epochs=30,
                        validation_data=validation,
                        steps_per_epoch=100,
                        callbacks=[early_stopping, lr, TestCallback(test)],
                        batch_size=32)

    # Zapisanie wytrenowanego modelu i historii treningu
    model.save('save_models/model_vgg19.h5')

    with open('save_models/model_vgg19.json', 'w') as f:
        json.dump(history.history, f, cls=NumpyEncoder)