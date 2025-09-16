'''
Created on Jul 10, 2025

@author: ahypki
'''
import os
import importlib.metadata

from rich.console import Console
from rich.markdown import Markdown
from rich import print

def version():
    try:
        __version__ = importlib.metadata.version("beans-cli")
        return str(__version__)
    except Exception as e:
        return ""

def printUsage():
    this_dir, this_filename = os.path.split(__file__)
    myfile = os.path.join(this_dir, 'usage.md') 
    file = open(myfile)
    s = file.read()
    
    s = s.replace('VERSION', 'version `' + version() + '`')

    console = Console()
    renderable_markup = Markdown(s)
#    Logger.logInfo(s, printLogLevel = False, printNewLine = False)
#    print(renderable_markup)
    console.print(renderable_markup)
#    console.print("Where there is a [bold cyan]Will[/bold cyan] there [u]is[/u] a [i]way[/i].")
    


def main():
    printUsage()
    
if __name__ == '__main__':
    main()