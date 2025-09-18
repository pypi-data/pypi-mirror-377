# SPDX-License-Identifier: 	NASA-1.3

from typing import List, Dict, Tuple
from itertools import combinations_with_replacement, permutations, product
import numpy as np
from .block import Block
from .blockfunctions import rotate_block, reduce_blocks
from .face import Face
from .facefunctions import outer_face_dict_to_list,match_faces_dict_to_list, create_face_from_diagonals, find_bounding_faces,get_outer_faces
from .connectivity import get_face_intersection, face_matches_to_dict
from math import cos, radians, sin, sqrt, acos, radians
from copy import deepcopy
import math 

def periodicity_fast(blocks:List[Block],outer_faces:List[Face], matched_faces:List[Dict[str,int]], periodic_direction:str='k', rotation_axis:str='x',nblades:int=55):
    """Finds the connectivity of blocks when they are rotated by an angle defined by the number of blades. Only use this if your mesh is of an annulus. 
        This function reduces the size of the blocks by a factor of the minimum gcd. This speeds up finding the connectivity 

    Args:
        blocks (List[Block]): List of blocks that will be scanned for perodicity
        outer_faces (List[Dict[str,int]]): List of outer faces for each block as a dictionary format. You can get this from connectivity
        matched_faces (ListList[Dict[str,int]]): List of matched faces from connectivity. Matched faces was added so that it's always removed from outer faces 
        periodic_direction (str): either i,j,k to look for
        rotation_axis (str): either x,y,z
        nblades (int): Number of blades to consider, this affects the rotation angle. 

    Returns:
        (Tuple): containing

        - **periodic_faces_export** (List[Dict[str,int]]):  This is list of all the surfaces/faces that match when rotated by an angle formatted as a dictionary.
        - **outer_faces_export** (List[Dict[str,int]]): These are the list of outer faces that are not periodic formatted as a dictionary.
        - **periodic_faces** (List[Tuple[Face,Face]]): - This is a list of Face objects that are connected to each other organized as a list of tuples: [Face1, Face2] where Face 1 will contain the block number and the diagonals [IMIN,JMIN,KMIN,IMAX,JMAX,KMAX]. Example: blk: 1 [168,0,0,268,100,0].
        - **outer_faces_all** (List[Face]): This is a list of outer faces save as a list of Faces
        
    """
    gcd_array = list()
    # Find the gcd of all the blocks 
    for block_indx in range(len(blocks)):
        block = blocks[block_indx]
        gcd_array.append(math.gcd(block.IMAX-1, math.gcd(block.JMAX-1, block.KMAX-1)))
    gcd_to_use = min(gcd_array) # You need to use the minimum gcd otherwise 1 block may not exactly match the next block. They all have to be scaled the same way.
    print(f"gcd to use {gcd_to_use}")
    new_blocks = reduce_blocks(deepcopy(blocks),gcd_to_use)
    matched_faces = deepcopy(matched_faces)
    # Reduce face matches for the block 
    for i in range(len(matched_faces)):
        matched_faces[i]['block1']['IMIN'] = int(matched_faces[i]['block1']['IMIN']/gcd_to_use)
        matched_faces[i]['block1']['JMIN'] = int(matched_faces[i]['block1']['JMIN']/gcd_to_use)
        matched_faces[i]['block1']['KMIN'] = int(matched_faces[i]['block1']['KMIN']/gcd_to_use)
        matched_faces[i]['block1']['IMAX'] = int(matched_faces[i]['block1']['IMAX']/gcd_to_use)
        matched_faces[i]['block1']['JMAX'] = int(matched_faces[i]['block1']['JMAX']/gcd_to_use)
        matched_faces[i]['block1']['KMAX'] = int(matched_faces[i]['block1']['KMAX']/gcd_to_use)

        matched_faces[i]['block2']['IMIN'] = int(matched_faces[i]['block2']['IMIN']/gcd_to_use)
        matched_faces[i]['block2']['JMIN'] = int(matched_faces[i]['block2']['JMIN']/gcd_to_use)
        matched_faces[i]['block2']['KMIN'] = int(matched_faces[i]['block2']['KMIN']/gcd_to_use)
        matched_faces[i]['block2']['IMAX'] = int(matched_faces[i]['block2']['IMAX']/gcd_to_use)
        matched_faces[i]['block2']['JMAX'] = int(matched_faces[i]['block2']['JMAX']/gcd_to_use)
        matched_faces[i]['block2']['KMAX'] = int(matched_faces[i]['block2']['KMAX']/gcd_to_use)

    # Reduce outer faces for the block
    for i in range(len(outer_faces)):
        outer_faces[i]['IMIN'] = int(outer_faces[i]['IMIN']/gcd_to_use)
        outer_faces[i]['IMAX'] = int(outer_faces[i]['IMAX']/gcd_to_use)
        outer_faces[i]['JMIN'] = int(outer_faces[i]['JMIN']/gcd_to_use)
        outer_faces[i]['JMAX'] = int(outer_faces[i]['JMAX']/gcd_to_use)
        outer_faces[i]['KMIN'] = int(outer_faces[i]['KMIN']/gcd_to_use)
        outer_faces[i]['KMAX'] = int(outer_faces[i]['KMAX']/gcd_to_use)

    # Find Periodicity 
    periodic_faces_export, outer_faces_export, periodic_faces, outer_faces_all = periodicity(new_blocks,outer_faces,matched_faces,periodic_direction,rotation_axis,nblades)
    # scale it up
    for i in range(len(periodic_faces_export)):
        periodic_faces_export[i]['block1']['IMIN'] *= gcd_to_use
        periodic_faces_export[i]['block1']['JMIN'] *= gcd_to_use
        periodic_faces_export[i]['block1']['KMIN'] *= gcd_to_use
        periodic_faces_export[i]['block1']['IMAX'] *= gcd_to_use
        periodic_faces_export[i]['block1']['JMAX'] *= gcd_to_use
        periodic_faces_export[i]['block1']['KMAX'] *= gcd_to_use

        periodic_faces_export[i]['block2']['IMIN'] *= gcd_to_use
        periodic_faces_export[i]['block2']['JMIN'] *= gcd_to_use
        periodic_faces_export[i]['block2']['KMIN'] *= gcd_to_use
        periodic_faces_export[i]['block2']['IMAX'] *= gcd_to_use
        periodic_faces_export[i]['block2']['JMAX'] *= gcd_to_use
        periodic_faces_export[i]['block2']['KMAX'] *= gcd_to_use
    
    for i in range(len(periodic_faces)):
        periodic_faces[i][0].I *= gcd_to_use
        periodic_faces[i][0].J *= gcd_to_use
        periodic_faces[i][0].K *= gcd_to_use

        periodic_faces[i][1].I *= gcd_to_use
        periodic_faces[i][1].J *= gcd_to_use
        periodic_faces[i][1].K *= gcd_to_use

    for j in range(len(outer_faces_export)):
        outer_faces_export[j]['IMIN'] *= gcd_to_use
        outer_faces_export[j]['JMIN'] *= gcd_to_use
        outer_faces_export[j]['KMIN'] *= gcd_to_use
        outer_faces_export[j]['IMAX'] *= gcd_to_use
        outer_faces_export[j]['JMAX'] *= gcd_to_use
        outer_faces_export[j]['KMAX'] *= gcd_to_use
    
    for j in range(len(outer_faces_all)):
        outer_faces_all[j].I *= gcd_to_use
        outer_faces_all[j].J *= gcd_to_use
        outer_faces_all[j].K *= gcd_to_use
        
    return periodic_faces_export, outer_faces_export, periodic_faces, outer_faces_all

