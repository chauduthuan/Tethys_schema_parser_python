import xml.etree.ElementTree as ET
import json
from XmlTree import XmlTree

file_name = "book.xml"
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
parent_map = parent_map = {c:p for p in tree.iter() for c in p}

for c in tree.iter():
    if c == root:
        continue
    print(c.tag)
    p = parent_map[c]
    print(p.tag)
    print("====================")
    
js = {"a":{"b":"c"}}
print(js)
    
    
    
    
    
    
    
    
    
    
    
    