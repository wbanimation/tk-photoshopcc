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
# import publish_output

# get the standard logger
logger = sgtk.platform.get_logger(__name__)

# cant do a normal import...
model_sheet_layer = imp.load_source('model_sheet_layer', os.path.join(os.path.dirname(os.path.realpath(__file__)),'model_sheet_layer.py'))
publish_output = imp.load_source('publish_output', os.path.join(os.path.dirname(os.path.realpath(__file__)),'publish_output.py'))

today = date.today()

def add_model_sheet_layer(engine) :
    
    # grab all the environment variables that were set for us
    mode = json.loads(os.environ.get('MODELSHEET_EXPORT_MODE'))
    version_playlist_mode = json.loads(os.environ.get('MODELSHEET_VERSION_PLAYLIST_MODE'))
    update_version_status = json.loads(os.environ.get('MODELSHEET_UPDATE_STATUS'))
    copy_version_links = json.loads(os.environ.get('MODELSHEET_COPY_LINKS'))
    copy_version_notes = json.loads(os.environ.get('MODELSHEET_COPY_NOTES'))
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
    fields = ['code','path','task','entity','version','version.Version.sg_status_list','version.Version.entity','version.Version.playlists','project.Project.tank_name',
               'task.Task.sg_task_token','task.Task.content','task.Task.task_assignees','task.Task.sg_task_token']
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
            
            if 'task.Task.content' in sg_pubfile:
                task_name = sg_pubfile['task.Task.content']
            if 'task.Task.task_assignees' in sg_pubfile :
            
                task_assignees = sg_pubfile['task.Task.task_assignees']
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
        
        try:
            version_name = _get_version_name_from_filename(local_path.rsplit(os.sep,1)[1])
        except :
            version_name = ''
        
        engine.clear_busy()
        engine.show_busy(
            version_name,
            "Opening Version... " +
            "<br>" 
            )
        
        # open the photshop file
        file_open = engine.adobe.File(local_path)
        engine.adobe.app.load(file_open)
        
        # get the version name from the current file name
        version_name = _get_version_name_from_filename(engine.adobe.app.activeDocument.name)
        
        engine.show_busy(
            version_name,
            "Adding Model Sheet..." +
            "<br>" 
            )
        
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
        
        # export versions
        if mode == 0 :
            
            engine.show_busy(
                version_name,
                "Finding Next Version to Publish..." +
                "<br>" 
                )
            
            # need to get the correct output folder for the new Published File
            work_template = engine.get_template("work_template")
            publish_template = engine.get_template("publish_template")
            
#             logger.info(' ===== work_template: %s' % work_template)
#             logger.info(' ===== publish_template: %s' % publish_template)
            
            version_number = 1
            looking_for_highest_version = True
            
            # look for the current highest version number for the Design Package     
            filters = [['project','is',context.project],['entity','is',sg_pubfile['version.Version.entity']]]
            fields = ['code','sg_version_number']
            sg_find_versions = engine.shotgun.find("Version",filters,fields)
            
            current_version_name = sg_pubfile['version']['name']
            version_name_base = sg_pubfile['project.Project.tank_name']+'_'+sg_pubfile['version.Version.entity']['name']+'_'+sg_pubfile['task.Task.sg_task_token']+'_v'
            
            for find_version in sg_find_versions :
                
                if find_version['code'].startswith(version_name_base) :
                    if int(find_version['sg_version_number']) > version_number :
                        version_number = int(find_version['sg_version_number'])
            
            version_number +=1
            new_version_name = sg_pubfile['project.Project.tank_name']+'_'+sg_pubfile['version.Version.entity']['name']+'_'+sg_pubfile['task.Task.sg_task_token']+'_v'+str(version_number).zfill(2)
            publish_path = local_path.replace(current_version_name,new_version_name)
            version_playlists = sg_pubfile['version.Version.playlists']
            
            publish_folder = publish_path.rsplit(os.sep,1)[0]
            
            # make sure publish directory exists
            if not os.path.exists(publish_folder) :
                os.makedirs(publish_folder)
            
            # save file to selected folder
            saveOptions = engine.adobe.PhotoshopSaveOptions()
            saveOptions.layers = True
            
            file_save = engine.adobe.File(publish_path)
            engine.adobe.app.activeDocument.saveAs(file_save, saveOptions ,True)

            sg_version = publish_output.publish_output(engine, publish_path, publish_path, sg_pubfile['version.Version.entity'], sg_pubfile['task'], sg_pubfile['version.Version.sg_status_list'], new_version_name, version_playlists)
            
            # close the file
            engine.adobe.app.activeDocument.close(engine.adobe.SaveOptions.DONOTSAVECHANGES)
            
            if copy_version_notes :
                # get the notes attached to the version
                filters = [['project','is',context.project],['note_links','in',sg_pubfile['version']]]
                fields = ['note_links']
                sg_notes = engine.shotgun.find('Note',filters,fields)
                
                for note in sg_notes :
                    note_links = note['note_links']
                    note_links.append(sg_version)
                    data = {'note_links':note_links}
                    result = engine.shotgun.update('Note', note['id'], data)
            
        # export to file system
        elif mode == 1:
            # get the output name from the local_path
            output_filename, extension = _get_output_filename(local_path, filename_prefix, filename_suffix, current_sc, ship_episode)
            output_path = os.path.join(export_folder,output_filename)
            
            engine.clear_busy()
            engine.show_busy(
                version_name,
                "Exporting Photshop Document... " +
                "<br>" 
                )
                    
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
            
            # open the export folder
            if open_export_folder:
                subprocess.check_call(['open' ,export_folder])
            
            # quit photoshop
#             engine.adobe.app.executeAction(engine.adobe.app.charIDToTypeID('quit'), engine.adobe.undefined, engine.adobe.DialogModes.ALL)
    
    engine.clear_busy()
    
    # quit photoshop
    engine.adobe.app.executeAction(engine.adobe.app.charIDToTypeID('quit'), engine.adobe.undefined, engine.adobe.DialogModes.ALL)
    
    # re-enable context switching
    # not that it matters...
    engine._CONTEXT_CHANGES_DISABLED = False
    engine._HEARTBEAT_DISABLED = False
    
    # unset all of the environment variables
    os.unsetenv("MODELSHEET_EXPORT_MODE")
    os.unsetenv("MODELSHEET_UPDATE_STATUS")
    os.unsetenv("MODELSHEET_COPY_LINKS")
    os.unsetenv("MODELSHEET_COPY_NOTES")
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