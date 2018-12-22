import numpy as np
import cv2
import os
import time
import functools


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        tick = time.time()
        func(*args, **kw)
        tock = time.time()
        print("Time: {:.4f}s".format(tock-tick))
    return wrapper


def orb_feature(img_path, max_kp):
    img = cv2.imread(img_path)
    detector = cv2.ORB_create(max_kp)  # limit the number of keypoints
    kp, des = detector.detectAndCompute(img, None)
    return des


def compute_LSH(feature, I):
    feature = feature.reshape((-1,))
    # print(feature.shape)    # N*32 , 0 <= x <= 255
    d, C = feature.shape[0], 255
    result = list()
    for I_i in I:
        i = int((I_i - 1)//C + 1)  # i = 1,2,...,d
        x_i = feature[i - 1]
        if I_i <= x_i + C * (i - 1):
            result.append(1)
        else:
            result.append(0)
    result = np.array(result)
    return result


def compute_hash(vector, mod):
    result = 0
    for i, x in enumerate(vector):
        result = (result + (i + 1) * x) % mod
    return result


def LSH(img_path):
    I = np.linspace(0, 50*32*255, 100, dtype="int32")
    # print(I.shape)
    feature = orb_feature(img_path, 100)
    LSH = compute_LSH(feature, I)
    # print(LSH.shape)  # should be (1000,)
    hash_bucket = compute_hash(LSH, 100)
    # print(hash_bucket)
    return hash_bucket, feature


def LSH_match(target_img, dataset_folder):
    # preprocessing...
    target_hash, target_feature = LSH(target_img)
    dataset_hash = list()
    print("The Hash value of the target image:", target_hash)
    for dir_path, dir_names, file_names in os.walk(dataset_folder):
        for file_name in file_names:
            img_path = os.path.join(dir_path, file_name)
            img_hash, img_feature = LSH(img_path)
            dataset_hash.append((img_path, img_hash, img_feature))
    # searching...
    tick = time.time()
    possible_result = list()
    for img_path, img_hash, img_feature in dataset_hash:
        if(img_hash == target_hash):
            possible_result.append((img_path, img_hash, img_feature))
    if not possible_result:
        print("No image matched!")
        return
    best_match = None
    for img_path, img_hash, img_feature in possible_result:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(target_feature, img_feature)
        # print(img_path, len(matches))
        if not best_match or len(matches) > best_match[1]:
            best_match = (img_path, len(matches))
    print("The best match is:", best_match[0])
    tock = time.time()
    print("LSH search: {:.6f}s".format(tock - tick))


def NN_match(target_img, dataset_folder):
    # preprocessing...
    target_feature = orb_feature(target_img, 100)
    dataset_feature = list()
    for dir_path, dir_names, file_names in os.walk(dataset_folder):
        for file_name in file_names:
            img_path = os.path.join(dir_path, file_name)
            img_feature = orb_feature(img_path, 100)
            dataset_feature.append((img_path, img_feature))
    # searching...
    tick = time.time()
    best_match = None
    for img_path, img_feature in dataset_feature:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(target_feature, img_feature)
        # print(img_path, len(matches))
        if not best_match or len(matches) > best_match[1]:
            best_match = (img_path, len(matches))
    print("The best match is:", best_match[0])
    tock = time.time()
    print("NN search: {:.6f}s".format(tock - tick))


if __name__ == '__main__':
    target_img = "target.jpg"
    dataset_folder = "dataset"
    LSH_match(target_img, dataset_folder)
    NN_match(target_img, dataset_folder)
