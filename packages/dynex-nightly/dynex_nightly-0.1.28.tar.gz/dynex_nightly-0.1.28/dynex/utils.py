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
import hashlib
import os
import sys
import time

import dimod

from dynex import DynexConfig, BQM, DynexSampler
from .sampler import _DynexSampler


def calculate_sha3_256_hash(string):
    """
    `Internal Function`
    """
    sha3_256_hash = hashlib.sha3_256()
    sha3_256_hash.update(string.encode('utf-8'))
    return sha3_256_hash.hexdigest()


def calculate_sha3_256_hash_bin(bin):
    """
    `Internal Function`
    """
    sha3_256_hash = hashlib.sha3_256()
    sha3_256_hash.update(bin)
    return sha3_256_hash.hexdigest()




def max_value(inputlist):
    """
    `Internal Function`
    """
    return max([sublist[-1] for sublist in inputlist])


def get_core_count():
    """
    `Internal Function`
    """
    if sys.platform == 'win32':
        return (int)(os.environ['NUMBER_OF_PROCESSORS'])
    else:
        return (int)(os.popen('grep -c cores /proc/cpuinfo').read())

def sample_qubo(Q, offset=0.0, logging=True, formula=2, mainnet=False, description='Dynex SDK Job',
                bnb=True, num_reads=32, annealing_time=10, clones=1, switchfraction=0.0, alpha=20, beta=20, gamma=1,
                delta=1, epsilon=1, zeta=1, minimum_stepsize=0.05, debugging=False, block_fee=0, is_cluster=True,
                cluster_type=1,
                shots=1, v2=False):
    """
    Samples a Qubo problem.

    :Parameters:

    - :Q: The Qubo problem

    - :offset: The offset value of the Qubo problem

    - :logging: Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (`bool`)

    - :mainnet: Defines if the mainnet (Dynex platform sampling) or the testnet (local sampling) is being used for sampling (`bool`)

    - :description: Defines the description for the sampling, which is shown in Dynex job dashboards as well as in the market place  (`string`)

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

    .. code-block:: Python

        from pyqubo import Array
        N = 15
        K = 3
        numbers = [4.8097315016016315, 4.325157567810298, 2.9877429101815127,
                   3.199880179616316, 0.5787939511978596, 1.2520928214246918,
                   2.262867466401502, 1.2300003067401255, 2.1601079352817925,
                   3.63753899583021, 4.598232793833491, 2.6215815162575646,
                   3.4227134835783364, 0.28254151584552023, 4.2548151473817075]

        q = Array.create('q', N, 'BINARY')
        H = sum(numbers[i] * q[i] for i in range(N)) + 5.0 * (sum(q) - K)**2
        model = H.compile()
        Q, offset = model.to_qubo(index_label=True)
        sampleset = dynex.sample_qubo(Q, offset, formula=2, annealing_time=200, bnb=True)
        print(sampleset)
           0  1  2  3  4  5  6  7  8  9 10 11 12 13 14   energy num_oc.
        0  0  1  0  0  0  0  0  1  0  0  1  0  0  0  0 2.091336       1
        ['BINARY', 1 rows, 1 samples, 15 variables]

    """
    dyn_ver = 2 if v2 else 1  # FIXME Temporary solution
    config = DynexConfig(mainnet=mainnet, solver_version=dyn_ver)
    bqm = dimod.BinaryQuadraticModel.from_qubo(Q, offset)
    model = BQM(bqm, logging=logging, formula=formula, config=config)
    sampler = DynexSampler(model, logging=logging, description=description, bnb=bnb, config=config)
    sampleset = sampler.sample(num_reads=num_reads, annealing_time=annealing_time, clones=clones,
                               switchfraction=switchfraction, alpha=alpha, beta=beta, gamma=gamma, delta=delta,
                               epsilon=epsilon, zeta=zeta, minimum_stepsize=minimum_stepsize, debugging=debugging,
                               block_fee=block_fee, is_cluster=is_cluster, shots=shots, cluster_type=cluster_type)
    return sampleset


