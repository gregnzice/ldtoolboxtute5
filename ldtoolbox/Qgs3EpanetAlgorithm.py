# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Qgs3Epanet
                                 A QGIS plugin
 Implementation of Epanet within QGIS3.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
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
import getpass
import io
import datetime
import re
from sys import platform
if platform=='linux' or platform=='darwin':
    import pwd
import subprocess
from operator import itemgetter
from numpy import mean,float32
#from processing.core.ProcessingLog import ProcessingLog
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication,QVariant
from qgis.core import (QgsProcessing,
                       QgsMessageLog,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingUtils,
                       QgsProcessingParameterString,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingException,
                       QgsDefaultValue,
                       QgsVectorLayer,
                       QgsProject,
                       QgsField,
                       QgsFields,
                       QgsWkbTypes,
                       QgsFeature,
                       QgsVectorLayerJoinInfo,
                       Qgis,
                       QgsProcessingParameterFeatureSink)

class Qgs3EpanetAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    TITLE      = 'TITLE'
    # layers
    JUNCTIONS  = 'JUNCTIONS'
    RESERVOIRS = 'RESERVOIRS'
    TANKS      = 'TANKS'
    PIPES      = 'PIPES'
    PUMPS      = 'PUMPS'
    VALVES     = 'VALVES'
    EMITTERS   = 'EMITTERS'
    SOURCES    = 'SOURCES'

    # tables
    DEMANDS    = 'DEMANDS'
    STATUS     = 'STATUS'
    PATTERNS   = 'PATTERNS'
    CURVES     = 'CURVES'
    CONTROLS   = 'CONTROLS'
    QUALITY    = 'QUALITY'
    MIXING     = 'MIXING'
    RULES      = 'RULES'

    # key values
    ENERGY     = 'ENERGY'
    REACTIONS  = 'REACTIONS'
    TIMES      = 'TIMES'
    REPORT     = 'REPORT'
    OPTIONS    = 'OPTIONS'

    NODE_TABLE_OUTPUT = 'NODE_TABLE_OUTPUT'
    TIME_AGGREGATE_NODE_TABLE_OUTPUT = 'TIME_AGGREGATE_NODE_TABLE_OUTPUT'
    LINK_TABLE_OUTPUT = 'LINK_TABLE_OUTPUT'
    TIME_AGGREGATE_LINK_TABLE_OUTPUT = 'TIME_AGGREGATE_LINK_TABLE_OUTPUT'

    # everything else
    ADDITIONAL_FILE = 'ADDITIONAL_FILE'


    def name(self):
        return 'epanetsim'
    def tr(self, string):
        return QCoreApplication.translate('epanetsim', string)

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterString(self.TITLE,'TITLE','EPANET Simulation'))
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]

        flag=0
        for layer in layers:
            if layer.name().lower() == self.JUNCTIONS.lower():
                flag=1
                #QgsMessageLog.logMessage(layer.name(),tag="Epanet Processing")
                self.addParameter(QgsProcessingParameterVectorLayer(self.JUNCTIONS,'Junctions Layer',[QgsProcessing.TypeVectorPoint],layer.name()+ ' ['+layer.crs().authid()+']'))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.JUNCTIONS,'Junctions Layer',[QgsProcessing.TypeVectorPoint],'[not selected]'))
        flag=0
        for layer in layers:
            if layer.name().lower() == self.PIPES.lower():
                flag=1

                self.addParameter(QgsProcessingParameterVectorLayer(self.PIPES,'Pipes Layer',[QgsProcessing.TypeVectorLine],layer.name()+ ' ['+layer.crs().authid()+']'))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.PIPES,'Pipes Layer',[QgsProcessing.TypeVectorLine],'[not selected]'))
        flag=0
        for layer in layers:
            if layer.name().lower() == self.RESERVOIRS.lower():
                flag=1

                self.addParameter(QgsProcessingParameterVectorLayer(self.RESERVOIRS,'Reservoirs Layer',[QgsProcessing.TypeVectorPoint],layer.name()+ ' ['+layer.crs().authid()+']'))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.RESERVOIRS,'Reservoirs Layer',[QgsProcessing.TypeVectorPoint],'[not selected]'))
        flag=0
        for layer in layers:
            if layer.name().lower() == self.TANKS.lower():
                flag=1

                self.addParameter(QgsProcessingParameterVectorLayer(self.TANKS,'Tanks Layer',[QgsProcessing.TypeVectorPoint],layer.name()+ ' ['+layer.crs().authid()+']'))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.TANKS,'Tanks Layer',[QgsProcessing.TypeVectorPoint],'[not selected]'))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.PUMPS.lower():
                flag=1

                self.addParameter(QgsProcessingParameterVectorLayer(self.PUMPS,'Pumps Layer',[QgsProcessing.TypeVectorPoint,QgsProcessing.TypeVectorLine],layer.name()+ ' ['+layer.crs().authid()+']'))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.PUMPS,'Pumps Layer',[QgsProcessing.TypeVectorPoint,QgsProcessing.TypeVectorLine],'[not selected]'))
        flag=0
        for layer in layers:
            if layer.name().lower() == self.VALVES.lower():
                flag=1

                self.addParameter(QgsProcessingParameterVectorLayer(self.VALVES,'Valves Layer',[QgsProcessing.TypeVectorPoint,QgsProcessing.TypeVectorLine],layer.name()+ ' ['+layer.crs().authid()+']',True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.VALVES,'Valves Layer',[QgsProcessing.TypeVectorPoint,QgsProcessing.TypeVectorLine],'',True))
        flag=0
        for layer in layers:
            if layer.name().lower() == self.EMITTERS.lower():
                flag=1

                self.addParameter(QgsProcessingParameterVectorLayer(self.EMITTERS,'Emitters Layer',[QgsProcessing.TypeVectorPoint],layer.name()+ ' ['+layer.crs().authid()+']',True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.EMITTERS,'Emitters Layer',[QgsProcessing.TypeVectorPoint],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.DEMANDS.lower():
                flag=1

                self.addParameter(QgsProcessingParameterVectorLayer(self.DEMANDS,'Demands Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.DEMANDS,'Demands Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.STATUS.lower():
                flag=1

                self.addParameter(QgsProcessingParameterVectorLayer(self.STATUS,'Status Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.STATUS,'Status Table',[QgsProcessing.TypeVector],'',True))
        flag=0
        for layer in layers:
            if layer.name().lower() == self.PATTERNS.lower():
                flag=1
                self.addParameter(QgsProcessingParameterVectorLayer(self.PATTERNS,'Patterns Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.PATTERNS,'Patterns Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.CURVES.lower():
                flag=1
                self.addParameter(QgsProcessingParameterVectorLayer(self.CURVES,'Curves Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.CURVES,'Curves Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.CONTROLS.lower():
                flag=1
                self.addParameter(QgsProcessingParameterVectorLayer(self.CONTROLS,'Controls Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.CONTROLS,'Controls Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.QUALITY.lower():
                flag=1
                self.addParameter(QgsProcessingParameterVectorLayer(self.QUALITY,'Quality Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.QUALITY,'Quality Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.MIXING.lower():
                flag=1
                self.addParameter(QgsProcessingParameterVectorLayer(self.MIXING,'Mixing Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.MIXING,'Mixing Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.TIMES.lower():
                flag=1
                self.addParameter(QgsProcessingParameterVectorLayer(self.TIMES,'Times Table',[QgsProcessing.TypeVector],layer.name()))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.TIMES,'Times Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.RULES.lower():
                flag=1
                self.addParameter(QgsProcessingParameterVectorLayer(self.RULES,'Rules Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.RULES,'Rules Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.ENERGY.lower():
                flag=1
                self.addParameter(QgsProcessingParameterVectorLayer(self.ENERGY,'Energy Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.ENERGY,'Energy Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.REACTIONS.lower():
                flag=1
                self.addParameter(QgsProcessingParameterVectorLayer(self.REACTIONS,'Reactions Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.REACTIONS,'Reactions Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.REPORT.lower():
                flag=1
                self.addParameter(QgsProcessingParameterVectorLayer(self.REPORT,'Report Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.REPORT,'Report Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.OPTIONS.lower():
                flag=1
                self.addParameter(QgsProcessingParameterVectorLayer(self.OPTIONS,'Options Table',[QgsProcessing.TypeVector],layer.name(),True))
                break
        if flag==0: self.addParameter(QgsProcessingParameterVectorLayer(self.OPTIONS,'Options Table',[QgsProcessing.TypeVector],'',True))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.NODE_TABLE_OUTPUT	.lower():
                flag=1
                self.addParameter(QgsProcessingParameterFeatureSink(self.NODE_TABLE_OUTPUT,'Node_Output_Table',QgsProcessing.TypeVector,layer.name()+ ' ['+layer.crs().authid()+']'))
                break
        if flag==0: self.addParameter(QgsProcessingParameterFeatureSink(self.NODE_TABLE_OUTPUT,'Node_Output_Table',QgsProcessing.TypeVector,''))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.LINK_TABLE_OUTPUT	.lower():
                flag=1
                self.addParameter(QgsProcessingParameterFeatureSink(self.LINK_TABLE_OUTPUT,'Link_Output_Table',QgsProcessing.TypeVector,layer.name()+ ' ['+layer.crs().authid()+']'))
                break
        if flag==0: self.addParameter(QgsProcessingParameterFeatureSink(self.LINK_TABLE_OUTPUT,'Link_Output_Table',QgsProcessing.TypeVector,''))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.TIME_AGGREGATE_NODE_TABLE_OUTPUT	.lower():
                flag=1
                self.addParameter(QgsProcessingParameterFeatureSink(self.TIME_AGGREGATE_NODE_TABLE_OUTPUT,'NodeTimeAgg',QgsProcessing.TypeVector,layer.name()+ ' ['+layer.crs().authid()+']'))
                break
        if flag==0: self.addParameter(QgsProcessingParameterFeatureSink(self.TIME_AGGREGATE_NODE_TABLE_OUTPUT,'NodeTimeAgg',QgsProcessing.TypeVector,''))

        flag=0
        for layer in layers:
            if layer.name().lower() == self.TIME_AGGREGATE_LINK_TABLE_OUTPUT	.lower():
                flag=1
                self.addParameter(QgsProcessingParameterFeatureSink(self.TIME_AGGREGATE_LINK_TABLE_OUTPUT,'LinkTimeAgg',QgsProcessing.TypeVector,layer.name()+ ' ['+layer.crs().authid()+']'))
                break
        if flag==0: self.addParameter(QgsProcessingParameterFeatureSink(self.TIME_AGGREGATE_LINK_TABLE_OUTPUT,'LinkTimeAgg',QgsProcessing.TypeVector,''))


        if not ProcessingConfig.getSetting('EPANET_CLI'):
             QgsMessageLog.logMessage('EPANET command line tool is not configured.\n\
                Please configure it before running EPANET algorithms.',tag="EPANET Processing")

        return

    def epanetTable(self,layer,parameters,context):

        if not layer: return u''
        pkidx = layer.dataProvider().pkAttributeIndexes()
        if not pkidx:
            pkidx=[]
            pkidx.append(layer.dataProvider().fields().indexFromName('id'))
            if int(pkidx[0])<0:
                pkidx=[]
                pkidx.append(layer.dataProvider().fields().indexFromName('fid'))
        fields = ""
        for i,field in enumerate(layer.fields()):
            if not i in pkidx:
                fields+=field.name()+"\t"

        tbl =u'['+layer.name()+']\n'\
            ';'+fields+'\n'
        attr=[]
        for feature in layer.getFeatures():
                attr.append(feature.attributes())
        if  pkidx:
            attr.sort(key=lambda x: x[pkidx[0]])
        for i,v in enumerate(attr):
            for j,t in enumerate(attr[i]):
                if not j in pkidx:# and v in k:
                    if str(t) != 'NULL': tbl += str(t)+'\t'
                else: tbl += '\t'
            tbl += '\n'
        tbl += '\n'
        return tbl;

    def epanetKeyVal(self,layer,parameters,context, simul_title):
        if not layer: return u''
        pkidx = layer.dataProvider().pkAttributeIndexes()
        if not pkidx:
            pkidx=[]
            pkidx.append(layer.dataProvider().fields().indexFromName('id'))
            if int(pkidx[0])<0:
                pkidx=[]
                pkidx.append(layer.dataProvider().fields().indexFromName('fid'))
        fields = []
        k=[]
        for i,field in enumerate(layer.dataProvider().fields()):
            if not i in pkidx:
                k.append(i)
                fields.append(field.name())
        tbl =u'['+layer.name()+']\n'
        found = False
        if 0 not in k:
            idx=1
            offset=1
        else:
            idx=0
            offset=0
        for feature in layer.getFeatures():

            if str(feature[idx]) == simul_title:
                for i,v in enumerate(fields):
                        if i and str(v) != 'NULL': tbl += fields[i].upper()+'\t'+str(feature[i+offset])+'\n'                #v)+'\n'
                        elif i : tbl += '\t'
                found = True
                tbl += '\n'
        tbl += '\n'
        k=None
        idx=None
        if not found:
            raise QgsProcessingException(
                    "No simulation named '"+simul_title+"' in "+layer.name())
        return tbl;

    def processAlgorithm(self, parameters, context, feedback):
        epanet_cli = os.path.abspath(ProcessingConfig.getSetting('EPANET_CLI'))
        folder = ProcessingConfig.getSetting(ProcessingConfig.OUTPUT_FOLDER)
        filename = os.path.join(folder, 'epanet.inp')
        f = io.open(filename,'w',encoding='utf-8')
        f.write('[TITLE]\n')
        f.write(self.parameterAsString(parameters,self.TITLE,context)+'\n\n')
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.JUNCTIONS,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.RESERVOIRS,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.TANKS,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.PIPES,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.PUMPS,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.VALVES,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.EMITTERS,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.SOURCES,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.DEMANDS,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.STATUS,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.PATTERNS,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.CURVES,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.CONTROLS,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.QUALITY,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.MIXING,context)),parameters,context))
        f.write(self.epanetTable((self.parameterAsVectorLayer(parameters,self.RULES,context)),parameters,context))
        f.write(self.epanetKeyVal((self.parameterAsVectorLayer(parameters,self.TIMES,context)),parameters,context,self.parameterAsString(parameters,self.TITLE,context)))
        f.write(self.epanetKeyVal((self.parameterAsVectorLayer(parameters,self.OPTIONS,context)),parameters,context,self.parameterAsString(parameters,self.TITLE,context)))
        f.write(self.epanetKeyVal((self.parameterAsVectorLayer(parameters,self.REPORT,context)),parameters,context,self.parameterAsString(parameters,self.TITLE,context)))
        f.write(self.epanetKeyVal((self.parameterAsVectorLayer(parameters,self.REACTIONS,context)),parameters,context,self.parameterAsString(parameters,self.TITLE,context)))
        f.write(self.epanetKeyVal((self.parameterAsVectorLayer(parameters,self.ENERGY,context)),parameters,context,self.parameterAsString(parameters,self.TITLE,context)))
        f.write('\n[END]\n')

        f.close()

        outfilename = os.path.join(folder,'epanet.out')
        log=""
        error = False
        def demote(user_uid, user_gid):
            def result():
                os.setgid(user_gid)
                os.setuid(user_uid)
            return result
        loglines=[]
        if platform=='linux' or platform=='darwin':
            user_name=getpass.getuser()
            pw_record = pwd.getpwnam(user_name)
            user_name      = pw_record.pw_name
            user_home_dir  = pw_record.pw_dir
            user_uid       = pw_record.pw_uid
            user_gid       = pw_record.pw_gid
            env = os.environ.copy()
            cwd=ProcessingConfig.getSetting(ProcessingConfig.OUTPUT_FOLDER)
            env[ 'HOME'     ]  = user_home_dir
            env[ 'PWD'      ]  = cwd
            env[ 'LOGNAME'  ]  = user_name
            env[ 'USER'     ]  = user_name
            with subprocess.Popen(
                [epanet_cli, filename, outfilename],
                shell=False,
                preexec_fn=demote(user_uid, user_gid),
                env=env,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stdin=open(os.devnull),
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                ) as epanet:
                for line in epanet.stdout:
                    feedback.pushConsoleInfo(line)
                    loglines.append(line)
                QgsMessageLog.logMessage('\n'.join(loglines),level=Qgis.Info)
                epanet.wait()
                returncode = epanet.returncode
        elif platform=='win32':
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            with subprocess.Popen(
                ['\& '+epanet_cli,filename,outfilename],
                stdout=subprocess.PIPE,
                shell=True,
                stdin=open(os.devnull),
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                startupinfo=si
                ) as epanet:
                for line in epanet.stdout:
                    feedback.pushConsoleInfo(line)
                    loglines.append(str(line))
                QgsMessageLog.logMessage('\n'.join(loglines),level=Qgis.Info)
                epanet.wait()
                returncode = epanet.returncode
        total_size = os.path.getsize(outfilename)
        total_read = 0
        o = io.open(outfilename,'r',encoding='utf-8')
        o.seek(0)
        # get nodes results6+
        in_link = False
        in_node = False
        time = ''
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        link_table = []
        line = o.readline()
        node_table = []
        while line:

            line = line.rstrip()
            if (in_node or in_link) and not line:
                in_node = False
                in_link = False
            if re.search('^  Node Results', line):
                in_node = True
                time = re.search('at (\S+) ', line).group(1)
                for i in range(5): line = o.readline()
                line = line.rstrip()
            if re.search('^  Link Results', line):
                in_link = True
                time = re.search('at (\S+) ', line).group(1)
                for i in range(5): line = o.readline()
                line = line.rstrip()
            if in_node:
                tbl = re.findall(r"\S+(?:\s\S+)*", line)
                if len(tbl) >= 4:
                    node_table.append(tbl[0:4]+[date+' '+time])
            if in_link:
                tbl = re.findall(r"\S+(?:\s\S+)*", line)
                if len(tbl) >= 4:
                    link_table.append(tbl[0:4]+[date+' '+time])

            line = o.readline()
            total_read += len(line)
        o.close()

        node_fields=QgsFields()
        node_fields.append(QgsField('id',QVariant.Int,'Integer'))
        node_fields.append(QgsField('Node', QVariant.String, 'String'))
        node_fields.append(QgsField('Demand', QVariant.Double, 'Real'))
        node_fields.append(QgsField('Head', QVariant.Double, 'Real'))
        node_fields.append(QgsField('Pressure', QVariant.Double, 'Real'))
        node_fields.append(QgsField('Time', QVariant.String, 'String'))

        (node_table_feat, node_dest_id) = self.parameterAsSink(parameters, self.NODE_TABLE_OUTPUT, context,node_fields)
        i=1
        for node in node_table:
            fet=QgsFeature()
            fet.setAttributes([i,node[0],node[1],node[2],node[3],node[4]])
            node_table_feat.addFeatures([fet])
            i=i+1

        link_fields=QgsFields()
        link_fields.append( QgsField('id',QVariant.Int,'Integer'))
        link_fields.append(QgsField('Link', QVariant.String, 'String'))
        link_fields.append(QgsField('Flow', QVariant.Double, 'Real'))
        link_fields.append(QgsField('Velocity', QVariant.String, 'Real'))
        link_fields.append(QgsField('Headloss', QVariant.Double, 'Real'))
        link_fields.append(QgsField('Time', QVariant.String, 'String'))

        (link_table_feat, link_dest_id) = self.parameterAsSink(parameters, self.LINK_TABLE_OUTPUT, context,link_fields)
        i=1
        for link in link_table:
            fet=QgsFeature()
            fet.setAttributes([i,link[0],link[1],link[2],link[3],link[4]])
            link_table_feat.addFeatures([fet])
            i=i+1

        agr_node_fields = QgsFields()
        agr_node_fields.append( QgsField('id',QVariant.Int,'Integer'))
        agr_node_fields.append(QgsField('Node', QVariant.String, 'String'))
        agr_node_fields.append(QgsField('MaxPressure', QVariant.Double, 'Real'))
        agr_node_fields.append(QgsField('MinPressure', QVariant.Double, 'Real'))
        agr_node_fields.append(QgsField('MaxHead', QVariant.Double, 'Real'))
        agr_node_fields.append(QgsField('MinHead', QVariant.Double, 'Real'))

        sorted_res = sorted(node_table,key=itemgetter(0))
        key = ""
        node_res = []
        agr_node_table = []
        total_size = len(sorted_res)
        total_read = 0
        for r in sorted_res:
            if key != r[0] and node_res:
                agr_node_table.append( [key,
                    max([row[3] for row in node_res]),
                    min([row[3] for row in node_res]),
                    max([row[2] for row in node_res]),
                    min([row[2] for row in node_res]),
                    ] )
                key = r[0]
                node_res = []
            elif key != r[0]:
                key = r[0]
            else:
                node_res.append(r)
            total_read += 1

        if key and node_res:
            agr_node_table.append( [key,
                max([row[3] for row in node_res]),
                min([row[3] for row in node_res]),
                max([row[2] for row in node_res]),
                min([row[2] for row in node_res]),
                ] )

        (agr_node_table_feat, agr_node_dest_id) = self.parameterAsSink(parameters, self.TIME_AGGREGATE_NODE_TABLE_OUTPUT, context,agr_node_fields)
        i=1
        for node in agr_node_table:
            fet=QgsFeature()
            fet.setAttributes([i,node[0],node[1],node[2],node[3],node[4]])
            agr_node_table_feat.addFeatures([fet])
            i=i+1

        agr_link_fields = QgsFields()
        agr_link_fields.append( QgsField('id',QVariant.Int,'Integer'))
        agr_link_fields.append(QgsField('Link', QVariant.String, 'String'))
        agr_link_fields.append(QgsField('AvgFlow', QVariant.Double, 'Real'))
        agr_link_fields.append(QgsField('AvgVelocity', QVariant.Double, 'Real'))
        agr_link_fields.append(QgsField('AvgHeadloss', QVariant.Double, 'Real'))

        sorted_res = sorted(link_table,key=itemgetter(0))
        key = ""
        link_res = []
        agr_link_table = []
        total_size = len(sorted_res)
        total_read = 0
        for r in sorted_res:
            if key != r[0] and link_res: # new stuff, we create and aggregate
                agr_link_table.append( [key,
                    float(mean([float(row[1]) for row in link_res])),
                    float(mean([float(row[2]) for row in link_res])),
                    float(mean([float(row[3]) for row in link_res])),
                    ] )
                key = r[0]
                link_res = []
            elif key != r[0]:
                key = r[0]
            else:
                link_res.append(r)
            total_read += 1

        if key and link_res: # last aggregate not agregated in loop
            agr_link_table.append( [key,
                float(mean([float(row[1]) for row in link_res])),
                float(mean([float(row[2]) for row in link_res])),
                float(mean([float(row[3]) for row in link_res])),
                ] )

        (agr_link_table_feat, agr_link_dest_id) = self.parameterAsSink(parameters, self.TIME_AGGREGATE_LINK_TABLE_OUTPUT, context,agr_link_fields)
        i=1
        for link in agr_link_table:
            fet=QgsFeature()
            fet.setAttributes([i,link[0],link[1],link[2],link[3]])
            agr_link_table_feat.addFeatures([fet])
            i=i+1
        agr_node_table_feat.flushBuffer()
        agr_link_table_feat.flushBuffer()

        return  {self.NODE_TABLE_OUTPUT: node_dest_id}

    def icon(self):
        return QIcon(":/plugins/ldtoolbox/epanet.png")

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Run EPANET simulation')
    def shortHelpString(self):
        file=os.path.realpath(__file__)
        file = os.path.join(os.path.dirname(file),'Qgs3EpanetAlgorithm.help')
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
        return 'EPANET'

    def createInstance(self):
        return Qgs3EpanetAlgorithm()
