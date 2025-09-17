from typing import Type

from gen_epix import fastapp
from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.abac import CaseAbac as CaseAbac
from gen_epix.casedb.domain.model.abac import CaseTypeAccessAbac as CaseTypeAccessAbac
from gen_epix.casedb.domain.model.abac import CaseTypeShareAbac as CaseTypeShareAbac
from gen_epix.casedb.domain.model.abac import (
    OrganizationAccessCasePolicy as OrganizationAccessCasePolicy,
)
from gen_epix.casedb.domain.model.abac import (
    OrganizationAdminPolicy as OrganizationAdminPolicy,
)
from gen_epix.casedb.domain.model.abac import (
    OrganizationShareCasePolicy as OrganizationShareCasePolicy,
)
from gen_epix.casedb.domain.model.abac import (
    UserAccessCasePolicy as UserAccessCasePolicy,
)
from gen_epix.casedb.domain.model.abac import UserShareCasePolicy as UserShareCasePolicy
from gen_epix.casedb.domain.model.case import BaseCaseRights as BaseCaseRights
from gen_epix.casedb.domain.model.case import Case as Case
from gen_epix.casedb.domain.model.case import (
    CaseDataCollectionLink as CaseDataCollectionLink,
)
from gen_epix.casedb.domain.model.case import CaseDataIssue as CaseDataIssue
from gen_epix.casedb.domain.model.case import CaseForCreateUpdate as CaseForCreateUpdate
from gen_epix.casedb.domain.model.case import CaseQuery as CaseQuery
from gen_epix.casedb.domain.model.case import CaseRights as CaseRights
from gen_epix.casedb.domain.model.case import CaseSet as CaseSet
from gen_epix.casedb.domain.model.case import CaseSetCategory as CaseSetCategory
from gen_epix.casedb.domain.model.case import (
    CaseSetDataCollectionLink as CaseSetDataCollectionLink,
)
from gen_epix.casedb.domain.model.case import CaseSetMember as CaseSetMember
from gen_epix.casedb.domain.model.case import CaseSetQuery as CaseSetQuery
from gen_epix.casedb.domain.model.case import CaseSetRights as CaseSetRights
from gen_epix.casedb.domain.model.case import CaseSetStat as CaseSetStat
from gen_epix.casedb.domain.model.case import CaseSetStatus as CaseSetStatus
from gen_epix.casedb.domain.model.case import CaseType as CaseType
from gen_epix.casedb.domain.model.case import CaseTypeCol as CaseTypeCol
from gen_epix.casedb.domain.model.case import CaseTypeColSet as CaseTypeColSet
from gen_epix.casedb.domain.model.case import (
    CaseTypeColSetMember as CaseTypeColSetMember,
)
from gen_epix.casedb.domain.model.case import CaseTypeDim as CaseTypeDim
from gen_epix.casedb.domain.model.case import CaseTypeSet as CaseTypeSet
from gen_epix.casedb.domain.model.case import CaseTypeSetCategory as CaseTypeSetCategory
from gen_epix.casedb.domain.model.case import CaseTypeSetMember as CaseTypeSetMember
from gen_epix.casedb.domain.model.case import CaseTypeStat as CaseTypeStat
from gen_epix.casedb.domain.model.case import (
    CaseValidationReport as CaseValidationReport,
)
from gen_epix.casedb.domain.model.case import Col as Col
from gen_epix.casedb.domain.model.case import CompleteCaseType as CompleteCaseType
from gen_epix.casedb.domain.model.case import Dim as Dim
from gen_epix.casedb.domain.model.case import (
    GeneticDistanceProtocol as GeneticDistanceProtocol,
)
from gen_epix.casedb.domain.model.case import TreeAlgorithm as TreeAlgorithm
from gen_epix.casedb.domain.model.case import TreeAlgorithmClass as TreeAlgorithmClass
from gen_epix.casedb.domain.model.case import ValidatedCase as ValidatedCase
from gen_epix.casedb.domain.model.geo import Region as Region
from gen_epix.casedb.domain.model.geo import RegionRelation as RegionRelation
from gen_epix.casedb.domain.model.geo import RegionSet as RegionSet
from gen_epix.casedb.domain.model.geo import RegionSetShape as RegionSetShape
from gen_epix.casedb.domain.model.ontology import Concept as Concept
from gen_epix.casedb.domain.model.ontology import ConceptSet as ConceptSet
from gen_epix.casedb.domain.model.ontology import ConceptSetMember as ConceptSetMember
from gen_epix.casedb.domain.model.ontology import Disease as Disease
from gen_epix.casedb.domain.model.ontology import EtiologicalAgent as EtiologicalAgent
from gen_epix.casedb.domain.model.ontology import Etiology as Etiology
from gen_epix.casedb.domain.model.organization import User as User
from gen_epix.casedb.domain.model.organization import UserInvitation as UserInvitation
from gen_epix.casedb.domain.model.organization import (
    UserInvitationConstraints as UserInvitationConstraints,
)
from gen_epix.casedb.domain.model.seqdb import AlleleProfile as AlleleProfile
from gen_epix.casedb.domain.model.seqdb import GeneticSequence as GeneticSequence
from gen_epix.casedb.domain.model.seqdb import PhylogeneticTree as PhylogeneticTree
from gen_epix.casedb.domain.model.subject import Subject as Subject
from gen_epix.casedb.domain.model.subject import SubjectIdentifier as SubjectIdentifier
from gen_epix.commondb.domain import enum as common_enum
from gen_epix.commondb.domain import model as common_model
from gen_epix.commondb.domain.model import (
    SORTED_MODELS_BY_SERVICE_TYPE as _COMMON_SORTED_MODELS_BY_SERVICE_TYPE,
)
from gen_epix.commondb.domain.model import Contact as Contact
from gen_epix.commondb.domain.model import DataCollection as DataCollection
from gen_epix.commondb.domain.model import DataCollectionSet as DataCollectionSet
from gen_epix.commondb.domain.model import (
    DataCollectionSetMember as DataCollectionSetMember,
)
from gen_epix.commondb.domain.model import IdentifierIssuer as IdentifierIssuer
from gen_epix.commondb.domain.model import Model as Model
from gen_epix.commondb.domain.model import Organization as Organization
from gen_epix.commondb.domain.model import OrganizationSet as OrganizationSet
from gen_epix.commondb.domain.model import (
    OrganizationSetMember as OrganizationSetMember,
)
from gen_epix.commondb.domain.model import Outage as Outage
from gen_epix.commondb.domain.model import Site as Site
from gen_epix.commondb.domain.model import UserNameEmail as UserNameEmail
from gen_epix.fastapp.services.auth import IdentityProvider as IdentityProvider
from gen_epix.fastapp.services.auth import IDPUser as IDPUser

