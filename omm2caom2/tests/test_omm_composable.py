# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2018.                            (c) 2018.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
#  $Revision: 4 $
#
# ***********************************************************************
#

import os

from mock import Mock, patch

from astropy.io import fits

from omm2caom2 import omm_composable, omm_footprint_augmentation
from omm2caom2 import omm_preview_augmentation, manage_composable
from caom2utils import fits2caom2
from caom2 import obs_reader_writer, SimpleObservation, Algorithm
from omm2caom2 import CadcException, OmmName


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
TESTDATA_DIR = os.path.join(THIS_DIR, 'data')


def test_meta_execute():
    test_obs_id = 'test_obs_id'
    test_dir = os.path.join(THIS_DIR, test_obs_id)

    # clean up from previous tests
    if os.path.exists(test_dir):
        for ii in os.listdir(test_dir):
            os.remove(os.path.join(test_dir, ii))
        os.rmdir(test_dir)
    netrc = os.path.join(THIS_DIR, 'test_netrc')
    assert os.path.exists(netrc)

    # mocks for this test
    fits2caom2._get_cadc_meta = Mock(return_value={'size': 37,
            'md5sum': 'e330482de75d5c4c88ce6f6ef99035ea',
            'type': 'applicaton/octect-stream'})
    fits2caom2.get_cadc_headers = Mock(side_effect=_get_headers)

    test_config = manage_composable.Config()
    test_config.working_directory = THIS_DIR
    test_config.collection = 'OMM'
    test_config.netrc_file = 'test_netrc'
    test_config.work_file = 'todo.txt'
    test_config.logging_level = 'DEBUG'

    # run the test
    with patch('subprocess.Popen') as subprocess_mock:
        subprocess_mock.return_value.communicate.side_effect = _communicate
        test_executor = omm_composable.Omm2Caom2Meta(test_config, test_obs_id)
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e

    # check that things worked as expected
    assert fits2caom2._get_cadc_meta.called


def test_meta_local_execute():
    test_obs_id = 'test_obs_id'
    test_output_fname = os.path.join(TESTDATA_DIR,
                                     OmmName(test_obs_id).get_model_file_name())

    # clean up from previous tests
    if os.path.exists(test_output_fname):
        os.remove(test_output_fname)
    netrc = os.path.join(TESTDATA_DIR, 'test_netrc')
    assert os.path.exists(netrc)

    # mocks for this test
    meta_orig = fits2caom2._get_file_meta
    fits2caom2._get_file_meta = Mock(return_value={'size': 37,
                                                   'md5sum': 'e330482de75d5c4c88ce6f6ef99035ea',
                                                   'type': 'applicaton/octect-stream'})
    headers_orig = fits2caom2._get_headers_from_fits
    fits2caom2._get_headers_from_fits = Mock(side_effect=_get_file_headers)

    test_config = manage_composable.Config()
    test_config.working_directory = TESTDATA_DIR
    test_config.collection = 'OMM'
    test_config.netrc_file = 'test_netrc'
    test_config.logging_level = 'INFO'

    # run the test
    with patch('subprocess.Popen') as subprocess_mock:
        subprocess_mock.return_value.communicate.side_effect = _communicate
        test_executor = omm_composable.Omm2Caom2LocalMeta(
            test_config, test_obs_id)
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e

    # check that things worked as expected
    # assert fits2caom2._get_headers_from_fits.called
    assert fits2caom2._get_cadc_meta.called
    assert os.path.exists(test_output_fname)

    fits2caom2._get_headers_from_fits = headers_orig
    fits2caom2._get_file_meta = meta_orig


