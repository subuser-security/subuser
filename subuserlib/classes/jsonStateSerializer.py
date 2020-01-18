# -*- coding: utf-8 -*-
# pylint: disable=no-init,old-style-class

"""
This code helps you serialize, in an organized fashion, your json states for debugging purposes.
"""

#external imports
import os,sys
#internal imports
#import ...

class Renderer():
  def __init__(self,serialize_base_dir=None):
    self.serialize_base_dir = serialize_base_dir
    if not os.path.exists(self.serialize_base_dir):
      sys.exit("Serialization base dir "+self.serialize_base_dir+" does not exist. Exiting...")
    os.path.join(self.serialize_base_dir,"json-states",todays_date)
          "by-index" -> self.by_index_dir
          "by-id" -> self.by_id_dir
    
    self.serialize_dir = os.path.join(self.serialize_base_dir,"json_states")
    self.this_runs_serialize_dir = os.path.join(self.serialize_base_dir,
    try:
      os.mkdir(

  def render(self,generateTree):
    import subprocess
    graph = "digraph {"
    tree = generateTree()
    for 
    graph += "}"
    p = Popen(['dot', '-Tx11'], stdin=PIPE)    
    p.communicate(input=graph.encode("utf-8"))

class MockRenderer():
  def __init__(self,serialize_base_dir=None):
    pass

  def render(self,generateDotFile):
    pass

dir_env_var = "JSON_STATE_SERIALIZE_BASE_DIR"
if dir_env_var in os.environ:
  renderer = Renderer(serialize_base_dir = os.environ[dir_env_var])
else:
  renderer = MockRenderer()
