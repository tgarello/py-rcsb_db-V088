##
# File:    SchemaDocumentHelper.py
# Author:  J. Westbrook
# Date:    7-Jun-2018
# Version: 0.001 Initial version
#
# Updates:
#  22-Jun-2018 jdw change collection attribute id specification to dot notation
#  14-Aug-2018 jdw generalize document key attribute to attribute list
#  20-Aug-2018 jdw slice details added to __schemaContentFilters
#   8-Oct-2018 jdw added getSubCategoryAggregates() method
#   3-Dec-2018 jdw add method getDocumentIndices()
#  16-Jan-2019 jdw add method getDocumentReplaceAttributeNames()
#  11-Mar-2019 jdw add methods getSubCategoryAggregateFeatures() and  getSubCategoryAggregateUnitCardinality()
#  13-Mar-2019 jdw add getCollectionVersion() and getCollectionInfo() and remove getCollections().
#   6-Sep-2019 jdw incorporate search type and brief descriptions
#
##
"""
Inject additional document information into a schema definition.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging

logger = logging.getLogger(__name__)


class DocumentDefinitionHelper(object):
    """ Inject additional configuration information into a document schema definition.

        Single source of document schema semantic configuration content.
    """

    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: (below)

        """
        # ----
        #
        self.__cfgOb = kwargs.get("cfgOb", None)
        sectionName = kwargs.get("config_section", "document_helper_configuration")
        self.__cfgD = self.__cfgOb.exportConfig(sectionName=sectionName)
        self.__searchTypeD = {}
        self.__attributeDescriptionD = {}
        self.__categoryNested = {}
        self.__attributeSeachPriority = {}
        #
        # ----

    def getCollectionInfo(self, schemaName):
        """ Returns a list of [{NAME: xx, VERSION: xxx}, ...] for the input schema.
        """
        cL = []
        try:
            cL = [td for td in self.__cfgD["document_collection_names"][schemaName]]
        except Exception as e:
            logger.debug("Schema definitions name %s failing with %s", schemaName, str(e))
        return cL

    def getCollectionVersion(self, schemaName, collectionName):
        """ Return the version string for the the input schema/collection
        """
        v = None
        try:
            for td in self.__cfgD["document_collection_names"][schemaName]:
                if collectionName == td["NAME"]:
                    return td["VERSION"]
        except Exception as e:
            logger.debug("Schema definitiona name %s failing with %s", schemaName, str(e))
        return v

    def getExcluded(self, collectionName):
        """  For input collection, return the list of excluded schema identifiers.

        """
        includeL = []
        try:
            includeL = [tS.upper() for tS in self.__cfgD["document_collection_content_filters"][collectionName]["EXCLUDE"]]
        except Exception as e:
            logger.debug("Collection %s failing with %s", collectionName, str(e))
        return includeL

    def getIncluded(self, collectionName):
        """  For input collection, return the list of included schema identifiers.

        """
        excludeL = []
        try:
            excludeL = [tS.upper() for tS in self.__cfgD["document_collection_content_filters"][collectionName]["INCLUDE"]]
        except Exception as e:
            logger.debug("Collection %s failing with %s", collectionName, str(e))
        return excludeL

    def getSliceFilter(self, collectionName):
        """  For input collection, return an optional slice filter or None.

        """
        sf = None
        try:
            sf = self.__cfgD["document_collection_content_filters"][collectionName]["SLICE"]
        except Exception as e:
            logger.debug("Collection %s failing with %s", collectionName, str(e))
        return sf

    def getDocumentExcludedAttributes(self, collectionName, asTuple=True):
        atExcludeD = {}
        for cn, cDL in self.__cfgD["collection_attribute_content_filters"].items():
            if cn != collectionName:
                continue
            for cD in cDL:
                catName = cD["CATEGORY_NAME"]
                if "ATTRIBUTE_NAME_LIST" in cD:
                    for atName in cD["ATTRIBUTE_NAME_LIST"]:
                        if asTuple:
                            atExcludeD[(catName, atName)] = collectionName
                        else:
                            atExcludeD.setdefault(catName, []).append(atName)
        return atExcludeD

    def getDocumentKeyAttributeNames(self, collectionName):
        ret = []
        try:
            for dD in self.__cfgD["collection_indices"][collectionName]:
                if dD["INDEX_NAME"] == "primary":
                    ret = dD["ATTRIBUTE_NAMES"]
                    break
        except Exception as e:
            logger.exception("Collection %s failing with %s", collectionName, str(e))
        return ret

    def getDocumentReplaceAttributeNames(self, collectionName):
        """ Return index labeled replace in provided or 'primary' otherwise
        """
        ret = []
        try:
            for dD in self.__cfgD["collection_indices"][collectionName]:
                if dD["INDEX_NAME"] == "replace":
                    ret = dD["ATTRIBUTE_NAMES"]
                    break
            if ret:
                return ret
            #
            for dD in self.__cfgD["collection_indices"][collectionName]:
                if dD["INDEX_NAME"] == "primary":
                    ret = dD["ATTRIBUTE_NAMES"]
                    break
        except Exception as e:
            logger.exception("Collection %s failing with %s", collectionName, str(e))
        return ret

    def getDocumentIndices(self, collectionName):
        ret = []
        try:
            ret = [d for d in self.__cfgD["collection_indices"][collectionName] if d["ATTRIBUTE_NAMES"] and len(d["ATTRIBUTE_NAMES"]) > 0]
        except Exception as e:
            logger.exception("Collection %s failing with %s", collectionName, str(e))
        return ret

    def getPrivateDocumentAttributes(self, collectionName):
        ret = []
        try:
            return [d for d in self.__cfgD["collection_private_keys"][collectionName] if d["PRIVATE_DOCUMENT_NAME"] and len(d["PRIVATE_DOCUMENT_NAME"]) > 0]
        except Exception as e:
            logger.debug("Collection %s failing with %s", collectionName, str(e))
        return ret

    def getSubCategoryAggregates(self, collectionName):
        ret = []
        try:
            return [tS["NAME"] for tS in self.__cfgD["collection_subcategory_aggregates"][collectionName]]
        except Exception as e:
            logger.debug("Collection %s failing with %s", collectionName, str(e))
        return ret

    def getSubCategoryAggregateUnitCardinality(self, collectionName, subCategoryName):
        ret = False
        try:
            if collectionName in self.__cfgD["collection_subcategory_aggregates"]:
                for dD in self.__cfgD["collection_subcategory_aggregates"][collectionName]:
                    if dD["NAME"] == subCategoryName:
                        ret = dD["HAS_UNIT_CARDINALITY"]
                        break
        except Exception as e:
            logger.debug("Collection %s failing with %s", collectionName, str(e))
        return ret

    def getSubCategoryAggregateFeatures(self, collectionName):
        ret = []
        try:
            return [tD for tD in self.__cfgD["collection_subcategory_aggregates"][collectionName]]
        except Exception as e:
            logger.debug("Collection %s failing with %s", collectionName, str(e))
        return ret

    def getRetainSingletonObjects(self, collectionName):
        """ By default singleton objects are expanded in global scope.  To avoid
            this behaviour set the retain singleton option for the collection.
        """
        ret = False
        try:
            return self.__cfgD["collection_retain_singleton"][collectionName]
        except Exception as e:
            logger.debug("Collection %s failing with %s", collectionName, str(e))
        return ret

    def getSuppressedCategoryRelationships(self, collectionName):
        """
         Example:

            collection_suppress_category_relationships:
                ihm_dev:
                    - PARENT_CATEGORY_NAME: chem_comp
                      CHILD_CATEGORY_NAME: atom_site
                    - PARENT_CATEGORY_NAME: entity_poly_seq
                      CHILD_CATEGORY_NAME: atom_site
        """
        rL = []
        try:
            rL = [tD for tD in self.__cfgD["collection_suppress_category_relationships"][collectionName]]
        except Exception as e:
            logger.debug("Collection %s failing with %s", collectionName, str(e))

        return rL

    def __prepareAttributeSearchContexts(self):
        """
        Example:

        collection_attribute_search_contexts:
            pdbx_core_entity_instance:
                - SEARCH_TYPE: exact-match
                  ATTRIBUTE_NAMES:
                  - rcsb_polymer_instance_feature.name
                - SEARCH_TYPE: default-match
                  ATTRIBUTE_NAMES:
                  - rcsb_entity_instance_domain_scop.domain_class_lineage.name
                  - rcsb_entity_instance_domain_scop.domain_class_lineage.id
                  - rcsb_entity_instance_domain_cath.domain_class_lineage.name
                  - rcsb_entity_instance_domain_cath.domain_class_lineage.id

        returns:
            dict : {collectionName: {(category, attribute): [search type, ...], }, }

        """
        cD = {}
        # preprocess search context data --
        for collectionName, tDL in self.__cfgD["collection_attribute_search_contexts"].items():
            aD = {}
            for tD in tDL:
                for atName in tD["ATTRIBUTE_NAMES"]:
                    ff = atName.split(".")
                    if len(ff) > 2:
                        logger.error("Bad attribute name for search type %r", atName)
                        continue
                    aD.setdefault((ff[0], ff[1]), []).append(tD["SEARCH_TYPE"])
                    if tD["SEARCH_TYPE"] in ["exact-match", "suggest"]:
                        aD.setdefault((ff[0], ff[1]), []).append("full-text")
                #
            cD[collectionName] = {tup: sorted(list(set(sL))) for tup, sL in aD.items()}

        return cD

    def getAttributeSearchContexts(self, collectionName, categoryName, attributeName):
        """ Return the list of search types assigned to the input collection/item.

        returns:
            list : [search type, ...]

        """
        rL = []
        try:
            self.__searchTypeD = self.__prepareAttributeSearchContexts() if not self.__searchTypeD else self.__searchTypeD
            rL = self.__searchTypeD[collectionName][(categoryName, attributeName)]
        except Exception as e:
            logger.debug("Collection %sr categoryName %r attributeName %r failing with %s", collectionName, categoryName, attributeName, str(e))

        return rL

    def isTextSearchType(self, categoryName, attributeName):
        _ = categoryName
        _ = attributeName
        return False

    def __prepareAttributeDescriptions(self):
        """
        Example:

            attribute_descriptions:
                - ATTRIBUTE_NAME: rcsb_entry_container_identifiers.entry_id
                  TYPE: brief
                  TEXT: PDB ID(s)
                - ATTRIBUTE_NAME: pdbx_deposit_group.group_id
                  TYPE: brief
                  TEXT: Deposit Group ID(s)
        """
        aD = {}
        # preprocess description data --
        for tD in self.__cfgD["attribute_descriptions"]:
            atName = tD["ATTRIBUTE_NAME"]
            dType = tD["TYPE"]
            ff = atName.split(".")
            if len(ff) != 2:
                logger.error("Bad attribute name for text description %r", atName)
                continue
            aD[(ff[0], ff[1], dType)] = tD["TEXT"]
        return aD

    def getAttributeDescription(self, categoryName, attributeName, contextType="brief"):
        ret = None
        try:
            self.__attributeDescriptionD = self.__prepareAttributeDescriptions() if not self.__attributeDescriptionD else self.__attributeDescriptionD
            ret = self.__attributeDescriptionD[(categoryName, attributeName, contextType)]
        except Exception as e:
            logger.debug("CategoryName %r attributeName %r failing  %s", categoryName, attributeName, str(e))
        return ret

    def __prepareCategoryNested(self):
        """
        Example:

            collection_category_nested:
                pdbx_core_entry:
                    - citation
                pdbx_core_entity:
                    - rcsb_polymer_entity_feature
                pdbx_core_entity_instance:
                    - rcsb_polymer_instance_feature

        """
        cD = {}
        # preprocess the nesting data --
        for collectionName, catNameL in self.__cfgD["collection_category_nested"].items():
            catD = {catName: True for catName in catNameL}
            cD[collectionName] = catD
        return cD

    def isCategoryNested(self, collectionName, categoryName):
        """Return is the input category in this collection is nested.

        Args:
            collectionName (str): collection name
            categoryName (str): category name

        Returns:
            (bool): True if nested or False otherwise

        """
        ret = False
        try:
            self.__categoryNested = self.__prepareCategoryNested() if not self.__categoryNested else self.__categoryNested
            ret = categoryName in self.__categoryNested[collectionName]
        except Exception:
            pass
        return ret

    def __prepareAttributeSearchPriorities(self):
        """
        Example:

            collection_attribute_search_priority:
                pdbx_core_entry:
                    - ATTRIBUTE_NAME: rcsb_entry_container_identifiers.entry_id
                    PRIORITY_VALUE: 20
                    - ATTRIBUTE_NAME: entity.rcsb_macromolecular_names_combined
                    PRIORITY_VALUE: 20

        """
        pD = {}
        try:
            # preprocess priority data --
            for collectionName, tDL in self.__cfgD["collection_attribute_search_priority"].items():
                aD = {}
                for tD in tDL:
                    ff = str(tD["ATTRIBUTE_NAME"]).split(".")
                    pValue = tD["PRIORITY_VALUE"]
                    aD[(ff[0], ff[1])] = pValue
                pD[collectionName] = aD
            return pD
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return pD

    def getAttributeTextSearchPriority(self, collectionName, categoryName, attributeName):
        try:
            self.__attributeSeachPriority = self.__prepareAttributeSearchPriorities() if not self.__attributeSeachPriority else self.__attributeSeachPriority
            try:
                # return a config priority first
                return self.__attributeSeachPriority[collectionName](categoryName, attributeName)
            except Exception:
                pass
            # return an elevated priority based on search context -
            #
            scL = self.getAttributeSearchContexts(collectionName, categoryName, attributeName)
            if "suggest" in scL:
                return 20
            if "exact-match" in scL:
                return 10
            if "full-text" in scL:
                return 1
        except Exception:
            pass
        return None
