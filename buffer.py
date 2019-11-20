import arcpy
import json
import buffer_procs


arcpy.env.overwriteOutput=True

config="mphepo_buffer4.json"

with open(config) as json_file:
    config = json.load(json_file)
    workspace=config['workspace']
    
    print("Using workspace: " + workspace)
    arcpy.env.workspace=workspace

    buffers=[]

  
    for feature in config['features']:
        if 'ignore' in feature:
            print("Ignoring: " + feature['name'])    
        else:
            if 'no_preprocess' not in feature:
                print("Buffering: " + feature['name'])

                if feature['input_type'] == 'kmz':
                    f_in=config['workspace'] + "\\" + config['input_folder'] + "\\" + feature['input']
                    buffer_procs.import_kmz(f_in,config['temp_workspace'] ,config['workspace'] + "\\" + config['input_folder'],feature['ref'],feature['feature_type'])

                if feature['input_type'] == 'shp':
                    f_in=config['workspace'] + "\\" + config['input_folder'] + "\\" + feature['input']    
                    arcpy.FeatureClassToFeatureClass_conversion(f_in, config['workspace'] + "\\" + config['input_folder'] + "\\", feature['ref'] + ".shp")
                
                f_out = config['workspace'] + "\\" + config['input_folder'] + "\\" + feature['ref'] + ".shp" 
                f_in = f_out

                #repair
                arcpy.RepairGeometry_management(f_out)

                #reproject if needed
                desc = arcpy.Describe(f_in)
                if desc.spatialReference.factoryCode != config['coordinate_system']:
                    print("Feature has coordinate system: " + desc.spatialReference.name + ". Projecting to: " +  str(config['coordinate_system']))
                    f_out=config['output_folder'] + "\\" + feature['ref'] + "_proj.shp"
                    sys= arcpy.SpatialReference(config['coordinate_system'])
                    arcpy.Project_management(f_in, f_out, sys)

                #clip input feature to the start_area
                print("Clipping: " + feature['name'])
                f_in = f_out
                f_clip = config['input_folder'] + "\\" + config['start_area'] + ".shp"
                f_out = config['output_folder'] + "\\" + feature['ref'] + "_clip.shp"
                arcpy.Clip_analysis(f_in, f_clip, f_out)
        

                #buffer
                f_in=f_out
                f_out = config['output_folder'] + "\\" + feature['ref'] + "_buffer.shp"
                if feature['buffer_meters']>0:
                    print("Buffering to: " + f_out)
                    arcpy.Buffer_analysis(f_in, f_out, feature['buffer_meters'])
                else:
                    arcpy.CopyFeatures_management(f_in, f_out)

                #label
                f_in=f_out
                print("Labeling to: " + f_out)
                arcpy.AddField_management(f_in, "feat_ref", "TEXT", field_length=30)
                arcpy.CalculateField_management(f_in,"feat_ref",'"' + feature['ref'] + '"')
    

    #merge
    print('Merging to buffers.shp')
    fs_in=[]
    f_out = config['output_folder'] + "\\buffers.shp"
    fm_ref = arcpy.FieldMap()
    fm_fid = arcpy.FieldMap()
    fms = arcpy.FieldMappings()

    for feature in config['features']:
        if 'ignore' not in feature and 'no_exclusion' not in feature:
            print("Adding " + feature['name'])
            f_in=config['output_folder'] + "\\" + feature['ref'] + "_buffer.shp"
            fs_in.append(f_in)            
            fm_ref.addInputField(f_in, "feat_ref") 
            fm_fid.addInputField(f_in, "FID") 
    
    ref_name = fm_ref.outputField
    ref_name.name = 'feat_ref'
    fid_name = fm_ref.outputField
    fid_name.name = 'orig_fid'
    
    fm_ref.outputField = ref_name
    fm_fid.outputField = fid_name
    fms.addFieldMap(fm_ref)
    fms.addFieldMap(fm_fid)

    arcpy.Merge_management(fs_in,f_out,fms)


    #dissolve buffers
    print("Dissolving")
    f_in=f_out
    f_out=config['output_folder'] + "\\dissolve.shp"
    arcpy.Dissolve_management(f_in,f_out,"feat_ref")

    #clip
    print("Producing available area")
    f_in=config['input_folder'] + "\\" + config['start_area'] + ".shp"
    f_erase=f_out
    f_out=config['output_folder'] + "\\available_area.shp"
    arcpy.Erase_analysis(f_in, f_erase, f_out)