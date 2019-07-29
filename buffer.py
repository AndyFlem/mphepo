import arcpy
import json

arcpy.env.overwriteOutput=True

config="mphepo_buffer.json"

with open(config) as json_file:
    config = json.load(json_file)
    workspace=config['workspace']
    
    print("Using workspace: " + workspace)
    arcpy.env.workspace=workspace

    buffers=[]


    for feature in config['features']:
        if 'ignore' in feature:
            print("Ignoring feature type: " + feature['name'])    
        else:
            print("Buffering feature type: " + feature['name'])
            #buffer_procs.process(feature)

            #clip input feature to the start_area
            f_in = config['input_folder'] + "/" + feature['ref'] + ".shp"
            f_clip = config['input_folder'] + "/" + config['start_area'] + ".shp"
            f_out = config['output_folder'] + "/" + feature['ref'] + "_clip.shp"
            arcpy.Clip_analysis(f_in, f_clip, f_out)

            desc = arcpy.Describe(f_out)
    
            #reproject if needed
            if desc.spatialReference.factoryCode != config['coordinate_system']:
                print("Feature has coordinate system: " + desc.spatialReference.name + ". Projecting to: " +  str(config['coordinate_system']))
                f_in=f_out
                f_out=config['output_folder'] + "/" + feature['ref'] + "_proj.shp"
                sys= arcpy.SpatialReference(config['coordinate_system'])
                arcpy.Project_management(f_in, f_out, sys)

            #buffer
            f_in=f_out
            f_out = config['output_folder'] + "/" + feature['ref'] + "_buffer.shp"
            print("Buffering to: " + f_out)
            arcpy.Buffer_analysis(f_in, f_out, feature['buffer_meters'])

            #label
            f_in=f_out
            print("Labeling to: " + f_out)
            arcpy.AddField_management(f_in, "feat_ref", "TEXT", field_length=30)
            arcpy.CalculateField_management(f_in,"feat_ref",'"' + feature['ref'] + '"')

    #merge
    fs_in=[]
    f_out = config['output_folder'] + "/buffers.shp"
    fm_ref = arcpy.FieldMap()
    fm_fid = arcpy.FieldMap()
    fms = arcpy.FieldMappings()

    for feature in config['features']:
        if 'ignore' not in feature:
            f_in=config['output_folder'] + "/" + feature['ref'] + "_buffer.shp"
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

    #clip
    f_in=config['input_folder'] + "/" + config['start_area'] + ".shp"
    f_erase=f_out
    f_out=config['output_folder'] + "/available_area.shp"
    arcpy.Erase_analysis(f_in, f_erase, f_out)