def create_rotation_matrix(rotation_angle:float, rotation_axis:str="x"):
    """Creates a rotation matrix given an angle and axis 

    Args:
        rotation_angle (float): Rotation angle in radians
        rotation_axis (str, optional): Axis of rotation "x", "y", or "z". Defaults to "x".

    Returns:
        np.ndarray: 3x3 rotation matrix 
    """
    
    if rotation_axis=='x':
        rotation_matrix = np.array([[1,0,0],
                            [0,cos(rotation_angle),-sin(rotation_angle)],
                            [0,sin(rotation_angle),cos(rotation_angle)]])

    elif rotation_axis=='y':
        rotation_matrix = np.array([[cos(rotation_angle),0,sin(rotation_angle)],
                            [0,1,0],
                            [-sin(rotation_angle),0,cos(rotation_angle)]])
    elif rotation_axis=='z':
        rotation_matrix = np.array([[cos(rotation_angle),-sin(rotation_angle), 0],
                            [sin(rotation_angle),cos(rotation_angle), 0],
                            [0, 0, 1]])

    return rotation_matrix 

def periodicity(blocks:List[Block],outer_faces:List[Dict[str,int]], matched_faces:List[Dict[str,int]], periodic_direction:str='k', rotation_axis:str='x',nblades:int=55):
    """This function is used to check for periodicity of the other faces rotated about an axis. Use periodicity_fast instead. Periodicity_fast calls this function after reducing the size of the mesh.
        The way it works is to find faces of a constant i,j, or k value

    Args:
        blocks (List[Block]): List of blocks that will be scanned for perodicity
        outer_faces (List[Dict[str,int]]): List of outer faces for each block as a dictionary format. You can get this from connectivity
        matched_faces (ListList[Dict[str,int]]): List of matched faces from connectivity. Matched faces was added so that it's always removed from outer faces 
        periodic_direction (str): either i,j,k to look for
        rotation_axis (str): either x,y,z
        nblades (int): Number of blades to consider, this affects the rotation angle. 

    Returns:
        (Tuple): containing
            
            - **periodic_faces_export** (List[Dict[str,int]]):  This is list of all the surfaces/faces that match when rotated by an angle formatted as a dictionary.
            - **outer_faces_export** (List[Dict[str,int]]): These are the list of outer faces that are not periodic formatted as a dictionary.
            - **periodic_faces** (List[Tuple[Face,Face]]): - This is a list of Face objects that are connected to each other organized as a list of tuples: [Face1, Face2] where Face 1 will contain the block number and the diagonals [IMIN,JMIN,KMIN,IMAX,JMAX,KMAX]. Example: blk: 1 [168,0,0,268,100,0].
            - **outer_faces_all** (List[Face]): This is a list of outer faces save as a list of Faces

    """
    
    rotation_angle = radians(360.0/nblades)
    rotation_matrix1 = create_rotation_matrix(rotation_angle,rotation_axis)
    rotation_matrix2 = create_rotation_matrix(-rotation_angle,rotation_axis)
    
    # Check periodic within a block 
    periodic_found = True
    
    # Here we make a list of all the outer faces
    periodic_faces = list()      # This is the output of the code 
    periodic_faces_export = list() 
    outer_faces_all = outer_face_dict_to_list(blocks,outer_faces)
    matched_faces_all = match_faces_dict_to_list(blocks,matched_faces)

    split_faces = list()         # List of split but free surfaces, this will be appended to outer_faces_to_remove list
    while periodic_found:
        periodic_found = False        
        outer_faces_to_remove = list()  # Integer list of which outher surfaces to remove
        outer_face_combos = list(combinations_with_replacement(range(len(outer_faces_all)),2))
        t = len(outer_face_combos)
        for i in t: 
            # Check if surfaces are periodic with each other
            face1_indx = outer_face_combos[i][0]
            face2_indx = outer_face_combos[i][1]
            face1 = outer_faces_all[face1_indx]
            face2 = outer_faces_all[face2_indx]
            t.set_description(f"Checking connections block {face1.blockIndex} with {face2.blockIndex}")

            if periodic_direction.lower() == "i":
                
                if (face1.IMIN == face1.IMAX) and (face2.IMIN == face2.IMAX):
                    # Rotate Block 1 -> Check periodicity -> if not periodic -> Rotate Block 1 opposite direction -> Check periodicity
                    #   Rotate Block 1
                    block1_rotated = rotate_block(blocks[face1.blockIndex],rotation_matrix1)
                    block2 = blocks[face2.blockIndex]
                    #   Check periodicity
                    df, periodic_faces_temp, split_faces_temp = __periodicity_check__(face1,face2,block1_rotated, block2)

                    if len(periodic_faces_temp) == 0:
                        block1_rotated = rotate_block(blocks[face1.blockIndex],rotation_matrix2)
                        block2 = blocks[face2.blockIndex]
                        df, periodic_faces_temp, split_faces_temp = __periodicity_check__(face1,face2,block1_rotated, block2)
                        if len(periodic_faces_temp)>0:  # Save the data
                            outer_faces_to_remove.append(face1)
                            outer_faces_to_remove.append(face2)
                            outer_faces_to_remove.append(periodic_faces_temp[0])    # Make sure periodic faces are also removed from outer faces during the loop
                            outer_faces_to_remove.append(periodic_faces_temp[1])
                            periodic_faces.append(periodic_faces_temp)
                            periodic_faces_export.append((face1,face2,block1_rotated,block2))
                            split_faces.extend(split_faces_temp)
                            periodic_found = True
                            break
                    else:   # Save the data
                        outer_faces_to_remove.append(face1)
                        outer_faces_to_remove.append(face2)
                        outer_faces_to_remove.append(periodic_faces_temp[0])
                        outer_faces_to_remove.append(periodic_faces_temp[1])
                        periodic_faces.append(periodic_faces_temp)
                        periodic_faces_export.append(face_matches_to_dict(face1,face2,block1_rotated,block2))
                        split_faces.extend(split_faces_temp)
                        periodic_found = True
                        break

            elif periodic_direction.lower() == "j":
                
                if (face1.JMIN == face1.JMAX) and (face2.JMIN == face2.JMAX): 
                    # Rotate Block 1 -> Check periodicity -> if not periodic -> Rotate Block 1 opposite direction -> Check periodicity
                    #   Rotate Block 1
                    block1_rotated = rotate_block(blocks[face1.blockIndex],rotation_matrix1)
                    block2 = blocks[face2.blockIndex]
                    #   Check periodicity
                    df, periodic_faces_temp, split_faces_temp = __periodicity_check__(face1,face2,block1_rotated, block2)

                    if len(periodic_faces_temp) == 0:
                        block1_rotated = rotate_block(blocks[face1.blockIndex],rotation_matrix2)
                        block2 = blocks[face2.blockIndex]
                        df, periodic_faces_temp, split_faces_temp = __periodicity_check__(face1,face2,block1_rotated, block2)
                        if len(periodic_faces_temp)>0:  # Save the data
                            outer_faces_to_remove.append(face1)
                            outer_faces_to_remove.append(face2)
                            outer_faces_to_remove.append(periodic_faces_temp[0])
                            outer_faces_to_remove.append(periodic_faces_temp[1])
                            periodic_faces.append(periodic_faces_temp)
                            periodic_faces_export.append(face_matches_to_dict(face1,face2,block1_rotated,block2))
                            split_faces.extend(split_faces_temp)
                            periodic_found = True
                            break
                    else:   # Save the data
                        outer_faces_to_remove.append(face1)
                        outer_faces_to_remove.append(face2)
                        outer_faces_to_remove.append(periodic_faces_temp[0])
                        outer_faces_to_remove.append(periodic_faces_temp[1])
                        periodic_faces.append(periodic_faces_temp)
                        periodic_faces_export.append(face_matches_to_dict(face1,face2,block1_rotated,block2))
                        split_faces.extend(split_faces_temp)
                        periodic_found = True
                        break

            elif periodic_direction.lower() == 'k':       # constant k between surfaces 
                 if (face1.KMIN == face1.KMAX) and (face2.KMIN == face2.KMAX): 
                    # Rotate Block 1 -> Check periodicity -> if not periodic -> Rotate Block 1 opposite direction -> Check periodicity
                    #   Rotate Block 1
                    block1_rotated = rotate_block(blocks[face1.blockIndex],rotation_matrix1)
                    block2 = blocks[face2.blockIndex]
                    #   Check periodicity
                    df, periodic_faces_temp, split_faces_temp = __periodicity_check__(face1,face2,block1_rotated, block2)

                    if len(periodic_faces_temp) == 0:
                        block1_rotated = rotate_block(blocks[face1.blockIndex],rotation_matrix2)
                        block2 = blocks[face2.blockIndex]
                        df, periodic_faces_temp, split_faces_temp = __periodicity_check__(face1,face2,block1_rotated, block2)
                        if len(periodic_faces_temp)>0:  # Save the data
                            outer_faces_to_remove.append(face1)
                            outer_faces_to_remove.append(face2)
                            outer_faces_to_remove.append(periodic_faces_temp[0])
                            outer_faces_to_remove.append(periodic_faces_temp[1])
                            periodic_faces.append(periodic_faces_temp)
                            periodic_faces_export.append(face_matches_to_dict(periodic_faces_temp[0],periodic_faces_temp[1],block1_rotated,block2))
                            split_faces.extend(split_faces_temp)
                            periodic_found = True
                            break
                    else:   # Save the data
                        outer_faces_to_remove.append(face1)
                        outer_faces_to_remove.append(face2)
                        outer_faces_to_remove.append(periodic_faces_temp[0])
                        outer_faces_to_remove.append(periodic_faces_temp[1])
                        periodic_faces.append(periodic_faces_temp)
                        periodic_faces_export.append(face_matches_to_dict(periodic_faces_temp[0],periodic_faces_temp[1],block1_rotated,block2))
                        split_faces.extend(split_faces_temp)
                        periodic_found = True
                        break

        if (periodic_found):
            outer_faces_to_remove = list(set(outer_faces_to_remove))
            outer_faces_all = [p for p in outer_faces_all if p not in outer_faces_to_remove]
            if len(split_faces)>0:
                outer_faces_all.extend(split_faces)
                split_faces.clear()

    # This is an added check to make sure all periodic faces are in the outer_faces_to_remove
    for p in periodic_faces:
        outer_faces_to_remove.append(p[0])
        outer_faces_to_remove.append(p[1])

    for m in matched_faces_all:
        outer_faces_to_remove.append(m)

    outer_faces_to_remove = list(set(outer_faces_to_remove))    # Use only unique values
    outer_faces_all = [p for p in outer_faces_all if p not in outer_faces_to_remove]    # remove from outer faces 
    # remove any duplicate periodic face pairs 
    indx_to_remove = list()
    for i in range(len(periodic_faces)):
        for j in range(i+1,len(periodic_faces)):
            if periodic_faces[i][0] == periodic_faces[j][0]:
                if periodic_faces[i][1] == periodic_faces[j][1]:
                    indx_to_remove.append(j)
            if periodic_faces[i][1] == periodic_faces[j][0]:
                if periodic_faces[i][0] == periodic_faces[j][1]:
                    indx_to_remove.append(j)
    

    periodic_faces_export = [periodic_faces_export[i] for i in range(len(periodic_faces)) if i not in indx_to_remove]
    periodic_faces = [periodic_faces[i] for i in range(len(periodic_faces)) if i not in indx_to_remove]
    # Export periodic faces and outer faces
    outer_faces_export = list() 

    for o in outer_faces_all:
        outer_faces_export.append(o.to_dict())
                        
    return periodic_faces_export, outer_faces_export, periodic_faces, outer_faces_all


