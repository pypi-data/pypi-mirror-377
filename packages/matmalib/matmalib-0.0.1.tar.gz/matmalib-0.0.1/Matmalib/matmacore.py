from time import sleep

import numpy as np
import os
import sys
import networkx as nx
import re
from matmautil import *

class Atom():

    def __init__(self, coord:list = None, type:str = None, valence:int = None, index:int = None):
        self.coord = None
        self.type = None
        self.atomic_num = None
        self.valence = None
        self.index = None

        if self.coord is not None:
            self.x = self.coord[0]
            self.y = self.coord[1]
            self.z = self.coord[2]

    def set_coord (self, coord:list):
        self.coord = coord

    def set_type (self, type:str):
        self.type = type

    def set_atomic_num (self, atomic_num:int):
        self.atomic_num = atomic_num

    def set_valence (self, valence:int):
        self.valence = valence

    def set_index (self, index:int):
        self.index = index

class Mol():

    def __init__(self):
        self.atoms = None
        self.graph = None
        self.path = None
        self.conn_mat = None
        self.xyz

    def element_symbol(A):

        """ A dictionary for atomic number and atomic symbol
        :param A: either atomic number or atomic symbol for Hydrogen, Carbon, Nitrogen, Oxygen, Fluorine and Silicon
        :return: the corresponding atomic symbol or atomic number
        """

        periodic_table = {'1': 'H', '2': 'He',
                          '3': 'Li', '4': 'Be', '5': 'B', '6': 'C', '7': 'N', '8': 'O', '9': 'F', '10': 'Ne',
                          '11': 'Na', '12': 'Mg', '13': 'Al', '14': 'Si', '15': 'P', '16': 'S', '17': 'Cl', '18': 'Ar',
                          '19': 'K', '20': 'Ca', '35': 'Br'
                          }
        return periodic_table[A]

    def get_atoms(self):
        xyz_list = self.xyz
        type_list = self.type_list

        atom_list = []

        index = 0
        for xyz, type in zip(xyz_list, type_list):
            atom = Atom(coord=xyz, type=type, index=index)
            atom_list.append(atom)

        self.atoms = atom_list
        return atom_list

    def gaussian(self):

        """
        Parses log files from Gaussian 16 and appends information inside the log file to the mol object.

        """

        flags = {'freq_flag': False, 'nmr_flag': False, 'opt_flag': False, 'jcoup_flag': False, 'normal_mode': False,
                 'read_geom': False}
        job_type = None

        # temprorary variables to hold the data
        freq = [];
        ints = [];
        vibs = [];
        geom = [];
        atoms = [];
        nmr = []
        self.NAtoms = None

        for line in open(self.path, 'r').readlines():

            if not job_type and re.search('^ #', line):

                if "opt" in line:
                    if "freq" in line:
                        job_type = 'optfreq'
                    else:
                        job_type = 'opt'
                elif "freq" in line:
                    if "opt" in line:
                        job_type = 'optfreq'
                    else:
                        job_type = 'freq'
                        flags["freq_flag"] = True
                elif "nmr" in line:
                    job_type = 'nmr'
                else:
                    job_type = 'sp'

            if self.NAtoms is None and re.search('^ NAtoms=', line):
                self.NAtoms = int(line.split()[1])

            if job_type == 'optfreq' or job_type == "freq":

                if flags['freq_flag'] == False and re.search('Normal termination', line): flags['freq_flag'] = True
                # We skip the opt part of optfreq job, all info is in the freq part

                if flags['freq_flag'] == True:

                    if re.search('SCF Done', line):
                        self.E = float(line.split()[4])
                    elif re.search('Sum of electronic and zero-point Energies', line):
                        self.Ezpe = float(line.split()[6])
                    elif re.search('Sum of electronic and thermal Enthalpies', line):
                        self.H = float(line.split()[6])
                    elif re.search('Sum of electronic and thermal Free Energies', line):
                        self.F = float(line.split()[7])

                    elif re.search('Coordinates', line) and len(geom) == 0:
                        flags['read_geom'] = True

                    elif flags['read_geom'] == True and re.search('^\s*.\d', line):
                        geom.append([float(x) for x in line.split()[3:6]])
                        atoms.append(Mol.element_symbol(line.split()[1]))
                        if int(line.split()[0]) == self.NAtoms:
                            flags['read_geom'] = False

                    elif re.search(' Deg. of freedom', line):
                        self.NVibs = int(line.split()[3])

                    elif re.search('^ Frequencies', line):
                        freq_line = line.strip()
                        for f in freq_line.split()[2:5]: freq.append(float(f))
                        flags['normal_mode'] = False

                    elif re.search('^ IR Inten', line):
                        ir_line = line.strip()
                        for i in ir_line.split()[3:6]: ints.append(float(i))

                    elif re.search('^  Atom  AN', line):
                        flags['normal_mode'] = True  # locating normal modes of a frequency
                        mode_1 = [];
                        mode_2 = [];
                        mode_3 = [];
                        # continue

                    elif flags['normal_mode'] == True and re.search('^\s*\d*\s*.\d*', line) and len(line.split()) > 3:
                        mode_1.append([float(x) for x in line.split()[2:5]])
                        mode_2.append([float(x) for x in line.split()[5:8]])
                        mode_3.append([float(x) for x in line.split()[8:11]])

                    elif flags['normal_mode'] == True:
                        flags['normal_mode'] = False
                        for m in [mode_1, mode_2, mode_3]: vibs.append(np.array(m))

            elif job_type == 'opt':

                if re.search('SCF Done', line): E = float(line.split()[4])
                if re.search('Optimization completed.', line):
                    self.E = E;
                    flags['opt_flag'] = True
                if flags['opt_flag'] == True:
                    if re.search('Standard orientation:', line):
                        flags['read_geom'] = True

                    elif flags['read_geom'] == True and re.search('^\s*.\d', line):
                        geom.append([float(x) for x in line.split()[3:6]])
                        atoms.append(Mol.element_symbol(line.split()[1]))
                        if int(line.split()[0]) == self.NAtoms:
                            flags['read_geom'] = False

            elif job_type == 'nmr':

                if re.search('SCF Done', line):
                    self.E = float(line.split()[4])
                elif re.search('Coordinates', line) and len(geom) == 0:
                    flags['read_geom'] = True

                elif flags['read_geom'] == True and re.search('^\s*.\d', line):
                    geom.append([float(x) for x in line.split()[3:6]])
                    atoms.append(Mol.element_symbol(line.split()[1]))
                    if int(line.split()[0]) == self.NAtoms:
                        flags['read_geom'] = False

                elif re.search('Total nuclear spin-spin coupling J', line):
                    spin = [[] for i in range(self.NAtoms)]
                    flags['jcoup_flag'] = True

                elif flags['jcoup_flag'] == True and re.search('-?\d\.\d+[Dd][+\-]\d\d?', line):
                    for x in line.split()[1:]:
                        spin[int(line.split()[0]) - 1].append(float(x.replace('D', 'E')))

                elif flags['jcoup_flag'] == True and re.search('End of Minotr F.D. properties file', line):
                    flags['jcoup_flag'] = False

            elif job_type == 'sp':

                if re.search('SCF Done', line):
                    self.E = float(line.split()[4])
                elif re.search('Standard orientation:', line):
                    flags['read_geom'] = True
                elif flags['read_geom'] == True and re.search('^\s*.\d', line):
                    geom.append([float(x) for x in line.split()[3:6]])
                    atoms.append(Mol.element_symbol(line.split()[1]))
                    if int(line.split()[0]) == self.NAtoms:
                        flags['read_geom'] = False

        # postprocessing:
        if job_type == 'freq' or job_type == 'optfreq':
            self.Freq = np.array(freq)
            self.Ints = np.array(ints)
            self.Vibs = np.zeros((self.NVibs, self.NAtoms, 3))
            for i in range(self.NVibs): self.Vibs[i, :, :] = vibs[i]

        if job_type == 'nmr':
            for at in spin:
                while len(at) < self.NAtoms: at.append(0)
            self.nmr = np.tril(spin)

        self.xyz = np.array(geom)
        self.type_list = atoms
        self.get_atoms()

    def connectivity_matrix(self, distXX=1.65, distXH=1.15):

        """ Creates a connectivity matrix of the molecule. A connectivity matrix holds the information of which atoms are bonded and to what.

        :param distXX: The max distance between two atoms (not hydrogen) to be considered a bond
        :param distXH: The max distance between any atom and a hydrogen atom to be considered a bond
        """

        Nat = self.NAtoms
        self.conn_mat = np.zeros((Nat, Nat))

        for at1 in self.atoms:
            for at2 in self.atoms:

                dist = Measure.get_distance([at1,at2])

                if at1 == at2:
                    pass

                elif (at1.type == 'H' or at2.type == 'H') and dist < distXH:
                    self.conn_mat[at1.index, at2.index] = 1;
                    self.conn_mat[at2.index, at1.index] = 1
                elif (at1.type != 'H' and at2.type != 'H') and dist < distXX:
                    self.conn_mat[at1.index, at2.index] = 1;
                    self.conn_mat[at2.index, at1.index] = 1

        # Remove bifurcated Hs:
        for at1 in self.get_atoms():
            if at1.type == 'H' and np.sum(self.conn_mat[at1.index, :]) > 1:

                at2list = np.where(self.conn_mat[at1.index, :] == 1)
                at2list = at2list[0].tolist()

                at2dist = [round(Measure.get_distance([at1, self.atoms[at2x]]), 3) for at2x in at2list]
                for at, dist in zip(at2list, at2dist):
                    if self.atoms[at].type == 'H':
                        at2list.remove(at)
                        at2dist.remove(dist)

                at2 = at2list[at2dist.index(min(at2dist))]
                for at2x in at2list:
                    if at2x != at2:
                        print('remove', self._id, at2x, at1, at2)
                        self.conn_mat[at1.index, at2x] = 0;
                        self.conn_mat[at2x, at1.index] = 0

        graph = nx.graph.Graph(self.conn_mat)
        self.Nmols = nx.number_connected_components(graph)
        self.graph = graph

    def cp2k(self):

        """ Parses information from CP2K. Right now only works for AIMD Trajectories, plan to implement opt compatability later.

        :param job_type: (string) Currently only md is supported. Should be manually specified.
        :param colvar: (list) A list containing the atom numbers that define your collective variable.
        :param timestep: (float) Timestep of your MD calculation. The function will attempt to extract this from your input file if present.
        :param traj_file: (string) File containing the CP2K trajectory.
        :param input_file: (string) File containing your CP2K inputs.
        :param output_file: (string) File containing your CP2K output.
        """

        with open(self.path, 'r') as geom:
            first_line = geom.readline()
            NAtoms = int(first_line.split()[0])

            raw_coords = geom.readlines()[-NAtoms:]

            coords = np.array([line.split()[1:] for line in raw_coords], dtype=float)
            types = np.array([line.split()[0] for line in raw_coords])

            geom.close()

        self.NAtoms = NAtoms
        self.xyz = coords
        self.type_list = types

        self.get_atoms()

    def orca(self, output_file="input.log", job_type="opt"):

        """ Parses information from ORCA input.log file
        :param output_file: (string) File containing ORCA output file.
        :param job_type: (string) The type of calculation ORCA run.
        """

        with open("/".join([self.path, output_file]), "r") as f:
            for line in f:
                if "Geometry Optimization Run" in line:
                    output_file = "input.orca.xyz"

                    with open("/".join([self.path, output_file]), "r") as f2:
                        first_line = f2.readline()
                        Natoms = int(first_line.split()[0])

                        second_line = f2.readlines()[0:1]
                        energy = np.array([i.split()[-1] for i in second_line], dtype=float)

                        raw_coords = f2.readlines()[-Natoms:]

                        coords = np.array([line.split()[1:] for line in raw_coords], dtype=float)
                        atoms = np.array([line.split()[0] for line in raw_coords])

                    self.Natoms = Natoms
                    self.xyz = coords
                    self.type_list = atoms
                    self.energy = energy
                    self.get_atoms()

                elif "Single Point Calculation" and "FINAL SINGLE POINT ENERGY" in line:
                    # print(line.split()[-1])
                    job_type = "sp"
                    energy = np.array(line.split()[-1], dtype=float)
                    print(self.energy)

                else:
                    print("Unable to read ORCA log file")

