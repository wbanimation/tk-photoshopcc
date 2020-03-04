# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os 
import sgtk
import json
import imp
import subprocess
from datetime import date

# get the standard logger
logger = sgtk.platform.get_logger(__name__)

# cant do a normal import...
model_sheet_layer = imp.load_source('model_sheet_layer', os.path.join(os.path.dirname(os.path.realpath(__file__)),'model_sheet_layer.py'))

today = date.today()

def add_model_sheet_layer(engine) :
    
    # grab all the environment variables that were set for us
    export_folder = json.loads(os.environ.get('MODELSHEET_EXPORT_FOLDER'))
    open_export_folder =  json.loads(os.environ.get('MODELSHEET_OPEN_EXPORT_FOLDER'))
    photoshop_file_ids = json.loads(os.environ.get('MODELSHEET_PUB_FILE_IDS'))
    filename_prefix = json.loads(os.environ.get('MODELSHEET_PREFIX'))
    filename_suffix =  json.loads(os.environ.get('MODELSHEET_SUFFIX'))
    banner_color = json.loads(os.environ.get('MODELSHEET_BANNER_COLOR'))
    font = json.loads(os.environ.get('MODELSHEET_FONT'))
    project_type = json.loads(os.environ.get('MODELSHEET_PROJECT_TYPE'))
    show_logo = json.loads(os.environ.get('MODELSHEET_SHOW_LOGO'))
    show_labels = json.loads(os.environ.get('MODELSHEET_SHOW_LABELS'))
    show_disclaimer = json.loads(os.environ.get('MODELSHEET_SHOW_DISCLAIMER'))
    show_date = json.loads(os.environ.get('MODELSHEET_SHOW_DATE'))
    
    # get the sg_pubfile information from the file ids all at once
    selected_filter = [['project','is',engine.context.project]]
    fields = ['code','path','task','entity']
    pubfiles_filter = []
    for id in photoshop_file_ids :
        pubfile_filter = ['id', 'is', int(id)]
        pubfiles_filter.append(pubfile_filter)
    selected_filter.append({"filter_operator": "any", "filters": pubfiles_filter })
    sg_pubfiles = engine.shotgun.find("PublishedFile",selected_filter,fields)
    
    # go through published files that were passed from Shotgun
    # first we need to get information from the published files
    # then we need to look up some additional information based on the published file information
    # now open up each file and add the model sheet information
    
    # disable context switching to speed up file loading
    engine._CONTEXT_CHANGES_DISABLED = True
    engine._HEARTBEAT_DISABLED = True
    
    for sg_pubfile in sg_pubfiles :
        
        project_name = ''
        asset_name = ''
        task_name = ''
        asset_type = ''
        version_name = ''
        episode_name = ''
        ship_episode = ''
        current_sc = ''
        sap_number = ''
        assigned_to = ''
    
        local_path = None
        sg_task = None
        task_assignees = None
        
        
        # get the path to the photoshop file
        if sg_pubfile['path']['local_path']:
            local_path = sg_pubfile['path']['local_path']
        
        tk = sgtk.sgtk_from_path(local_path)
        context = tk.context_from_entity("PublishedFile",sg_pubfile['id'])
        
        # get project from published file context
        if 'name' in context.project:
            project_name = context.project['name']
        
        # get task from published file context
        if context.task != None :
            if 'name' in context.task:
                task_name = context.task['name']
        else :
            task_name = ""
        
        # get entity from published file context
        if context.entity != None :
            if 'name' in context.entity:
                asset_name = context.entity['name']
        else :
            asset_name = ""
        
        # get the task information from the pubfile task field
        if sg_pubfile['task']:
            sg_task = sg_pubfile['task']
            # check that we actually need this part...
            task_filter = [['project','is',engine.context.project],
                           ['id','is',sg_task['id']]]
            task_fields = ['content','task_assignees']
            sg_photoshopcc_task = engine.shotgun.find_one("Task",task_filter,task_fields)
            
            if 'content' in sg_photoshopcc_task:
                task_name = sg_photoshopcc_task['content']
            if 'task_assignees' in sg_photoshopcc_task :
            
                task_assignees = sg_photoshopcc_task['task_assignees']
                task_assignees_list = []
                for each_assignee in task_assignees :
                    task_assignees_list.append(each_assignee['name'])
                assigned_to = ', '.join(task_assignees_list)
            
        # get the entity information from the pubfile entity field
        if sg_pubfile['entity']:
            sg_asset = sg_pubfile['entity']
            # check that we actually need this part...
            asset_filter = [['project','is',engine.context.project],
                           ['id','is',sg_asset['id']]]
            asset_fields = ['code',
                            'sg_asset_type',
                            'sg_current_episode',
                            'sg_current_sc',
                            'sg_ship_episode',
                            'sg_ship_episode.CustomEntity01.sg_sap_number',
                            'sg_current_episode.CustomEntity01.sg_episode_number'
                            ]
            sg_photoshopcc_asset = engine.shotgun.find_one("Asset",asset_filter,asset_fields)
            
            if sg_photoshopcc_asset['sg_asset_type'] != None :
                asset_type = sg_photoshopcc_asset['sg_asset_type']
            if sg_photoshopcc_asset['sg_current_episode.CustomEntity01.sg_episode_number'] != None :
                episode_name = sg_photoshopcc_asset['sg_current_episode.CustomEntity01.sg_episode_number']
            if sg_photoshopcc_asset['sg_ship_episode'] != None :
                ship_episode = sg_photoshopcc_asset['sg_ship_episode']['name']
            if sg_photoshopcc_asset['sg_current_sc'] != None :
                current_sc = sg_photoshopcc_asset['sg_current_sc']
            if sg_photoshopcc_asset['sg_ship_episode.CustomEntity01.sg_sap_number'] != None :
                sap_number = sg_photoshopcc_asset['sg_ship_episode.CustomEntity01.sg_sap_number']
        
        # open the photshop file
        file_open = engine.adobe.File(local_path)
        engine.adobe.app.load(file_open)
        
        # get the version name from the current file name
        version_name = _get_version_name_from_filename(engine.adobe.app.activeDocument.name)
        
        # add the model sheet layer
        model_sheet_layer.model_sheet_layer(
                                engine,
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
                                show_logo,
                                show_labels,
                                show_date,
                                show_disclaimer
                                )
        
        # get the output name from the local_path
        output_filename, extension = _get_output_filename(local_path, filename_prefix, filename_suffix, current_sc, ship_episode)
        output_path = os.path.join(export_folder,output_filename)
                    
        # make sure directory exists
        if not os.path.exists(export_folder) :
            os.makedirs(export_folder)
        
        # save file to selected folder
        saveOptions = engine.adobe.PhotoshopSaveOptions()
        saveOptions.layers = True

        # save the file as large document format is required
        # need to find out how to do this...
        if extension == 'psb' :
