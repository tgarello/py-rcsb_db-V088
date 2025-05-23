##
# File:    PdbxLoaderTests.py
# Author:  J. Westbrook
# Date:    14-Mar-2018
# Version: 0.001
#
# Updates:
#   22-Mar-2018 jdw  Revise all tests
#   23-Mar-2018 jdw  Add reload test cases
#   27-Mar-2018 jdw  Update configuration handling and mocking
#    4-Apr-2018 jdw  Add size pruning tests
#   25-Jul-2018 jdw  Add large test case to test failure and salvage scenarios
#   10-Sep-2018 jdw  Update assert conditions for tests
#   11-Nov-2018 jdw  Add chem_comp_core schema support
#    6-Aug-2019 jdw  Autogenerate schema during tests.
#
##
"""
Tests for creating and loading MongoDb using BIRD, CCD and PDBx/mmCIF data files
and following external schema definitions.

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import logging
import os
import time
import unittest

from rcsb.db.mongo.DocumentLoader import DocumentLoader
from rcsb.db.mongo.PdbxLoader import PdbxLoader
from rcsb.utils.config.ConfigUtil import ConfigUtil

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


class PdbxLoaderTests(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super(PdbxLoaderTests, self).__init__(methodName)
        self.__verbose = True

    def setUp(self):
        #
        #
        mockTopPath = os.path.join(TOPDIR, "rcsb", "mock-data")
        configPath = os.path.join(TOPDIR, "rcsb", "db", "config", "exdb-config-example.yml")
        configName = "site_info_configuration"
        self.__cfgOb = ConfigUtil(configPath=configPath, defaultSectionName=configName, mockTopPath=mockTopPath)
        #
        self.__resourceName = "MONGO_DB"
        self.__failedFilePath = os.path.join(HERE, "test-output", "failed-list.txt")
        self.__cachePath = os.path.join(TOPDIR, "CACHE")
        self.__readBackCheck = True
        self.__numProc = 2
        self.__chunkSize = 10
        self.__fileLimit = None
        self.__documentStyle = "rowwise_by_name_with_cardinality"
        self.__ldList = [
            # {"databaseName": "chem_comp_core", "collectionNameList": None, "loadType": "full", "mergeContentTypes": None, "validationLevel": "min"},
            {"databaseName": "bird_chem_comp_core", "collectionNameList": None, "loadType": "full", "mergeContentTypes": None, "validationLevel": "min"},
            {"databaseName": "bird_chem_comp_core", "collectionNameList": None, "loadType": "replace", "mergeContentTypes": None, "validationLevel": "min"},
            {"databaseName": "pdbx_core", "collectionNameList": None, "loadType": "full", "mergeContentTypes": ["vrpt"], "validationLevel": "min"},
        ]
        #
        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testPdbxLoader(self):
        #
        for ld in self.__ldList:
            self.__pdbxLoaderWrapper(**ld)

    def __pdbxLoaderWrapper(self, **kwargs):
        """ Wrapper for PDBx loader modue
        """
        try:
            logger.info("Loading %s", kwargs["databaseName"])
            mw = PdbxLoader(
                self.__cfgOb,
                cachePath=self.__cachePath,
                resourceName=self.__resourceName,
                numProc=self.__numProc,
                chunkSize=self.__chunkSize,
                fileLimit=None,
                verbose=self.__verbose,
                readBackCheck=self.__readBackCheck,
                maxStepLength=2000,
                useSchemaCache=True,
                rebuildSchemaFlag=False,
            )
            ok = mw.load(
                kwargs["databaseName"],
                collectionLoadList=kwargs["collectionNameList"],
                loadType=kwargs["loadType"],
                inputPathList=None,
                styleType=self.__documentStyle,
                dataSelectors=["PUBLIC_RELEASE"],
                failedFilePath=self.__failedFilePath,
                saveInputFileListPath=None,
                pruneDocumentSize=None,
                logSize=False,
                validationLevel=kwargs["validationLevel"],
                mergeContentTypes=kwargs["mergeContentTypes"],
                useNameFlag=False,
            )
            self.assertTrue(ok)
            ok = self.__loadStatus(mw.getLoadStatus())
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def __loadStatus(self, statusList):
        sectionName = "data_exchange_configuration"
        dl = DocumentLoader(
            self.__cfgOb,
            self.__cachePath,
            resourceName=self.__resourceName,
            numProc=self.__numProc,
            chunkSize=self.__chunkSize,
            documentLimit=None,
            verbose=self.__verbose,
            readBackCheck=self.__readBackCheck,
        )
        #
        databaseName = self.__cfgOb.get("DATABASE_NAME", sectionName=sectionName)
        collectionName = self.__cfgOb.get("COLLECTION_UPDATE_STATUS", sectionName=sectionName)
        ok = dl.load(databaseName, collectionName, loadType="append", documentList=statusList, indexAttributeList=["update_id", "database_name", "object_name"], keyNames=None)
        return ok


def mongoLoadPdbxSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(PdbxLoaderTests("testPdbxLoader"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = mongoLoadPdbxSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
