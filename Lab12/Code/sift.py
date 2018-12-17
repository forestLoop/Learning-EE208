import cv2
import numpy as np


def rgb_to_grayscale(rgb_img):
    ratios = [0.114, 0.587, 0.299]
    result = np.zeros(rgb_img.shape[:-1], dtype="float32")
    for i in range(3):
        result += ratios[i] * rgb_img[:, :, i]
    result = result.astype("uint8")
    return result


def compute_gradient(grayscale_image):
    img = grayscale_image.copy().astype("int32")
    gradient, direction = [np.zeros_like(img, dtype="float32"), ] * 2
    width, height = img.shape
    for i in range(width - 1):  # just ignore pixels on the edge
        for j in range(height - 1):
            d_x = img[i+1, j] - img[i-1, j]
            d_y = img[i, j+1] - img[i, j-1]
            gradient[i][j] = np.sqrt(d_x * d_x + d_y * d_y)
            direction[i][j] = np.arctan(d_y/(d_x + 1e-8))   # -pi/2 ~ pi/2
            if(d_x < 0):
                direction[i][j] += np.pi    # -pi/2 ~ 3pi/2
            if(direction[i][j] < 0):
                direction[i][j] += 2 * np.pi
            # assert direction[i][j] >= 0, "Something wrong!"
    return gradient, direction


