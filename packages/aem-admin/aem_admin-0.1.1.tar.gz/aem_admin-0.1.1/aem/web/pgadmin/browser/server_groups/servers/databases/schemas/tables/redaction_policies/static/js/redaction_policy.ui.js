/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2022, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////

import gettext from 'sources/gettext';
import BaseUISchema from 'sources/SchemaView/base_schema.ui';

export default class RowSecurityPolicySchema extends BaseUISchema {
  constructor(fieldOptions = {}, initValues) {
    super({
      name: undefined,
      policyowner: 'public',
      event: 'ALL',
      using: undefined,
      using_orig: undefined,
      withcheck: undefined,
      withcheck_orig: undefined,
      type: 'PERMISSIVE',
      ...initValues,
    });

    this.fieldOptions = {
      role: [],
      function_names: [],
      ...fieldOptions,
    };

    this.nodeInfo = this.fieldOptions.nodeInfo;
  }

  get idAttribute() {
    return 'oid';
  }

  disableUsingField(state) {
    if (state.event == 'INSERT') {
      return true;
    }
    return false;
  }

  disableWithCheckField(state) {
    var event = state.event;
    if (event == 'SELECT' || event == 'DELETE') {
      state.withcheck = '';
      return true;
    }
    return false;
  }

  get baseFields() {
    let obj = this;
    return [
      {
        group: gettext('General'),
        id: 'oid',
        label: gettext('ID'),
        cell: 'string',
        editable: false,
        type: 'text',
        mode: ['properties'],
      },
      {
        group: gettext('General'),
        id: 'name',
        label: gettext('Name'),
        cell: 'text',
        editable: true,
        type: 'text',
        readonly: true,
        noEmpty: true,
      },      
      {
        group: gettext('General'),
        id: 'rdenable',
        label: gettext('Redaction Enable'),
        cell: 'string',
        editable: false,
        type: 'switch',
        readonly: true,
        mode: ['properties', 'edit'],
      },
      {
        group: gettext('General'),
        id: 'rdexpr',
        label: gettext('Redaction policy expression'),
        cell: 'string',
        editable: false,
        type: 'text',
        readonly: true,
        mode: ['properties', 'edit'],
      },
      {
        group: gettext('General'),
        id: 'rdrelid',
        label: gettext('Redaction relation table'),
        editable: false,
        type: 'select',
        readonly: true,
        options: obj.fieldOptions.getDatabases,
        mode: ['properties', 'edit'],
      },
    ];
  }
}