def rotated_periodicity(blocks:List[Block], matched_faces:List[Dict[str,int]], outer_faces:List[Dict[str,int]], rotation_angle:float, rotation_axis:str = "x", ReduceMesh:bool=True):
    """Finds the peridocity/connectivity by rotating a block. This is a bit different from "periodicity_fast" where you specify the periodic direction. This method doesn't care about the direction as long as the angle you specify results in a match between the Left Face and the Right Face. I would use this instead.

    Example 1:              
        L      RL           R
        | blk1 || Copy blk1 |
        | blk2 || Copy blk2 |
        | blk3 || Copy blk3 |
        Rotates the set of blocks by an angle and checks the matching surfaces for R and L. 

    Args:
        blocks (List[Block]): List of blocks for a particular geometry. Do not duplicate the geometry and pass it in! 
        outer_faces (List[Dict[str,int]]): List of outer faces in dictionary form
        rotation_angle (float): rotation angle in between geometry in degrees.
        rotation_axis (str, Optional): "x", "y", or "z" 
        ReduceMesh (bool, Optional): True, reduces the mesh for faster matching
    
    periodic_faces, outer_faces_export, _, _ = rotated_periodicity(blocks,face_matches, outer_faces, rotation_angle=rotation_angle, rotation_axis = "x")
    
    Replaces:
        Is the same as 

        periodic_surfaces, outer_faces_to_keep,periodic_faces,outer_faces = periodicity_fast(blocks,outer_faces,face_matches,periodic_direction='k',rotation_axis='x',nblades=55)
        and
        periodic_surfaces, outer_faces_to_keep,periodic_faces,outer_faces = periodicity(blocks,outer_faces,face_matches,periodic_direction='k',rotation_axis='x',nblades=55)


    Returns:
        (Tuple): containing
            
            - **periodic_faces_export** (List[Dict[str,int]]):  This is list of all the surfaces/faces that match when rotated by an angle formatted as a dictionary.
            - **outer_faces_export** (List[Dict[str,int]]): These are the list of outer faces that are not periodic formatted as a dictionary.
            - **periodic_faces** (List[Tuple[Face,Face]]): - This is a list of Face objects that are connected to each other organized as a list of tuples: [Face1, Face2] where Face 1 will contain the block number and the diagonals [IMIN,JMIN,KMIN,IMAX,JMAX,KMAX]. Example: blk: 1 [168,0,0,268,100,0].
            - **outer_faces_all** (List[Face]): This is a list of outer faces save as a list of Faces
    """
    gcd_array = list()
    # Find the gcd of all the blocks 
    if ReduceMesh==True:
        for block_indx in range(len(blocks)):
            block = blocks[block_indx]
            gcd_array.append(math.gcd(block.IMAX-1, math.gcd(block.JMAX-1, block.KMAX-1)))
        gcd_to_use = min(gcd_array) # You need to use the minimum gcd otherwise 1 block may not exactly match the next block. They all have to be scaled the same way.
        blocks = reduce_blocks(deepcopy(blocks),gcd_to_use)

    rotation_matrix = create_rotation_matrix(radians(rotation_angle),rotation_axis)
    
    blocks_rotated = [rotate_block(b,rotation_matrix) for b in blocks] 
   
    # Check periodic within a block 
    periodic_found = True
    
    # Here we make a list of all the outer faces
    periodic_faces = list()      # This is the output of the code 
    periodic_faces_export = list() 

    outer_faces_all = outer_face_dict_to_list(blocks,outer_faces,gcd_to_use)
    matched_faces_all = match_faces_dict_to_list(blocks,matched_faces,gcd_to_use)

    split_faces = list()         # List of split but free surfaces, this will be appended to outer_faces_to_remove list
    non_matching = list()
    while periodic_found:
        periodic_found = False        
        outer_faces_to_remove = list()  # Integer list of which outer surfaces to remove
        outer_face_combos = list(permutations(range(len(outer_faces_all)),2))
        outer_face_combos = list(set(outer_face_combos) - set(non_matching)) # removes face combinations already checked
        t = len(outer_face_combos)
        for i in t: 
            # Check if surfaces are periodic with each other
            face1_indx = outer_face_combos[i][0]
            face2_indx = outer_face_combos[i][1]
            face1 = outer_faces_all[face1_indx]
            face2 = outer_faces_all[face2_indx]
            t.set_description(f"Checking connections block {face1.blockIndex} with {face2.blockIndex}")

            if (face1.IMIN == face1.IMAX) and (face2.IMIN == face2.IMAX) or \
                (face1.JMIN == face1.JMAX) and (face2.JMIN == face2.JMAX) or \
                (face1.KMIN == face1.KMAX) and (face2.KMIN == face2.KMAX):
                    
                # Rotate Block 1 -> Check periodicity -> if not periodic -> Rotate Block 1 opposite direction -> Check periodicity
                #   Rotate Block 1
                block1_rotated = blocks_rotated[face1.blockIndex]
                block2 = blocks[face2.blockIndex]
                #   Check periodicity
                df, periodic_faces_temp, split_faces_temp = __periodicity_check__(face1,face2,block1_rotated, block2)
                
                if len(periodic_faces_temp) > 0:
                    outer_faces_to_remove.append(face1)
                    outer_faces_to_remove.append(face2)
                    outer_faces_to_remove.append(periodic_faces_temp[0])
                    outer_faces_to_remove.append(periodic_faces_temp[1])
                    periodic_faces.append(periodic_faces_temp)
                    periodic_faces_export.append(face_matches_to_dict(periodic_faces_temp[0],periodic_faces_temp[1],block1_rotated,block2))
                    split_faces.extend(split_faces_temp)
                    periodic_found = True
                    break
            else: 
                non_matching.append((face1_indx,face2_indx))

        if (periodic_found):
            outer_faces_to_remove = list(set(outer_faces_to_remove))
            outer_faces_all = [p for p in outer_faces_all if p not in outer_faces_to_remove]
            if len(split_faces)>0:
                outer_faces_all.extend(split_faces)
                split_faces.clear()        
            
    # This is an added check to make sure all periodic faces are in the outer_faces_to_remove
    for p in periodic_faces:
        outer_faces_to_remove.append(p[0])
        outer_faces_to_remove.append(p[1])

    for m in matched_faces_all:
        outer_faces_to_remove.append(m)

    outer_faces_to_remove = list(set(outer_faces_to_remove))    # Use only unique values
    outer_faces_all = [p for p in outer_faces_all if p not in outer_faces_to_remove]    # remove from outer faces 
    # remove any duplicate periodic face pairs 
    indx_to_remove = list()
    for i in range(len(periodic_faces)):
        for j in range(i+1,len(periodic_faces)):
            if periodic_faces[i][0] == periodic_faces[j][0]:
                if periodic_faces[i][1] == periodic_faces[j][1]:
                    indx_to_remove.append(j)
            if periodic_faces[i][1] == periodic_faces[j][0]:
                if periodic_faces[i][0] == periodic_faces[j][1]:
                    indx_to_remove.append(j)
    

    periodic_faces_export = [periodic_faces_export[i] for i in range(len(periodic_faces)) if i not in indx_to_remove]
    periodic_faces = [periodic_faces[i] for i in range(len(periodic_faces)) if i not in indx_to_remove]
    # Export periodic faces and outer faces
    outer_faces_export = list() 

    for o in outer_faces_all:
        outer_faces_export.append(o.to_dict())

    # scale it up
    for i in range(len(periodic_faces_export)):
        periodic_faces_export[i]['block1']['IMIN'] *= gcd_to_use
        periodic_faces_export[i]['block1']['JMIN'] *= gcd_to_use
        periodic_faces_export[i]['block1']['KMIN'] *= gcd_to_use
        periodic_faces_export[i]['block1']['IMAX'] *= gcd_to_use
        periodic_faces_export[i]['block1']['JMAX'] *= gcd_to_use
        periodic_faces_export[i]['block1']['KMAX'] *= gcd_to_use

        if (periodic_faces_export[i]['block2']['IMIN'] == 168):
            print("check")
        periodic_faces_export[i]['block2']['IMIN'] *= gcd_to_use
        periodic_faces_export[i]['block2']['JMIN'] *= gcd_to_use
        periodic_faces_export[i]['block2']['KMIN'] *= gcd_to_use
        periodic_faces_export[i]['block2']['IMAX'] *= gcd_to_use
        periodic_faces_export[i]['block2']['JMAX'] *= gcd_to_use
        periodic_faces_export[i]['block2']['KMAX'] *= gcd_to_use
    
    for i in range(len(periodic_faces)):
        periodic_faces[i][0].I *= gcd_to_use
        periodic_faces[i][0].J *= gcd_to_use
        periodic_faces[i][0].K *= gcd_to_use

        periodic_faces[i][1].I *= gcd_to_use
        periodic_faces[i][1].J *= gcd_to_use
        periodic_faces[i][1].K *= gcd_to_use

    for j in range(len(outer_faces_export)):
        outer_faces_export[j]['IMIN'] *= gcd_to_use
        outer_faces_export[j]['JMIN'] *= gcd_to_use
        outer_faces_export[j]['KMIN'] *= gcd_to_use
        outer_faces_export[j]['IMAX'] *= gcd_to_use
        outer_faces_export[j]['JMAX'] *= gcd_to_use
        outer_faces_export[j]['KMAX'] *= gcd_to_use
    
    for j in range(len(outer_faces_all)):
        outer_faces_all[j].I *= gcd_to_use
        outer_faces_all[j].J *= gcd_to_use
        outer_faces_all[j].K *= gcd_to_use
    return periodic_faces_export, outer_faces_export, periodic_faces, outer_faces_all

