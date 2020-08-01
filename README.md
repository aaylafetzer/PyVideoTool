# VideoTool
## Installation
To install this tool, you can run the following commands in your terminal to set up a virtual environment (optional) and use the tool
```shell script
# Optional Commands for venv
python3 -m pip install --user virtualenv
python3 -m venv env
source env/bin/activate
# Actual setup
pip3 install -r requirements.txt
```
VideoTool is now ready to use
## Usage
For simple cropping, VideoTool accepts several arguments that can also be displayed by running the script with the -h argument.

### Transformations
 - ``--slice | -s`` When given colon-separated pixel locations, the rectangle between them will be cropped as the output video
 - ``--rescale | -r`` Will resize the output video to the given x-separated resolution
 - ``--framerange | -f`` Will export only the frames between the colon-separated integers. Use x:-1 to export from frame x to the end of the video.
### Other arguments
 - ``--swaprb`` Will swap the red and blue channels for bgr recordings