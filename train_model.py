import cv2
from keras.applications.vgg16 import VGG16, preprocess_input
import json
from keras.models import load_model, Model
from keras import optimizers
import os
import matplotlib.pyplot as plt
from keras.optimizers import RMSprop
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, GlobalAveragePooling2D
from keras.layers import Conv2D, MaxPooling2D, ZeroPadding2D, BatchNormalization
import numpy as np
from keras.preprocessing.image import ImageDataGenerator


# Load pre-trained VGG16 model
model = VGG16(weights='imagenet', include_top=False, input_shape = (224, 224, 3))
# freeze layers 
for layer in model.layers:
    layer.trainable = False
    
for (i,layer) in enumerate(model.layers):
    print(str(i) + " "+ layer.__class__.__name__, layer.trainable)

def lw(bottom_model, num_classes):
    """creates the top layers to be placed ontop of Original VGG16 bottom layers"""
    top_model = bottom_model.output
    top_model = GlobalAveragePooling2D()(top_model)
    top_model = Dense(1024,activation='relu')(top_model)
    top_model = Dropout(0.2)(top_model) 
    top_model = Dense(1024,activation='relu')(top_model)
    top_model = Dropout(0.3)(top_model)
    top_model = Dense(num_classes,activation='softmax')(top_model)
    return top_model 
    


train_data_dir = './images/train_images'
test_data_dir = './images/validate_images'
# Set the numbers of classes ( total images folders)
num_classes = len(os.listdir(train_data_dir))

FC_Head = lw(model, num_classes)
vgg = Model(inputs = model.input, outputs = FC_Head)
print(vgg.summary())

batch_size = 4
epochs = 50
# Data augmentation
train_datagen = ImageDataGenerator(
      rescale=1./255,
      rotation_range=30,
      width_shift_range=0.2,
      height_shift_range=0.2,
      horizontal_flip=True,
      fill_mode='nearest')

validate_dategen = ImageDataGenerator(rescale =1./255)

train_generator = train_datagen.flow_from_directory(
        train_data_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical')

validation_generator = validate_dategen.flow_from_directory(
        test_data_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical')

checkpoint = ModelCheckpoint("face_recognition_xxx.h5",
                             monitor="val_loss",
                             mode="min",
                             save_best_only = True,
                             verbose=1)

earlystop = EarlyStopping(monitor = 'val_loss', 
                          min_delta = 0, 
                          patience = 5,
                          verbose = 1,
                          restore_best_weights = True)

callbacks = [ earlystop, checkpoint]

vgg.compile(loss = 'categorical_crossentropy',
              optimizer = RMSprop(learning_rate = 0.0001),
              metrics = ['accuracy'])

history = vgg.fit(
    train_generator,
    steps_per_epoch=len(train_generator),
    #steps_per_epoch = nb_train_samples // batch_size,
    epochs = epochs,
    callbacks=callbacks,
    validation_data = validation_generator,
    validation_steps = len(validation_generator) // batch_size)

vgg.save("face_recognition_xxx.h5")

train_label_names = os.listdir(train_data_dir)
validate_label_names = os.listdir(test_data_dir)
print(train_label_names)
print(validate_label_names)

accuracy = history.history['accuracy']
loss = history.history['loss']
val_accuracy = history.history['val_accuracy']
val_loss = history.history['val_loss']
epoch = list(range(1, len(accuracy) + 1 ))
print('accuracy', ' ' , accuracy)
print('loss', ' ', loss)
print('val accuracy', ' ' , val_accuracy)
print('val loss', ' ', val_loss)
print('total epoch', ' ' , epoch)
print('history' , history)

# Plot trained model accuracy and loss
plt.plot(epoch, accuracy, label='Training Accuracy ')
plt.plot(epoch, val_accuracy, label='Validation Accuracy')
plt.title('Training Accuracy and Validation Accuracy of Model')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
#plt.axvline(x=8, color='r', linestyle='--', label='Restore Model from Best Epoch : 8')
plt.show()

# Plot trained model accuracy and loss
plt.plot(epoch, loss,  label='Training Loss')
plt.plot(epoch, val_loss, label='Validation Loss')
plt.title('Training Loss and Validation Loss of Model')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
#plt.axvline(x=8, color='r', linestyle='--', label='Restore Model from Best Epoch : 8')
plt.show()


from sklearn.metrics import confusion_matrix

# Generate predictions for the validation dataset
validation_steps = len(validation_generator)
validation_predictions = vgg.predict(validation_generator, steps=validation_steps)

# Convert the predictions to class labels
predicted_classes = np.argmax(validation_predictions, axis=1)

# Get the true labels for the validation dataset
true_classes = validation_generator.classes
print('true classes' , true_classes)
print('predicted classes', predicted_classes)
# Calculate the confusion matrix
confusion = confusion_matrix(true_classes, predicted_classes)

# Extract TP, TN, FP, and FN
TP = confusion[1, 1]
TN = confusion[0, 0]
FP = confusion[0, 1]
FN = confusion[1, 0]

# Confusion matrix
confusion = confusion_matrix(true_classes, predicted_classes)
print(confusion)
accuracies = []
for i in range(confusion.shape[0]):
    tp = confusion[i, i]
    total_samples = np.sum(confusion[i, :])
    accuracy = tp / total_samples
    accuracies.append(accuracy)

# Print accuracy for each label
for label, accuracy in enumerate(accuracies):
    print(f"Label {label}: Accuracy = {accuracy:.2f}")
# Calculate overall accuracy
correct_predictions = sum(1 for true, prediction in zip(true_classes, predicted_classes) if true == prediction)
total_predictions = len(true_classes)
overall_accuracy = correct_predictions / total_predictions
print(f"Overall Model Accuracy: {overall_accuracy:.2f}")

