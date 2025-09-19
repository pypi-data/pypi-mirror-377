#!/usr/bin/python3
"""
Copyright (c) 2025 Penterep Security s.r.o.

ptvulns is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ptvulns is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ptvulns.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import importlib
import os
import threading
import subprocess
import shutil
import itertools
import time
import json
import hashlib
import sys; sys.path.append(__file__.rsplit("/", 1)[0])

from types import ModuleType
from urllib.parse import urlparse, urlunparse
from ptlibs import ptjsonlib, ptmisclib, ptnethelper
from ptlibs.ptprinthelper import ptprint, print_banner, help_print, get_colored_text
from ptlibs.threads import ptthreads, printlock
from ptlibs.http.http_client import HttpClient

from helpers._thread_local_stdout import ThreadLocalStdout
from helpers.helpers import Helpers

from _version import __version__

class PtVulns:
    def __init__(self, args):
        self.args        = args
        self.ptjsonlib   = ptjsonlib.PtJsonLib()
        self.http_client = HttpClient(args=self.args, ptjsonlib=self.ptjsonlib)
        self.helpers     = Helpers(args=self.args, ptjsonlib=self.ptjsonlib, http_client=self.http_client)


    def _check_if_db_loaded(self):
        """Check if cpe .db file is loaded with data"""
        current_file = os.path.abspath(__file__)
        db_file = os.path.join(os.path.dirname(current_file), '3rd_party', 'cpe_search', 'cpe-search-dictionary.db3')

        if not os.path.exists(db_file):
            raise FileNotFoundError(f"Database file not found: {db_file}")

        file_size = os.path.getsize(db_file)  # velikost v bajtech
        size_mb = file_size / (1024 * 1024)

        if size_mb < 300:
            print(f"Loading DB ({size_mb:.2f} MB) gonna take a while...")

        #print(f"Database file is loaded, size: {file_size / (1024*1024):.2f} MB")

    def run(self) -> None:
        """Main method"""
        current_file = os.path.abspath(__file__)

        #self._check_if_db_loaded()
        self.cpe_search_path = os.path.join(os.path.dirname(current_file), '3rd_party', 'cpe_search', 'cpe_search.py')
        self.cve_search_path = os.path.join(os.path.dirname(current_file), '3rd_party', 'cve-search', 'cve_finder', '__main__.py')

        cpe = self.args.search
        if not self.is_cpe(cpe):
            # call string to automat that creates cpe and return the cpe string
            result = self.call_external_script([sys.executable, self.cpe_search_path, "-q", self.args.search])
            cpe = self.parse_cpe_from_result(result)
            ptprint(f"CPE: {cpe}", "TITLE", not self.args.json)
            #print(f"\nGot cpe: {cpe}\n{'-'*60}")


        # TODO:
        # call python skript with the cpe with json option
        # parse json, add data to ptjsonlib
        #ptprint(f"Running cve_finder..", "TITLE", not self.args.json)

        result = self.call_external_script([sys.executable, self.cve_search_path, "--cpe", cpe, "--no-ssl-verify"])
        path = self.get_latest_combined_report_path()
        self.print_cve_report(path)


        self.ptjsonlib.set_status("finished")
        ptprint(self.ptjsonlib.get_result_json(), "", self.args.json)

    def _get_latest_combined_report_file(self):
        self.cve_search_path = os.path.join(os.path.dirname(current_file), '3rd_party', 'cve-search', 'cve_finder', '__main__.py')

    def print_cve_report(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        cpe_list = data.get("cpe_list", [])
        for cpe in cpe_list:
            entries = data.get(cpe, [])
            if entries:
                self.ptjsonlib.add_vulnerability("PTV-WEB-SW-KNOWNVULN")

            for entry in entries:
                cve_id = entry["id"]["selected"]
                date = entry["date_published"]["selected"]
                score = entry["score"]["average"]
                desc = entry["desc"]["selected"]

                ptprint(f"CVE: {cve_id}", "TEXT", not self.args.json)
                ptprint(f"Published: {date}", "TEXT", not self.args.json)
                ptprint(f"Score: {score}", "TEXT", not self.args.json)
                ptprint(f"Description: {desc}\n", "TEXT", not self.args.json)

                """
                ptprint(f"CVE: {cve_id}", "TITLE", not self.args.json)
                ptprint(f"Published: {date}", "TITLE", not self.args.json)
                ptprint(f"Score: {score}", "TITLE", not self.args.json)
                ptprint(f"Description: {desc}\n", "TITLE", not self.args.json)
                """

                node = self.ptjsonlib.create_node_object(node_type="cve", properties={"cve": cve_id, "published": date, "score": score, "description": desc})
                self.ptjsonlib.add_node(node)

    def get_latest_combined_report_path(self, path=None):
        # folder where reports are stored
        folder = os.path.join(os.path.dirname(__file__), "json_reports")

        # if no specific file path is provided, find the oldest combined_report
        if path is None:
            # list all files starting with "combined_report_"
            files = [f for f in os.listdir(folder) if f.startswith("combined_report_")]

            if not files:
                raise FileNotFoundError("No combined_report_ files found in json_reports folder.")

            # select the oldest file based on the lexicographical order of the date part
            oldest_file = min(files, key=lambda f: f[len("combined_report_"):])
            path = os.path.join(folder, oldest_file)

        # here you can open/process the file at 'path'
        #print(f"Opening combined report: {path}")
        return path


    def parse_cpe_from_result(self, result):
        if result:
            if "could not find software for query:" in result.stdout.lower():
                self.ptjsonlib.end_error(f"No CPE found for query: {self.args.search}", condition=self.args.json)
            cpe = result.stdout.strip()
            return cpe
        else:
            self.ptjsonlib.end_error(f"Error parsing CPE from query: {self.args.search}", condition=self.args.json)

    def is_cpe(self, string: str) -> bool:
        """Check if string is a valid CPE 2.3 formatted string"""
        if not string.startswith("cpe:2.3:"):
            return False

        parts = string.split(":")
        # cpe:2.3:<part>:<vendor>:<product>:<version>:<update>:<edition>:<language>:<sw_edition>:<target_sw>:<target_hw>:<other>
        if len(parts) != 13:
            return False

        part = parts[2]
        if part not in ("a", "o", "h"):  # a = application, o = OS, h = hardware
            return False

        return True

    def call_external_script(self, subprocess_args: list) -> None:
        def spinner_func(stop_event):
            spinner = itertools.cycle(["|", "/", "-", "\\"])
            spinner_dots = itertools.cycle(["."] * 5 + [".."] * 6 + ["..."] * 7)
            if not self.args.json:
                sys.stdout.write("\033[?25l")  # Hide cursor
                sys.stdout.flush()
            while not stop_event.is_set():
                ptprint(get_colored_text(f"[{next(spinner)}] ", "TITLE") + f"ptvulns is running, please wait {next(spinner_dots)}", "TEXT", not self.args.json, end="\r", flush=True, clear_to_eol=True, colortext="TITLE")
                #ptprint(f"    ptvulns is running, please wait {next(spinner_dots)}", "TEXT", not self.args.json, end="\r", flush=True, clear_to_eol=True, colortext="TITLE")
                time.sleep(0.1)
            ptprint(f" ", "TEXT", not self.args.json, flush=True, clear_to_eol=True)
            #ptprint(" ", "TEXT", not self.args.json, flush=True, clear_to_eol=True)

        if self.args.verbose:
            #ptprint(f"ptvulns is running, please wait:", "TITLE", not self.args.json, flush=True, clear_to_eol=True, colortext=True, end="")
            if not self.args.json:
                sys.stdout.write("\033[?25l")  # Hide cursor
        #else:
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(target=spinner_func, args=(stop_spinner,))
        #ptprint(f" ", "TEXT", not self.args.json, end="\n", flush=True, clear_to_eol=True)
        spinner_thread.start()
        try:
            result = subprocess.run(
                subprocess_args,
                #check=True,
                #bufsize=1,
                #suniversal_newlines=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            return result

        except subprocess.CalledProcessError as e:
            self.ptjsonlib.end_error("Raised exception:", details=e, condition=self.args.json)

        finally:
            stop_spinner.set()
            spinner_thread.join()
            if not self.args.json:
                sys.stdout.write("\033[?25h")  # Show cursor
            #if not self.args.verbose:
                #stop_spinner.set()
                #spinner_thread.join()

    def run_single_module(self, module_name: str) -> None:
        """
        Safely loads and executes a specified module's `run()` function.

        The method locates the module file in the "modules" directory, imports it dynamically,
        and executes its `run()` method with provided arguments and a shared `ptjsonlib` object.
        It also redirects stdout/stderr to a thread-local buffer for isolated output capture.

        If the module or its `run()` method is missing, or if an error occurs during execution,
        it logs appropriate messages to the user.

        Args:
            module_name (str): The name of the module (without `.py` extension) to execute.
        """
        try:
            module = _import_module_from_path(module_name)

            if hasattr(module, "run") and callable(module.run):
                buffer = StringIO()
                self.thread_local_stdout.set_thread_buffer(buffer)
                try:
                    module.run(
                        args=self.args,
                        ptjsonlib=self.ptjsonlib,
                        helpers=self.helpers,
                        ptvulns_result=self.ptvulns_result
                    )

                except Exception as e:
                    print(e)
                    error = e
                else:
                    error = None
                finally:
                    self.thread_local_stdout.clear_thread_buffer()
                    ptprint(buffer.getvalue(), "TEXT", not self.args.json, end="\n")
            else:
                ptprint(f"Module '{module_name}' does not have 'run' function", "WARNING", not self.args.json)

        except FileNotFoundError as e:
            ptprint(f"Module '{module_name}' not found", "ERROR", not self.args.json)
        except Exception as e:
            ptprint(f"Error running module '{module_name}': {e}", "ERROR", not self.args.json)



def _import_module_from_path(module_name: str) -> ModuleType:
    """
    Dynamically imports a Python module from a given file path.

    This method uses `importlib` to load a module from a specific file location.
    The module is then registered in `sys.modules` under the provided name.

    Args:
        module_name (str): Name under which to register the module.

    Returns:
        ModuleType: The loaded Python module object.

    Raises:
        ImportError: If the module cannot be found or loaded.
    """
    module_path = os.path.join(os.path.dirname(__file__), "modules", f"{module_name}.py")

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise ImportError(f"Cannot find spec for {module_name} at {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def _get_all_available_modules() -> list:
    """
    Returns a list of available Python module names from the 'modules' directory.

    Modules must:
    - Not start with an underscore
    - Have a '.py' extension
    """
    modules_folder = os.path.join(os.path.dirname(__file__), "modules")
    available_modules = [
        f.rsplit(".py", 1)[0]
        for f in sorted(os.listdir(modules_folder))
        if f.endswith(".py") and not f.startswith("_")
    ]
    return available_modules

def get_help():
    """
    Generate structured help content for the CLI tool.

    This function dynamically builds a list of help sections including general
    description, usage, examples, and available options. The list of tests (modules)
    is generated at runtime by scanning the 'modules' directory and reading each module's
    optional '__TESTLABEL__' attribute to describe it.

    Returns:
        list: A list of dictionaries, where each dictionary represents a section of help
              content (e.g., description, usage, options). The 'options' section includes
              available command-line flags and dynamically discovered test modules.
    """

    # Build dynamic help from available modules
    def _get_available_modules_help() -> list:
        rows = []
        available_modules = _get_all_available_modules()
        modules_folder = os.path.join(os.path.dirname(__file__), "modules")
        for module in available_modules:
            mod = _import_module_from_path(module)
            label = getattr(mod, "__TESTLABEL__", f"Test for {module.upper()}")
            row = ["", "", f" {module.upper()}", label.rstrip(':')]
            rows.append(row)
        return sorted(rows, key=lambda x: x[2])

    return [
        #{"description": ["ptvulns"]},
        {"usage": ["ptvulns <options>"]},
        {"usage_example": [
            "ptvulns -u https://www.example.com",
        ]},
        {"options": [
            ["-s",  "--search",                 "<search>",        "Search string for vulns"],
            #["-ts", "--tests",                  "<test>",     "Specify one or more tests to perform:"],
            #*_get_available_modules_help(),
            #["", "", "", ""],
            ["-vv", "--verbose",                "",                 "Show verbose output"],
            ["-v",  "--version",                "",                 "Show script version and exit"],
            ["-h",  "--help",                   "",                 "Show this help message and exit"],
            ["-j",  "--json",                   "",                 "Output in JSON format"],
        ]
        }]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help="False", description=f"{SCRIPTNAME} <options>")
    parser.add_argument("-s",  "--search",         type=str, required=True)
    parser.add_argument("-vv", "--verbose",        action="store_true")
    parser.add_argument("-j",  "--json",           action="store_true")
    parser.add_argument("-v",  "--version",        action='version', version=f'{SCRIPTNAME} {__version__}')

    parser.add_argument("--socket-address",          type=str, default=None)
    parser.add_argument("--socket-port",             type=str, default=None)
    parser.add_argument("--process-ident",           type=str, default=None)

    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptprint(help_print(get_help(), SCRIPTNAME, __version__))
        sys.exit(0)

    args = parser.parse_args()

    print_banner(SCRIPTNAME, __version__, args.json, 0)
    return args

def main():
    global SCRIPTNAME
    SCRIPTNAME = os.path.splitext(os.path.basename(__file__))[0]
    args = parse_args()
    script = PtVulns(args)
    script.run()

if __name__ == "__main__":
    main()
