__author__ = 'shams'


from NHD_RWSDelin_Utilities import *
import time
import fiona
import subprocess
import glob
import sys
def Point_Watershed_Function(longitude,latitude,snapping,maximum_snap_distance,Pre_process_TauDEM_dir,Ocean_stream_file,gage_watershed_raster,gage_watershed_shapefile,np,TauDEM_dir, MPI_dir):
   start_time = time.time()
   start_time2 = time.time()
   X=float(longitude)
   Y=float(latitude)
   point1 = Point(X,Y)
   dir_main=str(Pre_process_TauDEM_dir)+'\Main_Watershed'
   Main_watershed=gage_watershed_shapefile
   #Coast_watershed=coast_watershed_file
   Ocean_Stream=Ocean_stream_file
   Output_dir=str(Pre_process_TauDEM_dir)+'\Test1'
   if not os.path.exists(Output_dir):
       os.makedirs(Output_dir)

   os.chdir(dir_main)
   infile_crs=[]
   with fiona.open(Main_watershed+'.shp') as source:
      projection = source.crs
      infile_crs.append(projection)
   os.chdir(Output_dir)
   #start_time = time.time()
   createShape_from_Point(X,Y,"mypoint",infile_crs[0])
   #print("creating shape %s seconds ---" % (time.time() - start_time2))
   if os.path.isfile(os.path.join(dir_main,Ocean_Stream+'.shp')):
       ID_Ocean_Stream=point_in_Polygon(dir_main,Ocean_Stream,point1)
       if (ID_Ocean_Stream!=None):
          sys.exit("POINT LOCATED IN SIDE THE OCEAN!")

   gage_watershed_rasterfile = os.path.join(dir_main, gage_watershed_raster)
   #start_time = time.time()
   ## extract ID from gage watershed raster saves significant amount of time, that is polygon searching takes long amount of time
   ## however extract raster value from raster does not takes
   fg=int(extract_value_from_raster_point(gage_watershed_rasterfile, longitude, latitude))
   #fg=point_in_Polygon(dir_main,Main_watershed,point1)
   #print("find point in polygon %s seconds ---" % (time.time() - start_time2))
   ID=fg
   print(ID)
   if (ID is None):
       sys.exit("POINT LOCATED OUT SIDE THE WATERSHED!")
   if(ID>0):
      dir_name='Subwatershed'
      sub_file_name="subwatershed_"
      subwatershed_dir=str(Pre_process_TauDEM_dir)+'\\Subwatershed_ALL\\'+dir_name+str(int(ID))
      dist_file=sub_file_name+str(int(ID))+"dist.tif"
      src_filename =os.path.join(subwatershed_dir,dist_file)
      shp_filename = os.path.join(Output_dir,"mypoint.shp")
      distance_stream=extract_value_from_raster(src_filename,shp_filename)
      Grid_Name=sub_file_name+str(int(ID))
      ## add file name for attributes
      ad8_file = sub_file_name + str(int(ID)) + "ad8.tif"
      gord_file = sub_file_name + str(int(ID)) + "gord.tif"
      plen_file = sub_file_name + str(int(ID)) + "plen.tif"
      tlen_file = sub_file_name + str(int(ID)) + "tlen.tif"

   MPH_dir=MPI_dir
   TauDEM_dir=TauDEM_dir
   np=np
   Grid_dir=subwatershed_dir
   Outlet_Point="mypoint"
   Distance_thresh=float(str(maximum_snap_distance))
   New_Gage_watershed_Name="local_subwatershed"
   snaptostream=snapping
   print("search %s seconds ---" % (time.time() - start_time2))
   #start_time = time.time()
   if(snaptostream==1):
     if((ID>0&(distance_stream<Distance_thresh))):
        os.chdir(Output_dir)
        #subprocess.call('AreaD8.exe')
        subprocess.call(str(MOVEOUTLETTOSTREAMS(MPH_dir,np,TauDEM_dir,Grid_dir,Grid_Name,Output_dir,Outlet_Point,Distance_thresh)))
        #os.chdir(Output_dir)

        os.chdir(Output_dir)
        outlet_moved_file=os.path.join(Output_dir,"New_Outlet.shp")
     else:
         os.chdir(Output_dir)
         subprocess.call(MOVEOUTLETTOSTREAMS(MPH_dir,np,TauDEM_dir,Grid_dir,Grid_Name,Output_dir,Outlet_Point,0)) ## not move
         outlet_moved_file=os.path.join(Output_dir,"New_Outlet.shp")
   else:
     os.chdir(Output_dir)
     subprocess.call(MOVEOUTLETTOSTREAMS(MPH_dir,np,TauDEM_dir,Grid_dir,Grid_Name,Output_dir,Outlet_Point,0)) ## not move
     outlet_moved_file=os.path.join(Output_dir,"New_Outlet.shp")
   #os.chdir(Grid_dir)
   subprocess.call(GAUGE_WATERSHED(MPH_dir,np,TauDEM_dir,Grid_dir,Grid_Name,Output_dir,outlet_moved_file,New_Gage_watershed_Name))
   #new_watershed_raster=os.path.join(Output_dir,New_Gage_watershed_Name+".tif")
   cmd4='gdal_polygonize.py -8 local_subwatershed.tif -b 1 -f "ESRI Shapefile"  local_subwatershed.shp local_subwatershed GRIDCODE '
   os.system(cmd4)
   cmd1='ogr2ogr local_subwatershed_dissolve.shp local_subwatershed.shp -dialect sqlite -sql'+ " "+ ' "SELECT GRIDCODE ,ST_Union(geometry) as geometry FROM '+" "+" 'local_subwatershed' " + " " +' GROUP BY GRIDCODE" ' + '  -nln results -overwrite'
   print(cmd1)
   subprocess.call(cmd1)
   ##cmd3='ogr2ogr outfile.shp infile.shp - simplify 1' need to check later for testing
   ##subprocess.call(cmd3)
   New_Gage_watershed_Dissolve=New_Gage_watershed_Name+ "_dissolve"
   myid=[]
   subid=[]
   start_time2 = time.time()
   src_ds = gdal.Open(gage_watershed_rasterfile)
   gt = src_ds.GetGeoTransform()
   rb = src_ds.GetRasterBand(1)

   num_lines = sum(1 for line in open('upwacoor.txt'))
   if(num_lines)>1:
    with open("upwacoor.txt", "rt") as f:
       #next(f)
       for line in f:
           x = float(line.split(',')[0])
           y = float(line.split(',')[1])
           mx = x
           my = y
           # ,my=geom.GetX(), geom.GetY()  #coord in map units
           ## using this approach is the fastest than others such as using gdallocation info or extract raster
           px = int((mx - gt[0]) / gt[1])  # x pixel
           py = int((my - gt[3]) / gt[5])  # y pixel
           Pixel_Data = rb.ReadAsArray(px, py, 1, 1)  # Assumes 16 bit int aka 'short'
           Pixel_Val = Pixel_Data[0, 0]  # use the 'short' format code (2 bytes) not int (4 bytes)
           #cmd='gdallocationinfo -valonly -b 1'+' '+gage_watershed_rasterfile +' '+str(x) +' '+ str(y)
          # result =subprocess.check_output(('gdallocationinfo'+' '+gage_watershed_rasterfile+' '+' -geoloc '+str(x)+' '+str(y)+ ' -valonly'))
           # myid.append(extract_value_from_raster_point(gage_watershed_rasterfile,x,y))

           myid.append(int( Pixel_Val ))
    subid=list(set(myid))
   # print(subid)
    print("identify upstream watershed %s seconds ---" % (time.time() - start_time2))

   #start_time = time.time()
   if((ID>0)&(num_lines>1)):
    compli_watershed_ID= [i for i in subid if i >0]
    len_comp=len(subid)
   else:
     len_comp=-1

   if(len_comp>0):
      start_time = time.time()
      flag="Up stream edge was reached"
      print (flag)
      sub_water_file=[]
      lc_watershed=os.path.join(Output_dir,New_Gage_watershed_Dissolve+'.shp')
      sub_water_file.append(lc_watershed)

      for i in compli_watershed_ID:
          subwater_dir=str(Pre_process_TauDEM_dir)+'\\Subwatershed_ALL\\Subwatershed'+str(int(i))
          com_watershed="Full_watershed"+str(int(i))
          com_file=os.path.join(subwater_dir, com_watershed+'.shp')

          if os.path.isfile(com_file):
            sub_water_file.append(com_file)

      os.chdir(Output_dir)
      for x in range(1, len(sub_water_file)):
          cmd2='ogr2ogr -update -append'+ " "+sub_water_file[0]+ " " + sub_water_file[x]
          print(cmd2)
          os.system(cmd2)
      ## adding st_buffer remove the gaps between polygons
      cmd='ogr2ogr New_Point_Watershed.shp local_subwatershed_dissolve.shp -dialect sqlite -sql'+ " "+ ' "SELECT GRIDCODE ,ST_Union(ST_buffer(geometry, 30)) as geometry FROM '+" "+" 'local_subwatershed_dissolve' " + " " +' GROUP BY GRIDCODE" '
      os.system(cmd)
   else:
      flag="Up stream edge was Not reached"
      print (flag)
      os.chdir(Output_dir)

      cmd='ogr2ogr New_Point_Watershed.shp local_subwatershed_dissolve.shp -dialect sqlite -sql'+ " "+ ' "SELECT GRIDCODE ,ST_Union(geometry) as geometry FROM '+" "+" 'local_subwatershed_dissolve' " + " " +' GROUP BY GRIDCODE" '
      os.system(cmd)

   start_time = time.time()
   Get_Watershed_Attributes('New_Outlet.shp', 'New_Point_Watershed.shp',ad8_file, plen_file, tlen_file, gord_file, subwatershed_dir, Output_dir)
   print("watershed attributes time %s seconds ---" % (time.time() - start_time))
   pattern = "^mypoint"
   path=Output_dir
   remove_file_directory(path,pattern)
   pattern = "^Outlets"
   path=Output_dir
   purge(path,pattern)
   pattern = "^local"
   path=Output_dir
   purge(path,pattern)
   remove_file('mypoint.shp')
   remove_file('Outlets.shp')
   remove_file('Outlets_moved.shp')
   remove_file('local_subwatershed.shp')
   remove_file('local_subwatershed_dissolve.shp')
   remove_file('point_watershed.shp')
   os.remove('upwacoor.txt')
   pattern = "^point_watershed"
   path=Output_dir
   purge(path,pattern)
   filelist = glob.glob("temp_*")
   for f in filelist:
    os.remove(f)





















