from Manager import Manager
from Node import Node


class NodeManager(Manager):

    def __init__(self, nodes, callbackNodeAdded=None):
        super().__init__(nodes)
        self.__callbackNodeAdded = callbackNodeAdded

    def setCallbackNodeAdded(self, callbackNodeAdded):
        self.__callbackNodeAdded = callbackNodeAdded

    def getBySensorType(self, sensorType):
        nodeList = {}
        for node in self.getAll().values():
            if node.hasSensorType(sensorType):
                nodeList[node.id] = node
        return nodeList

    def addId(self, nodeId):
        if self.containsId(nodeId):
            return
        node = Node(nodeId)
        self.add(node)
        if self.__callbackNodeAdded is not None:
            self.__callbackNodeAdded(node)
