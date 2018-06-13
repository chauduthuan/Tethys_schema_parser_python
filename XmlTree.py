# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 17:09:13 2018

@author: ThuanPC
"""

import xml.etree.ElementTree as ET
from collections import defaultdict
import json
import xml.dom.minidom as minidom
import copy



class XmlTree:
    def __init__(self, file_name):
        self.file_name = file_name
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        
        #self.schema = []        #dictionary array represents what we want, then convert it to json
        self.schema = defaultdict(dict)
        self.schema["name"] = self.file_name
        self.schema["children"] = []
        self.schema_root = self.schema["children"]
        self.initialize_namespace_map()
        
        #SOME NOTE
        #before createing schema, look up all dependencies such as base, ref or xs:include
        #add dependencies to a dictionary
        #modify tree by adding these dependencies
        self.dependencies = {} #dictionary for dependencies, key is name, value is element tree        
        self.initialize_dependencies_and_patch_tree()
        
        self.initialize_parent_map()
        self.breath_first_iteration()


    def initialize_parent_map(self):
        """create parent map as dictionary, key and value are Element """
        self.parent_map = {c:p for p in self.tree.iter() for c in p}
        
    def initialize_namespace_map(self):
        """create name space map as dictionary, key is {uri, value is namespace 
        so when split node tag with delimeter }, first item is {uri and second item is ns
        """
        #self.namespace_map = {"http://www.w3.org/2001/XMLSchema":"xs"}
        namespaces = {}
        for event, elem in ET.iterparse(self.file_name, events=("start-ns","start")):
            if event =="start-ns":
                #if elem[0] in namespaces and namespaces[elem[0]] != elem[1]:
                #    raise KeyError("Duplicate prefix with different URI found.")
                #namespaces[str(elem[0])] = elem[1]
                if elem[1] in namespaces and namespaces[elem[1]] != elem[0]:
                    raise KeyError("Duplicate prefix with different URI found.")                
                namespaces["{" + elem[1] ] = elem[0]
        self.namespace_map = namespaces
        print(self.namespace_map)
        
    def initialize_dependencies_and_patch_tree(self):
        """create dependencies dictionary which key is name and key is elementree
        example: "Deployment":element 
        then patch all missing element in tree, for example, xs:extension 
        """
        ##append dependencies
        #append denendencies in xs:include
        file_names = self.get_included_dependencies_names()
        for file_name in file_names:
            xmlTree = XmlTree(file_name)
            included_dependencies = xmlTree.get_dependencies()
            for key in included_dependencies:
                #probably need to check for duplicate keys
                self.dependencies[key] = included_dependencies[key]
        
        #append dependencies in current file
        for node in self.root.getchildren():
            tag = self.get_node_tag(node)
            attributes = node.attrib
            if "name" in attributes:
                name = attributes["name"]
                self.dependencies[name] = node
            
        #patch tree
        print("FINDING NODES NEED PATCH")
        nodes_need_patch = self.find_node_need_patches()
        for node in nodes_need_patch:
            print(self.get_node_tag(node))
            name = self.get_base_or_ref(node)
            patch = self.dependencies[name]
            self.patch_node(node, patch)
            #print("base = " + name)
            #node.insert(0, self.dependencies[name])
        
    def find_node_need_patches(self):
        """Iterate through tree, append node that is needed to patch up
        return list of nodes/element 
        """
        nodes_need_patch = []
        for node in self.root.getiterator():
            if self.is_node_needed_to_be_patched(node):
                nodes_need_patch.append(node)
        return nodes_need_patch
    
    def is_node_needed_to_be_patched(self, node):
        """check if node needs to be patched
        return true if node is xs:extension or has attribute base
        """
        #tag = self.get_node_tag(node)
        attributes = node.attrib
        if ("ref" in attributes):
            ref = attributes["ref"]
            if not self.is_xs_reference(ref):
                return True
        elif ("base" in attributes):
            base = attributes["base"]
            if not self.is_xs_reference(base):
                return True
        return False
    
    def patch_node(self, node, patch):
        """add all children and attributes or patch to node """
        attributes = patch.attrib
        for key in attributes:
            if key!="name":
                node.attrib[key] = attributes[key]
        index = 0
        for child in patch.getchildren():
            new_child = copy.deepcopy(child)
            node.insert(index, new_child)
            index += 1
        
    def is_xs_reference(self, ref):
        """check if reference is xs type such as xs:string """
        xs = ref[0:2]
        return xs=="xs"
    
    def get_base_or_ref(self, node):
        attributes = node.attrib
        name = ""
        if ("ref" in attributes):
             name = attributes["ref"]
        elif ("base" in attributes):
            name = attributes["base"]
        return name
    
    def get_dependencies(self):
        """return dictionary of dependencies"""
        return self.dependencies
    
    def get_included_dependencies_names(self):
        """return list of file_name in xs:include 
        <xs:include schemaLocation="CommonElements.xsd"/>
        """
        dependencies_names = []
        for node in self.root.getchildren():
            tag = self.get_node_tag(node)
            if tag == "xs:include":
                attributes = node.attrib
                schema_location = attributes["schemaLocation"]
                dependencies_names.append(schema_location)
        return dependencies_names


    def get_node_parent(self, node):
        """Return parent element of a node """
        if node in self.parent_map:
            return self.parent_map[node]
        else:
            return None
        
    def is_root(self, node):
        """check if a node is root element """
        return node == self.root
    
    def breath_first_iteration(self):
        """Iterate throuth tree and create schema as json"""
        queue = []
        queue.append(self.root)
        
        while (len(queue) != 0):
            node = queue.pop(0)
            for child in node.getchildren():
                queue.append(child)
            self.add_node_to_schema(node)
        #NEED to convert schema to json
                    
    def get_parent_list(self, node):
        """Return list of parent element of current node, first element in the list is root which is xs:schema"""
        parent_list = []
        parent = node
        while True:
            parent = self.get_node_parent(parent)
            if parent is None:
                break
            parent_list.append(parent)
        #reverse the list to have the order correctly, first element is root
        parent_list.reverse()
        return parent_list
    
    def get_parent_name_list(self, parent_list):
        """Return parent name list of current node from parent list"""
        #NEED to check not only using name attributes in schema but maybe using element tag 
        #NEED to consider xs:schema
        name_list = []
        for parent in parent_list:
            attributes = parent.attrib
            if "name" in attributes:
                name = attributes["name"]
                name_list.append(name)
        return name_list
        
    
    def add_node_to_schema(self, node):
        """Add current node to dictionary schema """
        #print(node.tag)
        parent_list = self.get_parent_list(node)
        #self.print_parent_list(parent_list)
        
        parent_name_list = self.get_parent_name_list(parent_list)
        
        #extract information of a node
        tag = self.get_node_tag(node)
        attributes = node.attrib
        name = ""
        if "name" in attributes:
            name = attributes["name"]

        #NEED to know what to add to schema
        #NEED to ADD root to schema, root can have multiple childs and root is xs:schema
        #if (((tag == "xs:element") or (tag == "xs:complexType"))and (name!="")):
        if (name != ""):
            #self.print_tag_and_name_of_node(node)
            #self.print_parent_name_list(parent_name_list)
            
            # do stuff such as adding node to schema
            schema_node = defaultdict(dict)
            schema_node["name"] = name
            schema_node["children"] = []
            
            #find a location in schema to add node
            if (len(parent_name_list) == 0): #no parents
                self.schema_root.append(schema_node)
            else:
                #search to correct location in schema
                location = self.schema_root 
                #print(location)
                for i in range(len(parent_name_list)):
                    parent = parent_name_list[i]
                    for j in range(len(location)):
                        if(location[j]['name'] == parent):
                            location = location[j]["children"]
                            break
                location.append(schema_node)
                    
                    
                
            
            
    def print_parent_list(self, parent_list):
        print("---parent list---")
        for parent in parent_list:
            print(self.get_tag_type(parent.tag))
        print("=============")
        
    def print_parent_name_list(self, parent_name_list):
        print("--- parent name list---")
        for name in parent_name_list:
            print(name)
        print("=============")
        
    def print_tag_and_name_of_node(self, node):
        tag = self.get_node_tag(node)
        attributes = node.attrib
        name = ""
        if "name" in attributes:
            name = attributes["name"]

            print("tag = " + tag)
            print("name = " + name)
        
    def get_node_tag(self, node):
        """
        node.tag contains {uri}type such as {http://www.w3.org/2001/XMLSchema}element, not xs:element, xs:schema
        Return xs:element or xs:schema as string
        """
        tag = node.tag      #{http://www.w3.org/2001/XMLSchema}element
        ns = tag.split("}") #ns[0] = {uri and ns[1] = element
        tag = self.namespace_map[ns[0]] + ":" + ns[1] #xs:element
        return tag
        
    def get_schema(self):
        return self.schema
        
    def get_root(self):
        return self.root
    
    
if __name__ == '__main__':
    print("*****Start*****")
    file_name = 'Deployment.xsd'
    xmlTree = XmlTree(file_name)
    #xmlTree.breath_first_iteration()
    schema = xmlTree.get_schema()
    schema = json.dumps(schema, indent=4)
    #print(schema)
    
    dependencies_names = xmlTree.get_included_dependencies_names()
    print(dependencies_names)
    
    dependencies = xmlTree.get_dependencies()
    for key in dependencies:
        print(key)
        
    root = xmlTree.get_root()
    print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
    print("Checking unknownSensor node")
    nodes = root.findall(".//*[@name='unknownSensor']")
    for node in nodes:
#        for child in node.getiterator():
#            if "name" in child.attrib:
#                print(child.attrib["name"])
        print(minidom.parseString(ET.tostring(node)).toprettyxml(indent="   "))

    
    print("*****End*****")