import sys
import os
import cv2
import rasterio
import rasterio.mask
import fiona
import json


def process_one_image(pan_file,meta_file,anno_file):

    img = cv2.imread(pan_file)
    bilateral_filtered_image = cv2.bilateralFilter(img, 5, 175, 175)
    edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 200)
    contours, hierarchy= cv2.findContours(edge_detected_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour_list = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)
        if ((len(approx) > 20) and area >= 30):
            contour_list.append(contour)

    with rasterio.open(pan_file) as dataset:
        #print(dataset.name)
        #print(dataset.bounds)
        #print(dataset.bounds.left)

        row_pix=(dataset.bounds.bottom - dataset.bounds.top)/img.shape[0]
        col_pix=(dataset.bounds.right-dataset.bounds.left)/img.shape[1]

    res_jobj={}
    res_jobj["type"]="FeatureCollection"
    res_jobj["crs"]={}
    res_jobj["crs"]["type"]="name"
    res_jobj["crs"]["properties"]={}
    res_jobj["crs"]["properties"]["name"]="urn:ogc:def:crs:EPSG::32723"
    res_jobj["features"]=[]
    contour_jobj = {}
    contour_jobj["type"] = "Feature"
    contour_jobj["properties"] = {}
    contour_jobj["geometry"] = {}
    contour_jobj["geometry"]["type"] = "Polygon"
    contour_jobj["geometry"]["coordinates"] = []
    res_jobj["features"].append(contour_jobj)

    for contour in contour_list:
        nodes=[]
        first_node=None
        #print(contour)
        for point in contour:
            point=point[0]
            coordinates=[dataset.bounds.left+point[1]*col_pix,
                         dataset.bounds.top+point[0]*row_pix]
            if first_node is None:
                first_node=coordinates
            nodes.append(coordinates)
        nodes.append(first_node)
        contour_jobj["geometry"]["coordinates"].append(nodes)
    with open(anno_file,'w') as fout:
        json.dump(res_jobj,fout)







if __name__=='__main__':
    #read one file and process
    data_dir=sys.argv[1]
    output_dir=sys.argv[2]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    images=os.listdir(data_dir)
    for imageid in images:
        image_dir=os.path.join(data_dir,imageid)
        pan_file=os.path.join(image_dir,imageid+'_PAN.tif')
        meta_file=os.path.join(image_dir,imageid+'_metadata.json')
        anno_file=os.path.join(output_dir,imageid+'_anno.geojson')

        process_one_image(pan_file,meta_file,anno_file)


