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

import platform
# pylint: disable=E0401
import gdb
import calltrace2_binutils

class PrintEvent :
    """
    https://sourceware.org/gdb/onlinedocs/gdb/Basic-Python.html
    """
    def __init__(self, string, log) :
        self._string = string
        self._log = log

    def __call__(self) :
        if self._log is not None :
            self._log.write(self._string + "\n")
        else :
            gdb.write(self._string + "\n", gdb.STDOUT)

class EntryBreak(gdb.Breakpoint) :
    """
    https://sourceware.org/gdb/onlinedocs/gdb/Breakpoints-In-Python.html
    """
    def __init__(self, name, addr, calltrace) :
        super().__init__(name, internal=True)
        self._name = name
        self._addr = addr
        self._calltrace = calltrace

    def stop(self) :
        if not self.enabled :
            return False
        self._calltrace.entry_append(self._name, self._addr)
        try :
            ExitBreak(self._name, self._calltrace, self)
        except ValueError :
            print(f"Cannot set FinishBreakpoint for {self._name}")
        return False

class ExitBreak(gdb.FinishBreakpoint) :
    """
    https://sourceware.org/gdb/onlinedocs/gdb/Finish-Breakpoints-in-Python.html#Finish-Breakpoints-in-Python
    """
    def __init__(self, name, calltrace, entry) :
        super().__init__(internal=True)
        self._name = name
        self._calltrace = calltrace
        self._entry = entry

    def out_of_scope(self) :
        print(f"exit breakpoint for {self._name} out of scope")
        if self._entry.enabled :
            self._calltrace.exit_append(self._name, fake=True)

    def stop(self) :
        if self._entry.enabled :
            self._calltrace.exit_append(self._name)
        return False

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

    def entry_append(self, name, addr) :
        self._depth += 1
        outstr = ("*" * self._depth) + " > " + name
        if self._sourceinfo :
            outstr += f" [[{self.binutils.addr2line(self.elf, addr)}]]"
        gdb.post_event(PrintEvent(outstr, self._log))

    def exit_append(self, name, fake=False) :
        outstr = ("*" * self._depth) + " < " + name
        if not fake :
            pc = gdb.execute("print/x $pc", to_string=True)
            addr = int(pc.split()[2], 16)
            if not self._minimal :
                outstr += f"@0x{addr:x}"
            if self._sourceinfo :
                outstr += f"  [[{self.binutils.addr2line(self.elf, addr)}]]"
        else :
            outstr += " (return out of scope)"
        gdb.post_event(PrintEvent(outstr, self._log))
        if self._depth > 0 :
            self._depth -= 1

    def finish(self, event) :
        print(f"Execution finished, exit code {event.exit_code:d}")
        if self._log is not None :
            print(f"results written to {self._log.name}")
            self._log.close()
            self._log = None

    def invoke(self, arg, from_tty) :
        args = gdb.string_to_argv(arg)
        if len(args) == 0 :
            gdb.execute("r")
        else :
            parse_args_switch = {
                "minimal" : self._parse_minimal_args,
                "nominimal" : self._parse_nominimal_args,
                "log" : self._parse_log_args,
                "sourceinfo" : self._parse_sourceinfo_args,
                "nosourceinfo" : self._parse_nosourceinfo_args,
                "disable" : self._parse_disable_args,
                "break" : self._parse_break_args,
            }
            parse_args_switch[args[0]](args, from_tty)

    def _parse_minimal_args(self, _args, _from_tty) :
        self._minimal = True
        self._sourceinfo = False
        self._enable_breakpoints(value=True)

    def _parse_nominimal_args(self, _args, _from_tty) :
        self._minimal = False
        self._enable_breakpoints(value=True)

    def _parse_log_args(self, args, _from_tty) :
        if len(args) == 1 :
            self._log = None
            self._enable_breakpoints(value=True)
        elif len(args) == 2 :
            print(f"setting log to {args[1]}")
            self._log = open(args[1], "w", encoding='utf8')
            self._enable_breakpoints(value=True)

    def _parse_sourceinfo_args(self, _args, _from_tty) :
        self._sourceinfo = True
        self._enable_breakpoints(value=True)

    def _parse_nosourceinfo_args(self, _args, _from_tty) :
        self._sourceinfo = False
        self._enable_breakpoints(value=True)

    def _parse_disable_args(self, _args, _from_tty) :
        self._enable_breakpoints(value=False)

    def _parse_break_args(self, args, _from_tty) :
        print(f"adding breakpoint for {args[1]}")
        info_addr = gdb.execute(f"info address {args[1]}", to_string=True)
        addr = info_addr.split()[-1].rstrip('.')
        self._breakpoints.append(EntryBreak(args[1], int(addr, 16), self))

    def _enable_breakpoints(self, value : bool) :
        for bp in self._breakpoints :
            bp.enabled = value

CallTrace()
