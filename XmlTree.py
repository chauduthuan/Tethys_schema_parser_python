# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 17:09:13 2018

@author: ThuanPC
"""

import xml.etree.ElementTree as ET
import json

class XmlTree:
    def __init__(self, file_name):
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        self.schema = {}        #dictionary represents what we want, then convert it to json
        
        self.initialize_parent_map()
        self.breath_first_iteration()


    def initialize_parent_map(self):
        """create parent map as dictionary, key and value are Element """
        self.parent_map = {c:p for p in self.tree.iter() for c in p}

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
        attributes = node.attrib
        name = ""
        if "name" in attributes:
            name = attributes["name"]
        if name != "":
            print(name)
            self.print_parent_name_list(parent_name_list)
        
        schema_node = {}
        #NEED to know what to add to schema
        
    def print_parent_list(self, parent_list):
        print("---parent list---")
        for parent in parent_list:
            print(parent.tag)
        print("=============")
        
    def print_parent_name_list(self, parent_name_list):
        print("--- parent name list---")
        for name in parent_name_list:
            print(name)
        print("=============")
        
    
    
if __name__ == '__main__':
    print("*****Start*****")
    file_name = 'Deployment.xsd'
    xmlTree = XmlTree(file_name)
    
    print("*****End*****")