def translational_periodicity(blocks:List[Block], lower_connected_faces:List[Dict[str,int]], upper_connected_faces:List[Dict[str,int]],delta:float=None, translational_direction:str = "z"):
    """Find periodicity using translated blocks. Simple example: if you have a rectangle and the top and bottom surfaces are periodic, this will copy the rectangle and shift it up to find which surfaces match. 

    Args:
        blocks (List[Block]): List of blocks for a particular geometry. Do not duplicate the geometry and pass it in
        lower_connected_faces (List[Dict[str,int]]): List of faces in the lower or left bound of the mesh
        upper_connected_faces (List[Dict[str,int]]): List of faces in the upper or right bound of the mesh
        delta (float): if specified the delta will be used to shift the blocks. Defaults to None
        translational_direction (str, Optional): "x", "y", or "z" 
    
    Example:
        y_periodic_faces_export, periodic_faces = translational_periodicity(blocks,left_bound,right_bound,translational_direction='y')

    Returns:
        (Tuple): containing
            
            - **periodic_faces_export** (List[Dict[str,int]]):  This is list of all the surfaces/faces that match when rotated by an angle formatted as a dictionary.
            - **outer_faces_export** (List[Dict[str,int]]): These are the list of outer faces that are not periodic formatted as a dictionary.
            - **periodic_faces** (List[Tuple[Face,Face]]): - This is a list of Face objects that are connected to each other organized as a list of tuples: [Face1, Face2] where Face 1 will contain the block number and the diagonals [IMIN,JMIN,KMIN,IMAX,JMAX,KMAX]. Example: blk: 1 [168,0,0,268,100,0].
            - **outer_faces_all** (List[Face]): This is a list of outer faces save as a list of Faces
    """
    gcd_array = list()
    # Find the gcd of all the blocks
    for block_indx in range(len(blocks)):
        block = blocks[block_indx]
        gcd_array.append(math.gcd(block.IMAX-1, math.gcd(block.JMAX-1, block.KMAX-1)))
    gcd_to_use = min(gcd_array) # You need to use the minimum gcd otherwise 1 block may not exactly match the next block. They all have to be scaled the same way.
    lower_connected_faces = outer_face_dict_to_list(blocks,lower_connected_faces,gcd_to_use)
    upper_connected_faces = outer_face_dict_to_list(blocks,upper_connected_faces,gcd_to_use)
    blocks = reduce_blocks(deepcopy(blocks),gcd_to_use)    
    
    # Now for the periodicity part
    
    def shift_blocks(sign:int=1):
        blocks_shifted = deepcopy(blocks)
        if translational_direction.lower().strip() == "x":
            xmin = min([b.X.min() for b in blocks])
            xmax = max([b.X.max() for b in blocks])
            dx = xmax-xmin if not delta else delta
            [b.shift(sign*dx,translational_direction) for b in blocks_shifted]
        elif translational_direction.lower().strip() == "y":
            ymin = np.array([(b.X.min(), b.Y.min(), b.Z.min()) for b in blocks]) # Look at the front face 
            ymax = np.array([(b.X.min(), b.Y.max(), b.Z.min()) for b in blocks])
            xmin = min([b.X.min() for b in blocks])
            zmin = min([b.Z.min() for b in blocks])

            ymin = ymin[ymin[:,0] == xmin,:]
            ymax = ymax[ymax[:,0] == xmin,:]

            ymin = ymin[ymin[:,2] == zmin,:]
            ymax = ymax[ymax[:,2] == zmin,:]
            
            dy = ymax[:,1].max() - ymin[:,1].min() if not delta else delta
            [b.shift(sign*dy,translational_direction) for b in blocks_shifted]
        else: #  direction.lower().strip() == "z"
            zmin = min([b.Z.min() for b in blocks])
            zmax = max([b.Z.max() for b in blocks])
            dz = zmax-zmin if not delta else delta
            [b.shift(sign*dz,translational_direction) for b in blocks_shifted]
        return blocks_shifted

    blocks_shifted = shift_blocks()
    periodic_found = True # start of the loop 
    
    # Here we make a list of all the outer faces
    times_failed = 0 
    periodic_faces = list()      # This is the output of the code 
    periodic_faces_export = list()
    non_matching = list()
    lower_connected_faces = list(set(lower_connected_faces))
    upper_connected_faces = list(set(upper_connected_faces))
    lower_blocks = [l.BlockIndex for l in lower_connected_faces]
    upper_blocks = [u.BlockIndex for u in upper_connected_faces]
    #pbar = tqdm(total = len(lower_connected_faces))
    
    periodicity_tol = 1E-6 
    while len(lower_connected_faces)>0:
        periodic_found = False
        face1 = lower_connected_faces[0]
        for indx in range(len(upper_connected_faces)):
            face2 = upper_connected_faces[indx]
            # Check if surfaces are periodic with each other
            #pbar.set_description(f"Checking connections block {face1.blockIndex} with {face2.blockIndex}")
            # Shift block 1 -> Check periodicity -> if not periodic -> shift Block 1 opposite direction -> Check periodicity
            #   Rotate Block 1
            block1 = blocks[face1.blockIndex]
            block1_shifted = blocks_shifted[face1.blockIndex]
            block2 = blocks[face2.blockIndex]
            block2_shifted = blocks_shifted[face2.blockIndex]

            #   Check periodicity
            _, periodic_faces_temp, split_faces_temp = __periodicity_check__(face1,face2,block1_shifted, block2,periodicity_tol)                           

            if len(periodic_faces_temp) > 0:
                lower_connected_faces.pop(0)
                upper_connected_faces.pop(indx)
                periodic_faces.append(periodic_faces_temp)
                periodic_faces_export.append(face_matches_to_dict(periodic_faces_temp[0],periodic_faces_temp[1],block1_shifted,block2))
                lower_split_faces = [s for s in split_faces_temp if s.BlockIndex in lower_blocks]
                upper_split_faces = [s for s in split_faces_temp if s.BlockIndex in upper_blocks]
                lower_connected_faces.extend(lower_split_faces)
                upper_connected_faces.extend(upper_split_faces)
                periodic_found = True
                #pbar.update(1)
                break
            else:
                # Try the other way 
                _, periodic_faces_temp, split_faces_temp = __periodicity_check__(face1,face2,block1,block2_shifted,periodicity_tol)
                if len(periodic_faces_temp) > 0:
                    lower_connected_faces.pop(0)
                    upper_connected_faces.pop(indx)
                    periodic_faces.append(periodic_faces_temp)
                    periodic_faces_export.append(face_matches_to_dict(periodic_faces_temp[0],periodic_faces_temp[1],block1, block2_shifted))
                    lower_split_faces = [s for s in split_faces_temp if s.BlockIndex in lower_blocks]
                    upper_split_faces = [s for s in split_faces_temp if s.BlockIndex in upper_blocks]
                    lower_connected_faces.extend(lower_split_faces)
                    upper_connected_faces.extend(upper_split_faces)
                    periodic_found = True
                    #pbar.update(1)
                    break
    
        if periodic_found == False:
            # Lets switch the order 
            non_matching.append(deepcopy(face1))
            lower_connected_faces.pop(0)
            # periodicity_tol *=10
            times_failed+=1

    if len(non_matching)>0:
        print(f"\nNot periodic {translational_direction}")
    else:
        print(f"\nPeriodic {translational_direction}")
        
    # remove any duplicate periodic face pairs 
    indx_to_remove = list()
    for i in range(len(periodic_faces)):
        for j in range(i+1,len(periodic_faces)):
            if periodic_faces[i][0] == periodic_faces[j][0]:
                if periodic_faces[i][1] == periodic_faces[j][1]:
                    indx_to_remove.append(j)
            if periodic_faces[i][1] == periodic_faces[j][0]:
                if periodic_faces[i][0] == periodic_faces[j][1]:
                    indx_to_remove.append(j)
    

    periodic_faces_export = [periodic_faces_export[i] for i in range(len(periodic_faces)) if i not in indx_to_remove]
    periodic_faces = [periodic_faces[i] for i in range(len(periodic_faces)) if i not in indx_to_remove]

    # scale it up
    for i in range(len(periodic_faces_export)):
        periodic_faces_export[i]['block1']['IMIN'] *= gcd_to_use
        periodic_faces_export[i]['block1']['JMIN'] *= gcd_to_use
        periodic_faces_export[i]['block1']['KMIN'] *= gcd_to_use
        periodic_faces_export[i]['block1']['IMAX'] *= gcd_to_use
        periodic_faces_export[i]['block1']['JMAX'] *= gcd_to_use
        periodic_faces_export[i]['block1']['KMAX'] *= gcd_to_use

        if (periodic_faces_export[i]['block2']['IMIN'] == 168):
            print("check")
        periodic_faces_export[i]['block2']['IMIN'] *= gcd_to_use
        periodic_faces_export[i]['block2']['JMIN'] *= gcd_to_use
        periodic_faces_export[i]['block2']['KMIN'] *= gcd_to_use
        periodic_faces_export[i]['block2']['IMAX'] *= gcd_to_use
        periodic_faces_export[i]['block2']['JMAX'] *= gcd_to_use
        periodic_faces_export[i]['block2']['KMAX'] *= gcd_to_use
    
    for i in range(len(periodic_faces)):
        periodic_faces[i][0].I *= gcd_to_use
        periodic_faces[i][0].J *= gcd_to_use
        periodic_faces[i][0].K *= gcd_to_use

        periodic_faces[i][1].I *= gcd_to_use
        periodic_faces[i][1].J *= gcd_to_use
        periodic_faces[i][1].K *= gcd_to_use

    return periodic_faces_export, periodic_faces


