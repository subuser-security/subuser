import subuserlib.classes.user
import subuserlib.classes.gitRepository
import subuserlib.classes.fileStructure
import os
u = subuserlib.classes.user.User()
g = subuserlib.classes.gitRepository.GitRepository(u,os.path.expanduser("~/.subuser/repositories/default/"))
fs = subuserlib.classes.fileStructure.BasicFileStructure(os.path.expanduser("~/.subuser/repositories/default"))
fsac = g.getFileStructureAtCommit("latest")
