

class NodeManager:

    def __init__(self):
        self.__nodes = {}

    def __isValidNodeId(self, id):
        return id is not None and id in self.__nodes

    def __isValidNode(self, node):
        return node is not None and node.id in self.__nodes

    def loadNodes(self, nodeFile):
        return

    def node(self, id):
        if self.__isValidNodeId(id):
            return self.__nodes[id]

    def setNode(self, node):
        if self.__isValidNode(node):
            self.__nodes[node.id] = node

    def delNode(self, id):
        if self.__isValidNodeId(id):
            del self.__nodes[id]

    def forAll(self, func, **kwargs):
        if func is not None:
            for node in self.__nodes:
                func(node, kwargs)

