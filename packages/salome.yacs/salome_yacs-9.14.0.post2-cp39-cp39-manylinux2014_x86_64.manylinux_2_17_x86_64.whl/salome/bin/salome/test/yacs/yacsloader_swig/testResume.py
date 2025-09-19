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

import time
import unittest
import threading
import tempfile
import os

from salome.yacs import SALOMERuntime
from salome.yacs import loader
from salome.yacs import pilot
from salome.kernel import salome

class TestResume(unittest.TestCase):

    def setUp(self):
        SALOMERuntime.RuntimeSALOME_setRuntime(1)
        self.l = loader.YACSLoader()
        self.e = pilot.ExecutorSwig()
        self.p = self.l.load("samples/bloc2.xml")
        workdir = tempfile.mkdtemp(suffix=".yacstest")
        self.statefile = os.path.join(workdir, 'dumpPartialBloc2.xml')
        pass

    def tearDown(self):
      salome.salome_init()
      cm = salome.lcc.getContainerManager()
      cm.ShutdownContainers()
      pass

    def test1_PartialExec(self):
        # --- stop execution after breakpoint
        time.sleep(1)

        print("================= Start of PARTIALEXEC ===================")
        brp=['b1.b2.node1']
        self.e.setListOfBreakPoints(brp)
        self.e.setExecMode(2) # YACS::STOPBEFORENODES
        #self.e.displayDot(self.p)
        run1 = threading.Thread(None, self.e.RunPy, "breakpoint", (self.p,0))
        run1.start()
        time.sleep(0.1)
        self.e.waitPause()
        #self.e.displayDot(self.p)
        self.e.saveState(self.statefile)
        #self.e.displayDot(self.p)
        self.e.stopExecution()
        #self.e.displayDot(self.p)
        self.assertEqual(101, self.p.getChildByName('b1.b2.node1').getEffectiveState())
        self.assertEqual(106, self.p.getChildByName('b1.node1').getEffectiveState())
        print("================= reach BREAKPOINT PARTIAL EXEC ==========")

        # --- reload state from previous partial execution then exec
        time.sleep(1)

        print("================= Start of EXECLOADEDSTATE ===============")
        sp = loader.stateParser()
        sl = loader.stateLoader(sp,self.p)
        sl.parse(self.statefile)
        #self.e.displayDot(self.p)
        self.e.setExecMode(0) # YACS::CONTINUE
        run2 = threading.Thread(None, self.e.RunPy, "loadState", (self.p,0,True,True))
        run2.start()
        time.sleep(0.1)
        self.e.waitPause()
        #self.e.displayDot(self.p)
        run2.join()
        self.assertEqual(106, self.p.getChildByName('node1').getEffectiveState())
        self.assertEqual(106, self.p.getChildByName('node2').getEffectiveState())
        self.assertEqual(106, self.p.getChildByName('b1.node1').getEffectiveState())
        self.assertEqual(106, self.p.getChildByName('b1.node2').getEffectiveState())
        self.assertEqual(106, self.p.getChildByName('b1.b2.node1').getEffectiveState())
        self.assertEqual(106, self.p.getChildByName('b1.b2.node2').getEffectiveState())
        self.assertEqual(106, self.p.getChildByName('b1.b2.loop1.node1').getEffectiveState())
        print("================= End of EXECLOADEDSTATE =================")
                          
    pass

if __name__ == '__main__':
  dir_test = tempfile.mkdtemp(suffix=".yacstest")
  file_test = os.path.join(dir_test,"UnitTestsResult")
  with open(file_test, 'a') as f:
      f.write("  --- TEST src/yacsloader: testResume.py\n")
      suite = unittest.makeSuite(TestResume)
      result=unittest.TextTestRunner(f, descriptions=1, verbosity=1).run(suite)
  sys.exit(not result.wasSuccessful())
