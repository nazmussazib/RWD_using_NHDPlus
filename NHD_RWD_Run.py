__author__ = 'shams'

from NHD_Rapid_Watershed_Delineation import *




longitude=788395.320   ## user input latitude from clicking on the map
latitude= 1419615.317
## user input longitude from clicking on the map  1,394,160.926


snapping=1 ##user input snapping option ( on=1,off=0)
maximum_snap_distance=10000 ##user input maximum snapping distance
#-75.063120 40.368621
#75.276639 39.892986
# -75.276639 39.892986
#-74.857721  40.283314 ##big area
""" One time input from Pre-Processing Product"""


Pre_process_TauDEM_dir=r'F:\DGT_NHDPlus\NHDPlus\NHDPlusRegion6\Nazmus_Test\Final_Testing'
gage_watershed_shapefile="WBD_HUC10_prj"
gage_watershed_raster="region6watershed"
Ocean_stream_file='none'
gage_watershed_ID_file='Watershed_ID.txt'
np=1
#TauDEM_dir='E:\\USU_Research_work\\MMW_PROJECT\\TauDEM_Project\\TauDEM_deploy_6_working_copy\\Taudem5PCVS2010\\x64\\Release'
TauDEM_dir='F:\TauDEMexe_Test' ## this is my test exe for modified Gagewatershed function
#TauDEM_dir=r'C:\Program Files\TauDEM\TauDEM5Exe'
MPI_dir='C:\\Program Files\\Microsoft HPC Pack 2012\\Bin'

##run Point Watershed Function to get watershed
start_time = time.time()
import sys
sys.path
Point_Watershed_Function(longitude,latitude,snapping,maximum_snap_distance,Pre_process_TauDEM_dir,Ocean_stream_file,
                         gage_watershed_raster,gage_watershed_shapefile,np,TauDEM_dir, MPI_dir)
print("delineation time %s seconds ---" % (time.time() - start_time))
