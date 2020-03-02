# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

# standard toolkit logger
logger = sgtk.platform.get_logger(__name__)

def model_sheet_layer( engine,
                       project_name,
                       project_type,
                       asset_name,
                       task_name,
                       version_name,
                       asset_type,
                       episode_name,
                       ship_episode,
                       current_sc,
                       sap_number,
                       assigned_to,
                       banner_color,
                       font,
                       show_logo = True,
                       show_labels = False,
                       show_date = False,
                       show_disclaimer = True
                       ) :
                       
    import os, datetime
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    
    # set the banner constants
    _banner_min_height = 150
    _banner_aspect = 0.08
    
#    project_type = '2D'
    
    # main column layouts
    if project_type == '2D' :
        _logo_position = 0.01
#         _info_position = 0.32
        _info_position = 0.25
        _2d_label_position = 0.59
        _2d_info_position = 0.595
        _disclaimer_position = 0.73
    else :
        _logo_position = 0.37
        _info_position = 0.01
        _2d_label_position = 0.25
        _2d_info_position = 0.40
        _disclaimer_position = 0.68
    
    # get the model sheet bg image
    script_path = os.path.dirname(os.path.realpath(__file__))
    model_sheet_bg_path = os.path.join(script_path,'../../resources/model_sheet_bg.png')
    model_sheet_image_path = '/tmp/sg_modelsheet_images/model_sheet_image.png'
    model_sheet_studio_image_path = '/tmp/sg_modelsheet_images/studio_image.jpg'
    
    # make File references if image paths exist
    if os.path.exists(model_sheet_bg_path) :
        model_sheet_bg_file = engine.adobe.File(model_sheet_bg_path)
    if os.path.exists(model_sheet_image_path) :
        model_sheet_image_path_file = engine.adobe.File(model_sheet_image_path)
    if os.path.exists(model_sheet_studio_image_path) :
        model_sheet_studio_image_file = engine.adobe.File(model_sheet_studio_image_path)
    
    # get the photoshop application
    app = engine.adobe.app
    
    # get the current active document
    current_active_document = app.activeDocument
    
    # store the current background color and units
    original_bg_color_red = app.backgroundColor.rgb.red
    original_bg_color_green= app.backgroundColor.rgb.green
    original_bg_color_blue = app.backgroundColor.rgb.blue
    
    original_ruler_units = app.preferences.rulerUnits
    original_type_units = app.preferences.typeUnits
    
    # set the units to PIXELS
    app.preferences.rulerUnits = engine.adobe.Units.PIXELS
    
    # store the current height and width of active document for later
    _width = app.activeDocument.width.value
    _height = app.activeDocument.height.value
    
    # pixels per inch
    _baseUnit = app.activeDocument.width.baseUnit.value
    
    _72dpi = 0.0138888888889
    _300dpi = 0.00333333333333
    _72dpi_factor = round(_baseUnit/_72dpi, 3)
    
    # calculate banner dimensions
    _banner_height = int(max(_banner_min_height,_width*_banner_aspect))
    _canvas_height = _height + _banner_height
    
    # text scale factor
    text_scale_factor = float(_banner_height)/float(478)
    
    # need to look for an existing model sheet layer
    # if it exists, remove it
    # if it does not exist, we need to add the margin at the top of the document
    try:
        model_sheet_layer = app.activeDocument.layers["WBA Model Sheet"]
        model_sheet_layer.remove()
        existing_banner = True
    except:
        existing_banner = False
        pass
    
    
    # set mode to RGB
    current_active_document.changeMode(engine.adobe.ChangeMode.RGB)
    
    # set the background color
    # this is the color of the modelsheet top banner
    if banner_color in ['Black'] :
        engine.adobe.rpc_eval('app.backgroundColor.rgb.red = 0')
        engine.adobe.rpc_eval('app.backgroundColor.rgb.green = 0')
        engine.adobe.rpc_eval('app.backgroundColor.rgb.blue = 0')
    elif banner_color in ['Dark Gray'] :
        engine.adobe.rpc_eval('app.backgroundColor.rgb.red = 50')
        engine.adobe.rpc_eval('app.backgroundColor.rgb.green = 50')
        engine.adobe.rpc_eval('app.backgroundColor.rgb.blue = 50')
    elif banner_color in ["Middle Gray"] :
        engine.adobe.rpc_eval('app.backgroundColor.rgb.red = 125')
        engine.adobe.rpc_eval('app.backgroundColor.rgb.green = 125')
        engine.adobe.rpc_eval('app.backgroundColor.rgb.blue = 125')
    elif banner_color in ["White"] :
        engine.adobe.rpc_eval('app.backgroundColor.rgb.red = 255')
        engine.adobe.rpc_eval('app.backgroundColor.rgb.green = 255')
        engine.adobe.rpc_eval('app.backgroundColor.rgb.blue = 255')
        
    if not existing_banner :
    
        # resize the canvas for the model sheet banner
        engine.adobe.app.activeDocument.resizeCanvas(engine.adobe.UnitValue(_width,"px"),engine.adobe.UnitValue(_canvas_height,"px"),engine.adobe.AnchorPosition.BOTTOMCENTER)
    
    # change to 72dpi
