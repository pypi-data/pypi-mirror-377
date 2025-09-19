#!/usr/bin/env python3
# Copyright (C) 2006-2024  CEA, EDF
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

import unittest
import tempfile
import os

from salome.yacs import pilot
from salome.yacs import SALOMERuntime
from salome.yacs import loader
from salome.kernel import salome

import datetime

class TestSaveLoadRun(unittest.TestCase):
  def setUp(self):
    SALOMERuntime.RuntimeSALOME.setRuntime()
    self.r=SALOMERuntime.getSALOMERuntime()
    self.workdir = tempfile.mkdtemp(suffix=".yacstest")
    pass

  def tearDown(self):
    salome.salome_init()
    cm = salome.lcc.getContainerManager()
    cm.ShutdownContainers()
    salome.dsm.shutdownScopes()
    pass

  def test0(self):
    """First test of HP Container no loop here only the 3 sorts of python nodes (the Distributed is it still used and useful ?) """
    fname=os.path.join(self.workdir, "TestSaveLoadRun0.xml")
    nbOfNodes=8
    sqrtOfNumberOfTurn=1000 # 3000 -> 3.2s/Node, 1000 -> 0.1s/Node
    l=loader.YACSLoader()
    p=self.r.createProc("prTest0")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    pg=pilot.PlayGround()
    pg.setData([("localhost",4)])
    cont=p.createContainer("gg","HPSalome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    cont.setProperty("nb_proc_per_node","1")
    script0="""
def ff(nb,dbg):
    from math import cos
    import datetime
    
    ref=datetime.datetime.now()
    t=0. ; pas=1./float(nb)
    for i in range(nb):
        for j in range(nb):
            x=j*pas
            t+=1.+cos(1.*(x*3.14159))
            pass
        pass
    print("coucou from script0-%i  -> %s"%(dbg,str(datetime.datetime.now()-ref)))
    return t
"""
    script1="""
from math import cos
import datetime
ref=datetime.datetime.now()
o2=0. ; pas=1./float(i1)
for i in range(i1):
  for j in range(i1):
    x=j*pas
    o2+=1.+cos(1.*(x*3.14159))
    pass
print("coucou from script1-%i  -> %s"%(dbg,str(datetime.datetime.now()-ref)))
"""
    for i in range(nbOfNodes):
      node0=self.r.createFuncNode("DistPython","node%i"%(i))
      p.edAddChild(node0)
      node0.setFname("ff")
      node0.setContainer(cont)
      node0.setScript(script0)
      nb=node0.edAddInputPort("nb",ti) ; nb.edInitInt(sqrtOfNumberOfTurn)
      dbg=node0.edAddInputPort("dbg",ti) ; dbg.edInitInt(i+1)
      out0=node0.edAddOutputPort("s",td)
      #
      nodeMiddle=self.r.createFuncNode("Salome","node%i_1"%(i))
      p.edAddChild(nodeMiddle)
      p.edAddCFLink(node0,nodeMiddle)
      nodeMiddle.setFname("ff")
      nodeMiddle.setContainer(cont)
      nodeMiddle.setScript(script0)
      nb=nodeMiddle.edAddInputPort("nb",ti) ; nb.edInitInt(sqrtOfNumberOfTurn)
      dbg=nodeMiddle.edAddInputPort("dbg",ti) ; dbg.edInitInt(i+1)
      out0=nodeMiddle.edAddOutputPort("s",td)
      nodeMiddle.setExecutionMode("remote")
      #
      nodeEnd=self.r.createScriptNode("Salome","node%i_2"%(i+1))
      p.edAddChild(nodeEnd)
      p.edAddCFLink(nodeMiddle,nodeEnd)
      nodeEnd.setContainer(cont)
      nodeEnd.setScript(script1)
      i1=nodeEnd.edAddInputPort("i1",ti) ; i1.edInitInt(sqrtOfNumberOfTurn)
      dbg=nodeEnd.edAddInputPort("dbg",ti) ; dbg.edInitInt(i)
      o2=nodeEnd.edAddOutputPort("o2",td)
      nodeEnd.setExecutionMode("remote")
      pass
    p.saveSchema(fname)
    p=l.load(fname)
    ex=pilot.ExecutorSwig()
    self.assertEqual(p.getState(),pilot.READY)
    st=datetime.datetime.now()
    p.propagePlayGround(pg)
    # 1st exec
    ex.RunW(p,0)
    print("Time spend of test0 to run 1st %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    # 2nd exec using the same already launched remote python interpreters
    st=datetime.datetime.now()
    ex.RunW(p,0)
    print("Time spend of test0 to run 2nd %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    # 3rd exec using the same already launched remote python interpreters
    st=datetime.datetime.now()
    ex.RunW(p,0)
    print("Time spend of test0 to run 3rd %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    pass

  def test1(self):
    """ HP Container again like test0 but the initialization key of HPContainer is used here."""
    fname=os.path.join(self.workdir, "TestSaveLoadRun1.xml")
    nbOfNodes=8
    sqrtOfNumberOfTurn=1000 # 3000 -> 3.2s/Node, 1000 -> 0.1s/Node
    l=loader.YACSLoader()
    p=self.r.createProc("prTest1")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    pg=pilot.PlayGround()
    pg.setData([("localhost",4)])
    cont=p.createContainer("gg","HPSalome")
    cont.setProperty("InitializeScriptKey","aa=123.456")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    cont.setProperty("nb_proc_per_node","1")
    script0="""
def ff(nb,dbg):
    from math import cos
    import datetime
    
    ref=datetime.datetime.now()
    t=0. ; pas=1./float(nb)
    for i in range(nb):
        for j in range(nb):
            x=j*pas
            t+=1.+cos(1.*(x*3.14159))
            pass
        pass
    print("coucou from script0-%i  -> %s"%(dbg,str(datetime.datetime.now()-ref)))
    return t
"""
    # here in script1 aa is refered ! aa will exist thanks to HPCont Init Script
    script1="""
from math import cos
import datetime
ref=datetime.datetime.now()
o2=0. ; pas=1./float(i1)
for i in range(i1):
  for j in range(i1):
    x=j*pas
    o2+=1.+cos(1.*(x*3.14159))
    pass
print("coucou %lf from script1-%i  -> %s"%(aa,dbg,str(datetime.datetime.now()-ref)))
aa+=1.
"""
    #
    for i in range(nbOfNodes):
      nodeMiddle=self.r.createFuncNode("Salome","node%i_1"%(i)) # PyFuncNode remote
      p.edAddChild(nodeMiddle)
      nodeMiddle.setFname("ff")
      nodeMiddle.setContainer(cont)
      nodeMiddle.setScript(script0)
      nb=nodeMiddle.edAddInputPort("nb",ti) ; nb.edInitInt(sqrtOfNumberOfTurn)
      dbg=nodeMiddle.edAddInputPort("dbg",ti) ; dbg.edInitInt(i+1)
      out0=nodeMiddle.edAddOutputPort("s",td)
      nodeMiddle.setExecutionMode("remote")
      #
      nodeEnd=self.r.createScriptNode("Salome","node%i_2"%(i+1)) # PythonNode remote
      p.edAddChild(nodeEnd)
      p.edAddCFLink(nodeMiddle,nodeEnd)
      nodeEnd.setContainer(cont)
      nodeEnd.setScript(script1)
      i1=nodeEnd.edAddInputPort("i1",ti) ; i1.edInitInt(sqrtOfNumberOfTurn)
      dbg=nodeEnd.edAddInputPort("dbg",ti) ; dbg.edInitInt(i)
      o2=nodeEnd.edAddOutputPort("o2",td)
      nodeEnd.setExecutionMode("remote")
      pass
    #
    p.saveSchema(fname)
    p=l.load(fname)
    self.assertEqual(p.edGetDirectDescendants()[0].getContainer().getProperty("InitializeScriptKey"),"aa=123.456")
    p.propagePlayGround(pg)
    # 1st exec
    ex=pilot.ExecutorSwig()
    self.assertEqual(p.getState(),pilot.READY)
    st=datetime.datetime.now()
    ex.RunW(p,0)
    print("Time spend of test1 to 1st run %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    # 2nd exec
    st=datetime.datetime.now()
    ex.RunW(p,0)
    print("Time spend of test1 to 2nd run %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    # 3rd exec
    st=datetime.datetime.now()
    ex.RunW(p,0)
    print("Time spend of test1 to 3rd run %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    pass

  def test2(self):
    """ Test on HP Containers in foreach context."""
    script0="""def ff():
    global aa
    print("%%lf - %%s"%%(aa,str(my_container)))
    return 16*[%i],0
"""
    script1="""from math import cos
import datetime
ref=datetime.datetime.now()
o2=0. ; pas=1./float(i1)
for i in range(i1):
  for j in range(i1):
    x=j*pas
    o2+=1.+cos(1.*(x*3.14159))
    pass
print("coucou %lf from script  -> %s"%(aa,str(datetime.datetime.now()-ref)))
aa+=1.
o3=0
"""
    script2="""o9=sum(i8)
"""
    fname=os.path.join(self.workdir, "TestSaveLoadRun2.xml")
    nbOfNodes=8
    sqrtOfNumberOfTurn=1000 # 3000 -> 3.2s/Node, 1000 -> 0.1s/Node
    l=loader.YACSLoader()
    p=self.r.createProc("prTest1")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    tdi=p.createSequenceTc("seqint","seqint",ti)
    tdd=p.createSequenceTc("seqdouble","seqdouble",td)
    pg=pilot.PlayGround()
    pg.setData([("localhost",4)])
    cont=p.createContainer("gg","HPSalome")
    cont.setProperty("InitializeScriptKey","aa=123.456")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    cont.setProperty("nb_proc_per_node","1")
    #
    node0=self.r.createFuncNode("Salome","PyFunction0") # PyFuncNode remote
    p.edAddChild(node0)
    node0.setFname("ff")
    node0.setContainer(cont)
    node0.setScript(script0%(sqrtOfNumberOfTurn))
    out0_0=node0.edAddOutputPort("o1",tdi)
    out1_0=node0.edAddOutputPort("o2",ti)
    node0.setExecutionMode("remote")
    #
    node1=self.r.createForEachLoop("node1",ti)
    p.edAddChild(node1)
    p.edAddCFLink(node0,node1)
    p.edAddLink(out0_0,node1.edGetSeqOfSamplesPort())
    node1.edGetNbOfBranchesPort().edInitInt(8)
    #
    node2=self.r.createScriptNode("Salome","PyScript3")
    node1.edAddChild(node2)
    node2.setContainer(cont)
    node2.setScript(script1)
    i1=node2.edAddInputPort("i1",ti)
    p.edAddLink(node1.edGetSamplePort(),i1)
    out0_2=node2.edAddOutputPort("o2",td)
    out1_2=node2.edAddOutputPort("o3",ti)
    node2.setExecutionMode("remote")
    #
    node3=self.r.createScriptNode("Salome","PyScript7")
    p.edAddChild(node3)
    node3.setScript(script2)
    p.edAddCFLink(node1,node3)
    i8=node3.edAddInputPort("i8",tdd)
    o9=node3.edAddOutputPort("o9",td)
    p.edAddLink(out0_2,i8)
    #
    p.saveSchema(fname)
    p=l.load(fname)
    o9=p.getChildByName("PyScript7").getOutputPort("o9")
    self.assertTrue(len(p.edGetDirectDescendants()[1].getChildByName("PyScript3").getContainer().getProperty("InitializeScriptKey"))!=0)
    # 1st exec
    refExpected=16016013.514623128
    ex=pilot.ExecutorSwig()
    p.propagePlayGround(pg)
    self.assertEqual(p.getState(),pilot.READY)
    st=datetime.datetime.now()
    ex.RunW(p,0)
    print("Time spend of test2 to 1st run %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertAlmostEqual(refExpected,o9.getPyObj(),5)
    # 2nd exec
    st=datetime.datetime.now()
    ex.RunW(p,0)
    print("Time spend of test2 to 2nd run %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertAlmostEqual(refExpected,o9.getPyObj(),5)
    # 3rd exec
    st=datetime.datetime.now()
    ex.RunW(p,0)
    print("Time spend of test2 to 3rd run %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertAlmostEqual(refExpected,o9.getPyObj(),5)
    pass

  def test3(self):
    """ Test that focuses on parallel load of containers."""
    script0="""
if "aa" not in globals():
  aa=123.456
print("%%lf - %%s"%%(aa,str(my_container)))
o1=100*[%i]
o2=0
"""
    script1="""from math import cos
import datetime
ref=datetime.datetime.now()
if "aa" not in globals():
  aa=123.456
o2=0. ; pas=1./float(i1)
for i in range(i1):
  for j in range(i1):
    x=j*pas
    o2+=1.+cos(1.*(x*3.14159))
    pass
print("coucou %lf from script  -> %s"%(aa,str(datetime.datetime.now()-ref)))
aa+=1.
o3=0
"""
    script2="""o9=sum(i8)
"""
    nbOfNodes=8
    sqrtOfNumberOfTurn=10
    l=loader.YACSLoader()
    p=self.r.createProc("prTest1")
    p.setProperty("executor","workloadmanager")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    tdi=p.createSequenceTc("seqint","seqint",ti)
    tdd=p.createSequenceTc("seqdouble","seqdouble",td)
    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    # no limit for the number of containers launched
    cont.setProperty("nb_proc_per_node","0")
    cont.setProperty("type","multi")
    cont.usePythonCache(True)
    cont.attachOnCloning()
    #
    node0=self.r.createScriptNode("Salome","Node0")
    p.edAddChild(node0)
    node0.setContainer(cont)
    node0.setScript(script0%(sqrtOfNumberOfTurn))
    out0_0=node0.edAddOutputPort("o1",tdi)
    out1_0=node0.edAddOutputPort("o2",ti)
    node0.setExecutionMode("remote")
    #
    node1=self.r.createForEachLoop("node1",ti)
    p.edAddChild(node1)
    p.edAddCFLink(node0,node1)
    p.edAddLink(out0_0,node1.edGetSeqOfSamplesPort())
    node1.edGetNbOfBranchesPort().edInitInt(16)
    #
    node2=self.r.createScriptNode("Salome","Node2")
    node1.edAddChild(node2)
    node2.setContainer(cont)
    node2.setScript(script1)
    i1=node2.edAddInputPort("i1",ti)
    p.edAddLink(node1.edGetSamplePort(),i1)
    out0_2=node2.edAddOutputPort("o2",td)
    out1_2=node2.edAddOutputPort("o3",ti)
    node2.setExecutionMode("remote")
    #
    node3=self.r.createScriptNode("Salome","Node3")
    p.edAddChild(node3)
    node3.setScript(script2)
    p.edAddCFLink(node1,node3)
    i8=node3.edAddInputPort("i8",tdd)
    o9=node3.edAddOutputPort("o9",td)
    p.edAddLink(out0_2,i8)
    #
    fname=os.path.join(self.workdir, "t3_new.xml")
    p.saveSchema(fname)
    p=l.load(fname)
    o9=p.getChildByName("Node3").getOutputPort("o9")
    # 1st exec
    refExpected=11000.008377058712
    ex=pilot.ExecutorSwig()
    self.assertEqual(p.getState(),pilot.READY)
    st=datetime.datetime.now()
    ex.RunW(p,0)
    print("Time spend of test3 to 1st run %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertAlmostEqual(refExpected,o9.getPyObj(),5)
    # 2nd exec
    st=datetime.datetime.now()
    ex.RunW(p,0)
    print("Time spend of test3 to 2nd run %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertAlmostEqual(refExpected,o9.getPyObj(),5)
    # 3rd exec
    st=datetime.datetime.now()
    ex.RunW(p,0)
    print("Time spend of test3 to 3rd run %s"%(str(datetime.datetime.now()-st)))
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertAlmostEqual(refExpected,o9.getPyObj(),5)
    pass

  def test4(self):
    """Double foreach."""
    fname=os.path.join(self.workdir, "TestSaveLoadRun4.xml")
    script1="""nb=7
ii=0
o1=nb*[None]
for i in range(nb):
    tmp=(i+10)*[None]
    for j in range(i+10):
        tmp[j]=ii
        ii+=1
        pass
    o1[i]=tmp
    pass
"""
    l=loader.YACSLoader()
    ex=pilot.ExecutorSwig()
    p=self.r.createProc("pr")
    p.setProperty("executor","workloadmanager")
    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    # no limit for the number of containers launched
    cont.setProperty("nb_proc_per_node","0")
    cont.setProperty("type","multi")
    cont.attachOnCloning()
    td=p.createType("int","int")
    td2=p.createSequenceTc("seqint","seqint",td)
    td3=p.createSequenceTc("seqintvec","seqintvec",td2)
    node1=self.r.createScriptNode("","node1")
    node1.setScript(script1)
    o1=node1.edAddOutputPort("o1",td3)
    p.edAddChild(node1)
    #
    node2=self.r.createForEachLoop("node2",td2)
    p.edAddChild(node2)
    p.edAddCFLink(node1,node2)
    p.edAddLink(o1,node2.edGetSeqOfSamplesPort())
    node2.edGetNbOfBranchesPort().edInitInt(2)
    node20=self.r.createBloc("node20")
    node2.edAddChild(node20)
    node200=self.r.createForEachLoop("node200",td)
    node20.edAddChild(node200)
    node200.edGetNbOfBranchesPort().edInitInt(10)
    p.edAddLink(node2.edGetSamplePort(),node200.edGetSeqOfSamplesPort())
    node2000=self.r.createScriptNode("","node2000")
    node2000.setContainer(cont)
    node2000.setExecutionMode("remote")
    node200.edAddChild(node2000)
    i5=node2000.edAddInputPort("i5",td)
    o6=node2000.edAddOutputPort("o6",td)
    node2000.setScript("o6=2+i5")
    p.edAddLink(node200.edGetSamplePort(),i5)
    #
    node3=self.r.createForEachLoop("node3",td2)
    p.edAddChild(node3)
    p.edAddCFLink(node2,node3)
    p.edAddLink(o6,node3.edGetSeqOfSamplesPort())
    node3.edGetNbOfBranchesPort().edInitInt(2)
    node30=self.r.createBloc("node30")
    node3.edAddChild(node30)
    node300=self.r.createForEachLoop("node300",td)
    node30.edAddChild(node300)
    node300.edGetNbOfBranchesPort().edInitInt(10)
    p.edAddLink(node3.edGetSamplePort(),node300.edGetSeqOfSamplesPort())
    node3000=self.r.createScriptNode("","node3000")
    node3000.setContainer(cont)
    node3000.setExecutionMode("remote")
    node300.edAddChild(node3000)
    i14=node3000.edAddInputPort("i14",td)
    o15=node3000.edAddOutputPort("o15",td)
    node3000.setScript("o15=3+i14")
    p.edAddLink(node300.edGetSamplePort(),i14)
    #
    node4=self.r.createScriptNode("","node4")
    node4.setScript("o9=i8")
    p.edAddChild(node4)
    i8=node4.edAddInputPort("i8",td3)
    o9=node4.edAddOutputPort("o9",td3)
    p.edAddCFLink(node3,node4)
    p.edAddLink(o15,i8)
    p.saveSchema(fname)
    p=l.load(fname)
    ex = pilot.ExecutorSwig()
    self.assertEqual(p.getState(),pilot.READY)
    ex.RunW(p,0)
    self.assertEqual(p.getState(),pilot.DONE)
    zeResu=p.getChildByName("node4").getOutputPort("o9").get()
    self.assertEqual(zeResu,[[5,6,7,8,9,10,11,12,13,14],[15,16,17,18,19,20,21,22,23,24,25],[26,27,28,29,30,31,32,33,34,35,36,37],[38,39,40,41,42,43,44,45,46,47,48,49,50],[51,52,53,54,55,56,57,58,59,60,61,62,63,64],[65,66,67,68,69,70,71,72,73,74,75,76,77,78,79], [80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95]])
    pass

  def test5(self):
    """Non regression test 2 of multi pyNode, pyFuncNode sharing the same HPContainer instance."""
    # TODO : This test is DEPRECATED. HPContainer will be removed.
    self.skipTest("HPContainer deprecated.")
    fname=os.path.join(self.workdir, "TestSaveLoadRun5.xml")
    script1="""nb=7
ii=0
o1=nb*[None]
for i in range(nb):
    tmp=(i+10)*[None]
    for j in range(i+10):
        tmp[j]=ii
        ii+=1
        pass
    o1[i]=tmp
    pass
"""
    l=loader.YACSLoader()
    ex=pilot.ExecutorSwig()
    p=self.r.createProc("pr")
    pg=pilot.PlayGround()
    pg.setData([("localhost",10)])
    cont=p.createContainer("gg","HPSalome")
    cont.setProperty("nb_proc_per_node","1")
    td=p.createType("int","int")
    td2=p.createSequenceTc("seqint","seqint",td)
    td3=p.createSequenceTc("seqintvec","seqintvec",td2)
    node1=self.r.createScriptNode("","node1")
    node1.setScript(script1)
    o1=node1.edAddOutputPort("o1",td3)
    p.edAddChild(node1)
    #
    node2=self.r.createForEachLoop("node2",td2)
    p.edAddChild(node2)
    p.edAddCFLink(node1,node2)
    p.edAddLink(o1,node2.edGetSeqOfSamplesPort())
    node2.edGetNbOfBranchesPort().edInitInt(2)
    node20=self.r.createBloc("node20")
    node2.edAddChild(node20)
    node200=self.r.createForEachLoop("node200",td)
    node20.edAddChild(node200)
    node200.edGetNbOfBranchesPort().edInitInt(10)
    p.edAddLink(node2.edGetSamplePort(),node200.edGetSeqOfSamplesPort())
    node2000=self.r.createFuncNode("Salome","node2000")
    node2000.setFname("ff")
    node2000.setContainer(cont)
    node2000.setExecutionMode("remote")
    node200.edAddChild(node2000)
    i5=node2000.edAddInputPort("i5",td)
    o6=node2000.edAddOutputPort("o6",td)
    node2000.setScript("def ff(x):\n  return 2+x")
    p.edAddLink(node200.edGetSamplePort(),i5)
    #
    node3=self.r.createForEachLoop("node3",td2)
    p.edAddChild(node3)
    p.edAddCFLink(node2,node3)
    p.edAddLink(o6,node3.edGetSeqOfSamplesPort())
    node3.edGetNbOfBranchesPort().edInitInt(2)
    node30=self.r.createBloc("node30")
    node3.edAddChild(node30)
    node300=self.r.createForEachLoop("node300",td)
    node30.edAddChild(node300)
    node300.edGetNbOfBranchesPort().edInitInt(10)
    p.edAddLink(node3.edGetSamplePort(),node300.edGetSeqOfSamplesPort())
    node3000=self.r.createFuncNode("Salome","node3000")
    node3000.setFname("ff")
    node3000.setContainer(cont)
    node3000.setExecutionMode("remote")
    node300.edAddChild(node3000)
    i14=node3000.edAddInputPort("i14",td)
    o15=node3000.edAddOutputPort("o15",td)
    node3000.setScript("def ff(x):\n  return 3+x")
    p.edAddLink(node300.edGetSamplePort(),i14)
    #
    node4=self.r.createScriptNode("","node4")
    node4.setScript("o9=i8")
    p.edAddChild(node4)
    i8=node4.edAddInputPort("i8",td3)
    o9=node4.edAddOutputPort("o9",td3)
    p.edAddCFLink(node3,node4)
    p.edAddLink(o15,i8)
    p.saveSchema(fname)
    p=l.load(fname)
    p.propagePlayGround(pg)
    ex = pilot.ExecutorSwig()
    self.assertEqual(p.getState(),pilot.READY)
    ex.RunW(p,0)
    self.assertEqual(p.getState(),pilot.DONE)
    zeResu=p.getChildByName("node4").getOutputPort("o9").get()
    self.assertEqual(zeResu,[[5,6,7,8,9,10,11,12,13,14],[15,16,17,18,19,20,21,22,23,24,25],[26,27,28,29,30,31,32,33,34,35,36,37],[38,39,40,41,42,43,44,45,46,47,48,49,50],[51,52,53,54,55,56,57,58,59,60,61,62,63,64],[65,66,67,68,69,70,71,72,73,74,75,76,77,78,79], [80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95]])
    pass

  def test6(self):
    fname=os.path.join(self.workdir, "test6.xml")
    p=self.r.createProc("prTest0")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    tsi=p.createSequenceTc("seqint","seqint",ti)
    tsd=p.createSequenceTc("seqdbl","seqdbl",td)
    n0=self.r.createScriptNode("","n0")
    o0=n0.edAddOutputPort("o0",tsi)
    n0.setScript("o0=[3,6,8,9,-2,5]")
    p.edAddChild(n0)
    n1=self.r.createForEachLoop("n1",ti)
    n10=self.r.createScriptNode("","n10")
    n1.edAddChild(n10)
    n10.setScript("o2=2*i1")
    i1=n10.edAddInputPort("i1",ti)
    o2=n10.edAddOutputPort("o2",ti)
    p.edAddChild(n1)
    p.edAddLink(o0,n1.edGetSeqOfSamplesPort())
    p.edAddLink(n1.edGetSamplePort(),i1)
    p.edAddCFLink(n0,n1)
    n1.edGetNbOfBranchesPort().edInitPy(1)
    n2=self.r.createScriptNode("","n2")
    n2.setScript("o4=i3")
    i3=n2.edAddInputPort("i3",tsi)
    o4=n2.edAddOutputPort("o4",tsi)
    n2.setScript("o4=i3")
    p.edAddChild(n2)
    p.edAddCFLink(n1,n2)
    p.edAddLink(o2,i3)
    p.saveSchema(fname)
    #
    l=loader.YACSLoader()
    p=l.load(fname)
    n1=p.getChildByName("n1")
    ex=pilot.ExecutorSwig()
    #
    ex.RunW(p,0)
    #
    self.assertEqual(n1.getState(),pilot.DONE)
    n1.edGetSeqOfSamplesPort().getPyObj()
    a,b,c=n1.getPassedResults(ex)
    self.assertEqual(a,list(range(6)))
    self.assertEqual([elt.getPyObj() for elt in b],[[6, 12, 16, 18, -4, 10]])
    self.assertEqual(c,['n10_o2_interceptor'])
    pass

  def test7(self):
    fname=os.path.join(self.workdir, "test7.xml")
    p=self.r.createProc("prTest1")
    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    cont.setProperty("type","multi")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    tsi=p.createSequenceTc("seqint","seqint",ti)
    tsd=p.createSequenceTc("seqdbl","seqdbl",td)
    n0=self.r.createScriptNode("","n0")
    o0=n0.edAddOutputPort("o0",tsi)
    n0.setScript("o0=[3,6,8,9,-2,5]")
    p.edAddChild(n0)
    n1=self.r.createForEachLoop("n1",ti)
    n10=self.r.createScriptNode("","n10")
    n10.setExecutionMode("remote")
    n10.setContainer(cont)
    n1.edAddChild(n10)
    n10.setScript("""
import time
if i1==9:
  time.sleep(2)
  raise Exception("Simulated error !")
else:
  o2=2*i1
""")
    i1=n10.edAddInputPort("i1",ti)
    o2=n10.edAddOutputPort("o2",ti)
    p.edAddChild(n1)
    p.edAddLink(o0,n1.edGetSeqOfSamplesPort())
    p.edAddLink(n1.edGetSamplePort(),i1)
    p.edAddCFLink(n0,n1)
    n1.edGetNbOfBranchesPort().edInitPy(1)
    n2=self.r.createScriptNode("","n2")
    n2.setScript("o4=i3")
    i3=n2.edAddInputPort("i3",tsi)
    o4=n2.edAddOutputPort("o4",tsi)
    n2.setScript("o4=i3")
    p.edAddChild(n2)
    p.edAddCFLink(n1,n2)
    p.edAddLink(o2,i3)
    p.saveSchema(fname)
    #
    l=loader.YACSLoader()
    p=l.load(fname)
    n1=p.getChildByName("n1")
    ex=pilot.ExecutorSwig()
    #
    ex.RunW(p,0)
    #
    self.assertEqual(n1.getState(),pilot.FAILED)
    n1.edGetSeqOfSamplesPort().getPyObj()
    a,b,c=n1.getPassedResults(ex)
    self.assertEqual(a,list(range(3)))
    self.assertEqual([elt.getPyObj() for elt in b],[[6,12,16]])
    self.assertEqual(c,['n10_o2_interceptor'])
    pass

  def test8(self):
    from datetime import datetime
    fname=os.path.join(self.workdir, "test8.xml")
    p=self.r.createProc("prTest2")
    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    cont.setProperty("type","multi")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    tsi=p.createSequenceTc("seqint","seqint",ti)
    tsd=p.createSequenceTc("seqdbl","seqdbl",td)
    n0=self.r.createScriptNode("","n0")
    o0=n0.edAddOutputPort("o0",tsi)
    n0.setScript("o0=[3,6,8,9,-2,5]")
    p.edAddChild(n0)
    n1=self.r.createForEachLoop("n1",ti)
    n10=self.r.createScriptNode("","n10")
    n10.setExecutionMode("remote")
    n10.setContainer(cont)
    n1.edAddChild(n10)
    n10.setScript("""
import time
if i1==9:
  raise Exception("Simulated error !")
else:
  time.sleep(0.1)
  o2=2*i1
""")
    i1=n10.edAddInputPort("i1",ti)
    o2=n10.edAddOutputPort("o2",ti)
    p.edAddChild(n1)
    p.edAddLink(o0,n1.edGetSeqOfSamplesPort())
    p.edAddLink(n1.edGetSamplePort(),i1)
    p.edAddCFLink(n0,n1)
    n1.edGetNbOfBranchesPort().edInitPy(2)
    n2=self.r.createScriptNode("","n2")
    n2.setScript("o4=i3")
    i3=n2.edAddInputPort("i3",tsi)
    o4=n2.edAddOutputPort("o4",tsi)
    n2.setScript("o4=i3")
    p.edAddChild(n2)
    p.edAddCFLink(n1,n2)
    p.edAddLink(o2,i3)
    p.saveSchema(fname)
    #
    l=loader.YACSLoader()
    p=l.load(fname)
    n1=p.getChildByName("n1")
    ex=pilot.ExecutorSwig()
    ex.setKeepGoingProperty(True)
    #
    startt=datetime.now()
    ex.RunW(p,0)
    t0=datetime.now()-startt
    #
    self.assertEqual(n1.getState(),pilot.FAILED)
    n1.edGetSeqOfSamplesPort().getPyObj()
    a,b,c=n1.getPassedResults(ex)
    self.assertEqual(a,[0,1,2,4,5])
    self.assertEqual([elt.getPyObj() for elt in b],[[6,12,16,-4,10]])
    self.assertEqual(c,['n10_o2_interceptor'])
    
    p.getChildByName("n1").getChildByName("n10").setScript("""
import time
if i1==3:
  time.sleep(2)
  raise Exception("Simulated error !")
else:
  o2=2*i1
""")
    ex=pilot.ExecutorSwig()
    ex.setKeepGoingProperty(True)
    #
    startt=datetime.now()
    ex.RunW(p,0)
    t1=datetime.now()-startt
    #
    self.assertEqual(n1.getState(),pilot.FAILED)
    n1.edGetSeqOfSamplesPort().getPyObj()
    a,b,c=n1.getPassedResults(ex)
    self.assertEqual(a,[1,2,3,4,5])
    self.assertEqual([elt.getPyObj() for elt in b],[[12,16,18,-4,10]])
    self.assertEqual(c,['n10_o2_interceptor'])
    pass

  def test9(self):
    """ Test of assignation of already computed values for foreach node."""
    fname=os.path.join(self.workdir, "test9.xml")
    from datetime import datetime
    p=self.r.createProc("prTest2")
    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    cont.setProperty("type","multi")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    tsi=p.createSequenceTc("seqint","seqint",ti)
    tsd=p.createSequenceTc("seqdbl","seqdbl",td)
    n0=self.r.createScriptNode("","n0")
    o0=n0.edAddOutputPort("o0",tsi)
    n0.setScript("o0=[3,6,8,9,-2,5]")
    p.edAddChild(n0)
    n1=self.r.createForEachLoop("n1",ti)
    n10=self.r.createScriptNode("","n10")
    n10.setExecutionMode("remote")
    n10.setContainer(cont)
    n1.edAddChild(n10)
    n10.setScript("""
import time
if i1==9:
  raise Exception("Simulated error !")
else:
  time.sleep(0.1)
  o2=2*i1
""")
    i1=n10.edAddInputPort("i1",ti)
    o2=n10.edAddOutputPort("o2",ti)
    p.edAddChild(n1)
    p.edAddLink(o0,n1.edGetSeqOfSamplesPort())
    p.edAddLink(n1.edGetSamplePort(),i1)
    p.edAddCFLink(n0,n1)
    n1.edGetNbOfBranchesPort().edInitPy(2)
    n2=self.r.createScriptNode("","n2")
    n2.setScript("o4=i3")
    i3=n2.edAddInputPort("i3",tsi)
    o4=n2.edAddOutputPort("o4",tsi)
    n2.setScript("o4=i3")
    p.edAddChild(n2)
    p.edAddCFLink(n1,n2)
    p.edAddLink(o2,i3)
    p.saveSchema(fname)
    #
    l=loader.YACSLoader()
    p=l.load(fname)
    n1=p.getChildByName("n1")
    ex=pilot.ExecutorSwig()
    ex.setKeepGoingProperty(True)
    #
    startt=datetime.now()
    ex.RunW(p,0)
    t0=datetime.now()-startt
    #
    self.assertEqual(p.getState(),pilot.FAILED)
    self.assertEqual(n1.getState(),pilot.FAILED)
    n1.edGetSeqOfSamplesPort().getPyObj()
    a,b,c=n1.getPassedResults(ex)
    self.assertEqual(a,[0,1,2,4,5])
    self.assertEqual([elt.getPyObj() for elt in b],[[6,12,16,-4,10]])
    self.assertEqual(c,['n10_o2_interceptor'])
    
    p.getChildByName("n1").getChildByName("n10").setScript("""
import time
time.sleep(2)
o2=7*i1
""")
    ex=pilot.ExecutorSwig()
    ex.setKeepGoingProperty(True)
    p.getChildByName("n1").assignPassedResults(a,b,c)
    #
    startt=datetime.now()
    ex.RunW(p,0)
    t1=datetime.now()-startt
    #
    self.assertEqual(n1.getState(),pilot.DONE)
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertEqual(p.getChildByName("n2").getOutputPort("o4").getPyObj(),[6,12,16,63,-4,10])
    pass

  def test10(self):
    fname=os.path.join(self.workdir, "test10.xml")
    from datetime import datetime
    p=self.r.createProc("prTest2")
    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    cont.setProperty("type","multi")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    tsi=p.createSequenceTc("seqint","seqint",ti)
    tsd=p.createSequenceTc("seqdbl","seqdbl",td)
    n0=self.r.createScriptNode("","n0")
    o0=n0.edAddOutputPort("o0",tsi)
    n0.setScript("o0=[ 3*elt for elt in range(12) ]")
    p.edAddChild(n0)
    n1=self.r.createForEachLoop("n1",ti)
    n10=self.r.createScriptNode("","n10")
    n10.setExecutionMode("remote")
    n10.setContainer(cont)
    n1.edAddChild(n10)
    n10.setScript("""
import time
if i1%2==0:
  raise Exception("Simulated error !")
else:
  time.sleep(0.1)
  o2=4*i1
""")
    i1=n10.edAddInputPort("i1",ti)
    o2=n10.edAddOutputPort("o2",ti)
    p.edAddChild(n1)
    p.edAddLink(o0,n1.edGetSeqOfSamplesPort())
    p.edAddLink(n1.edGetSamplePort(),i1)
    p.edAddCFLink(n0,n1)
    n1.edGetNbOfBranchesPort().edInitPy(2)
    n2=self.r.createScriptNode("","n2")
    n2.setScript("o4=i3")
    i3=n2.edAddInputPort("i3",tsi)
    o4=n2.edAddOutputPort("o4",tsi)
    n2.setScript("o4=i3")
    p.edAddChild(n2)
    p.edAddCFLink(n1,n2)
    p.edAddLink(o2,i3)
    p.saveSchema(fname)
    #
    l=loader.YACSLoader()
    p=l.load(fname)
    n1=p.getChildByName("n1")
    ex=pilot.ExecutorSwig()
    ex.setKeepGoingProperty(True)
    #
    startt=datetime.now()
    ex.RunW(p,0)
    t0=datetime.now()-startt
    #
    self.assertEqual(p.getState(),pilot.FAILED)
    self.assertEqual(n1.getState(),pilot.FAILED)
    n1.edGetSeqOfSamplesPort().getPyObj()
    a,b,c=n1.getPassedResults(ex)
    self.assertEqual(a,[1,3,5,7,9,11])
    self.assertEqual([elt.getPyObj() for elt in b],[[12,36,60,84,108,132]])
    self.assertEqual(c,['n10_o2_interceptor'])
    
    p.getChildByName("n1").getChildByName("n10").setScript("""
import time
if i1%2==1:
  raise Exception("Simulated error !")
else:
  time.sleep(1)
  o2=5*i1
""")
    ex=pilot.ExecutorSwig()
    ex.setKeepGoingProperty(True)
    p.getChildByName("n1").assignPassedResults(a,b,c)
    #
    startt=datetime.now()
    ex.RunW(p,0)
    t1=datetime.now()-startt
    #assert(t1.total_seconds()<6.+1.)# normally 6/2+1 s (6 remaining elts in 2 // branches + 1s to launch container)
    #
    self.assertEqual(n1.getState(),pilot.DONE)
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertEqual(p.getChildByName("n2").getOutputPort("o4").getPyObj(),[0,12,30,36,60,60,90,84,120,108,150,132])
    pass

  pass


  def test11(self):
    "test if we do not restart from the begining of the schema after an error in a foreach"
    fname=os.path.join(self.workdir, "test11.xml")
    from datetime import datetime
    p=self.r.createProc("prTest2")
    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    cont.setProperty("type","multi")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    tsi=p.createSequenceTc("seqint","seqint",ti)
    tsd=p.createSequenceTc("seqdbl","seqdbl",td)
    n0=self.r.createScriptNode("","n0")
    o0=n0.edAddOutputPort("o0",tsi)
    n0.setScript("o0=[ elt for elt in range(12) ]")
    p.edAddChild(n0)
    n1=self.r.createForEachLoop("n1",ti)
    n10=self.r.createScriptNode("","n10")
    n10.setExecutionMode("remote")
    n10.setContainer(cont)
    n1.edAddChild(n10)
    n10.setScript("""
import time
if i1%2==1:
  raise Exception("Simulated error !")
else:
  time.sleep(0.1)
  o2=2*i1
""")
    i1=n10.edAddInputPort("i1",ti)
    o2=n10.edAddOutputPort("o2",ti)
    p.edAddChild(n1)
    p.edAddLink(o0,n1.edGetSeqOfSamplesPort())
    p.edAddLink(n1.edGetSamplePort(),i1)
    p.edAddCFLink(n0,n1)
    n1.edGetNbOfBranchesPort().edInitPy(2)
    n2=self.r.createScriptNode("","n2")
    n2.setScript("o4=i3")
    i3=n2.edAddInputPort("i3",tsi)
    o4=n2.edAddOutputPort("o4",tsi)
    n2.setScript("o4=i3")
    p.edAddChild(n2)
    p.edAddCFLink(n1,n2)
    p.edAddLink(o2,i3)
    p.saveSchema(fname)
    #
    l=loader.YACSLoader()
    p=l.load(fname)
    n1=p.getChildByName("n1")
    ex=pilot.ExecutorSwig()
    ex.setKeepGoingProperty(True)
    #
    startt=datetime.now()
    ex.RunW(p,0)
    t0=datetime.now()-startt
    #
    self.assertEqual(p.getState(),pilot.FAILED)
    self.assertEqual(n1.getState(),pilot.FAILED)
    n1.edGetSeqOfSamplesPort().getPyObj()
    a,b,c=n1.getPassedResults(ex)

    self.assertEqual(a,[0,2,4,6,8,10])
    self.assertEqual([elt.getPyObj() for elt in b],[[0,4,8,12,16,20]])
    
    p.getChildByName("n0").setScript("o0=[ 3*elt for elt in range(12) ]")
    p.getChildByName("n1").getChildByName("n10").setScript("""
import time
if i1%2==0:
  raise Exception("Simulated error !")
else:
  time.sleep(1)
  o2=5*i1
""")
    p.resetState(1)


    p.getChildByName("n1").assignPassedResults(a,b,c)
    p.exUpdateState();
    #
    startt=datetime.now()
    ex.RunW(p,0,False)
    t1=datetime.now()-startt
    #
    self.assertEqual(n1.getState(),pilot.DONE)
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertEqual(p.getChildByName("n2").getOutputPort("o4").getPyObj(),[0,5,4,15,8,25,12,35,16,45,20,55])
    pass
  
  def test12(self):
    """ Test of nested ForEachLoop with a port connected inside and outside the loop."""
    schema = self.r.createProc("schema")
    ti = schema.getTypeCode("int")
    tiset = schema.createSequenceTc("", "seqint", ti)
    tisetseq = schema.createSequenceTc("", "seqintvec", tiset)

    n1 = self.r.createScriptNode("", "PyScript2")
    n1.edAddInputPort("i3", ti)
    n1.edAddInputPort("i4", ti)
    n1.edAddOutputPort("o5", ti)
    n1.setScript("o5=i3+i4")

    n2 = self.r.createScriptNode("", "PyScript1")
    n2.edAddInputPort("i2", ti)
    n2.edAddOutputPort("o3", ti)
    n2.setScript("o3=i2")

    b1 = self.r.createBloc("Bloc1")
    b1.edAddChild(n1)
    b1.edAddChild(n2)

    fe1 = self.r.createForEachLoop("ForEach1", ti)
    fe1.getInputPort("nbBranches").edInitPy(2)
    fe1.getInputPort("SmplsCollection").edInitPy([1, 2, 3, 4])
    fe1.edSetNode(b1)

    n3 = self.r.createScriptNode("", "PostProcessing")
    n3.edAddInputPort("i7", tiset)
    n3.edAddInputPort("i5", tiset)
    n3.edAddOutputPort("o4", ti)
    n3.setScript("""
o4 = 0
for i in i7:
    o4 = i + o4

for i in i5:
    o4 = i + o4
""")

    b0 = self.r.createBloc("Bloc0")
    b0.edAddChild(fe1)
    b0.edAddChild(n3)

    fe0 = self.r.createForEachLoop("ForEach1", ti)
    fe0.getInputPort("nbBranches").edInitPy(2)
    fe0.getInputPort("SmplsCollection").edInitPy([1, 2, 3, 4])
    fe0.edSetNode(b0)

    schema.edAddChild(fe0)

    nx = self.r.createScriptNode("", "Result")
    nx.edAddInputPort("i8", tiset)
    nx.edAddOutputPort("o6", ti)
    nx.setScript("""
o6 = 0
for i in i8:
    o6 = i + o6
""")
    schema.edAddChild(nx)

    schema.edAddLink(fe1.getOutputPort("evalSamples"), n1.getInputPort("i3"))
    schema.edAddLink(fe0.getOutputPort("evalSamples"), n1.getInputPort("i4"))

    schema.edAddDFLink(n1.getOutputPort("o5"), n3.getInputPort("i7"))
    schema.edAddDFLink(n2.getOutputPort("o3"), n3.getInputPort("i5"))

    po5 = fe1.getOutputPort("Bloc1.PyScript2.o5")
    schema.edAddDFLink(po5, n2.getInputPort("i2"))

    schema.edAddDFLink(n3.getOutputPort("o4"), nx.getInputPort("i8"))
#    schema.saveSchema("foreach12.xml")
    
    e = pilot.ExecutorSwig()
    e.RunW(schema)
    self.assertEqual(schema.getState(),pilot.DONE)
    resVal = schema.getChildByName("Result").getOutputPort("o6").getPyObj()
    self.assertEqual(resVal, 160)
    pass

  def test13(self):
    """ Non regression test EDF11239. ForEach into ForEach. Problem on cloning linked to DeloymentTree.appendTask method that was too strong."""
    p=self.r.createProc("Bug11239")
    ti=p.createType("int","int")
    ti2=p.createSequenceTc("seqint","seqint",ti)
    #
    cont=p.createContainer("DefaultContainer","Salome")
    #
    node0=self.r.createForEachLoop("ForEachLoop_int0",ti)
    p.edAddChild(node0)
    node0.edGetSeqOfSamplesPort().edInitPy(list(range(4)))
    node0.edGetNbOfBranchesPort().edInitInt(2)
    #
    node00=self.r.createBloc("Bloc0")
    node0.edAddChild(node00)
    node000_0=self.r.createForEachLoop("ForEachLoop_int1",ti)
    node00.edAddChild(node000_0)
    node000_0.edGetSeqOfSamplesPort().edInitPy(list(range(4)))
    node000_0.edGetNbOfBranchesPort().edInitInt(3)
    #
    node0000=self.r.createBloc("Bloc1")
    node000_0.edAddChild(node0000)
    #
    node0000_0=self.r.createScriptNode("","PyScript2")
    node0000.edAddChild(node0000_0)
    i3=node0000_0.edAddInputPort("i3",ti)
    i4=node0000_0.edAddInputPort("i4",ti)
    o5=node0000_0.edAddOutputPort("o5",ti)
    node0000_0.setScript("o5 = i3 + i4")
    node0000_0.setContainer(cont)
    node0000_0.setExecutionMode("remote")
    p.edAddLink(node0.edGetSamplePort(),i3)
    p.edAddLink(node000_0.edGetSamplePort(),i4)
    #
    node0000_1=self.r.createScriptNode("","PyScript1")
    node0000.edAddChild(node0000_1)
    o3=node0000_1.edAddOutputPort("o3",ti)
    node0000_1.setScript("o3 = 7")
    node0000_1.setExecutionMode("local")
    p.edAddCFLink(node0000_0,node0000_1)
    #
    node000_1=self.r.createScriptNode("","PostTraitement")
    node00.edAddChild(node000_1)
    i7=node000_1.edAddInputPort("i7",ti2)
    i5=node000_1.edAddInputPort("i5",ti2)
    node000_1.setScript("for i in i7:\n    print(i)\nprint(\"separation\")\nfor i in i5:\n    print(i)")
    node000_1.setContainer(cont)
    node000_1.setExecutionMode("remote")
    p.edAddLink(o5,i7)
    p.edAddLink(o3,i5)
    p.edAddCFLink(node000_0,node000_1)
    #
    #p.saveSchema("tmpp.xml")
    ex = pilot.ExecutorSwig()
    self.assertEqual(p.getState(),pilot.READY)
    ex.RunW(p,0)
    self.assertEqual(p.getState(),pilot.DONE)
    pass

  def test14(self):
    """ Non regression EDF11027. Problem after Save/Load of a foreach node with type pyobj with input "SmplsCollection" manually set before. Correction in convertToYacsObjref from XML->Neutral. Objref can hide a string !"""
    xmlFileName=os.path.join(self.workdir, "test14.xml")
    SALOMERuntime.RuntimeSALOME_setRuntime()
    r=pilot.getRuntime()
    n0=r.createProc("test23/zeRun")
    tp=n0.createInterfaceTc("python:obj:1.0","pyobj",[])
    tp2=n0.createSequenceTc("list[pyobj]","list[pyobj]",tp)
    n0bis=r.createBloc("test23/main") ; n0.edAddChild(n0bis)
    n00=r.createBloc("test23/run") ; n0bis.edAddChild(n00)
    #
    n000=r.createForEachLoop("test23/FE",tp) ; n00.edAddChild(n000)
    n0000=r.createScriptNode("Salome","test23/run_internal") ; n000.edSetNode(n0000)
    i0=n0000.edAddInputPort("i0",tp)
    i1=n0000.edAddInputPort("i1",tp) ; i1.edInitPy(3)
    o0=n0000.edAddOutputPort("o0",tp)
    n0000.setScript("o0=i0+i1")
    #
    n00.edAddLink(n000.edGetSamplePort(),i0)
    #
    n000.edGetSeqOfSamplesPort().edInitPy(list(range(10)))
    n000.edGetNbOfBranchesPort().edInitInt(2)
    #
    n01=r.createScriptNode("Salome","test23/check") ; n0bis.edAddChild(n01)
    n0bis.edAddCFLink(n00,n01)
    i2=n01.edAddInputPort("i2",tp2)
    o1=n01.edAddOutputPort("o1",tp2)
    n01.setScript("o1=i2")
    n0bis.edAddLink(o0,i2)
    #
    n0.saveSchema(xmlFileName)
    #
    l=loader.YACSLoader()
    p=l.load(xmlFileName) # very import do not use n0 but use p instead !
    ex=pilot.ExecutorSwig()
    #
    self.assertEqual(p.getState(),pilot.READY)
    ex.RunW(p,0)
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertEqual(p.getChildByName("test23/main.test23/check").getOutputPort("o1").getPyObj(),[3,4,5,6,7,8,9,10,11,12])
    pass

  def test15(self):
    from salome.kernel.SALOME_PyNode import UnProxyObjectSimple
    #fname=os.path.join(self.workdir, "BugInConcurrentLaunchDftCont.xml")
    p=self.r.createProc("pr")
    ti=p.createType("int","int")
    cont=p.createContainer("DefaultContainer","Salome")
    # enable WorkloadManager mode because containers are not registered right
    # in classical mode (4 containers with the same name are launched at the
    # same time).
    p.setProperty("executor", "WorkloadManager")
    cont.setProperty("type", "multi")
    cont.setProperty("container_name","FactoryServer")
    b=self.r.createBloc("Bloc") ; p.edAddChild(b)
    #
    nb=4
    outs=[]
    for i in range(nb):
      node=self.r.createScriptNode("Salome","node%d"%i)
      node.setExecutionMode("remote")
      node.setContainer(cont)
      outs.append(node.edAddOutputPort("i",ti))
      node.setScript("i=%d"%i)
      b.edAddChild(node)
    #
    node=self.r.createScriptNode("Salome","nodeEnd")
    node.setExecutionMode("remote")
    node.setContainer(cont)
    res=node.edAddOutputPort("res",ti)
    p.edAddChild(node)
    l=[]
    for i in range(nb):
      elt="i%d"%i
      inp=node.edAddInputPort(elt,ti) ; l.append(elt)
      p.edAddChild(node)
      p.edAddLink(outs[i],inp)
    node.setScript("res="+"+".join(l))
    p.edAddCFLink(b,node)
    #
    for i in range(10):
      p.init()
      ex = pilot.ExecutorSwig()
      self.assertEqual(p.getState(),pilot.READY)
      ex.RunW(p,0)
      self.assertEqual(UnProxyObjectSimple( res.getPyObj() ),6)
      self.assertEqual(p.getState(),pilot.DONE)
    pass

  def test16(self):
    """ Test to check that a list[pyobj] outputport linked to pyobj inputport is OK."""
    SALOMERuntime.RuntimeSALOME_setRuntime()
    self.r=pilot.getRuntime()
    n0=self.r.createProc("test16/zeRun")
    tp=n0.createInterfaceTc("python:obj:1.0","pyobj",[])
    tp2=n0.createSequenceTc("list[pyobj]","list[pyobj]",tp)
    
    n00=self.r.createScriptNode("Salome","n00") ; n0.edAddChild(n00)
    o0=n00.edAddOutputPort("o0",tp2)
    n00.setScript("o0=[[i+1] for i in range(8)]")
    n01=self.r.createScriptNode("Salome","n01") ; n0.edAddChild(n01)
    i1=n01.edAddInputPort("i1",tp)
    n01.setScript("assert(i1==[[1], [2], [3], [4], [5], [6], [7], [8]])")
    n0.edAddCFLink(n00,n01)
    n0.edAddLink(o0,i1)
    #
    ex=pilot.ExecutorSwig()
    self.assertEqual(n0.getState(),pilot.READY)
    ex.RunW(n0,0)
    self.assertEqual(n0.getState(),pilot.DONE)
    pass

  def test17(self):
    """ Same as test16 except that tp2 is not list of tp but a list of copy of tp"""
    SALOMERuntime.RuntimeSALOME_setRuntime()
    self.r=pilot.getRuntime()
    n0=self.r.createProc("test17/zeRun")
    tp=n0.createInterfaceTc("python:obj:1.0","pyobj",[])
    tpp=n0.createInterfaceTc("python:obj:1.0","pyobj",[]) # diff is here
    tp2=n0.createSequenceTc("list[pyobj]","list[pyobj]",tpp)
    
    n00=self.r.createScriptNode("Salome","n00") ; n0.edAddChild(n00)
    o0=n00.edAddOutputPort("o0",tp2)
    n00.setScript("o0=[[i+1] for i in range(8)]")
    n01=self.r.createScriptNode("Salome","n01") ; n0.edAddChild(n01)
    i1=n01.edAddInputPort("i1",tp)
    n01.setScript("assert(i1==[[1], [2], [3], [4], [5], [6], [7], [8]])")
    n0.edAddCFLink(n00,n01)
    n0.edAddLink(o0,i1)
    #
    ex=pilot.ExecutorSwig()
    self.assertEqual(n0.getState(),pilot.READY)
    ex.RunW(n0,0)
    self.assertEqual(n0.getState(),pilot.DONE)
    pass

  def test18(self):
    p=self.r.createProc("prTest18")
    n00=self.r.createScriptNode("Salome","n00")
    self.assertEqual(n00.getMaxLevelOfParallelism(),1)
    n00.setExecutionMode("remote")
    self.assertEqual(n00.getMaxLevelOfParallelism(),1)
    cont=p.createContainer("gg","Salome")
    n00.setContainer(cont)
    self.assertEqual(n00.getMaxLevelOfParallelism(),1)
    cont.setProperty("nb_proc_per_nod","6")
    self.assertEqual(n00.getMaxLevelOfParallelism(),1)
    cont.setProperty("nb_proc_per_node","7")           # <- here
    self.assertEqual(n00.getMaxLevelOfParallelism(),7) # <- here
    pass
    
  def test19(self):
    """This test checks the mechanism of YACS that allow PythonNodes to know their DynParaLoop context."""
    fname=os.path.join(self.workdir, "test19.xml")
    l=loader.YACSLoader()
    #
    p=self.r.createProc("PROC")
    p.setProperty("executor","workloadmanager")
    ti=p.createType("int","int")
    tdi=p.createSequenceTc("seqint","seqint",ti)
    # Level0
    fe0=self.r.createForEachLoop("FE0",ti) ; p.edAddChild(fe0)
    fe0.edGetNbOfBranchesPort().edInitInt(4)
    fe0_end=self.r.createScriptNode("Salome","fe0_end")
    fe0.edSetFinalizeNode(fe0_end)
    fe0_end.setScript("""assert([elt[0] for elt in my_dpl_localization]==["FE0"])
assert(my_dpl_localization[0][1]>=0 and my_dpl_localization[0][1]<4)""")
    n0=self.r.createScriptNode("Salome","n0") ; p.edAddChild(n0)
    n0.setScript("o1=list(range(10))")
    a=n0.edAddOutputPort("o1",tdi)
    p.edAddLink(a,fe0.edGetSeqOfSamplesPort()) ; p.edAddCFLink(n0,fe0)
    # Level1
    b0=self.r.createBloc("b0") ; fe0.edAddChild(b0)
    n1=self.r.createScriptNode("Salome","n1") ; b0.edAddChild(n1)
    n1.setScript("""assert([elt[0] for elt in my_dpl_localization]==["FE0"])
assert(my_dpl_localization[0][1]>=0 and my_dpl_localization[0][1]<4)
o1=list(range(10))""")
    b=n1.edAddOutputPort("o1",tdi)
    fe1=self.r.createForEachLoop("FE1",ti) ; b0.edAddChild(fe1)
    fe1.edGetNbOfBranchesPort().edInitInt(3)
    fe1_end=self.r.createScriptNode("Salome","fe1_end")
    fe1_end.setScript("""assert([elt[0] for elt in my_dpl_localization]==["FE0.b0.FE1","FE0"])
assert(my_dpl_localization[1][1]>=0 and my_dpl_localization[1][1]<4)
assert(my_dpl_localization[0][1]>=0 and my_dpl_localization[0][1]<3)
""")
    fe1.edSetFinalizeNode(fe1_end)
    p.edAddLink(b,fe1.edGetSeqOfSamplesPort()) ; p.edAddCFLink(n1,fe1)
    # Level2
    n2=self.r.createScriptNode("Salome","n2") ; fe1.edAddChild(n2)
    n2.setScript("""assert([elt[0] for elt in my_dpl_localization]==["FE0.b0.FE1","FE0"])
assert(my_dpl_localization[1][1]>=0 and my_dpl_localization[1][1]<4)
assert(my_dpl_localization[0][1]>=0 and my_dpl_localization[0][1]<3)
""")
    
    p.saveSchema(fname)
    ex=pilot.ExecutorSwig()
    
    # local run of PythonNodes n1 and n2
    p=l.load(fname)
    p.init()
    self.assertEqual(p.getState(),pilot.READY)
    ex.setDPLScopeSensitive(True) # <- this line is the aim of the test
    ex.RunW(p,0)
    self.assertEqual(p.getState(),pilot.DONE)

    # run remote
    p=l.load(fname)
    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    # no limit for the number of containers launched
    cont.setProperty("nb_proc_per_node","0")
    cont.setProperty("type","multi")
    #cont.usePythonCache(True)
    cont.attachOnCloning()
    n1=p.getChildByName("FE0.b0.n1") ; n1.setExecutionMode("remote") ; n1.setContainer(cont)
    n2=p.getChildByName("FE0.b0.FE1.n2") ; n2.setExecutionMode("remote") ; n2.setContainer(cont)
    p.init()
    self.assertEqual(p.getState(),pilot.READY)
    ex.RunW(p,0)
    self.assertEqual(p.getState(),pilot.DONE)
    pass

  def test20(self):
    """This test revealed a huge bug in ElementaryNode contained in a loop or foreach. The RECONNECT state generated invalid dependancies that only HPContainer can reveal the problem"""
    def assignCont(n,cont):
      n.setExecutionMode("remote") ; n.setContainer(cont) 
      pass
    xmlFileName="test20.xml"
    p=self.r.createProc("test26")
    p.setProperty("executor","workloadmanager")
    #
    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    # no limit for the number of containers launched
    cont.setProperty("nb_proc_per_node","0")
    cont.setProperty("type","multi")
    cont.usePythonCache(True)
    cont.attachOnCloning()
    #
    po=p.createInterfaceTc("python:obj:1.0","pyobj",[])
    sop=p.createSequenceTc("list[pyobj]","list[pyobj]",po)
    #
    b0=self.r.createBloc("test26/main") ; p.edAddChild(b0)
    n0=self.r.createScriptNode("Salome","test26/n0") ; assignCont(n0,cont) # 1
    n0.setScript("""import os
dd=list( range(10) )""")
    dd=n0.edAddOutputPort("dd",sop) ; b0.edAddChild(n0)
    fe0=self.r.createForEachLoop("test26/FE0",po) ; b0.edAddChild(fe0)
    fe0.edGetNbOfBranchesPort().edInitInt(1) # very important for the test : 1 !
    fe0i=self.r.createBloc("test26/FE0_internal") ; fe0.edSetNode(fe0i)
    zeArgInitNode2=self.r.createScriptNode("Salome","zeArgInitNode") ; assignCont(zeArgInitNode2,cont) # 2
    fe0i.edAddChild(zeArgInitNode2)
    c1=zeArgInitNode2.edAddInputPort("c",po)
    c2=zeArgInitNode2.edAddOutputPort("c",po)
    zeRun=self.r.createBloc("test26/zeRun") ; fe0i.edAddChild(zeRun)
    zeArgInitNode=self.r.createScriptNode("Salome","zeArgInitNode") ; assignCont(zeArgInitNode,cont) # 3
    zeRun.edAddChild(zeArgInitNode)
    ff1=zeArgInitNode.edAddInputPort("ff",po)
    ff2=zeArgInitNode.edAddOutputPort("ff",po)
    line01=self.r.createScriptNode("Salome","line01") ; zeRun.edAddChild(line01) ; assignCont(line01,cont) # 4
    line01.setScript("ee=3")
    ee0=line01.edAddOutputPort("ee",po)
    initt=self.r.createScriptNode("Salome","test26/initt") ; assignCont(initt,cont) # 5
    initt.setScript("pass") ; zeRun.edAddChild(initt)
    end=self.r.createScriptNode("Salome","test26/end") ; assignCont(end,cont) # 6
    end.setScript("import os") ; zeRun.edAddChild(end)
    retu=self.r.createScriptNode("Salome","return") ; assignCont(retu,cont) # 7
    retu.setScript("ee=i0") ; zeRun.edAddChild(retu)
    i0=retu.edAddInputPort("i0",po)
    ee=retu.edAddOutputPort("ee",po)
    zeRun.edAddCFLink(zeArgInitNode,line01)
    zeRun.edAddCFLink(line01,initt)
    zeRun.edAddCFLink(initt,end)
    zeRun.edAddCFLink(end,retu)
    p.edAddLink(ee0,i0)
    #
    returnn=self.r.createScriptNode("Salome","return") ; assignCont(returnn,cont) # 8
    returnn.setScript("elt=i0")
    i00=returnn.edAddInputPort("i0",po)
    elt=returnn.edAddOutputPort("elt",po)
    fe0i.edAddChild(returnn)
    fe0i.edAddCFLink(zeArgInitNode2,zeRun)
    fe0i.edAddCFLink(zeRun,returnn)
    p.edAddLink(c2,ff1)
    p.edAddLink(ee,i00)
    #
    finalize=self.r.createScriptNode("Salome","test26/finalize") ; b0.edAddChild(finalize) ; assignCont(finalize,cont) # 9
    finalize.setScript("pass")
    b0.edAddCFLink(n0,fe0)
    b0.edAddCFLink(fe0,finalize)
    #
    p.edAddLink(dd,fe0.edGetSeqOfSamplesPort())
    p.edAddLink(fe0.edGetSamplePort(),c1)
    #
    #xmlFileName="test20.xml"
    #p.saveSchema(xmlFileName)
    p.getChildByName("test26/main.test26/FE0").edGetNbOfBranchesPort().edInitInt(1) # very important 1 !
    #
    ex=pilot.ExecutorSwig()
    self.assertEqual(p.getState(),pilot.READY)
    ex.RunW(p,0)
    self.assertEqual(p.getState(),pilot.DONE)
    pass

  pass

  def test21(self):
    "test if we restart from a saved state in a foreach loop"
    fname=os.path.join(self.workdir, "test21.xml")
    xmlStateFileName=os.path.join(self.workdir, "saveState21.xml")
    from datetime import datetime
    p=self.r.createProc("prTest21")
    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    cont.setProperty("type","multi")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    tsi=p.createSequenceTc("seqint","seqint",ti)
    tsd=p.createSequenceTc("seqdbl","seqdbl",td)
    n0=self.r.createScriptNode("","n0")
    o0=n0.edAddOutputPort("o0",tsi)
    n0.setScript("o0=[ elt for elt in range(6) ]")
    p.edAddChild(n0)
    n1=self.r.createForEachLoop("n1",ti)
    n10=self.r.createScriptNode("","n10")
    n10.setExecutionMode("remote")
    n10.setContainer(cont)
    n1.edAddChild(n10)
    n10.setScript("""
import time
time.sleep(9)
o2=2*i1
""")
    i1=n10.edAddInputPort("i1",ti)
    o2=n10.edAddOutputPort("o2",ti)
    p.edAddChild(n1)
    p.edAddLink(o0,n1.edGetSeqOfSamplesPort())
    p.edAddLink(n1.edGetSamplePort(),i1)
    p.edAddCFLink(n0,n1)
    n1.edGetNbOfBranchesPort().edInitPy(2)
    n2=self.r.createScriptNode("","n2")
    n2.setScript("o4=i3")
    i3=n2.edAddInputPort("i3",tsi)
    o4=n2.edAddOutputPort("o4",tsi)
    n2.setScript("o4=i3")
    p.edAddChild(n2)
    p.edAddCFLink(n1,n2)
    p.edAddLink(o2,i3)
    p.saveSchema(fname)
    #
    l=loader.YACSLoader()
    p=l.load(fname)
    n1=p.getChildByName("n1")
    ex=pilot.ExecutorSwig()
    ex.setKeepGoingProperty(True)
    #
    startt=datetime.now()
    import threading
    myRun=threading.Thread(None, ex.RunW, None, (p,0))
    myRun.start()
    import time
    time.sleep(15)
    SALOMERuntime.schemaSaveState(p, ex, xmlStateFileName)
    a,b,c=n1.getPassedResults(ex)
    myRun.join()
    t0=datetime.now()-startt
    #
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertEqual(n1.getState(),pilot.DONE)
    self.assertEqual(a,[0,1])
    self.assertEqual([elt.getPyObj() for elt in b],[[0,2]])
    #
    p.getChildByName("n0").setScript("o0=[ 3*elt for elt in range(6) ]")
    p.getChildByName("n1").getChildByName("n10").setScript("""
import time
time.sleep(0.1)
o2=5*i1
""")
    loader.loadState(p, xmlStateFileName)
    p.resetState(1)
    p.getChildByName("n1").assignPassedResults(a,b,c)
    p.exUpdateState();
    #
    ex.RunW(p,0,False)
    #
    self.assertEqual(n1.getState(),pilot.DONE)
    self.assertEqual(p.getState(),pilot.DONE)
    self.assertEqual(p.getChildByName("n2").getOutputPort("o4").getPyObj(),[0,2,10,15,20,25])

    # Restart from a saved state in a foreach loop without using assignPassedResults.
    # This test uses the files test21.xml and saveState21.xml produced by test21.

    ex=pilot.ExecutorSwig()
    l=loader.YACSLoader()
    q=l.load(fname)
    q.getChildByName("n0").setScript("o0=[ 3*elt for elt in range(6) ]")
    q.getChildByName("n1").getChildByName("n10").setScript("""
import time
time.sleep(0.1)
print("execution n10:", i1)
o2=5*i1
""")
    q.getChildByName("n2").setScript("""
print("execution n2:", i3)
o4=i3
""")
    loader.loadState(q, xmlStateFileName)
    q.resetState(1)
    q.exUpdateState()
    #
    ex.RunW(q,0,False)
    #
    self.assertEqual(q.getChildByName("n1").getState(),pilot.DONE)
    self.assertEqual(q.getState(),pilot.DONE)
    self.assertEqual(q.getChildByName("n2").getOutputPort("o4").getPyObj(),[0,2,10,15,20,25])
    pass

  def test23(self):
    """ test focused on weight attribut after a dump and reload from a xml file
    """
    fname=os.path.join(self.workdir, "test23.xml")
    p=self.r.createProc("prTest23")
    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    cont.setProperty("type","multi")
    td=p.createType("double","double")
    ti=p.createType("int","int")
    tsi=p.createSequenceTc("seqint","seqint",ti)
    tsd=p.createSequenceTc("seqdbl","seqdbl",td)
    n0=self.r.createScriptNode("","n0")
    o0=n0.edAddOutputPort("o0",tsi)
    n0.setScript("o0=[ elt for elt in range(6) ]")
    p.edAddChild(n0)
    n1=self.r.createForEachLoop("n1",ti)
    n1.setWeight(3)
    n10=self.r.createScriptNode("","n10")
    n10.setExecutionMode("remote")
    n10.setContainer(cont)
    n1.edAddChild(n10)
    n10.setScript("""
import time
time.sleep(2)
o2=2*i1
""")
    n10.setWeight(4.)
    i1=n10.edAddInputPort("i1",ti)
    o2=n10.edAddOutputPort("o2",ti)
    p.edAddChild(n1)
    p.edAddLink(o0,n1.edGetSeqOfSamplesPort())
    p.edAddLink(n1.edGetSamplePort(),i1)
    p.edAddCFLink(n0,n1)
    n1.edGetNbOfBranchesPort().edInitPy(2)
    n2=self.r.createScriptNode("","n2")
    n2.setScript("o4=i3")
    i3=n2.edAddInputPort("i3",tsi)
    o4=n2.edAddOutputPort("o4",tsi)
    n2.setScript("o4=i3")
    p.edAddChild(n2)
    p.edAddCFLink(n1,n2)
    p.edAddLink(o2,i3)
    p.saveSchema(fname)
    #
    l=loader.YACSLoader()
    p=l.load(fname)
    self.assertEqual(p.getChildByName("n1").getWeight().getSimpleLoopWeight(),3.0)
    self.assertEqual(p.getChildByName("n1").getChildByName("n10").getWeight().getElementaryWeight(),4.0)
    pass

  def test24(self):
    """ Non regression test EDF17470"""
    SALOMERuntime.RuntimeSALOME.setRuntime()
    r=SALOMERuntime.getSALOMERuntime()
    p=r.createProc("prTest2")
    #
    cont1=p.createContainer("cont1","Salome")
    cont1.setProperty("name","localhost")
    cont1.setProperty("hostname","localhost")
    cont1.setProperty("type","multi")
    cont1.setProperty("container_name","container1")
    #
    cont2=p.createContainer("cont2","Salome")
    cont2.setProperty("name","localhost")
    cont2.setProperty("hostname","localhost")
    cont2.setProperty("type","multi")
    cont2.setProperty("container_name","container2")
    #
    td=p.createType("double","double")
    ti=p.createType("int","int")
    ts=p.createType("string","string")
    n0=r.createScriptNode("","n0")
    n0.setScript("""from salome.kernel import SalomeSDSClt
from salome.kernel import SALOME
from salome.kernel import salome
import unittest
import pickle
import gc
import time

def obj2Str(obj):
  return pickle.dumps(obj,pickle.HIGHEST_PROTOCOL)
def str2Obj(strr):
  return pickle.loads(strr)


salome.salome_init()
scopeName="Scope1"
varName="a"
dsm=salome.naming_service.Resolve("/DataServerManager")
dsm.cleanScopesInNS()
if scopeName in dsm.listScopes():
  dsm.removeDataScope(scopeName)
dss,isCreated=dsm.giveADataScopeTransactionCalled(scopeName)
#
t0=dss.createRdExtVarTransac(varName,obj2Str({"ab":[4,5,6]}))
dss.atomicApply([t0])
""")
    n0_sn=n0.edAddOutputPort("scopeName",ts)
    n0_vn=n0.edAddOutputPort("varName",ts)
    #
    n1=r.createScriptNode("","n1")
    n1_sn=n1.edAddInputPort("scopeName",ts)
    n1_vn=n1.edAddInputPort("varName",ts)
    n1.setScript("""from salome.kernel import SalomeSDSClt
from salome.kernel import SALOME
from salome.kernel import salome
import unittest
import pickle
import gc
import time


def obj2Str(obj):
  return pickle.dumps(obj,pickle.HIGHEST_PROTOCOL)
def str2Obj(strr):
  return pickle.loads(strr)

salome.salome_init()
dsm=salome.naming_service.Resolve("/DataServerManager")
dss,isCreated=dsm.giveADataScopeTransactionCalled(scopeName)
assert(not isCreated)

t1=dss.addMultiKeyValueSession(varName)
# lecture 'ef'
wk2=dss.waitForKeyInVar(varName,obj2Str("ef"))
wk2.waitFor()
assert(str2Obj(dss.waitForMonoThrRev(wk2))==[11,12])""")
    n1.setContainer(cont1)
    n1.setExecutionMode("remote")
    #
    n2=r.createScriptNode("","n2")
    n2_sn=n2.edAddInputPort("scopeName",ts)
    n2_vn=n2.edAddInputPort("varName",ts)
    n2.setScript("""from salome.kernel import SalomeSDSClt
from salome.kernel import SALOME
from salome.kernel import salome
import unittest
import pickle
import gc
import time


def obj2Str(obj):
  return pickle.dumps(obj,pickle.HIGHEST_PROTOCOL)
def str2Obj(strr):
  return pickle.loads(strr)

salome.salome_init()
dsm=salome.naming_service.Resolve("/DataServerManager")
dss,isCreated=dsm.giveADataScopeTransactionCalled(scopeName)
assert(not isCreated)
time.sleep(3.)
t1=dss.addMultiKeyValueSession(varName)
t1.addKeyValueInVarErrorIfAlreadyExistingNow(obj2Str("cd"),obj2Str([7,8,9,10]))
t1.addKeyValueInVarErrorIfAlreadyExistingNow(obj2Str("ef"),obj2Str([11,12]))
""")
    n2.setContainer(cont2)
    n2.setExecutionMode("remote")
    #
    p.edAddChild(n0)
    p.edAddChild(n1)
    p.edAddChild(n2)
    p.edAddCFLink(n0,n1)
    p.edAddCFLink(n0,n2)
    p.edAddLink(n0_sn,n1_sn)
    p.edAddLink(n0_vn,n1_vn)
    p.edAddLink(n0_sn,n2_sn)
    p.edAddLink(n0_vn,n2_vn)
    #
    ex=pilot.ExecutorSwig()
    ex.RunW(p,0)
    self.assertEqual(p.getState(),pilot.DONE)
    pass

  def test25(self):
    fname=os.path.join(self.workdir, "test25.xml")
    p=self.r.createProc("p0")
    tp=p.createInterfaceTc("python:obj:1.0","pyobj",[])
    n1_0_sc=self.r.createScriptNode("Salome","n1_0_sc")
    p.edAddChild(n1_0_sc)
    n1_0_sc.setExecutionMode("remote")
    n1_0_sc.setScript("""""")
    i1_0_sc=n1_0_sc.edAddInputPort("i1",tp)
    i1_0_sc.edInitPy(list(range(4)))

    cont=p.createContainer("gg","Salome")
    cont.setProperty("name","localhost")
    cont.setProperty("hostname","localhost")
    n1_0_sc.setContainer(cont)

    p.saveSchema(fname)
    l=loader.YACSLoader()
    p=l.load(fname)
    ex=pilot.ExecutorSwig()
    self.assertEqual(p.getState(),pilot.READY)
    ex.RunW(p,0)
    self.assertEqual(p.getState(),pilot.DONE)
    pass

  def test27(self):
    """ 
    This test is here to check that old (<=930) graphs are always loadable.
    So an xml file coming from test14 in 930 has been generated and converted into home made "base64" like format.
    This test puts unbased64 byte array into test_930.xml and load it to check that everything is OK.
    """
    import os
    content_of_file = b'DDkShXM2PeNCndPqRfnYX5EAt.GaRgPq7dNqtfnYZgvqh=kQf7moXCE2z5lED.tCxgM2RcOqdfl29ePC9YnAx3uaGetqF5lE=.E2D0uS1eM2RcOqdfl2FjPqBYE2pdNq7fl2FjPqBYHoT3.2=.Ew9dsCdUFqVfOaj2Eaxet4BeN2=BOKRWOwF0PqfYMqdYHoT3.2=.EwxYNKHeNa=5O4heOwF4OKBeN2=7Maj2FaZXOaFDFwI.E2=1kibUua=5O4heOwF7Nq9YE2pdNq7fl2ZbMiFDFwI.E2=1nqFZNCdaM2RcOqdfl21dvqFZN2=7Maj2ECbWsKxbNQxYNKL6lo12HoT3.2=.EwneOCfeNqleM2RcOqdfl2BdPC9hcCbjN4Jfd2=APqRWuaRWuwF.uSxYNKFDFwI.E2=1kibUua=5O4heOwFAsiHdNqtYE2pdNq7fl2nWtCZbPaFDFwI.E2=1n4xbMiVdNqdYs2RcOqdfl26eNaVesq9g9qRWu4ZbOaHYFwI.E2=.E2=1kCHjMCdYsibUFqVfOaj2H4xbMiVdNqdYvupdNq7YE2PcMqfeOwFAe4BjOqdYHoT3.2=.E2=.Ew1Yvq1eNC9ds2RcOqdfl2VWsiVgMKdWPuxbPulXPqRdNqtYE2PcMqfeOwF.l2x5lE=.E2=.E2D.tCxUuaHWuS=5O4heOwFAPqRWu4ZbOaHjdqVfOaF.FiVXOidfl2McP49jNCbgeaHauaHYHoT3.2=.E2=.Ew1Yvq1eNC9ds2RcOqdfl2RcOqdYE2PcMqfeOwF1PqlcMq3jPC9YHoT3.2=.EwxAPqRWu4ZbOaHblE=.E2D2MqxgM2RcOqdfl29ePC9YnAx9O4ZbN2T3.2=.E2=.EwFXPqlUFqVfOaj2EidgsiHAnoHetqF5lE=.E2=.E2=.E2D4PqHeO4lVM2RcOqdfl29ePC9YnAx48WF.FqFYu4RgMKj2FAF.EqxjMCueOKtVMij2GoX2E29dsCdfl21dvqFZN2T3.2=.E2=.E2=.E2=.EwZbMqZbOa=5O4heOwF0uanWtAnDFCfbPuZbMidYtqVXN2T3.2=.E2=.E2=.E2=.E2=.EwngNCZUsiT1n4xWOaT1m2qg6WUWe0qjMAj7MAp7OAifdwDDH4xWOaT1nongNCZUsiT3.2=.E2=.E2=.E2=.E2=.EwZbMCxYsi=5O4heOwF7MAF.EibUuaj2ECbjN4JYHoT3.2=.E2=.E2=.E2=.E2=.EwZbMCxYsi=5O4heOwF7OAF.EibUuaj2ECbjN4JYHoT3.2=.E2=.E2=.E2=.E2=.Ewxesi1jNC9UFqVfOaj2Hq12E29dsCdfl21dvqFZN2x5lE=.E2=.E2=.E2=.E2DDGKRXOKReNwI.E2=.E2=.E2=1noNjNCdcP43blE=.E2=.E2=.E2D0O49cMqZbPK=APqRWtCxXOwF4O4BguaF5lE=.E2=.E2=.E2=.E2D4NCxfNqxWOaT0uanWtAnDFWcXnoNYvqhbPq7eNw=1laHjOq1jNC9bmaPcMqmcOq1XOanXnoNYvqhUvqHWtwI.E2=.E2=.E2=.E2=1kixbPq7eNw9ePC9YnAx48WR0uanWtAnDFCfbPuZbMidYtqVXMwx0vqRjMadbk2D0vq1jNC9bmK11no9jMCxYsiT3.2=.E2=.E2=.Ewx0O49cMqZbPKT3.2=.E2=.Ewx2MqxgNwI.E2=.E2=1mKRXOKReM2RcOqdfl29ePC9YnAxAMKdgPKF5lE=.E2=.E2=.E2DAv4HdMC9bkwljMadbkwVBf06c6eUhfqX9mKH9euT1noljMadbkwxAv4HdMC9blE=.E2=.E2=.E2D7Nq1jNC9UFqVfOaj2GKH2E29dsCdfl2BdPC9hcCbjN4Jfd2x5lE=.E2=.E2=.E2DDOi9UvqHWs2RcOqdfl2xcl2=0uS1eOwF1OKnWvO1dvqFZOuFDFwI.E2=.E2=1noZbMqZbOaT3.2=.E2=.EwljNq9YvqBbk2D4NCxfNqxWOaT0uanWtAnDFCfbMwx4NCxfNqxWOaT.Ew9jNqxWOaT0uanWtAnDH43eP4pXno9jNqxWOaT.EwxAPqRWtCxXNwI.E2=.E2=1kaVWu4BdNqpUH4xbMiHjMqj2FaVXPCdYFwI.E2=.E2=.E2=1laHjOqRjMadbkidgsiHAnoHetqR0uanWtAnDFWcbEidgsiHAnoHetqydNq9eNCRcMqDDFaHjOqRjMadbk2D4NCxfMCxYsiTDMADDFaHjOq1jNC9blE=.E2=.E2=.E2D0vqRjMadbkidgsiHAnolVOalhMwx0vqRjMadbk2D0vq1jNC9bmKH1no9jMCxYsiT3.2=.E2=.Ewx0O49cMqZbPKT3.2=.Ewx2MqxgNwI.E2=1kCVYu4heMidYtwI.E2=.E2=1kixbPq7eNw9ePC9YnAx9O4ZbNo9ePC9YnAx2uiRbEidgsiHAnoMe6wx0vqRjMadbkw9jMCxYsiT5N4EYu4RgMKdgswx0vq1jNC9blE=.E2=.E2D4u4BeuaT1mKRWtwH1noZbMiT1noPcMqfeNwI.E2=1no1cNCVfOa9eNCT3.2=.Ew1cNCVfOa9eNCT3.2=.E2=.Ew9jNqxWOaT0uanWtAnDGqVdNqR0uanWtAnDFCfbNo9ePC9YnAx48WDDEixbPq7eNwD0vq1jNC9bn8hUsqng9qBXOalWuKxbMwx0vq1jNC9blE=.E2=.E2D4u4BeuaT1m4HYu4bbkw7cMiVblED4u4BeuaT1nC9YuKRiNwAUkmI5EwxAsiHdNqtbkwx4u4BeuaT3.wPcMqfeNwDAsiHdNqtbkmX17ER1nonWtCZbPaT1noPcMqfeNwI1liVXOidbkwnWtCZbPaT17AAZ=oDDHC9YuKRiNwDDFiVXOidblED4u4BeuaT1nC9YuKRiNwAgkmI5EwxAsiHdNqtbkwx4u4BeuaT3.wPcMqfeNwDAsiHdNqtbkm917ER1nonWtCZbPaT1noPcMqfeNwI1liVXOidbkwnWtCZbPaT18gAZ=oDDHC9YuKRiNwDDFiVXOidblED4u4BeuaT1nC9YuKRiNwAakmI5EwxAsiHdNqtbkwx4u4BeuaT3.wPcMqfeNwDAsiHdNqtbkmv17ER1nonWtCZbPaT1noPcMqfeNwI1liVXOidbkwnWtCZbPaT16QAZ=oDDHC9YuKRiNwDDFiVXOidblED4u4BeuaT1nC9YuKRiNwAdkmI5EwxAsiHdNqtbkwx4u4BeuaT3.wx0O49cNwDDG4HYu4bbkwx4u4BeuaT3.2=.Ewx.u4HcOqdWuaHblE=.E2D.u4HcOqdWuaHblE=.E2=.E2D0vqRjMadbkidgsiHAnohcOKRbEidgsiHAnoHetqR0uanWtAnDFWcbEidgsiHAnoHetqydNq9eNCRcMqDDEixbPq7eNwD0vq1jNC9bmKX1no9jMCxYsiT3.2=.E2=.EwPcMqfeNwDDN4JYuaNbkwVBf06c6eUhcmn17ER9euT1noxYNKHeNaT1noPcMqfeNwI.E2=1no1cNCVfOa9eNCT3.wx.tCxgNwI3'

    fname=os.path.join(self.workdir, "test_930.xml")
    with open(fname,"wb") as f:
      f.write( pilot.FromBase64Swig(content_of_file) )

    SALOMERuntime.RuntimeSALOME_setRuntime()
    l=loader.YACSLoader()
    p=l.load(fname)
    self.assertTrue(p.getChildByName("test23/main").getChildByName("test23/run").getChildByName("test23/FE").getChildByName("test23/run_internal").getInputPort("i1").getPyObj() == 3)
    self.assertTrue(p.getChildByName("test23/main").getChildByName("test23/run").getChildByName("test23/FE").edGetSeqOfSamplesPort().getPyObj()==list(range(10)))
    os.remove(fname)
    pass

if __name__ == '__main__':
  dir_test = tempfile.mkdtemp(suffix=".yacstest")
  file_test = os.path.join(dir_test,"UnitTestsResult")
  with open(file_test, 'a') as f:
      f.write("  --- TEST src/yacsloader: testSaveLoadRun.py\n")
      suite = unittest.makeSuite(TestSaveLoadRun)
      result=unittest.TextTestRunner(f, descriptions=1, verbosity=1).run(suite)
  sys.exit(not result.wasSuccessful())
