from os import listdir
from os.path import join, exists

import numpy as np
import torch.utils.data as data
import torchvision.transforms as transforms
from PIL import Image
from skimage import feature, color, util

from pix2pix_temporal.util import is_image_file, load_img


class DatasetFromFolder(data.Dataset):
    def __init__(self, image_dir, use_line_art=False):
        super(DatasetFromFolder, self).__init__()
        self.use_line_art = use_line_art
        self.photo_path = image_dir
        self.image_filenames = [x for x in listdir(self.photo_path) if is_image_file(x)]
        transform_list = [transforms.ToTensor()]
        self.transform = transforms.Compose(transform_list)

    def __getitem__(self, index):
        # Load Image
        frame_num = None
        try:
            target_path = join(self.photo_path, self.image_filenames[index])
            frame_num = target_path.split("e")[-1]
            frame_num = int(frame_num.split(".")[0]) - 1
            frame_prev = self.get_prev(frame_num)  # will be either black or colored
            target = load_img(target_path)
            input_image = color.rgb2gray(target)
            if self.use_line_art:
                # needed for lineart only, not grayscale
                input_image = feature.canny(input_image, sigma=1)
                input_image = util.invert(input_image)
            input_image = Image.fromarray(np.uint8(input_image) * 255)
            # input = Image.fromarray(input)
            frame_prev = self.transform(frame_prev)
            target = self.transform(target)
            input_image = self.transform(input_image)

            return input_image, target, frame_prev
        except Exception as e:
            print("Something went wrong frame:" + str(frame_num))
            print(e)
            return self[0]

    def __len__(self):
        return len(self.image_filenames)

    def get_prev(self, num):
        if not exists(join(self.photo_path, "frame" + str(num) + ".jpg")):
            initial_prev_frame = Image.new("RGB", [256, 256])
            return initial_prev_frame
        else:
            # define rnd num generator and if statement <0.5 take black or color
            rnd = np.random.uniform(0, 1)
            if rnd <= 0.5:
                prev = load_img(join(self.photo_path, "frame" + str(num) + ".jpg"))
            else:
                prev = Image.new("RGB", [256, 256])

            return prev
            # frame_1 = join(self.photo_path,"frame"+str(frame_num)+".jpg")