# List up model classes per service and sorted according to links topology
SORTED_MODELS_BY_SERVICE_TYPE: dict[enum.ServiceType, list[Type[fastapp.Model]]] = (
    {  # pyright: ignore[reportAssignmentType]
        # Common models
        enum.ServiceType.AUTH: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.AUTH]
        ),
        enum.ServiceType.SYSTEM: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.SYSTEM]
        ),
        enum.ServiceType.RBAC: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.RBAC]
        ),
        enum.ServiceType.ORGANIZATION: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.ORGANIZATION]
        ),
        # Specific models
        enum.ServiceType.ONTOLOGY: [
            Concept,
            ConceptSet,
            ConceptSetMember,
            Disease,
            EtiologicalAgent,
            Etiology,
        ],
        enum.ServiceType.GEO: [
            RegionSet,
            Region,
            RegionRelation,
            RegionSetShape,
        ],
        enum.ServiceType.SEQDB: [
            AlleleProfile,
            GeneticSequence,
            PhylogeneticTree,
        ],
        enum.ServiceType.SUBJECT: [
            Subject,
            SubjectIdentifier,
        ],
        enum.ServiceType.CASE: [
            TreeAlgorithmClass,
            TreeAlgorithm,
            GeneticDistanceProtocol,
            Dim,
            Col,
            CaseTypeSetCategory,
            CaseType,
            CaseTypeSet,
            CaseTypeSetMember,
            CaseTypeDim,
            CaseTypeCol,
            CaseTypeColSet,
            CaseTypeColSetMember,
            CompleteCaseType,
            Case,
            CaseForCreateUpdate,
            CaseSetCategory,
            CaseSetStatus,
            CaseSet,
            CaseSetMember,
            CaseDataCollectionLink,
            CaseSetDataCollectionLink,
            CaseTypeStat,
            CaseSetStat,
            CaseQuery,
            CaseSetQuery,
            CaseRights,
            CaseSetRights,
            CaseValidationReport,
        ],
        enum.ServiceType.ABAC: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.ABAC]
        )
        + [
            OrganizationAccessCasePolicy,
            OrganizationShareCasePolicy,
            UserAccessCasePolicy,
            UserShareCasePolicy,
        ],
    }
)
SORTED_SERVICE_TYPES = tuple(SORTED_MODELS_BY_SERVICE_TYPE.keys())

COMMON_MODEL_IMPL: dict[Type[fastapp.Model], Type[fastapp.Model]] = {
    common_model.User: User,
    common_model.UserInvitation: UserInvitation,
    common_model.UserInvitationConstraints: UserInvitationConstraints,
    common_model.OrganizationAdminPolicy: OrganizationAdminPolicy,
}
