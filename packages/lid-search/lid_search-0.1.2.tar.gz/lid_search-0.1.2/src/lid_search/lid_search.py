from pathlib import Path
import json
from rich import print
import sqlite3
from semantic_version_tools import Vers 
from shutil import rmtree
from importlib.metadata import version

__version__=version('lid_search')

class LidDB:
    
    def __init__(self,jFile:Path,temporary_folder:Path=Path('tmp'),cache:bool=False):
        if isinstance(jFile,str):
            jFile=Path(jFile)
        if isinstance(temporary_folder,str):
            temporary_folder=Path(temporary_folder)
        if not temporary_folder.exists():
            temporary_folder.mkdir()
        
        self.temporary_folder=temporary_folder
        self.db=sqlite3.connect(temporary_folder.joinpath('db.sqlite'))
        self.cursor=self.db.cursor()
        if not cache:
            jdata = json.loads(jFile.read_text())
            self.cursor.execute('CREATE TABLE data (id INTEGER PRIMARY KEY, lid TEXT, version Text)')
            for i in jdata['summary']:
                self.cursor.execute('INSERT INTO data (lid, version) VALUES (?,?)', (i['logicalIdentifier'], i['versionId']))
            self.db.commit()
            
    def search(self,lid:str):
        self.cursor.execute('SELECT * FROM data WHERE lid=?', (lid,))
        result=self.cursor.fetchall()
        if len(result)==0:
            ret=None
        else:
            # print(len(result))
            ret=result[0][2]
        return ret
    
    def close(self,preserve:bool=False):
        self.db.close()
        if not preserve:
            rmtree(self.temporary_folder,)

def lid_builder(filename:Path,collection:str=None,instrument:str='simbio-sys',mission:str='bc_mpo'):
    if collection is None:
        parts=filename.stem.split('_')
        if parts[2] =='sc':
            if parts[1]=='raw':
                collection='data_raw'
            else:
                collection='data_calibrated'
    
    return f"urn:esa:psa:{mission}_{instrument}:{collection}:{filename.stem}"