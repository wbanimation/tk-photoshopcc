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
import os

# standard toolkit logger
logger = sgtk.platform.get_logger(__name__)


def publish_output(engine, thumnail_path, published_file_path, sg_asset, sg_task, sg_version_status, version_name, version_playlists) :

#     publisher = sgtk.platform.current_bundle()
    upload_path = published_file_path
    path_to_movie = None
    path_to_frames = published_file_path
    version_desrciption = 'Updated Model Sheet...'    
    asset_name = sg_asset['name']
    
    # brute force method for getting pubfile name
    # need to replace with publisher method above
    try :
        publish_directory,pubfile_name = upload_path.rsplit(os.sep,1)
    except :
        pubfile_name = upload_path
    
    engine.clear_busy()
    engine.show_busy(
        version_name,
        "Creating Version...<br>" 
        )
    
    # populate the version data to send to SG
    version_data = {
        "project": engine.context.project,
        "code": version_name,
        "description": version_desrciption,
        "entity": sg_asset,
        "sg_task": sg_task,
        "sg_path_to_frames": path_to_frames,
        "sg_path_to_movie": path_to_movie,
        "playlists" : version_playlists,
        "sg_status_list" : sg_version_status,
    }
    
    # create the version
    logger.info("Creating Version...")
    sg_version = engine.shotgun.create("Version", version_data)

    # populate the published file data to send to SG
    pubfile_data = {
        "project": engine.context.project,
        "code": pubfile_name,
        "entity": sg_asset,
        "task": sg_task,
        'version': sg_version,
        'path': {'local_path':path_to_frames,'name':pubfile_name},
    }

    # create the published file
    logger.info("Creating Published File...")
    published_file = engine.shotgun.create("PublishedFile", pubfile_data)

    # make the jpeg proxy and create a published file
    published_jpg_file_path = published_file_path.replace('.psd','.jpg')

    try :
        published_jpg_file_folder,jpg_pubfile_name = published_jpg_file_path.rsplit(os.sep,1)
    except :
        jpg_pubfile_name = published_jpg_file_path

    engine.export_as_jpeg(
            document=engine.adobe.app.activeDocument,
            output_path=published_jpg_file_path,
            max_size=2048,
            quality=12
        )
    
    # populate the published file data to send to SG
    pubfile_data = {
        "project": engine.context.project,
        "code": jpg_pubfile_name,
        "entity": sg_asset,
        "task": sg_task,
        'version': sg_version,
        'path': {'local_path':published_jpg_file_path,'name':jpg_pubfile_name},
    }

    # create the published file for the jpeg proxy
    logger.info("Creating Published File for JPG Proxy..")
    published_file = engine.shotgun.create("PublishedFile", pubfile_data)    
    
    engine.clear_busy()
    engine.show_busy(
        version_name,
        "Uploading Media...<br>" 
            )

    # upload the file to SG
    logger.info("Uploading Version Media...")
    engine.shotgun.upload(
        "Version",
        sg_version["id"],
        upload_path,
        "sg_uploaded_movie"
    )
    
    logger.info("DONE Uploading Media...")
    
    engine.clear_busy()
    
    return sg_version
