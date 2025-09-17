##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2022, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################
import logging
import re
from functools import wraps

import pgadmin.browser.server_groups as sg
import json
from flask import render_template, request, jsonify, current_app
from flask_babel import gettext as _
import dateutil.parser as dateutil_parser
from pgadmin.browser.collection import CollectionNodeModule
from pgadmin.browser.utils import PGChildNodeView
from pgadmin.utils.ajax import make_json_response, \
    make_response as ajax_response, precondition_required, \
    internal_server_error, forbidden, success_return, gone
from pgadmin.utils.driver import get_driver
from pgadmin.utils.constants import ERROR_FETCHING_ROLE_INFORMATION, \
    ERROR_FETCHING_PROFILE_INFORMATION

from config import PG_DEFAULT_DRIVER
from flask_babel import gettext

_REASSIGN_OWN_SQL = 'reassign_own.sql'
# logger = logging.getLogger('PProfile')
# logger.setLevel(logging.DEBUG)

class PasswordProfileModule(CollectionNodeModule):
    _NODE_TYPE = 'password_profile'
    _COLLECTION_LABEL = _("Password Profile")

    def __init__(self, *args, **kwargs):
        self.min_ver = None
        self.max_ver = None

        super(PasswordProfileModule, self).__init__(*args, **kwargs)

    def get_nodes(self, gid, sid):
        """
        Generate the collection node
        """
        if self.show_node:
            yield self.generate_browser_collection_node(sid)

    @property
    def node_inode(self):
        """
        Override this property to make the node as leaf node.
        """
        return False

    @property
    def script_load(self):
        """
        Load the module script for server, when any of the server-group node is
        initialized.
        """

        return sg.ServerGroupModule.node_type

    @property
    def csssnippets(self):
        """
        Returns a snippet of css to include in the page
        """
        snippets = [
            render_template(
                self._COLLECTION_CSS,
                node_type=self.node_type
            ),
            render_template("passwordprofile/css/passwordprofile.css")]

        for submodule in self.submodules:
            snippets.extend(submodule.csssnippets)

        return snippets

    @property
    def module_use_template_javascript(self):
        """
        Returns whether Jinja2 template is used for generating the javascript
        module.
        """
        return False


blueprint = PasswordProfileModule(__name__)


