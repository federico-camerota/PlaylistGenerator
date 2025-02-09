# coding=utf-8

import numpy as np
import pgutils as pg
import pgmath as pm
import algorithm as al
import os
import time
from numpy import savetxt


def latent_representation(output_file, root_dir, dimension, lam, n_iter, tau, r=None):
    with open(os.path.join(root_dir, "train.txt"), "r") as f:
        train_data = f.readlines()
    train_dataset = pg.data_to_list(train_data[2:])

    # train_dataset = train_dataset[:400]
    # songs = 9775
    songs = 3168

    tic = time.perf_counter()
    jump_matrix = pg.transition_count(songs, train_dataset)
    toc = time.perf_counter()
    print("Jump matrix:", toc - tic)

    num_transition = np.sum(jump_matrix)
    n_landmarks = 50

    params = pm.AlgParams(lam, tau, num_transition, dimension, n_iter, r, n_landmarks)

    tic = time.perf_counter()
    X = al.single_point_algorithm(songs, jump_matrix, params)
    toc = time.perf_counter()

    savetxt(output_file, X, delimiter=' ')
    print(f"total time {toc - tic} seconds")


def tran_matrix(file_path):
    x = np.genfromtxt(file_path, delimiter=' ')
    x_dim, y_dim = x.shape
    chunks = np.zeros((x_dim, x_dim, y_dim))
    d2 = pm.Distances.delta(pm.Distances.difference_matrix(x, chunks))
    prob_matrix = np.exp(-d2) / pm.Distances.zeta(d2)
    cum_sum = np.sum(prob_matrix, axis=1)
    prob_matrix = prob_matrix / cum_sum[:, np.newaxis]

    return prob_matrix


def save_prob_matrix(file_path, prob_matrix):
    savetxt(file_path, prob_matrix, delimiter=',')


def evaluation_loss(root_dir, songs, prob_matrix):
    with open(os.path.join(root_dir, 'test.txt')) as f:
        test_data = f.readlines()

    test_dataset = pg.data_to_list(test_data[2:])
    n_test = np.sum(pg.transition_count(songs, test_dataset))

    evaluation = pg.log_like(test_dataset, prob_matrix) / n_test
    print('loss on test set ', evaluation)
