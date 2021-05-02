
import os.path
import sys

dirname = os.path.abspath(os.path.dirname(__file__))
folderG4 = os.path.join(dirname, '../../../20-fs-ias-lec/groups/04-logMerge/')
sys.path.append(folderG4)

import EventCreationTool
ecf = EventCreationTool.EventFactory()