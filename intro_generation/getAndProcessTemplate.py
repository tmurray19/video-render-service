import logging
import os
import json

from templatedetails import TemplateDetails as template_details
import createtemplate01 as template_1
import createtemplate02 as template_2
import createtemplate03 as template_3
import createtemplate04 as template_4
import createtemplate05 as template_5
import createtemplate06 as template_6
import createtemplate07 as template_7

from datetime import datetime

from config import Config
cfg = Config()

def getandprocesstemplate(proj_id):
    logging.debug('Starting intro creation instance')

    # Get Template Config Details
    # from template.json
    template_info = template_details()
    template_info.readtemplate(proj_id)
    logging.debug('Template details received for {}'.format(proj_id))
    logging.debug('getandprocesstemplate: got template details' + str(template_info.templateID))

    process_status = None
    transparent = False

    if str(template_info.templateID) == "1":
        process_status = template_1.createintro(proj_id)
    if str(template_info.templateID) == "2":
        process_status = template_2.createintro(proj_id)
        transparent = True
    if str(template_info.templateID) == "3":
        process_status = template_3.createintro(proj_id)
    if str(template_info.templateID) == "4":
        process_status = template_4.createintro(proj_id)
        transparent = True
    if str(template_info.templateID) == "5":
        process_status = template_5.createintro(proj_id)
    # Blank - Black BG
    if str(template_info.templateID) == "6":
        process_status = template_6.createintro(proj_id)
    # Blank - White BG
    if str(template_info.templateID) == "7":
        process_status = template_7.createintro(proj_id)

    return process_status, transparent



