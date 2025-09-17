##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2022, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

from flask import render_template, request, jsonify, current_app
from flask_babel import gettext as _
from pgadmin.utils.ajax import make_json_response, \
    internal_server_error, bad_request, precondition_required
from pgadmin.utils.constants import ERROR_FETCHING_ROLE_INFORMATION, \
    ERROR_FETCHING_PROFILE_INFORMATION


def update_verify_function_process(sql_path, conn, request):

    r = request  # 항상 전달됨
    name = 'prfname'
    em = 'editMode'  # 항상 전달됨
    fc = 'prfpasswordverifyfunc'
    sc = 'prfpasswordverifyfuncschema'
    db = 'prfpasswordverifyfuncdb'
    sql = 'prfpasswordverifyfuncsql'
    ppid = r['oid']  # 항상 전달됨
    old_pp = PP(get_profile(conn, ppid))

    r_prfname = r.get(name) if bool(r.get(name)) else old_pp.prfname
    r_db = r.get(db) if bool(r.get(db)) else old_pp.prfpasswordverifyfuncdb
    r_fc = r.get(fc) if bool(r.get(fc)) else old_pp.prfpasswordverifyfunc
    r_sc = r.get(sc) if bool(r.get(sc)) else extract_func_schema_oid_by_funcoid(conn, r_fc)
    r_sql = r.get(sql) if bool(r.get(sql)) else None
    funcname = extract_funcname_by_oid(conn, r_sc, r_fc)

    errmsg = None
    try:
        if em not in r:
            # no action, return.
            return
        elif em in r:
            if r[em] == 'load':
                errmsg = load_branch_of_update_verify_function_process(request, conn,
                                                              r_prfname, funcname)
                return errmsg
            elif r[em] == 'new':
                errmsg = new_branch_of_update_verify_function_process(request, conn,
                                                              r_prfname, funcname)
                return errmsg
            elif r[em] == 'edit':
                errmsg = edit_branch_of_update_verify_function_process(request, conn,
                                                              r_prfname, funcname)
                return errmsg
            return
        return errmsg
    except IndexError as ie:
        raise ie

def load_branch_of_update_verify_function_process(r, conn, r_prfname, funcname):

    sql = 'prfpasswordverifyfuncsql'

    if sql not in r:
        return
    if r[sql] == "--Sciprt Load Error":
        cutoff_verification_function(conn, r_prfname)
    elif r[sql] != "--Sciprt Load Error":
        alter_profile_func(conn, r_prfname, funcname)
    else:
        return

def new_branch_of_update_verify_function_process(r, conn, r_prfname, funcname):

    sql = 'prfpasswordverifyfuncsql'
    rset = None

    try:
        r_sql = r.get(sql) if bool(r.get(sql)) else None
        if sql not in r:
            cutoff_verification_function(conn, r_prfname)
            return
        if r[sql] == "CREATE OR REPLACE FUNCTION":
            cutoff_verification_function(conn, r_prfname)
        elif r[sql] != "CREATE OR REPLACE FUNCTION":

            rset = create_or_update_func(conn, r_sql)

            if rset is not None:
                return rset  # 에러 메세지를 리턴

            funcname = extract_funcname_by_sql(r_sql)
            alter_profile_func(conn, r_prfname, funcname)
        else:
            return
    except IndexError as ie:
        raise ie

def edit_branch_of_update_verify_function_process(r, conn, r_prfname, funcname):

    sql = 'prfpasswordverifyfuncsql'
    rset = None

    try:
        r_sql = r.get(sql) if bool(r.get(sql)) else None

        if sql not in r:
            cutoff_verification_function(conn, r_prfname)
            return
        if r[sql] == "--Sciprt Load Error":
            cutoff_verification_function(conn, r_prfname)
        elif r[sql] != "--Sciprt Load Error":
            rset = create_or_update_func(conn, r_sql)

            if rset is not None:
                return rset  # 에러 메세지를 리턴

            funcname = extract_funcname_by_sql(r_sql)
            alter_profile_func(conn, r_prfname, funcname)
        else:
            return
    except IndexError as ie:
        raise ie



