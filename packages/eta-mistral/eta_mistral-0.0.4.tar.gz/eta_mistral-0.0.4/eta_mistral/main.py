"""
This file starts the frontend and backend of ETA-MISTRAL.
"""

__author__ = ["Michael Frank (MFr)", "Lukas Theisinger (LT)", "Fabian Borst (FBo)", "Borys Ioshchikhes (BI)"]
__maintainer__ = "Michael Frank (MFr)"
__email__ = "m.frank@ptw.tu-darmstadt.de"
__project__ = "MISTRAL FKZ: 03EN4098A-E "
__subject__ = "Cluster 2: Software solution"
__version__ = "0.0.1"
__status__ = "Work in progress"

from eta_mistral.frontend.cli_app import CommandLineApplication

if __name__ == "__main__":
    APP = CommandLineApplication()
    APP.run()
