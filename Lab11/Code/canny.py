import cv2
import numpy as np


def rgb_to_grayscale(rgb_img):
    ratios = [0.114, 0.587, 0.299]
    result = np.zeros(rgb_img.shape[:-1], dtype="float32")
    for i in range(3):
        result += ratios[i] * rgb_img[:, :, i]
    result = result.astype("uint8")
    return result


def sobel(img):
    result = np.zeros_like(img)
    direction = np.zeros_like(img)
    width, height = img.shape
    for i in range(1, width-1):
        for j in range(1, height-1):
            s_x = (img[i+1][j-1]+2*img[i+1][j]+img[i+1][j+1]) - (img[i-1][j-1] + 2*img[i-1][j] + img[i-1][j+1])
            s_y = (img[i-1][j-1]+2*img[i][j-1]+img[i+1][j-1]) - (img[i-1][j+1] + 2*img[i][j+1] + img[i+1][j+1])
            result[i][j] = np.sqrt(s_x * s_x + s_y * s_y)
            direction[i][j] = np.arctan(s_y/(s_x+1e-5))
    result = result.astype("uint8")
    return result, direction


def cv_sobel(img):
    x = cv2.Sobel(img, cv2.CV_16S, 1, 0)
    y = cv2.Sobel(img, cv2.CV_16S, 0, 1)
    absX = cv2.convertScaleAbs(x)   # 转回uint8
    absY = cv2.convertScaleAbs(y)
    dst = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
    return dst


def get_gaussian_kernel(sigma=1):
    kernel = np.zeros((3, 3))
    for x in range(-1, 2):
        for y in range(-1, 2):
            kernel[1+x][1+y] = np.exp(-(x*x+y*y)/(2*sigma*sigma)) / (2*np.pi*sigma*sigma)
    kernel = kernel / np.sum(kernel)
    return kernel


def non_maximum_suppression(gradient, direction):
    result = np.zeros_like(gradient)
    width, height = gradient.shape
    for i in range(1, width-1):
        for j in range(1, height - 1):
            if -np.pi/4 < direction[i][j] < np.pi/4:
                x1, y1 = i + 1, j + np.tan(direction[i][j])
                x2, y2 = i - 1, j - np.tan(direction[i][j])
                temp1 = (y1 - int(y1))*gradient[x1][min(height-1, int(y1)+1)] + (int(y1) + 1 - y1)*gradient[x1][int(y1)]
                temp2 = (y2 - int(y2))*gradient[x2][min(height-1, int(y2)+1)] + (int(y2) + 1 - y2)*gradient[x2][int(y2)]
            else:
                x1, y1 = i + 1/np.tan(direction[i][j]), j + 1
                x2, y2 = i - 1/np.tan(direction[i][j]), j - 1
                temp1 = (x1 - int(x1))*gradient[min(width-1, int(x1)+1)][y1] + (int(x1) + 1 - x1)*gradient[int(x1)][y1]
                temp2 = (x2 - int(x2))*gradient[min(width-1, int(x2)+1)][y2] + (int(x2) + 1 - x2)*gradient[int(x2)][y2]
            if(gradient[i][j] >= temp1 and gradient[i][j] >= temp2):
                result[i][j] = gradient[i][j]
    return result


def double_threshold(img, low, high):
    result = np.zeros_like(img)
    width, height = img.shape
    for i in range(0, width):
        for j in range(0, height):
            result[i][j] = 254*(img[i][j] >= high) + 1*(img[i][j] >= low)
    return result


def track_edge(img):
    result = np.zeros_like(img)
    uncertain_points = list()
    width, height = img.shape
    for i in range(1, width-1):
        for j in range(1, height-1):
            if img[i][j] == 255:
                result[i][j] = 255
            elif img[i][j] == 1:
                result[i][j] = 0
                doubt = False
                for x in range(i-1, i+2):
                    for y in range(j-1, j+2):
                        if img[x][y] == 255:
                            result[i][j] = 255
                        elif img[x][y] == 1:
                            doubt = True
                if(result[i][j] == 0 and doubt):
                    uncertain_points.append((i, j))
    prev_len = 0
    while(prev_len != len(uncertain_points)):
        prev_len = len(uncertain_points)
        print(prev_len)
        still_uncertain = list()
        for point in uncertain_points:
            for x in range(point[0]-1, point[0]+2):
                for y in range(point[1]-1, point[1]+2):
                    if result[x][y] == 255:
                        result[point[0]][point[1]] = 255
            if result[point[0]][point[1]] == 0:
                still_uncertain.append(point)
        uncertain_points = still_uncertain
    return result


def canny(image_path):
    color_img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    img = rgb_to_grayscale(color_img)
    kernel = get_gaussian_kernel()
    gaussian_blur_img = cv2.filter2D(img, -1, kernel)
    sobel_img, sobel_direction = sobel(gaussian_blur_img)
    nms_img = non_maximum_suppression(sobel_img, sobel_direction)
    threshold_img = double_threshold(nms_img, 50, 100)
    final_result = track_edge(threshold_img)
    cv2.imshow("Color Image", color_img)
    # cv2.imshow("Grayscale", img)
    # cv2.imshow("Gaussian Blur", gaussian_blur_img)
    # cv2.imshow("Sobel", sobel_img)
    # cv2.imshow("After non maximum suppression", nms_img)
    cv2.imshow("After double threshold", threshold_img)
    cv2.imshow("Final result", final_result)
    cv2.imshow("OpenCV", cv2.Canny(img, 50, 100))
    # cv2.imshow("Sobel CV", cv_sobel(gaussian_blur_img))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    images_list = ["dataset/3.jpg", ]
    for image in images_list:
        canny(image)
