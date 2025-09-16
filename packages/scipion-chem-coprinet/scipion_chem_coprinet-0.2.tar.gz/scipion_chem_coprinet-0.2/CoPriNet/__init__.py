# **************************************************************************
# *
# * Authors: Verónica Gamo (veronica.gamoparejo@usp.ceu.es)
# *
# * Biocomputing Unit, CNB-CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

# Scipion em imports
import os, subprocess
from subprocess import run
from scipion.install.funcs import InstallHelper

# Scipion chem imports
import pwchem

# Plugin imports
from .constants import PLUGIN_VERSION, COPRINET_DIC

_version_ = PLUGIN_VERSION
_logo = ""
_references = ['']


class Plugin(pwchem.Plugin):
    @classmethod
    def _defineVariables(cls):
        """ Return and write a variable in the config file. """
        cls._defineEmVar(
            COPRINET_DIC['home'],
            '{}-{}'.format(COPRINET_DIC['name'], COPRINET_DIC['version'])
        )

    @classmethod
    def defineBinaries(cls, env):
        """ Install the necessary packages. """
        cls.addCoPriNetEnv(env)

    ########################### PACKAGE FUNCTIONS ###########################

    @classmethod
    def addCoPriNetEnv(cls, env, default=True):
        """Create the CoPriNet38 conda environment with all dependencies."""
        installer = InstallHelper(
            'CoPriNet',
            packageHome=cls.getVar(COPRINET_DIC['home']),
            packageVersion=COPRINET_DIC['version']
        )

        # Commands to build the environment
        installer.addCommand(
            "conda create -y -n CoPriNet38 python=3.8"
        ).addCommand(
            "conda run -n CoPriNet38 pip install torch torchvision torchaudio"
        ).addCommand(
            "conda run -n CoPriNet38 pip install torch_geometric pytorch_lightning"
        ).addCommand(
            "conda run -n CoPriNet38 pip install pandas more-itertools"
        ).addCommand(
            "conda run -n CoPriNet38 conda install -y -c conda-forge rdkit"
        ).addPackage(env, dependencies=['conda'], default=default)

    @classmethod
    def runCoPriNet(cls, program, args, cwd=None):
        """ Run CoPriNet command from a given protocol. """
        activation_command = '{}conda activate {}'.format(
            cls.getCondaActivationCmd(), "CoPriNet38"
        )
        dir = os.path.join(cls.getVar(COPRINET_DIC['home']), "CoPriNet")
        full_program = f'{activation_command} && cd {dir} && {program} {args}'
        run(full_program, env=cls.getEnviron(), cwd=cwd, shell=True)
