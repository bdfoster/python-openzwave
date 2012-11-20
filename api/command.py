# -*- coding: utf-8 -*-
"""
.. module:: openzwave.command

This file is part of **python-openzwave** project http://code.google.com/p/python-openzwave.
    :platform: Unix, Windows, MacOS X
    :sinopsis: openzwave wrapper

.. moduleauthor:: bibi21000 aka Sébastien GALLET <bibi21000@gmail.com>

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
import libopenzwave
from collections import namedtuple
import thread
from threading import Timer
import time
import logging
from openzwave.object import ZWaveException, ZWaveCommandClassException
from openzwave.object import ZWaveObject, NullLoggingHandler, ZWaveNodeInterface
from openzwave.group import ZWaveGroup

logging.getLogger('openzwave').addHandler(logging.NullHandler())

class ZWaveNodeBasic(ZWaveNodeInterface):
    '''
    Represents an interface to BasicCommands
    I known it's not necessary as they can be included in the node directly.
    But it's a good starting point.

    What I want to do is provide an automatic mapping system hidding
    the mapping classes.

    First example, the battery level, it's not a basic command but don't care.
    Its command class is 0x80.

    A user should write

        if self.handle_command_class(class_id):

            ret=commandclass(...)

    The classic way to do it is a classique method of registering. But

    Another way : using heritage multiple

    ZWaveNode(ZWaveObject, ZWaveNodeBasic, ....)
    The interface will implement methods
    command_class_0x80(paramm1,param2,...)
    That's the first thing to do
    We also can define a property wtih a fiendly name

    handle_command_class will do the rest

    Another way to do it :
    A node can manage actuators (switch, dimmer, ...)
    and sensors (temperature, consommation, temperature)

    So we need a kind of mechanism to retrive commands in a user friendly way
    Same for sensors.

    A good use caser is the AN158 Plug-in Meter Appliance Module
    We will study the following command classes :
    'COMMAND_CLASS_SWITCH_ALL', 'COMMAND_CLASS_SWITCH_BINARY',
    'COMMAND_CLASS_METER',

    the associated values are :

    COMMAND_CLASS_SWITCH_ALL : {
        72057594101481476L: {
            'help': '',
            'max': 0L,
            'ispolled': False,
            'units': '',
            'data': 'On and Off Enabled',
            'min': 0L,
            'writeonly': False,
            'label': 'Switch All',
            'readonly': False,
            'data_str': 'On and Off Enabled',
            'type': 'List'}
    }

    COMMAND_CLASS_SWITCH_BINARY : {
        72057594093060096L: {
            'help': '',
            'max': 0L,
            'ispolled': False,
            'units': '',
            'data': False,
            'min': 0L,
            'writeonly': False,
            'label': 'Switch',
            'readonly': False,
            'data_str': False,
            'type': 'Bool'}
    }

    COMMAND_CLASS_METER : {
        72057594093273600L: {
            'help': '',
            'max': 0L,
            'ispolled': False,
            'units': '',
            'data': False,
            'min': 0L,
            'writeonly': False,
            'label': 'Exporting',
            'readonly': True,
            'data_str': False,
            'type': 'Bool'},
        72057594101662232L: {
            'help': '',
            'max': 0L,
            'ispolled': False,
            'units': '',
            'data': 'False',
            'min': 0L,
            'writeonly': True,
            'label': 'Reset',
            'readonly': False,
            'data_str': 'False',
            'type': 'Button'},
        72057594093273090L: {
            'help': '',
            'max': 0L,
            'ispolled': False,
            'units': 'kWh',
            'data': 0.0,
            'min': 0L,
            'writeonly': False,
            'label': 'Energy',
            'readonly': True,
            'data_str': 0.0,
            'type': 'Decimal'},
        72057594093273218L: {
            'help': '',
            'max': 0L,
            'ispolled': False,
            'units': 'W',
            'data': 0.0,
            'min': 0L,
            'writeonly': False,
            'label': 'Power',
            'readonly': True,
            'data_str': 0.0,
            'type': 'Decimal'}
    }

    Another example from an homepro dimmer (not congifured in openzwave):
    COMMAND_CLASS_SWITCH_MULTILEVEL : {
        72057594109853736L: {
            'help': '',
            'max': 0L,
            'ispolled': False,
            'units': '',
            'data': 'False',
            'min': 0L,
            'writeonly': True,
            'label': 'Dim',
            'readonly': False,
            'data_str': 'False',
            'type': 'Button'},
        72057594109853697L: {
            'help': '',
            'max': 255L,
            'ispolled': False,
            'units': '',
            'data': 69,
            'min': 0L,
            'writeonly': False,
            'label': 'Level',
            'readonly': False,
            'data_str': 69,
            'type': 'Byte'},
        72057594118242369L: {
            'help': '',
            'max': 255L,
            'ispolled': False,
            'units': '',
            'data': 0,
            'min': 0L,
            'writeonly': False,
            'label': 'Start Level',
            'readonly': False,
            'data_str': 0,
            'type': 'Byte'},
        72057594109853720L: {
            'help': '',
            'max': 0L,
            'ispolled': False,
            'units': '',
            'data': 'False',
            'min': 0L,
            'writeonly': True,
            'label': 'Bright',
            'readonly': False,
            'data_str': 'False',
            'type': 'Button'},
        72057594118242352L: {
            'help': '',
            'max': 0L,
            'ispolled': False,
            'units': '',
            'data': False,
            'min': 0L,
            'writeonly': False,
            'label': 'Ignore Start Level',
            'readonly': False,
            'data_str': False,
            'type': 'Bool'}
    }

    What about the conclusion :

        The COMMAND_CLASS_SWITCH_ALL is defined with the same label and
        use a list as parameter. This should be a configuration parameter.
        Don't know what to do for this command class

        The COMMAND_CLASS_SWITCH_BINARY use a bool as parameter while
        COMMAND_CLASS_SWITCH_MULTILEVEL use 2 buttons : Dim and Bright.
        Dim and Bright must be done in 2 steps : set the level and activate
        the button.

        So we must add one or more lines in the actuators :

        Switch : {setter:self.set_command_class_0xYZ(valueId, new), getter:}
        We must find a way to access the value directly

        Bright
        Dim

        So for the COMMAND_CLASS_SWITCH_BINARY we must define a function called
        Switch (=the label of the value). What happen if we have 2 switches
        on the node : 2 values I suppose.

        COMMAND_CLASS_SWITCH_MULTILEVEL uses 2 commands : 4 when 2 dimmers on the
        done ? Don't know but it can.

        COMMAND_CLASS_METER export many values : 2 of them sends a decimal
        and are readonly. They also have a Unit defined ans values are readonly

        COMMAND_CLASS_METER are used for sensors only. So we would map
        every values entries as defined before

        Programming :
        get_switches : retrieve the list of switches on the node
        is_switch (label) : says if the value with label=label is a switch
        get_switch (label) : retrive the value where label=label
    '''


    def get_battery_level(self, value_id=None):
        """
        The battery level of this node.
        The command 0x80 (COMMAND_CLASS_BATTERY) of this node.

        :param value_id: The value to retrieve state. If None, retrieve the first value
        :type value_id: int
        :return: The level of this battery
        :rtype: int
        """
        #print value_id
        if value_id == None:
            for val in self.get_battery_levels():
                return self.values[val].data
        elif value_id in self.get_battery_levels():
                return self.values[value_id].data
        return None

    def get_battery_levels(self):
        """
        The command 0x80 (COMMAND_CLASS_BATTERY) of this node.
        Retrieve the list of values to consider as batteries.
        Filter rules are :

            command_class = 0x80
            genre = "User"
            type = "Byte"
            readonly = True
            writeonly = False

        :return: The list of switches on this node
        :rtype: dict()
        """
        return self.get_values(class_id=0x80, genre='User', \
        type='Byte', readonly=True, writeonly=False)

    def get_power_level(self, value_id=None):
        """
        The power level of this node.
        The command 0x73 (COMMAND_CLASS_POWERLEVEL) of this node.

        :param value_id: The value to retrieve state. If None, retrieve the first value
        :type value_id: int
        :return: The level of this battery
        :rtype: int
        """
        #print value_id
        if value_id == None:
            for val in self.get_power_levels():
                return self.values[val].data
        elif value_id in self.get_power_levels():
                return self.values[value_id].data
        return None

    def get_power_levels(self):
        """
        The command 0x73 (COMMAND_CLASS_POWERLEVEL) of this node.
        Retrieve the list of values to consider as power_levels.
        Filter rules are :

            command_class = 0x73
            genre = "User"
            type = "Byte"
            readonly = True
            writeonly = False

        :return: The list of switches on this node
        :rtype: dict()
        """
        return self.get_values(class_id=0x73, genre='User', \
        type='Byte', readonly=True, writeonly=False)

class ZWaveNodeSwitch(ZWaveNodeInterface):
    '''
    Represents an interface to switches and dimmers Commands

    '''

    def get_switches_all(self):
        """
        The command 0x27 (COMMAND_CLASS_SWITCH_ALL) of this node.
        Retrieve the list of values to consider as switches_all.
        Filter rules are :

            command_class = 0x27
            genre = "System"
            type = "List"
            readonly = False
            writeonly = False

        :return: The list of switches on this node
        :rtype: dict()

        """
        return self.get_values(class_id=0x27, genre='System', \
        type='List', readonly=False, writeonly=False)

    def set_switch_all(self, value_id, value):
        """
        The command 0x27 (COMMAND_CLASS_SWITCH_ALL) of this node.
        Set switches_all to value (using value value_id).

        :param value_id: The value to retrieve state
        :type value_id: int
        :param value: A predifined string
        :type value: str

        """
        #print value_id
        if value_id in self.get_switches_all():
            self.values[value_id].data = value
            return True
        return False

    def get_switch_all_item(self, value_id):
        """
        The command 0x27 (COMMAND_CLASS_SWITCH_ALL) of this node.
        Return the current value (using value value_id) of a switch_all.

        :param value_id: The value to retrieve switch_all value
        :type value_id: int
        :return: The value of the value
        :rtype: str

        """
        #print value_id
        if value_id in self.get_switches_all():
            return self.values[value_id].data
        return None

    def get_switch_all_items(self, value_id):
        """
        The command 0x27 (COMMAND_CLASS_SWITCH_ALL) of this node.
        Return the all the possible values (using value value_id) of a switch_all.

        :param value_id: The value to retrieve items list
        :type value_id: int
        :return: The value of the value
        :rtype: set()

        """
        #print value_id
        if value_id in self.get_switches_all():
            return self.values[value_id].data_items
        return None

    def get_switches(self):
        """
        The command 0x25 (COMMAND_CLASS_SWITCH_BINARY) of this node.
        Retrieve the list of values to consider as switches.
        Filter rules are :

            command_class = 0x25
            genre = "User"
            type = "Bool"
            readonly = False
            writeonly = False

        :return: The list of switches on this node
        :rtype: dict()

        """
        return self.get_values(class_id=0x25, genre='User', \
        type='Bool', readonly=False, writeonly=False)

    def set_switch(self, value_id, value):
        """
        The command 0x25 (COMMAND_CLASS_SWITCH_BINARY) of this node.
        Set switch to value (using value value_id).

        :param value_id: The value to retrieve state
        :type value_id: int
        :param value: True or False
        :type value: bool

        """
        #print value_id
        if value_id in self.get_switches():
            self.values[value_id].data = value
            return True
        return False

    def get_switch_state(self, value_id):
        """
        The command 0x25 (COMMAND_CLASS_SWITCH_BINARY) of this node.
        Return the state (using value value_id) of a switch.

        :param value_id: The value to retrieve state
        :type value_id: int
        :return: The state of the value
        :rtype: bool

        """
        #print value_id
        if value_id in self.get_switches():
            return self.values[value_id].data
        return None

    def get_dimmers(self):
        """
        The command 0x26 (COMMAND_CLASS_SWITCH_MULTILEVEL) of this node.
        Retrieve the list of values to consider as dimmers.
        Filter rules are :

            command_class = 0x26
            genre = "User"
            type = "Bool"
            readonly = False
            writeonly = False

        :return: The list of dimmers on this node
        :rtype: dict()

        """
        return self.get_values(class_id=0x26, genre='User', \
        type='Byte', readonly=False, writeonly=False)

    def set_dimmer(self, value_id, value):
        """
        The command 0x26 (COMMAND_CLASS_SWITCH_MULTILEVEL) of this node.
        Set switch to value (using value value_id).

        :param value_id: The value to retrieve state
        :type value_id: int
        :param value: The level : a value between 0-99 or 255. 255 set the level to the last value. \
        0 turn the dimmer off
        :type value: int

        """
        #print value_id
        #logging.debug("set_dimmer type Level:%s" % (type(value)))
        logging.debug("set_dimmer Level:%s" % (value))
        if value_id in self.get_dimmers():
            if value >99 and value <255 :
                value = 99
            elif value < 0 :
                value = 0
            #logging.debug("set_dimmer corrected Level:%s" % (value))
            self.values[value_id].data = value
            #Dimmers doesn't return the good level.
            #Add a Timer to refresh the value
            if value == 0:
                timer = Timer(2, self.values[value_id].refresh())
                timer = Timer(4, self.values[value_id].refresh())
            return True
        return False

    def get_dimmer_level(self, value_id):
        """
        The command 0x26 (COMMAND_CLASS_SWITCH_MULTILEVEL) of this node.
        Get the dimmer level (using value value_id).

        :param value_id: The value to retrieve level
        :type value_id: int
        :return: The level : a value between 0-99
        :rtype: int

        """
        #print value_id
        if value_id in self.get_dimmers():
            return self.values[value_id].data
        return None

class ZWaveNodeSensor(ZWaveNodeInterface):
    '''
    Represents an interface to Sensor Commands

    '''

    def get_sensors(self):
        """
        The command 0x30 (COMMAND_CLASS_SENSOR_BINARY) of this node.
        The command 0x31 (COMMAND_CLASS_SENSOR_MULTILEVEL) of this node.
        The command 0x32 (COMMAND_CLASS_METER) of this node.
        Retrieve the list of values to consider as sensors.
        Filter rules are :

            command_class = 0x30-32
            genre = "User"
            readonly = True
            writeonly = False

        :return: The list of switches on this node
        :rtype: dict()

        """
        values = {}
        values.update(self.get_values(class_id=0x30, genre='User', \
            readonly=True, writeonly=False))
        values.update(self.get_values(class_id=0x31, genre='User', \
            readonly=True, writeonly=False))
        values.update(self.get_values(class_id=0x32, genre='User', \
            readonly=True, writeonly=False))
        return values

    def get_sensor_value(self, value_id):
        """
        The command 0x30 (COMMAND_CLASS_SENSOR_BINARY) of this node.
        The command 0x31 (COMMAND_CLASS_SENSOR_MULTILEVEL) of this node.
        The command 0x32 (COMMAND_CLASS_METER) of this node.

        :param value_id: The value to retrieve value
        :type value_id: int
        :return: The state of the sensors
        :rtype: variable

        """
        #print value_id
        if value_id in self.get_sensors():
            return self.values[value_id].data
        return None

class ZWaveNodeSecurity(ZWaveNodeInterface):
    '''
    Represents an interface to Security Commands

    '''

    def get_protections(self):
        """
        The command 0x75 (COMMAND_CLASS_PROTECTION) of this node.
        Retrieve the list of values to consider as protection.
        Filter rules are :

            command_class = 0x75
            genre = "User"
            readonly = True
            writeonly = False

        :return: The list of switches on this node
        :rtype: dict()

        """
        return self.get_values(class_id=0x75, genre='System', \
            type='List', readonly=False, writeonly=False)

    def set_protection(self, value_id, value):
        """
        The command 0x75 (COMMAND_CLASS_PROTECTION) of this node.
        Set protection to value (using value value_id).

        :param value_id: The value to set protection
        :type value_id: int
        :param value: A predifined string
        :type value: str

        """
        #print value_id
        if value_id in self.get_protections():
            self.values[value_id].data = value
            return True
        return False

    def get_protection_item(self, value_id):
        """
        The command 0x75 (COMMAND_CLASS_PROTECTION) of this node.
        Return the current value (using value value_id) of a protection.

        :param value_id: The value to retrieve protection value
        :type value_id: int
        :return: The value of the value
        :rtype: str

        """
        #print value_id
        if value_id in self.get_protections():
            return self.values[value_id].data
        return None

    def get_protection_items(self, value_id):
        """
        The command 0x75 (COMMAND_CLASS_PROTECTION) of this node.
        Return the all the possible values (using value value_id) of a protection.

        :param value_id: The value to retrieve items list
        :type value_id: int
        :return: The value of the value
        :rtype: set()

        """
        #print value_id
        if value_id in self.get_protections():
            return self.values[value_id].data_items
        return None
