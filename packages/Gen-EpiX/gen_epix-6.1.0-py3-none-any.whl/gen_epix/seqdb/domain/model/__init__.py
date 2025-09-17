from typing import Type

from gen_epix import fastapp
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
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.abac import (
    OrganizationAdminPolicy as OrganizationAdminPolicy,
)
from gen_epix.seqdb.domain.model.organization import User as User
from gen_epix.seqdb.domain.model.organization import UserInvitation as UserInvitation
from gen_epix.seqdb.domain.model.seq import AlignmentMixin as AlignmentMixin
from gen_epix.seqdb.domain.model.seq import AlignmentProtocol as AlignmentProtocol
from gen_epix.seqdb.domain.model.seq import Allele as Allele
from gen_epix.seqdb.domain.model.seq import AlleleAlignment as AlleleAlignment
from gen_epix.seqdb.domain.model.seq import AlleleProfile as AlleleProfile
from gen_epix.seqdb.domain.model.seq import AssemblyProtocol as AssemblyProtocol
from gen_epix.seqdb.domain.model.seq import AstMeasurement as AstMeasurement
from gen_epix.seqdb.domain.model.seq import AstPrediction as AstPrediction
from gen_epix.seqdb.domain.model.seq import AstProtocol as AstProtocol
from gen_epix.seqdb.domain.model.seq import CodeMixin as CodeMixin
from gen_epix.seqdb.domain.model.seq import (
    CompleteAlleleProfile as CompleteAlleleProfile,
)
from gen_epix.seqdb.domain.model.seq import CompleteContig as CompleteContig
from gen_epix.seqdb.domain.model.seq import CompleteSample as CompleteSample
from gen_epix.seqdb.domain.model.seq import CompleteSeq as CompleteSeq
from gen_epix.seqdb.domain.model.seq import CompleteSnpProfile as CompleteSnpProfile
from gen_epix.seqdb.domain.model.seq import ContigAlignment as ContigAlignment
from gen_epix.seqdb.domain.model.seq import (
    KmerDetectionProtocol as KmerDetectionProtocol,
)
from gen_epix.seqdb.domain.model.seq import KmerProfile as KmerProfile
from gen_epix.seqdb.domain.model.seq import LibraryPrepProtocol as LibraryPrepProtocol
from gen_epix.seqdb.domain.model.seq import Locus as Locus
from gen_epix.seqdb.domain.model.seq import (
    LocusDetectionProtocol as LocusDetectionProtocol,
)
from gen_epix.seqdb.domain.model.seq import LocusSet as LocusSet
from gen_epix.seqdb.domain.model.seq import LocusSetMember as LocusSetMember
from gen_epix.seqdb.domain.model.seq import MultipleAlignment as MultipleAlignment
from gen_epix.seqdb.domain.model.seq import PcrMeasurement as PcrMeasurement
from gen_epix.seqdb.domain.model.seq import PcrProtocol as PcrProtocol
from gen_epix.seqdb.domain.model.seq import PhylogeneticTree as PhylogeneticTree
from gen_epix.seqdb.domain.model.seq import ProtocolMixin as ProtocolMixin
from gen_epix.seqdb.domain.model.seq import QualityMixin as QualityMixin
from gen_epix.seqdb.domain.model.seq import RawSeq as RawSeq
from gen_epix.seqdb.domain.model.seq import ReadSet as ReadSet
from gen_epix.seqdb.domain.model.seq import RefAllele as RefAllele
from gen_epix.seqdb.domain.model.seq import RefSeq as RefSeq
from gen_epix.seqdb.domain.model.seq import RefSnp as RefSnp
from gen_epix.seqdb.domain.model.seq import RefSnpSet as RefSnpSet
from gen_epix.seqdb.domain.model.seq import RefSnpSetMember as RefSnpSetMember
from gen_epix.seqdb.domain.model.seq import Sample as Sample
from gen_epix.seqdb.domain.model.seq import Seq as Seq
from gen_epix.seqdb.domain.model.seq import SeqAlignment as SeqAlignment
from gen_epix.seqdb.domain.model.seq import SeqCategory as SeqCategory
from gen_epix.seqdb.domain.model.seq import SeqCategorySet as SeqCategorySet
from gen_epix.seqdb.domain.model.seq import SeqClassification as SeqClassification
from gen_epix.seqdb.domain.model.seq import (
    SeqClassificationProtocol as SeqClassificationProtocol,
)
from gen_epix.seqdb.domain.model.seq import SeqDistance as SeqDistance
from gen_epix.seqdb.domain.model.seq import SeqDistanceProtocol as SeqDistanceProtocol
from gen_epix.seqdb.domain.model.seq import SeqMixin as SeqMixin
from gen_epix.seqdb.domain.model.seq import SeqTaxonomy as SeqTaxonomy
from gen_epix.seqdb.domain.model.seq import SnpDetectionProtocol as SnpDetectionProtocol
from gen_epix.seqdb.domain.model.seq import SnpProfile as SnpProfile
from gen_epix.seqdb.domain.model.seq import SubtypingScheme as SubtypingScheme
from gen_epix.seqdb.domain.model.seq import Taxon as Taxon
from gen_epix.seqdb.domain.model.seq import TaxonLocusLink as TaxonLocusLink
from gen_epix.seqdb.domain.model.seq import TaxonomyProtocol as TaxonomyProtocol
from gen_epix.seqdb.domain.model.seq import TaxonSet as TaxonSet
from gen_epix.seqdb.domain.model.seq import TaxonSetMember as TaxonSetMember
from gen_epix.seqdb.domain.model.seq import TreeAlgorithm as TreeAlgorithm
from gen_epix.seqdb.domain.model.seq import TreeAlgorithmClass as TreeAlgorithmClass

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
        enum.ServiceType.ABAC: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.ABAC]
        )
        + [],
        enum.ServiceType.SEQ: [
            SubtypingScheme,
            Taxon,
            TaxonSet,
            TaxonSetMember,
            Locus,
            TaxonLocusLink,
            LocusSet,
            LocusSetMember,
            RefSeq,
            RefAllele,
            RefSnp,
            RefSnpSet,
            RefSnpSetMember,
            AlignmentProtocol,
            AssemblyProtocol,
            AstProtocol,
            KmerDetectionProtocol,
            LibraryPrepProtocol,
            LocusDetectionProtocol,
            PcrProtocol,
            SeqClassificationProtocol,
            SeqDistanceProtocol,
            SnpDetectionProtocol,
            TaxonomyProtocol,
            TreeAlgorithmClass,
            TreeAlgorithm,
            SeqCategorySet,
            SeqCategory,
            Sample,
            RawSeq,
            ReadSet,
            Seq,
            Allele,
            AlleleProfile,
            KmerProfile,
            SnpProfile,
            AstMeasurement,
            AstPrediction,
            PcrMeasurement,
            SeqAlignment,
            AlleleAlignment,
            ContigAlignment,
            SeqClassification,
            SeqDistance,
            SeqTaxonomy,
        ],
    }
)

SORTED_SERVICE_TYPES = tuple(SORTED_MODELS_BY_SERVICE_TYPE.keys())

COMMON_MODEL_IMPL: dict[Type[fastapp.Model], Type[fastapp.Model]] = {
    common_model.User: User,
    common_model.UserInvitation: UserInvitation,
    common_model.OrganizationAdminPolicy: OrganizationAdminPolicy,
}
