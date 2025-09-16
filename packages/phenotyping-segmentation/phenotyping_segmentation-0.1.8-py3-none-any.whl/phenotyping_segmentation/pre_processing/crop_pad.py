import math
import os

import cv2

from phenotyping_segmentation.utils.imglist import get_imglist


def add_0padding_crop(
    patch_size,
    overlap_size,
    image_name,
    crop_path,
):
    """Add zero padding to the size of image and crop it for patch.

    Args:
        patch_size: expected patch size of deep learning model.
        overlap_size: the expected overlap/border of two adjacent images.
        image_name: the original image name with path.
        crop_path: the path to save the cropped images.

    Returns
        Add padding of current image and save padding images.
    """
    color = [0, 0, 0]  # add zero padding
    name_crop_paths = []

    im = cv2.imread(image_name)

    # get image height and width
    H, W = im.shape[:2]

    stride = patch_size - overlap_size

    # number of patches along each dimension
    n_h = math.ceil((H - overlap_size) / stride)
    n_w = math.ceil((W - overlap_size) / stride)

    # required padded size
    pad_h = stride * (n_h - 1) + patch_size
    pad_w = stride * (n_w - 1) + patch_size

    extra_h = pad_h - H
    extra_w = pad_w - W

    # split padding equally on both sides
    top = extra_h // 2
    bottom = extra_h - top
    left = extra_w // 2
    right = extra_w - left

    im_pad = cv2.copyMakeBorder(
        im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )

    idx = 0
    for i in range(n_h):
        for j in range(n_w):
            idx += 1
            crop_name = str(os.path.splitext(image_name)[0]) + "_" + str(idx) + ".png"
            top = i * (patch_size - overlap_size)
            left = j * (patch_size - overlap_size)
            im_crop = im_pad[top : top + patch_size, left : left + patch_size, :]
            name_crop = os.path.join(crop_path, os.path.basename(crop_name)).replace(
                "\\", "/"
            )

            base_fodler = os.path.dirname(name_crop)
            if not os.path.exists(base_fodler):
                os.makedirs(base_fodler)

            cv2.imwrite(name_crop, im_crop)
            name_crop_paths.append(name_crop)
    return name_crop_paths


def add_0padding_crop_df(patch_size, overlap_size, scans_df, image_replace):
    """Add zero padding to the size of image and crop it for patch.

    Args:
        patch_size: expected patch size of deep learning model.
        overlap_size: the expected overlap/border of two adjacent images.
        scans_df: dataframe of scans with a column of plant scan path (scan_path);
        image_replace: the string to replace in scan_path to get the correct path for cropping.

    Returns
        Add padding of current image and save padding images.
    """
    color = [0, 0, 0]  # add zero padding
    save_paths = []

    for i in range(len(scans_df)):
        scan_path = scans_df["scan_path"][i].replace("/images/", image_replace)
        # create save crop folders, same architecture as scans
        crop_path = scan_path.replace(image_replace, "/crop/")
        if not os.path.exists(crop_path):
            os.makedirs(crop_path)
        # get the images
        image_list = get_imglist(scan_path)

        # Loop through each image in the scan path
        for name in image_list:
            image_name = os.path.join(scan_path, name).replace("\\", "/")
            im = cv2.imread(image_name)
            # skip if not loaded
            if im is None:
                print(f"⚠️ Skipping unreadable image: {image_name}")
                continue
            name_crop_paths = add_0padding_crop(
                patch_size,
                overlap_size,
                image_name,
                crop_path,
            )
        save_paths.append(crop_path)
    return save_paths
