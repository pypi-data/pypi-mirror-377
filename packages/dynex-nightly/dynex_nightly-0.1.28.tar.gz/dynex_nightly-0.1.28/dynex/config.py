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

import os
import configparser
import logging
from typing import Optional, Dict, ClassVar, List
from functools import cached_property

class DynexConfig:
    """Configuration handler for Dynex SDK with ENV priority and validation."""

    DEFAULT_CONFIG_LOCATIONS: ClassVar[List[str]] = [
        "dynex.ini",
        os.path.expanduser("~/.dynex.ini"),
        "/etc/dynex.ini"
    ]
    DEFAULT_SOLVER_LOCATIONS: ClassVar[List[str]] = ["testnet/"]
    ENV_PREFIX: ClassVar[str] = "DYNEX_"

    def __init__(
        self,
        config_path: Optional[str] = None,
        solver_version: int = 2,
        solver_path: Optional[str] = None,
        mainnet: bool = True,
        is_logging: bool = True,
        retry_count: int = 5,
        remove_local_solutions: bool = False,
    ) -> None:
        self.logger = self._init_logger()
        self.mainnet = mainnet
        self.is_logging = is_logging
        self.remove_local_solutions = remove_local_solutions
        self.retry_count = retry_count
        self.solver_version = solver_version if solver_version in (1, 2) else 2
        self._env_config = self._load_env_config()  # Load ENV first
        self.config_path = self._resolve_path(config_path, "config")
        self.solver_path = self._resolve_path(solver_path, "solver")

        if not self.config_path:
            raise FileNotFoundError("Config file not found in default locations or ENV.")
        if not mainnet and not self.solver_path:
            raise FileNotFoundError("Solver file not found in testnet mode.")

        self.config = configparser.ConfigParser()
        self._load_config()
        self._ensure_tmp_directory()

    @staticmethod
    def _init_logger() -> logging.Logger:
        logger = logging.getLogger("dynex.config")
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[DYNEX] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def _load_env_config(self) -> Dict[str, Optional[str]]:
        """Load configuration from environment variables."""
        env_keys = {
            "API_KEY": os.getenv(f"{self.ENV_PREFIX}API_KEY"),
            "API_ENDPOINT": os.getenv(f"{self.ENV_PREFIX}API_ENDPOINT"),
            "API_SECRET": os.getenv(f"{self.ENV_PREFIX}API_SECRET"),
            "FTP_HOSTNAME": os.getenv(f"{self.ENV_PREFIX}FTP_HOSTNAME"),
            "FTP_USERNAME": os.getenv(f"{self.ENV_PREFIX}FTP_USERNAME"),
            "FTP_PASSWORD": os.getenv(f"{self.ENV_PREFIX}FTP_PASSWORD"),
        }
        return {k: v for k, v in env_keys.items() if v is not None}

    def _resolve_path(self, file_path: Optional[str], file_type: str) -> Optional[str]:
        """Resolve path for config/solver with ENV fallback."""
        env_var = f"{self.ENV_PREFIX}{file_type.upper()}"
        locations = (
            self.DEFAULT_CONFIG_LOCATIONS
            if file_type == "config"
            else self.DEFAULT_SOLVER_LOCATIONS
        )

        # 1. Check explicit path
        if file_path and os.path.exists(file_path):
            return file_path
        # 2. Check ENV
        if env_path := os.getenv(env_var):
            if os.path.exists(env_path):
                return env_path
        # 3. Check default locations
        for path in locations:
            if os.path.exists(path):
                return path
        return None

    def _ensure_tmp_directory(self) -> None:
        """Create tmp/ directory with write permissions."""
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        try:
            os.makedirs(tmp_dir, exist_ok=True)
            if not os.access(tmp_dir, os.W_OK):
                raise PermissionError(f"Cannot write to tmp/: {tmp_dir}")
        except OSError as e:
            self.logger.error(f"Failed to create tmp/: {e}")
            raise

    def _load_config(self) -> None:
        """Load config file and validate required keys."""
        self.config.read(self.config_path)
        required_keys = {
            "DYNEX": ["API_KEY", "API_ENDPOINT", "API_SECRET"],
            "FTP_SOLUTION_FILES": ["ftp_hostname", "ftp_username", "ftp_password"],
        }
        for section, keys in required_keys.items():
            if section not in self.config:
                raise KeyError(f"Missing section in config: {section}")
            for key in keys:
                if key not in self.config[section]:
                    raise KeyError(f"Missing key: {section}.{key}")

    @cached_property
    def api_key(self) -> str:
        return self._env_config.get("API_KEY") or self.config["DYNEX"]["API_KEY"]

    @cached_property
    def api_endpoint(self) -> str:
        return self._env_config.get("API_ENDPOINT") or self.config["DYNEX"]["API_ENDPOINT"]

    @cached_property
    def api_secret(self) -> str:
        return self._env_config.get("API_SECRET") or self.config["DYNEX"]["API_SECRET"]

    @cached_property
    def ftp_hostname(self) -> str:
        return self._env_config.get("FTP_HOSTNAME") or self.config["FTP_SOLUTION_FILES"]["ftp_hostname"]

    @cached_property
    def ftp_username(self) -> str:
        return self._env_config.get("FTP_USERNAME") or self.config["FTP_SOLUTION_FILES"]["ftp_username"]

    @cached_property
    def ftp_password(self) -> str:
        return self._env_config.get("FTP_PASSWORD") or self.config["FTP_SOLUTION_FILES"]["ftp_password"]

    def as_dict(self) -> dict:
        """Return all config parameters as a dict (ENV values take priority)."""
        return {
            "API_KEY": self.api_key,
            "API_ENDPOINT": self.api_endpoint,
            "API_SECRET": self.api_secret,
            "FTP_HOSTNAME": self.ftp_hostname,
            "FTP_USERNAME": self.ftp_username,
            "FTP_PASSWORD": self.ftp_password,
            "solver_version": self.solver_version,
            "solver_path": self.solver_path,
        }