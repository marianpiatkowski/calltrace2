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

import sys
import subprocess
from abc import ABC, abstractmethod

if sys.version_info < (3, 6) :
    print("Python 3.6 or higher is required for calltrace2", file=sys.stderr)
    sys.exit(1)

class BinUtils(ABC) :
    @abstractmethod
    def addr2line(self, elf, addr, verbose=False) -> str :
        pass

    @abstractmethod
    def get_function_names(self, elf, verbose=False) :
        pass

class MacOSBinUtils(BinUtils) :
    def addr2line(self, elf, addr, verbose=False) -> str :
        cmd = f"gaddr2line -e {elf} {addr:x}"
        output = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n')
        if verbose :
            print(output)
        return output.replace(":", "::")

    def get_function_names(self, elf, verbose=False) :
        cmds = [f"gobjdump -w -t {elf}", "awk '$4 == \"FUN\"'", "c++filt"]
        cmd = " | ".join(cmds)
        if verbose :
            print("executing: " + cmd)
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding='utf8')
        output = process.communicate()[0]
        output = output.rstrip('\n').split('\n')
        results = []
        for line in output :
            if not line :
                continue
            line_splitted = line.split()
            if len(line_splitted) < 7 :
                continue
            addr = int(line_splitted[0], 16)
            name = " ".join(line_splitted[6:])
            if addr != 0 :
                results.append((name, addr))
        return results

class LinuxBinUtils(BinUtils) :
    def addr2line(self, elf, addr, verbose=False) -> str :
        cmd = f"addr2line -e {elf} {addr:x}"
        output = subprocess.check_output(cmd, shell=True, encoding='utf8').rstrip('\n')
        if verbose :
            print(output)
        return output.replace(":", "::")

    def get_function_names(self, elf, verbose=False) :
        cmds = [f"readelf -W -s {elf}", "awk '$4 == \"FUNC\"'", "c++filt"]
        cmd = " | ".join(cmds)
        if verbose :
            print("executing: " + cmd)
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding='utf8')
        output = process.communicate()[0]
        output = output.rstrip('\n').split('\n')
        results = []
        for line in output :
            if not line :
                continue
            line_splitted = line.split()
            if len(line_splitted) < 8 :
                continue
            addr = int(line_splitted[1], 16)
            name = " ".join(line_splitted[7:])
            if addr != 0 :
                results.append((name, addr))
        return results

class BinUtilsFactory :
    def __init__(self) :
        self._binutilizers = {
            'Darwin' : MacOSBinUtils,
            'Linux' : LinuxBinUtils, }

    def register_platform(self, platform_sys, binutilizer) :
        self._binutilizers[platform_sys] = binutilizer

    def get_binutilizer(self, platform_sys) :
        binutilizer = self._binutilizers.get(platform_sys)
        if not binutilizer :
            raise ValueError(platform_sys)
        return binutilizer()
