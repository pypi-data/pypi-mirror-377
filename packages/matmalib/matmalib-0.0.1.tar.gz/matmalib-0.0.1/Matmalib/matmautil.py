import numpy as np
import os
import sys
import math

class Measure():

    @staticmethod
    def get_distance(atom_list):

       at1 = atom_list[0]
       at2 = atom_list[1]

       dist = 0
       for dim in range(2):
           dist += (at1.coord[dim]-at2.coord[dim])**2

       return math.sqrt(dist)

    @staticmethod
    def get_angle(atom_list):

        at1 = atom_list[0]
        at2 = atom_list[1]
        at3 = atom_list[2]

        r1 = [x-y for x,y in zip(at1.coord,at2.coord)]
        r2 = [x-y for x,y in zip(at3.coord,at3.coord)]

        norm1 = Measure.get_distance([at1,at2])
        norm2 = Measure.get_distance([at2,at3])

        norm = norm1*norm2
        dot = np.dot(r1,r2)/norm
        angle = math.acos(dot)
        axor = np.cross(r1,r2)

        return angle*180/np.pi, axor

    @staticmethod
    def get_dihedral(atom_list):

        at1 = atom_list[0]
        at2 = atom_list[1]
        at3 = atom_list[2]
        at4 = atom_list[3]

        r1 = [x-y for x,y in zip(at1.coord,at2.coord)]
        r2 = [x-y for x,y in zip(at2.coord,at3.coord)]
        r3 = [x-y for x,y in zip(at3.coord,at4.coord)]

        p1 = np.cross(r1,r2)
        p2 = np.cross(r2,r3)

        axor = np.cross(p1,p2)

        norm_p1 = np.sqrt(np.sum(p1**2))
        norm_p2 = np.sqrt(np.sum(p2**2))

        norm = norm_p1*norm_p2
        dot = np.clip(np.dot(p1,p2)/norm,-0.999999999,0.999999999)
        angle = math.acos(dot)

        ppoint = -np.dot(p1,at1.coord)
        dpoint = np.dot(p1,at4.coord) + ppoint/norm_p1

        if dpoint >= 0:
            return -(angle*180/np.pi)
        else:
            return angle*180/np.pi

    @staticmethod
    def measure(atom_list):

        if len(atom_list) == 2:
            return Measure.get_distance(atom_list)
        elif len(atom_list) == 3:
            return Measure.get_angle(atom_list)
        elif len(atom_list) == 4:
            return Measure.get_dihedral(atom_list)