def linear_real_transform(face1:Face,face2:Face) -> Tuple:
    """Computes the rotation angle from Face1 to Face2. This can be used to check if the faces are periodic 
        This function assumes the rotation axis is in the "x" direction. This is good for faces within the same block 

    Reference:
        - Linear Real Transforms from GlennHT https://gitlab.grc.nasa.gov/lte-turbo/GlennHT/-/blob/master/src/M_ccMBMesh.F See computeLRT
        
    Args:
        Face1 (Face): Face to rotate
        Face2 (Face): Face to rotate to

    Returns:
        (tuple): tuple containing:

            - **ang** (float): rotation angle
            - **rotation_matrix** (numpy.ndarray): Rotation matrix 3x3
        
    """

    cTo3,cTo1 = face1.get_corners() 
    cFrom3,cFrom1 = face2.get_corners()

    dTo  = np.array(cTo3).transpose() - np.array(cTo1).transpose()                      # difference in corner points = diagonal vector for Face 1
    ldTo=np.sqrt(np.sum(dTo*dTo))
    if ldTo > 0:
        dTo=dTo/ldTo
    
    dFrom = np.array(cFrom3).transpose() - np.array(cFrom1).transpose()                 # difference in corner points = diagonal vector for Face 2
    ldFrom = np.sqrt(np.sum(dFrom*dFrom))
    if( ldFrom > 0 ):
        dFrom=dFrom/ldFrom
    
    dotprod = np.sum(dTo * dFrom)
    
    if( abs(dotprod-1) < 1E-10 ): # Case of no rotation
        ang = 0

        rotation_matrix  = np.zeros(shape=(3,3))
    else:
        #Compute the angle of rotation  
        cosAng=(dTo[1]*dFrom[1]+dTo[2]*dFrom[2])/sqrt(dTo[1]*dTo[1]+dTo[2]*dTo[2])/sqrt(dFrom[1]*dFrom[1]+dFrom[2]*dFrom[2])
        sinAng=(dTo[2]*dFrom[1]-dTo[1]*dFrom[2])/sqrt(dTo[1]*dTo[1]+dTo[2]*dTo[2])/sqrt(dFrom[1]*dFrom[1]+dFrom[2]*dFrom[2])
        ang=acos(cosAng)

        rotation_matrix = [ [1, 0, 0],
                            [0, cosAng, -sinAng],
                            [0, sinAng, cosAng] ]
        if( sinAng < 0 ):
            ang*=-1
    return ang, rotation_matrix

