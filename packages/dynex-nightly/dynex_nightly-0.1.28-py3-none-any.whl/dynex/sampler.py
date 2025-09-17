"""
Dynex SDK (beta) Neuromorphic Computing Library
Copyright (c) 2021-2025, Dynex Developers

All rights reserved.

1. Redistributions of source code must retain the above copyright notice, this list of
    conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list
   of conditions and the following disclaimer in the documentation and/or other
   materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be
   used to endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import ast
import multiprocessing
import zlib
import subprocess
import os
import sys
import time
import secrets
import neal

import json
from sympy.physics.pring import energy

from tqdm.notebook import tqdm
from ftplib import FTP
import dimod
import numpy as np
from IPython.core.display_functions import clear_output
from tabulate import tabulate

from dynex.config import DynexConfig
from dynex.models import BQM
from dynex.api import DynexAPI


def to_wcnf_string(clauses, num_variables, num_clauses):
    """
    `Internal Function`

    Saves the model as an string
    """

    line = "p wcnf %d %d\n" % (num_variables, num_clauses)
    for clause in clauses:
        line += ' '.join(str(int(lit)) for lit in clause) + ' 0\n'
    return line


################################################################################################################################
# Dynex Sampler (public class)
################################################################################################################################
class DynexSampler:
    """
    Initialises the sampler object given a model.

    :Parameters:

    - :logging: Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (`bool`)
    - :mainnet: Defines if the mainnet (Dynex platform sampling) or the testnet (local sampling) is being used for sampling (`bool`)
    - :description: Defines the description for the sampling, which is shown in Dynex job dashboards as well as in the market place  (`string`)

    :Returns:

    - class:`dynex.samper`

    :Example:

    .. code-block:: Python

        sampler = dynex.DynexSampler(model)

    """

    def __init__(self,
                 model,
                 logging=True,
                 description='Dynex SDK Job',
                 test=False,
                 bnb=True,
                 filename_override='',
                 config: DynexConfig = None):

        # multi-model parallel sampling

        if not config:
            config = DynexConfig()

        self.config = config
        self.logger = config.logger
        self.state = 'initialised'
        self.model = model
        self.logging = logging
        self.filename_override = filename_override
        self.description = description
        self.test = test
        self.dimod_assignments = {}
        self.bnb = bnb

    @staticmethod
    def _sample_thread(q, x, model, logging, logger, description, num_reads, annealing_time, switchfraction, alpha,
                       beta,
                       gamma, delta, epsilon, zeta, minimum_stepsize, block_fee, is_cluster, shots, cluster_type):
        """
        `Internal Function` which creates a thread for clone sampling
        """
        if logging:
            logger.info(f'[DYNEX] Clone {x} started...')
        _sampler = _DynexSampler(model, False, True, description, False)
        _sampleset = _sampler.sample(num_reads, annealing_time, switchfraction, alpha, beta, gamma, delta, epsilon,
                                     zeta,
                                     minimum_stepsize, False, block_fee, is_cluster, shots, cluster_type)
        if logging:
            logger.info(f'[DYNEX] Clone {x} finished')
        q.put(_sampleset)
        return

    def sample(self, num_reads=32, annealing_time=10, clones=1, switchfraction=0.0, alpha=20, beta=20, gamma=1, delta=1,
               epsilon=1, zeta=1, minimum_stepsize=0.05, debugging=False, block_fee=0, is_cluster=True, shots=1, rank=1,
               cluster_type=1, preprocess=False):
        """
        The main sampling function:

        :Parameters:

        - :num_reads: Defines the number of parallel samples to be performed (`int` value in the range of [32, MAX_NUM_READS] as defined in your license)

        - :annealing_time: Defines the number of integration steps for the sampling. Models are being converted into neuromorphic circuits, which are then simulated with ODE integration by the participating workers (`int` value in the range of [1, MAX_ANNEALING_TIME] as defined in your license)

        - :clones: Defines the number of clones being used for sampling. Default value is 1 which means that no clones are being sampled. Especially when all requested num_reads will fit on one worker, it is desired to also retrieve the optimum ground states found from more than just one worker. The number of clones runs the sampler for n clones in parallel and aggregates the samples. This ensures a broader spectrum of retrieved samples. Please note, it the number of clones is set higher than the number of available threads on your local machine, then the number of clones processed in parallel is being processed in batches. Clone sampling is only available when sampling on the mainnet. (`integer` value in the range of [1,128])

        - :switchfraction: Defines the percentage of variables which are replaced by random values during warm start samplings (`double` in the range of [0.0, 1.0])

        - :alpha: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :beta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :gamma: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :delta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :epsilon: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :zeta: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is using automatic tuning of these parameters for the ODE integration. Setting values defines the upper bound for the automated parameter tuning (`double` value in the range of [0.00000001, 100.0] for alpha and beta, and [0.0 and 1.0] for gamma, delta and epsilon)

        - :minimum_stepsize: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is performig adaptive stepsizes for each ODE integration forward Euler step. This value defines the smallest step size for a single adaptive integration step (`double` value in the range of [0.0000000000000001, 1.0])

        - :debugging: Only applicable for test-net sampling. Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (TRUE) (`bool`)

        - :bnb: Use alternative branch-and-bound sampling when in mainnet=False (`bool`)

        - :block_fee: Computing jobs on the Dynex platform are being prioritised by the block fee which is being offered for computation. If this parameter is not specified, the current average block fee on the platform is being charged. To set an individual block fee for the sampling, specify this parameter, which is the amount of DNX in nanoDNX (1 DNX = 1,000,000,000 nanoDNX)

        - :shots: Sets the minimum number of solutions to retrieve from the network. Works both on mainnet=False and mainnet=True (Default: 1). Typically used for situations where not only the best global optimum (sampleset.first) is required, but multiple optima from different workers.

        :Returns:

        - Returns a dimod sampleset object class:`dimod.sampleset`

        :Example:

        .. code-block::

            import dynex
            import dimod

            # Define the QUBU problem:
            bqmodel = dimod.BinaryQuadraticModel({0: -1, 1: -1}, {(0, 1): 2}, 0.0, dimod.BINARY)

            # Sample the problem:
            model = dynex.BQM(bqmodel)
            sampler = dynex.DynexSampler(model)
            sampleset = sampler.sample(num_reads=32, annealing_time = 100)

            # Output the result:
            print(sampleset)

        .. code-block::

            ╭────────────┬───────────┬───────────┬─────────┬─────┬─────────┬───────┬─────┬──────────┬──────────╮
            │   DYNEXJOB │   ELAPSED │   WORKERS │   CHIPS │   ✔ │   STEPS │   LOC │   ✔ │   ENERGY │        ✔ │
            ├────────────┼───────────┼───────────┼─────────┼─────┼─────────┼───────┼─────┼──────────┼──────────┤
            │       3617 │      0.07 │         1 │       0 │  32 │     100 │     0 │   1 │        0 │ 10000.00 │
            ╰────────────┴───────────┴───────────┴─────────┴─────┴─────────┴───────┴─────┴──────────┴──────────╯
            ╭─────────────────────────────┬───────────┬─────────┬───────┬──────────┬───────────┬───────────────┬──────────╮
            │                      WORKER │   VERSION │   CHIPS │   LOC │   ENERGY │   RUNTIME │   LAST UPDATE │   STATUS │
            ├─────────────────────────────┼───────────┼─────────┼───────┼──────────┼───────────┼───────────────┼──────────┤
            │ *** WAITING FOR WORKERS *** │           │         │       │          │           │               │          │
            ╰─────────────────────────────┴───────────┴─────────┴───────┴──────────┴───────────┴───────────────┴──────────╯
            [DYNEX] FINISHED READ AFTER 0.07 SECONDS
            [DYNEX] PARSING 1 VOLTAGE ASSIGNMENT FILES...
            progress: 100%
            1/1 [00:05<00:00, 5.14s/it]
            [DYNEX] SAMPLESET LOADED
            [DYNEX] MALLOB: JOB UPDATED: 3617 STATUS: 2
               0  1 energy num_oc.
            0  0  1   -1.0       1
            ['BINARY', 1 rows, 1 samples, 2 variables]
        """

        # assert parameters:
        if clones < 1:
            raise Exception("[DYNEX] ERROR: Value of clones must be in range [1,128]")
        if clones > 128:
            raise Exception("[DYNEX] ERROR: Value of clones must be in range [1,128]")
        if self.config.mainnet == False and clones > 1:
            raise Exception("[DYNEX] ERROR: Clone sampling is only supported on the mainnet")

        # sampling without clones: -------------------------------------------------------------------------------------------
        if clones == 1:
            _sampler = _DynexSampler(self.model, self.logging, self.config.mainnet, self.description, self.test,
                                     self.bnb,
                                     self.filename_override, self.config)
            _sampleset = _sampler.sample(
                num_reads=num_reads,
                annealing_time=annealing_time,
                switchfraction=switchfraction,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
                delta=delta,
                epsilon=epsilon,
                zeta=zeta,
                minimum_stepsize=minimum_stepsize,
                debugging=debugging,
                block_fee=block_fee,
                is_cluster=is_cluster,
                shots=shots,
                rank=rank,
                cluster_type=cluster_type,
                preprocess=preprocess
            )
            return _sampleset

        # sampling with clones: ----------------------------------------------------------------------------------------------
        else:
            supported_threads = multiprocessing.cpu_count()
            if clones > supported_threads:
                self.logger.info(
                    f'[DYNEX] WARNING: number of clones > CPU cores: clones: {clones} threads available: {supported_threads}')
            jobs = []
            results = []

            if self.logging:
                self.logger.info(f'[DYNEX] STARTING SAMPLING (, {clones}, CLONES )...')

            # define n samplers:
            for i in range(clones):
                q = multiprocessing.Queue()
                results.append(q)
                p = multiprocessing.Process(target=self._sample_thread, args=(
                    q, i, self.model, self.logging, self.logger, self.description, num_reads, annealing_time,
                    switchfraction, alpha, beta, gamma, delta, epsilon, zeta, minimum_stepsize, block_fee, is_cluster,
                    shots, cluster_type))
                jobs.append(p)
                p.start()

            # wait for samplers to finish:
            for job in jobs:
                job.join()

            # collect samples for each job:
            assignments_cum = []
            for result in results:
                assignments = result.get()
                assignments_cum.append(assignments)

            # accumulate and aggregate all results:
            r = None
            for assignment in assignments_cum:
                if len(assignment) > 0:
                    if r is None:
                        r = assignment
                    else:
                        r = dimod.concatenate((r, assignment))

            # aggregate samples:
            r = r.aggregate()

            self.dimod_assignments = r

            return r


################################################################################################################################
# Dynex Sampler class (private)
################################################################################################################################

class _DynexSampler:
    """
    `Internal Class` which is called by public class `DynexSampler`
    """
    num_retries: int = 10

    def __init__(self, model, logging=True, mainnet=True, description='Dynex SDK Job', test=False,
                 bnb=True, filename_override='', config: DynexConfig = None):

        if not test and not os.path.isfile('dynex.test'):
            raise Exception("CONFIGURATION TEST NOT COMPLETED. PLEASE RUN 'dynex.test()'")

        if model.type not in ['cnf', 'wcnf', 'qasm']:
            raise Exception("INCORRECT MODEL TYPE:", model.type)

        self.description = description
        self.config = config if config is not None else DynexConfig(mainnet=mainnet)
        self.api = DynexAPI(config=self.config, logging=logging)
        self.logger = self.config.logger
        # FTP data where miners submit results:
        self.solutionurl = f'ftp://{self.config.ftp_hostname}/'
        self.solutionuser = f'{self.config.ftp_username}:{self.config.ftp_password}'

        # local path where tmp files are stored
        # tmppath = Path("tmp/test.bin")
        # tmppath.parent.mkdir(exist_ok=True)
        # with open(tmppath, 'w') as f:
        #     f.write('0123456789ABCDEF')
        self.filepath = 'tmp/'
        self.filepath_full = os.getcwd() + '/tmp'

        # path to testnet
        self.solver_path = self.config.solver_path
        self.bnb = bnb

        # multi-model parallel sampling?
        multi_model_mode = False
        if isinstance(model, list) and not mainnet:
            if not mainnet:
                raise Exception("[ÐYNEX] ERROR: Multi model parallel sampling is only supported on mainnet")
            multi_model_mode = True

        self.multi_model_mode = multi_model_mode

        # single model sampling:
        if not multi_model_mode:
            # auto generated temp filename:
            if len(filename_override) > 0:
                if filename_override.endswith(".dnx"):
                    self.filename = filename_override
                else:
                    self.filename = filename_override + ".dnx"
            else:
                self.filename = secrets.token_hex(16) + ".dnx"

            self.logging = logging
            self.type_str = model.type_str
            self.wcnf_offset = model.wcnf_offset
            self.precision = model.precision

            if model.type == 'cnf':
                # convert to 3sat?
                if self._check_list_length(model.clauses):
                    # we need to convert to 3sat:
                    self.clauses = self.api.k_sat(model.clauses)
                else:
                    self.clauses = model.clauses
                self._save_cnf(self.clauses, self.filepath + self.filename)
                self.num_clauses = len(self.clauses)
                self.num_variables = max(max(abs(lit) for lit in clause) for clause in self.clauses)

            elif model.type == 'wcnf':
                if self.config.solver_version == 1:
                    self.clauses = model.clauses
                    self.num_variables = model.num_variables
                    self.num_clauses = model.num_clauses
                else:
                    self.num_variables = model.bqm.num_variables
                    self.num_clauses = len(model.bqm.to_qubo()[0])
                    self.clauses = model.bqm.to_qubo()
                self.var_mappings = model.var_mappings
                self.precision = model.precision
                self._save_wcnf(self.clauses, self.filepath + self.filename, self.num_variables, self.num_clauses,
                                self.var_mappings)

            elif model.type == 'qasm':
                self.clauses = [0, -9999999999]
                self.num_variables = None
                self.num_clauses = None
                self.var_mappings = None
                self.precision = None

            self.type = model.type
            self.assignments = {}
            self.dimod_assignments = {}
            self.bqm = model.bqm
            self.model = model

        # multi model sampling:
        else:
            _filename = []
            _type_str = []
            _clauses = []
            _num_clauses = []
            _num_variables = []
            _var_mappings = []
            _precision = []
            _type = []
            _assignments = []
            _dimod_assignments = []
            _bqm = []
            _model = []
            for m in model:
                _filename.append(secrets.token_hex(16) + ".dnx")
                _type_str.append(m.type)
                if m.type == 'cnf':
                    raise Exception(
                        "[ÐYNEX] ERROR: Multi model parallel sampling is currently not implemented for SAT")
                if m.type == 'wcnf':
                    if self.config.solver_version == 1:
                        _num_clauses.append(m.num_clauses)
                        _num_variables.append(m.num_variables)
                        _clauses.append(m.clauses)
                    else:
                        _num_variables.append(m.bqm.num_variables)
                        _num_clauses.append(len(m.bqm.to_qubo()[0]))
                        _clauses.append(m.bqm.to_qubo())
                    _var_mappings.append(m.var_mappings)
                    _precision.append(m.precision)
                    self._save_wcnf(_clauses[-1], self.filepath + _filename[-1], _num_variables[-1], _num_clauses[-1],
                                    _var_mappings[-1])
                _type.append(m.type)
                _assignments.append({})
                _dimod_assignments.append({})
                _bqm.append(m.bqm)
                _model.append(m)
            self.filename = _filename
            self.type_str = _type_str
            self.clauses = _clauses
            self.num_clauses = _num_clauses
            self.num_variables = _num_variables
            self.var_mappings = _var_mappings
            self.precision = _precision
            self.type = _type
            self.assignments = _assignments
            self.dimod_assignments = _dimod_assignments
            self.bqm = _bqm
            self.model = _model
            self.wcnf_offset = _model.wcnf_offset
            self.precision = _model.precision
            self.logging = logging

        if self.logging:
            self.logger.info("[DYNEX] SAMPLER INITIALISED")

    @staticmethod
    def _check_list_length(lst: list) -> bool:
        """
        `Internal Function`

        :Returns:
        - TRUE if the sat problem is k-Sat, FALSE if the problem is 3-sat or 2-sat (`bool`)
        """

        for sublist in lst:
            if isinstance(sublist, list) and len(sublist) > 3:
                return True
        return False

    @staticmethod
    def _save_cnf(clauses: list, filename: str) -> None:
        """
        `Internal Function`

        Saves the model as an encrypted .bin file locally in /tmp as defined in dynex.ini
        """

        num_variables = max(max(abs(lit) for lit in clause) for clause in clauses)
        num_clauses = len(clauses)

        with open(filename, 'w') as f:
            line = "p cnf %d %d" % (num_variables, num_clauses)

            line_enc = line
            f.write(line_enc + "\n")

            for clause in clauses:
                line = ' '.join(str(int(lit)) for lit in clause) + ' 0'
                line_enc = line
                f.write(line_enc + "\n")

    def _save_wcnf(self, clauses, filename, num_variables, num_clauses, var_mappings):
        """
        `Internal Function`

        Saves the model as an encrypted .bin file locally in /tmp as defined in dynex.ini
        """

        if self.config.solver_version == 1:
            with open(filename, 'w') as f:
                line = "p wcnf %d %d" % (num_variables, num_clauses)

                line_enc = line
                f.write(line_enc + "\n")

                for clause in clauses:
                    line = ' '.join(str(int(lit)) for lit in clause) + ' 0'

                    line_enc = line
                    f.write(line_enc + "\n")
        else:
            with open(filename, 'w') as f:
                line = "p qubo %d %d %f" % (num_variables, num_clauses, clauses[1])
                f.write(line + "\n")
                for (i, j), value in clauses[0].items():
                    if var_mappings:
                        i = next((k for k, v in var_mappings.items() if v == i), i)  # i if not mapped
                        j = next((k for k, v in var_mappings.items() if v == j), j)  # j if not mapped
                    line = "%d %d %f" % (i, j, value)
                    f.write(line + "\n")

    # deletes all assignment files on FTP
    def cleanup_ftp(self, files):
        """
        `Internal Function`

        This function is called on __exit__ of the sampler class or by sampler.clear().
        It ensures that submitted sample-files, which have not been parsed and used from the sampler, will be deleted on the FTP server.
        """

        if len(files) > 0:
            try:
                host = self.solutionurl[6:-1]
                username = self.solutionuser.split(":")[0]
                password = self.solutionuser.split(":")[1]
                directory = ""
                ftp = FTP(host)
                ftp.login(username, password)
                ftp.cwd(directory)
                for file in files:
                    ftp.delete(file)
                if self.logging:
                    self.logger.info("[ÐYNEX] FTP DATA CLEANED")
            except Exception as e:
                self.logger.error(f"[DYNEX] An error occurred while deleting file: {str(e)}")
                raise Exception("ERROR: An error occurred while deleting file")
            finally:
                ftp.quit()
        return

    # delete file from FTP server
    def delete_file_on_ftp(self, hostname, username, password, local_file_path, remote_directory, logging=True):
        """
        `Internal Function`

        Deletes a file on the FTP server as specified in dynex,ini
        """

        ftp = FTP(hostname)
        ftp.login(username, password)
        # Change to the remote directory
        ftp.cwd(remote_directory)
        ftp.delete(local_file_path.split("/")[-1])
        if logging:
            self.logger.info(f'[DYNEX] COMPUTING FILE {local_file_path.split("/")[-1]} REMOVED')
        return

    # upload file to ftp server
    def upload_file_to_ftp(self, hostname, username, password, local_file_path, remote_directory, logging=True):
        """
        `Internal Function`

        Submits a computation file (xxx.bin) to the FTP server as defined in dynex.ini

        :Returns:

        - Status if successful or failed (`bool`)
        """

        try:
            ftp = FTP(hostname)
            ftp.login(username, password)
            # Change to the remote directory
            ftp.cwd(remote_directory)

            # Open the local file in binary mode for reading
            with open(local_file_path, 'rb') as file:
                total = os.path.getsize(local_file_path)  # file size
                # sanity check:
                if total > 104857600:
                    self.logger.error("[ERROR] PROBLEM FILE TOO LARGE (MAX 104,857,600 BYTES)")
                    raise Exception('PROBLEM FILE TOO LARGE (MAX 104,857,600 BYTES)')

                # upload:
                if logging:
                    with tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024,
                              desc='file upload progress') as pbar:
                        def cb(data):
                            pbar.update(len(data))

                        # Upload the file to the FTP server
                        ftp.storbinary(f'STOR {local_file_path.split("/")[-1]}', file, 1024, cb)
                else:
                    # Upload the file to the FTP server
                    ftp.storbinary(f'STOR {local_file_path.split("/")[-1]}', file)

            if logging:
                self.logger.info(
                    f"[DYNEX] File '{local_file_path}' sent successfully to '{hostname}/{remote_directory}'")

        except Exception as e:
            self.logger.error(f"[DYNEX] An error occurred while sending the file: {str(e)}")
            raise Exception("ERROR: An error occurred while sending the file")
        finally:
            ftp.quit()
            return True

    # calculate ground state energy and numer of falsified softs from model ==========================================================
    def _energy(self, sample, mapping=True):
        """
        `Internal Function`

        Takes a model and dimod samples and calculates the energy and loc.

        Input:
        ======

        - dimod sample (dict) with mapping = True
          example: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0}

        or

        - assignments (list) with mapping = False (raw solution file)
          example: [1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, -1, -1]
        """
        # convert dimod sample to wcnf mapping:
        wcnf_vars = []
        if mapping:
            for v in sample:
                if v in self.model.var_mappings:
                    v_mapped = self.model.var_mappings[v]
                else:
                    v_mapped = v
                wcnf_vars.append(sample[v_mapped])
        # or convert solution file to 0/1:
        else:
            for v in sample:
                if v > 0:
                    wcnf_vars.append(1)
                else:
                    wcnf_vars.append(0)

        loc = 0
        energy = 0.0
        for clause in self.model.clauses:

            if len(clause) == 2:
                # 2-lit clause:
                w = clause[0]
                i = int(abs(clause[1]))
                i_dir = np.sign(clause[1])
                if i_dir == -1:
                    i_dir = 0
                i_assign = wcnf_vars[i - 1]
                if (i_dir != i_assign):
                    loc += 1
                    energy += w
            else:
                # 3-lit clause:
                w = clause[0]
                i = int(abs(clause[1]))
                i_dir = np.sign(clause[1])
                if i_dir == -1:
                    i_dir = 0
                i_assign = wcnf_vars[i - 1]
                j = int(abs(clause[2]))
                j_dir = np.sign(clause[2])
                if j_dir == -1:
                    j_dir = 0
                j_assign = wcnf_vars[j - 1]
                if (i_dir != i_assign) and (j_dir != j_assign):
                    loc += 1
                    energy += w

        return loc, energy

    def add_salt_local(self) -> str:
        """
        `Internal Function`

        Adds salt to new local solutions - ensuring multiple solutions with similar result
        """

        directory = self.filepath_full
        fn = self.filename + "."
        token = str()
        # search for current solution files:
        for filename in os.listdir(directory):
            if filename.startswith(fn):
                # check if salt already added:
                if filename.split('.')[-1].isnumeric():
                    token = secrets.token_hex(16)
                    os.rename(directory + '/' + filename, directory + '/' + filename + '.' + token)
        return token

        # list local available (downloaded) iles in /tmp =================================================================================

    def list_files_with_text_local(self):
        """
        `Internal Function`

        Scans the temporary directory for assignment files

        :Returns:

        - Returns a list of all assignment files (filenames) which are locally available in /tmp as specified in dynex.ini for the current sampler model (`list`)
        """

        directory = self.filepath_full
        fn = self.filename + "."
        # list to store files
        filtered_files = []

        # search for current solution files:
        for filename in os.listdir(directory):
            if filename.startswith(fn) and filename.endswith('model') == False:
                if os.path.getsize(directory + '/' + filename) > 0:
                    filtered_files.append(filename)

        return filtered_files

        # verify correctness of downloaded file (loc and energy) ==========================================================================

    def validate_file(self, file, debugging=False):
        """
        `Internal Function`

        Validates loc and energy provided in filename with voltages. File not matching will be deleted on FTP and locally.
        """

        # v2 has a different format
        if self.config.solver_version == 2:
            return True

        valid = False

        if self.type == 'cnf':
            return True

        # format: xxx.bin.32.1.0.0.000000
        # jobfile chips steps loc energy
        info = file[len(self.filename) + 1:]
        chips = int(info.split(".")[0])
        steps = int(info.split(".")[1])
        loc = int(info.split(".")[2])

        # energy can also be non decimal:
        if len(info.split(".")) > 4:
            energy = float(info.split(".")[3] + "." + info.split(".")[4])
        else:
            energy = float(info.split(".")[3])

        with open(self.filepath + file, 'r') as ffile:
            data = ffile.read()
            # enough data?
            if self.config.mainnet:
                if len(data) > 96:
                    wallet = data.split("\n")[0]
                    tmp = data.split("\n")[1]
                    voltages = tmp.split(", ")[:-1]
                else:
                    voltages = ['NaN']  # invalid file received
            else:  # test-net is not returning wallet
                voltages = data.split(", ")[:-1]

            # convert string voltages to list of floats:
            voltages = list(map(float, voltages))
            if debugging:
                self.logger.debug('DEBUG:')
                self.logger.debug(voltages)

            # valid result? ignore Nan values and other incorrect data
            if len(voltages) > 0 and voltages[0] != 'NaN' and self.num_variables == len(voltages):
                val_loc, val_energy = self._energy(voltages, mapping=False)

                # from later versions onwards, enforce also correctness of LOC (TBD):
                if energy == val_energy:
                    valid = True

                if debugging:
                    self.logger.debug('DEBUG:', self.filename, chips, steps, loc, energy, '=>', val_loc, val_energy,
                                      'valid?',
                                      valid)

            else:
                if debugging:
                    self.logger.debug('DEBUG:', self.filename, ' NaN or num_variables =', len(voltages), ' vs ',
                                      self.num_variables,
                                      'valid?', valid)

        return valid

    # list and download solution files ================================================================================================
    def download_and_validate(self, ftp, name, local_path, max_attempts=3):
        """Вспомогательная функция для загрузки и валидации файла"""
        for attempt in range(max_attempts):
            try:
                with open(local_path, 'wb') as file:
                    if self.logging and attempt > 0:
                        self.logger.info(f'[DYNEX] Попытка {attempt + 1}: Загрузка файла {name}')
                    ftp.retrbinary(f'RETR {name}', file.write)

                if os.path.getsize(local_path) > 0 and self.validate_file(name, self.logging):
                    self.cnt_solutions += 1
                    return True

                if self.logging:
                    self.logger.info(f'[DYNEX] Удаление файла {name} (некорректная энергия или напряжение)')
                os.remove(local_path)
                self.api.report_invalid(filename=name, reason='wrong energy reported')

            except Exception as e:
                if self.logging:
                    self.logger.error(f'[DYNEX] Ошибка при загрузке {name}: {str(e)}')
                if attempt == max_attempts - 1:
                    raise
                time.sleep(1)  # Короткая пауза перед повторной попыткой
        return False

    def list_files_with_text(self):
        """
        `Internal Function`

        Downloads assignment files from the FTP server specified in dynex.ini and stores them in /tmp as specified in dynex.ini
        Downloaded files are automatically deleted on the FTP server.

        :Returns:

        - List of locally in /tmp saved assignment files for the current sampler model (`list`)
        """

        try:
            host = self.solutionurl[6:-1]
            target_size = 97 + self.num_variables

            with FTP(host) as ftp:
                ftp.login(user=self.config.ftp_username, passwd=self.config.ftp_password)
                ftp.cwd("")  # Корневая директория

                # Используем списковое включение для фильтрации файлов
                valid_files = [
                    (name, facts) for name, facts in ftp.mlsd()
                    if 'size' in facts
                       and int(facts['size']) >= target_size
                       and name.startswith(self.filename)
                ]

                for name, _ in valid_files:
                    local_path = os.path.join(self.filepath, name)

                    # Пропускаем существующие валидные файлы
                    if os.path.isfile(local_path) and os.path.getsize(local_path) > 0:
                        continue

                    if self.download_and_validate(ftp, name, local_path):
                        ftp.delete(name)

        except Exception as e:
            if self.logging:
                self.logger.error(f'[DYNEX] Ошибка FTP: {str(e)}')
            raise

    # clean function ======================================================================================================================
    def _clean(self):
        """
        `Internal Function`
        This function can be called after finishing a sampling process on the Mainnet. It ensures that submitted sample-files,
        which have not been parsed and used from the sampler, will be deleted on the FTP server. It is also called automatically
        during __exit___ event of the sampler class.
        """
        if self.config.mainnet:
            files = self.list_files_with_text_local()
            self.cleanup_ftp(files)

    # on exit ==============================================================================================================================
    def __exit__(self, exc_type, exc_value, traceback):
        """
        `Internal Function`
        Upon __exit__, the function clean() is being called.
        """
        self.logger.info('[DYNEX] SAMPLER EXIT')

    # update function: =====================================================================================================================
    def _update(self, model, logging=True):
        """
        `Internal Function`
        Typically, the sampler object is being initialised with a defined model class. This model can also be updated without
        regenerating a new sampler object by calling the function update(model).
        """
        self.logging = logging
        self.filename = secrets.token_hex(16) + ".bin"

        if model.type == 'cnf':
            # convert to 3sat?
            if self._check_list_length(model.clauses):
                self.clauses = self.api.d(model.clauses)
            else:
                self.clauses = model.clauses
            self._save_cnf(self.clauses, self.filepath + self.filename)

        if model.type == 'wcnf':
            if self.config.solver_version == 1:
                self.clauses = model.clauses
                self.num_variables = model.num_variables
                self.num_clauses = model.num_clauses
            else:
                self.num_variables = model.bqm.num_variables
                self.num_clauses = len(model.bqm.to_qubo()[0])
                self.clauses = model.to_qubo()
            self.var_mappings = model.var_mappings
            self.precision = model.precision
            self._save_wcnf(self.clauses, self.filepath + self.filename, self.num_variables, self.num_clauses)

        self.type = model.type
        self.assignments = {}
        self.dimod_assignments = {}
        self.bqm = model.bqm

    def delete_local_files_by_prefix(self, directory: str, prefix: str):
        for filename in os.listdir(directory):
            if filename.startswith(prefix):
                file_path = os.path.join(directory, filename)
                try:
                    os.remove(file_path)
                    self.logger.info(f"Solution deleted: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete solution {file_path}: {e}")

    @staticmethod
    def _convert(a):
        """
        `Internal Function`
        """
        it = iter(a)
        res_dct = dict(zip(it, it))
        return res_dct

    # print summary of sampler: =============================================================================================================
    def _print(self):
        """
        `Internal Function`
        Prints summary information about the sampler object:

        - :Mainnet: If the mainnet (Dynex platform sampling) or the testnet (local sampling) is being used for sampling (`bool`)
        - :logging: Show progress and status information or be quiet and omit terminal output (`bool`)
        - :tmp filename: The filename of the computation file (`string`)
        - :model type: [cnf, wcnf]: The type of the model: Sat problems (cnf) or QUBU/Ising type problems (wcnf) (`string`)
        - :num_variables: The number of variables of the model (`int`)
        - :num_clauses: The number of clauses of the model (`int`)

        :Example:

        .. code-block::

            DynexSampler object
            mainnet? True
            logging? True
            tmp filename: tmp/b8fa34a815f96098438d68142dfb68b6.dnx
            model type: BQM
            num variables: 15
            num clauses: 120
            configuration: dynex.ini
        """
        self.logger.info('{DynexSampler object}')
        self.logger.info(f'mainnet? {self.config.mainnet}')
        self.logger.info(f'logging? {self.logging}')
        self.logger.info(f'tmp filename: {self.filepath + self.filename}')
        self.logger.info(f'model type: {self.type_str}')
        self.logger.info(f'num variables: {self.num_variables}')
        self.logger.info(f'num clauses: {self.num_clauses}')
        self.logger.info('configuration: dynex.ini')

    # convert a sampler.sampleset[x]['sample'] into an assignment: ==========================================================================
    def _sample_to_assignments(self, lowest_set):
        """
        `Internal Function`
        The voltates of a sampling can be retrieved from the sampler with sampler.sampleset

        The sampler.sampleset returns a list of voltages for each variable, ranging from -1.0 to +1.0 and is a double precision value. Sometimes it is required to transform these voltages to binary values 0 (for negative voltages) or 1 (for positive voltages). This function converts a given sampler.sampleset[x] from voltages to binary values.

        :Parameters:

        - :lowest_set: The class:`dynex.sampler.assignment' which has to be converted (`list`)

        :Returns:

        - Returns the converted sample as `list`
        """
        sample = {}
        i = 0
        for var in self.var_mappings:
            sample[var] = 1
            if float(lowest_set[i]) < 0:
                sample[var] = 0
            i = i + 1
        return sample

    # sampling entry point: =================================================================================================================
    def sample(self, num_reads=32, annealing_time=10, switchfraction=0.0, alpha=20, beta=20, gamma=1, delta=1,
               epsilon=1, zeta=1, minimum_stepsize=0.05, debugging=False, block_fee=0, is_cluster=True, shots=1, rank=1,
               cluster_type=1, preprocess=False):
        """
        `Internal Function` which is called by public function `DynexSampler.sample`
        """

        retval = {}

        # In a malleable environment, it is rarely possible that a worker is submitting an inconsistent solution file. If the job
        # is small, we need to re-sample again. This routine samples up to NUM_RETRIES (10) times. If an error occurs, or
        # a keyboard interrupt was triggered, the return value is a dict containing key 'error'

        for i in range(0, self.num_retries):
            retval = self._sample(
                num_reads=num_reads,
                annealing_time=annealing_time,
                switchfraction=switchfraction,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
                delta=delta,
                epsilon=epsilon,
                zeta=zeta,
                minimum_stepsize=minimum_stepsize,
                debugging=debugging,
                block_fee=block_fee,
                is_cluster=is_cluster,
                shots=shots,
                rank=rank,
                cluster_type=cluster_type,
                preprocess=preprocess
            )
            if len(retval) > 0:
                break

            # TODO: support multi-model sampling
            self.logger.info(f'[DYNEX] NO VALID SAMPLE RESULT FOUND. RESAMPLING...{i + 1} / {self.num_retries}')
            # generate a fresh sampling file:
            self.filename = secrets.token_hex(16) + ".bin"
            if self.type == 'cnf':
                # convert to 3sat?
                if self._check_list_length(self.model.clauses):
                    self.clauses = self.api.r_sat(self.model.clauses)
                else:
                    self.clauses = self.model.clauses
                self._save_cnf(self.clauses, self.filepath + self.filename)
            if self.type == 'wcnf':
                self.save_wcnf(self.clauses, self.filepath + self.filename, self.num_variables, self.num_clauses,
                               self.model.var_mappings)

                # aggregate sampleset:
            if self.type == 'wcnf' and len(retval) > 0 and ('error' in retval) == False:
                retval = retval.aggregate()

        return retval

    def read_voltage_data(self, file, mainnet, rank):
        file_path = os.path.join(self.filepath, file)
        try:
            with open(file_path, 'r') as ffile:
                # Определяем стратегию чтения
                if mainnet:
                    if rank > 1:
                        return self._read_last_non_empty_line(ffile)
                    else:
                        return self._read_second_line(ffile)
                else:  # test-net
                    if rank > 1:
                        return self._read_last_non_empty_line(ffile)
                    else:
                        return self._read_entire_file(ffile)

        except (IOError, OSError) as e:
            self.logger.error(f'Error reading file {file_path}: {e}')
            return ['NaN']

    def _read_last_non_empty_line(self, file_obj):
        last_line = None
        for line in file_obj:
            if line.strip():
                last_line = line

        if not last_line:
            return ['NaN']

        return self._process_voltage_line(last_line)

    def _read_second_line(self, file_obj):
        file_obj.readline()
        second_line = file_obj.readline()

        if not second_line:
            return ['NaN']

        return self._process_voltage_line(second_line)

    def _read_entire_file(self, file_obj):
        data = file_obj.read()
        return self._process_voltage_line(data)

    @staticmethod
    def _process_voltage_line(line):
        if not line:
            return ['NaN']

        voltages = line.split(", ")[:-1]
        if voltages and not voltages[-1]:
            voltages = voltages[:-1]
        return voltages if voltages else ['NaN']

    # main sampling function =================================================================================================================
    def _sample(self, num_reads=32, annealing_time=10, switchfraction=0.0, alpha=20, beta=20, gamma=1, delta=1,
                epsilon=1, zeta=1, minimum_stepsize=0.05, debugging=False, block_fee=0, is_cluster=False, shots=1,
                rank=1,
                cluster_type=1, preprocess=False):
        """
        `Internal Function` which is called by private function `DynexSampler.sample`. This functions performs the sampling.
        """

        if self.multi_model_mode == True:
            raise Exception('ERROR: Multi-model parallel sampling is not implemented yet')

        if self.type == 'cnf' and self.config.mainnet == False and self.bnb == True:
            raise Exception('ERROR: Your local sampler does not support SAT jobs')

        mainnet = self.config.mainnet
        price_per_block = 0
        job_id = False
        self.cnt_solutions = 0

        dimod_sample = []

        # ensure correct ground state display:
        if self.config.solver_version == 2 and self.bqm:
            self.model.wcnf_offset = self.bqm.offset
            self.model.precision = 1

        # Preprocess:
        if self.config.solver_version == 2 and self.bqm and preprocess:
            sampler_sa = neal.SimulatedAnnealingSampler()
            sampleset = []
            start_time = time.time()
            for shot in range(0, shots):
                self.logger.info("[DYNEX] *** WAITING FOR READS ***")
                _sampleset = sampler_sa.sample(self.bqm, num_reads=num_reads, num_sweeps=annealing_time)
                if not sampleset:
                    sampleset = _sampleset
                else:
                    sampleset = dimod.concatenate([sampleset, _sampleset])
            end_time = time.time()
            elapsed_time = end_time - start_time  # in s
            elapsed_time *= 100

            self.logger.info(f"[DYNEX] PREPROCESSED WITH ENERGY {sampleset.first.energy} OFFSET={self.bqm.offset}")
            if sampleset.first.energy <= 0:
                if self.logging:
                    self.logger.info(f"[DYNEX] FINISHED READ AFTER {elapsed_time} SECONDS")
                table = ([
                    ['DYNEXJOB', 'QUBITS', 'QUANTUM GATES', 'BLOCK FEE', 'ELAPSED', 'WORKERS READ', 'CIRCUITS',
                     'STEPS', 'GROUND STATE']])
                table.append(['-1', self.num_variables, self.num_clauses, 0, '',
                              '*** WAITING FOR READS ***', '', '', ''])
                ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f")
                self.logger.info(ta + '\n')
                return sampleset

            dimod_sample = [sampleset.first.sample]

        try:

            # step 1: upload problem file to Dynex Platform: ---------------------------------------------------------------------------------
            if mainnet:
                params = {
                    "sampler": self,
                    "annealing_time": annealing_time,
                    "switchfraction": switchfraction,
                    "num_reads": num_reads,
                    "alpha": alpha,
                    "beta": beta,
                    "gamma": gamma,
                    "delta": delta,
                    "epsilon": epsilon,
                    "zeta": zeta,
                    "minimum_stepsize": minimum_stepsize,
                    "block_fee": block_fee,
                    "is_cluster": is_cluster,
                    "cluster_type": cluster_type,
                    "shots": shots,
                    "rank": rank,
                }
                # create job on mallob system:
                if self.config.solver_version == 2:
                    params.update({
                        "target_energy": 0.0 - self.clauses[1]
                    })
                job_id, self.filename, price_per_block, qasm = self.api.create_job_api(**params)
                # show effective price in DNX:
                price_per_block = price_per_block / 1000000000
                # parse qasm data:
                if self.type == 'qasm':
                    _data = qasm
                    _feed_dict = _data['feed_dict']
                    _model = _data['model']
                    if debugging:
                        self.logger.info(f'[DYNEX] feed_dict: {_feed_dict}')
                        self.logger.info(f'[DYNEX] model: {_model}')
                        # construct circuit model:
                    q = zlib.decompress(bytearray.fromhex(_model['q']))
                    q = str(q)[2:-1]
                    offset = float(_model['offset'])
                    bqm = dimod.BinaryQuadraticModel.from_qubo(ast.literal_eval(q), offset)
                    _model = BQM(bqm)
                    self.bqm = bqm
                    if self.config.solver_version == 1:
                        self.clauses = _model.clauses
                        self.num_variables = _model.num_variables
                        self.num_clauses = _model.num_clauses
                    else:
                        self.num_variables = _model.bqm.num_variables
                        self.num_clauses = len(_model.bqm.to_qubo()[0])
                        self.clauses = _model.bqm.to_qubo()
                    self.var_mappings = _model.var_mappings
                    self.precision = _model.precision
                    self._save_wcnf(self.clauses, self.filepath + self.filename, self.num_variables, self.num_clauses,
                                    self.var_mappings)
                    self.model.clauses = self.clauses
                    self.model.num_variables = self.num_variables
                    self.model.num_clauses = self.num_clauses
                    self.model.var_mappings = self.var_mappings
                    self.model.precision = self.precision
                if self.logging:
                    self.logger.info("[ÐYNEX] STARTING JOB...")
            else:
                # run on test-net:
                if self.type == 'wcnf':
                    localtype = 5
                elif self.type == 'cnf':
                    localtype = 0
                elif self.type == 'qasm':
                    localtype = 5
                    # testnet qasm sampling requires a dedicated library (not in default package):
                    command = 'python3 dynex_circuit_backend.py --mainnet False --file ' + self.model.qasm_filepath + self.model.qasm_filename
                    if debugging:
                        command = command + ' --debugging True'
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                    if debugging:
                        for c in iter(lambda: process.stdout.read(1), b""):
                            sys.stdout.write(c.decode('utf-8'))
                    elif self.logging:
                        self.logger.info("[DYNEX] *** WAITING FOR READS ***")
                        process.wait()
                    # read returned model:
                    f = open(self.model.qasm_filepath + self.model.qasm_filename + '.model', "r", encoding="utf-8")
                    _data = json.load(f)
                    _feed_dict = _data['feed_dict']
                    _model = _data['model']
                    if debugging:
                        self.logger.debug('[DYNEX] feed_dict:')
                        self.logger.debug(_feed_dict)
                        self.logger.debug('[DYNEX] model:')
                        self.logger.debug(_model)
                    f.close()
                    # construct circuit model:
                    q = zlib.decompress(bytearray.fromhex(_model['q']))
                    q = str(q)[2:-1]
                    offset = _model['offset']
                    bqm = dimod.BinaryQuadraticModel.from_qubo(ast.literal_eval(q), offset)
                    _model = BQM(bqm)
                    self.bqm = bqm
                    if self.config.solver_version == 1:
                        self.clauses = _model.clauses
                        self.num_variables = _model.num_variables
                        self.num_clauses = _model.num_clauses
                    else:
                        self.num_variables = _model.bqm.num_variables
                        self.num_clauses = len(_model.bqm.to_qubo()[0])
                        self.clauses = _model.bqm.to_qubo()
                    self.var_mappings = _model.var_mappings
                    self.precision = _model.precision
                    self.save_wcnf(self.clauses, self.filepath + self.filename, self.num_variables, self.num_clauses,
                                   self.var_mappings)

                job_id = -1
                command = self.solver_path + "np -t=" + str(localtype) + " -ms=" + str(
                    annealing_time) + " -st=1 -msz=" + str(minimum_stepsize) + " -c=" + str(
                    num_reads) + " --file='" + self.filepath_full + "/" + self.filename + "'"
                # in test-net, it cannot guaranteed that all requested chips are fitting:
                # num_reads = 0

                if alpha != 0:
                    command = command + " --alpha=" + str(alpha)
                if beta != 0:
                    command = command + " --beta=" + str(beta)
                if gamma != 0:
                    command = command + " --gamma=" + str(gamma)
                if delta != 0:
                    command = command + " --delta=" + str(delta)
                if epsilon != 0:
                    command = command + " --epsilon=" + str(epsilon)
                if zeta != 0:
                    command = command + " --zeta=" + str(zeta)

                # use branch-and-bound (testnet) sampler instead?:
                if self.bnb:
                    command = self.solver_path + "dynex-testnet-bnb " + self.filepath_full + "/" + self.filename

                # use self.config.solver_version == 2?
                if self.config.solver_version == 2:
                    population_size = num_reads
                    if rank > population_size:
                        raise Exception(
                            f'Rank must be equal to population size! Shots:{rank} Population:{population_size}')
                    command = self.solver_path + "dynexcore"
                    command += " file=" + self.filepath_full + "/" + self.filename
                    command += " num_steps=" + str(annealing_time)
                    command += " population_size=" + str(num_reads)
                    command += " max_iterations=" + str(num_reads)
                    command += " target_energy=" + str(0.0 - self.clauses[1])
                    # command += " ode_steps=" + str(annealing_time) #
                    # command += " search_steps=" + str(1000000) #
                    # command += " mutation_rate=10"
                    command += " init_dt=" + str(minimum_stepsize)
                    command += " cpu_threads=4"
                    command += " shots=" + str(rank)
                command += " json=1"
                # self.logger.info(f'[DYNEX DEBUG] Solver command: {command}')

                table = ([["SHOT", "SOLUTION ENERGY", "BEST SOLUTION", "SOLUTION FILE"]])
                for shot in range(0, shots):
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                    if debugging:
                        solution_energy = str()
                        solution_file = str()
                        best_solution = str()
                        for line in process.stdout:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                data = json.loads(line)
                                # self.logger.info(f'[DYNEX DEBUG] Solver output: {data}')
                                if "msg" in data and data["msg"].startswith("Best solution:"):
                                    best_solution = data["msg"].split(":")[1].strip()

                                if "solution_energy" in data:
                                    solution_energy = data['solution_energy']

                                if "solution_file" in data:
                                    solution_file = data['solution_file']
                            except json.JSONDecodeError:
                                # не-JSON строки выводим как есть
                                self.logger.info(f'[DYNEX DEBUG] Solver output: {line}')

                        table.append([shot + 1, solution_energy, best_solution, solution_file])
                        ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f")
                        self.logger.info(f'\n{ta}\n')
                    else:
                        if self.logging:
                            self.logger.info("[DYNEX] *** WAITING FOR READS ***")
                        process.wait()
                    # add salt:
                    self.add_salt_local()

            # step 2: wait for process to be finished: -------------------------------------------------------------------------------------
            t = time.process_time()
            finished = False
            runupdated = False
            cnt_workers = 0

            # initialise display:
            if mainnet and not debugging:
                clear_output(wait=True)
                table = ([
                    ['DYNEXJOB', 'QUBITS', 'QUANTUM GATES', 'BLOCK FEE', 'ELAPSED', 'WORKERS READ', 'CIRCUITS', 'STEPS',
                     'GROUND STATE']])
                table.append(
                    ['', self.num_variables, self.num_clauses, '', '', '*** WAITING FOR READS ***', '', '', ''])
                ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f")
                self.logger.info(f'\n{ta}\n')

            while not finished:
                total_chips = 0
                total_steps = 0
                lowest_energy = 1.7976931348623158e+308
                lowest_loc = 1.7976931348623158e+308

                # retrieve solutions
                if mainnet:
                    try:
                        self.list_files_with_text()
                    except Exception as e:
                        self.logger.info(f'[DYNEX] CONNECTION TO FTP ENDPOINT FAILED: {e}')
                        raise Exception('ERROR: CONNECTION TO FTP ENDPOINT FAILED')
                files = self.list_files_with_text_local()
                cnt_workers = len(files)

                for file in files:
                    if self.type == 'cnf':
                        info = file[len(self.filename) + 1:]
                        chips = -1
                        steps = -1
                        loc = 0
                        energy = 0
                    elif self.type in ['wcnf', 'qasm']:
                        info = file[len(self.filename) + 1:]
                        chips = int(info.split(".")[0])
                        steps = int(info.split(".")[1])
                        loc = int(info.split(".")[2])
                        # energy can also be non decimal:
                        if len(info.split(".")) > 4 and info.split(".")[4].isnumeric():
                            energy = float(info.split(".")[3] + "." + info.split(".")[4])
                        else:
                            energy = float(info.split(".")[3])

                    if mainnet:
                        self.cnt_solutions = cnt_workers
                    else:
                        self.cnt_solutions += 1
                    total_chips += chips
                    total_steps = steps
                    if energy < lowest_energy:
                        lowest_energy = energy
                    if loc < lowest_loc:
                        lowest_loc = loc
                    if self.type == 'cnf' and loc == 0:
                        finished = True
                    if total_chips >= num_reads * 0.90 and self.cnt_solutions >= shots:
                        finished = True
                details = ""
                if self.logging:
                    if mainnet and not debugging:
                        clear_output(wait=True)
                    if mainnet:
                        _loc_min, _energy_min, _mallob_chips, details = self.api.get_status_details_api(job_id,
                                                                                                        annealing_time,
                                                                                                        wcnf_offset=self.model.wcnf_offset,
                                                                                                        precision=self.model.precision)
                    table = ([
                        ['DYNEXJOB', 'QUBITS', 'QUANTUM GATES', 'BLOCK FEE', 'ELAPSED', 'WORKERS READ', 'CIRCUITS',
                         'STEPS', 'GROUND STATE']])
                    if cnt_workers < 1:
                        table.append([job_id, self.num_variables, self.num_clauses, price_per_block, '',
                                      '*** WAITING FOR READS ***', '', '', ''])
                    else:
                        elapsed_time = time.process_time() - t
                        table.append(
                            [job_id, self.num_variables, self.num_clauses, price_per_block, elapsed_time, cnt_workers,
                             total_chips, total_steps,
                             (lowest_energy + self.model.wcnf_offset) * self.model.precision])
                    ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f")
                    self.logger.info(f'\n{ta}\n{details}')

                    # update mallob - job running: -------------------------------------------------------------------------------------------------
                    if runupdated == False and mainnet:
                        self.api.update_job_api(job_id)
                        runupdated = True

            # update mallob - job finished: -------------------------------------------------------------------------------------------------
            if mainnet:
                self.api.finish_job_api(job_id, lowest_loc, lowest_energy)

            # update final output (display all workers as stopped as well):
            if cnt_workers > 0 and self.logging:
                if mainnet and not debugging:
                    clear_output(wait=True)
                details = ""
                if mainnet:
                    _loc_min, _energy_min, _mallob_chips, details = self.api.get_status_details_api(job_id,
                                                                                                    annealing_time,
                                                                                                    all_stopped=True,
                                                                                                    wcnf_offset=self.model.wcnf_offset,
                                                                                                    precision=self.model.precision)
                elapsed_time = time.process_time() - t
                if mainnet:
                    # display:
                    table = ([
                        ['DYNEXJOB', 'QUBITS', 'QUANTUM GATES', 'BLOCK FEE', 'ELAPSED', 'WORKERS READ', 'CIRCUITS',
                         'STEPS', 'GROUND STATE']])
                    table.append(
                        [job_id, self.num_variables, self.num_clauses, price_per_block, elapsed_time, cnt_workers,
                         total_chips, total_steps, (lowest_energy + self.model.wcnf_offset) * self.model.precision])
                    ta = tabulate(table, headers="firstrow", tablefmt='rounded_grid', floatfmt=".2f")
                    self.logger.info(f'\n{ta}\n{details}')

            elapsed_time = time.process_time() - t
            elapsed_time *= 100
            if self.logging:
                self.logger.info(f'[DYNEX] FINISHED READ AFTER {elapsed_time} SECONDS')

            # step 3: now parse voltages: ---------------------------------------------------------------------------------------------------

            sampleset = []
            lowest_energy = 1.7976931348623158e+308
            lowest_loc = 1.7976931348623158e+308
            total_chips = 0
            total_steps = 0
            lowest_set = []
            dimod_sample = []
            for file in files:
                if self.type == 'cnf':
                    info = file[len(self.filename) + 1:]
                    chips = -1
                    steps = -1
                    loc = 0
                    energy = 0
                # format: xxx.dnx.32.1.0.0.000000
                # jobfile chips steps loc energy
                elif self.type in ['wcnf', 'qasm']:
                    info = file[len(self.filename) + 1:]
                    chips = int(info.split(".")[0])
                    steps = int(info.split(".")[1])
                    loc = int(info.split(".")[2])

                    # energy can also be non decimal:
                    if len(info.split(".")) > 4 and info.split(".")[4].isnumeric():
                        energy = float(info.split(".")[3] + "." + info.split(".")[4])
                    else:
                        energy = float(info.split(".")[3])

                total_chips = total_chips + chips
                total_steps = steps

                voltages = self.read_voltage_data(file, mainnet, rank)

                # valid result? ignore Nan values and other incorrect data
                if self.type == 'cnf':
                    if 0 < len(voltages) == self.num_variables and voltages[0] != 'NaN':
                        self.dimod_assignments = {}
                        for i in range(0, len(voltages) - 8):  # REMOVE VALIDATION VARS
                            var = voltages[i]
                            if int(var) > 0:
                                self.dimod_assignments[abs(int(var))] = 1
                            else:
                                self.dimod_assignments[abs(int(var))] = 0

                if self.type in ['wcnf', 'qasm']:
                    if self.config.solver_version == 1:
                        if 0 < len(voltages) == self.num_variables and voltages[0] != 'NaN':
                            sampleset.append(
                                ['sample', voltages, 'chips', chips, 'steps', steps, 'falsified softs', loc, 'energy',
                                 energy])
                            if loc < lowest_loc:
                                lowest_loc = loc
                            if energy < lowest_energy:
                                lowest_energy = energy
                                lowest_set = voltages
                            # add voltages to dimod return sampleset:
                            dimodsample = {}
                            i = 0
                            for var in range(0, self.num_variables - 8):  # REMOVE VALIDATION VARS
                                # mapped variable?
                                if var in self.var_mappings:
                                    dimodsample[self.var_mappings[var]] = 1
                                    if float(voltages[i]) < 0:
                                        dimodsample[self.var_mappings[var]] = 0
                                else:
                                    dimodsample[i] = 1
                                    if float(voltages[i]) < 0:
                                        dimodsample[i] = 0
                                i = i + 1

                            dimod_sample.append(dimodsample)

                        else:
                            self.logger.info(f'[DYNEX] OMITTED SOLUTION FILE: {file} - INCORRECT DATA')
                    else:
                        sampleset.append(
                            ['sample', voltages, 'chips', chips, 'steps', steps, 'falsified softs', loc, 'energy',
                             energy])
                        if loc < lowest_loc:
                            lowest_loc = loc
                        if energy < lowest_energy:
                            lowest_energy = energy
                            lowest_set = voltages
                        # add voltages to dimod return sampleset:
                        dimodsample = {}
                        i = 0
                        for var in range(0, self.num_variables):
                            # mapped variable?
                            if var in self.var_mappings:
                                dimodsample[self.var_mappings[var]] = 1
                                if float(voltages[i]) < 0:
                                    dimodsample[self.var_mappings[var]] = 0
                            else:
                                dimodsample[i] = 1
                                if float(voltages[i]) < 0:
                                    dimodsample[i] = 0
                            i = i + 1

                        dimod_sample.append(dimodsample)

            if self.type in ['wcnf', 'qasm']:
                sampleset.append(
                    ['sample', lowest_set, 'chips', total_chips, 'steps', total_steps, 'falsified softs', lowest_loc,
                     'energy', lowest_energy])

            # build sample dict "assignments" with 0/1 and dimod_sampleset ------------------------------------------------------------------
            if (self.type in ['wcnf', 'qasm']) and len(lowest_set) == self.num_variables:
                sample = {}
                i = 0
                for var in self.var_mappings:
                    # _var = self.var_mappings[var]
                    sample[var] = 1
                    if (float(lowest_set[i]) < 0):
                        sample[var] = 0
                    i = i + 1
                self.assignments = sample

                # generate dimod format sampleset:
                self.dimod_assignments = dimod.SampleSet.from_samples_bqm(dimod_sample, self.bqm)

            if self.logging:
                self.logger.info(f"[DYNEX] SAMPLESET READY WITH ENERGY {self.dimod_assignments}")

            # create return sampleset: ------------------------------------------------------------------------------------------------------
            sampleset_clean = []
            for sample in sampleset:
                sample_dict = self._convert(sample)
                sampleset_clean.append(sample_dict)

            # Delete local files
            if self.config.remove_local_solutions:
                self.delete_local_files_by_prefix(self.filepath, self.filename)

        except KeyboardInterrupt:
            if mainnet:
                self.api.cancel_job_api(job_id)
            self.logger.error("[DYNEX] Keyboard interrupt")
            return {'error': 'Keyboard interrupt'}

        except Exception as e:
            self.logger.info(f"[DYNEX] Exception encountered during hadling exception: {e}")
            if mainnet:
                self.api.cancel_job_api(job_id)
            return {'error': 'Exception encountered during handling excepiton', 'details': e}

        self.sampleset = sampleset_clean

        # CQM model?
        if self.model.type_str == 'CQM':
            cqm_sample = self.model.invert(self.dimod_assignments.first.sample)
            self.dimod_assignments = dimod.SampleSet.from_samples_cqm(cqm_sample, self.model.cqm)

        # DQM model?
        elif self.model.type_str == 'DQM':
            cqm_sample = self.model.invert(self.dimod_assignments.first.sample)
            dqm_sample = {}
            for s, c in cqm_sample:
                if cqm_sample[(s, c)] == 1:
                    dqm_sample[s] = c
            self.dimod_assignments = dimod.SampleSet.from_samples(dimod.as_samples(dqm_sample), 'DISCRETE', 0)

        return self.dimod_assignments
