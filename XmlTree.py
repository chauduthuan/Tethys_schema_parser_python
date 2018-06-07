# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 17:09:13 2018

@author: ThuanPC
"""

import xml.etree.ElementTree as ET
import json


class XmlTree:
    def __init__(self, file_name):
        self.file_name = file_name
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        self.schema = {}        #dictionary represents what we want, then convert it to json
        
        self.initialize_parent_map()
        self.initialize_namespace_map()
        self.breath_first_iteration()


    def initialize_parent_map(self):
        """create parent map as dictionary, key and value are Element """
        self.parent_map = {c:p for p in self.tree.iter() for c in p}
        
    def initialize_namespace_map(self):
        """create name space map as dictionary, key is uri, value is namespace """
        #self.namespace_map = {"http://www.w3.org/2001/XMLSchema":"xs"}
        namespaces = {}
        for event, elem in ET.iterparse(self.file_name, events=("start-ns","start")):
            if event =="start-ns":
                if elem[0] in namespaces and namespaces[elem[0]] != elem[1]:
                    raise KeyError("Duplicate prefix with different URI found.")
                #namespaces[str(elem[0])] = elem[1]
                namespaces["{" + str(elem[1]) ] = str(elem[0])
        self.namespace_map = namespaces
        print(self.namespace_map)


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
        """Return list of parent element of current node, first element in the list is root """
        parent_list = []
        parent = node
        while True:
            parent = self.get_node_parent(parent)
            if parent is None:
                break
            parent_list.append(parent)
     
        parent_list.reverse()
        return parent_list
    
    def get_parent_name_list(self, parent_list):
        """Return parent name list of current node from parent list"""
        #NEED to check not only using name attributes in schema but element tag
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

        tag = self.get_node_tag(node)
        attributes = node.attrib
        name = ""
        if "name" in attributes:
            name = attributes["name"]
           
        if ((tag == "xs:element") and (name!="")):
            print(tag)
            print(name)
            
            self.print_parent_name_list(parent_name_list)
            # do stuff
            schema_node = {}
            schema_node["name"] = name
            schema_node["children"] = {}
            
            
        #NEED to know what to add to schema
        
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
    
    def get_node_tag(self, node):
        """
        node.tag contains {uri}type such as {http://www.w3.org/2001/XMLSchema}element, not xs:element, xs:schema
        Return xs:element or xs:schema as string
        """
        tag = node.tag      #{http://www.w3.org/2001/XMLSchema}element
        ns = tag.split("}") #ns[0] = {uri and ns[1] = element
        tag = self.namespace_map[ns[0]] + ":" + ns[1] #xs:element
        return tag
        
        
    
    
if __name__ == '__main__':
    print("*****Start*****")
    file_name = 'Deployment.xsd'
    xmlTree = XmlTree(file_name)
    
    
    print("*****End*****")