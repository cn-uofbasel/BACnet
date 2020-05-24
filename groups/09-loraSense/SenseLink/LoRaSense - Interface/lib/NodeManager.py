from lib.Manager import Manager


class NodeManager(Manager):

    def __init__(self, nodes):
        super().__init__(nodes)

    def getBySensorType(self, sensorType):
        nodeList = {}
        for node in self.getAll().values():
            if node.hasSensorType(sensorType):
                nodeList[node.id] = node
        return nodeList
