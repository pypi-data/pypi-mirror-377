import rich_click as click
from pathlib import Path
from lid_search.lid_search import LidDB,lid_builder
from semantic_version_tools import Vers
from xml.dom.minidom import parse


def getFromXml(xml, label, idx=0):
    a = xml.getElementsByTagName(label)[idx]
    return a.firstChild.nodeValue

def get_lid(filename:Path)->str:
    tree = parse(filename.__str__())
    lid=getFromXml(tree, 'logical_identifier')
    return lid

@click.group()
def main():
    pass

@main.command
@click.argument("filename", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path))
@click.option(
    "-d",
    "--database",
    type=click.Path(
        exists=False, file_okay=True, dir_okay=False, readable=True, path_type=Path
    ),
    help="Path and name of the database file",
)
@click.option('-p','--preserve', is_flag=True, help="Preserve the database file",default=False)
@click.option('-c','--cache', is_flag=True, help="Use the cache file",default=False)
def search(filename:Path,database:Path,preserve:bool,cache:bool):
    """Get the current version of the lid"""
    lid=get_lid(filename)
    # print(lid)
    
    db=LidDB(database,cache=cache)
        
    dat=db.search(lid)    
    if dat:
        v=Vers(dat)
    print(f"Current version: {v.short()}, Next Version {v+1}")
    
    db.close(preserve)
    
@main.command
@click.argument("filename", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path))
def getlid(filename:Path):
    """Extract the LID from the XML file"""
    # lid=lid_builder(filename)
    # print(lid)
    lid2=get_lid(filename)
    print(lid2)