'''
Created on Aug 15, 2025

@author: ahypki
'''
from net.hypki.apiutils import streamGET, streamPOST
from beans.PlainConnector import PlainConnector
from io import StringIO

class BeansTable:
    '''
    classdocs
    '''
    __token = None
    
    __dsQuery = None
    __tbQuery = None
    
    __in_iter = None
    
    __out_file = None    

    def __init__(self, token, dsQuery, tbQuery):
        '''
        Constructor
        '''
        self.__token = token
        self.__dsQuery = dsQuery
        self.__tbQuery = tbQuery
        
    def close(self):
        if self.__out_file is not None:
            self.__out_file.close()
        # TODO conf
        streamPOST("http://localhost:25000/api/file/upload",
                       self.__tbQuery,
                       {"token": self.__token, 
                        "datasetId" : self.__dsQuery,
                        "tableName" : self.__tbQuery})
        
    def __iter__(self):
        if self.__in_iter == None:
            # TODO conf
            self.__in_iter = PlainConnector(streamGET("http://localhost:25000/api/table/data", 
                                    {"token": self.__token, 
                                     "dsQuery": self.__dsQuery, 
                                     "tbQuery": self.__tbQuery, 
                                     "tableId": self.__tbQuery}))
        return self
    
    def __next__(self):
        return next(self.__in_iter)
    
    def write(self, line):
        if self.__out_file == None:
            self.__out_file = open(self.__tbQuery, 'w', encoding = 'UTF8')
            
        self.__out_file.write(line)
        