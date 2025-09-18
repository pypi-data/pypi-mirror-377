"""
Small library to track and log the declaration of new (setup) variables.

Usage example:

    from SetupVariableTracker import SetupVariableTracker
    vtrack = SetupVariableTracker(locals())

    ##################################################
    # Define parameters for this script
    setup_variable_1 = "Hello"
    setup_variable_2 = "World!"
    foo = 1
    bar = None
    ##################################################
    # Create a summary of all newly defined variables
    summary_content = vtrack.save(locals(), sort=True)
    print(summary_content)

More information on https://github.com/Aypac/VariableTracker
@author René Vollmer
"""

from tabulate import tabulate  # Library for formatting text tables
from types import ModuleType
import time
from typing import Union

class SetupVariableTracker:
    base_vars = None

    def __init__(self, locals_c, delete: bool = False, verbose: bool = False):
        self._verbose = verbose
        # Clean up previously defined vars
        self._print("> Determining variables defined prior...")
        self.base_vars = list(locals_c.keys())[:]
        if delete:
            for k in self.base_vars:
                if k not in ['base_vars', 'dict', 'locals', 'ModuleType'] and not isinstance(locals_c[k], ModuleType):
                    if k[0] != '_' and k in self.base_vars:
                        try:
                            del self.base_vars[k]
                            exec(f"del {k:s}")
                        except:
                            pass
                del k

    def _print(self, msg):
        if self._verbose:
            print(msg)

    def get_hash(self, locals_c, hash_size: int = 4):
        """
        Generate a MD5 hash value of all variables.

        :param locals_c:  return value of built-in locals() function
        :param hash_size: Size of the hash to be generated
        :return: hash
        """
        import hashlib
        vs = self.get_variables(locals_c=locals_c, sort=True)
        return hashlib.blake2b(str(vs).encode(), digest_size=hash_size).hexdigest()

    def get_variables(self, locals_c, sort: bool = False):
        """
        Generates a list of defined variables.

        :param locals_c: return value of built-in locals() function
        :param sort: Sort the variables by name?
        :return: List of newly defined variable names and their values
        """
        self._print("> Determining newly defined variables...")
        new_vars = list(locals_c.keys())[:]
        new_vars = [k for k in new_vars if k not in self.base_vars]

        nv = dict(locals_c)

        if sort:
            new_vars.sort(key=str.lower)
        items = [[k, nv[k]] for k in new_vars if not isinstance(locals_c[k], type(self))]
        return items

    def get_table(self, locals_c, sort: bool = False, add_hash: bool = False):
        self._print("> Generate variable overview...")
        items = self.get_variables(locals_c, sort=sort)
        if add_hash:
            items.append(['hash of all variables', self.get_hash(locals_c)])
        return tabulate(items, headers=['Parameter', 'Value'], tablefmt="rst")

    def save(self, locals_c, filename=None, sort: bool = False, add_hash: bool = False):
        if not filename:
            from datetime import datetime
            filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_SetupVariables.log"

        import codecs
        cont = self.get_table(locals_c=locals_c, sort=sort, add_hash=add_hash)
        with codecs.open(filename, 'w', 'utf-8') as f:
            f.write(cont)
            f.flush()
        return cont



class Timekeeper:
    start_timestamp: float
    last_timestamp: dict

    def __init__(self):
        self.start_timestamp = time.time()
        self.last_timestamp = {}
        self.touch()

    def touch(self, slot=0):
        self.last_timestamp[slot] = time.time()

    def total_elapsed_time(self) -> str:
        self.touch()
        return Timekeeper.format_time(time.time() - self.start_timestamp)

    def diff_elapsed_time(self, short: bool = True, touch: bool = True, slot=0) -> str:
        t: str = ""
        if slot in self.last_timestamp:
            t = Timekeeper.format_time(time.time() - self.last_timestamp[slot], short=short)

        if touch:
            self.touch(slot)
        return t

    @staticmethod
    def format_time(delta: Union[float, int], short: bool = False) -> str:
        h = int(delta / 3600)
        m = int(delta / 60)
        s = ""
        if not short or h > 0:
            s += f"{h:02d}:"
        if not short or m > 0 or h > 0:
            s += f"{m:02d}:"
        else:
            return f"{delta % 60:.3f}s"
        return s + f"{delta % 60:06.3f}"