def verify_function_process(conn, request):

    r = request
    editMode = request['editMode']

    prfname = request['prfname']
    func_oid = request['prfpasswordverifyfunc']
    func_sql = request['prfpasswordverifyfuncsql']
    func_schema_oid = request['prfpasswordverifyfuncschema']
    func_db_oid = request['prfpasswordverifyfuncdb']
    _funcname = None

    if editMode == "load":
        _funcname = extract_funcname_by_oid(conn, func_schema_oid, func_oid)
    elif editMode == "edit":
        conn.execute_void(func_sql)
        _funcname = extract_funcname_by_sql(func_sql)
    elif editMode == "new":
        conn.execute_void(func_sql)
        _funcname = extract_funcname_by_sql(func_sql)
    elif not 'editMode' in request:
        return internal_server_error(
            _("Could not parse editMode\n")
        )
    else:
        pass
    alter_profile_func(conn, prfname, _funcname)

################################################

def default_or_unmlimited_transfromer(sql_path, conn, source):
        sql = render_template(sql_path + 'default_or_unmlimited_transfromer.sql',
                                      data=source,
                                      dummy=False,
                                      conn=conn)
        status, result = conn.execute_dict(sql)

        if not status:
            return internal_server_error(
                _("Could not execute interval converting.\n{0}").format(result)
            )

        return (result['rows'])[0]

def prfassociation_transform(self, rset):
    for row in rset['rows']:
        res = []

        row['prfassociation'] = row['prfassociation'].replace('{', '').replace('}', '')
        assoarray = row['prfassociation'].split(',')
        for asso in assoarray:
            if asso != '':
                res.append(asso)
        row['prfassociation'] = res

def cutoff_verification_function(conn, prfname):

    status, rset = conn.execute_void(
        "ALTER PROFILE {0} LIMIT password_verify_function NULL;".format(prfname))

    if not status:
        return internal_server_error(
            _("Could not alter profile verification function.\n{0}").format(
                rset)
        )

def create_or_update_func(conn, sql):

    status, rset = conn.execute_void(sql)
    if not status:
        return rset

def create_func(conn, sql):

    status, rset = conn.execute_void(sql)
    if not status:
        return rset

def alter_profile_func(conn, prf_name, func_name):
    sql = 'ALTER PROFILE {0} LIMIT PASSWORD_VERIFY_FUNCTION {1};'
    if func_name is None:
        sql = 'ALTER PROFILE {0} LIMIT PASSWORD_VERIFY_FUNCTION NULL;'
    status, rset = conn.execute_dict(sql.format(prf_name, func_name))

    if not status:
        return internal_server_error(
            _("Could not alter profile verification function.\n{0}").format(
                rset)
        )

def get_profile(conn, ppid):

    p = __execute_dict_with_sql(conn,
                            sql='select * from ag_profile '
                                'where oid=' + str(ppid) + '::oid;')

    return p

def unepoching(sql_path, conn, intervalData):
    """
    interval 형태로 표현된 시간을 day,hour,minutes로 분리한 dict 리턴.
    """
    status, rset = conn.execute_dict(
        render_template(sql_path + 'unepoch.sql',
                        data=intervalData,
                        dummy=False,
                        conn=conn)
    )

    if not status:
        return internal_server_error(
            _("Could not unepoch timedata.\n{0}").format(rset)
        )

    unepoched_row_data = (rset['rows'])[0]

    return unepoched_row_data

def epoching(sql_path, conn, dayHourMinData):
    """
    day, hour, minutes로 표현된 시간을 interval 형태로 병합한 dict 리턴.
    """

    status, rset = conn.execute_dict(
        render_template(
            sql_path + 'epoch.sql',
            data=dayHourMinData,
            dummy=False,
            conn=conn
        )
    )

    if not status:
        return internal_server_error(
            _("Could not epoch timedata.\n{0}").format(rset)
        )

    epoched_row_data = (rset['rows'])[0]

    return epoched_row_data

def __execute_dict_with_sql(conn, sql):

    status, result = conn.execute_dict(sql)

    if not status:
        return internal_server_error(
            _("Could not execute sql .\n{0} \n result : {1}")
                .format(sql, result)
        )

    ret = result['rows'][0]
    return ret

class PP:
    """
    wrapper class of password profile's database row
    """

    def __init__(self, row_dict):
        self.oid = None
        self.prfname = None
        self.prffailedloginattempts = None
        self.prfpasswordlocktime = None
        self.prfpasswordlifetime = None
        self.prfpasswordgracetime = None
        self.prfpasswordreusetime = None
        self.prfpasswordreusemax = None
        self.prfpasswordverifyfuncdb = None
        self.prfpasswordverifyfunc = None

        self.update(row_dict)

    def update(self, row_dict):
        for key in row_dict:
            self.__dict__[key] = row_dict.get(key, None)

