# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 by Imio.be
#
# GNU General Public License (GPL)
#

from collective.contact.plonegroup.utils import get_all_suffixes
from collective.contact.plonegroup.utils import get_organizations
from collective.contact.plonegroup.utils import select_org_for_function
from copy import deepcopy
from plone import api
from plone.memoize.forever import _memos
from Products.Archetypes.event import ObjectEditedEvent
from Products.MeetingCharleroi.config import CHARLEROI_COUNCIL_ITEM_WF_VALIDATION_LEVELS
from Products.MeetingCharleroi.config import POLICE_GROUP_PREFIX
from Products.MeetingCharleroi.config import PROJECTNAME
from Products.MeetingCharleroi.profiles.zcharleroi import import_data as charleroi_import_data
from Products.MeetingCharleroi.setuphandlers import _addCouncilDemoData
from Products.MeetingCharleroi.setuphandlers import _demoData
from Products.MeetingCharleroi.testing import MCH_TESTING_PROFILE_FUNCTIONAL
from Products.MeetingCharleroi.tests.helpers import MeetingCharleroiTestingHelpers
from Products.MeetingCharleroi.utils import finance_group_uid
from Products.MeetingCommunes.tests.MeetingCommunesTestCase import MeetingCommunesTestCase
from Products.PloneMeeting.exportimport.content import ToolInitializer
from Products.PloneMeeting.utils import org_id_to_uid
from zope.event import notify

import copy