def __periodicity_check__(face1:Face, face2:Face,block1:Block,block2:Block,tol:float=1E-6):
    """General function to find periodicity within a given block. 
    
    Steps:
        - 1: Take the face with the shorter diagonal. 
        - 2: Rotate the shorter face by angle 360/nblades.  
        - 3: Check to see if faces intersect

    Args:
        face1 (Face): An arbitrary face 
        face2 (Face): An arbitrary face 
        block1 (Block): block 1 cooresponding to face 1
        block2 (Block): block 2 cooresponding to face 2 

    Returns:
        (tuple): containing

            - **df** (pandas.Dataframe): List of point matches for periodic surfaces 
            - **periodic_surface** (List[Face]):  These are faces that are periodic 
            - **split_surfaces** (List[Face]): Some blocks may have periodic faces with other blocks. But the faces may need to be split so say you pair a small face with a larger face. The split surfaces should be treated as an outer face  

    """
    
    periodic_faces = list()
    split_faces = list()
    swapped = False
    if (face2.diagonal_length < face1.diagonal_length): # switch so that face 2 is always longer
        temp = deepcopy(face1)
        face1 = deepcopy(face2)
        face2 = temp

        temp_block = deepcopy(block1)
        block1 = deepcopy(block2)
        block2 = temp_block        
        swapped = True
    
    df,split_face1,split_face2 = get_face_intersection(face1,face2,block1,block2,tol)

    if len(df)>=4:
        f1 = create_face_from_diagonals(block1,imin=df['i1'].min(),jmin=df['j1'].min(),kmin=df['k1'].min(), imax=df['i1'].max(),jmax=df['j1'].max(),kmax=df['k1'].max())
        f1.set_block_index(face1.blockIndex)
        f1.set_face_id(face1.id)

        f2 = create_face_from_diagonals(block2,imin=df['i2'].min(),jmin=df['j2'].min(),kmin=df['k2'].min(), imax=df['i2'].max(),jmax=df['j2'].max(),kmax=df['k2'].max())
        f2.set_block_index(face2.blockIndex)
        f2.set_face_id(face2.id)
        
        split_faces.extend(split_face1)
        split_faces.extend(split_face2)
        if swapped:
            periodic_faces.append(f2)
            periodic_faces.append(f1)
        else:
            periodic_faces.append(f1)
            periodic_faces.append(f2)

    return df,periodic_faces,split_faces


