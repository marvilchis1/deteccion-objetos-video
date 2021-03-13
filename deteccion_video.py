from __future__ import division
from models import *
from utils.utils import *
from utils.datasets import *
import os
import sys
import argparse
import cv2
from PIL import Image
import torch
from torch.autograd import Variable

import pandas as pd

def Convertir_RGB(img):
    # Convertir Blue, green, red a Red, green, blue
    b = img[:, :, 0].copy()
    g = img[:, :, 1].copy()
    r = img[:, :, 2].copy()
    img[:, :, 0] = r
    img[:, :, 1] = g
    img[:, :, 2] = b
    return img


def Convertir_BGR(img):
    # Convertir red, blue, green a Blue, green, red
    r = img[:, :, 0].copy()
    g = img[:, :, 1].copy()
    b = img[:, :, 2].copy()
    img[:, :, 0] = b
    img[:, :, 1] = g
    img[:, :, 2] = r
    return img


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_folder", type=str, default="data/samples", help="path to dataset")
    parser.add_argument("--model_def", type=str, default="config/yolov3.cfg", help="path to model definition file")
    parser.add_argument("--weights_path", type=str, default="weights/yolov3.weights", help="path to weights file")
    parser.add_argument("--class_path", type=str, default="data/coco.names", help="path to class label file")
    parser.add_argument("--conf_thres", type=float, default=0.8, help="object confidence threshold")
    parser.add_argument("--webcam", type=int, default=1,  help="Is the video processed video? 1 = Yes, 0 == no" )
    parser.add_argument("--nms_thres", type=float, default=0.4, help="iou thresshold for non-maximum suppression")
    parser.add_argument("--batch_size", type=int, default=1, help="size of the batches")
    parser.add_argument("--n_cpu", type=int, default=0, help="number of cpu threads to use during batch generation")
    parser.add_argument("--img_size", type=int, default=416, help="size of each image dimension")
    parser.add_argument("--directorio_video", type=str, help="Directorio al video")
    parser.add_argument("--checkpoint_model", type=str, help="path to checkpoint model")
    opt = parser.parse_args()
    print(opt)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("cuda" if torch.cuda.is_available() else "cpu")
    model = Darknet(opt.model_def, img_size=opt.img_size).to(device)


    if opt.weights_path.endswith(".weights"):
        model.load_darknet_weights(opt.weights_path)
    else:
        model.load_state_dict(torch.load(opt.weights_path))

    model.eval()  
    classes = load_classes(opt.class_path)
    Tensor = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor
    if opt.webcam==1:
        cap = cv2.VideoCapture(0)
        out = cv2.VideoWriter('output.mp4',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (1280,960))
    else:
        cap = cv2.VideoCapture(opt.directorio_video)
        # frame_width = int(cap.get(3))
        # frame_height = int(cap.get(4))
        out = cv2.VideoWriter('outvideo.mp4', cv2.VideoWriter_fourcc(*"mp4v"), 30, (1280, 960), True)
    colors = np.random.randint(0, 255, size=(len(classes), 3), dtype="uint8")
    a=[]
    
    filter_list = [1, 13, 24, 26, 28, 32, 34, 35, 36, 56, 57, 58, 60, 61, 65, 71]
    filter_list = set(filter_list)
    name = []
    dx1 = []
    dy1 = []
    dx2 = []
    dy2 = []
    number_frame = []
    
    while cap:
        ret, frame = cap.read()
        if ret is False:
            break
        frame = cv2.resize(frame, (1280, 960), interpolation=cv2.INTER_CUBIC)
        #LA imagen viene en Blue, Green, Red y la convertimos a RGB que es la entrada que requiere el modelo
        RGBimg=Convertir_RGB(frame)
        imgTensor = transforms.ToTensor()(RGBimg)
        imgTensor, _ = pad_to_square(imgTensor, 0)
        imgTensor = resize(imgTensor, 416)
        imgTensor = imgTensor.unsqueeze(0)
        imgTensor = Variable(imgTensor.type(Tensor))


        with torch.no_grad():
            detections = model(imgTensor)
            detections = non_max_suppression(detections, opt.conf_thres, opt.nms_thres)
        
        for detection in detections:
            if detection is not None:
                #print(detection)
                detection = rescale_boxes(detection, opt.img_size, RGBimg.shape[:2])
                for x1, y1, x2, y2, conf, cls_conf, cls_pred in detection:
                    #print(int(cls_pred))
                    num_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    if int(cls_pred) in filter_list:
                        box_w = x2 - x1
                        box_h = y2 - y1
                        color = [int(c) for c in colors[int(cls_pred)]]
                        #print("{} en X1: {}, Y1: {}, X2: {}, Y2: {}; FRAME: {}".format(classes[int(cls_pred)], x1, y1, x2, y2, cap.get(cv2.CAP_PROP_POS_FRAMES)))
#                        print cam.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
                        name.append(classes[int(cls_pred)])
                        dx1.append(float(x1))
                        dy1.append(float(y1))
                        dx2.append(float(x2))
                        dy2.append(float(y2))
                        number_frame.append(float(num_frame))
                        frame = cv2.rectangle(frame, (int(x1), int(y1 + box_h)), (int(x2), int(y1)), (155, 255, 0), 3)
                        cv2.putText(frame, classes[int(cls_pred)], (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 5)# Nombre de la clase detectada
                        cv2.putText(frame, str("%.2f" % float(conf)), (int(x2), int(y2 - box_h)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,color, 5) # Certeza de prediccion de la clase
        #
        #Convertimos de vuelta a BGR para que cv2 pueda desplegarlo en los colores correctos
        
        if opt.webcam==1:
            cv2.imshow('frame', Convertir_BGR(RGBimg))
            out.write(RGBimg)
        else:
            out.write(Convertir_BGR(RGBimg))
            cv2.imshow('frame', RGBimg)
        #cv2.waitKey(0)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    data = {'NAME': name, 'X1': dx1, 'Y1': dy1, 'X2': dx2, 'Y2': dy2, 'FRAME':number_frame}
    df = pd.DataFrame(data, columns = ['NAME', 'X1', 'Y1', 'X2', 'Y2', 'FRAME'])
    df.to_csv('result.csv')
    out.release()
    cap.release()
    cv2.destroyAllWindows()