def test_data_execute():
    test_obs_id = 'TEST_OBS_ID'
    test_dir = os.path.join(THIS_DIR, test_obs_id)
    test_fits_fqn = os.path.join(test_dir,
                                 OmmName(test_obs_id).get_file_name())
    os.mkdir(test_dir)
    precondition = open(test_fits_fqn, 'w')
    precondition.close()

    omm_footprint_augmentation.visit = Mock()
    omm_preview_augmentation.visit = Mock()
    obs_reader_writer.ObservationReader.read = Mock(side_effect=_read_obs)

    test_config = manage_composable.Config()
    test_config.working_directory = THIS_DIR
    test_config.collection = 'OMM'
    test_config.netrc_file = 'test_netrc'
    test_config.work_file = 'todo.txt'
    test_config.logging_level = 'DEBUG'

    # run the test
    with patch('subprocess.Popen') as subprocess_mock:
        subprocess_mock.return_value.communicate.side_effect = _communicate
        test_executor = omm_composable.Omm2Caom2Data(test_config, test_obs_id)
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e

    # check that things worked as expected - cleanup should have occurred
    assert omm_footprint_augmentation.visit.called
    assert omm_preview_augmentation.visit.called


def test_data_local_execute():
    test_obs_id = 'test_obs_id'

    omm_footprint_augmentation.visit = Mock()
    omm_preview_augmentation.visit = Mock()
    obs_reader_writer.ObservationReader.read = Mock(side_effect=_read_obs)

    test_config = manage_composable.Config()
    test_config.working_directory = THIS_DIR
    test_config.collection = 'OMM'
    test_config.netrc_file = 'test_netrc'
    test_config.work_file = 'todo.txt'
    test_config.logging_level = 'DEBUG'

    # run the test
    with patch('subprocess.Popen') as subprocess_mock:
        subprocess_mock.return_value.communicate.side_effect = _communicate
        test_executor = omm_composable.Omm2Caom2LocalData(test_config,
                                                          test_obs_id)
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e

    # check that things worked as expected - no cleanup
    assert omm_footprint_augmentation.visit.called
    assert omm_preview_augmentation.visit.called


def test_data_store():
    test_obs_id = 'test_obs_id'

    test_config = manage_composable.Config()
    test_config.working_directory = THIS_DIR
    test_config.collection = 'OMM'
    test_config.netrc_file = 'test_netrc'
    test_config.work_file = 'todo.txt'
    test_config.logging_level = 'DEBUG'

    # run the test
    with patch('subprocess.Popen') as subprocess_mock:
        subprocess_mock.return_value.communicate.side_effect = _communicate
        test_executor = omm_composable.Omm2Caom2Store(test_config,
                                                      test_obs_id)
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e


def test_scrape():
    test_obs_id = 'test_obs_id'
    test_output_fname = os.path.join(TESTDATA_DIR,
                                     OmmName(test_obs_id).get_model_file_name())

    # clean up from previous tests
    if os.path.exists(test_output_fname):
        os.remove(test_output_fname)
    netrc = os.path.join(TESTDATA_DIR, 'test_netrc')
    assert os.path.exists(netrc)

    # mocks for this test
    headers_orig = fits2caom2._get_headers_from_fits
    fits2caom2._get_headers_from_fits = Mock(side_effect=_get_file_headers)

    test_config = manage_composable.Config()
    test_config.working_directory = TESTDATA_DIR
    test_config.collection = 'OMM'
    test_config.netrc_file = 'test_netrc'
    test_config.logging_level = 'INFO'

    # run the test
    with patch('subprocess.Popen') as subprocess_mock:
        subprocess_mock.return_value.communicate.side_effect = _communicate
        test_executor = omm_composable.Omm2Caom2Scrape(
            test_config, test_obs_id)
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e

    # check that things worked as expected
    assert fits2caom2._get_headers_from_fits.called
    assert os.path.exists(test_output_fname)

    fits2caom2._get_headers_from_fits = headers_orig