#    engine.adobe.app.activeDocument.resizeImage(_width, _canvas_height, 200, engine.adobe.ResampleMethod.NONE)
    
    # add a group for the model sheet layers
    model_sheet_group = engine.adobe.app.activeDocument.layerSets.add()
    model_sheet_group.name = "WBA Model Sheet"
    
    # create a layer for the banner background
    banner_bg_layer = engine.adobe.app.activeDocument.artLayers.add()
    banner_bg_layer.name = 'Background Banner'
    
    # create banner
    x = str(0)
    y = str(0)
    sw = str(_width)
    sh = str(_banner_height)
    
    # set the selection to the banner area
    selection_command = 'app.activeDocument.selection.select([ ['+x+','+y+'], ['+x+','+y+'+'+sh+'], ['+x+'+'+sw+','+y+'+'+sh+'], ['+x+'+'+sw+','+y+'] ])'
    engine.adobe.rpc_eval(selection_command)
    
    # crashing here...
    
    # fill it with the previously set background color
    engine.adobe.app.activeDocument.selection.fill(engine.adobe.app.backgroundColor)
    
    # move banner bg image into active documents model sheet layerSet
    banner_bg_layer.move(model_sheet_group, engine.adobe.ElementPlacement.INSIDE)
    
    if project_type == '3D' or '2D':
    
        # add the model_sheet_image logo
        _max_logo_width = _width * 0.25
        _max_logo_height = _banner_height
        _max_logo_aspect =  float(_max_logo_height) / float(_max_logo_width)
    
        # add 'Project.sg_model_sheet_image'
        try :
            sg_model_sheet_image = app.open(model_sheet_image_path_file)
        except :
            sg_model_sheet_image = None
        
        if sg_model_sheet_image is not None:
            with engine.context_changes_disabled():
                # turn off isBackgroundLayer flag and make it capable of transparency
                sg_model_sheet_image.artLayers[0].isBackgroundLayer = False
                # set the layer name
                sg_model_sheet_image.artLayers[0].name = "Model Sheet Image"
        
                # set u its to PIXELS
                app.preferences.rulerUnits = engine.adobe.Units.PIXELS
    
                # get the height and width of sg_model_sheet_image
                app.activeDocument = sg_model_sheet_image
                _logo_width = app.activeDocument.width.value
                _logo_height = app.activeDocument.height.value
                _logo_aspect = float(_logo_height) / float(_logo_width)
        
                if _max_logo_aspect > _logo_aspect :
                    sg_model_sheet_image.resizeImage(_max_logo_width , int(_max_logo_width * _logo_aspect))
                else :
                    sg_model_sheet_image.resizeImage(int(_max_logo_height * 1/_logo_aspect) ,_max_logo_height)
    
                # get the new logo size
                _logo_width = app.activeDocument.width.value
                _logo_height = sg_model_sheet_image.height.value
    
            #     logger.info('_logo_scaled_width: %s    _logo_scaled_height: %s' % (_logo_width,_logo_height))
    
                # duplicate sg_model_sheet_image into active document
                model_sheet_image_layer = sg_model_sheet_image.artLayers[0].duplicate(current_active_document)
                # close sg_model_sheet_image file
                sg_model_sheet_image.close(engine.adobe.SaveOptions.DONOTSAVECHANGES)
    
        # switch back to the main document
        app.activeDocument = current_active_document
    
        if sg_model_sheet_image is not None:
            # position the logo
            model_sheet_image_layer.translate(_width*_logo_position , _banner_height/100)
            model_sheet_image_layer.translate(0 , _banner_height/100)

            # move sg_model_sheet_image into active documents model sheet layerSet
            model_sheet_image_layer.move(model_sheet_group, engine.adobe.ElementPlacement.INSIDE)
    
    if project_type == '2D' :
    # show the model sheet labels

        text_layer1 = engine.adobe.app.activeDocument.artLayers.add()
        text_layer1.name = "Model Sheet Labels"
        text_layer1.kind = engine.adobe.LayerKind.TEXT
        text_layer1.textItem.kind = engine.adobe.TextType.PARAGRAPHTEXT
        text_layer1.textItem.justification = engine.adobe.Justification.RIGHTJUSTIFIED
        
        text_layer1.textItem.width = _width * 0.07  * _72dpi_factor
        text_layer1.textItem.height = _banner_height * _72dpi_factor
        text_layer1.textItem.size = 70 * _72dpi_factor * text_scale_factor
        
        # position 2D info labels