#extract

def extract_funcname_by_oid(conn, funcsc_oid, func_oid):

    sql = """
    SELECT proname
        from pg_catalog.pg_namespace as ns
            left join pg_catalog.pg_proc as pr on ns.oid = pr.pronamespace
    where ns.oid = {0}::oid
        and pr.oid = {1}::oid;
    """

    if funcsc_oid is not None and func_oid is not None:
        status, funcname = conn.execute_scalar(
            sql.format(int(funcsc_oid), int(func_oid)))

        if not status:
            return internal_server_error(
                _("Could not retrieve function info.\n{0}").format(funcname)
            )
        return funcname

    else:
        pass

def extract_oid_by_prfname(conn, prfname):

    status, ppid = conn.execute_scalar(
        "SELECT oid FROM ag_profile WHERE prfname = %(prfname)s",
        {'prfname': prfname}
    )

    if status:
        return ppid
    else:
        return internal_server_error(
            _(ERROR_FETCHING_PROFILE_INFORMATION + "\n{0}").format(status))

def extract_func_schema_oid_by_funcoid(conn, func_oid):

    status, funcsc_oid = conn.execute_scalar(
        """
        SELECT ns.oid
        from pg_catalog.pg_namespace as ns
            left join pg_catalog.pg_proc as pr on ns.oid = pr.pronamespace
        where pr.oid = {0}::oid;
        """.format(func_oid)
    )

    if status:
        return funcsc_oid
    else:
        return internal_server_error(
            _(ERROR_FETCHING_PROFILE_INFORMATION + "\n{0}").format(status))

def extract_funcname_by_sql(sql):

    try:
        if ('-- FUNCTION:' in sql) or ('-- DROP FUNCTION' in sql):
            sql = sql.split('CREATE')[1]
        funcname = (sql.split('FUNCTION')[1].split('(')[0]).strip()
        return funcname if '.' not in funcname else funcname.split('.')[1]
    except IndexError as ie:
        raise ie

#update
def update_profile_interval(sql_path, conn, request, ppid):
    old_profile_row = get_profile(conn, ppid)
    # 이전 프로필 db조회값의 시간정보값 형변환 ( 3660 -> 1 hours, 1 minutes )
    unepoched_old_profile_dict = unepoching(sql_path, conn, old_profile_row)

    # 이전의 프로필 테이블값에서 DEFAULT, UNLIMITED 값을 dict key값으로 치환
    transform_result = default_or_unmlimited_transfromer(sql_path, conn,
                                                         old_profile_row)
    # 키값 추가결과하여  업데이트
    unepoched_old_profile_dict.update(transform_result)

    # 리퀘스트로 전달된 시간정보값만 덮어쓰기 ( 1 hours -> 1 days 12 hours )
    unepoched_old_profile_dict.update(request)

    # 리퀘스트로 전달 수치까지 반영하여 프로필 입력형태(interval)로 조정 (1 days 12 hours -> 1.5)
    epoched_updated_profile_dict = epoching(sql_path, conn,
                                            unepoched_old_profile_dict)

    # sql 입력형태로 조정하여 dict update
    unepoched_old_profile_dict.update(epoched_updated_profile_dict)

    # 바뀐 이름을 대상으로하여 프로필 속성값들 변경
    sql = render_template(
        sql_path + 'update.sql',
        data=unepoched_old_profile_dict,
        requestParam=request,
        olddata=old_profile_row,
        dummy=False,
        conn=conn
    )

    if sql.isspace():
        pass
    else:
        status, msg = conn.execute_dict(sql)
        if not status:
            return internal_server_error(
                _("Could not update the profile.\n{0}").format(msg)
            )

    return unepoched_old_profile_dict

def update_profile_assiciation(sql_path, old_profile : PP, conn, request, is_msql_calling : bool):

    r = request

    if 'prfassociation' in r:
        if 'prfname' not in r:
            r['prfname'] = old_profile.prfname

        association_length = len(r['prfassociation'])

        alter_role_sql = render_template(
            sql_path + 'update_associate.sql',
            data=r,
            dummy=False,
            conn=conn,
            association_length=association_length
        )

        if (is_msql_calling):
            return alter_role_sql
        status, msg = conn.execute_void(alter_role_sql)

        if not status:
            return internal_server_error(
                _("Could not create the profile.\n{0}").format(msg)
            )

