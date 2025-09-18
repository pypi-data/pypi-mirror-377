# BSD 3-Clause License
# Copyright (c) 2024-2025, The Regents of the University of California (Regents)
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from sdtp import  RemoteSDMLTable, RowTable, InvalidDataException
from sdtp.sdtp_table_factory import RowTableFactory, RemoteSDMLTableFactory,  SDMLTableFactory,TableBuilder
import pytest

def test_table_builder_init():
    assert TableBuilder.table_registry['RowTable'] == {
        'class': RowTableFactory,
        'locked': True
    }
    assert TableBuilder.table_registry['RemoteSDMLTable'] == {
        'class': RemoteSDMLTableFactory,
        'locked': True
    }

def _check_row_table_equal(built_table, original_table):
    assert built_table.rows == original_table.rows
    assert built_table.schema == original_table.schema

def _check_remote_table_equal(built_table, original_table):
    assert built_table.schema == original_table.schema
    assert built_table.url == original_table.url
    assert built_table.table_name == original_table.table_name
    assert built_table.auth == original_table.auth
    assert built_table.header_dict == original_table.header_dict

def test_build():
    row_table = RowTable([{"name": "age", "type": "number"}], [[1], [2]])
    spec = row_table.to_dictionary()
    _check_row_table_equal(RowTableFactory.build_table(spec), row_table)
    _check_row_table_equal(TableBuilder.build_table(spec), row_table)
    spec['schema'].append({"name": "name", "type": "string"})
    with pytest.raises(InvalidDataException):
        t1 = RowTableFactory.build_table(spec)
    remote_table = RemoteSDMLTable('test', spec['schema'], 'https://www.example.com')
    spec = remote_table.to_dictionary()
    _check_remote_table_equal(RemoteSDMLTableFactory.build_table(spec), remote_table)
    _check_remote_table_equal(TableBuilder.build_table(spec), remote_table)
    # auth is checked elsewhere
    remote_table = RemoteSDMLTable('test', spec['schema'], 'https://www.example.com', header_dict = {'foo': 'bar'})
    spec = remote_table.to_dictionary()
    _check_remote_table_equal(RemoteSDMLTableFactory.build_table(spec), remote_table)
    
test_build()

class SDMLTestTableFactory(SDMLTableFactory):
    '''
    A simple SDMLTableFactory to test add_table_factory
    '''
    
    @classmethod
    def build_table(cls, table_spec):
        # Since this is just a test, don't do anything different 
        # than a RowTableFactory and take the same spec
        super().build_table(table_spec)
        return RowTable(table_spec["schema"], table_spec["rows"])
    

def test_add_table_factory():
    
    table_factory = SDMLTestTableFactory()

    
    # test for None
    with pytest.raises(TypeError):
        TableBuilder.register_factory_class(None)
    # test for non-factory
    with pytest.raises(InvalidDataException):
        TableBuilder.register_factory_class('foo', None)
    # test that we can't add SDMLTestTable for "RowTable"
    with pytest.raises(InvalidDataException):
        TableBuilder.register_factory_class('RowTable', SDMLTestTableFactory)
    # test that adding a second 'RowTable' factory is OK
    TableBuilder.register_factory_class('RowTable', RowTableFactory)
    assert TableBuilder.get_factory('RowTable') == RowTableFactory
    TableBuilder.register_factory_class('TestTable', RowTableFactory)
    assert TableBuilder.get_factory('TestTable') == RowTableFactory
    TableBuilder.register_factory_class('TestTable', SDMLTestTableFactory, True)
    assert TableBuilder.get_factory('TestTable') == SDMLTestTableFactory
    with pytest.raises(InvalidDataException):
        TableBuilder.register_factory_class('TestTable', RowTableFactory)
        

