'''
Created on Aug 13, 2025

@author: ahypki
'''
from net.hypki.Logger import Logger
from net.hypki.io import isDouble
from net.hypki.regex import isLong

class PlainConnector:
    '''
    classdocs
    '''

    __path = None
    __stream = None
    
    # iterator from a file/stream
    __iter_file = None
    __iter_header_read = False
    __iter_line = None
    __iter_line_dict = None
    __iter_types_autodetermined = False
    
    __cache_header_line = None
    __cache_header_names = None
    __cache_types = []

    def __init__(self, pathOrStream):
        '''
        Constructor
        '''
        if isinstance(pathOrStream, str):
            self.__path = pathOrStream
        else:
            self.__stream = pathOrStream
            
    def __isStream(self):
        return self.__stream is not None
    
    def __isPath(self):
        return self.__path is not None
        
    def __parse_header(self):
        if self.__cache_header_line is not None:
            s = self.__cache_header_line.strip()[1:] # removing leading hash
            namesWithBrackets = s.split()
            self.__cache_header_names = []
            for nameWithBracket in namesWithBrackets:
                self.__cache_header_names.append(nameWithBracket[:(nameWithBracket.rfind('('))])
        pass
        
    def printSummary(self):
        if self.__isPath():
            Logger.info("BeansTable, reading from file: " + self.__path)
        elif self.__isStream():
            Logger.info("BeansTable, reading from stream")
        # Logger.info("Header: " + self.__cache_header_names)
        
    def __iter__(self):
        if self.__isPath():
            if self.__iter_file == None:
                self.__iter_file = open(self.__path)
        elif self.__isStream():
            # do nothing, actually
            pass
        else:
            Logger.error("Unimplemented case")
        return self
    
    def __next__(self):
        if self.__isPath():
            self.__iter_line = next(self.__iter_file)
        else:
            self.__iter_line = next(self.__stream).decode('utf-8')
        
        # reading next line
        if not self.__iter_header_read:
            if self.__iter_line.startswith('#'):
                self.__iter_header_read = True
                
                # Logger.debug("header" + self.__iter_line)
                self.__cache_header_line = self.__iter_line
                self.__parse_header()
                
                # reading next line with the data
                if self.__isPath():
                    self.__iter_line = next(self.__iter_file)
                else:
                    self.__iter_line = next(self.__stream).decode('utf-8')
        
        columns = self.__iter_line.split();
        __iter_line_dict = {}
        for i in range(len(columns)):
            # determining the types (once)
            if not self.__iter_types_autodetermined:
                if isDouble(columns[i]):
                    __iter_line_dict[self.__cache_header_names[i]] = float(columns[i])
                    self.__cache_types.append(1)
                elif isLong(columns[i]):
                    __iter_line_dict[self.__cache_header_names[i]] = int(columns[i])
                    self.__cache_types.append(2)
                else:
                    __iter_line_dict[self.__cache_header_names[i]] = columns[i]
                    self.__cache_types.append(3)
            else:
                if self.__cache_types[i] == 1:
                    __iter_line_dict[self.__cache_header_names[i]] = float(columns[i])
                elif self.__cache_types[i] == 2:
                    __iter_line_dict[self.__cache_header_names[i]] = int(columns[i])
                else:
                    __iter_line_dict[self.__cache_header_names[i]] = columns[i]
        
        self.__iter_types_autodetermined = True
            
        return __iter_line_dict
        
        
        