# SPDX-License-Identifier: 	NASA-1.3

from os import write
import numpy as np 
import os.path as osp
import struct
from typing import List

from .block import Block

def __write_plot3D_block_binary(f,B:Block,double_precision:bool=True):
    """Write binary plot3D block which contains X,Y,Z
        default format is Big-Endian

    Args:
        f (IO): file handle
        B (Block): writes a single block to a file
        double_precision (bool): writes to binary using double precision
    """
    '''
        https://docs.python.org/3/library/struct.html
    '''
    def write_var(V:np.ndarray):
        for k in range(B.KMAX):
            for j in range(B.JMAX):
                for i in range(B.IMAX):
                    if not double_precision:
                        f.write(struct.pack('<f',V[i,j,k]))
                    else:
                        f.write(struct.pack('<d',V[i,j,k]))
    write_var(B.X)
    write_var(B.Y)
    write_var(B.Z)

def __write_plot3D_block_ASCII(f,B:Block,columns:int=6):
    """Write plot3D block in ascii format 

    Args:
        f (IO): file handle
        B (Block): writes a single block to a file
        columns (int, optional): Number of columns in the file. Defaults to 6.
    """
    def write_var(V:np.ndarray):
        bNewLine = False
        indx = 0
        for k in range(B.KMAX):
            for j in range(B.JMAX):
                for i in range(B.IMAX):
                    f.write('{0:8.8f} '.format(V[i,j,k]))
                    bNewLine=False
                    indx+=1
                    if (indx % columns) == 0:
                        f.write('\n')
                        bNewLine=True
                    
        if not bNewLine:
            f.write('\n')
    write_var(B.X)
    write_var(B.Y)
    write_var(B.Z)

def write_plot3D(filename:str,blocks:List[Block],binary:bool=True,double_precision:bool=True):
    """Writes blocks to a Plot3D file

    Args:
        filename (str): name of the file to create 
        blocks (List[Block]): List containing all the blocks to write
        binary (bool, optional): Binary big endian. Defaults to True.
        double_precision (bool, optional). Writes to binary file using double precision. Defaults to True
    """
    if binary:
        with open(filename,'wb') as f:
            f.write(struct.pack('I',len(blocks)))
            for b in blocks:
                IMAX,JMAX,KMAX = b.X.shape
                f.write(struct.pack('I',IMAX))
                f.write(struct.pack('I',JMAX))
                f.write(struct.pack('I',KMAX))
            for b in blocks:
                __write_plot3D_block_binary(f,b,double_precision)
    else:
        with open(filename,'w') as f:
            f.write('{0:d}\n'.format(len(blocks)))
            for b in blocks:
                IMAX,JMAX,KMAX = b.X.shape
                f.write('{0:d} {1:d} {2:d}\n'.format(IMAX,JMAX,KMAX))            
            for b in blocks:
                __write_plot3D_block_ASCII(f,b)

def __write_plot2D_block_binary(f,B:Block,double_precision:bool=True):
    """Write binary Plot2D block which contains X,Y
        default format is Big-Endian

    Args:
        f (IO): file handle
        B (Block): writes a single block to a file
        double_precision (bool): writes to binary using double precision
    """
    '''
        https://docs.python.org/3/library/struct.html
    '''
    def write_var(V:np.ndarray):
        k = 0
        for j in range(B.JMAX):
            for i in range(B.IMAX):
                if not double_precision:
                    f.write(struct.pack('<f',V[i,j,k]))
                else:
                    f.write(struct.pack('<d',V[i,j,k]))
    write_var(B.X)
    write_var(B.Y)

def __write_plot2D_block_ASCII(f,B:Block,columns:int=6):
    """Write Plot2D block in ascii format 

    Args:
        f (IO): file handle
        B (Block): writes a single block to a file
        columns (int, optional): Number of columns in the file. Defaults to 6.
    """
    def write_var(V:np.ndarray):
        bNewLine = False
        indx = 0
        k = 0
        for j in range(B.JMAX):
            for i in range(B.IMAX):
                f.write('{0:8.8f} '.format(V[i,j,k]))
                bNewLine=False
                indx+=1
                if (indx % columns) == 0:
                    f.write('\n')
                    bNewLine=True
                    
        if not bNewLine:
            f.write('\n')
    write_var(B.X)
    write_var(B.Y)

def write_plot2D(filename:str,blocks:List[Block],binary:bool=True,double_precision:bool=True):
    """Writes blocks to a Plot2D file

    Args:
        filename (str): name of the file to create 
        blocks (List[Block]): List containing all the blocks to write
        binary (bool, optional): Binary big endian. Defaults to True.
        double_precision (bool, optional). Writes to binary file using double precision. Defaults to True
    """
    if binary:
        with open(filename,'wb') as f:
            f.write(struct.pack('I',len(blocks)))
            for b in blocks:
                IMAX,JMAX,KMAX = b.X.shape
                f.write(struct.pack('I',IMAX))
                f.write(struct.pack('I',JMAX))
            for b in blocks:
                __write_plot2D_block_binary(f,b,double_precision)
    else:
        with open(filename,'w') as f:
            f.write('{0:d}\n'.format(len(blocks)))
            for b in blocks:
                IMAX,JMAX,KMAX = b.X.shape
                f.write('{0:d} {1:d}\n'.format(IMAX,JMAX))            
            for b in blocks:
                __write_plot2D_block_ASCII(f,b)