#         text_layer1.textItem.position = (((float(_width)*0)-(float(_width) * 0.15)) , (_banner_height/10))
        text_layer1.textItem.position = ((float(_width)*(_info_position-0.075)) , (_banner_height/10))
        
        if banner_color in ['Dark Gray','Black'] :
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.red = 245')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.green = 245')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.blue = 245')
        else :
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.red = 10')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.green = 10')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.blue = 10')
        
        model_sheet_label = ''
        model_sheet_label +=    "Project : "
        if version_name != "" :
            model_sheet_label += "\rVersion Name: " 
        model_sheet_label += "\rAsset Name : "
        if asset_type != "" :
            model_sheet_label += "\rType : " 
        if task_name != "" :
            model_sheet_label += "\rTask : "
        
        text_layer1.textItem.contents = model_sheet_label
        text_layer1.move(model_sheet_group, engine.adobe.ElementPlacement.INSIDE)

    # add the model sheet information
    text_layer2 = engine.adobe.app.activeDocument.artLayers.add()
    text_layer2.name = "Model Sheet Info"
    text_layer2.kind = engine.adobe.LayerKind.TEXT
    text_layer2.textItem.kind = engine.adobe.TextType.PARAGRAPHTEXT
    text_layer2.textItem.justification = engine.adobe.Justification.LEFTJUSTIFIED
    
    text_layer2.textItem.width = _width * 0.40 * _72dpi_factor
    text_layer2.textItem.height = _banner_height * _72dpi_factor
    text_layer2.textItem.size = 70 * _72dpi_factor * text_scale_factor
    
    # set the font
#     engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.font = "'+ font +'"')
    text_layer2.textItem.font = font
    
    # position info text
    text_layer2.textItem.position = ((float(_width)*_info_position) , (_banner_height/10))
    
    if banner_color in ['Dark Gray','Black'] :
        engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.red = 245')
        engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.green = 245')
        engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.blue = 245')
    else :
        engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.red = 10')
        engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.green = 10')
        engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.blue = 10')
    
    model_sheet_text = ''
    
    # 3D Project and Episode
    if project_type == '3D' :
        if episode_name == "" :
            model_sheet_text =  project_name + "\r"
        else :
            model_sheet_text =  project_name + "                      Ep: "+episode_name+"\r"
        
        if task_name != "" :
            # asset type    task name
            model_sheet_text += asset_type + "                      "+task_name +"\r"
        else :
            # task name
            model_sheet_text += asset_type + "\r"
        
        # asset name
        if asset_name != "" :
            model_sheet_text += asset_name + "\r"
        
        # assigned to
        if assigned_to != "" :
            model_sheet_text += assigned_to + "\r"
        
        # version
        if version_name != "" :
            model_sheet_text += version_name + "\r"

        
    # 2D Project Only
    else :
        model_sheet_text =  project_name + "\r"
    
        # Version
        if version_name != "" :
            model_sheet_text += version_name + "\r"
        model_sheet_text += asset_name + "\r"
        if asset_type != "" :
            model_sheet_text += asset_type + "\r"
        if task_name != "" :
            model_sheet_text += task_name + "\r"
