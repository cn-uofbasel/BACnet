import sys,os

sys.path.append(os.path.join(os.path.dirname(__file__), '...', '20-fs-ias-lec/groups/13-sneakernet/code/logMerge'))
print(os.path.join(os.path.dirname(__file__), '../../..', '20-fs-ias-lec/groups/13-sneakernet/code/logMerge'))


from feedCtrl import ui

ui.run()