def profile_funcdb_connection_assigner(manager, pp: PP, did=None):
    funcdb_oid=None

    if did is not None:
        return manager.connection(did=did)
    
    if pp is not None:
        funcdb_oid = pp.prfpasswordverifyfuncdb

    if funcdb_oid is None:
        return manager.connection()  # return default connection
    else:
        return manager.connection(did=funcdb_oid)




def msql_epoching_for_update(sql_path, conn, request):
    ppid = int(request['oid'])

    old_profile_row = get_profile(conn, ppid)

    # 이전 프로필 db조회값의 시간정보값 형변환 ( 3660 -> 1 hours, 1 minutes )
    unepoched_old_profile_dict = unepoching(sql_path, conn, old_profile_row)

    # 이전의 프로필 테이블값에서 DEFAULT, UNLIMITED 값을 dict key값으로 치환
    transform_result = default_or_unmlimited_transfromer(sql_path, conn, old_profile_row)
    # 키값 추가결과하여  업데이트
    unepoched_old_profile_dict.update(transform_result)

    # 리퀘스트로 전달된 시간정보값만 덮어쓰기 ( 1 hours -> 1 days 12 hours )
    unepoched_old_profile_dict.update(request)

    # 리퀘스트로 전달 수치까지 반영하여 프로필 입력형태(interval)로 조정 (1 days 12 hours -> 1.5)
    epoched_updated_profile_dict = epoching(sql_path, conn, unepoched_old_profile_dict)

    # sql 입력형태로 조정하여 dict update
    unepoched_old_profile_dict.update(epoched_updated_profile_dict)

    # 바뀐 이름을 대상으로하여 프로필 속성값들 변경
    sql = render_template(
        sql_path + 'msql_update.sql',
        data=unepoched_old_profile_dict,
        requestParam=request,
        olddata=old_profile_row,
        dummy=False,
        conn=conn
    )
    # print('profile data incoming', unepoched_old_profile_dict)
    # print('request params', request)
    # print('old data', old_profile_row)
    return sql


def msql_epoching_for_create(sql_path, conn, request):
    r = request

    epoched_sql = render_template(
        sql_path + 'msql_create.sql',
        data=r,
        dummy=True,
        conn=conn)

    return epoched_sql

def msql_association(sql_path, conn, request, profile_name):
    print('profile data', profile_name)

    r = request

    if 'prfassociation' in r and len(str(r['prfassociation'])) > 2:

        asso_list = (r['prfassociation']).lstrip('[').rstrip(']').split(',')
        asso_dict = dict()
        asso_dict['prfassociation'] = asso_list
        r.update(asso_dict)

        asso_sql = render_template(
            sql_path + 'msql_create_associate.sql',
            data=r['prfassociation'],
            prfname=profile_name,
            dummy=True,
            conn=conn)

        return '\n -- associating roles with profile. \n ' + asso_sql
    else:
        return ''

def msql_verifyfunction_for_create(request):
    r = request
    pn = 'prfname'
    em = 'editMode'
    fc = 'prfpasswordverifyfunc'
    sc = 'prfpasswordverifyfuncschema'
    db = 'prfpasswordverifyfuncdb'
    sql = 'prfpasswordverifyfuncsql'
    createfunc_sql = ''

    if em in r:
        if not (db in r and sc in r and fc in r):
            return ''
        if r[em] == 'load' and db in r and sc in r and fc in r:
            funcname = extract_funcname_by_sql(r[sql])
        elif r[em] == 'new' and db in r and sc in r and sql in r:
            funcname = extract_funcname_by_sql(r[sql])
            createfunc_sql = msql_create_or_replace_func(r[sql])
        elif r[em] == 'edit' and db in r and sc in r and sql in r:
            funcname = extract_funcname_by_sql(r[sql])
            createfunc_sql = msql_create_or_replace_func(r[sql])
        else:
            funcname = 'NULL'
        assignfunc_sql = msql_assigning_verify_func(r[pn], funcname)
        return createfunc_sql + assignfunc_sql
    else:
        return ''

