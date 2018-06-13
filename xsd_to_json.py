import xml.etree.ElementTree as ET
import json
from XmlTree import XmlTree
import xml.dom.minidom as minidom


file_name = "ex2.xsd"
#file_name = "sampleXSD.xsd"
#file_name = "Deployment.xsd"

tree = ET.parse(file_name)

root = tree.getroot()
print(root.tag)
print(root.attrib)

children = root.getchildren()
child = children[0]

print(child.tag)
print(child.attrib)


""" Breath first search Iteration
iterate through entire document, keep track of current node and its parents
seems cannot keep track of parents
"""
# queue = []
# queue.append(root)

# while (queue.length() != 0): #queue is not empty
# 	cur_node = queue.pop()
	
# 	parents_list.append(cur_node)
# 	for child in cur_node:
# 		queue.append(child)

	
""" Depth first search Iteration """
#parent_map = parent_map = {c:p for p in tree.iter() for c in p}

#for c in tree.iter():
#    if c == root:
#        continue
#    print(c.tag)
#    p = parent_map[c]
#    print(p.tag)
#    print("====================")
#    
#js = {"a":{"b":"c"}}
#print(js)
#

dependencies = {}
for node in root.getchildren():
    #tag = get_node_tag(node)
    attributes = node.attrib
    if "name" in attributes:
        name = attributes["name"]
        dependencies[name] = node    
        
for key in dependencies:
    print(key)

def node_contains_ref(node):
    attributes = node.attrib
    

node_need_to_patch = []
for node in root.getiterator():
    attributes = node.attrib
    if "ref" in attributes:
        node_need_to_patch.append(node)

dependencies = {}
for node in root.getchildren():
    attributes = node.attrib
    if "name" in attributes:
        name = attributes["name"]
        dependencies[name] = node
        
for node in node_need_to_patch:
    attrib = node.attrib
    name = attrib["ref"]
    node.insert(0, dependencies[name])
    
#for node in node_need_to_patch:
#    print("ref " + node.attrib["ref"])
#    for child in node.getchildren():
#        print("--->" + child.tag)
#        print("--->" + child.attrib["name"])

xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
for node in root.getiterator():
    print(minidom.parseString(ET.tostring(node)).toprettyxml(indent="   "))
    print("====================================================")
    
    
    
    
    
    