class Data ():

    def __init__(self):

        self.data = None

    def csv(self, skiprows=1, dtype=float, delimiter: str = ','):
        """
        Parses a csv file and appends the data to the mol object

        :param file: (string) File containing the csv data.
        :param skiprows: (int) Number of rows to skip
        :param dtype: (type) Data type
        :param delimiter: (str) Delimiter
        """

        self.data = np.loadtxt(self.path, skiprows=skiprows, dtype=dtype, delimiter=delimiter)

    def gromacs(self):
        """ Parses information from gromacs *.xvg file

        :param file: (string) File containing the gromacs data.
        """

        # I don't use Gromacs enough to know how the output looks like. Right now, I am just reading the .xvg file:

        if re.search('.xvg', self.path):

            with open(self.path, 'r') as f:
                i = 0
                for line in f.readlines():
                    if re.search('#', line) or re.search('@', line):
                        i = i + 1

                    if re.search('Time', line):
                        time_unit = line.split()[-1].strip('()"')
                        self.time_unit = time_unit
                f.close()

            data = np.loadtxt(self.path, skiprows=i)

            self.data = data
            self.software = 'gromacs'

        if re.search('.xpm', self.path):

            f = open(self.path, 'r')
            pattern = None;
            matrix_lett = [];
            matrix_dict = {}
            grid = None
            for line in f.readlines():

                if re.search(r'(\d\s\d\b)', line) and grid is None:
                    grid = int(line.split()[1])
                    pattern = grid * '[A-Z]'

                if pattern and re.search(pattern, line):
                    replL1 = line.replace('",', '')
                    replL2 = line.replace('"', '')
                    matrix_lett.append('\n'.join(replL2.split()))

                if re.search('((".*")[0-9])', line):
                    replL1 = line.replace('"', ' ')
                    letters, energy = values = str(replL1.split()[0]), float(replL1.split()[4])
                    matrix_dict.update(dict.fromkeys(letters, energy))

            matrix = np.zeros([grid, grid])
            for i in range(grid):
                for j in range(grid):
                    matrix[grid - i - 1, j] = matrix_dict[matrix_lett[i][j]]

            self.data = matrix
            self.software = 'gromacs'

    def cp2k(self, colvar = None, timestep = None):

        self.time_unit = 'fs'  # Default unit in CP2K
        self.software = 'cp2k'

        if re.search('.xyz', self.path):
            # Reads colvars straight from the xyz file. Requires specification of timestep and colvar coordinate.

            if colvar == None:
                raise ValueError('Error: Specify the atoms for your collective variables.')

            if timestep == None:
                raise ValueError('Error: Specify timestep for reading CP2K trajectories.')

            xyz_array = []

            with open(self.path, 'r') as geom:
                line_1 = geom.readline()
                self.Natoms = int(line_1.split()[0])

                for line in geom.readlines():



            colvar_data = Measure.measure(self.path, colvar)
            time = [i / (1 / timestep) for i in range(len(colvar_data))]

            data = np.array(list(zip(time, colvar_data)))
            self.data = data

        elif re.search('.metadynLog', self.path):
            # Reads colvars from the metadynLog file.

            data = np.loadtxt(self.path)
            self.data = data