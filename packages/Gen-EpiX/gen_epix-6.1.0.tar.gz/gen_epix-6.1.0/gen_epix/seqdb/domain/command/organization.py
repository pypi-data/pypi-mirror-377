from typing import ClassVar

import gen_epix.commondb.domain.command as common_command
from gen_epix.seqdb.domain import model


class UserCrudCommand(common_command.UserCrudCommand):
    MODEL_CLASS: ClassVar = model.User


class UserInvitationCrudCommand(common_command.UserInvitationCrudCommand):
    MODEL_CLASS: ClassVar = model.UserInvitation
