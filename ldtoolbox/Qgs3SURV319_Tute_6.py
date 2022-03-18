# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Plugin for SURV319 Tute 9
                                 A QGIS plugin
                              -------------------
        Date                 : July 2018
        Copyright            : (C) 2018 by Greg Leonard
        Email                : greg.h.leonard@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Greg Leonard'
__date__ = 'July 2018'
__copyright__ = '(C) 2018 by Greg Leonard'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
from numpy import array
from processing import run,runAndLoadResults
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsMessageLog,QgsProcessingAlgorithm,
                       QgsProcessingUtils,QgsProcessingParameterString,
                       QgsProcessingParameterEnum,QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingFeedback,QgsVectorLayer,
                       QgsProcessing,
                       QgsProcessingUtils,
                       QgsRasterLayer,
                       QgsProject,
                       QgsLayerTreeLayer)

class SURV319Tute9(QgsProcessingAlgorithm):

    #Variables to assign names of layers to.
    DEM='DEM'
    PITMASK='PITMASK'
    PITFILLEDDEM='PFDEM'
    DEMNAME=''
    PITMASKNAME=''
    PFDEMNAME=''
    def initAlgorithm(self, config):

        #We need parameters for the DEM to pit fill, name of Pit Mask Vector layer and the destination raster layer in which the pit filled DEM will be placed.
        #Provide code for adding the input raster layer parameter here.

        self.addParameter(QgsProcessingParameterVectorLayer(self.PITMASK,'Pit Mask',[QgsProcessing.TypeVectorPoint],self.PITMASKNAME,False))

        #Provide code for adding the destination raster layer parameter here.


    def processAlgorithm(self, parameters, context, feedback):

        #We need to get the extents and pixel size of the input DEM to use as inputs for the GDAL Rasterize function to convert the Pit Mask vector layer to a raster layer that has a value of 1 underneath pit(s) and 0 everywhere else.


        rlayer=self.parameterAsRasterLayer(parameters,self.DEM,context)
        ext = rlayer.extent()
        #Provide the code to get the input raster's xmin,xmax,ymin,ymax,pixelSizeX and PixelSizeY here.

        #Now we set up a parameter dictionary to input to the gdal:rasterize tool.
        rasterize_param={ 'BURN' : 1, 'DATA_TYPE' : 5, 'EXTENT' :str(xmin)+','+str(xmax)+','+str(ymin)+','+str(ymax)+' [EPSG:'+rlayer.crs().authid() +']', 'FIELD' : None, 'HEIGHT' : pixelSizeY, 'INIT' : 0, 'INPUT' : self.parameterAsVectorLayer(parameters,self.PITMASK,context), 'INVERT' : False, 'NODATA' : 0, 'OPTIONS' : '', 'OUTPUT' : QgsProcessingUtils.tempFolder()+'/OUTPUT.tif', 'UNITS' : 1, 'WIDTH' : pixelSizeX}

        #Here we run the gdal:rasterize tool with the rasterize_param dictionary and pipe any feedback into the processing log.

        #Provide the code to run the gdal:rasterize tool here.

        outLayer = self.parameterAsOutputLayer(parameters, self.PITFILLEDDEM, context)
        #Below we set up a parameter dictionary for the TauDEM pit fill tool.

        #Provide the code to set up the parameter dictionary to be input to the taudem:pitremove tool.

        #Below we run the taudem:pitremove tool with the pitfill_param dictionary and pipe any feedback into the processing log.
        run("taudem:pitremove",pitfill_param,feedback=QgsProcessingFeedback())

        #Below we go about adding the pit-filled DEM to the active project's Layers panel.
        rlayer = QgsRasterLayer(outLayer,'WakariDEM_PitFilled')
        #Below we add the layer to project but do not display it.
        QgsProject.instance().addMapLayer(rlayer,False)
        #Here we are locating the group called 'DEMs' so that we can add the new layer to this group.
        root = QgsProject.instance().layerTreeRoot()
        myGroup1=QgsProject.instance().layerTreeRoot().findGroup('DEMs')
        myGroup1.insertChildNode(1,QgsLayerTreeLayer(rlayer))
        return  {}

    def name(self):
        return 'surv319tute9'
    def tr(self, string):
        return QCoreApplication.translate('surv319tute9', string)

    def icon(self):
        return QIcon(":/plugins/ldtoolbox/swmm.png")

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SURV319 Tute 9')
    def shortHelpString(self):
        file=os.path.realpath(__file__)
        file = os.path.join(os.path.dirname(file),'Qgs3SURV319_Tute_9.help')
        if not os.path.exists(file):
            return ''
        with open(file) as helpf:
            help=helpf.read()
        return help

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'SWMM'

    def createInstance(self):
        return SURV319Tute9()
