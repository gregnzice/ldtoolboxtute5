# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ldtoolbox
                                 A QGIS plugin
 A tooblox of land development related algorithms.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-06-28
        copyright            : (C) 2018 by Greg Leonard
        email                : greg.h.leonard@gmail.com
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
__date__ = '2018-06-28'
__copyright__ = '(C) 2018 by Greg Leonard'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'
from qgis.PyQt.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
from qgis.core import QgsProcessingProvider
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from .Qgs3EpanetAlgorithm import Qgs3EpanetAlgorithm
from .Qgs3SwmmAlgorithm import Qgs3SwmmAlgorithm
from .Qgs3PostProcessEpanet import Qgs3PostProcessEpanet
from .Qgs3PlotSwmm import Qgs3PlotSwmm
from .Qgs3SURV319_Tute_5 import SURV319Tute5
# To add your Lab 1 stormwater modelling tool to the ldtoolbox, you will need to add a new line similar to line 40, except you need to update
# the folder and class reference to point to your Lab 1 stormwater modelling tool.  You also need to add this tool
# to the end of the list of tools in line 81.
from . import resources

class LdtoolboxProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)
    def load(self):
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(self.name(), 'ACTIVATE_LDTools',
                                            self.tr('Activate'), True))
        ProcessingConfig.addSetting(Setting(self.name(),'EPANET_CLI','EPANET command line tool',''))
        ProcessingConfig.addSetting(Setting(self.name(),'SWMM_CLI','SWMM command line tool',''))
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True
    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        ProcessingConfig.removeSetting('ACTIVATE_LDTools')
        ProcessingConfig.removeSetting('EPANET_CLI')
        ProcessingConfig.removeSetting('SWMM_CLI')

    def isActive(self):
        return ProcessingConfig.getSetting('ACTIVATE_LDTools')

    def setActive(self, active):
        ProcessingConfig.setSettingValue('ACTIVATE_LDTools', active)
    def tr(self, string, context=''):
        if context == '':
            context = 'ldtoolboxProvider'
        return QCoreApplication.translate(context, string)
    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        self.algs = [Qgs3EpanetAlgorithm(),Qgs3PostProcessEpanet(),Qgs3SwmmAlgorithm(),Qgs3PlotSwmm(),SURV319Tute5()]
        # For Lab 2, you need to add your Lab 2 stormwater modelling tool to the end of the list in Line 81 to register your
        # tool in the ldtoolbox so it shows up as being available in QGIS.
        for alg in self.algs:
            self.addAlgorithm( alg )

    def icon(self):
        return QIcon(":/plugins/ldtoolbox/engineer.png")
    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'ldtoolbox'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('Land Development Toolbox')

    def longName(self):
        """
        Returns a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.name()
