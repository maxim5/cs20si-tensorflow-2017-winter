""" Starter code for logistic regression model to solve OCR task 
with MNIST in TensorFlow
MNIST dataset: yann.lecun.com/exdb/mnist/
Author: Chip Huyen
Prepared for the class CS 20SI: "TensorFlow for Deep Learning Research"
cs20si.stanford.edu
"""
from __future__ import print_function

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

import numpy as np
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import time

# Define parameters for the model
learning_rate = 0.01
batch_size = 128
n_epochs = 10

# Step 1: Read in data
# using TF Learn's built in function to load MNIST data to the folder data/mnist
mnist = input_data.read_data_sets('~/p/data/mnist-tf/', one_hot=True)

# Step 2: create placeholders for features and labels
# each image in the MNIST data is of shape 28*28 = 784
# therefore, each image is represented with a 1x784 tensor
# there are 10 classes for each image, corresponding to digits 0 - 9. 
# Features are of the type float, and labels are of the type int
x = tf.placeholder(dtype=tf.float32, shape=[None, 28*28], name='x')
y = tf.placeholder(dtype=tf.float32, shape=[None, 10], name='y')

# Step 3: create weights and bias
# weights and biases are initialized to 0
# shape of w depends on the dimension of X and Y so that Y = X * w + b
# shape of b depends on Y
w = tf.Variable(initial_value=np.random.standard_normal([28*28, 10]) * 0.01, dtype=tf.float32, name='w')
b = tf.Variable(initial_value=np.zeros([10]), dtype=tf.float32, name='b')

# Step 4: build model
# the model that returns the logits.
# this logits will be later passed through softmax layer
# to get the probability distribution of possible label of the image
logits = tf.matmul(x, w) + b

# Step 5: define loss function
# use cross entropy loss of the real labels with the softmax of logits
# use the method:
# tf.nn.softmax_cross_entropy_with_logits(logits, Y)
# then use tf.reduce_mean to get the mean loss of the batch
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=y))

# Step 6: define training op
# using gradient descent to minimize loss
optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(loss)

with tf.Session() as sess:
  start_time = time.time()
  sess.run(tf.global_variables_initializer())
  writer = tf.summary.FileWriter('/tmp/logistic-reg', graph=sess.graph)

  n_batches = int(mnist.train.num_examples / batch_size)
  for i in range(n_epochs):  # train the model n_epochs times
    total_loss = 0
    for j in range(n_batches):
      x_batch, y_batch = mnist.train.next_batch(batch_size)
      _, loss_batch = sess.run([optimizer, loss], feed_dict={x: x_batch, y: y_batch})
      total_loss += loss_batch
    print('Average loss epoch {0}: {1}'.format(i, total_loss / n_batches))
  print('Total time: {0} seconds'.format(time.time() - start_time))
  print('Optimization Finished!')  # should be around 0.35 after 25 epochs

  writer.close()

  # Test the model
  preds = tf.nn.softmax(logits)
  correct_preds = tf.equal(tf.argmax(preds, 1), tf.argmax(y, 1))
  accuracy = tf.reduce_sum(tf.cast(correct_preds, tf.float32))  # need numpy.count_nonzero(boolarr) :(

  n_batches = int(mnist.test.num_examples / batch_size)
  total_correct_preds = 0

  for i in range(n_batches):
    x_batch, y_batch = mnist.test.next_batch(batch_size)
    accuracy_batch = sess.run(accuracy, feed_dict={x: x_batch, y: y_batch})
    total_correct_preds += accuracy_batch

  print('Accuracy {0}'.format(total_correct_preds / mnist.test.num_examples))