class PasswordProfileView(PGChildNodeView):
    node_type = 'password_profile'

    parent_ids = [
        {'type': 'int', 'id': 'gid'},
        {'type': 'int', 'id': 'sid'}
    ]
    ids = [
        {'type': 'int', 'id': 'ppid'}
    ]

    operations = dict({
        'obj': [
            {'get': 'properties', 'delete': 'drop', 'put': 'update'},
            {'get': 'list', 'post': 'create', 'delete': 'drop'},
        ],
        'nodes': [{'get': 'node'}, {'get': 'nodes'}],
        'sql': [{'get': 'sql'}],
        'msql': [{'get': 'msql'}, {'get': 'msql'}],
        'dependency': [{'get': 'dependencies'}],
        'dependent': [{'get': 'dependents'}],
        'children': [{'get': 'children'}],
        'vopts': [{}, {'get': 'voptions'}],
        'variables': [{'get': 'variables'}],
        'reassign': [{'get': 'get_reassign_own_sql',
                      'post': 'role_reassign_own'}]
    })

    def _validate_input_dict_for_new(self, data, req_keys):
        """
        This functions validates the input dict and check for required
        keys in the dict when creating a new object
        :param data: input dict
        :param req_keys: required keys
        :return: Valid or Invalid
        """
        if not isinstance(data, list):
            return False

        for item in data:
            if not isinstance(item, dict):
                return False

            for a_key in req_keys:
                if a_key not in item:
                    return False

        return True

    def _validate_input_dict_for_update(
            self, data, req_add_keys, req_delete_keys):
        """
        This functions validates the input dict and check for required
        keys in the dict when updating an existing object
        :param data: input dict
        :param req_add_keys: required keys when adding, updating
        :param req_delete_keys: required keys when deleting
        :return: Valid or Invalid
        """
        if not isinstance(data, dict):
            return False

        for op in ['added', 'deleted', 'changed']:
            op_data = data.get(op, [])
            check_keys = req_add_keys \
                if op in ['added', 'changed'] else req_delete_keys
            if not self._validate_input_dict_for_new(op_data, check_keys):
                return False

        return True

    def _validate_rolvaliduntil(self, data):
        """
        Validate the rolvaliduntil in input data dict
        :param data: role data
        :return: valid or invalid message
        """
        if 'rolvaliduntil' in data:
            # Make date explicit so that it works with every
            # postgres database datestyle format
            try:
                if data['rolvaliduntil'] is not None and \
                    data['rolvaliduntil'] != '' and \
                        len(data['rolvaliduntil']) > 0:
                    data['rolvaliduntil'] = dateutil_parser.parse(
                        data['rolvaliduntil']
                    ).isoformat()
            except Exception:
                return _("Date format is invalid.")

        return None

    def _validate_rolconnlimit(self, data):
        """
        Validate the rolconnlimit data dict
        :param data: role data
        :return: valid or invalid message
        """
        if 'rolconnlimit' in data:
            # If roleconnlimit is empty string then set it to -1
            if data['rolconnlimit'] == '':
                data['rolconnlimit'] = -1

            if data['rolconnlimit'] is not None:
                data['rolconnlimit'] = int(data['rolconnlimit'])
                if not isinstance(data['rolconnlimit'], int) or \
                        data['rolconnlimit'] < -1:
                    return _("Connection limit must be an integer value "
                             "or equal to -1.")
        return None

    def _process_rolemembership(self, id, data):
        """
        Process the input rolemembership list to appropriate keys
        :param id: id of role
        :param data: input role data
        """
        def _part_dict_list(dict_list, condition, list_key=None):
            ret_val = []
            for d in dict_list:
                if condition(d):
                    ret_val.append(d[list_key])

            return ret_val

        if id == -1:
            data['members'] = []
            data['admins'] = []

            data['admins'] = _part_dict_list(
                data['rolmembership'], lambda d: d['admin'], 'role')
            data['members'] = _part_dict_list(
                data['rolmembership'], lambda d: not d['admin'], 'role')
        else:
            data['admins'] = _part_dict_list(
                data['rolmembership'].get('added', []),
                lambda d: d['admin'], 'role')
            data['members'] = _part_dict_list(
                data['rolmembership'].get('added', []),
                lambda d: not d['admin'], 'role')

            data['admins'].extend(_part_dict_list(
                data['rolmembership'].get('changed', []),
                lambda d: d['admin'], 'role'))
            data['revoked_admins'] = _part_dict_list(
                data['rolmembership'].get('changed', []),
                lambda d: not d['admin'], 'role')

            data['revoked'] = _part_dict_list(
                data['rolmembership'].get('deleted', []),
                lambda _: True, 'role')

    def _process_rolmembers(self, id, data):
        """
        Parser role members.
        :param id:
        :param data:
        """
        def _part_dict_list(dict_list, condition, list_key=None):
            ret_val = []
            for d in dict_list:
                if condition(d):
                    ret_val.append(d[list_key])

            return ret_val
        if id == -1:
            data['rol_members'] = []
            data['rol_admins'] = []

            data['rol_admins'] = _part_dict_list(
                data['rolmembers'], lambda d: d['admin'], 'role')
            data['rol_members'] = _part_dict_list(
                data['rolmembers'], lambda d: not d['admin'], 'role')
        else:
            data['rol_admins'] = _part_dict_list(
                data['rolmembers'].get('added', []),
                lambda d: d['admin'], 'role')
            data['rol_members'] = _part_dict_list(
                data['rolmembers'].get('added', []),
                lambda d: not d['admin'], 'role')

            data['rol_admins'].extend(_part_dict_list(
                data['rolmembers'].get('changed', []),
                lambda d: d['admin'], 'role'))
            data['rol_revoked_admins'] = _part_dict_list(
                data['rolmembers'].get('changed', []),
                lambda d: not d['admin'], 'role')

            data['rol_revoked'] = _part_dict_list(
                data['rolmembers'].get('deleted', []),
                lambda _: True, 'role')

    def _validate_rolemembers(self, id, data):
        """
        Validate the rolmembers data dict
        :param data: role data
        :return: valid or invalid message
        """
        if 'rolmembers' not in data:
            return None

        if id == -1:
            msg = _("""
Role members information must be passed as an array of JSON objects in the
following format:

rolmembers:[{
    role: [rolename],
    admin: True/False
    },
    ...
]""")

            if not self._validate_input_dict_for_new(data['rolmembers'],
                                                     ['role', 'admin']):
                return msg

            self._process_rolmembers(id, data)
            return None

        msg = _("""
Role membership information must be passed as a string representing an array of
JSON objects in the following format:
rolmembers:{
    'added': [{
        role: [rolename],
        admin: True/False
        },
        ...
        ],
    'deleted': [{
        role: [rolename],
        admin: True/False
        },
        ...
        ],
    'updated': [{
        role: [rolename],
        admin: True/False
        },
        ...
        ]
""")
        if not self._validate_input_dict_for_update(data['rolmembers'],
                                                    ['role', 'admin'],
                                                    ['role']):
            return msg

        self._process_rolmembers(id, data)
        return None

    def _validate_rolemembership(self, id, data):
        """
        Validate the rolmembership data dict
        :param data: role data
        :return: valid or invalid message
        """
        if 'rolmembership' not in data:
            return None

        if id == -1:
            msg = _("""
Role membership information must be passed as an array of JSON objects in the
following format:

rolmembership:[{
    role: [rolename],
    admin: True/False
    },
    ...
]""")

            if not self._validate_input_dict_for_new(
                    data['rolmembership'], ['role', 'admin']):
                return msg

            self._process_rolemembership(id, data)
            return None

        msg = _("""
Role membership information must be passed as a string representing an array of
JSON objects in the following format:
rolmembership:{
    'added': [{
        role: [rolename],
        admin: True/False
        },
        ...
        ],
    'deleted': [{
        role: [rolename],
        admin: True/False
        },
        ...
        ],
    'updated': [{
        role: [rolename],
        admin: True/False
        },
        ...
        ]
""")
        if not self._validate_input_dict_for_update(
                data['rolmembership'], ['role', 'admin'], ['role']):
            return msg

        self._process_rolemembership(id, data)
        return None

    def _validate_seclabels(self, id, data):
        """
        Validate the seclabels data dict
        :param data: role data
        :return: valid or invalid message
        """
        if 'seclabels' not in data or self.manager.version < 90200:
            return None

        if id == -1:
            msg = _("""
Security Label must be passed as an array of JSON objects in the following
format:
seclabels:[{
    provider: <provider>,
    label: <label>
    },
    ...
]""")
            if not self._validate_input_dict_for_new(
                    data['seclabels'], ['provider', 'label']):
                return msg

            return None

        msg = _("""
Security Label must be passed as an array of JSON objects in the following
format:
seclabels:{
    'added': [{
        provider: <provider>,
        label: <label>
        },
        ...
        ],
    'deleted': [{
        provider: <provider>,
        label: <label>
        },
        ...
        ],
    'updated': [{
        provider: <provider>,
        label: <label>
        },
        ...
        ]
""")
        if not self._validate_input_dict_for_update(
                data['seclabels'], ['provider', 'label'], ['provider']):
            return msg

        return None

    def _validate_variables(self, id, data):
        """
        Validate the variables data dict
        :param data: role data
        :return: valid or invalid message
        """
        if 'variables' not in data:
            return None

        if id == -1:
            msg = _("""
Configuration parameters/variables must be passed as an array of JSON objects
in the following format in create mode:
variables:[{
database: <database> or null,
name: <configuration>,
value: <value>
},
...
]""")
            if not self._validate_input_dict_for_new(
                    data['variables'], ['name', 'value']):
                return msg

            return None

        msg = _("""
Configuration parameters/variables must be passed as an array of JSON objects
in the following format in update mode:
rolmembership:{
'added': [{
    database: <database> or null,
    name: <configuration>,
    value: <value>
    },
    ...
    ],
'deleted': [{
    database: <database> or null,
    name: <configuration>,
    value: <value>
    },
    ...
    ],
'updated': [{
    database: <database> or null,
    name: <configuration>,
    value: <value>
    },
    ...
    ]
""")
        if not self._validate_input_dict_for_update(
                data['variables'], ['name', 'value'], ['name']):
            return msg
        return None

    def _validate_rolname(self, id, data):
        """
        Validate the rolname data dict
        :param data: role data
        :return: valid or invalid message
        """
        if (id == -1) and 'rolname' not in data:
            return precondition_required(
                _("Name must be specified.")
            )
        return None

    def validate_request(f):
        @wraps(f)
        def wrap(self, **kwargs):
            if request.data:
                data = json.loads(request.data, encoding='utf-8')
            else:
                data = dict()
                req = request.args or request.form

                for key in req:

                    val = req[key]
                    if key in [
                        'rolcanlogin', 'rolsuper', 'rolcreatedb',
                        'rolcreaterole', 'rolinherit', 'rolreplication',
                        'rolcatupdate', 'variables', 'rolmembership',
                        'seclabels', 'rolmembers'
                    ]:
                        data[key] = json.loads(val, encoding='utf-8')
                    else:
                        data[key] = val

            # invalid_msg_arr = [
            #     self._validate_rolname(kwargs.get('rid', -1), data),
            #     self._validate_rolvaliduntil(data),
            #     self._validate_rolconnlimit(data),
            #     self._validate_rolemembership(kwargs.get('rid', -1), data),
            #     self._validate_seclabels(kwargs.get('rid', -1), data),
            #     self._validate_variables(kwargs.get('rid', -1), data),
            #     self._validate_rolemembers(kwargs.get('rid', -1), data)
            # ]

            # replace_me 요청시 파라미터가 유효한지 미리 체크하는 함수인데 임시비활성화
            # for invalid_msg in invalid_msg_arr:
            #     if invalid_msg is not None:
            #         return precondition_required(invalid_msg)

            self.request = data

            return f(self, **kwargs)

        return wrap

    @staticmethod
    def _check_action(action, kwargs):
        check_permission = False
        fetch_name = False
        forbidden_msg = None
        if action in ['drop', 'update']:
            if 'pid' in kwargs:
                fetch_name = True
                check_permission = True

            if action == 'drop':
                forbidden_msg = _(
                    "The current user does not have permission to drop"
                    " the role."
                )
            else:
                forbidden_msg = _(
                    "The current user does not have permission to "
                    "update the role."
                )
        elif action == 'create':
            check_permission = True
            forbidden_msg = _(
                "The current user does not have permission to create "
                "the role."
            )
        elif action == 'msql' and 'pid' in kwargs:
            fetch_name = True

        return fetch_name, check_permission, forbidden_msg

    def _check_permission(self, check_permission, action, kwargs):
        if check_permission:
            user = self.manager.user_info

            if not user['is_superuser'] and \
                not user['can_create_password_profile'] and \
                (action != 'update' or 'pid' in kwargs) and \
                kwargs['pid'] != -1 and \
                    user['id'] != kwargs['pid']:
                return True
        return False

    def _check_and_fetch_name(self, fetch_name, kwargs):
        if fetch_name:
            status, res = self.conn.execute_dict(
                render_template(
                    self.sql_path + 'permission.sql',
                    pid=kwargs['pid'],
                    conn=self.conn
                )
            )

            if not status:
                return True, internal_server_error(
                    _(
                        "Error retrieving the role information.\n{0}"
                    ).format(res)
                )

            if len(res['rows']) == 0:
                return True, gone(
                    _("Could not find the role on the database "
                      "server.")
                )

            row = res['rows'][0]

            self.role = row['rolname']
            self.rolCanLogin = row['rolcanlogin']
            self.rolCatUpdate = row['rolcatupdate']
            self.rolSuper = row['rolsuper']

        return False, ''

    def check_precondition(action=None):
        """
        This function will behave as a decorator which will checks the status
        of the database connection for the maintainance database of the server,
        beforeexecuting rest of the operation for the wrapped function. It will
        also attach manager, conn (maintenance connection for the server) as
        properties of the instance.
        """

        def wrap(f):
            @wraps(f)
            def wrapped(self, **kwargs):
                self.manager = get_driver(
                    PG_DEFAULT_DRIVER
                ).connection_manager(
                    kwargs['sid']
                )
                self.conn = self.manager.connection()

                driver = get_driver(PG_DEFAULT_DRIVER)
                self.qtIdent = driver.qtIdent

                if not self.conn.connected():
                    return precondition_required(
                        _("Connection to the server has been lost.")
                    )

                self.datlastsysoid = (
                    self.manager.db_info.get(self.manager.did, {}).get('datlastsysoid', 0)
                    if self.manager.db_info is not None else 0
                )

                self.datistemplate = False
                if (
                    self.manager.db_info is not None and
                    self.manager.did in self.manager.db_info and
                    'datistemplate' in self.manager.db_info[self.manager.did]
                ):
                    self.datistemplate = self.manager.db_info[
                        self.manager.did]['datistemplate']
                # print('checking up manager', self.manager.__dict__)
                self.sql_path = 'passwordprofile/sql/#{0}#'.format(self.manager.version)

                self.alterKeys = [
                    'rolcanlogin', 'rolsuper', 'rolcreatedb',
                    'rolcreaterole', 'rolinherit', 'rolreplication',
                    'rolconnlimit', 'rolvaliduntil', 'rolpassword'
                ]

                fetch_name, check_permission, \
                    forbidden_msg = PasswordProfileView._check_action(action, kwargs)

                is_permission_error = self._check_permission(check_permission,
                                                             action, kwargs)
                if is_permission_error:
                    return forbidden(forbidden_msg)

                is_error, errmsg = self._check_and_fetch_name(fetch_name,
                                                              kwargs)
                if is_error:
                    return errmsg

                return f(self, **kwargs)

            return wrapped

        return wrap

    @check_precondition(action='list')
    def list(self, gid, sid):
        status, res = self.conn.execute_dict(
            render_template(
                self.sql_path + self._PROPERTIES_SQL
            )
        )

        if not status:
            return internal_server_error(
                _(ERROR_FETCHING_ROLE_INFORMATION + "\n{0}").format(res))

        # self.transform(res)

        return ajax_response(
            response=res['rows'],
            status=200
        )

    @check_precondition(action='nodes')
    def nodes(self, gid, sid):

        status, rset = self.conn.execute_2darray(
            render_template(self.sql_path + self._NODES_SQL)
        )

        if not status:
            return internal_server_error(
                _(ERROR_FETCHING_ROLE_INFORMATION + "\n{0}").format(rset))

        res = []
        for row in rset['rows']:
            res.append(
                self.blueprint.generate_browser_node(
                    row['oid'], # node_id
                    sid, # parent_id
                    row['prfname'], # label
                    'icon-password_profile' if row['oid'] else None,    # icon
                    prffailedloginattempts=row['prffailedloginattempts'], # **kwargs
                    _prffailedloginattempts_default=row['_prffailedloginattempts_default'], # **kwargs
                    _prffailedloginattempts_unlimited=row['_prffailedloginattempts_unlimited'], # **kwargs

                    _prfpasswordlocktime_default=row['_prfpasswordlocktime_default'], # **kwargs
                    _prfpasswordlocktime_unlimited=row['_prfpasswordlocktime_unlimited'], # **kwargs
                    _prfpasswordlocktime_day=row['_prfpasswordlocktime_day'], # **kwargs
                    _prfpasswordlocktime_hour=row['_prfpasswordlocktime_hour'], # **kwargs
                    _prfpasswordlocktime_minute=row['_prfpasswordlocktime_minute'], # **kwargs

                    _prfpasswordlifetime_default=row['_prfpasswordlifetime_default'], # **kwargs
                    _prfpasswordlifetime_unlimited=row['_prfpasswordlifetime_unlimited'], # **kwargs
                    _prfpasswordlifetime_day=row['_prfpasswordlifetime_day'], # **kwargs
                    _prfpasswordlifetime_hour=row['_prfpasswordlifetime_hour'], # **kwargs
                    _prfpasswordlifetime_minute=row['_prfpasswordlifetime_minute'], # **kwargs

                    _prfpasswordgracetime_default=row['_prfpasswordgracetime_default'], # **kwargs
                    _prfpasswordgracetime_unlimited=row['_prfpasswordgracetime_unlimited'], # **kwargs
                    _prfpasswordgracetime_day=row['_prfpasswordgracetime_day'], # **kwargs
                    _prfpasswordgracetime_hour=row['_prfpasswordgracetime_hour'], # **kwargs
                    _prfpasswordgracetime_minute=row['_prfpasswordgracetime_minute'], # **kwargs

                    _prfpasswordreusetime_default=row['_prfpasswordreusetime_default'], # **kwargs
                    _prfpasswordreusetime_unlimited=row['_prfpasswordreusetime_unlimited'], # **kwargs
                    _prfpasswordreusetime_day=row['_prfpasswordreusetime_day'], # **kwargs
                    _prfpasswordreusetime_hour=row['_prfpasswordreusetime_hour'], # **kwargs
                    _prfpasswordreusetime_minute=row['_prfpasswordreusetime_minute'], # **kwargs

                    prfpasswordreusemax=row['prfpasswordreusemax'], # **kwargs
                    _prfpasswordreusemax_default=row['_prfpasswordreusemax_default'], # **kwargs
                    _prfpasswordreusemax_unlimited=row['_prfpasswordreusemax_unlimited'], # **kwargs

                    prfpasswordverifyfuncdb=row['prfpasswordverifyfuncdb'],
                    prfpasswordverifyfunc=row['prfpasswordverifyfunc'],
                )
            )

        return make_json_response(
            data=res,
            status=200
        )

    @check_precondition(action='node')
    def node(self, gid, sid, rid):

        status, rset = self.conn.execute_2darray(
            render_template(
                self.sql_path + self._NODES_SQL,
                rid=rid
            )
        )

        if not status:
            return internal_server_error(
                _(
                    ERROR_FETCHING_ROLE_INFORMATION + "\n{0}").format(rset))

        for row in rset['rows']:
            return make_json_response(
                data=self.blueprint.generate_browser_node(
                    row['oid'],
                    sid,
                    row['rolname'],
                    'icon-role' if row['rolcanlogin'] else 'icon-group',
                    can_login=row['rolcanlogin'],
                    is_superuser=row['rolsuper']
                ),
                status=200
            )

        return gone()

    def _set_seclabels(self, row):

        if 'seclabels' in row and row['seclabels'] is not None:
            res = []
            for sec in row['seclabels']:
                sec = re.search(r'([^=]+)=(.*$)', sec)
                res.append({
                    'provider': sec.group(1),
                    'label': sec.group(2)
                })
            row['seclabels'] = res

    def _set_rolemembership(self, row):

        if 'rolmembers' in row:
            rolmembers = []
            for role in row['rolmembers']:
                role = re.search(r'([01])(.+)', role)
                rolmembers.append({
                    'role': role.group(2),
                    'admin': True if role.group(1) == '1' else False
                })
            row['rolmembers'] = rolmembers


    def prfassociation_transform(self, rset):
        for row in rset['rows']:
            res = []

            row['prfassociation'] = row['prfassociation'].replace('{', '').replace('}', '')
            assoarray = row['prfassociation'].split(',')
            print(assoarray)
            for asso in assoarray:
                if asso != '':
                    res.append(asso)
            row['prfassociation'] = res

    def transform(self, rset):
        for row in rset['rows']:
            res = []

            roles = row['rolmembership']

            row['rolpassword'] = ''
            for role in roles:
                role = re.search(r'([01])(.+)', role)
                res.append({
                    'role': role.group(2),
                    'admin': True if role.group(1) == '1' else False
                })
            row['rolmembership'] = res
            self._set_seclabels(row)
            self._set_rolemembership(row)

    @check_precondition(action='properties')
    def properties(self, gid, sid, ppid):

        status, res = self.conn.execute_dict(
           'select prfpasswordverifyfunc from ag_profile as ap where ap.oid = ' + str(ppid)
        )
        _func_oid = res['rows'][0]['prfpasswordverifyfunc']

        status, res = self.conn.execute_dict(
            'select prfpasswordverifyfuncdb from ag_profile as ap where ap.oid = ' + str(ppid)
        )
        _func_db_oid = res['rows'][0]['prfpasswordverifyfuncdb']


        if _func_db_oid is None:
            _func_db_oid = self.manager.did

        from pgadmin.utils.driver import get_driver
        _temp_manager = get_driver(PG_DEFAULT_DRIVER).connection_manager(sid)
        print(_temp_manager.__dict__)

        _target_did_conn = _temp_manager.connection(did=_func_db_oid, auto_reconnect=True)
        print(_target_did_conn.__dict__)

        #데이터베이스 연결(안되어있다면 연결,되어있다면 넘김)
        already_connected = _target_did_conn.connected()
        if not already_connected:
            status, errmsg = _target_did_conn.connect()
            if not status:
                current_app.logger.error(
                    "Could not connected to database(#{0}).\nError: {1}"
                        .format(
                        _func_db_oid, errmsg
                    )
                )

                return internal_server_error(errmsg)
            else:
                current_app.logger.info(
                    'Connection Established for Database Id: \
                    %s' % (_func_db_oid)
                )

        # status, res = self.conn.execute_dict(
        status, res = _target_did_conn.execute_dict( #db커넥션을 만든 후 쿼리
            render_template(
                self.sql_path + self._PROPERTIES_SQL,
                ppid=ppid,
                funcoid=_func_oid
            )
        )

        if not status:
            return internal_server_error(
                _(ERROR_FETCHING_ROLE_INFORMATION + "\n{0}").format(res))

        self.prfassociation_transform(res)

        _response = res['rows'][0]
        # _target_did_conn.close() # 명시적 커넥션 클로즈해야되는데 못찾음

        return ajax_response(
            response=_response,
            status=200
        )

    @check_precondition(action='drop')
    def drop(self, gid, sid, ppid=None):

        if self.manager.user_info['is_superuser'] is False:
            return internal_server_error(
                _("Only superuser can drop the password profile.\n")
            )

        if ppid is None:
            data = request.form if request.form else json.loads(
                request.data, encoding='utf-8'
            )
        else:
            data = {'ids': [ppid]}

        for ppid in data['ids']:
            prfname_fetch_stmt = " SELECT prfname " \
                   " FROM ag_profile " \
                   " WHERE oid = " + str(ppid) + "::oid;"

            status, prfname = self.conn.execute_scalar(prfname_fetch_stmt)

            if not status:
                return internal_server_error(
                    _("Could not fetch the profile name.\n{0}").format(prfname)
                )

            drop_passwordprofile_stmt = " DROP PROFILE " + prfname + \
                                        " RESTRICT "

            status, res = self.conn.execute_void(drop_passwordprofile_stmt)

            if not status:
                return internal_server_error(
                    _("Could not drop the password profile.\n{0}").format(res)
                )
        return success_return()

    @check_precondition()
    def sql(self, gid, sid, ppid):
        # show_password = self.conn.manager.user_info['is_superuser']
        status, res = self.conn.execute_scalar(
            render_template(
                self.sql_path + 'sql.sql'
                , ppid=ppid
            )
        )

        if not status:
            return internal_server_error(
                _("Could not generate reversed engineered query for the "
                  "role.\n{0}").format(
                    res
                )
            )

        if res is None or (len(res) == 0):
            return gone(
                _("Could not generate reversed engineered query for the role.")
            )

        return ajax_response(response=res.strip('\n'))


    def default_or_unmlimited_transfromer(self, gid, sid, source):
        sql = render_template(self.sql_path + 'default_or_unmlimited_transfromer.sql',
                                      data=source,
                                      dummy=False,
                                      conn=self.conn)
        status, result = self.conn.execute_dict(sql)

        if not status:
            return internal_server_error(
                _("Could not execute interval converting.\n{0}").format(result)
            )

        return (result['rows'])[0]

    def unepoching(self, gid, sid, source):
        """
        interval 형태로 표현된 시간을 day,hour,minutes로 분리한 dict 리턴.
        """
        unepoch_sql = render_template(self.sql_path + self._UNEPOCH_SQL,
                                      data=source,
                                      dummy=False,
                                      conn=self.conn)
        status, unepoched = self.conn.execute_dict(unepoch_sql)

        if not status:
            return internal_server_error(
                _("Could not execute interval converting.\n{0}").format(unepoched)
            )

        return (unepoched['rows'])[0]

    def epoching(self, gid, sid, source):
        """
        day, hour, minutes로 표현된 시간을 interval 형태로 병합한 dict 리턴.
        """
        self.manager = get_driver(
            PG_DEFAULT_DRIVER
        ).connection_manager(sid)
        self.conn = self.manager.connection()

        # driver = get_driver(PG_DEFAULT_DRIVER)
        # self.qtIdent = driver.qtIdent

        if not self.conn.connected():
            return precondition_required(
                _("Connection to the server has been lost.")
            )

        epoch = render_template(
            self.sql_path + 'epoch.sql',
            data=source,
            dummy=False,
            conn=self.conn
        )
        status, rset = self.conn.execute_dict(epoch)

        if not status:
            return internal_server_error(
                _("Could not epoch timedata.\n{0}").format(rset)
            )

        return (rset['rows'])[0]


    def _update_function_process(self, sid, request):

        def _create_func(conn, sql):
            status, rset = conn.execute_dict(sql)
            if not status:
                return internal_server_error(
                    _("Could not create function.\n{0}").format(rset)
                )

        def _extract_funcname_by_oid(conn, funcoid, funcdboid):
            sql = 'SELECT pr.proname FROM pg_catalog.pg_proc as pr, pg_catalog.pg_namespace as ns, pg_catalog.pg_database as db ' \
                  'WHERE pr.oid = {0}::oid and db.oid = {1}::oid and pr.pronamespace = ns.oid;'

            status, funcname = conn.execute_scalar(sql.format(funcoid, funcdboid))

            if not status:
                return internal_server_error(
                    _("Could not retrieve function info.\n{0}").format(funcname)
                )
            return funcname

        def _alter_profile_func(conn, prf_name, func_name):
            sql = 'ALTER PROFILE {0} LIMIT PASSWORD_VERIFY_FUNCTION {1};'
            status, rset = conn.execute_dict(sql.format(prf_name, func_name))
            if not status:
                return internal_server_error(
                    _("Could not alter profile verification function.\n{0}").format(rset)
                )

        def _select_public_schema_oid(conn):
            sql = "select oid from pg_catalog.pg_namespace where nspname = 'public';"
            status, rset = conn.execute_dict(sql)
            if not status:
                return internal_server_error(
                    _("Could not alter profile verification function.\n{0}").format(rset)
                )

        def _extract_profile_info_by_oid(ppid):
            status, res = self.conn.execute_dict(
                    'select prfpasswordverifyfunc from ag_profile as ap where ap.oid = ' + str(ppid)
                )
            _func_oid = res['rows'][0]['prfpasswordverifyfunc']

            status, res = self.conn.execute_dict(
                'select prfpasswordverifyfuncdb from ag_profile as ap where ap.oid = ' + str(ppid)
            )
            _func_db_oid = res['rows'][0]['prfpasswordverifyfuncdb']

            #dboid 조회 후 커넥션 재생성
            _target_db_conn = self.manager.connection(did=_func_db_oid)

            status, res = _target_db_conn.execute_dict( #db커넥션을 만든 후 쿼리
                render_template(
                    self.sql_path + self._PROPERTIES_SQL,
                    ppid=ppid,
                    funcoid=_func_oid
                )
            )
            return res['rows'][0]

        def _extract_funcname_by_sql(sql):
            funcname = (sql.split('FUNCTION')[1].split('(')[0]).strip()
            if '.' in funcname:
                funcname= funcname.split('.')[1]
            return funcname

        def _cutoff_verification_function_in_profile(conn,prfname):
            sql = "ALTER PROFILE {0} LIMIT password_verify_function NULL;"
            status, rset = conn.execute_dict(sql.format(prfname))

            if not status:
                return internal_server_error(
                    _("Could not alter profile verification function.\n{0}").format(rset)
                )

        ## 기본 서버용 커넥션 매니저 우선 생성
        self.manager = get_driver(
            PG_DEFAULT_DRIVER
        ).connection_manager(sid=sid)
        #oid로 지정된 기존 패스워드프로파일 조회
        _password_profile = _extract_profile_info_by_oid(ppid=request['oid']) # dict
        #값이 있는채로 request에 담겨오면 덮어씌우기, 아니면 기존 테이블값으로 진행
        if 'prfpasswordverifyfunc' in request and request['prfpasswordverifyfunc'] is not None:
            _funcoid = request['prfpasswordverifyfunc']
        else:
            _funcoid = _password_profile['prfpasswordverifyfunc']
        if 'prfpasswordverifyfuncdb' in request and request['prfpasswordverifyfuncdb'] is not None and request['prfpasswordverifyfuncdb'] :
            _funcdboid = request['prfpasswordverifyfuncdb']
        else:
            _funcdboid = _password_profile['prfpasswordverifyfuncdb']
        if 'prfpasswordverifyfuncschema' in request and request['prfpasswordverifyfuncschema'] is not None:
            _funcschemaoid = request['prfpasswordverifyfuncschema']
        else:
            _funcschemaoid = _password_profile['prfpasswordverifyfuncschema']

        if _funcdboid is None:
            _funcdboid = self.manager.did

        _target_db_conn = self.manager.connection(did=_funcdboid)

        if request['editMode'] == "load":
            _alter_profile_func(_target_db_conn, _password_profile['prfname'], _extract_funcname_by_oid(_target_db_conn,_funcoid,_funcdboid))
        elif request['editMode'] == "edit":
            # 함수 수정 하여 새로 생성
            _create_func(_target_db_conn, request['prfpasswordverifyfuncsql'])
            # editMode값이 edit인데 dboid가 없을경우 삭제로 간주            
            if 'prfpasswordverifyfuncsql' in request:
                if request['prfpasswordverifyfuncsql'] != "--Sciprt Load Error" :
                    # 새로 생성한 함수를 sql에서 이름을 찾아 검색하여 함수 업데이트
                    _funcname = _extract_funcname_by_sql(request['prfpasswordverifyfuncsql'])
                    _alter_profile_func(_target_db_conn, _password_profile['prfname'],_funcname)
                else:
                    None
            elif 'prfpasswordverifyfuncdb' not in request and 'prfpasswordverifyfuncschema' not in request and 'prfpasswordverifyfunc' not in request:
                None
            elif 'prfpasswordverifyfuncsql' in request:
                if request['prfpasswordverifyfuncsql'] == "--Sciprt Load Error":
                    _cutoff_verification_function_in_profile(self.conn, _password_profile['prfname'])
            elif 'prfpasswordverifyfunc' in request:
                if request['prfpasswordverifyfunc'] == "" :
                    _cutoff_verification_function_in_profile(self.conn, _password_profile['prfname'])
            elif 'prfpasswordverifyfuncschema' in request:
                if request['prfpasswordverifyfuncschema'] == "":
                    _cutoff_verification_function_in_profile(self.conn, _password_profile['prfname'])
            elif 'prfpasswordverifyfuncdb' in request:
                if request['prfpasswordverifyfuncdb'] == "": 
                    _cutoff_verification_function_in_profile(self.conn, _password_profile['prfname'])                
        elif request['editMode'] == "new":
            # 함수 생성
            _create_func(_target_db_conn, request['prfpasswordverifyfuncsql'])
            # 새로 생성한 함수를 sql에서 이름을 찾아 검색하여 함수 업데이트
            _funcname = _extract_funcname_by_sql(request['prfpasswordverifyfuncsql'])
            _alter_profile_func(_target_db_conn, _password_profile['prfname'],_funcname)

        if 'prfpasswordverifyfuncdb' in request and \
            request['prfpasswordverifyfuncdb'] == "" and \
            _password_profile['prfpasswordverifyfuncdb'] > 0:
            print('이전 프로필은 db있는데, 리퀘스트 날라올떄 db oid 없는 경우, 삭제로 볼 수 있음')
            _cutoff_verification_function_in_profile(self.conn, _password_profile['prfname'])
        elif 'prfpasswordverifyfuncsql' in request:
            if request['prfpasswordverifyfuncsql'] == '--Sciprt Load Error':
                _cutoff_verification_function_in_profile(self.conn, _password_profile['prfname'])
        elif 'prfpasswordverifyfunc' in request:
            if request['prfpasswordverifyfunc'] == "" :
                _cutoff_verification_function_in_profile(self.conn, _password_profile['prfname'])
        elif 'prfpasswordverifyfuncschema' in request:
            if request['prfpasswordverifyfuncschema'] == "":
                _cutoff_verification_function_in_profile(self.conn, _password_profile['prfname'])
        elif 'prfpasswordverifyfuncdb' in request:
            if request['prfpasswordverifyfuncdb'] == "": 
                _cutoff_verification_function_in_profile(self.conn, _password_profile['prfname']) 
            # 프로필에 연관된 함수정보 삭제(실제 함수 삭제가 아님, 연관관계만 끊기)
            # 프로필 이름만 필요함
        return None

    def verify_function_process(self, sid, request):

        def _extract_funcname_by_sql(sql):
            funcname = (sql.split('FUNCTION')[1].split('(')[0]).strip()
            if '.' in funcname:
                funcname= funcname.split('.')[1]
            return funcname

        def _extract_funcname_by_oid(conn):
            sql = 'SELECT pr.proname FROM pg_catalog.pg_proc as pr, pg_catalog.pg_namespace as ns, pg_catalog.pg_database as db ' \
                  'WHERE pr.oid = {0}::oid and db.oid = {1}::oid and pr.pronamespace = ns.oid;'

            status, funcname = conn.execute_scalar(sql.format(request['prfpasswordverifyfunc'],request['prfpasswordverifyfuncdb']))

            if not status:
                return internal_server_error(
                    _("Could not retrieve function info.\n{0}").format(funcname)
                )
            return funcname

        def _create_func(conn, sql):
            status, rset = conn.execute_dict(sql)
            if not status:
                return internal_server_error(
                    _("Could not create function.\n{0}").format(rset)
                )

        def _alter_profile_func(conn, prf_name, func_name):
            sql = 'ALTER PROFILE {0} LIMIT PASSWORD_VERIFY_FUNCTION {1};'
            status, rset = conn.execute_dict(sql.format(prf_name, func_name))
            if not status:
                return internal_server_error(
                    _("Could not alter profile verification function.\n{0}").format(rset)
                )

        #리턴용
        additional_funcinfo = dict()

        func_oid = request['prfpasswordverifyfunc']
        func_sql = request['prfpasswordverifyfuncsql']
        schema_oid = request['prfpasswordverifyfuncschema']
        db_oid = request['prfpasswordverifyfuncdb']



        if db_oid is None:
            db_oid = self.manager.did
        # 원격 db에 함수생성용 서버매니저로부터 타겟 db커넥션 생성
        self.manager = get_driver(
            PG_DEFAULT_DRIVER
        ).connection_manager(sid)
        _temp_conn = self.manager.connection(did=db_oid)

        print("_temp_conn : {0}", _temp_conn)

        if not 'editMode' in request:
            return None
        if request['editMode'] == "load":
            _alter_profile_func(_temp_conn, request['prfname'],_extract_funcname_by_oid(_temp_conn))
        elif request['editMode'] == "edit":
            _create_func(_temp_conn, request['prfpasswordverifyfuncsql'])
            _funcname = _extract_funcname_by_sql(request['prfpasswordverifyfuncsql'])
            _alter_profile_func(_temp_conn, request['prfname'],_funcname)
        elif request['editMode'] == "new":
            _create_func(_temp_conn, request['prfpasswordverifyfuncsql'])
            _funcname = _extract_funcname_by_sql(request['prfpasswordverifyfuncsql'])
            _alter_profile_func(_temp_conn, request['prfname'],_funcname)

        #함수생성용 커넥션 릴리즈
        self.manager.release(conn_id=_temp_conn)
        return additional_funcinfo


    @check_precondition(action='create')
    @validate_request
    def create(self, gid, sid):

        # 프로파일 생성 처리
        epoched_data = self.epoching(gid,sid,self.request)
        (self.request).update(epoched_data)

        sql = render_template(
            self.sql_path + self._CREATE_SQL,
            data=self.request,
            dummy=False,
            conn=self.conn
        )
        status, msg = self.conn.execute_void(sql)

        print('테스트용 리퀘스트 데이터 출력')
        print(str(self.request))

        # verify function 설정 -  ALTER PROFILE 처리
        self.verify_function_process(sid, self.request)

        # association 설정 - ALTER PROFILE 처리
        alter_role_sql = render_template(
            self.sql_path + 'associate.sql',
            data=self.request,
            dummy=False,
            conn=self.conn
        )

        if len(alter_role_sql.strip()) > 2:
            status, msg = self.conn.execute_void(alter_role_sql)
            if not status:
                return internal_server_error(
                    _("Could not create the profile.\n{0}").format(msg)
                )

        #프로필 이름으로 oid 추출
        status, ppid = self.conn.execute_scalar(
            "SELECT oid FROM ag_profile WHERE prfname = %(prfname)s",
            {'prfname': self.request['prfname']}
        )

        if not status:
            return internal_server_error(
                _(ERROR_FETCHING_PROFILE_INFORMATION + "\n{0}").format(msg))

        # 트리노드 상태 refresh
        status, rset = self.conn.execute_dict(
            render_template(self.sql_path + self._NODES_SQL,
                            ppid=ppid)
        )
        if not status:
            return internal_server_error(
                _(
                    ERROR_FETCHING_ROLE_INFORMATION + "\n{0}").format(rset))
        for row in rset['rows']:
            return jsonify(
                node=self.blueprint.generate_browser_node(
                    ppid, #_id
                    sid, #pid
                    row['prfname'], #id
                    'icon-password_profile'
                )
            )

        return gone(self.not_found_error_msg())


    def _get_profile(self, ppid):
        status, old_profile = self.conn.execute_dict(
            "select * from ag_profile where oid=" + str(ppid) + "::oid ;"
        )

        if not status:
            return internal_server_error(
                _("Could not retrieve the profile.\n{0}").format(old_profile)
            )
        return old_profile['rows'][0]

    @check_precondition(action='update')
    @validate_request
    def update(self, gid, sid, ppid):

        #변경 전 프로필 테이블값 oid로 조회
        old_profile_row = self._get_profile(ppid)
        print('old_profile_row==========')
        print(old_profile_row)

        #이전 프로필 db조회값의 시간정보값 형변환 ( 3600 -> 1 hours )
        unepoched_old_profile_dict = self.unepoching(gid, sid, old_profile_row)

        #이전의 프로필 테이블값에서 DEFAULT, UNLIMITED 값을 dict key값으로 치환
        transform_result = self.default_or_unmlimited_transfromer(gid, sid, old_profile_row)

        # default_or_unmlimited_transfromer 함수로 처리되지 않는 키값 처리
        if transform_result['_prfpassword_reuse_max_unlimited'] is True \
            or transform_result['_prfpassword_reuse_max_default'] is True:
            transform_result['prfpasswordreusemax'] = 0
        if transform_result['_prffailed_login_attempts_unlimited'] is True \
            or transform_result['_prffailed_login_attempts_default'] is True:
            transform_result['prffailedloginattempts'] = 0

        print('변환결과 transform_result')
        print(transform_result)

        # 키값 추가결과하여  업데이트
        unepoched_old_profile_dict.update(transform_result)

        #프로필 시간정보값 업데이트 온 값만 덮어쓰기 ( 1 hours -> 1 days 12 hours )
        unepoched_old_profile_dict.update(self.request)
        print('key added unepoched_old_profile_dict==========')
        print(unepoched_old_profile_dict)

        # 최신 시간정보 기준으로 프로필 입력형태로 조정 (1 days 12 hours -> 1.5)
        epoched_updated_profile_dict = self.epoching(gid, sid, unepoched_old_profile_dict)

        # sql 입력형태로 조정하여 dict update
        unepoched_old_profile_dict.update(epoched_updated_profile_dict)

        print('time updated unepoched_old_profile_dict==========')
        print(unepoched_old_profile_dict)

        #바뀐 이름을 대상으로하여 프로필 속성값들 변경
        sql = render_template(
            self.sql_path + self._UPDATE_SQL,
            data=unepoched_old_profile_dict,
            requestParam=self.request,
            olddata=old_profile_row,
            dummy=False,
            conn=self.conn,
            alterKeys=self.alterKeys
        )

        if sql.isspace():
            pass
        else:
            status, msg = self.conn.execute_dict(sql)
            if not status:
                return internal_server_error(
                    _("Could not update the profile.\n{0}").format(msg)
                )

        unepoched_old_profile_dict.update({'prfname':old_profile_row['prfname']})

        # association 업데이트 - ALTER PROFILE 처리 ( 리퀘스트 값으로 넘어온 경우에만 처리 )
        if 'prfassociation' in unepoched_old_profile_dict:

            association_length = len(unepoched_old_profile_dict['prfassociation'])

            alter_role_sql = render_template(
                self.sql_path + 'update_associate.sql',
                data=unepoched_old_profile_dict,
                dummy=False,
                conn=self.conn,
                association_length=association_length
            )

            status, msg = self.conn.execute_void(alter_role_sql)

            if not status:
                return internal_server_error(
                    _("Could not create the profile.\n{0}").format(msg)
                )


        # request에 키값 'editMode' 가 없으면,함수관련 수정을 하지 않는것으로 가정.
        # 함수 관련 프로필 업데이트
        if 'editMode' in self.request:
            self._update_function_process(sid, self.request)

        # editMode가 없는 경우, 함수 메뉴 자체를 진입하지 않았거나

        # tree node 현황 갱신(update)
        status, rset = self.conn.execute_dict(
            render_template(self.sql_path + self._NODES_SQL,
                            ppid=ppid))

        if not status:
            return internal_server_error(
                _(ERROR_FETCHING_ROLE_INFORMATION + "\n{0}").format(rset))

        for row in rset['rows']:
            return jsonify(
                node=self.blueprint.generate_browser_node(
                    ppid, sid,
                    row['prfname'],
                    'icon-password_profile'
                )
            )

        return gone(self.not_found_error_msg())

    @check_precondition(action='msql')
    @validate_request
    def msql(self, gid, sid, ppid=None):

        def _extract_funcname_by_sql(sql):
            if '-- FUNCTION:' in sql and '-- DROP FUNCTION' in sql :
                funcname = (sql.split('CREATE OR REPLACE FUNCTION ')[1].split('(')[0]).strip()
                if '.' in funcname:
                    funcname= funcname.split('.')[1]
                return funcname
            else :
                funcname = (sql.split('FUNCTION')[1].split('(')[0]).strip()
                if '.' in funcname:
                    funcname= funcname.split('.')[1]
                return funcname

        def _extract_funcname_by_oid(conn, request):
            sql = 'SELECT pr.proname FROM pg_catalog.pg_proc as pr, pg_catalog.pg_namespace as ns, pg_catalog.pg_database as db ' \
                  'WHERE pr.oid = {0}::oid and db.oid = {1}::oid and pr.pronamespace = ns.oid;'

            status, funcname = conn.execute_scalar(sql.format(int(request['prfpasswordverifyfunc']),int(request['prfpasswordverifyfuncdb'])))

            if not status:
                return internal_server_error(
                    _("Could not retrieve function info.\n{0}").format(funcname)
                )
            return funcname

        def _extract_rolname_by_prf_oid(profile_oid):
            sql = 'select rolname from pg_authid where rolprofile={0}::oid'
            status, rolname = self.conn.execute_dict(sql.format(int(profile_oid)))

            if not status:
                return internal_server_error(
                    _("Could not retrieve function info.\n{0}").format(funcname)
                )

            return rolname['rows']


        # 새로 생성하는 경우
        if ppid is None:

            ##url 쿼리파라미터로 오는 값들은 전부 string이므로 기존에 썼던 형변환이나
            #분기체크가 작동하지 않음. 새로 파일 정의하여 처리함
            #나중에 리팩토링 요소 본명 있을것임

            _request = self.request

            #msql 전용 시간변환
            epoched = render_template(
                self.sql_path + 'msql_epoch.sql',
                data=_request,
                dummy=False,
                conn=self.conn
            )

            status, rset = self.conn.execute_dict(epoched)

            if not status:
                return internal_server_error(
                    _("Could not epoch timedata.\n{0}").format(rset)
                )

            epoched_data = (rset['rows'])[0]

            # 시간변환 결과 업데이트
            _request.update(epoched_data)

            # msql 전용 cretae문 (시간만 epoched되어 반영되었음)
            epoched_sql = render_template(
                self.sql_path + 'msql_create.sql',
                data=_request,
                dummy=True,
                conn=self.conn)

            import json

            json.dumps(  {'prfassociation': _request['prfassociation'] } )
            asso_dumped = json.loads(json.dumps(_request))

            result_sql = epoched_sql

            if 'prfassociation' in _request and _request['prfassociation'] != ['']:
                array = _request['prfassociation'].lstrip('[').rstrip(']').split(',')

                asso_dict = dict()
                asso_dict['prfassociation'] = array
                _request.update(asso_dict)

                print(_request['prfassociation'])

                asso_sql = render_template(
                    self.sql_path + 'msql_create_associate.sql',
                    data=_request['prfassociation'],
                    prfname=_request['prfname'],
                    dummy=True,
                    conn=self.conn)
                result_sql = result_sql + \
                             '\n -- associating roles with profile. \n ' \
                             + asso_sql

            #리퀘스트에 이것저것 값을 마구잡이로 변경한 경우에는, editMode와 무관하게 변경을 시도한 모든값이 전달될 수 있음.
            #예) 마지막 전달은 new인데, 이전 load클릭시 지정했던 func의 oid가 전달된다던가 하는 경우가 있음
            #mode를 통해 사용자로부터 입력받은 변수를 한정짓는 방식을 택해야 함.

            funcname=''
            create_or_replace_func_sql_string = ''
            if 'editMode' in _request and len(_request['editMode']) >= 3:
                if _request['editMode'] == 'load' \
                    and 'prfpasswordverifyfunc' in _request \
                    and 'prfpasswordverifyfuncschema' in _request \
                    and 'prfpasswordverifyfuncdb' in _request:
                    funcname = _extract_funcname_by_oid(self.conn)

                if _request['editMode'] == 'new' \
                    and 'prfpasswordverifyfuncsql' in _request \
                    and 'prfpasswordverifyfuncschema' in _request \
                    and 'prfpasswordverifyfuncdb' in _request :
                    funcname = _extract_funcname_by_sql(_request['prfpasswordverifyfuncsql'])
                    create_or_replace_func_sql_string = '\n -- create or replace function to assigning profile. ' \
                                                        '\n{0}\n'.format(_request['prfpasswordverifyfuncsql'])

                if _request['editMode'] == 'edit' \
                    and 'prfpasswordverifyfuncsql' in _request \
                    and 'prfpasswordverifyfuncschema' in _request \
                    and 'prfpasswordverifyfuncdb' in _request :
                    funcname = _extract_funcname_by_sql(_request['prfpasswordverifyfuncsql'])
                    create_or_replace_func_sql_string = '\n -- create or replace function to assigning profile. ' \
                                                        '\n{0}\n'.format(_request['prfpasswordverifyfuncsql'])

                assigning_func_sql_string = '\n -- assigning verification function to profile. ' \
                                  '\n ALTER PROFILE {0} LIMIT PASSWORD_VERIFY_FUNCTION {1};'.format(_request['prfname'], funcname)

                result_sql = result_sql + create_or_replace_func_sql_string + assigning_func_sql_string

            return make_json_response(
                data= (result_sql).strip('\n')
            )

        # 기존것 업데이트 하는 경우(oid 있음)
        else:

            _request = self.request

            #변경 전 프로필 테이블값 oid로 조회
            old_profile_row = self._get_profile(ppid)

            #이전 프로필 db조회값의 시간정보값 형변환 ( 3600 -> 1 hours )
            unepoched_old_profile_dict = self.unepoching(gid, sid, old_profile_row)

            #이전의 프로필 테이블값에서 DEFAULT, UNLIMITED 값을 dict key값으로 치환
            transform_result = self.default_or_unmlimited_transfromer(gid, sid, old_profile_row)

            # default_or_unmlimited_transfromer 함수로 처리되지 않는 키값 처리
            # unlimited 또는 default인 경우 reusemax 값이나 attempts 같은 정수값을 가지는 키값을 삭제함(분기처리 방지)

            if transform_result['_prfpassword_reuse_max_unlimited'] is True \
                or transform_result['_prfpassword_reuse_max_default'] is True:
                transform_result.pop('prfpasswordreusemax')
            if transform_result['_prffailed_login_attempts_unlimited'] is True \
                or transform_result['_prffailed_login_attempts_default'] is True:
                transform_result.pop('prffailedloginattempts')

            print('변환결과 transform_result')
            print(transform_result)

            # 키값 추가결과하여  업데이트
            unepoched_old_profile_dict.update(transform_result)

            #프로필 시간정보값 업데이트 온 값만 덮어쓰기 ( 1 hours -> 1 days 12 hours )
            unepoched_old_profile_dict.update(self.request)

            # 최신 시간정보 기준으로 프로필 입력형태로 조정 (1 days 12 hours -> 1.5)
            epoched_updated_profile_dict = self.epoching(gid, sid, unepoched_old_profile_dict)

            # sql 입력형태로 조정하여 dict update
            unepoched_old_profile_dict.update(epoched_updated_profile_dict)

            print('time updated unepoched_old_profile_dict==========')
            print(unepoched_old_profile_dict)

            result_sql = ''
            #epoched 계산한 시간 업데이트문
            #바뀐 이름을 대상으로하여 프로필 속성값들 변경
            epoched_sql = render_template(
                self.sql_path + self._UPDATE_SQL,
                data=unepoched_old_profile_dict,
                requestParam=self.request,
                olddata=old_profile_row,
                dummy=False,
                conn=self.conn,
                alterKeys=self.alterKeys
            )

            result_sql = epoched_sql

            #이름의 변경이 있을 경우, 변경을 원하는 이름으로 프로필 이름 교체(없으면 예전이름 사용)
            if ('prfname' in _request and _request['prfname'] != old_profile_row['prfname']):
                prfname = _request['prfname']
            else:
                prfname = old_profile_row['prfname']

            # profile의 갖는 asso 업데이트
            if 'prfassociation' in _request and _request['prfassociation'] != ['']:

                requested_asso_array = _request['prfassociation'].lstrip('[').rstrip(']').replace('\"', '').split(',')

                asso_dict = dict()
                asso_dict['prfassociation'] = requested_asso_array
                _request.update(asso_dict)

                for rolname in requested_asso_array:
                    print(rolname)

                rolname_dict = _extract_rolname_by_prf_oid(ppid)

                old_role_list = []
                for d in rolname_dict:
                    old_role_list.append( (dict(d)['rolname']))

                old_asso_set = set(old_role_list)
                requested_asso_set = set(requested_asso_array)

                assign_asso_sql =  '\n -- attaching role\'s association from profile. \n '
                for rolname in (requested_asso_set - old_asso_set):
                    assign_asso_sql = assign_asso_sql + 'ALTER role {0} PROFILE {1} \n'.format(rolname,prfname)

                remove_asso_sql =  '\n -- detaching role\'s association from profile. \n '
                for rolname in (old_asso_set - requested_asso_set):
                    remove_asso_sql = remove_asso_sql + 'ALTER role {0} PROFILE \"NULL\" \n'.format(rolname)

                result_sql = result_sql + assign_asso_sql + remove_asso_sql


            # func 업데이트문
            funcname=''
            create_or_replace_func_sql_string = ''

            #삭제에 해당되는 경우
            if ('prfpasswordverifyfuncdb' in _request and _request['prfpasswordverifyfuncdb'] is None) or \
                ('prfpasswordverifyfuncschema' in _request and _request['prfpasswordverifyfuncschema'] is None) or \
                ('prfpasswordverifyfunc' in _request and _request['prfpasswordverifyfunc'] is None) or \
                ('prfpasswordverifyfuncsql' in _request and  _request['prfpasswordverifyfuncsql'] is None) or \
                 _request['prfpasswordverifyfuncsql'].strip() == '--Sciprt Load Error' or \
                 _request['prfpasswordverifyfuncsql'].strip() == 'CREATE OR REPLACE FUNCTION' :

                detach_verify_func_from_profile_sql_string = '\n -- detaching verify function from profile. ' \
                                                             '\n ALTER PROFILE {0} LIMIT PASSWORD_VERIFY_FUNCTION NULL;'.format(prfname)

                result_sql = result_sql + detach_verify_func_from_profile_sql_string

            elif bool(_request.get('editMode')):

                ##이 분기에서 오류남. load누르고 함수 변경시에.
                if _request['editMode'] == 'load':

                    if 'prfpasswordverifyfuncdb' not in _request:
                        _request['prfpasswordverifyfuncdb'] = old_profile_row['prfpasswordverifyfuncdb']
                    funcname = _extract_funcname_by_oid(self.conn, _request)

                if _request['editMode'] == 'new':
                    funcname = _extract_funcname_by_sql(_request['prfpasswordverifyfuncsql'])
                    create_or_replace_func_sql_string = '\n -- create or replace function to assigning profile. ' \
                                                        '\n{0}\n'.format(_request['prfpasswordverifyfuncsql'])

                if _request['editMode'] == 'edit':
                    funcname = _extract_funcname_by_sql(_request['prfpasswordverifyfuncsql'])
                    create_or_replace_func_sql_string = '\n -- create or replace function to assigning profile. ' \
                                                        '\n{0}\n'.format(_request['prfpasswordverifyfuncsql'])

                assigning_func_sql_string = '\n -- assigning verification function to profile. ' \
                                            '\n ALTER PROFILE {0} LIMIT PASSWORD_VERIFY_FUNCTION {1};'.format(prfname, funcname)

                result_sql = result_sql + create_or_replace_func_sql_string + assigning_func_sql_string

            return make_json_response(
                data=result_sql.strip('\n')
            )

    @check_precondition()
    def dependencies(self, gid, sid, ppid):
        """
        This function gets the dependencies and returns an ajax response
        for the role.

        Args:
            gid: Server Group ID
            sid: Server ID
            rid: Role ID
        """
        dependencies_result = self.get_dependencies(self.conn, ppid)
        return ajax_response(
            response=dependencies_result,
            status=200
        )

    @check_precondition()
    def dependents(self, gid, sid, ppid):
        """
        This function gets the dependents and returns an ajax response
        for the role.

        Args:
            gid: Server Group ID
            sid: Server ID
            rid: Role ID
        """
        dependents_result = self.get_dependents(self.conn, sid, ppid)
        return ajax_response(
            response=dependents_result,
            status=200
        )

    @staticmethod
    def _handle_dependents_type(types, type_str, type_name, rel_name, row):
        if types[type_str[0]] is None:
            if type_str[0] == 'i':
                type_name = 'index'
                rel_name = row['indname'] + ' ON ' + rel_name
            elif type_str[0] == 'o':
                type_name = 'operator'
                rel_name = row['relname']
        else:
            type_name = types[type_str[0]]

        return type_name, rel_name

    @staticmethod
    def _handle_dependents_data(result, types, dependents, db_row):
        for row in result['rows']:
            rel_name = row['nspname']
            if rel_name is not None:
                rel_name += '.'

            if rel_name is None:
                rel_name = row['relname']
            else:
                rel_name += row['relname']

            type_name = ''
            type_str = row['relkind']
            # Fetch the type name from the dictionary
            # if type is not present in the types dictionary then
            # we will continue and not going to add it.
            if type_str[0] in types:
                # if type is present in the types dictionary, but it's
                # value is None then it requires special handling.
                type_name, rel_name = PasswordProfileView._handle_dependents_type(
                    types, type_str, type_name, rel_name, row)
            else:
                continue

            dependents.append(
                {
                    'type': type_name,
                    'name': rel_name,
                    'field': db_row['datname']
                }
            )

    def _temp_connection_check(self, rid, temp_conn, db_row, types,
                               dependents):
        if temp_conn.connected():
            query = render_template(
                "/".join([self.sql_path, 'dependents.sql']),
                fetch_dependents=True, rid=rid,
                lastsysoid=db_row['datlastsysoid']
            )

            status, result = temp_conn.execute_dict(query)
            if not status:
                current_app.logger.error(result)

            PasswordProfileView._handle_dependents_data(result, types, dependents, db_row)

    @staticmethod
    def _release_connection(is_connected, manager, db_row):
        # Release only those connections which we have created above.
        if not is_connected:
            manager.release(db_row['datname'])

    def get_dependents(self, conn, sid, rid):
        """
        This function is used to fetch the dependents for the selected node.

        Args:
            conn: Connection object
            sid: Server Id
            rid: Role Id.

        Returns: Dictionary of dependents for the selected node.
        """

        # Dictionary for the object types
        types = {
            # None specified special handling for this type
            'r': 'table',
            'i': None,
            'S': 'sequence',
            'v': 'view',
            'x': 'external_table',
            'p': 'function',
            'n': 'schema',
            'y': 'type',
            'd': 'domain',
            'T': 'trigger_function',
            'C': 'conversion',
            'o': None
        }

        query = render_template("/".join([self.sql_path, 'dependents.sql']),
                                fetch_database=True, rid=rid)
        status, db_result = self.conn.execute_dict(query)
        if not status:
            current_app.logger.error(db_result)

        dependents = list()

        # Get the server manager
        manager = get_driver(PG_DEFAULT_DRIVER).connection_manager(sid)

        for db_row in db_result['rows']:
            oid = db_row['datdba']
            if db_row['type'] == 'd':
                if rid == oid:
                    dependents.append(
                        {
                            'type': 'database',
                            'name': '',
                            'field': db_row['datname']
                        }
                    )
            else:
                dependents.append(
                    {
                        'type': 'tablespace',
                        'name': db_row['datname'],
                        'field': ''
                    }
                )

            # If connection to the database is not allowed then continue
            # with the next database
            if not db_row['datallowconn']:
                continue

            # Get the connection from the manager for the specified database.
            # Check the connect status and if it is not connected then create
            # a new connection to run the query and fetch the dependents.
            is_connected = True
            try:
                temp_conn = manager.connection(database=db_row['datname'])
                is_connected = temp_conn.connected()
                if not is_connected:
                    temp_conn.connect()
            except Exception as e:
                current_app.logger.exception(e)

            self._temp_connection_check(rid, temp_conn, db_row, types,
                                        dependents)
            PasswordProfileView._release_connection(is_connected, manager, db_row)

        return dependents

    @check_precondition()
    def variables(self, gid, sid, rid):

        status, rset = self.conn.execute_dict(
            render_template(self.sql_path + 'variables.sql',
                            rid=rid
                            )
        )

        if not status:
            return internal_server_error(
                _(
                    "Error retrieving variable information for the role.\n{0}"
                ).format(rset)
            )

        return make_json_response(
            data=rset['rows']
        )

    @check_precondition()
    def voptions(self, gid, sid):

        status, res = self.conn.execute_dict(
            """
SELECT
name, vartype, min_val, max_val, enumvals
FROM
(
SELECT
    'role'::text AS name, 'string'::text AS vartype,
    NULL AS min_val, NULL AS max_val, NULL::text[] AS enumvals
UNION ALL
SELECT
    name, vartype, min_val::numeric AS min_val, max_val::numeric AS max_val,
    enumvals
FROM
    pg_settings
WHERE
    context in ('user', 'superuser')
) a""")

        if not status:
            return internal_server_error(
                _(
                    "Error retrieving the variable options for the role.\n{0}"
                ).format(res)
            )
        return make_json_response(
            data=res['rows']
        )

    def _execute_role_reassign(self, conn, rid=None, data=None):

        """
        This function is used for executing reassign/drop
        query
        :param conn:
        :param rid:
        :param data:
        :return: status & result object
        """

        SQL = render_template(
            "/".join([self.sql_path, _REASSIGN_OWN_SQL]),
            rid=rid, data=data
        )
        status, res = conn.execute_scalar(SQL)

        if not status:
            return status, res

        return status, res

    @check_precondition()
    def get_reassign_own_sql(self, gid, sid, rid):

        """
        This function is used to generate sql for reassign/drop role.

        Args:
            sid: Server ID
            rid: Role Id.

        Returns: Json object with sql generate
        """

        try:

            data = dict()

            if request.data:
                data = json.loads(request.data, encoding='utf-8')
            else:
                rargs = request.args or request.form
                for k, v in rargs.items():
                    try:
                        data[k] = json.loads(v, encoding='utf-8')
                    except ValueError as ve:
                        data[k] = v

            required_args = ['role_op', 'did', 'old_role_name',
                             'new_role_name'] \
                if 'role_op' in data and data['role_op'] == 'reassign' \
                else ['role_op', 'did', 'drop_with_cascade']

            for arg in required_args:
                if arg not in data:
                    return make_json_response(
                        data=gettext("-- definition incomplete"),
                        status=200
                    )

            is_reassign = True if data['role_op'] == 'reassign' else False
            data['is_reassign'] = is_reassign

            sql = render_template(
                "/".join([self.sql_path, _REASSIGN_OWN_SQL]),
                data=data
            )

            return make_json_response(
                data=sql.strip('\n'),
                status=200
            )

        except Exception as e:
            return False, internal_server_error(errormsg=str(e))

    @check_precondition()
    def role_reassign_own(self, gid, sid, rid):

        """
        This function is used to reassign/drop role for the selected database.

        Args:
            sid: Server ID
            rid: Role Id.

        Returns: Json object with success/failure status
        """
        if request.data:
            data = json.loads(request.data, encoding='utf-8')
        else:
            data = request.args or request.form

        did = int(data['did'])
        is_already_connected = False
        can_disconn = True

        try:

            # Connect to the database where operation needs to carry out.
            from pgadmin.utils.driver import get_driver
            manager = get_driver(PG_DEFAULT_DRIVER).connection_manager(sid)
            conn = manager.connection(did=did, auto_reconnect=True)
            is_already_connected = conn.connected()

            pg_db = self.manager.db_info[self.manager.did]

            if did == pg_db['did']:
                can_disconn = False

            # if database is not connected, try connecting it and get
            # the connection object.
            if not is_already_connected:
                status, errmsg = conn.connect()
                if not status:
                    current_app.logger.error(
                        "Could not connect to database(#{0}).\nError: {1}"
                        .format(
                            did, errmsg
                        )
                    )
                    return internal_server_error(errmsg)
                else:
                    current_app.logger.info(
                        'Connection Established for Database Id: \
                        %s' % did
                    )

            status, old_role_name = self._execute_role_reassign(conn, rid)

            if not status:
                raise Exception(old_role_name)

            data['old_role_name'] = old_role_name

            is_reassign = True if data['role_op'] == 'reassign' else False
            data['is_reassign'] = is_reassign

            # check whether role operation is to reassign or drop
            if is_reassign \
                and (data['new_role_name'] == 'CURRENT_USER' or
                     data['new_role_name'] == 'SESSION_USER' or
                     data['new_role_name'] == 'CURRENT_ROLE') is False:

                status, new_role_name = \
                    self._execute_role_reassign(conn, data['new_role_id'])

                if not status:
                    raise Exception(new_role_name)

                data['new_role_name'] = new_role_name

            status, res = self._execute_role_reassign(conn, None, data)

            if not status:
                raise Exception(res)

            if is_already_connected is False and can_disconn:
                manager.release(did=did)

            return make_json_response(
                success=1,
                info=gettext("Reassign owned executed successfully!")
                if is_reassign
                else gettext("Drop owned executed successfully!")
            )

        except Exception as e:
            # Release Connection
            current_app.logger.exception(e)
            if is_already_connected is False and can_disconn:
                self.manager.release(did=did)

            return internal_server_error(errormsg=str(e))


PasswordProfileView.register_node_view(blueprint)
