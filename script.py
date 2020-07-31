import argparse
import cv2
import numpy as np

args = argparse.ArgumentParser()
args.add_argument("path", help="path to the file being cropped")
args.add_argument("outpath", help="path of the cropped file")
transformGroup = args.add_argument_group("Transformations")
transformGroup.add_argument("--crop", "-c", help="x-separated integer resolution to crop video to (i.e. 1920x1080)",
                            required=False)
args.add_argument("--codec", help="4 character code of the codec used to compress the frames",
                  required=False, default='mp4v')
transformGroup.add_argument("--rescale", "-r", help="x-separated integer to scale output video to (i.e. 1280x720)",
                            required=False)
transformGroup.add_argument("--framerange", "-f", help="Colon-separated frame numbers to select. -1 can be used for "
                                                       "the second frame to run until the end of the video.",
                            required=False)
args = args.parse_args()

# Load video file and define relevant variables
cap = cv2.VideoCapture(args.path)
totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
frameRate = cap.get(cv2.CAP_PROP_FPS)
frameWidth, frameHeight = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Define resolution variables
cropRes = [int(i) for i in args.crop.split("x")] if args.crop else [frameWidth, frameHeight]
outRes = [int(i) for i in args.rescale.split("x")] if args.rescale else cropRes
if cropRes[0] > frameWidth or cropRes[1] > frameHeight:  # Make sure the crop settings are valid
    print("Crop can't be larger than frame!")
    exit(1)

# Parse frameRange argument
frameRange = [int(i) for i in args.framerange.split(":")] if args.framerange else [0, totalFrames]
frameRange[1] = totalFrames if frameRange[1] == -1 else frameRange[1]
totalFrames = frameRange[1] - frameRange[0]

# Create output file
fourCC = cv2.VideoWriter_fourcc(*args.codec)
out = cv2.VideoWriter(args.outpath, fourCC, frameRate, (outRes[0], outRes[1]))

# Main loop
i = 0
while True:
    # Read frame
    ret, frame = cap.read()
    if frame is None:
        exit(0)

    # Progress meter
    i += 1
    if args.framerange:
        if i < frameRange[0]:
            continue
        if i > frameRange[1]:
            exit(0)
    if i > frameRange[0]:
        print(f"{np.round((i / frameRange[1]) * 100, 2)}%", end="\r")

    # Cut and scale frame
    outFrame = frame[0:cropRes[1], 0:cropRes[0]] if args.crop else frame
    if cropRes != outRes:
        outFrame = cv2.resize(outFrame, (outRes[0], outRes[1]), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)

    # Write frame to file
    out.write(outFrame)
