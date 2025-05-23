##
# File:    DictMethodEntryHelper.py (DictMethodRunnerHelper.py)
# Author:  J. Westbrook
# Date:    18-Aug-2018
# Version: 0.001 Initial version
#
#
# Updates:
#  4-Sep-2018 jdw add methods to construct entry and entity identier categories.
# 10-Sep-2018 jdw add method for citation author aggregation
# 22-Sep-2018 jdw add method assignAssemblyCandidates()
# 27-Oct-2018 jdw add method consolidateAccessionDetails()
# 30-Oct-2018 jdw add category methods addChemCompRelated(), addChemCompInfo(),
#                 addChemCompDescriptor()
# 10-Nov-2018 jdw add addChemCompSynonyms(), addChemCompTargets(), filterBlockByMethod()
# 12-Nov-2018 jdw add InChIKey matching in addChemCompRelated()
# 15-Nov-2018 jdw add handling for antibody misrepresentation of multisource organisms
# 28-Nov-2018 jdw relax constraints on the production of rcsb_entry_info
#  1-Dec-2018 jdw add ncbi source and host organism info
# 11-Dec-2018 jdw add addStructRefSeqEntityIds and buildEntityPolySeq
# 10-Jan-2019 jdw better handle initialization in filterBlockByMethod()
# 11-Jan-2019 jdw revise classification in assignAssemblyCandidates()
# 16-Feb-2019 jdw add buildContainerEntityInstanceIds()
# 19-Feb-2019 jdw add internal method __addPdbxValidateAsymIds() to add cardinal identifiers to
#                 pdbx_validate_* categories
# 28-Feb-2019 jdw change criteria for adding rcsb_chem_comp_container_identiers to work with ion definitions
# 11-Mar-2019 jdw replace taxonomy file handling with calls to TaxonomyUtils()
# 11-Mar-2019 jdw add EC lineage using EnzymeDatabaseUtils()
# 17-Mar-2019 jdw add support for entity subcategory rcsb_macromolecular_names_combined
# 23-Mar-2019 jdw change criteria chem_comp collection criteria to _chem_comp.pdbx_release_status
# 25-Mar-2019 jdw remap merged taxons and adjust exception handling for taxonomy lineage generation
#  7-Apr-2019 jdw add CathClassificationUtils and CathClassificationUtils and sequence difference type counts
# 25-Apr-2019 jdw For source and host organism add ncbi_parent_scientific_name
#                 add rcsb_entry_info.deposited_modeled_polymer_monomer_count and
#                     rcsb_entry_info.deposited_unmodeled_polymer_monomer_count,
#  1-May-2019 jdw add support for _rcsb_entry_info.deposited_polymer_monomer_count,
#                   _rcsb_entry_info.polymer_entity_count_protein,
#                   _rcsb_entry_info.polymer_entity_count_nucleic_acid,
#                   _rcsb_entry_info.polymer_entity_count_nucleic_acid_hybrid,
#                   _rcsb_entry_info.polymer_entity_count_DNA,
#                   _rcsb_entry_info.polymer_entity_count_RNA,
#                   _rcsb_entry_info.nonpolymer_ligand_entity_count
#                   _rcsb_entry_info.selected_polymer_entity_types
#                   _rcsb_entry_info.polymer_entity_taxonomy_count
#                   _rcsb_entry_info.assembly_count
#                    add categories rcsb_entity_instance_domain_scop and rcsb_entity_instance_domain_cath
#  4-May-2019 jdw extend content in categories rcsb_entity_instance_domain_scop and rcsb_entity_instance_domain_cath
# 13-May-2019 jdw add rcsb_entry_info.deposited_polymer_entity_instance_count and deposited_nonpolymer_entity_instance_count
#                 add entity_poly.rcsb_non_std_monomer_count and rcsb_non_std_monomers
# 15-May-2019 jdw add _rcsb_entry_info.na_polymer_entity_types update enumerations for _rcsb_entry_info.selected_polymer_entity_types
# 19-May-2019 jdw add method __getStructConfInfo()
# 21-May-2019 jdw handle odd ordering of records in struct_ref_seq_dif.
#
##
"""
Helper class implements entry-level method references in the RCSB dictionary extension.

All data accessors and structures here refer to dictionary category and attribute names.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import logging

from mmcif.api.DataCategory import DataCategory

logger = logging.getLogger(__name__)


def cmpElements(lhs, rhs):
    return 0 if (lhs[-1].isdigit() or lhs[-1] in ["R", "S"]) and rhs[0].isdigit() else -1


class DictMethodEntryHelper(object):
    """ Helper class implements entry-level method references in the RCSB dictionary extension.

    """

    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: (dict)  Placeholder for future key-value arguments

        """
        #
        logger.debug("Dictionary entry method helper init with kwargs %r", kwargs)
        self._raiseExceptions = kwargs.get("raiseExceptions", False)
        #
        rP = kwargs.get("resourceProvider")
        self.__commonU = rP.getResource("DictMethodCommonUtils instance") if rP else None
        self.__dApi = rP.getResource("Dictionary API instance (pdbx_core)") if rP else None
        #
        # logger.debug("Dictionary entry method helper init")

    def echo(self, msg):
        logger.info(msg)

    def deferredItemMethod(self, dataContainer, catName, atName, **kwargs):
        """ Placeholder for an item method.
        """
        logger.debug("Called deferred item method for %r %r %r %r", dataContainer.getName(), catName, atName, kwargs)
        return True

    def deferredCategoryMethod(self, dataContainer, catName, **kwargs):
        """ Placeholder for a category method.
        """
        logger.debug("Called deferred category method for %r %r %r", dataContainer.getName(), catName, kwargs)
        return True

    def setDatablockId(self, dataContainer, catName, atName, **kwargs):
        """ Item-level method to set the value of the input item to the current container name.

        Args:
            dataContainer (object): mmif.api.DataContainer object instance
            catName (str): Category name
            atName (str): Attribute name

        Returns:
            bool: True for success or False otherwise
        """
        logger.debug("Starting catName %s atName %s kwargs %r", catName, atName, kwargs)
        try:
            val = dataContainer.getName()
            if not dataContainer.exists(catName):
                dataContainer.append(DataCategory(catName, attributeNameList=[atName]))
            #
            cObj = dataContainer.getObj(catName)
            if not cObj.hasAttribute(atName):
                cObj.appendAttribute(atName)
            #
            rc = cObj.getRowCount()
            numRows = rc if rc else 1
            for ii in range(numRows):
                cObj.setValue(val, atName, ii)
            return True
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False

    def setLoadDateTime(self, dataContainer, catName, atName, **kwargs):
        """Set the value of the input data item with container load date.

        Args:
            dataContainer (object): mmif.api.DataContainer object instance
            catName (str): Category name
            atName (str): Attribute name

        Returns:
            bool: True for success or False otherwise
        """
        logger.debug("Starting catName %s atName %s kwargs %r", catName, atName, kwargs)
        try:
            val = dataContainer.getProp("load_date")
            if not dataContainer.exists(catName):
                dataContainer.append(DataCategory(catName, attributeNameList=[atName]))
            #
            cObj = dataContainer.getObj(catName)
            if not cObj.hasAttribute(atName):
                cObj.appendAttribute(atName)
            #
            rc = cObj.getRowCount()
            numRows = rc if rc else 1
            for ii in range(numRows):
                cObj.setValue(val, atName, ii)
            return True
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False

    def setLocator(self, dataContainer, catName, atName, **kwargs):
        """Set the value of the input data item with container locator path.

        Args:
            dataContainer (object): mmif.api.DataContainer object instance
            catName (str): Category name
            atName (str): Attribute name

        Returns:
            bool: True for success or False otherwise
        """
        logger.debug("Starting catName %s atName %s kwargs %r", catName, atName, kwargs)
        try:
            val = dataContainer.getProp("locator")
            if not dataContainer.exists(catName):
                dataContainer.append(DataCategory(catName, attributeNameList=[atName]))
            #
            cObj = dataContainer.getObj(catName)
            if not cObj.hasAttribute(atName):
                cObj.appendAttribute(atName)
            #
            rc = cObj.getRowCount()
            numRows = rc if rc else 1
            for ii in range(numRows):
                cObj.setValue(val, atName, ii)
            return True
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False

    def setRowIndex(self, dataContainer, catName, atName, **kwargs):
        """Set the values of the input data item with the category row index.

        Args:
            dataContainer (object): mmif.api.DataContainer object instance
            catName (str): Category name
            atName (str): Attribute name

        Returns:
            bool: True for success or False otherwise
        """
        logger.debug("Starting catName %s atName %s kwargs %r", catName, atName, kwargs)
        try:
            if not dataContainer.exists(catName):
                # exit if there is no category to index
                return False
            #
            cObj = dataContainer.getObj(catName)
            if not cObj.hasAttribute(atName):
                cObj.appendAttribute(atName)
            #
            rc = cObj.getRowCount()
            numRows = rc if rc else 1
            for ii, iRow in enumerate(range(numRows), 1):
                # Note - we set the integer value as a string  -
                cObj.setValue(str(ii), atName, iRow)
            return True
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False

    def aggregateCitationAuthors(self, dataContainer, catName, atName, **kwargs):
        """Set the value of the input data item with list of citation authors.

        Args:
            dataContainer (object): mmif.api.DataContainer object instance
            catName (str): Category name

        Returns:
            bool: True for success or False otherwise
        """
        logger.debug("Starting catName %s atName %s kwargs %r", catName, atName, kwargs)
        try:
            if not dataContainer.exists(catName) or not dataContainer.exists("citation_author"):
                return False
            #
            cObj = dataContainer.getObj(catName)
            if not cObj.hasAttribute(atName):
                cObj.appendAttribute(atName)
            citIdL = cObj.getAttributeValueList("id")
            #
            tObj = dataContainer.getObj("citation_author")
            #
            citIdL = list(set(citIdL))
            tD = {}
            for ii, citId in enumerate(citIdL):
                tD[citId] = tObj.selectValuesWhere("name", citId, "citation_id")
            for ii in range(cObj.getRowCount()):
                citId = cObj.getValue("id", ii)
                cObj.setValue("|".join(tD[citId]), atName, ii)
            return True
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False

    def buildContainerEntryIds(self, dataContainer, catName, **kwargs):
        """Load the input category with rcsb_entry_container_identifiers content.

        Args:
            dataContainer (object): mmif.api.DataContainer object instance
            catName (str): Category name

        Returns:
            bool: True for success or False otherwise

        For example:

        loop_
        _rcsb_entry_container_identifiers.entry_id
        _rcsb_entry_container_identifiers.entity_ids
        _rcsb_entry_container_identifiers.polymer_entity_ids_polymer
        _rcsb_entry_container_identifiers.non-polymer_entity_ids
        _rcsb_entry_container_identifiers.assembly_ids
        _rcsb_entry_container_identifiers.rcsb_id
        ...

        """
        logger.debug("Starting catName  %s kwargs %r", catName, kwargs)
        try:
            if not dataContainer.exists("entry"):
                return False
            if not dataContainer.exists(catName):
                dataContainer.append(DataCategory(catName, attributeNameList=["entry_id", "entity_ids", "polymer_entity_ids", "non-polymer_entity_ids", "assembly_ids", "rcsb_id"]))
            #
            cObj = dataContainer.getObj(catName)

            tObj = dataContainer.getObj("entry")
            entryId = tObj.getValue("id", 0)
            cObj.setValue(entryId, "entry_id", 0)
            cObj.setValue(entryId, "rcsb_id", 0)

            #
            tObj = dataContainer.getObj("entity")
            entityIdL = tObj.getAttributeValueList("id")
            cObj.setValue(",".join(entityIdL), "entity_ids", 0)
            #
            #
            pIdL = tObj.selectValuesWhere("id", "polymer", "type")
            tV = ",".join(pIdL) if pIdL else "?"
            cObj.setValue(tV, "polymer_entity_ids", 0)

            npIdL = tObj.selectValuesWhere("id", "non-polymer", "type")
            tV = ",".join(npIdL) if npIdL else "?"
            cObj.setValue(tV, "non-polymer_entity_ids", 0)
            #
            tObj = dataContainer.getObj("pdbx_struct_assembly")
            assemblyIdL = tObj.getAttributeValueList("id") if tObj else []
            tV = ",".join(assemblyIdL) if assemblyIdL else "?"
            cObj.setValue(tV, "assembly_ids", 0)

            return True
        except Exception as e:
            logger.exception("For %s failing with %s", catName, str(e))
        return False

    def consolidateAccessionDetails(self, dataContainer, catName, **kwargs):
        """ Consolidate accession details into the rcsb_accession_info category.

        Args:
            dataContainer (object): mmif.api.DataContainer object instance
            catName (str): Category name

        Returns:
            bool: True for success or False otherwise

        For example:
            For example -
             _rcsb_accession_info.entry_id                1ABC
             _rcsb_accession_info.status_code             REL
             _rcsb_accession_info.deposit_date            2018-01-11
             _rcsb_accession_info.initial_release_date    2018-03-23
             _rcsb_accession_info.major_revision          1
             _rcsb_accession_info.minor_revision          2
             _rcsb_accession_info.revision_date           2018-10-25


            Taking data values from:

            _pdbx_database_status.entry_id                        3OQP
            _pdbx_database_status.deposit_site                    RCSB
            _pdbx_database_status.process_site                    RCSB
            _pdbx_database_status.recvd_initial_deposition_date   2010-09-03
            _pdbx_database_status.status_code                     REL
            _pdbx_database_status.status_code_sf                  REL
            _pdbx_database_status.status_code_mr                  ?
            _pdbx_database_status.status_code_cs                  ?
            _pdbx_database_status.pdb_format_compatible           Y
            _pdbx_database_status.methods_development_category    ?
            _pdbx_database_status.SG_entry                        Y
            #
            loop_
            _pdbx_audit_revision_history.ordinal
            _pdbx_audit_revision_history.data_content_type
            _pdbx_audit_revision_history.major_revision
            _pdbx_audit_revision_history.minor_revision
            _pdbx_audit_revision_history.revision_date
            1 'Structure model' 1 0 2010-10-13
            2 'Structure model' 1 1 2011-07-13
            3 'Structure model' 1 2 2011-07-20
            4 'Structure model' 1 3 2014-11-12
            5 'Structure model' 1 4 2017-10-25
            #
        """
        ##
        try:
            logger.debug("Starting with  %r %r %r", dataContainer.getName(), catName, kwargs)
            #
            # if there is incomplete accessioninformation then exit
            if not (dataContainer.exists("pdbx_database_status") or dataContainer.exists("pdbx_audit_revision_history")):
                return False
            # Create the new target category
            if not dataContainer.exists(catName):
                dataContainer.append(DataCategory(catName, attributeNameList=self.__dApi.getAttributeNameList(catName)))

            cObj = dataContainer.getObj(catName)
            #
            tObj = dataContainer.getObj("pdbx_database_status")
            entryId = tObj.getValue("entry_id", 0)
            statusCode = tObj.getValue("status_code", 0)
            depositDate = tObj.getValue("recvd_initial_deposition_date", 0)
            #
            cObj.setValue(entryId, "entry_id", 0)
            cObj.setValue(statusCode, "status_code", 0)
            cObj.setValue(depositDate, "deposit_date", 0)
            # cObj.setValue(depositDate[:4], "deposit_year", 0)

            #
            tObj = dataContainer.getObj("pdbx_audit_revision_history")
            nRows = tObj.getRowCount()
            # Assuming the default sorting order from the release module -
            releaseDate = tObj.getValue("revision_date", 0)
            minorRevision = tObj.getValue("minor_revision", nRows - 1)
            majorRevision = tObj.getValue("major_revision", nRows - 1)
            revisionDate = tObj.getValue("revision_date", nRows - 1)
            cObj.setValue(releaseDate, "initial_release_date", 0)
            # cObj.setValue(releaseDate[:4], "initial_release_year", 0)
            cObj.setValue(minorRevision, "minor_revision", 0)
            cObj.setValue(majorRevision, "major_revision", 0)
            cObj.setValue(revisionDate, "revision_date", 0)
            #
            return True
        except Exception as e:
            logger.exception("In %s for %s failing with %s", dataContainer.getName(), catName, str(e))
        return False

    def addEntryInfo(self, dataContainer, catName, **kwargs):
        """
        Add  _rcsb_entry_info, for example:
             _rcsb_entry_info.entry_id                      1ABC
             _rcsb_entry_info.polymer_composition           'heteromeric protein'
             _rcsb_entry_info.experimental_method           'multiple methods'
             _rcsb_entry_info.experimental_method_count     2
             _rcsb_entry_info.polymer_entity_count          2
             _rcsb_entry_info.entity_count                  2
             _rcsb_entry_info.nonpolymer_entity_count       2
             _rcsb_entry_info.branched_entity_count         0
             _rcsb_entry_info.software_programs_combined    'Phenix;RefMac'
             ....

        Also add the related field:

        _entity_poly.rcsb_entity_polymer_type

            'Protein'   'polypeptide(D) or polypeptide(L)'
            'DNA'       'polydeoxyribonucleotide'
            'RNA'       'polyribonucleotide'
            'NA-hybrid' 'polydeoxyribonucleotide/polyribonucleotide hybrid'
            'Other'      'polysaccharide(D), polysaccharide(L), cyclic-pseudo-peptide, peptide nucleic acid, or other'
            #
          _rcsb_entry_info.deposited_polymer_monomer_count
          'polymer_entity_count_protein',
          'polymer_entity_count_nucleic_acid',
          'polymer_entity_count_nucleic_acid_hybrid',
          'polymer_entity_count_DNA',
          'polymer_entity_count_RNA',

        """
        try:
            logger.debug("Starting with %r %r %r", dataContainer.getName(), catName, kwargs)
            # Exit if source categories are missing
            if not (dataContainer.exists("exptl") and dataContainer.exists("entity")):
                return False
            #
            # Create the new target category rcsb_entry_info
            if not dataContainer.exists(catName):
                dataContainer.append(DataCategory(catName, attributeNameList=self.__dApi.getAttributeNameList(catName)))
            # --------------------------------------------------------------------------------------------------------
            # catName = rcsb_entry_info
            cObj = dataContainer.getObj(catName)
            #
            # --------------------------------------------------------------------------------------------------------
            #  Filter experimental methods
            #
            xObj = dataContainer.getObj("exptl")
            entryId = xObj.getValue("entry_id", 0)
            methodL = xObj.getAttributeValueList("method")
            methodCount, expMethod = self.__commonU.filterExperimentalMethod(methodL)
            cObj.setValue(entryId, "entry_id", 0)
            cObj.setValue(expMethod, "experimental_method", 0)
            cObj.setValue(methodCount, "experimental_method_count", 0)
            #
            # --------------------------------------------------------------------------------------------------------
            #  Experimental resolution -
            #
            resL = self.__filterExperimentalResolution(dataContainer)
            if resL:
                cObj.setValue(",".join(resL), "resolution_combined", 0)
            #
            # ---------------------------------------------------------------------------------------------------------
            # Consolidate software details -
            #
            swNameL = []
            if dataContainer.exists("software"):
                swObj = dataContainer.getObj("software")
                swNameL.extend(swObj.getAttributeUniqueValueList("name"))
            if dataContainer.exists("pdbx_nmr_software"):
                swObj = dataContainer.getObj("pdbx_nmr_software")
                swNameL.extend(swObj.getAttributeUniqueValueList("name"))
            if dataContainer.exists("em_software"):
                swObj = dataContainer.getObj("em_software")
                swNameL.extend(swObj.getAttributeUniqueValueList("name"))
            if swNameL:
                cObj.setValue(";".join(swNameL), "software_programs_combined", 0)
            # ---------------------------------------------------------------------------------------------------------
            #  ENTITY FEATURES
            #
            #  entity and polymer entity counts -
            ##
            eObj = dataContainer.getObj("entity")
            eTypeL = eObj.getAttributeValueList("type")
            #
            numPolymers = 0
            numNonPolymers = 0
            numBranched = 0
            numSolvent = 0
            for eType in eTypeL:
                if eType == "polymer":
                    numPolymers += 1
                elif eType == "non-polymer":
                    numNonPolymers += 1
                elif eType == "branched":
                    numBranched += 1
                elif eType == "water":
                    numSolvent += 1
                else:
                    logger.error("Unexpected entity type for %s %s", dataContainer.getName(), eType)
            totalEntities = numPolymers + numNonPolymers + numBranched + numSolvent
            #
            # Simplified entity polymer type: 'Protein', 'DNA', 'RNA', 'NA-hybrid', or 'Other'
            pTypeL = []
            if dataContainer.exists("entity_poly"):
                epObj = dataContainer.getObj("entity_poly")
                pTypeL = epObj.getAttributeValueList("type")
                #
                atName = "rcsb_entity_polymer_type"
                if not epObj.hasAttribute(atName):
                    epObj.appendAttribute(atName)
                for ii in range(epObj.getRowCount()):
                    epObj.setValue(self.__commonU.filterEntityPolyType(pTypeL[ii]), atName, ii)
            #
            # Add any branched entity types to the type list -
            if dataContainer.exists("entity_branch"):
                ebObj = dataContainer.getObj("entity_branch")
                pTypeL.extend(ebObj.getAttributeValueList("type"))
            #
            polymerCompClass, ptClass, naClass, eptD = self.__commonU.getPolymerComposition(pTypeL)
            #

            cObj.setValue(polymerCompClass, "polymer_composition", 0)
            cObj.setValue(ptClass, "selected_polymer_entity_types", 0)
            cObj.setValue(naClass, "na_polymer_entity_types", 0)
            cObj.setValue(numPolymers, "polymer_entity_count", 0)
            cObj.setValue(numNonPolymers, "nonpolymer_entity_count", 0)
            cObj.setValue(numBranched, "branched_entity_count", 0)
            cObj.setValue(numSolvent, "solvent_entity_count", 0)
            cObj.setValue(totalEntities, "entity_count", 0)
            #
            num = eptD["protein"] if "protein" in eptD else 0
            cObj.setValue(num, "polymer_entity_count_protein", 0)
            #
            num = eptD["NA-hybrid"] if "NA-hybrid" in eptD else 0
            cObj.setValue(num, "polymer_entity_count_nucleic_acid_hybrid", 0)
            #
            numDNA = eptD["DNA"] if "DNA" in eptD else 0
            cObj.setValue(numDNA, "polymer_entity_count_DNA", 0)
            #
            numRNA = eptD["RNA"] if "RNA" in eptD else 0
            cObj.setValue(numRNA, "polymer_entity_count_RNA", 0)
            cObj.setValue(numDNA + numRNA, "polymer_entity_count_nucleic_acid", 0)
            #
            # ---------------------------------------------------------------------------------------------------------
            # INSTANCE FEATURES
            #
            ##
            repModelL = ["1"]
            if self.__commonU.hasMethodNMR(methodL):
                repModelL = self.__getRepresentativeModels(dataContainer)
            logger.debug("Representative model list %r", repModelL)
            #
            instanceTypeCountD = self.__commonU.getInstanceTypeCounts(dataContainer)
            cObj.setValue(instanceTypeCountD["polymer"], "deposited_polymer_entity_instance_count", 0)
            cObj.setValue(instanceTypeCountD["non-polymer"], "deposited_nonpolymer_entity_instance_count", 0)

            #
            # Various atom counts -
            #
            repModelId = repModelL[0]
            numAtomsModel, numAtomsTotal, numModelsTotal = self.__commonU.getDepositedAtomCounts(dataContainer, modelId=repModelId)
            #
            logger.debug("numAtomsTotal %d numAtomsModel %d numModelsTotal %d", numAtomsTotal, numAtomsModel, numModelsTotal)
            logger.debug("entity type atom counts %r", self.__commonU.getEntityTypeAtomCounts(dataContainer, modelId=repModelId))
            logger.debug("instance atom counts %r", self.__commonU.getEntityTypeAtomCounts(dataContainer, modelId=repModelId))
            #
            if numAtomsModel > 0:
                cObj.setValue(numAtomsModel, "deposited_atom_count", 0)
                cObj.setValue(numModelsTotal, "deposited_model_count", 0)
            #

            # ---------------------------------------------------------------------------------------------------------
            #  Deposited monomer/residue instance counts
            #
            #  Get modeled and unmodeled residue counts
            #
            modeledCount, unModeledCount = self.__commonU.getDepositedMonomerCounts(dataContainer, modelId=repModelId)
            cObj.setValue(modeledCount, "deposited_modeled_polymer_monomer_count", 0)
            cObj.setValue(unModeledCount, "deposited_unmodeled_polymer_monomer_count", 0)
            cObj.setValue(modeledCount + unModeledCount, "deposited_polymer_monomer_count", 0)
            #
            # ---------------------------------------------------------------------------------------------------------
            #  Counts of intermolecular bonds/linkages
            #
            #
            bCountsD = self.__commonU.getInstanceConnectionCounts(dataContainer)
            cObj.setValue(bCountsD["disulf"], "disulfide_bond_count", 0)
            cObj.setValue(bCountsD["metalc"], "inter_mol_metalic_bond_count", 0)
            cObj.setValue(bCountsD["covale"], "inter_mol_covalent_bond_count", 0)
            #
            cisPeptideD = self.__commonU.getCisPeptides(dataContainer)
            cObj.setValue(len(cisPeptideD), "cis_peptide_count", 0)
            #
            # This is reset in anothor method - filterSourceOrganismDetails()
            cObj.setValue(None, "polymer_entity_taxonomy_count", 0)
            #
            fw = self.__commonU.getFormulaWeightNonSolvent(dataContainer)
            cObj.setValue(str(round(fw, 2)), "molecular_weight", 0)
            #
            return True
        except Exception as e:
            logger.exception("For %s %r failing with %s", dataContainer.getName(), catName, str(e))
        return False

    def filterBlockByMethod(self, dataContainer, blockName, **kwargs):
        """ Filter empty placeholder data categories by experimental method.

        """
        logger.debug("Starting with %r blockName %r kwargs %r", dataContainer.getName(), blockName, kwargs)
        try:
            if not dataContainer.exists("exptl"):
                return False
            #
            xObj = dataContainer.getObj("exptl")
            methodL = xObj.getAttributeValueList("method")
            objNameL = []
            # Test for a diffraction method in the case of multiple methods
            if len(methodL) > 1:
                isXtal = False
                for method in methodL:
                    if method in ["X-RAY DIFFRACTION", "FIBER DIFFRACTION", "POWDER DIFFRACTION", "ELECTRON CRYSTALLOGRAPHY", "NEUTRON DIFFRACTION"]:
                        isXtal = True
                        break
                if not isXtal:
                    objNameL = ["cell", "symmetry", "refine", "refine_hist", "software", "diffrn", "diffrn_radiation"]
            else:
                #
                mS = methodL[0].upper()
                if mS in ["X-RAY DIFFRACTION", "FIBER DIFFRACTION", "POWDER DIFFRACTION", "ELECTRON CRYSTALLOGRAPHY", "NEUTRON DIFFRACTION"]:
                    objNameL = []
                elif mS in ["SOLUTION NMR", "SOLID-STATE NMR"]:
                    objNameL = ["cell", "symmetry", "refine", "refine_hist", "software", "diffrn", "diffrn_radiation"]
                elif mS in ["ELECTRON MICROSCOPY"]:
                    objNameL = ["cell", "symmetry", "refine", "refine_hist", "software", "diffrn", "diffrn_radiation"]
                elif mS in ["SOLUTION SCATTERING", "EPR", "THEORETICAL MODEL", "INFRARED SPECTROSCOPY", "FLUORESCENCE TRANSFER"]:
                    objNameL = ["cell", "symmetry", "refine", "refine_hist", "software", "diffrn", "diffrn_radiation"]
                else:
                    logger.error("Unexpected method %r", mS)
            #
            for objName in objNameL:
                dataContainer.remove(objName)
            return True
        except Exception as e:
            logger.exception("For %s failing with %s", dataContainer.getName(), str(e))
        return False

    def filterEnumerations(self, dataContainer, catName, atName, **kwargs):
        """ Standardize the item value to conform to enumeration specifications.
        """
        logger.debug("Starting with %r %r %r %r", dataContainer.getName(), atName, catName, kwargs)
        subD = {("pdbx_reference_molecule", "class"): [("Anti-tumor", "Antitumor")]}
        try:
            if not dataContainer.exists(catName):
                return False
            #
            cObj = dataContainer.getObj(catName)
            if not cObj.hasAttribute(atName):
                return False
            #
            subL = subD[(catName, atName)] if (catName, atName) in subD else []
            #
            for ii in range(cObj.getRowCount()):
                tV = cObj.getValue(atName, ii)
                if tV and tV not in [".", "?"]:
                    for sub in subL:
                        if sub[0] in tV:
                            tV = tV.replace(sub[0], sub[1])
                            cObj.setValue(tV, atName, ii)
            return True
        except Exception as e:
            logger.exception("%s %s %s failing with %s", dataContainer.getName(), catName, atName, str(e))
        return False

    def __getRepresentativeModels(self, dataContainer):
        """ Return the list of representative models

            Example:
                #
                _pdbx_nmr_ensemble.entry_id                                      5TM0
                _pdbx_nmr_ensemble.conformers_calculated_total_number            15
                _pdbx_nmr_ensemble.conformers_submitted_total_number             15
                _pdbx_nmr_ensemble.conformer_selection_criteria                  'all calculated structures submitted'
                _pdbx_nmr_ensemble.representative_conformer                      ?
                _pdbx_nmr_ensemble.average_constraints_per_residue               ?
                _pdbx_nmr_ensemble.average_constraint_violations_per_residue     ?
                _pdbx_nmr_ensemble.maximum_distance_constraint_violation         ?
                _pdbx_nmr_ensemble.average_distance_constraint_violation         ?
                _pdbx_nmr_ensemble.maximum_upper_distance_constraint_violation   ?
                _pdbx_nmr_ensemble.maximum_lower_distance_constraint_violation   ?
                _pdbx_nmr_ensemble.distance_constraint_violation_method          ?
                _pdbx_nmr_ensemble.maximum_torsion_angle_constraint_violation    ?
                _pdbx_nmr_ensemble.average_torsion_angle_constraint_violation    ?
                _pdbx_nmr_ensemble.torsion_angle_constraint_violation_method     ?
                #
                _pdbx_nmr_representative.entry_id             5TM0
                _pdbx_nmr_representative.conformer_id         1
                _pdbx_nmr_representative.selection_criteria   'fewest violations'
        """
        repModelL = []
        if dataContainer.exists("pdbx_nmr_representative"):
            tObj = dataContainer.getObj("pdbx_nmr_representative")
            if tObj.hasAttribute("conformer_id"):
                for ii in range(tObj.getRowCount()):
                    nn = tObj.getValue("conformer_id", ii)
                    if nn is not None and nn.isdigit():
                        repModelL.append(nn)

        if dataContainer.exists("pdbx_nmr_ensemble"):
            tObj = dataContainer.getObj("pdbx_nmr_ensemble")
            if tObj.hasAttribute("representative_conformer"):
                nn = tObj.getValue("representative_conformer", 0)
                if nn is not None and nn and nn.isdigit():
                    repModelL.append(nn)
        #
        repModelL = list(set(repModelL))
        if not repModelL:
            logger.debug("Missing representative model data for %s using 1", dataContainer.getName())
            repModelL = ["1"]

        return repModelL

    def __filterExperimentalResolution(self, dataContainer):
        """ Collect resolution estimates from method specific sources.
        """
        rL = []
        if dataContainer.exists("refine"):
            tObj = dataContainer.getObj("refine")
            if tObj.hasAttribute("ls_d_res_high"):
                for ii in range(tObj.getRowCount()):
                    rv = tObj.getValue("ls_d_res_high", ii)
                    if self.__commonU.isFloat(rv):
                        rL.append(rv)

        if dataContainer.exists("em_3d_reconstruction"):
            tObj = dataContainer.getObj("em_3d_reconstruction")
            if tObj.hasAttribute("resolution"):
                for ii in range(tObj.getRowCount()):
                    rv = tObj.getValue("resolution", ii)
                    if self.__commonU.isFloat(rv):
                        rL.append(rv)
        return rL
