import argparse

import cv2
import ffmpeg
import numpy as np

args = argparse.ArgumentParser()
args.add_argument("path", help="path to the file being cropped")
args.add_argument("outpath", help="path of the cropped file")
transformGroup = args.add_argument_group("Transformations")
transformGroup.add_argument("--slice", "-s", help="colon-separated comma-separated integer slice",
                            required=False)
transformGroup.add_argument("--rescale", "-r", help="x-separated integer to scale output video to",
                            required=False)
cutGroup = args.add_mutually_exclusive_group()
cutGroup.add_argument("--framerange", "-f", help="Colon-separated frame numbers to select. -1 can be used for "
                                                 "the second frame to run until the end of the video.", required=False)
cutGroup.add_argument("--timerange", help="Colon-separated numbers (in seconds) to select. -1 can be used to "
                                          "run until the end of the video.", required=False)
args.add_argument("--swaprb", help="Swap red and blue channels for bgr recordings", required=False, action="store_true")
args = args.parse_args()

# Load video file and define relevant variables
cap = cv2.VideoCapture(args.path)
totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frameRate = int(cap.get(cv2.CAP_PROP_FPS))
frameWidth, frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define resolution variables
if args.slice:
    sliceArea = [np.array(i.split(",")).astype(np.int) for i in [pair for pair in args.slice.split(":")]]
else:
    sliceArea = [[0, frameWidth], [0, frameHeight]]  # No slice was defined, so the crop is the whole frame
sliceArea = np.array(sliceArea)  # Convert strings in array to integers

# Is this being scaled? If not, output resolution is the frame size
outRes = [int(i) for i in args.rescale.split("x")] if args.rescale else [sliceArea[1][0], sliceArea[1][1]]
# Parse frameRange argument
if args.framerange:
    # Split colon-separated frames
    frameRange = [int(i) for i in args.framerange.split(":")]
elif args.timerange:
    # "Why in the everloving grace of His Holiness Fuck are you casting to float then back to int when you multiply"
    # - github.com/wundrweapon
    #
    # This is the same as frameRange, but because the unit is in seconds it needs to be multiplied by the framerate. The
    # cast to float and then to int is because the argument is initially provided as a string, but can't be safely cast
    # to int until after it is converted into a frame number. Does it suck? Yes. Will I fix it? Probably not.
    frameRange = [int(float(i)*frameRate) for i in args.timerange.split(":")]
else:
    # No cut was given, so process the entire file
    frameRange = [0, totalFrames]

frameRange[1] = totalFrames if frameRange[1] < 0 else frameRange[1]
totalFrames = frameRange[1] - frameRange[0]

# Validity Checks
if frameRange[1] < frameRange[0]:
    print("ERROR: Cut can't begin after it ends!")
    exit(1)

# Create output file
process = (
    ffmpeg
        .input('pipe:', format='rawvideo', s='{}x{}'.format(outRes[0], outRes[1]),
               pix_fmt="rgb24" if args.swaprb else "bgr24", r=frameRate)
        .output(args.outpath)
        .run_async(pipe_stdin=True, overwrite_output=True)
)

# Main loop
i = 0
while cap.isOpened():
    # Read frame
    ret, frame = cap.read()
    i += 1
    if not ret:
        break

    # Frame cut
    if i < frameRange[0]:
        continue
    elif i > frameRange[1]:
        break
    else:
        # Frame processing
        outFrame = frame
        if args.slice:
            outFrame = outFrame[sliceArea[0][1]:sliceArea[1][1], sliceArea[0][0]:sliceArea[1][0]]
        if args.rescale:
            outFrame = cv2.resize(outFrame, (outRes[0], outRes[1]), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        # Write frame to file
        process.stdin.write(outFrame.tobytes())

process.stdin.close()
process.wait()
