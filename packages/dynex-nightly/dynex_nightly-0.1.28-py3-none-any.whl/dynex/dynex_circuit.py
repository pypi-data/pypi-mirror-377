"""
Dynex SDK (beta) Neuromorphic Computing Library
Copyright (c) 2021-2024, Dynex Developers

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
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE, DATA, OR PROFITS OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import dynex
from pennylane import numpy as np
import pennylane as qml
import secrets
from collections import Counter
import json
import zlib
import base64
import inspect
import warnings

from dynex import DynexConfig

warnings.filterwarnings("ignore", category=DeprecationWarning)


class CircuitModel:
    """
    `Internal Class` to hold information about the Dynex circuit
    """

    def __init__(self, circuit_str=None, wires=None, params=None):
        self.qasm_circuit = None
        self.circuit_str = circuit_str
        self.qasm_filepath = "tmp/"
        self.qasm_filename = secrets.token_hex(16) + ".qasm.dnx"
        self.params = params
        self.wires = wires
        self.type = "qasm"
        self.type_str = "QASM"
        self.bqm = None
        self.clauses = []
        self.wcnf_offset = 0
        self.precision = 1.0


class DynexCircuit:
    description: str = "Dynex SDK Job"

    def __init__(self, config: DynexConfig = None):
        self.config = config if config is not None else DynexConfig()
        self.logger = self.config.logger

    def sol2state(self, sample, wires, is_qpe, is_grover, is_cqu, is_qu):
        state = [0] * wires
        for wire in range(wires):
            r_key = f'q_{wire}_real'
            i_key = f'q_{wire}_imag'
            qpe_key = f'q_{wire}_ctrl_qpe_imag'
            if is_qpe and qpe_key in sample:
                state[wire] = 1 if sample[qpe_key] > sample[r_key] else 0
            elif r_key in sample and i_key in sample:
                if is_grover or is_cqu or is_qu:
                    state[wire] = 1 if sample[i_key] > 0.5 else 0
                else:
                    state[wire] = 1 if sample[r_key] > 0.5 else 0
            else:
                self.logger.info(f"Warning: No final state found for wire {wire}")
        return state

    def get_samples(self, sampleset, wires, is_qpe, is_grover, is_cqu, is_qu):
        samples = []
        for solution, occurrence in zip(sampleset, sampleset.record.num_occurrences):
            sample = self.sol2state(solution, wires, is_qpe, is_grover, is_cqu, is_qu)
            samples.extend([sample] * occurrence)
        return samples

    def get_probs(self, sampleset, wires, is_qpe, is_grover, is_cqu, is_qu):
        state_counts = Counter()
        total_samples = sum(sampleset.record.num_occurrences)
        for solution, occurrence in zip(sampleset, sampleset.record.num_occurrences):
            state = self.sol2state(solution, wires, is_qpe, is_grover, is_cqu, is_qu)
            state_counts[tuple(state)] += occurrence
        qubit_probs = np.zeros(wires)
        for state, count in state_counts.items():
            for i, bit in enumerate(state):
                if bit == 1:
                    qubit_probs[i] += count / total_samples
        return qubit_probs[::-1]
    
    @staticmethod
    def _save_qasm_file(dnx_circuit):
        """
        `Internal Function`

        Saves the circuit as a .qasm file locally in /tmp as defined in dynex.ini
        """

        filename = dnx_circuit.qasm_filepath + dnx_circuit.qasm_filename

        with open(filename, "w", encoding="utf-8") as f:
            f.write(dnx_circuit.circuit_str)

    @staticmethod
    def check_pennylane_circuit(circuit) -> bool:
        if isinstance(circuit, qml.QNode):
            return True
        if hasattr(circuit, "quantum_instance") and isinstance(circuit.quantum_instance, qml.QNode):
            return True
        if inspect.isfunction(circuit):
            source = inspect.getsource(circuit)
            pops = [
                "qml.Hadamard", "qml.CNOT", "qml.RX", "qml.RY", "qml.RZ",
                "qml.BasisEmbedding", "qml.QFT", "qml.adjoint", "qml.state",
                "qml.sample", "qml.PauliX", "qml.PauliY", "qml.PauliZ",
                "qml.S", "qml.T", "qml.CZ", "qml.SWAP", "qml.CSWAP",
                "qml.Toffoli", "qml.PhaseShift", "qml.ControlledPhaseShift",
                "qml.CRX", "qml.CRY", "qml.CRZ", "qml.Rot", "qml.MultiRZ",
                "qml.QubitUnitary", "qml.ControlledQubitUnitary", "qml.IsingXX",
                "qml.IsingYY", "qml.IsingZZ", "qml.Identity", "qml.Kerr",
                "qml.CrossKerr", "qml.Squeezing", "qml.DisplacedSqueezed",
                "qml.TwoModeSqueezing", "qml.ControlledAddition", "qml.ControlledSubtraction"
            ]
            if "qml." in source and any(op in source for op in pops):
                return True
            if "wires=" in source:
                return True
        if hasattr(circuit, "interface") or hasattr(circuit, "device"):
            return True
        if hasattr(circuit, "func") and hasattr(circuit, "device"):
            return True
        return False

    @staticmethod
    def _qiskit_to_circuit(qc, circuit_params, wires):
        # construct circuit:
        _wires = []
        for i in range(0, wires):
            _wires.append(i)
        my_qfunc = qml.from_qiskit(qc)
        dev = qml.device("default.qubit", wires=wires)

        @qml.qnode(dev)
        def pl_circuit(params):
            my_qfunc(wires=_wires)
            return qml.state()

        # construct dynex_circuit:
        pl_circuit.construct([circuit_params], {})

        return pl_circuit

    @staticmethod
    def _qasm_to_circuit(t, circuit_params, wires):
        """
        `Internal Function`

        Reads raw qasm text and converts to PennyLane Circuit class object
        """
        # construct circuit:
        _wires = []
        for i in range(0, wires):
            _wires.append(i)
        qasm_circuit = qml.from_qasm(t, measurements=[])  # Create from qasm string
        # define bridge circuit:
        dev = qml.device("default.qubit", wires=wires)

        @qml.qnode(dev)
        def pl_circuit(params):
            # Add qasm circuit
            qasm_circuit(wires=_wires)
            return qml.state()

        # construct dynex_circuit:
        pl_circuit.construct([circuit_params], {})
        return pl_circuit
    
    @staticmethod
    def _pennylane_to_file(circuit, params, wires):
        with qml.tape.QuantumTape() as tape:
            circuit(params)
        ops = tape.operations
        is_qpe = any(op.name.startswith("QuantumPhaseEstimation") for op in ops)
        is_grover = any(op.name.startswith("GroverOperator") for op in ops)
        is_cqu = any(op.name.startswith("ControlledQubitUnitary") for op in ops)
        is_qu = any(op.name.startswith("QubitUnitary") for op in ops)

        def process_ops(op):
            op_dict = {
                "name": op.name,
                "wires": [int(w) for w in op.wires],  # ensure wires are integers
                "params": [p.tolist() if hasattr(p, "tolist") else p for p in op.parameters],
                "hyperparams": {k: v.tolist() if hasattr(v, "tolist") else v for k, v in op.hyperparameters.items() if
                                k != "wires"},  # For B.E gate
                "adjointD": 0,  # supporting nested daggers
                "ctrlD": 0  # supporting nested controlled gates
            }
            name = op.name
            if name.startswith("Snapshot"):
                pass
            while name.startswith(("Adjoint(", "C(")):
                if name.startswith("Adjoint("):
                    op_dict["adjointD"] += 1
                    name = name[8:-1]  # remove "Adjoint(" and ")"
                elif name.startswith("C("):
                    op_dict["ctrlD"] += 1
                    name = name[2:-1]  # remove "C(" and ")"
            op_dict["base_name"] = name
            if op_dict["ctrlD"] > 0 or name == "ControlledQubitUnitary":  # handling CQU
                op_dict["control_wires"] = [int(w) for w in op.control_wires]
                op_dict["target_wires"] = [int(w) for w in op.wires[len(op.control_wires):]]
            if name == "QuantumPhaseEstimation":  # handling QPE
                op_dict["estimation_wires"] = [int(w) for w in op.hyperparameters["estimation_wires"]]
                U = op.hyperparameters["unitary"]
                if isinstance(U, qml.operation.Operation):
                    op_dict["unitary"] = {
                        "name": U.name,
                        "wires": [int(w) for w in U.wires],
                        "params": [p.tolist() if hasattr(p, "tolist") else p for p in U.parameters],
                    }
                else:
                    op_dict["unitary"] = U.tolist() if hasattr(U, "tolist") else U
                    op_dict["target_wires"] = [int(w) for w in op.target_wires]
            return op_dict

        cir_info = [process_ops(op) for op in ops]
        cir_i = {
            "operations": cir_info,
            "nWires": wires,
            "nParams": len(params),
            "params": params
        }
        data = json.dumps(cir_i, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else str(x))
        comp = zlib.compress(data.encode("utf-8"))
        dynex_circuit = base64.b85encode(comp).decode("utf-8")
        return dynex_circuit, is_qpe, is_grover, is_cqu, is_qu

    def execute(self,
                circuit,
                params,
                wires,
                num_reads=1000,
                integration_steps=100,
                method="measure",
                logging=True,
                bnb=False,
                switchfraction=0.0,
                alpha=20,
                beta=20,
                gamma=1,
                delta=1,
                epsilon=1,
                zeta=1,
                minimum_stepsize=0.05,
                block_fee=0,
                is_cluster=True,
                cluster_type=0,
                shots=15
                ):
        """
        Function to execute quantum gate based circuits natively on the Dynex Neuromorphic Computing Platform.

        :Parameters:
        - :circuit: A circuit in one of the following formats: [openQASM, PennyLane, Qiskit, Cirq] (circuit class)
        - :params: Parameters for circuit execution (`list`)
        - :wires: number of qubits (`int`)
        - :method: Type of circuit measurement:
            'measure': samples of a single measurement
            'probs': computational basis state probabilities
            'all': all solutions as arrays
            'sampleset': dimod sampleset
        - :shots: Sets the minimum number of solutions to retrieve from the network. Works both on mainnet=False and mainnet=True (Default: 1). Typically used for situations where not only the best global optimum (sampleset.first) is required, but multiple optima from different workers (`int`).
        - :description: Defines the description for the job, which is shown in Dynex job dashboards as well as in the network explorer (`string`)

        :Sampling Parameters:

        - :num_reads: Defines the number of parallel samples to be performed (`int` value in the range of [32, MAX_NUM_READS] as defined in your license)

        - :annealing_time: Defines the number of integration steps for the sampling. Models are being converted into neuromorphic circuits, which are then simulated with ODE integration by the participating workers (`int` value in the range of [1, MAX_ANNEALING_TIME] as defined in your license)

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

        :Returns:

        - Returns the measurement based on the parameter 'measure'

        :Example:

        .. code-block:: Python

            params = [0.1, 0.2]
            wires = 2

            dev = qml.device('default.qubit', wires=wires, shots=1)
            @qml.qnode(dev)
            def circuit(params):
                qml.RX(params[0], wires=0)
                qml.RY(params[1], wires=1)
                qml.CNOT(wires=[0, 1])
                qml.Hadamard(wires=0)
                return qml.sample()#qml.expval(qml.Hadamard(0)) #qml.sample() #state()

            # Draw circuit:
            _ = qml.draw_mpl(circuit, style="black_white", expansion_strategy="device")(params)

            # Compute circuit on Dynex:
            import dynex_circuit
            measure = dynex_circuit.execute(circuit, params, mainnet=True)
            print(measure)

            │   DYNEXJOB │   QUBITS │   QUANTUM GATES │   BLOCK FEE │   ELAPSED │   WORKERS READ │   CIRCUITS │   STEPS │   GROUND STATE │
            ├────────────┼──────────┼─────────────────┼─────────────┼───────────┼────────────────┼────────────┼─────────┼────────────────┤
            │      28391 │       21 │              64 │        0.00 │      0.58 │              1 │       1000 │     256 │       38708.00 │
            ╰────────────┴──────────┴─────────────────┴─────────────┴───────────┴────────────────┴────────────┴─────────┴────────────────╯
            ╭────────────┬─────────────────┬────────────┬───────┬──────────┬──────────────┬─────────────────────────────┬───────────┬──────────╮
            │     WORKER │         VERSION │   CIRCUITS │   LOC │   ENERGY │      RUNTIME │                 LAST UPDATE │     STEPS │   STATUS │
            ├────────────┼─────────────────┼────────────┼───────┼──────────┼──────────────┼─────────────────────────────┼───────────┼──────────┤
            │ 1147..9be1 │ 2.3.5.OZM.134.L │       1000 │     0 │     0.00 │ 4.190416548s │ 2024-08-06T19:37:36.148518Z │ 0 (0.00%) │  STOPPED │
            ├────────────┼─────────────────┼────────────┼───────┼──────────┼──────────────┼─────────────────────────────┼───────────┼──────────┤
            │ 6a66..2857 │ 2.3.5.OZM.134.L │       1000 │     0 │     0.00 │ 9.002006172s │  2024-08-06T19:37:31.33693Z │ 0 (0.00%) │  STOPPED │
            ╰────────────┴─────────────────┴────────────┴───────┴──────────┴──────────────┴─────────────────────────────┴───────────┴──────────╯
            [DYNEX] FINISHED READ AFTER 57.94 SECONDS
            [DYNEX] SAMPLESET READY
            [1 0]

        ...
        """

        # enforce param wires to int value:
        if type(wires) == list:
            wires = len(wires)
        circuit_str = None
        is_qpe = False
        is_grover = False
        is_cqu = False
        is_qu = False
        # pennylane circuit? convert to qasm
        # plChecker = str(type(circuit)).find('pennylane') > 0 # this method DOES NOT detect a pennylane circuit if it's not executed with QNode/device
        if self.check_pennylane_circuit(circuit):  # this is more sophisticated approach (using inspection)
            # circuit.construct([params], {})
            circuit_str, is_qpe, is_grover, is_cqu, is_qu = self._pennylane_to_file(circuit, params, wires)
            if logging:
                self.logger.info("[DYNEX] Executing PennyLane quantum circuit")

        # qasm circuit? convert to pennylane->to_file
        qasm_checker = type(circuit) == str
        if qasm_checker:
            circuit = self._qasm_to_circuit(circuit, params, wires)
            circuit_str =  self._pennylane_to_file(circuit, params, wires)
            if logging:
                self.logger.info("[DYNEX] Executing OpenQASM quantum circuit")

        # cirq circuit? convert to pennylane->to_file
        # TBD

        # qiskit circuit? convert to pennylane->to_file
        qiskit_checker = str(type(circuit)).find('qiskit') > 0
        if qiskit_checker:
            circuit = self._qiskit_to_circuit(circuit, params, wires)
            circuit_str =  self._pennylane_to_file(circuit, params, wires)
            if logging:
                self.logger.info("[DYNEX] Executing Qiskit quantum circuit")

        # At this point we can assume its pennylane->to_file format circuit. We generate a dynex circuit model
        circ_model = CircuitModel(circuit_str=circuit_str, params=params, wires=wires)


        self._save_qasm_file(circ_model)

        sampler = dynex.DynexSampler(
            model=circ_model,
            description=self.description,
            bnb=bnb,
            logging=logging,
            filename_override=circ_model.qasm_filename,
            config=self.config)

        sampleset = sampler.sample(
            num_reads=num_reads,
            annealing_time=integration_steps,
            switchfraction=switchfraction,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            delta=delta,
            epsilon=epsilon,
            zeta=zeta,
            minimum_stepsize=minimum_stepsize,
            debugging=logging,
            block_fee=block_fee,
            is_cluster=is_cluster,
            cluster_type=cluster_type,
            shots=shots)

        # decode solution:
        if method not in ["measure", "probs", "all", "sampleset"]:
            raise ValueError("Method must be either 'measure', 'probs', 'all' or 'sampleset'")

        if logging:
            self.logger.info(f"[DYNEX] -------------- /  {method}  / ------------")
        if method == "measure":
            samples = self.get_samples(sampleset, wires, is_qpe, is_grover, is_cqu, is_qu)
            if is_qpe:
                result = np.array(samples[0])
            else:
                result = np.array(samples[0])[::-1]
        elif method == "sampleset":
            result = sampleset
        elif method == "all":
            result = [np.array(sample) for sample in
                      self.get_samples(sampleset, wires, is_qpe, is_grover, is_cqu, is_qu)]
        else:  # probs
            probs = self.get_probs(sampleset, wires, is_qpe, is_grover, is_cqu, is_qu)
            result = probs
        return result
