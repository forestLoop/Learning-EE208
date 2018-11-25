import cv2
import numpy as np
import matplotlib.pyplot as plt


def color_hist(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    hist = np.sum(img.reshape(-1, 3), axis=0)
    hist = hist / np.sum(hist)
    plt.bar(["Blue", "Green", "Red"], hist, color=["blue", "green", "red"])
    plt.title("Color Histogram of {}".format(image_path))
    plt.show()


def grayscale_hist(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    hist = np.bincount(img.ravel(), minlength=256)
    hist = hist / np.sum(hist)
    plt.bar(range(0, 256), hist, width=1.0)
    plt.title("Grayscale Histogram of {}".format(image_path))
    plt.show()


def gradient_hist(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # print(img.dtype)
    img = img.astype("int32")
    Ix = (img[:, 2:] - img[:, :-2])[1:-1, :]
    Iy = (img[2:, :] - img[:-2, :])[:, 1:-1]
    M = np.sqrt(Ix * Ix + Iy * Iy).astype("int32")
    hist = np.bincount(M.ravel(), minlength=361)
    hist = hist / np.sum(hist)
    plt.bar(range(0, 361), hist, width=1.0)
    # plt.hist(M.ravel(), 361, [0, 361])
    plt.title("Gradient Histogram of {}".format(image_path))
    plt.show()


if __name__ == '__main__':
    images_list = ["img1.png", "img2.png"]
    histograms_list = [color_hist, grayscale_hist, gradient_hist]
    for image in images_list:
        for histogram in histograms_list:
            histogram(image)
