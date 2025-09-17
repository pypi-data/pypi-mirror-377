Installation
============

.. _prerequisits:

Prerequisits
------------

This toolkit requires the following Python packages.

- paramiko, a networking package to run a local service the I/O library can talk to to establish a remote connection
- pyyaml, parsing yaml configuration files
- PyNaCl for encoding metadata with keys
- pillow for processing images
- h5py for adding HDF5 files
- redis for *hpc_campaign_cache* to list local cache information (Redis is used by ADIOS2 for caching)

Besides these packages, Python needs support for Tcl/Tk (python3-tk), so that *hpc_campaign_connector* can pop up a dialog for password entries.

How to install
--------------

HPC Campaign Management is just a bunch of Python scripts that can be installed in your Python environment, or can just be accessed by setting PYTHONPATH.

.. code-block:: console

    (.venv) $ git clone https://github.com/ornladios/hpc-campaign.git
    (.venv) $ cd hpc-campaign
    (.venv) $ pip3 install -e .
    (.venv) $ hpc_campaign_list

or

.. code-block:: bash

    $ git clone https://github.com/ornladios/hpc-campaign.git
    $ cd hpc-campaign
    $ export PYTHONPATH=${PWD}/source:$PYTHONPATH
    $ python3 -m hpc_campaign_list


Setup 
-----

~/.config/adios2/adios2.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are three paths/names important in the campaign setup. 

- `hostname` is used in the campaign archive. Define a specific name the project agrees upon (e.g. OLCF, NERSC, ALCF) that identifies the generic location of the data and then use that name later to specify the modes of remote data access.

- `campaignstorepath` is the directory where all the campaign archives are stored. This should be shared between project members in a center, and a private one on every member's laptop. It is up to the project to determine what file sharing / synchronization mechanism to use to sync this directories. 

- `cachepath` is the directory where ADIOS can unpack metadata from the campaign archive so that ADIOS engines can read them as if they were entirely local datasets. The cache contains the metadata as well as data that have already been retrieved by previous read requests. 

Use `~/.config/adios2/adios2.yaml` to specify these options. 

.. code-block:: bash
		
    $ cat ~/.config/adios2/adios2.yaml

    Campaign:
      hostname: OLCF
      campaignstorepath: /lustre/orion/csc143/proj-shared/campaign-store
      cachepath: /lustre/orion/csc143/proj-shared/campaign-cache
      verbose: 0

    $ ls -R /lustre/orion/csc143/proj-shared/campaign-store
    /lustre/orion/csc143/proj-shared/campaign-store/demoproject:
    frontier_gray-scott_100.aca

    $ python3 -m hpc_campaign_list
    demoproject/frontier_gray-scott_100.aca

~/.config/adios2/hosts.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ cat ~/.config/adios2/hosts.yaml

    OLCF:
        dtn-ssh:
            protocol: ssh
            host: dtn.olcf.ornl.gov
            user: user007
            authentication: passcode
            serverpath: ~/dtn/sw/adios2/bin/adios2_remote_server -background -report_port_selection -v -v -l /ccs/home/user007/dtn/log.adios2_remote_server -t 16
            verbose: 1

        NERSC:
        dtn-ssh:
            protocol: ssh
            host: dtn.nersc.gov
            user: user007
            authentication: publickey
            identity_file: ~/.ssh/nersc
            serverpath: ~/adios/master/dtn/bin/adios2_remote_server -background -report_port_selection -v -v -l /global/homes/u/user007/dtn/log.adios2_remote_server -t 16
            verbose: 1