def msql_verifyfunction_for_update(connection, request):
    r = request
    c = connection
    em = 'editMode'
    fc = 'prfpasswordverifyfunc'
    sc = 'prfpasswordverifyfuncschema'
    db = 'prfpasswordverifyfuncdb'
    sql = 'prfpasswordverifyfuncsql'
    createfunc_sql = ''
    ppid = request.get('oid')
    old_pp = PP(get_profile(c, ppid))

    r_db = r.get(db) if bool(r.get(db)) else old_pp.prfpasswordverifyfuncdb
    r_fc = r.get(fc) if bool(r.get(fc)) else old_pp.prfpasswordverifyfunc
    r_sc = r.get(sc) if bool(r.get(sc)) else extract_func_schema_oid_by_funcoid(c, r_fc)
    r_sql = r.get(sql) if bool(r.get(sql)) else None

    if 'prfname' in request:
        prfname = request.get('prfname')
    else:
        prfname = old_pp.prfname

    # 키O,값O     ### create, update   ### bool(r.get(db)) == true
    # 키O,값X('') ### drop action     ### db in r && bool(r.get(db)) == false
    # 키X,값X     ### no action       ### db not in r
    # 수정하기 이전과 같은 값인 경우에는 키+값이 넘어오지 않음

    if em in r:
        if not (db in r) and not (sc in r) and not (fc in r) and not (sql in r):
            return ''
        elif r[em] == 'load':
            if (db in r) and not bool(r.get(db)) or (sc in r) and not bool(r.get(sc)) or (fc in r) and not bool(r.get(fc)):
                funcname = 'NULL'
            elif (db in r) and bool(r.get(db)) or (sc in r) and bool(r.get(sc)) or (fc in r) and bool(r.get(fc)):
                funcname = extract_funcname_by_sql(r[sql])
            else:
                funcname = 'NULL'
        elif r[em] == 'new':
            if (db in r) and not bool(r.get(db)) or (sc in r) and not bool(r.get(sc)) :
                funcname = 'NULL'
            elif (db in r) and bool(r.get(db)) or (sc in r) and bool(r.get(sc)) or (sql in r) and bool(r.get(sql)):
                if r[sql] == 'CREATE OR REPLACE FUNCTION':
                    return ''
                elif r[sql] == '':
                    funcname = 'NULL'
                else:
                    funcname = extract_funcname_by_sql(r[sql])
                    createfunc_sql = msql_create_or_replace_func(r[sql])
            else:
                funcname = 'NULL'
        elif r[em] == 'edit':
            if (db in r) and not bool(r.get(db)) or (sc in r) and not bool(r.get(sc)):
                funcname = 'NULL'
            elif (db in r) and bool(r.get(db)) or (sc in r) and bool(r.get(sc)) or (sql in r) and bool(r.get(sql)):
                if r[sql] == 'CREATE OR REPLACE FUNCTION':
                    return ''
                elif r_sql == '--Sciprt Load Error' or (r[sql] == ''):
                    funcname = 'NULL'
                else:
                    funcname = extract_funcname_by_sql(r[sql])
                    createfunc_sql = msql_create_or_replace_func(r[sql])
            else:
                funcname = 'NULL'
        else:
            funcname = 'NULL'
        assignfunc_sql = msql_assigning_verify_func(prfname, funcname)
        return createfunc_sql + assignfunc_sql
    else:
        return ''

def msql_assigning_verify_func(prfname, funcname):
    if prfname != '' and funcname != '':
        assigning_func_sql = '\n -- assigning verification function to profile. ' \
                             '\n ALTER PROFILE {0} LIMIT PASSWORD_VERIFY_FUNCTION {1};'\
            .format(prfname, funcname)
        return assigning_func_sql
    else:
        return ''

def msql_create_or_replace_func(sql):
    create_or_replace_func_sql = ''
    if sql != '':
        create_or_replace_func_sql = '\n -- create or replace function to assigning profile. ' \
                                     '\n{0}\n'.format(sql)
    return create_or_replace_func_sql

#not in use
def extract_rolname_by_prf_oid(profile_oid,conn):
    sql = 'select rolname from pg_authid where rolprofile={0}::oid'
    status, rolname = conn.execute_dict(sql.format(int(profile_oid)))

    if not status:
        return internal_server_error(
            _("Could not retrieve function info.\n{0}").format(rolname)
        )

    return rolname['rows']