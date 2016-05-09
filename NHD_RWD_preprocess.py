from osgeo import gdal,ogr
import glob, os
from NHD_PreProcessor_For_Rapid_Watershed_Delineation import *


input_dir_name=r'F:\DGT_NHDPlus\NHDPlus\NHDPlusRegion6\Nazmus_Test\Final_Testing'
watershed_file='WBD_HUC10_prj.shp'
watershed_id_file="Watershed_ID.txt"
p_file="region6p.tif"
src_file="region6streamraster.tif"
gw_file="region6watershed.tif"
dist_file="region6dist.tif"
PreProcess_TauDEM_for_On_Fly_WatershedDelineation_NHD(input_dir_name, watershed_file, watershed_id_file,
                                                      p_file,src_file,dist_file)
