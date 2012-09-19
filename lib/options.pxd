"""
This file is part of **python-openzwave** project http://code.google.com/p/python-openzwave.

License : GPL(v3)

**python-openzwave** is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

**python-openzwave** is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with python-openzwave. If not, see http://www.gnu.org/licenses.

"""
from libc.stdint cimport uint32_t, uint64_t, int32_t, int16_t, uint8_t, int8_t
from mylibc cimport string
from libcpp cimport bool

cdef extern from "Options.h" namespace "OpenZWave":
    cdef cppclass Options:
        bool Lock()
        bool AddOptionBool( string name, bool default )
        bool AddOptionInt( string name, int32_t default )
        bool AddOptionString( string name, string default, bool append )

cdef extern from "Options.h" namespace "OpenZWave::Options":
    Options* Create(string a, string b, string c)

