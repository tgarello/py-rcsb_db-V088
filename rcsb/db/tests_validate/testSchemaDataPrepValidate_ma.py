##
# File:    SchemaDataPrepValidateTests.py
# Author:  J. Westbrook
# Date:    9-Jun-2018
# Version: 0.001
#
# Update:
#  7-Sep-2018 jdw add multi-level (strict/min) validation tests
# 29-Sep-2018 jdw add plugin for extended checks of JSON Schema formats.
# 31-Mar-2019 jdw add option to validate  'addParentRefs'
#
##
"""
Tests for utilities employed to construct local schema and json schema defintions from
dictionary metadata and user preference data, and to further apply these schema to
validate instance data.

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import glob
import logging
import os
import time
import unittest

from jsonschema import Draft4Validator
from jsonschema import FormatChecker

from mmcif.api.DictMethodRunner import DictMethodRunner
from rcsb.db.define.DictionaryApiProviderWrapper import DictionaryApiProviderWrapper
from rcsb.db.helpers.DictMethodResourceProvider import DictMethodResourceProvider
from rcsb.db.processors.DataTransformFactory import DataTransformFactory
from rcsb.db.processors.SchemaDefDataPrep import SchemaDefDataPrep
from rcsb.db.utils.RepositoryProvider import RepositoryProvider
from rcsb.db.utils.SchemaProvider import SchemaProvider
from rcsb.utils.config.ConfigUtil import ConfigUtil
from rcsb.utils.io.MarshalUtil import MarshalUtil

import shutil

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

HERE = None
TOPDIR = None
TMP_PATH = None

def set_cif2json_path(new_tmp_path):
    global TMP_PATH
    print(f'new temp file{new_tmp_path}')
    TMP_PATH = new_tmp_path

def chunkList(seq, size):
    return (seq[i::size] for i in range(size))


class SchemaDataPrepValidateTests(unittest.TestCase):
    def setUp(self):
        self.__numProc = 2
        # self.__fileLimit = 200
        self.__fileLimit = None
        self.__mockTopPath = os.path.join(TOPDIR, "rcsb", "mock-data")
        self.__cachePath = os.path.join(TOPDIR, "CACHE")
        self.__configPath = os.path.join(TOPDIR, "rcsb", "db", "config", "exdb-config-example-ma.yml")
        configName = "site_info_configuration"
        self.__configName = configName
        self.__cfgOb = ConfigUtil(configPath=self.__configPath, defaultSectionName=configName, mockTopPath=self.__mockTopPath)
        self.__mU = MarshalUtil(workPath=self.__cachePath)

        self.__schP = SchemaProvider(self.__cfgOb, self.__cachePath, useCache=False, rebuildFlag=True)
        self.__rpP = RepositoryProvider(cfgOb=self.__cfgOb, numProc=self.__numProc, fileLimit=self.__fileLimit, cachePath=self.__cachePath)
        #
        self.__birdRepoPath = self.__cfgOb.getPath("BIRD_REPO_PATH", sectionName=configName)
        #
        self.__fTypeRow = "drop-empty-attributes|drop-empty-tables|skip-max-width|convert-iterables|normalize-enums|translateXMLCharRefs"
        self.__fTypeCol = "drop-empty-tables|skip-max-width|convert-iterables|normalize-enums|translateXMLCharRefs"
        self.__verbose = True
        #
        self.__modulePathMap = self.__cfgOb.get("DICT_METHOD_HELPER_MODULE_PATH_MAP", sectionName=configName)
        self.__testDirPath = os.path.join(HERE, "test-output", "pdbx-files")
        self.__testMaDirPath = os.path.join(HERE, "test-output", "ma-files")
        self.__export = True
        #
        #self.__extraOpts = None
        # The following for extended parent/child info -
        self.__extraOpts = 'addParentRefs|addPrimaryKey'
        #
        self.__alldatabaseNameD = {
            "ma": ["ma"],
            "ihm_dev": ["ihm_dev"],
            "pdbx": ["pdbx", "pdbx_ext"],
            "pdbx_core": ["pdbx_core_entity", "pdbx_core_entry", "pdbx_core_assembly", "pdbx_core_entity_instance", "pdbx_core_entity_instance_validation"],
            "bird": ["bird"],
            "bird_family": ["family"],
            "chem_comp": ["chem_comp"],
            "bird_chem_comp": ["bird_chem_comp"],
            "bird_chem_comp_core": ["bird_chem_comp_core"],
        }

        self.__databaseNameD = {
            "pdbx_core": ["pdbx_core_entity", "pdbx_core_entry", "pdbx_core_assembly", "pdbx_core_entity_instance", "pdbx_core_entity_instance_validation"],
            "bird_chem_comp_core": ["bird_chem_comp_core"],
        }
        self.__mergeContentTypeD = {"pdbx_core": ["vrpt"]}
        # self.__databaseNameD = {"chem_comp_core": ["chem_comp_core"], "bird_chem_comp_core": ["bird_chem_comp_core"]}
        # self.__databaseNameD = {"ihm_dev_full": ["ihm_dev_full"]}
        # self.__databaseNameD = {"pdbx_core": ["pdbx_core_entity_instance_validation"]}
        # self.__databaseNameD = {"pdbx_core": ["pdbx_core_entity_monomer"]}
        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.debug("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testValidateOptsRepo(self):
        # schemaLevel = "min"

        schemaLevel = "full"
        inputPathList = None
        eCount = self.__testValidateOpts(databaseNameD=self.__databaseNameD, inputPathList=inputPathList, schemaLevel=schemaLevel, mergeContentTypeD=self.__mergeContentTypeD)
        logger.info("Total validation errors schema level %s : %d", schemaLevel, eCount)
        self.assertLessEqual(eCount, 1)

    @unittest.skip("Disable troubleshooting test")
    def testValidateOptsList(self):
        schemaLevel = "min"
        inputPathList = self.__mU.doImport(os.path.join(HERE, "test-output", "failed-path.list"), "list")
        # inputPathList = glob.glob(self.__testDirPath + "/*.cif")
        if not inputPathList:
            return True
        databaseNameD = {"pdbx_core": ["pdbx_core_entity", "pdbx_core_entry", "pdbx_core_entity_instance", "pdbx_core_entity_instance_validation"]}
        for ii, subList in enumerate(chunkList(inputPathList[::-1], 40)):
            if ii < 5:
                continue
            eCount = self.__testValidateOpts(databaseNameD=databaseNameD, inputPathList=subList, schemaLevel=schemaLevel, mergeContentTypeD=self.__mergeContentTypeD)
            logger.info("Chunk %d total validation errors schema level %s : %d", ii, schemaLevel, eCount)
        # self.assertGreaterEqual(eCount, 20)

    #@unittest.skip("Disable IHM troubleshooting test")
    def testValidateOptsIhmRepo(self):
        schemaLevel = "min"
        inputPathList = None
        self.__export = True

        databaseNameD = {"ihm_dev_full": ["ihm_dev_full"]}
        databaseNameD = {"ihm_dev": ["ihm_dev"]}
        eCount = self.__testValidateOpts(databaseNameD=databaseNameD, inputPathList=inputPathList, schemaLevel=schemaLevel, mergeContentTypeD=self.__mergeContentTypeD)
        logger.info("Total validation errors schema level %s : %d", schemaLevel, eCount)
        # self.assertGreaterEqual(eCount, 20)
        #

    #@unittest.skip("Disable IHM troubleshooting test")
    def testValidateOptsMaList(self):
        #schemaLevel = "full"
        schemaLevel = "min"

        inputPathList = glob.glob(TMP_PATH + "/*.cif")
        if not inputPathList:
            return True
        #databaseNameD = {"ihm_dev_full": ["ihm_dev_full"]}
        databaseNameD = {"ma": ["ma"]}
        eCount = self.__testValidateOpts(databaseNameD=databaseNameD, inputPathList=inputPathList, schemaLevel=schemaLevel, mergeContentTypeD=self.__mergeContentTypeD)
        logger.info("Total validation errors schema level %s : %d", schemaLevel, eCount)
        # self.assertGreaterEqual(eCount, 20)
        #

    def __testValidateOpts(self, databaseNameD, inputPathList=None, schemaLevel="full", mergeContentTypeD=None):
        #
        eCount = 0
        for databaseName in databaseNameD:
            mergeContentTypes = mergeContentTypeD[databaseName] if databaseName in mergeContentTypeD else None
            _ = self.__schP.makeSchemaDef(databaseName, dataTyping="ANY", saveSchema=True)
            pthList = inputPathList if inputPathList else self.__rpP.getLocatorObjList(databaseName, mergeContentTypes=mergeContentTypes)
            for collectionName in databaseNameD[databaseName]:
                cD = self.__schP.makeSchema(databaseName, collectionName, encodingType="JSON", level=schemaLevel, saveSchema=True, extraOpts=self.__extraOpts)
                #
                dL, cnL = self.__testPrepDocumentsFromContainers(
                    pthList, databaseName, collectionName, styleType="rowwise_by_name_with_cardinality", mergeContentTypes=mergeContentTypes
                )
                # Raises exceptions for schema compliance.
                try:
                    Draft4Validator.check_schema(cD)
                except Exception as e:
                    logger.error("%s %s schema validation fails with %s", databaseName, collectionName, str(e))
                #
                valInfo = Draft4Validator(cD, format_checker=FormatChecker())
                logger.info("Validating %d documents from %s %s", len(dL), databaseName, collectionName)
                for ii, dD in enumerate(dL):
                    logger.debug("Schema %s collection %s document %d", databaseName, collectionName, ii)
                    try:
                        cCount = 0
                        #for error in sorted(valInfo.iter_errors(dD), key=str):
                        #    logger.info("schema %s collection %s (%s) path %s error: %s", databaseName, collectionName, cnL[ii], error.path, error.message)
                        #    logger.debug("Failing document %d : %r", ii, list(dD.items()))
                        #    eCount += 1
                        #    cCount += 1
                        #if cCount > 0:
                        #    logger.info("schema %s collection %s container %s error count %d", databaseName, collectionName, cnL[ii], cCount)
                    except Exception as e:
                        logger.exception("Validation processing error %s", str(e))

        return eCount

    def __testPrepDocumentsFromContainers(self, inputPathList, databaseName, collectionName, styleType="rowwise_by_name_with_cardinality", mergeContentTypes=None):
        """Test case -  create loadable PDBx data from repository files
        """
        try:

            sd, _, _, _ = self.__schP.getSchemaInfo(databaseName)
            #
            dP = DictionaryApiProviderWrapper(self.__cfgOb, self.__cachePath, useCache=False)
            dictApi = dP.getApiByName(databaseName)
            rP = DictMethodResourceProvider(self.__cfgOb, configName=self.__configName, cachePath=self.__cachePath, siftsAbbreviated="TEST")
            dmh = DictMethodRunner(dictApi, modulePathMap=self.__modulePathMap, resourceProvider=rP)
            #
            dtf = DataTransformFactory(schemaDefAccessObj=sd, filterType=self.__fTypeRow)
            sdp = SchemaDefDataPrep(schemaDefAccessObj=sd, dtObj=dtf, workPath=self.__cachePath, verbose=self.__verbose)
            containerList = self.__rpP.getContainerList(inputPathList)
            for container in containerList:
                cName = container.getName()
                logger.debug("Processing container %s", cName)
                dmh.apply(container)
                if self.__export:
                    savePath = os.path.join(HERE, "test-output", cName + "-with-method.cif")
                    #self.__mU.doExport(savePath, [container], fmt="mmcif")
            #
            tableIdExcludeList = sd.getCollectionExcluded(collectionName)
            tableIdIncludeList = sd.getCollectionSelected(collectionName)
            sliceFilter = sd.getCollectionSliceFilter(collectionName)
            sdp.setSchemaIdExcludeList(tableIdExcludeList)
            sdp.setSchemaIdIncludeList(tableIdIncludeList)
            #
            docList, containerNameList, _ = sdp.processDocuments(
                containerList, styleType=styleType, filterType=self.__fTypeRow, dataSelectors=["PUBLIC_RELEASE"], sliceFilter=sliceFilter, collectionName=collectionName
            )

            docList = sdp.addDocumentPrivateAttributes(docList, collectionName)
            docList = sdp.addDocumentSubCategoryAggregates(docList, collectionName)
            #
            mergeS = "-".join(mergeContentTypes) if mergeContentTypes else ""
            if self.__export and docList:
                # for ii, doc in enumerate(docList[:1]):
                for ii, doc in enumerate(docList):
                    cn = containerNameList[ii]
                    fp = os.path.join(TMP_PATH, "prep-%s-%s-%s-%s.json" % (cn, databaseName, collectionName, mergeS))
                    self.__mU.doExport(fp, [doc], fmt="json", indent=3)
                    logger.debug("Exported %r", fp)
            #
            return docList, containerNameList

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def schemaValidateSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(SchemaDataPrepValidateTests("testValidateOptsRepo"))
    # suiteSelect.addTest(SchemaDataPrepValidateTests("testValidateOptsList"))
    return suiteSelect


def schemaMaValidateSuite():
    
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(SchemaDataPrepValidateTests("testValidateOptsMaList"))
    #suiteSelect.addTest(SchemaDataPrepValidateTests("testValidateOptsIhmRepo"))
    return suiteSelect

def convertToJsonMaFiles(dir_path):
    global HERE, TOPDIR, TMP_PATH
    HERE = "/Users/garell0000/py-rcsb_db-V088/rcsb/db/tests_validate"
    TOPDIR = "/Users/garell0000/py-rcsb_db-V088/"
    TMP_PATH = HERE

    # Copy files from dir_path to HERE
    for file in os.listdir(dir_path):
        if file.endswith('.cif'):
            shutil.copy(os.path.join(dir_path, file), HERE)

    
    mySuite = schemaMaValidateSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)

    for file in os.listdir(HERE):
        if file.endswith('.cif'):
            os.remove(os.path.join(HERE, file))

    # Convert files in HERE to JSON and copy them back to dir_path
    for file in os.listdir(HERE):
        if file.endswith('.json'):
            json_file_path = os.path.join(HERE, file)
            shutil.copy(json_file_path, dir_path)
            os.remove(os.path.join(HERE, file))
    return 1


if __name__ == "__main__":
    #mySuite = schemaValidateSuite()
    #unittest.TextTestRunner(verbosity=2).run(mySuite)

    HERE = os.path.abspath(os.path.dirname(__file__))
    TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    
    set_cif2json_path(os.path.join(HERE, 'tmp-dir'))

    mySuite = schemaMaValidateSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