def vote_for_direction(gradient_zone, direction_zone):
    potential_directions = np.zeros((36,))
    width, height = gradient_zone.shape
    for i in range(0, width):
        for j in range(0, height):
            d = int(direction_zone[i][j] // (np.pi/18))
            potential_directions[d] += gradient_zone[i][j]
    direction = (np.argmax(potential_directions) + 0.5) * np.pi / 18
    assert 0 <= direction <= 2*np.pi, direction
    return direction


def get_gradient(gradient, x, y):  # x,y might not be integers
    x_low, x_high = int(x), int(x)+1
    y_low, y_high = int(y), int(y)+1
    result = gradient[x_low][y_low] * (x_high - x) * (y_high - y)
    result += gradient[x_low][y_high] * (x_high - x)*(y-y_low)
    result += gradient[x_high][y_low] * (x-x_low) * (y_high - y)
    result += gradient[x_high][y_high] * (x-x_low) * (y - y_low)
    return result


def get_adjusted_direction(direction, main_direction, x, y):
    x_low, x_high = int(x), int(x)+1
    y_low, y_high = int(y), int(y)+1
    result = direction[x_low][y_low] * (x_high - x) * (y_high - y)
    result += direction[x_low][y_high] * (x_high - x)*(y-y_low)
    result += direction[x_high][y_low] * (x-x_low) * (y_high - y)
    result += direction[x_high][y_high] * (x-x_low) * (y - y_low)
    assert 0 <= result <= 2*np.pi, [x, y, direction[x_low][y_low], direction[x_low][y_high], direction[x_high][y_low], direction[x_high][y_high]]
    result -= main_direction
    if result < 0:
        result += 2*np.pi
    assert result >= 0, result
    return result


def extract_features(gradient, direction):  # both input size 16*16

    def compute_histogram(x, y):  # [x,x+3]*[y,y+3]
        bins = np.zeros((8,))
        for i in range(x, x+4):
            for j in range(y, y+4):
                d = int(direction[i][j] // (np.pi/4))
                bins[d] += gradient[i][j]
        return bins

    assert gradient.shape == (16, 16), "Invalid shape!"
    features = list()
    for i in range(0, 13, 4):
        for j in range(0, 13, 4):
            features.append(compute_histogram(i, j))
    features = np.array(features).reshape((-1,))
    features = features / np.sqrt(np.sum(features * features))
    return features


def get_descriptor(gradient, direction, x, y):
    width, height = gradient.shape
    x1, x2, y1, y2 = max(0, x-8), min(width, x+8), max(0, y-8), min(height, y+8)
    main_direction = vote_for_direction(gradient[x1:x2, y1:y2], direction[x1:x2, y1:y2])
    active_gradient, active_direction = [np.zeros((16, 16)), ] * 2
    for i in range(-8, 8):
        for j in range(-8, 8):
            new_x, new_y = x + i*np.cos(main_direction), y + j * np.sin(main_direction)
            new_x, new_y = min(width - 1.001, max(0, new_x)), min(height-1.001, max(0, new_y))
            active_gradient[8+i][8+j] = get_gradient(gradient, new_x, new_y)
            active_direction[8+i][8+j] = get_adjusted_direction(
                direction, main_direction, new_x, new_y)
    features = extract_features(active_gradient, active_direction)
    return features


def sift(image_path):
    img = cv2.imread(image_path)
    img = rgb_to_grayscale(img)
    shi_tomasi_corners = cv2.goodFeaturesToTrack(img, maxCorners=50, qualityLevel=0.01, minDistance=10)
    shi_tomasi_corners = shi_tomasi_corners.reshape((-1, 2)).astype("int32")    # reshape into (N,2)
    gradient, direction = compute_gradient(img)
    descriptors = list()
    for (x, y) in shi_tomasi_corners:
        # cv2.circle(img, (x, y), 5, (255, 0, 0))
        descriptors.append(get_descriptor(gradient, direction, x, y))
    descriptors = np.array(descriptors)
    return shi_tomasi_corners, descriptors


def sift_match(target_feature, feature, threshold):
    score = 0
    result = list()
    for i, descriptor in enumerate(target_feature[1]):
        max_j, max_similarity = 0, 0
        for j, x in enumerate(feature[1]):
            if np.dot(descriptor, x) >= max_similarity:
                max_j, max_similarity = j, np.dot(descriptor, x)
        if max_similarity >= threshold:
            score += 1
            feature[1][max_j] = np.zeros_like(feature[1][max_j])
            result.append((target_feature[0][i], feature[0][max_j]))
    return score, result


def merge(img1, img2):
    result = []
    img1 = cv2.imread(img1)
    img2 = cv2.imread(img2)
    # print(img1.shape, img2.shape)
    final_height = max(img1.shape[0], img2.shape[0])
    padding = int((final_height - img1.shape[0]) // 2)
    result.append(padding)
    result.append(padding)
    odd = 1 if padding * 2 != (final_height - img1.shape[0]) else 0
    img1 = cv2.copyMakeBorder(img1, padding, padding+odd, padding, padding, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    # print(img1.shape)
    padding = int((final_height - img2.shape[0]) // 2)
    result.append(padding+img1.shape[1])
    result.append(padding)
    odd = 1 if padding * 2 != (final_height - img2.shape[0]) else 0
    img2 = cv2.copyMakeBorder(img2, padding, padding+odd, padding, padding, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    # print(img2.shape)
    result.append(np.hstack((img1, img2)))
    return result


def link_matched_points(merged_img, x1, y1, x2, y2, match_result):
    new_img = merged_img.copy()
    # print(x1, y1, x2, y2)
    cv2.circle(new_img, (x1, y1), 5, [0, 0, 255], -1)
    cv2.circle(new_img, (x2, y2), 5, [0, 0, 255], -1)
    for pair in match_result:
        cv2.line(new_img, (int(x1+pair[0][0]), int(y1+pair[0][1])), (int(x2+pair[1][0]), int(y2+pair[1][1])), [255, 0, 0], 2)
    return new_img


if __name__ == '__main__':
    target_image = "target.jpg"
    possible_images = ["dataset/1.jpg", "dataset/2.jpg", "dataset/3.jpg",  "dataset/4.jpg", "dataset/5.jpg"]
    target_feature = sift(target_image)
    candidates_feature = list()
    match_result = list()
    best_match = 0
    for image in possible_images:
        candidates_feature.append(sift(image))
        match_result.append(sift_match(target_feature, candidates_feature[-1], 0.7))
    for i, img in enumerate(possible_images):
        print(img, match_result[i][0])
        if(match_result[i][0] > match_result[best_match][0]):
            best_match = i
    print("The best match is: ", possible_images[best_match])
    x1, y1, x2, y2, merged_img = merge(target_image, possible_images[best_match])
    final_img = link_matched_points(merged_img, x1, y1, x2, y2, match_result[best_match][1])
    cv2.imshow("Test", final_img)
    cv2.waitKey(0)
