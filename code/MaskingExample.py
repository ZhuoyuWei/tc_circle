#!/usr/bin/env python
# coding: utf-8

# In[6]:


import rasterio
import rasterio.mask
import fiona
import os


# For this exercise, the files are collocated with the notebook. 

# In[14]:


f_annotation = "103001005C50D100_0_anno.geojson"
f_pan = "103001005C50D100_0_PAN.tif"


# In[15]:


with fiona.open(f_annotation, "r") as annotation_collection:
    annotations = [feature["geometry"] for feature in annotation_collection]
                    


# In[20]:


with rasterio.open(f_pan) as src:
    out_image, out_transform = rasterio.mask.mask(src, annotations, all_touched=False, invert=True, crop=False)
    out_meta = src.meta


# In[21]:


out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})


# In[22]:


with rasterio.open("Masked.tif", "w", **out_meta) as dest:
    dest.write(out_image)


# In[ ]:




