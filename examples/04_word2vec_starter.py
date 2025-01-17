""" The mo frills implementation of word2vec skip-gram model using NCE loss. 
Author: Chip Huyen
Prepared for the class CS 20SI: "TensorFlow for Deep Learning Research"
cs20si.stanford.edu
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector

from process_data import process_data

VOCAB_SIZE = 50000
BATCH_SIZE = 128
EMBED_SIZE = 128  # dimension of the word embedding vectors
SKIP_WINDOW = 1   # the context window
NUM_SAMPLED = 64  # Number of negative examples to sample.
LEARNING_RATE = 1.0
NUM_TRAIN_STEPS = 20000
SKIP_STEP = 100   # how many steps to skip before reporting the loss


def word2vec(batch_gen):
  """ Build the graph for word2vec model and train it """

  # Step 1: define the placeholders for input and output
  # center_words have to be int to work on embedding lookup
  with tf.name_scope('data'):
    center_words = tf.placeholder(shape=[None], dtype=tf.int32, name='center_words')
    target_words = tf.placeholder(shape=[None, SKIP_WINDOW], dtype=tf.int32, name='target_words')

  # Step 2: define weights. In word2vec, it's actually the weights that we care about
  # vocab size x embed size initialized to random uniform -1 to 1
  with tf.name_scope('embedding_matrix'):
    embed_matrix = tf.Variable(np.random.uniform(-1, 1, size=[VOCAB_SIZE, EMBED_SIZE]),
                               dtype=tf.float32,
                               name='embed_matrix')

  with tf.name_scope('nce'):
    # Step 3: define the inference
    # get the embed of input words using tf.nn.embedding_lookup
    embed = tf.nn.embedding_lookup(embed_matrix, center_words, name='embed')

    # Step 4: construct variables for NCE loss
    # tf.nn.nce_loss(weights, biases, labels, inputs, num_sampled, num_classes, ...)
    # nce_weight (vocab size x embed size), intialized to truncated_normal stddev=1.0 / (EMBED_SIZE ** 0.5)
    # bias: vocab size, initialized to 0
    nce_weights = tf.Variable(tf.truncated_normal([VOCAB_SIZE, EMBED_SIZE], stddev=1.0 / (EMBED_SIZE ** 0.5)),
                              dtype=tf.float32,
                              name='weights')
    nce_biases = tf.Variable(np.zeros([VOCAB_SIZE]), dtype=tf.float32, name='biases')

    # define loss function to be NCE loss function
    # tf.nn.nce_loss(weights, biases, labels, inputs, num_sampled, num_classes, ...)
    # need to get the mean across the batch
    # note: you should use embedding of center words for inputs, not center words themselves
    with tf.name_scope('loss'):
      loss = tf.reduce_mean(
        tf.nn.nce_loss(weights=nce_weights,
                       biases=nce_biases,
                       inputs=embed,
                       labels=target_words,
                       num_sampled=NUM_SAMPLED,
                       num_classes=VOCAB_SIZE)
      )

  # Step 5: define optimizer
  optimizer = tf.train.GradientDescentOptimizer(LEARNING_RATE).minimize(loss)

  with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    print('Start training')

    total_loss = 0.0  # we use this to calculate the average loss in the last SKIP_STEP steps
    writer = tf.summary.FileWriter('/tmp/word2vec/no_frills/', sess.graph)
    for index in range(NUM_TRAIN_STEPS):
      centers, targets = next(batch_gen)
      _, loss_batch = sess.run([optimizer, loss], feed_dict={center_words: centers, target_words: targets})

      total_loss += loss_batch
      if (index + 1) % SKIP_STEP == 0:
        print('Step %4d: avg_loss=%.5f' % (index, total_loss / SKIP_STEP))
        total_loss = 0.0
    writer.close()


def main():
  batch_gen = process_data(VOCAB_SIZE, BATCH_SIZE, SKIP_WINDOW)
  word2vec(batch_gen)


if __name__ == '__main__':
  main()
