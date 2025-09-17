##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2022, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

from flask_babel import gettext
from pgadmin.browser.server_groups.servers.types import ServerType


class AgensSQL(ServerType):
    UTILITY_PATH_LABEL = gettext("Agens SQL Binary Path")
    UTILITY_PATH_HELP = gettext(
        "Path to the directory containing the Agens SQL Server utility"
        " programs (ag_dump, ag_restore etc)."
    )

    def instance_of(self, ver):
        return "AgensSQL" in ver


# Default Server Type
AgensSQL('asql', gettext("Agens SQL"), 4)
