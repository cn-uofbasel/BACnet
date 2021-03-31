import pathlib
import ntpath
import hash_

def _file_to_json(syspath):
    systemname = str(ntpath.basename(syspath))
    print(systemname)
    data = []
    jsondata = {}
    pathlist = pathlib.Path(syspath).glob('**/*.*')
    for path in pathlist:
        dict = {}
        dict['name'] = str(ntpath.basename(path))
        dict['fullpath'] = systemname + str(path).replace(syspath, "").replace(str(ntpath.basename(path)), "")
        dict['hash'] = hash_.get_hash(path)
        data.append(dict)
    jsondata["{}".format(syspath)] = data
    return jsondata
