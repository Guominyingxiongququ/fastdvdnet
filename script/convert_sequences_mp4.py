"""Convert image sequences in dirs found under `datab_root` into high quality mp4 video files.
"""
# import argparse
# from models import OutputCvBlock
import os
import subprocess
import cv2
import numpy as np
from numpy.lib.function_base import extract

default_codec = "h264"
default_crf = "18"
default_keyint = "4"

def convert_scenes(datab_root, out_root, codec, crf, keyint, quiet):
	# If not provided, set values by default
	if not codec:
		codec = default_codec
	assert codec in ['h264', 'hevc'], '--codec must be one of h264 or hevc'

	if not crf:
		crf = default_crf

	if not keyint:
		keyint = default_keyint

	# Codec options
	codec_args = ["-preset", "slow"]
	if codec == 'h264':
		codec_args = ["-c:v", "libx264", "-g", keyint,
					  "-profile:v", "high"]
	elif codec == 'hevc' or codec == 'h265':
		codec_args = ["-c:v", "libx265", "-x265-params",
					  "keyint=%s:no-open-gop=1" % (keyint)]
	else:
		raise ValueError("Unknown codec")

	# Quiet mode
	if quiet:
		cmdout = subprocess.DEVNULL
	else:
		cmdout = None

	# Output dir
	if not os.path.isdir(out_root):
		os.makedirs(out_root)
	print('Writing sequences to {}'.format(out_root))

	def convert(in_path, out_path):
		cmd = ["ffmpeg", "-y", "-i", in_path]
		cmd += codec_args
		cmd += ["-crf", crf, "-an", out_path]
		print("Running:", " ".join(cmd))
		subprocess.run(cmd, stdout=cmdout, stderr=cmdout)

	# Convert sequences in subdirs under datab_root
	for subdir in os.listdir(datab_root):
		in_path = os.path.join(datab_root, subdir, '%5d.jpg')
		out_path = os.path.join(out_root, subdir + '.mp4')
		convert(in_path, out_path)


def extract_frames(datab_root, out_root, quiet):
    file_list = os.listdir(datab_root)
    file_path_list = []
    for file_name in file_list:
        if file_name.endswith(".mp4"):
            file_path_list.append(file_name)
    file_path_list = file_path_list[:10]
    print(file_path_list)
    # Quiet mode
    if quiet:
        cmdout = subprocess.DEVNULL
    else:
        cmdout = None
    for file_name in file_path_list:
        in_path = os.path.join(datab_root, file_name)
        cmd = ["ffmpeg", "-i", in_path]
        output_dir = os.path.join(out_root, file_name[:-4])
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        output_path = os.path.join(out_root, "{}/{}%4d.png".format(file_name[:-4], file_name[:-4]))
        cmd += [output_path, "-hide_banner"]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, stdout=cmdout, stderr=cmdout)

def gen_noise_frames(out_root, out_noise_root):
    for i in range(50, 70, 10):
        delta_folder = os.path.join(out_noise_root, str(i))
        if not os.path.isdir(delta_folder):
            os.mkdir(delta_folder)
    folder_list = os.listdir(out_root)
    for i in range(50, 70, 10):
        for folder_name in folder_list:
            full_folder_path = os.path.join(out_root, folder_name)
            if os.path.isdir(full_folder_path):
            # noise_folder_path = os.path.join(out_noise_root, folder_name)
            # os.mkdir(noise_folder_path)
                delta_folder = os.path.join(out_noise_root, str(i))
                output_folder = os.path.join(delta_folder, folder_name)
                if not os.path.isdir(output_folder):
                    os.mkdir(output_folder)
                input_file_list = os.listdir(full_folder_path)
                for file_name in input_file_list:
                    input_file_path = os.path.join(full_folder_path, file_name)
                    output_file_path = os.path.join(output_folder, file_name)
                    input_img = cv2.imread(input_file_path)
                    noise = np.random.normal(0, i, size=input_img.shape)
                    output_img = np.clip(input_img + noise, 0, a_max=255)
                    cv2.imwrite(output_file_path, output_img)

if __name__=="__main__":
    datab_root = "/home/xinyuan/data/mp4"
    out_root = "/home/xinyuan/data/output"
    out_noise_root = "/home/xinyuan/data/noise"
    quite = True
    #extract_frames(datab_root, out_root, quite)
    gen_noise_frames(out_root, out_noise_root)