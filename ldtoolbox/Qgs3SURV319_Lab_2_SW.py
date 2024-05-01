# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Plugin for SURV319 Minilab 1
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
import matplotlib
matplotlib.use('Qt5Agg')
import scipy.integrate as integrate
from processing import run,runAndLoadResults
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsMessageLog,QgsProcessingAlgorithm,
                       QgsProcessingUtils,QgsProcessingParameterString,
                       QgsProcessingParameterEnum,QgsProcessingParameterRasterLayer,
                       QgsProcessingFeedback,QgsVectorLayer,
                       QgsProject,QgsLayerTreeLayer)

class SURV319lab2SW(QgsProcessingAlgorithm):
    #Variables for choosing the standard storm, the climate change storm, the storage tank and subcatchment to analyse.
    STORM1='TS1'
    STORM2='TS2'
    TANK='Tank'
    SUB='Sub'

    #Variables to be input to the ldtoolbox:swmmsim algorithm.
    TITLE = 'TITLE'
    OPTIONS = 'options'
    REPORT = 'report'
    RAINGAGES = 'raingages'
    SUBCATCHMENTS = 'subcatchments'
    SUBAREAS = 'subareas'
    INFILTRATION = 'infiltration'
    JUNCTIONS = 'junctions'
    OUTFALLS = 'outfalls'
    STORAGE = 'storage'
    CONDUITS = 'conduits'
    OUTLETS = 'outlets'
    XSECTIONS = 'xsections'
    TIMESERIES = 'timeseries'

    #variables for selecting which subcatchments and storage tanks to analyse.
    TANKSLIST=[]
    SUBSLIST=[]
    SUBCATCHMENT_TO_PLOT=set()
    NODES_TO_PLOT=set()
    SUB_DICT={}
    NODE_DICT={}
    SUBS_DICT={}
    TANK_DICT={}
    SUBCATCHMENT_OUTPUT = 'Subcatchment_output_layer'
    NODE_OUTPUT = 'Node_output_layer'

    #Variable for storing the pit-filled DEM.
    DEM='DEM'
    DEMNAME=''

    def initAlgorithm(self, config):

        #First we add a parameter for the title of the SWMM Simulation
        self.addParameter(QgsProcessingParameterString(self.TITLE,'TITLE','SWMM Simulation'))
        #Next we add a parameter for the standard design storm.
        self.addParameter(QgsProcessingParameterString(self.STORM1,'Rainfall timeseries for the standard design storm','TS1'))
        #Next we add a parameter for the climate change design storm.
        #Insert code here.
        self.addParameter(QgsProcessingParameterString(self.STORM2,'Rainfall timeseries for the future design storm','TS2'))

        #Next we populate an enumerator from which we choose the subcatchments to analyse.
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        for layer in layers:
            if layer.name().lower() == self.SUBCATCHMENTS.lower():
                for feature in layer.getFeatures():
                    self.SUBSLIST.append(feature['Name'])
        for i,member in enumerate(self.SUBSLIST):
                self.SUBS_DICT[i]=member

        self.addParameter(QgsProcessingParameterEnum(self.SUB,'Subcatchment to analyse',self.SUBSLIST))

        #Next we populate an enumerator from which we choose the tanks to analyse.
        for layer in layers:
            if layer.name().lower() == self.STORAGE.lower():
                for feature in layer.getFeatures():
                    self.TANKSLIST.append(feature['name'])
        for i,member in enumerate(self.TANKSLIST):
                self.TANK_DICT[i]=member
        self.addParameter(QgsProcessingParameterEnum(self.TANK,'Storage tank to analyse',self.TANKSLIST))

        #Next we create a parameter for choosing the name of the pit-filled DEM.
        for layer in layers:
            if "PitFilled" in layer.name():
                self.DEMNAME=layer.name()
        self.addParameter(QgsProcessingParameterRasterLayer(self.DEM,'Pit-filled DEM',self.DEMNAME))

    def processAlgorithm(self, parameters, context, feedback):
        #The following code block ensures that the catchment's rain gage's attribute tables references the standard design storm time series in its 'Source Name' field.
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        for layer in layers:
            if layer.name().lower() == self.RAINGAGES.lower():
                layer.startEditing()
                for feature in layer.getFeatures():
                    layer.changeAttributeValue(feature.id(),feature.fields().indexFromName('Source Name'),self.parameterAsString(parameters,self.STORM1,context))
                layer.commitChanges()
            #Next we set up the parameter dictionary for the ldtoolbox:swmmsim tool.  The output layers will be 'temporary' or 'memory' layers.
            swmm_param= {'TITLE': self.parameterAsString(parameters,self.TITLE,context),
                  'OPTIONS': self.OPTIONS,'REPORT': self.REPORT,
                  'RAINGAGES': self.RAINGAGES,'SUBCATCHMENTS': self.SUBCATCHMENTS,
                  'SUBAREAS': self.SUBAREAS,'INFILTRATION': self.INFILTRATION,
                  'JUNCTIONS': self.JUNCTIONS,'OUTFALLS': self.OUTFALLS,
                  'STORAGE': self.STORAGE,'CONDUITS': self.CONDUITS,
                  'XSECTIONS': self.XSECTIONS,'TIMESERIES': self.TIMESERIES,
                  'NODE_OUTPUT': 'memory:','LINK_OUTPUT': 'memory:',
                  'SUBCATCHMENT_OUTPUT': 'memory:'
                  }
        #The next line calls the ldtoolbox:swmmsim tool and loads the results into the project.
        swmmoutput=runAndLoadResults("ldtoolbox:swmmsim", swmm_param,feedback=QgsProcessingFeedback())
        #The next code block adds the features in a newly created subcatchment and node layer to dictionaries and lists.
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        for layer in layers:
            if layer.name().lower() == self.SUBCATCHMENT_OUTPUT.lower():
                for feature in layer.getFeatures():
                    self.SUBCATCHMENT_TO_PLOT.add(feature['Subcatchment'])
            if layer.name().lower() == self.NODE_OUTPUT.lower():
                for feature in layer.getFeatures():
                    self.NODES_TO_PLOT.add(feature['Node'])
        #In the next codeblock we choose which subcatchment to plot.  This comes from the 'Subcatchment to analyse' dropdown box.
        sub=self.SUBS_DICT[self.parameterAsEnum(parameters,self.SUB,context)]

        for i,member in enumerate(self.SUBCATCHMENT_TO_PLOT):
            if member==sub:
                self.SUB_DICT[member]=i
        #In the next codeblock we choose what tank to plot.  This comes from the 'Storage tank to analyse' dropdown box.
        tank=self.TANK_DICT[self.parameterAsEnum(parameters,self.TANK,context)]
        for i,member in enumerate(self.NODES_TO_PLOT):
            if member==tank:
                self.NODE_DICT[member]=i

        #Now we generate the plot for the standard storm by calling the ldtoolbox:swmmplot algorithm.  We will plot both the inflow and flooding.
        swmmplot_param={'SUBCATCHMENTS': self.SUB_DICT[sub],
              'NODES':self.NODE_DICT[tank],
              'nodeboolinflow':True,
              'nodeboolflooding':True}
        #The ouput from the ldtoolbox:swmmplot tool is saved to a variable named 'plotoutput'.  The output is a matplotlib figure (similar to a Matlab figure).  We can modify the attributes of the figure by modifying components of 'plotoutput'.
        plotoutput=run("ldtoolbox:swmmplot",swmmplot_param,feedback=QgsProcessingFeedback())
        #Next we remove the layers from the current project created by the ldtools:swmmsim algorithm as we no longer need them once we have created the plot.
        QgsProject.instance().removeMapLayer(swmmoutput['NODE_OUTPUT'])
        QgsProject.instance().removeMapLayer(swmmoutput['LINK_OUTPUT'])
        QgsProject.instance().removeMapLayer(swmmoutput['SUBCATCHMENT_OUTPUT'])

        #Next we modify the title of the plot.
        plotoutput['axis1'].set_title('Standard Storm\nSubcatchment '+sub)

        #Now we modify the raingages feature class to change from 'Source Name' "Standard Storm" to 'Source Name' "Climate Change Storm".

        layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        for layer in layers:
            if layer.name().lower() == self.RAINGAGES.lower():
                layer.startEditing()
                for feature in layer.getFeatures():
                    layer.changeAttributeValue(feature.id(),feature.fields().indexFromName('Source Name'),self.parameterAsString(parameters,self.STORM2,context))
                layer.commitChanges()


        #Now we run the model again with the climate change storm.
        

        #Insert single line of code here to run the model for the climate change storm.
        

        #Now we generate the plot for the climate change storm.

        #Insert single line of code here.  Assign the output of the ldtoolboxLswmmplot tool to a variable named 'plotoutput2'.


        #Next we remove the layers created by the ldtools:swmmsim algorithm as we no longer need them once we have created the plot.
        #Insert codeblock here.
        

        #Next we modify the title of the plot.
        #Insert single line of code here.
        

        #Now we calculate the volume of water that floods by retrieving the timestamps and flooding rate from the plot output and then using the scipy intergrate.cumtrapz algorithm to numerically integrate the flooding rate versus time.

        dates=plotoutput2['node_time'][0]
        numberdate=[]
        for i,member in enumerate(dates):
            numberdate.append(member.timestamp())
        flooding=array(plotoutput2['node_flooding'][0])
        floodvolume=integrate.cumtrapz(flooding,x=array(numberdate))

        #Next we add some text to the plot indicating the amount of water that has flooded.
        plotoutput2['axis1'].text(0.75, 0.5,r'Flooding volume = {0:.2f} m$^3$'.format(floodvolume[-1]/1000.), horizontalalignment='center',verticalalignment='center',transform=plotoutput2['axis1'].transAxes)

        #Now we set the Source Name field from the raingauges feature class back to the standard storm.

        #Insert codeblock here.

        #There are no more new codeblocks to add in this python script after this point. 
        # Please read through the rest of the file so that you can see how the tool determines 
        # where any water that floods from the tank will flow, and then shows the path the water will take in the QGIS project.

        #Now we need to retrieve the coordinates of the storage tank so that we can feed these into the r.drain algorithm.
        for layer in layers:
            if layer.name().lower() == self.STORAGE.lower():
                for feature in layer.getFeatures():
                    idx=feature.fields().indexFromName('name')
                    if feature.attributes()[idx]==tank:
                        geom = feature.geometry()
                        [x,y] = geom.asPoint()

        #Now we run the r.drain algorithm

        #First we create a dictionary of input parameters.

        drain_param={'input' : self.parameterAsRasterLayer(parameters,self.DEM,context),
        'start_coordinates' : str(x)+','+str(y),
        '-c' : False,'-a' : False,'-n' : False,'-d' : False,
        'output' : QgsProcessingUtils.tempFolder()+'/output.tif',
        'drain' : QgsProcessingUtils.tempFolder()+'/drain.shp',
        'GRASS_REGION_CELLSIZE_PARAMETER' : 0.0000,
        'GRASS_SNAP_TOLERANCE_PARAMETER' : -1,
        'GRASS_MIN_AREA_PARAMETER' : 0.0001,
        'GRASS_OUTPUT_TYPE_PARAMETER' : 0
        }
        #Then we run the algorithm.
        run("grass7:r.drain",drain_param,feedback=QgsProcessingFeedback())
        #Now we load the drain.shp output (the path the water will flow down) into a QGIS layer called vlayer.
        vlayer = QgsVectorLayer(QgsProcessingUtils.tempFolder()+'/drain.shp','Overflow path', "ogr")
        #Now we create the SURV319 Lab 2 group in the project's table of contents if it doesn't exist already.
        root = QgsProject.instance().layerTreeRoot()
        if QgsProject.instance().layerTreeRoot().findGroup('SURV319 Lab 2 Layers'):
            myGroup1=QgsProject.instance().layerTreeRoot().findGroup('SURV319 Lab 2 Layers')
        else:
            myGroup1 = root.insertGroup(0,'SURV319 Lab 2 Layers')
        #Next we assign a coordinate reference system to the drain shapefile.
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        for layer in layers:
            if layer.name().lower() == self.STORAGE.lower():
                crs= layer.crs()
        vlayer.setCrs(crs)
        #Now we add the layer vlayer to the project, but do not display it yet.
        QgsProject.instance().addMapLayer(vlayer,False)
        #Next we modify the layer by setting its line width to 0.7.
        props=vlayer.renderer().symbol()
        props.setWidth(0.7)

        #Finally we add vlayer to the SURV3019 Lab 2 layer group.
        myGroup1.insertChildNode(1,QgsLayerTreeLayer(vlayer))

        return  {}

    def name(self):
        return 'surv319lab2SW'
    def tr(self, string):
        return QCoreApplication.translate('surv319lab2SW', string)

    def icon(self):
        return QIcon(":/plugins/ldtoolbox/swmm.png")

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SURV319 Lab 2 SW')
    def shortHelpString(self):
        file=os.path.realpath(__file__)
        file = os.path.join(os.path.dirname(file),'Qgs3SURV319_Lab_2_SW.help')
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

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading | QgsProcessingAlgorithm.FlagDisplayNameIsLiteral

    def createInstance(self):
        return SURV319lab2SW()
