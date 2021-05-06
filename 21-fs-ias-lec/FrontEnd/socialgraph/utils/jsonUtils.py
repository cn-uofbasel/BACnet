import json


def extract_connections(data, id):

    nodes = data['nodes']
    links = data['links']

    connections = []

    for x in range(len(links)):
        s = links[x]['source']
        t = links[x]['target']

        if not any(s in q.values() for q in connections):
            connections.append({"source": s, "target": [t]})

        for y in range(len(connections)):
            d = connections[y]
            if d['source'] == s:
                if t not in d['target']:
                    d['target'].append(t)

    json = createJSON(connections, nodes, id)

    return json


def createJSON(connections, nodes, id):

    j = {}
    n = []
    l = []

    found = False

    for e in connections:
        if e.get('source') == int(id):
            found = True
            for x in nodes:
                if x.get('id') == e.get('source') and x not in n:
                    n.append(x)
                    break
            for t in e.get('target'):
                for x in nodes:
                    if x.get('id') == t and x not in n:
                        n.append(x)
                        break
                l.append({'source': e.get('source'), 'target': t})

    if not found:
        for x in nodes:
            if x.get('id') == int(id):
                n.append(x)
                break

    j.update({'nodes': n})
    j.update({'links': l})

    return json.dumps(j)

