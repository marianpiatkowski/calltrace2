# -*- python-indent-offset: 4 -*-
"""
Copyright (C) 2022-  Marian Piatkowski

This file is a part of calltrace2.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

# Execute the following before running gdb:
# export PYTHONPATH=$PWD:$PYTHONPATH

# export PYTHONPATH=''

import gdb
import platform
import calltrace2_binutils

class EntryBreak(gdb.Breakpoint) :
    """
    https://sourceware.org/gdb/onlinedocs/gdb/Breakpoints-In-Python.html
    """
    def __init__(self, name, addr, calltrace) :
        super().__init__(name, internal=True)
        self._name = name
        self._addr = addr
        self._calltrace = calltrace

class ExitBreak(gdb.FinishBreakpoint) :
    """
    https://sourceware.org/gdb/onlinedocs/gdb/Finish-Breakpoints-in-Python.html#Finish-Breakpoints-in-Python
    """
    pass

class CallTrace(gdb.Command) :
    """
    https://sourceware.org/gdb/onlinedocs/gdb/CLI-Commands-In-Python.html#CLI-Commands-In-Python
    """
    def __init__(self) :
        super().__init__("calltrace", gdb.COMMAND_DATA)
        self._depth = 0
        self._log = None
        self._minimal = False
        self._sourceinfo = False
        self._breakpoints = None
        self.elf = gdb.current_progspace().filename
        self.binutils = \
            calltrace2_binutils.BinUtilsFactory().get_binutilizer(platform.system())
        gdb.execute("set python print-stack full")
        gdb.execute("set pagination off")
        gdb.execute("set height unlimited")
        self.setup_breakpoints()
        self.setup_exit_handler()

    def setup_breakpoints(self) :
        if self.elf is None :
            return
        print("Searching symbol table for functions, this may take a while...")
        functions = self.binutils.get_function_names(self.elf)
        self._breakpoints = [ EntryBreak(name, addr, self) for name, addr in functions ]
        print("...done")

    def setup_exit_handler(self) :
        gdb.events.exited.connect(self.finish)

    def finish(self, event) :
        try :
            print(f"Execution finished, exit code {event.exit_code:d}")
        except Exception :
            print("Execution finished")
        if self._log is not None :
            print(f"results written to {self._log.name}")
            self._log.close()
            self._log = None

    def invoke(self, arg, from_tty) :
        # TODO Marian: finish this
        pass

CallTrace()
