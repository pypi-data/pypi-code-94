# -*- coding: utf-8 -*-
# Copyright © kakkarja (K A K)

import datetime
import os
import re
from .dbase import Datab as db
from itertools import islice
from typing import Union
from types import GeneratorType
import locale
from collections.abc import Iterator
from .tvdescript import Parent, ChildsNum, FileName, Gtv

def conftv(cls, childs = None, space = None):
    """Configure Childs with spaces limited from 1 to 10"""
    if space and space <= 10:
        cls.childs = ChildsNum(childs, space)
    else:
        raise ValueError('Space is exceeding the limitation! (1 to 10 only)')
    return cls

class TreeView:
    """
    This is a class of writing in txt file in treeview/outline mode.
    The beginning of creating TreeView text file, you need to start with-
    TreeView.writetree() to create parent at the beginning.
    The rest you must use other functions, to edit, add child and parent.
    WARNING: Do not use anymore writetree function, after the initial start-
    of making TreeView text file. Because it will erase everything in the text file.
    """
    
    __slots__ = '__weakref__', 'ndat', 'nchi'
    filename = FileName()
    childs = ChildsNum(50, 4)
    parent = Parent()
    loc = locale.getdefaultlocale()[1]
    
    def __init__(self, filename):
        """
        The default is 4 spaces
        The default is 50 childs
        """

        self.filename = filename
        self.parent = self.parent 
        self.childs = self.childs

    
    def __len__(self):
        """Len of childs"""

        return len(tuple(self.childs))
            
    def __enter__(self):
        """Context manager created."""
        
        return self
    
    def __exit__(self, type_, value, trace):
        """ When exit, all TreeView class properties is cleared."""
        
        if TreeView.filename.store1:
            TreeView.filename.finalize(self.__weakref__)
        return False
        
    def getdata(self) -> GeneratorType:
        """Get file datas"""
        
        if os.path.exists(f'{self.filename}.txt'):
            with open(f'{self.filename}.txt') as rd:
                yield from enumerate(rd)
        else:
            raise FileNotFoundError(f'{self.filename}.txt not exist!')
    
    def getdatanum(self) -> int:
        """Len of data"""
        
        return tuple(self.getdata())[-1][0]+1
        
    def filop(self, data: Union[str, list, GeneratorType, Iterator], mode: int = 0) -> None:
        """The file open function/method either for read or write."""
        
        try:
            if not mode:
                if isinstance(data, (GeneratorType, Iterator)):
                    with open(f'{self.filename}.txt', 'w') as wr:
                        for d in data:
                            wr.write(d)
                elif isinstance(data, str):
                    with open(f'{self.filename}.txt', 'w') as wr:
                        wr.write(data)
                else:
                    raise TypeError('Must be str/list/generator/iterator!')
            elif mode == 1:
                if isinstance(data, str):
                    with open(f'{self.filename}.txt', 'a') as wr:
                        wr.write(data)
                else:
                    raise TypeError('Must be a string!')
            else:
                raise ValueError('Mode must be an integer and the value is 0 or 1')                
        except Exception as e:
            raise e
        finally:
            del data
    
    def getchild(self, child: str) -> Union[tuple, None]:
        """Getting child position."""
        
        if child[:5] == 'child' and child[5:].isnumeric():
            idx = int(child[5:])-1 if int(child[5:]) and int(child[5:])-1 < len(self)  else None
            if idx is not None:
                return tuple(islice(self.childs, idx, idx + 1))[0][1]
            else:
                return idx

    def writetree(self, words: str) -> None:
        """
        This is initial start for creating Treeview with a parent.
        WARNING: After the initial, do not use this function anymore,
        otherwise, it can override the whole txt file like it is new. 
        """
        try:
            if isinstance(words, str):
                self.filop(f'{words}:\n')
            else:
                raise TypeError('Need to be string!')
        except TypeError as e:
            raise e
                
    def gspc(self, insider: bool = False):
        """Finding spaces that set originally or default"""
        
        if insider:
            try:
                pos = None
                for _, lsp in self.getdata():
                    if lsp != '\n' and lsp[-2] != ':':
                        pos = re.match(r'\s+', lsp).span()[1]
                        if (pos:= [p for p in range(1,11) if p % pos == 0]):
                            return pos[0]
                        else:
                            raise ValueError('No value found!')
            except Exception as e:
                raise e
            finally:
                del pos
        else:
            return tuple(islice(self.childs, 0, 1))[0][1]
    
    def compdatch(self, sp: bool = False):
        """Compose data to be written back to fileread"""
        
        try:
            di = {}
            if sp:
                spc = self.gspc()
            else:
                spc = self.gspc(True)
            for i, d  in self.getdata():
                if d == '\n':
                    di[i] = ('space', d)
                elif re.match(r'\s+', d) == None:
                    di[i] = (next(self.parent)[1], d)
                else:
                    pos = re.match(r'\s+', d).span()[1]
                    idx = (pos // spc)
                    di[i] = (tuple(islice(self.childs,idx - 1, idx))[0][0], 
                             d[pos:])
            return (di:= iter(di.values()) if di else None)
        except Exception as e:
            raise e
        
    def insighttree(self) -> dict:
        """
        This is very useful for looking at your TreeView data,
        with understanding your structure. Looking at rows, child and written words. 
        """
        
        try:
            di = {}
            spc = self.gspc()
            for i, d  in self.getdata():
                if d == '\n':
                    di[i] = ('space', d)
                elif re.match(r'\s+', d) == None:
                    di[i] = (next(self.parent)[1], d)
                else:
                    pos = re.match(r'\s+', d).span()[1]
                    idx = (pos // spc)
                    di[i] = (tuple(islice(self.childs,idx - 1, idx))[0][0], 
                             d[pos:])
            return (di:= iter(di.items()) if di else None)
        except Exception as e:
            raise e
            
    def insighthidden(self, data: Iterator) -> dict:
        """
        This is for structuring hidden items to be displayed. 
        """
        
        try:
            if isinstance(data, Iterator):
                di = {}
                spc = self.gspc()
                for i, d in data:
                    if d == '\n':
                        di[i] = ('space', d)
                    elif re.match(r'\s+', d) == None:
                        di[i] = (next(self.parent)[1], d)
                    else:
                        pos = re.match(r'\s+', d).span()[1]
                        idx = (pos // spc)
                        di[i] = (tuple(islice(self.childs,idx - 1, idx))[0][0], 
                                 d[pos:])
                return (di:= iter(di.items()) if di else None)
            else:
                raise TypeError('Must be list!')
        except Exception as e:
            raise e
        finally:
            del data, di, spc
            
    def quickchild(self, words: str, child: str ) -> None:
        """
        You must define the variable child e.g: 'child1'. 
        """
        
        try:
            if isinstance(words, str):
                if (child := self.getchild(child)):
                    self.filop(f'{" " * child}-{words}\n', 1)
                else:
                    raise ValueError('Invalid child!')
            else:
                raise TypeError('Must be string!')
        except (ValueError, TypeError) as e:
            raise e
        finally:
            del words, child

    def edittree(self, words: str, row: int = 0, child: str = None) -> None:
        """
        You can edit the structure of your tree from row and child.
        Using the insighttree() will help you identifies which row and child to change. 
        """
        
        try:
            data = None
            if isinstance(words, str):
                words = f'{" " * self.getchild(child)}-{words}\n' if child else f'{words}:\n'
                if isinstance(row, int) and self.getdatanum()-1 >= row >= 0 :
                    data = iter(tuple(self.getdata()))
                    self.filop(Gtv.editt(words, data, row))
                else:
                    raise ValueError(f'"row" must be int number and less or equal to {d-1}!')
            else:
                raise TypeError('Must be string and file need to be exist!')
        except TypeError as e:
            raise e
        finally:
            del words, row, child, data
            
    def addparent(self, words: str) -> None:
        """
        Use this if you want to add new parent. Do not use the writetree() anymore.
        """
        
        try:
            if isinstance(words, str):
                self.filop('\n', 1)
                self.filop(f'{words}:\n', 1)
            else:
                raise TypeError('Must be string!')
        except TypeError as e:
            raise e
        finally:
            del words
            
    def delrow(self, row: int) -> None:
        """
        This function is to delete a row in a TreeView text file.
        """
        
        try:
            read = None
            if isinstance(row, int):
                if row <= self.getdatanum() - 1:
                    read = (d for i, d in iter(tuple(self.getdata())) if i != row)
                    self.filop(read)
                else:
                    raise ValueError(f'The row {row} is not exist!')
            else:
                raise TypeError('Must be int!')
        except (TypeError, ValueError) as e:
            raise e
        finally:
            del row, read
            
    def insertrow(self, words: str, row: int = 0, child: str = None) -> None:
        """
        This function is to insert words into a decided row within the TreeView structure. 
        """
        
        try:
            data = None
            if isinstance(words,str):
                words = f'{" " * self.getchild(child)}-{words}\n' if child else f'{words}:\n'
                if row <= self.getdatanum()-1:
                    data = iter(tuple(self.getdata())) 
                    self.filop(Gtv.insertr(words, data, row))
                else:
                    raise ValueError('"row" need to be less or equal to {len(read)-1}')
            else:
                raise TypeError('Need to be string!')
        except (TypeError, ValueError) as e:
            raise e
        finally:
            del words, row, child, data
    
    def movetree(self, row: int, to: int) -> None:
        """
        Moving one row to another. From row to another row. Suggested to use insighttree(),
        for knowing where to move.
        """
        
        try:
            data = None
            num = None
            if isinstance(row, int) and isinstance(to, int):
                data = iter(tuple(self.getdata()))
                num = self.getdatanum()
                if to >=  num and row < to:
                    self.filop(Gtv.movet(data, row, to, True))
                elif row < num:
                    self.filop(Gtv.movet(data, row, to))
                else:
                    raise IndexError('Not implemented on this index!')
            else:
                raise ValueError('Must be int!')
        except (ValueError, IndexError) as e:
            raise e
        finally:
            del data, row, to, num
            
    def movechild(self, row: int, child: str) -> None:
        """
        Moving row to left or right side using child. Suggested to use insighttree(),
        for knowing where to move.
        """
        
        try:
            data = None
            if (child := self.getchild(child)):
                if row <= self.getdatanum()-1:
                    data = iter(tuple(self.getdata()))
                    self.filop(Gtv.movec(data, row, child))
                else:
                    raise IndexError('Not implemented index!')
            else:
                raise ValueError('Invalid child!')
        except (IndexError, ValueError) as e:
            raise e
        finally:
            del row, child, data
                            
    def readtree(self) -> None:
        """
        Print out your TreeView in console.
        """
        
        for _, r in self.getdata():
            print(r, end = '')
                    
    def fileread(self, file: Iterator) -> None:
        """
        File need to be a dict or list. The pattern need to be:
            - Dict:
                {0:('parent', 'This is the beginning of TreeView structure'),
                 1:('child1', 'This is the child structure'),
                }
                Note: However, the dict will converted to list as well.
                      This dict pattern is the same as the insighttree() function.
            - List:
                [('parent', 'This is the beginning of TreeView structure'),
                 ('child1', 'This is the child structure'),
                ]
        This file will be written to a filename.txt.
        
        WARNING: Make sure you create blank filename.txt.
        If you use existing TreeView structure, all that has been written will be lost.
        The new file will overwrite the existing one.
        """
        
        try:
            if isinstance(file, Iterator):
                with open(f'{self.filename}.txt', 'w') as wfile:
                    for f in file:
                        span, word = f
                        if all(isinstance(s, str) for s in [span, word]):
                            if span == 'parent':
                                if word[-2:] == ':\n' :
                                    wfile.write(f'{word}')
                                else:
                                    wfile.write(f'{word}:\n')
                            elif self.getchild(span):
                                if  word[0] == '-' and word[-1] == '\n':
                                    wfile.write(f'{" " * self.getchild(span)}{word}')
                                else:
                                    wfile.write(f'{" " * self.getchild(span)}-{word}\n')
                            elif span == 'space':
                                wfile.write('\n')
                            del span, word, f
                        else:
                            raise TypeError('Variables need to be string!')
            else:
                raise TypeError('File need to be an iterator!')
        except Exception as e:
            raise e
        finally:
            del file
            
    def backuptv(self) -> None:
        """
        Backup TreeView structure in json database file. The backup max is 10 records only.
        The max can be change in line with '< 11'
        """
        
        try:
            log = int(datetime.datetime.timestamp(datetime.datetime.now()))
            do = iter({log: tuple(self.compdatch(True))}.items())
            dbs = db(self.filename)
            if not os.path.exists(dbs.pname):
                dbs.createdb(do)
            else:
                if dbs.totalrecs() < 10:
                    dbs.indata(do)
                else:
                    dbs.indata(do)
                    dbs.deldata(sorted(tuple(dbs.loadkeys()))[0])
        except Exception as e:
            raise e
        finally:
            try:
                del log, do, dbs
            except:
                pass
            
    def loadbackup(self, filename: str, row: int = 0, stat: bool = False) -> Union[dict, None]:
        """
        This function can call back your previous data saved by backuptv() and 
        overwrite your existing one.
        """
        try:
            dbs = db(filename)
            if os.path.exists(dbs.pname):
                key = None
                if stat:
                    if row <= dbs.totalrecs()-1:
                        key = sorted(tuple(dbs.loadkeys()))[row]
                        self.fileread(iter(dbs.takedat(key)))
                else:
                    if row <= dbs.totalrecs()-1:
                        key = sorted(tuple(dbs.loadkeys()))[row]
                        return dict(enumerate(dbs.takedat(key)))
                del key
            else:
                raise FileNotFoundError('DataBase not found')
        except Exception as e:
            raise e
        finally:
            del dbs, filename, row, stat
            
    def checked(self, row: int) -> None:
        """ 
        Appearing nice only in 'utf-8' encoding.
        WARNING: Depend on computer encoding system for appropriate display.
        """
        
        try:
            data = None
            stc = None
            if isinstance(row, int):
                if row <= self.getdatanum()-1:
                    data = iter(tuple(self.getdata()))
                    if self.loc == 'cp65001':  
                        stc = chr(10004)
                    else:
                        stc = '«[DONE]»'
                    self.filop(Gtv.genchek(data, row, stc))
                else:
                    raise IndexError('Not implemeted index!')
            else:
                raise TypeError('Must be int!')
        except (IndexError, TypeError) as e:
            raise e
        finally:
            del row, data, stc
                    
    def insertspace(self, row: int) -> None:
        """
        Insert spaces before creating parent
        """
        
        try:
            data = None
            if row <= self.getdatanum()-1:
                data = iter(tuple(self.getdata()))
                self.filop(Gtv.gensp(data, row))
            else:
                raise IndexError('Not implemented index!')
        except IndexError as e:
            raise e
        finally:
            del data, row