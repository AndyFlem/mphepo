import arcpy
import json
import os
import shutil
import glob

def import_kmz(input_feature,temp_location,output_folder,output_name,input_type):
    delete_kmz_imports(temp_location,output_name)
    delete_shape(output_folder,output_name)

    print("Importing kmz: " + input_feature + ". Type: " + input_type)

    arcpy.KMLToLayer_conversion(input_feature,temp_location,output_name)

    print("Moving features: " + temp_location + " : " + output_name)
    f_in=temp_location + "\\" + output_name + ".gdb\\Placemarks\\" + input_type
    arcpy.FeatureClassToFeatureClass_conversion(f_in, output_folder, output_name)

    

def delete_kmz_imports(folder, base_name):
    print("Delete kmz: " + folder + "\\" + base_name)
    
    if os.path.exists(folder + "\\" + base_name + ".gdb"):
        shutil.rmtree(folder + "\\" + base_name + ".gdb")
    if os.path.exists(folder + "\\" + base_name + ".lyr"):
        os.remove(folder + "\\" + base_name + ".lyr")

def delete_shape(folder,base_name):
    fileList = glob.glob(folder + "\\" + base_name + ".*")
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)        
