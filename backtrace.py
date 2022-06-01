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

# pylint: disable=E0401
import gdb

class BackTrace(gdb.Command) :
    def __init__(self) :
        super().__init__("writebt", gdb.COMMAND_STACK)
        self._outfile = "out_backtrace.org"

    def invoke(self, arg, from_tty) :
        args = gdb.string_to_argv(arg)
        old_frame_args = gdb.parameter("print frame-arguments")
        if len(args) == 1 :
            self._outfile = args[0]
        try :
            gdb.execute("set print frame-arguments presence")
        except gdb.error :
            print("Ignoring undefined item 'frame-arguments presence'")
            print("Setting to 'frame-arguments none'")
            gdb.execute("set print frame-arguments none")
        self._write_bt_stack()
        gdb.execute(f"set print frame-arguments {old_frame_args}")

    def _write_bt_stack(self) :
        bt_output = gdb.execute("bt", to_string=True)
        bt_stack = bt_output.split("\n")
        with open(self._outfile, 'w', encoding='utf8') as outputfile :
            outputfile.write("#+STARTUP: showall\n")
            outputfile.write("\n")
            stack_elem_top = bt_stack[0].split()
            self._write_bt_line(outputfile, stack_elem_top[1:])
            for stack_elem in bt_stack[1:-1] :
                self._write_bt_line(outputfile, stack_elem.split()[2:])

    @staticmethod
    def _write_bt_line(outputfile, stack_elem) :
        outputfile.write("* " + " ".join(stack_elem[0:-2]) + "\n")
        outputfile.write("  file:" + stack_elem[-1].replace(":", "::", 1) + "\n")
        outputfile.write("\n")

BackTrace()
