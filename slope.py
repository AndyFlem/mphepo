import arcpy

arcpy.env.workspace="C:\Users\Andy Fleming\Documents\ArcGIS\Default.gdb"

arcpy.CopyFeatures_management("RasterT_tif1_nosmalls2", "RasterT_tif1_nosmalls3")
arcpy.MakeFeatureLayer_management("RasterT_tif1_nosmalls3", "tempLayer")

#expression = arcpy.AddFieldDelimiters("tempLayer", "gridcode") + " = 1"
#arcpy.SelectLayerByAttribute_management("tempLayer", "NEW_SELECTION", expression)
#arcpy.DeleteFeatures_management("tempLayer")

expression = arcpy.AddFieldDelimiters("tempLayer", "Shape_Area") + " < 1500"
arcpy.SelectLayerByAttribute_management("tempLayer", "NEW_SELECTION", expression)
arcpy.DeleteFeatures_management("tempLayer")