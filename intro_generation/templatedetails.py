import json
import logging

# required for SherpaFunctions
import sherpafunctions as sf

from config import Config
cfg = Config()


class TemplateDetails:
    textLine01 = ''
    textLine01Font = ''
    textLine01FontSize = 20
    textLine01FontColorR = 0
    textLine01FontColorG = 0
    textLine01FontColorB = 0

    textLine02 = ''
    textLine02Font = ''
    textLine02FontSize = 20
    textLine02FontColorR = 0
    textLine02FontColorG = 0
    textLine02FontColorB = 0

    textLine03 = ''
    textLine03Font = ''
    textLine03FontSize = 20
    textLine03FontColorR = 0
    textLine03FontColorG = 0
    textLine03FontColorB = 0

    templateID = ''

    templateBGColorR = 0
    templateBGColorG = 0
    templateBGColorB = 0

    firstclip = ''


    def readtemplate(self, projectid):
        status = "Reading Template"
        #try:
        projectpath = cfg.VIDEOS_LOCATION + str(projectid) + '/'
        with open(projectpath + 'template.json') as json_file:
            logging.debug('02 - Project Path' + projectpath + 'template.json')
            data = json.load(json_file)
            logging.debug('templateid: ' + str(data['templateid']))
            logging.debug(str(data['textlines']))

            d = data['textlines']
            for key in d:
                print(key, 'corresponds to', d[key])
                line = d[key]
                if key == "1":
                    self.textLine01 = line['text']
                    self.textLine01Font = './fonts/' + line['font'] + '.ttf'
                    self.textLine01FontSize = sf.fontsize(line['fontsize'])
                    self.textLine01FontColorR = int(line['fontcolorR'])
                    self.textLine01FontColorG = int(line['fontcolorG'])
                    self.textLine01FontColorB = int(line['fontcolorB'])
                elif key == "2":
                    self.textLine02 = line['text']
                    self.textLine02Font = './fonts/' + line['font'] + '.ttf'
                    self.textLine02FontSize = sf.fontsize(line['fontsize'])
                    self.textLine02FontColorR = int(line['fontcolorR'])
                    self.textLine02FontColorG = int(line['fontcolorG'])
                    self.textLine02FontColorB = int(line['fontcolorB'])
                elif key =="3":
                    self.textLine03 = line['text']
                    self.textLine03Font = './fonts/' + line['font'] + '.ttf'
                    self.textLine03FontSize = sf.fontsize(line['fontsize'])
                    self.textLine03FontColorR = int(line['fontcolorR'])
                    self.textLine03FontColorG = int(line['fontcolorG'])
                    self.textLine03FontColorB = int(line['fontcolorB'])

            # for p in data['textlines']:
            #     if p['textLine'] == 0:
            #         self.textLine01 = p['text']
            #         self.textLine01Font = './fonts/' + p['font'] + '.ttf'
            #         self.textLine01FontSize = sf.fontsize(p['fontsize'])
            #         self.textLine01FontColorR = int(p['fontcolorR'])
            #         self.textLine01FontColorG = int(p['fontcolorG'])
            #         self.textLine01FontColorB = int(p['fontcolorB'])
            #
            #         logging.debug('text: ' + p['text'])
            #         logging.debug('font: ' + './fonts/' + p['font'] + '.ttf')
            #         logging.debug('fontsize: ' + sf.fontsize(p['fontsize']))
            #
            #         print('')
            #     elif p['textLine'] == 1:
            #         self.textLine02 = p['text']
            #         self.textLine02Font = './fonts/' + p['font'] + '.ttf'
            #         self.textLine02FontSize = sf.fontsize(p['fontsize'])
            #         self.textLine02FontColorR = int(p['fontcolorR'])
            #         self.textLine02FontColorG = int(p['fontcolorG'])
            #         self.textLine02FontColorB = int(p['fontcolorB'])
            #
            #         print('text: ' + p['text'])
            #         print('font: ' + './fonts/' + p['font'] + '.ttf')
            #         print('fontsize: ' + sf.fontsize(p['fontsize']))
            #
            #         print('')
            #     elif p['textLine'] == 2:
            #         self.textLine03 = p['text']
            #         self.textLine03Font = './fonts/' + p['font'] + '.ttf'
            #         self.textLine03FontSize = sf.fontsize(p['fontsize'])
            #         self.textLine03FontColorR = int(p['fontcolorR'])
            #         self.textLine03FontColorG = int(p['fontcolorG'])
            #         self.textLine03FontColorB = int(p['fontcolorB'])
            #
            #         print('text: ' + p['text'])
            #         print('font: ' + './fonts/' + p['font'] + '.ttf')
            #         print('fontsize: ' + sf.fontsize(p['fontsize']))
            #
            #         print('')

        self.templateID = str(data['templateid'])

        self.templateBGColorR = int(data['backgroundcolorR'])
        self.templateBGColorG = int(data['backgroundcolorG'])
        self.templateBGColorB = int(data['backgroundcolorB'])

        self.firstclip = data['firstclip']
        #except Exception as e:
        #    status = str(e)

        logging.debug('readtemplate: Status'+status)