class MeetingCharleroiTestCase(MeetingCommunesTestCase, MeetingCharleroiTestingHelpers):
    """Base class for defining MeetingCharleroi test cases."""

    subproductIgnoredTestFiles = [
        "test_robot.py",
        "testPerformances.py",
        "testVotes.py",
    ]

    layer = MCH_TESTING_PROFILE_FUNCTIONAL

    def _configureCharleroiFinancesAdvice(self, cfg):
        """ """
        # add finances group
        self._createFinancesGroup()
        # put users in finances group
        self._setupFinancesGroup()
        # configure customAdvisers for 'meeting-config-college'
        # turn FINANCE_GROUP_ID into relevant org UID
        customAdvisers = deepcopy(charleroi_import_data.collegeMeeting.customAdvisers)
        for customAdviser in customAdvisers:
            customAdviser["org"] = finance_group_uid()
        cfg.setCustomAdvisers(customAdvisers)

        cfg.setTransitionsReinitializingDelays(
            charleroi_import_data.collegeMeeting.transitionsReinitializingDelays
        )

        # configure advisersConfig
        config = deepcopy(charleroi_import_data.data.advisersConfig)
        config[0]['org_uids'] = [finance_group_uid()]
        self.tool.setAdvisersConfig(config)
        self.tool.at_post_edit_script()

        # finances advice can be given when item in state 'prevalidated_waiting_advices'
        cfg.setKeepAccessToItemWhenAdvice("is_given")
        self._activate_wfas("waiting_advices", keep_existing=True)

    def _createFinancesGroup(self):
        """
        Create the finances group.
        """
        context = self.portal.portal_setup._getImportContext("Products.MeetingCharleroi:testing")
        initializer = ToolInitializer(context, PROJECTNAME)
        # create echevin2 first as it is a group in charge of finances org
        orgs, active_orgs, savedOrgsData = initializer.addOrgs([charleroi_import_data.ech2_grp])
        for org in orgs:
            org_uid = org.UID()
            self._select_organization(org_uid)

        dirfin_grp = deepcopy(charleroi_import_data.dirfin_grp)
        dirfin_grp.groups_in_charge = [
            org_id_to_uid(group_in_charge_id) for group_in_charge_id in dirfin_grp.groups_in_charge
        ]

        orgs, active_orgs, savedOrgsData = initializer.addOrgs([dirfin_grp])
        initializer.data = initializer.getProfileData()
        for org in orgs:
            org_uid = org.UID()
            org.item_advice_states = initializer._correct_advice_states(dirfin_grp.item_advice_states)
            org.item_advice_edit_states = initializer._correct_advice_states(
                dirfin_grp.item_advice_edit_states
            )
            self._select_organization(org_uid)
            select_org_for_function(org_uid, "financialcontrollers")
            select_org_for_function(org_uid, "financialeditors")
            select_org_for_function(org_uid, "financialmanagers")
            select_org_for_function(org_uid, "financialreviewers")
        # clean forever cache on utils finance_group_uid
        _memos.clear()

    def _setupFinancesGroup(self):
        """Configure finances group."""
        groupsTool = api.portal.get_tool("portal_groups")
        # add finances users to relevant groups
        # _advisers
        groupsTool.addPrincipalToGroup("pmFinController", "{0}_advisers".format(finance_group_uid()))
        groupsTool.addPrincipalToGroup("pmFinEditor", "{0}_advisers".format(finance_group_uid()))
        groupsTool.addPrincipalToGroup("pmFinReviewer", "{0}_advisers".format(finance_group_uid()))
        groupsTool.addPrincipalToGroup("pmFinManager", "{0}_advisers".format(finance_group_uid()))
        groupsTool.addPrincipalToGroup("dfin", "{0}_advisers".format(finance_group_uid()))
        # respective _financesXXX groups
        groupsTool.addPrincipalToGroup(
            "pmFinController", "{0}_financialcontrollers".format(finance_group_uid())
        )
        groupsTool.addPrincipalToGroup("pmFinEditor", "{0}_financialeditors".format(finance_group_uid()))
        groupsTool.addPrincipalToGroup("pmFinReviewer", "{0}_financialreviewers".format(finance_group_uid()))
        groupsTool.addPrincipalToGroup("pmFinManager", "{0}_financialmanagers".format(finance_group_uid()))
        # dfin is member of every finances groups
        groupsTool.addPrincipalToGroup("dfin", "{0}_financialcontrollers".format(finance_group_uid()))
        groupsTool.addPrincipalToGroup("dfin", "{0}_financialeditors".format(finance_group_uid()))
        groupsTool.addPrincipalToGroup("dfin", "{0}_financialreviewers".format(finance_group_uid()))
        groupsTool.addPrincipalToGroup("dfin", "{0}_financialmanagers".format(finance_group_uid()))

    def _setupPoliceGroup(self):
        """Configure police group.
        - create 'bourgmestre' group as in charge of police groups;
        - create police/police_compta groups;
        - add 'pmManager' to the _creators group;
        - add some default categories."""
        # due to complex setup to manage college and council,
        # sometimes this method is called twice...
        if org_id_to_uid(POLICE_GROUP_PREFIX, raise_on_error=False):
            return

        self.changeUser("siteadmin")
        context = self.portal.portal_setup._getImportContext("Products.MeetingCharleroi:testing")
        initializer = ToolInitializer(context, PROJECTNAME)
        # create bourgmestre first as it is a group in charge of police orgs
        orgs, active_orgs, savedOrgsData = initializer.addOrgs([charleroi_import_data.bourg_grp])
        bourg_grp = orgs[0]
        for org in orgs:
            org_uid = org.UID()
            self._select_organization(org_uid)

        # groups_in_charge are organziation ids, we need organization uids
        police_grp = deepcopy(charleroi_import_data.police_grp)
        police_grp.groups_in_charge = [
            org_id_to_uid(group_in_charge_id) for group_in_charge_id in police_grp.groups_in_charge
        ]
        police_compta_grp = deepcopy(charleroi_import_data.police_compta_grp)
        police_compta_grp.groups_in_charge = [
            org_id_to_uid(group_in_charge_id) for group_in_charge_id in police_compta_grp.groups_in_charge
        ]
        org_descriptors = (police_grp, police_compta_grp)
        orgs, active_orgs, savedOrgsData = initializer.addOrgs(org_descriptors, defer_data=False)
        for org in orgs:
            org_uid = org.UID()
            self._select_organization(org_uid)

        police = orgs[0]
        police_compta = orgs[1]
        gic1 = self.create(
            "organization",
            id="groupincharge1",
            title="Group in charge 1",
            acronym="GIC1",
        )
        gic1_uid = gic1.UID()
        self._select_organization(gic1.UID())
        gic2 = self.create(
            "organization",
            id="groupincharge2",
            title="Group in charge 2",
            acronym="GIC2",
        )
        gic2_uid = gic2.UID()
        self._select_organization(gic2.UID())
        # police is added at the end of existing groups
        self.assertEqual(
            get_organizations(the_objects=False),
            [
                self.developers_uid,
                self.vendors_uid,
                bourg_grp.UID(),
                police.UID(),
                police_compta.UID(),
                gic1.UID(),
                gic2.UID(),
            ],
        )
        # set groupsInCharge for police groups
        police.groups_in_charge = (gic1_uid,)
        police_compta.groups_in_charge = (gic1_uid,)
        self.vendors.groups_in_charge = (gic1_uid,)
        self.developers.groups_in_charge = (gic2_uid,)
        # make 'pmManager' able to manage everything for 'vendors' and 'police'
        groupsTool = self.portal.portal_groups
        for org in (self.vendors, police, police_compta):
            org_uid = org.UID()
            for suffix in get_all_suffixes(org_uid):
                groupsTool.addPrincipalToGroup("pmManager", "{0}_{1}".format(org_uid, suffix))

        self._removeConfigObjectsFor(
            self.meetingConfig,
            folders=["recurringitems", "itemtemplates", "categories"],
        )
        self._createCategories()
        self._createItemTemplates()

    def _createCategories(self):
        """ """
        if self.meetingConfig.getId() == "meeting-config-college":
            categories = charleroi_import_data.collegeMeeting.categories
        else:
            categories = charleroi_import_data.councilMeeting.categories
        # create categories
        existing = [cat.getId() for cat in self.meetingConfig.getCategories(onlySelectable=False)]
        for cat in categories:
            if cat.id not in existing:
                data = {
                    "id": cat.id,
                    "title": cat.title,
                    "description": cat.description,
                }
                self.create("meetingcategory", **data)

    def _createItemTemplates(self):
        """ """
        if self.meetingConfig.getId() == "meeting-config-college":
            templates = charleroi_import_data.collegeMeeting.itemTemplates
        else:
            templates = charleroi_import_data.councilMeeting.itemTemplates
        for template in templates:
            data = {
                "id": template.id,
                "title": template.title,
                "description": template.description,
                "category": template.category,
                "proposingGroup":
                    template.proposingGroup.startswith(POLICE_GROUP_PREFIX) and
                    template.proposingGroup or
                    self.developers_uid,
                # 'templateUsingGroups': template.templateUsingGroups,
                "decision": template.decision,
            }
            self.create("MeetingItemTemplate", **data)

    def _createRecurringItems(self):
        """ """
        if self.meetingConfig.getId() == "meeting-config-college":
            items = charleroi_import_data.collegeMeeting.recurringItems
        else:
            items = charleroi_import_data.councilMeeting.recurringItems
        for item in items:
            gic2_uid = org_id_to_uid("groupincharge2")
            group_in_charge_value = "{0}__groupincharge__{0}".format(self.developers_uid, gic2_uid)
            data = {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "category": item.category,
                "proposingGroup": self.developers_uid,
                "proposingGroupWithGroupInCharge": group_in_charge_value,
                "decision": item.decision,
                "meetingTransitionInsertingMe": item.meetingTransitionInsertingMe,
            }
            self.create("MeetingItemRecurring", **data)

    def setupCouncilConfig(self):
        """ """
        self.changeUser("siteadmin")
        cfg = getattr(self.tool, "meeting-config-college")
        cfg.setItemManualSentToOtherMCStates(
            charleroi_import_data.collegeMeeting.itemManualSentToOtherMCStates
        )

        cfg2 = getattr(self.tool, "meeting-config-council")
        # this will especially setup groups in charge, necessary to present items to a Council meeting
        self._setupPoliceGroup()
        cfg2.setListTypes(charleroi_import_data.councilMeeting.listTypes)
        cfg2.setSelectablePrivacies(charleroi_import_data.councilMeeting.selectablePrivacies)

        cfg2.setItemReferenceFormat(charleroi_import_data.councilMeeting.itemReferenceFormat)
        cfg2.setUsedItemAttributes(charleroi_import_data.councilMeeting.usedItemAttributes)
        # setup inserting methods
        cfg2.setInsertingMethodsOnAddItem(charleroi_import_data.councilMeeting.insertingMethodsOnAddItem)

        cfg2.setItemWFValidationLevels(copy.deepcopy(CHARLEROI_COUNCIL_ITEM_WF_VALIDATION_LEVELS))
        notify(ObjectEditedEvent(cfg2))
        self.setMeetingConfig(cfg2.id)
        self._createCategories()
        self._activate_wfas(
            charleroi_import_data.councilMeeting.workflowAdaptations,
            cfg=cfg,
            keep_existing=False,
        )
        self.setMeetingConfig(cfg.id)

    def setupCollegeConfig(self):
        """ """
        cfg = self.meetingConfig

        self._setupPoliceGroup()
        self._configureCharleroiFinancesAdvice(cfg)
        self._activate_wfas(
            charleroi_import_data.collegeMeeting.workflowAdaptations,
            cfg=cfg,
            keep_existing=False,
        )
        cfg.setListTypes(charleroi_import_data.collegeMeeting.listTypes)
        cfg.setInsertingMethodsOnAddItem(charleroi_import_data.collegeMeeting.insertingMethodsOnAddItem)
        cfg.setOrderedGroupsInCharge([])  # We'll use organization's order
        self._enableField('category')
        cfg.setItemReferenceFormat(charleroi_import_data.collegeMeeting.itemReferenceFormat)
        # let creators select the 'toDiscuss' value
        cfg.setToDiscussSetOnItemInsert(False)

    def setupCollegeDemoData(self):
        """ """
        self.setupCollegeConfig()
        # create items and meetings using demo data
        self.changeUser("pmManager")
        collegeMeeting, collegeExtraMeeting = _demoData(
            self.portal, userId="pmManager", firstTwoGroupIds=("developers", "vendors")
        )
        return collegeMeeting, collegeExtraMeeting

    def setupCouncilDemoData(self):
        """ """
        collegeMeeting, collegeExtraMeeting = self.setupCollegeDemoData()
        self.changeUser("siteadmin")
        self._removeConfigObjectsFor(
            self.meetingConfig2,
            folders=["recurringitems", "itemtemplates", "categories"],
        )
        current_cfg = self.meetingConfig
        self.setMeetingConfig(self.meetingConfig2.getId())
        self._createItemTemplates()
        self._createRecurringItems()
        self.setupCouncilConfig()
        self.changeUser("pmManager")
        councilMeeting = _addCouncilDemoData(
            collegeMeeting,
            collegeExtraMeeting,
            userId="pmManager",
            firstTwoGroupIds=("developers", "vendors"),
        )
        self.setMeetingConfig(current_cfg.getId())
        return councilMeeting