#                 saveOptions.formatOptions = engine.adobe.FormatOptions.STANDARDBASELINE
            pass
        
        file_save = engine.adobe.File(output_path)
        engine.adobe.app.activeDocument.saveAs(file_save, saveOptions ,True)
        engine.adobe.app.activeDocument.close(engine.adobe.SaveOptions.DONOTSAVECHANGES)
    
    # re-enable context switching
    # not that it matters...
    engine._CONTEXT_CHANGES_DISABLED = False
    engine._HEARTBEAT_DISABLED = False
    
    # open the export folder
    if open_export_folder:
        subprocess.check_call(['open' ,export_folder])
    
    # unset all of the environment variables
    os.unsetenv("MODELSHEET_EXPORT_FOLDER")
    os.unsetenv("MODELSHEET_OPEN_EXPORT_FOLDER")
    os.unsetenv("MODELSHEET_PUB_FILE_IDS")
    os.unsetenv("MODELSHEET_PREFIX")
    os.unsetenv("MODELSHEET_SUFFIX")
    os.unsetenv("MODELSHEET_BANNER_COLOR")
    os.unsetenv("MODELSHEET_FONT")
    os.unsetenv("MODELSHEET_PROJECT_TYPE")
    os.unsetenv("MODELSHEET_SHOW_LOGO")
    os.unsetenv("MODELSHEET_SHOW_LABELS")
    os.unsetenv("MODELSHEET_SHOW_DISCLAIMER")
    os.unsetenv("MODELSHEET_SHOW_DATE")
    
    # quit photoshop
    engine.adobe.app.executeAction(engine.adobe.app.charIDToTypeID('quit'), engine.adobe.undefined, engine.adobe.DialogModes.ALL)


def _get_version_name_from_filename(filename):
    
    try :
        version_name,extension = filename.rsplit('.')
        return version_name
    except :
        return filename


def _get_output_filename(local_path, filename_prefix, filename_suffix, current_sc, ship_episode):
    
    extension = None
    
    try :
        input_path,output_filename = local_path.rsplit(os.sep,1)
    except :
        output_filename = local_path
    
    try :
        output_basename,extension = output_filename.rsplit('.',1)
    except :
        output_basename = output_filename
    
    # add the filename prefix and suffix
    if filename_prefix != 'None' :
        if filename_prefix == 'Current Scene' :
            filename_prefix = current_sc
        elif filename_prefix == 'Ship Episode' :
            filename_prefix = ship_episode
        if filename_prefix != '' :
            output_basename = filename_prefix+'_'+output_basename
        
    if filename_suffix != 'None' :
        if filename_suffix == 'YYYYMMDD' :
            filename_suffix = str(today.strftime('%Y%m%d'))
        output_basename = output_basename+'_'+filename_suffix
    
    if extension != None :
        output_filename = output_basename+'.'+extension
    else :
        output_filename = output_basename
    
    return output_filename, extension