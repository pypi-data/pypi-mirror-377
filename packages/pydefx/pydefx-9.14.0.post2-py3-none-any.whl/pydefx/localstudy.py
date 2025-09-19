# -*- coding: utf-8 -*-
# Copyright (C) 2019-2024 EDF
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#
import copy
import os
import json
from . import pystudy
from . import localbuilder
from . import salome_proxy
from . import configuration

class LocalStudy(pystudy.PyStudy):
  """
  This study is always localy evaluated.
  """
  def __init__(self, sampleManager=None, schemaBuilder=None):
    if schemaBuilder is None:
      schemaBuilder = localbuilder.LocalBuilder()
    super().__init__(sampleManager, schemaBuilder)

  def createNewJob(self, script, sample, params):
    self._check(script,sample)
    self.sample = sample
    self.params = copy.deepcopy(params)
    # dump the remote jobs parameters to the configuration file
    params_dic = params.dumpDict()
    # modify the parameters for the local loop job
    self.params.salome_parameters.resource_required.name = "localhost"
    self.params.salome_parameters.job_type = "command_salome" #"python_salome"
    self.params.createTmpResultDirectory()
    result_directory = self.params.salome_parameters.result_directory
    # export sample to result_directory
    inputFiles = self.sampleManager.prepareRun(self.sample, result_directory)
    inputFiles.extend([self.schemaBuilder.getExecutor(),
                       self.schemaBuilder.getPointEval()])
    self.params.salome_parameters.job_file = self.schemaBuilder.getMainJob()

    # export config
    dicconfig = {}
    dicconfig["nbbranches"]  = self.params.nb_branches
    dicconfig["studymodule"] = "idefixstudy"
    dicconfig["sampleIterator"] = self.sampleManager.getModuleName()
    dicconfig["params"] = params_dic
    dicconfig["plugin"] = self.schemaBuilder.getPluginName()
    configpath = configuration.exportConfig(dicconfig, result_directory)
    studypath = os.path.join(result_directory, "idefixstudy.py")
    with open(studypath, "w") as f:
      f.write(script.script)

    inputFiles.extend([configpath, studypath])

    # this list manipulation is needed because in_files is not a python list
    # if we don't use a salome session. In that case swig uses a python tuple
    # in order to map a std::list as a parameter of a structure.
    in_files_as_list = list(self.params.salome_parameters.in_files)
    self.params.salome_parameters.in_files = in_files_as_list + inputFiles
    launcher = salome_proxy.getLauncher()
    self.job_id = launcher.createJob(self.params.salome_parameters)
    return self.job_id

  def jobType(self):
    return "command_salome"