#             model_sheet_text += assigned_to + "\r"
        
    
    text_layer2.textItem.contents = model_sheet_text
    text_layer2.move(model_sheet_group, engine.adobe.ElementPlacement.INSIDE)
    

    if project_type == '2D' :

        # add the 2D model sheet labels
        text_layer3 = engine.adobe.app.activeDocument.artLayers.add()
        text_layer3.name = "2D Model Sheet Labels"
        text_layer3.kind = engine.adobe.LayerKind.TEXT
        text_layer3.textItem.kind = engine.adobe.TextType.PARAGRAPHTEXT
        text_layer3.textItem.justification = engine.adobe.Justification.RIGHTJUSTIFIED
    
        text_layer3.textItem.width = _width * 0.15 * _72dpi_factor
        text_layer3.textItem.height = _banner_height * _72dpi_factor
        text_layer3.textItem.size = 70 * _72dpi_factor * text_scale_factor
    
        text_layer3.textItem.font = font
    
        # position 2D info labels
        text_layer3.textItem.position = (((float(_width)*_2d_label_position)-(float(_width) * 0.15)) , (_banner_height/10))
    
        if banner_color in ['Dark Gray','Black'] :
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.red = 245')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.green = 245')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.blue = 245')
        else :
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.red = 10')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.green = 10')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.blue = 10')
    
        model_sheet_label = ''
        if episode_name != "" :
            model_sheet_label += "Episode : " + "\r"
        if ship_episode != "" :
            model_sheet_label += "Ship Episode : " + "\r"
        if current_sc != "" :
            model_sheet_label += "Current Scene : " + "\r"
        if sap_number != "" :
            model_sheet_label += "SAP Number : " + "\r"
        if assigned_to != "" :
            model_sheet_label += "Assigned To : " + "\r"
                
        text_layer3.textItem.contents = model_sheet_label
        text_layer3.move(model_sheet_group, engine.adobe.ElementPlacement.INSIDE)


        # add the 2D model sheet information
        text_layer4 = engine.adobe.app.activeDocument.artLayers.add()
        text_layer4.name = "2D Model Sheet Info"
        text_layer4.kind = engine.adobe.LayerKind.TEXT
        text_layer4.textItem.kind = engine.adobe.TextType.PARAGRAPHTEXT
        text_layer4.textItem.justification = engine.adobe.Justification.LEFTJUSTIFIED
    
        text_layer4.textItem.width = _width * 0.20 * _72dpi_factor
        text_layer4.textItem.height = _banner_height * _72dpi_factor
        text_layer4.textItem.size = 70 * _72dpi_factor * text_scale_factor
    
        text_layer4.textItem.font = font
    
        # position 2D info text
        text_layer4.textItem.position = ((float(_width)*_2d_info_position) , (_banner_height/10))
    
        if banner_color in ['Dark Gray','Black'] :
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.red = 245')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.green = 245')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.blue = 245')
        else :
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.red = 10')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.green = 10')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.blue = 10')
    
        model_sheet_text = ''

        if episode_name != "" :
            model_sheet_text += episode_name + "\r"
        if ship_episode != "" :
            model_sheet_text += ship_episode + "\r"
        if current_sc != "" :
            model_sheet_text += current_sc + "\r"
        if sap_number != "" :
            model_sheet_text += sap_number + "\r"
        if assigned_to != "" :
           model_sheet_text += assigned_to + "\r"
        #     if show_date:
    #         model_sheet_text += today + "\r"
    
        text_layer4.textItem.contents = model_sheet_text
        text_layer4.move(model_sheet_group, engine.adobe.ElementPlacement.INSIDE)
    
    
    if show_disclaimer :
        disclaimer = engine.adobe.app.activeDocument.artLayers.add()
        disclaimer.name = "Disclaimer Info"
        disclaimer.kind = engine.adobe.LayerKind.TEXT
        disclaimer.textItem.kind = engine.adobe.TextType.PARAGRAPHTEXT
        
        disclaimer.textItem.width = int(_width* 0.35 * .85) * _72dpi_factor
        disclaimer.textItem.height = _banner_height * .85 * _72dpi_factor
        disclaimer.textItem.size = 54 * _72dpi_factor * text_scale_factor
        
        # set the font
#         engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.font = "'+ font +'"')

        disclaimer.textItem.font = font
        
        disclaimer.textItem.position = (_width * _disclaimer_position , _banner_height / 7)
        
        if banner_color in ['Dark Gray','Black'] :
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.red = 245')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.green = 245')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.blue = 245')
        else :
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.red = 10')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.green = 10')
            engine.adobe.rpc_eval('app.activeDocument.activeLayer.textItem.color.rgb.blue = 10')
        
        disclaimer_text = "(c) WARNER BROS. ENTERTAINMENT.\r"
        disclaimer_text += "THIS MATERIAL IS THE PROPERTY OF WARNER BROS. ANIMATION.\r"
        disclaimer_text += "IT IS UNPUBLISHED & MUST NOT BE DISTRIBUTED,\r"
        disclaimer_text += "DUPLICATED OR USED IN ANY MANNER, EXCEPT FOR PRODUCTION\r"
        disclaimer_text += "PURPOSES, AND MAY NOT BE SOLD OR TRANSFERRED.\r"
        disclaimer.textItem.contents = disclaimer_text
        disclaimer.move(model_sheet_group, engine.adobe.ElementPlacement.INSIDE)
        
    # merge the model sheet group
    model_sheet_group.merge()
    
    # set the original units
    engine.adobe.app.preferences.rulerUnits =original_ruler_units
    
    # set the background color back to the original color
    rpc_cmd = 'app.backgroundColor.rgb.red = '+str(original_bg_color_red)
    engine.adobe.rpc_eval(rpc_cmd)
    rpc_cmd = 'app.backgroundColor.rgb.green = '+str(original_bg_color_green)
    engine.adobe.rpc_eval(rpc_cmd)
    rpc_cmd = 'app.backgroundColor.rgb.blue = '+str(original_bg_color_blue)
    engine.adobe.rpc_eval(rpc_cmd)