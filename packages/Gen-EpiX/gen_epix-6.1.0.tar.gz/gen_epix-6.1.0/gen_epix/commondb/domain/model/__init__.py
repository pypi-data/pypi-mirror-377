from typing import Type

import gen_epix.fastapp as fastapp
from gen_epix.commondb.domain import enum
from gen_epix.commondb.domain.model.abac import (
    OrganizationAdminPolicy as OrganizationAdminPolicy,
)
from gen_epix.commondb.domain.model.base import Model as Model
from gen_epix.commondb.domain.model.organization import Contact as Contact
from gen_epix.commondb.domain.model.organization import DataCollection as DataCollection
from gen_epix.commondb.domain.model.organization import (
    DataCollectionSet as DataCollectionSet,
)
from gen_epix.commondb.domain.model.organization import (
    DataCollectionSetMember as DataCollectionSetMember,
)
from gen_epix.commondb.domain.model.organization import (
    IdentifierIssuer as IdentifierIssuer,
)
from gen_epix.commondb.domain.model.organization import Organization as Organization
from gen_epix.commondb.domain.model.organization import (
    OrganizationSet as OrganizationSet,
)
from gen_epix.commondb.domain.model.organization import (
    OrganizationSetMember as OrganizationSetMember,
)
from gen_epix.commondb.domain.model.organization import Site as Site
from gen_epix.commondb.domain.model.organization import User as User
from gen_epix.commondb.domain.model.organization import UserInvitation as UserInvitation
from gen_epix.commondb.domain.model.organization import (
    UserInvitationConstraints as UserInvitationConstraints,
)
from gen_epix.commondb.domain.model.organization import UserNameEmail as UserNameEmail
from gen_epix.commondb.domain.model.system import Outage as Outage
from gen_epix.commondb.domain.model.system import PackageMetadata as PackageMetadata
from gen_epix.fastapp.services.auth import IdentityProvider as IdentityProvider
from gen_epix.fastapp.services.auth import IDPUser as IDPUser

SORTED_MODELS_BY_SERVICE_TYPE: dict[
    enum.ServiceType, tuple[Type[fastapp.Model], ...]
] = {
    enum.ServiceType.AUTH: (
        IdentityProvider,
        IDPUser,
    ),
    enum.ServiceType.SYSTEM: (Outage, PackageMetadata),
    enum.ServiceType.ORGANIZATION: (
        Organization,
        OrganizationSet,
        OrganizationSetMember,
        DataCollection,
        DataCollectionSet,
        DataCollectionSetMember,
        IdentifierIssuer,
        Site,
        Contact,
        UserNameEmail,
        User,
        UserInvitation,
        UserInvitationConstraints,
    ),
    enum.ServiceType.RBAC: tuple(),
    enum.ServiceType.ABAC: (OrganizationAdminPolicy,),
}

SORTED_SERVICE_TYPES = tuple(SORTED_MODELS_BY_SERVICE_TYPE.keys())
