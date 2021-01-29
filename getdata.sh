DIR_VIDEO=$1
echo "Running process..."
xvfb-run python deteccion_video.py --webcam 0 --directorio_video ${DIR_VIDEO}
echo "Output files named as 'result.csv' and 'outvideo.mp4'"