def sample_ising(h, j, logging=True, formula=2, description='Dynex SDK Job', bnb=True,
                 num_reads=32, annealing_time=10, clones=1, switchfraction=0.0, alpha=20, beta=20, gamma=1, delta=1,
                 epsilon=1, zeta=1, minimum_stepsize=0.05, debugging=False, block_fee=0, is_cluster=True,
                 shots=1, cluster_type=1, config: DynexConfig=None):
    """
    Samples an Ising problem.

    :Parameters:

    - :h: Linear biases of the Ising problem

    - :j: Quadratic biases of the Ising problem

    - :logging: Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (`bool`)

    - :mainnet: Defines if the mainnet (Dynex platform sampling) or the testnet (local sampling) is being used for sampling (`bool`)

    - :description: Defines the description for the sampling, which is shown in Dynex job dashboards as well as in the market place  (`string`)

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

    - :minimum_stepsize: The ODE integration of the QUBU/Ising or SAT model based neuromorphic circuits is performing adaptive stepsizes for each ODE integration forward Euler step. This value defines the smallest step size for a single adaptive integration step (`double` value in the range of [0.0000000000000001, 1.0])

    - :debugging: Only applicable for test-net sampling. Defines if the sampling process should be quiet with no terminal output (FALSE) or if process updates are to be shown (TRUE) (`bool`)

    - :bnb: Use alternative branch-and-bound sampling when in mainnet=False (`bool`)

    - :block_fee: Computing jobs on the Dynex platform are being prioritised by the block fee which is being offered for computation. If this parameter is not specified, the current average block fee on the platform is being charged. To set an individual block fee for the sampling, specify this parameter, which is the amount of DNX in nanoDNX (1 DNX = 1,000,000,000 nanoDNX)

    - :shots: Sets the minimum number of solutions to retrieve from the network. Works both on mainnet=False and mainnet=True (Default: 1). Typically used for situations where not only the best global optimum (sampleset.first) is required, but multiple optima from different workers.

    :Returns:

    - Returns a dimod sampleset object class:`dimod.sampleset`

    """
    if config is None:
        config = DynexConfig()
    
    bqm = dimod.BinaryQuadraticModel.from_ising(h, j)
    model = BQM(bqm, logging=logging, formula=formula, config=config)
    sampler = DynexSampler(model, logging=logging, description=description, bnb=bnb, config=config)
    sampleset = sampler.sample(num_reads=num_reads, annealing_time=annealing_time, clones=clones,
                               switchfraction=switchfraction, alpha=alpha, beta=beta, gamma=gamma, delta=delta,
                               epsilon=epsilon, zeta=zeta, minimum_stepsize=minimum_stepsize, debugging=debugging,
                               block_fee=block_fee, is_cluster=is_cluster, shots=shots, cluster_type=cluster_type)
    return sampleset

def test():
    """
    Performs test of the dynex.ini settings. Successful completion is required to start using the sampler.
    """
    allpassed = True
    config = DynexConfig(is_logging=False)
    config.logger.info('[DYNEX] TEST: dimod BQM construction...')

    bqm = dimod.BinaryQuadraticModel({'a': 1.5}, {('a', 'b'): -1}, 0.0, 'BINARY')
    model = BQM(bqm)
    config.logger.info('[DYNEX] PASSED')
    config.logger.info('[DYNEX] TEST: Dynex Sampler object...')
    sampler = _DynexSampler(model, mainnet=False, logging=False, test=True, config=config)
    config.logger.info('[DYNEX] PASSED')
    config.logger.info('[DYNEX] TEST: submitting sample file...')
    worker_user = sampler.solutionuser.split(':')[0]
    worker_pass = sampler.solutionuser.split(':')[1]
    ret = sampler.upload_file_to_ftp(sampler.solutionurl[6:-1], worker_user, worker_pass,
                                     sampler.filepath + sampler.filename, '', sampler.logging)
    if ret == False:
        config.logger.error('[DYNEX] FAILED')
        raise Exception("DYNEX TEST FAILED")
    else:
        config.logger.info('[DYNEX] PASSED')
    time.sleep(1)
    config.logger.info('[DYNEX] TEST: retrieving samples...')
    try:
        sampler.list_files_with_text()
        config.logger.info('[DYNEX] PASSED')
    except:
        config.logger.error('[DYNEX] FAILED')
        raise Exception("DYNEX TEST FAILED")
    if allpassed:
        config.logger.info('[DYNEX] TEST RESULT: ALL TESTS PASSED')
        with open('dynex.test', 'w') as f:
            f.write('[DYNEX] TEST RESULT: ALL TESTS PASSED')
    else:
        config.logger.info('[DYNEX] TEST RESULT: ERRORS OCCURED')
    return allpassed