def test_data_scrape_execute():
    test_obs_id = 'test_obs_id'

    omm_footprint_augmentation.visit = Mock()
    omm_preview_augmentation.visit = Mock()
    obs_reader_writer.ObservationReader.read = Mock(side_effect=_read_obs)

    test_config = manage_composable.Config()
    test_config.working_directory = THIS_DIR
    test_config.collection = 'OMM'
    test_config.netrc_file = 'test_netrc'
    test_config.work_file = 'todo.txt'
    test_config.logging_level = 'DEBUG'

    # run the test
    with patch('subprocess.Popen') as subprocess_mock:
        subprocess_mock.return_value.communicate.side_effect = _communicate
        test_executor = omm_composable.Omm2Caom2DataScrape(test_config,
                                                          test_obs_id)
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e

    # check that things worked as expected - no cleanup
    assert omm_footprint_augmentation.visit.called
    assert omm_preview_augmentation.visit.called


def test_organize_executes():
    test_obs_id = 'test_obs_id'
    test_config = manage_composable.Config()
    test_config.working_directory = THIS_DIR
    test_config.collection = 'OMM'
    test_config.netrc_file = 'test_netrc'
    test_config.work_file = 'todo.txt'
    test_config.logging_level = 'DEBUG'
    test_config.use_local_files = True

    test_config.task_types = [manage_composable.TaskType.SCRAPE]
    test_oe = omm_composable.OrganizeExecutes(test_config)
    executors = test_oe.choose(test_obs_id)
    assert executors is not None
    assert len(executors) == 1
    assert isinstance(executors[0], omm_composable.Omm2Caom2Scrape)

    test_config.task_types = [manage_composable.TaskType.STORE,
                              manage_composable.TaskType.INGEST,
                              manage_composable.TaskType.ENHANCE]
    test_oe = omm_composable.OrganizeExecutes(test_config)
    executors = test_oe.choose(test_obs_id)
    assert executors is not None
    assert len(executors) == 3
    assert isinstance(executors[0], omm_composable.Omm2Caom2Store)
    assert isinstance(executors[1], omm_composable.Omm2Caom2LocalMeta)
    assert isinstance(executors[2], omm_composable.Omm2Caom2LocalData)

    test_config.use_local_files = False
    test_config.task_types = [manage_composable.TaskType.INGEST,
                              manage_composable.TaskType.ENHANCE]
    test_oe = omm_composable.OrganizeExecutes(test_config)
    executors = test_oe.choose(test_obs_id)
    assert executors is not None
    assert len(executors) == 2
    assert isinstance(executors[0], omm_composable.Omm2Caom2Meta)
    assert isinstance(executors[1], omm_composable.Omm2Caom2Data)

    test_config.task_types = [manage_composable.TaskType.SCRAPE,
                              manage_composable.TaskType.ENHANCE]
    test_config.use_local_files = True
    test_oe = omm_composable.OrganizeExecutes(test_config)
    executors = test_oe.choose(test_obs_id)
    assert executors is not None
    assert len(executors) == 2
    assert isinstance(executors[0], omm_composable.Omm2Caom2Scrape)
    assert isinstance(executors[1], omm_composable.Omm2Caom2DataScrape)


def _communicate():
    return ['return status', None]


def _get_headers(uri, subject):
    x = """SIMPLE  =                    T / Written by IDL:  Fri Oct  6 01:48:35 2017      
BITPIX  =                  -32 / Bits per pixel                                 
NAXIS   =                    2 / Number of dimensions                           
NAXIS1  =                 2048 /                                                
NAXIS2  =                 2048 /                                                
DATATYPE= 'REDUC   '           /Data type, SCIENCE/CALIB/REJECT/FOCUS/TEST
END
"""
    delim = '\nEND'
    extensions = \
        [e + delim for e in x.split(delim) if e.strip()]
    headers = [fits.Header.fromstring(e, sep='\n') for e in extensions]
    return headers


def _get_test_metadata(subject, path):
    return {'size': 37,
            'md5sum': 'e330482de75d5c4c88ce6f6ef99035ea',
            'type': 'applicaton/octect-stream'}


def _read_obs(arg1):
    return SimpleObservation(collection='test_collection',
                             observation_id='test_obs_id',
                             algorithm=Algorithm(str('exposure')))


def _get_file_headers(fname):
    return _get_headers(None, None)
