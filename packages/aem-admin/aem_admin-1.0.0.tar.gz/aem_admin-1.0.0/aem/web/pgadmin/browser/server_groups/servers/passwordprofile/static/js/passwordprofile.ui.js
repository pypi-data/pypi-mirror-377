/////////////////////////////////////////////////////////////
//
// AEM
//
// AgensSQL, AgensGraph, AGE tool
//
//////////////////////////////////////////////////////////////

import gettext from 'sources/gettext';
import BaseUISchema from 'sources/SchemaView/base_schema.ui';

export class LifeTimeSchema extends BaseUISchema {
  constructor(prefix) {
    super();
    this.prefix = prefix;
  }

  get baseFields() {
    return [
      {
        id: `_${this.prefix}_default`,
        type: 'switch',
        label: gettext('Default'),
        controlLabelClassName: 'control-label pg-el-sm-4 pg-el-12',
        controlsClassName: 'pgadmin-controls pg-el-sm-8 pg-el-12',
      },
      {
        id: `_${this.prefix}_unlimited`,
        type: 'switch',
        label: gettext('Unlimited'),
        controlLabelClassName: 'control-label pg-el-sm-4 pg-el-12',
        controlsClassName: 'pgadmin-controls pg-el-sm-8 pg-el-12',
        visible: function (state) {
          return !state[`_${this.prefix}_default`];
        },
      },
      {
        id: `_${this.prefix}_day`,
        type: 'int',
        label: gettext('Day'),
        cell: 'integer',
        min: 0,
        disabled: function (state) {
          return (
            state[`_${this.prefix}_default`] ||
            state[`_${this.prefix}_unlimited`]
          );
        },
        visible: function (state) {
          return !state[`_${this.prefix}_default`];
        },
      },
      {
        id: `_${this.prefix}_hour`,
        type: 'int',
        label: gettext('Hour'),
        cell: 'integer',
        min: 0,
        max: 23,
        disabled: function (state) {
          return (
            state[`_${this.prefix}_default`] ||
            state[`_${this.prefix}_unlimited`]
          );
        },
        visible: function (state) {
          return !state[`_${this.prefix}_default`];
        },
      },
      {
        id: `_${this.prefix}_minute`,
        type: 'int',
        label: gettext('Minute'),
        cell: 'integer',
        min: 0,
        max: 59,
        disabled: function (state) {
          return (
            state[`_${this.prefix}_default`] ||
            state[`_${this.prefix}_unlimited`]
          );
        },
        visible: function (state) {
          return !state[`_${this.prefix}_default`];
        },
      },
    ];
  }
}

export class LimitSchema extends BaseUISchema {
  constructor(id, label) {
    super();
    this.prefix = id;
    this.id = id;
    this.label = label;
  }

  get baseFields() {
    return [
      {
        id: `_${this.prefix}_default`,
        type: 'switch',
        label: gettext('Default'),
        controlLabelClassName: 'control-label pg-el-sm-4 pg-el-12',
        controlsClassName: 'pgadmin-controls pg-el-sm-8 pg-el-12',
      },
      {
        id: `_${this.prefix}_unlimited`,
        type: 'switch',
        label: gettext('Unlimited'),
        controlLabelClassName: 'control-label pg-el-sm-4 pg-el-12',
        controlsClassName: 'pgadmin-controls pg-el-sm-8 pg-el-12',
        disabled: function (state) {
          return state[`_${this.prefix}_default`];
        },
        visible: function (state) {
          return !state[`_${this.prefix}_default`];
        },
      },
      {
        id: `${this.prefix}`,
        type: 'int',
        label: gettext(this.label),
        cell: 'integer',
        min: 1,
        disabled: function (state) {
          return state[`_${this.prefix}_unlimited`];
        },
        visible: function (state) {
          return !state[`_${this.prefix}_default`];
        },
      },
    ];
  }
}

export class RoleAndUserSchema extends BaseUISchema {
  constructor(roles) {
    super();
    this.roles = roles;
  }

  get baseFields() {
    return [
      {
        id: 'role',
        label: gettext('User/Role'),
        type: 'text',
        editable: true,
        cell: () => ({
          cell: 'select',
          options: this.roles,
          controlProps: {
            allowClear: false,
          },
        }),
        noEmpty: true,
        minWidth: 300,
      },
    ];
  }
}

export default class PasswordProfileSchema extends BaseUISchema {
  constructor(fieldOptions = {}) {
    super({
      // General
      oid: null,
      prfname: null,
      // Login attempt failed
      prffailedloginattempts: null,
      _prffailedloginattempts_default: true,
      _prffailedloginattempts_unlimited: false,
      // password lock time
      _prfpasswordlocktime_default: true,
      _prfpasswordlocktime_unlimited: false,
      _prfpasswordlocktime_day: null,
      _prfpasswordlocktime_hour: null,
      _prfpasswordlocktime_minute: null,
      // password life time
      _prfpasswordlifetime_default: true,
      _prfpasswordlifetime_unlimited: false,
      _prfpasswordlifetime_day: null,
      _prfpasswordlifetime_hour: null,
      _prfpasswordlifetime_minute: null,
      // password grace time
      _prfpasswordgracetime_default: true,
      _prfpasswordgracetime_unlimited: false,
      _prfpasswordgracetime_day: null,
      _prfpasswordgracetime_hour: null,
      _prfpasswordgracetime_minute: null,
      // password reuse time
      _prfpasswordreusetime_default: true,
      _prfpasswordreusetime_unlimited: false,
      _prfpasswordreusetime_day: null,
      _prfpasswordreusetime_hour: null,
      _prfpasswordreusetime_minute: null,
      // password reuse max
      prfpasswordreusemax: null,
      _prfpasswordreusemax_default: true,
      _prfpasswordreusemax_unlimited: false,
      // Password Verify Function
      prfpasswordverifyfuncdb: null,
      prfpasswordverifyfuncschema: null,
      prfpasswordverifyfunc: null,
      prfpasswordverifyfuncsql: null,
      // Associations
      prfassociation: [],
      // etc
      editMode: 'load',
    });
    this.fieldOptions = {
      role: [],
      ...fieldOptions,
    };
    this.isReadOnly = null;
    this.nodeInfo = this.fieldOptions.nodeInfo;
    this.user = this.nodeInfo.server.user;
  }

  get idAttribute() {
    return 'oid';
  }

  readOnly(state) {
    var user = this.nodeInfo.server.user;
    this.oid = state.oid;
    this.isReadOnly = !(user.is_superuser || user.can_create_role);
    return !(user.is_superuser || user.can_create_role) && user.id != state.oid;
  }

  memberDataFormatter(rawData) {
    var members = '';
    if (_.isObject(rawData)) {
      var withAdmin = '';
      rawData.forEach((member) => {
        if (member.admin) {
          withAdmin = ' [WITH ADMIN]';
        }

        if (members.length > 0) {
          members += ', ';
        }
        members = members + (member.role + withAdmin);
      });
    }
    return members;
  }

  get baseFields() {
    let obj = this;
    return [
      // General
      {
        id: 'oid',
        label: gettext('ID'),
        cell: 'string',
        mode: ['properties'],
        editable: false,
        type: 'text',
        visible: true,
      },
      // password profile name 
      {
        id: 'prfname',
        label: gettext('Name'),
        type: 'text',
        noEmpty: true,
        disabled: obj.readOnly,
      },
      // Definition
      {
        type: 'nested-fieldset',
        label: gettext('Login Attempts'),
        group: gettext('Definition'),
        schema: new LimitSchema(
          'prffailedloginattempts',
          'Attempt failed limit'
        ),
      },
      // password lock time 
      {
        type: 'nested-fieldset',
        label: gettext('Password Lock Time'),
        group: gettext('Definition'),
        schema: new LifeTimeSchema('prfpasswordlocktime'),
      },
      // password life time 
      {
        type: 'nested-fieldset',
        label: gettext('Password Life Time'),
        group: gettext('Definition'),
        schema: new LifeTimeSchema('prfpasswordlifetime'),
      },
      // password Grace time 
      {
        type: 'nested-fieldset',
        label: gettext('Password Grace Time'),
        group: gettext('Definition'),
        schema: new LifeTimeSchema('prfpasswordgracetime'),
      },
      // password Reuse time 
      {
        type: 'nested-fieldset',
        label: gettext('Password Reuse Time'),
        group: gettext('Definition'),
        schema: new LifeTimeSchema('prfpasswordreusetime'),
      },
      // password Reuse Max
      {
        type: 'nested-fieldset',
        label: gettext('Password Reuse Max'),
        group: gettext('Definition'),
        schema: new LimitSchema('prfpasswordreusemax', 'Reuse Max'),
      },
      // Password Verify Function
      {
        id: 'editMode',
        label: gettext('Mode'),
        type: (state) => {
          return {
            type: 'toggle',
            value: state.editMode ?? false,
          };
        },
        options: [
          { label: gettext('load'), value: 'load' },
          { label: gettext('new'), value: 'new' },
          { label: gettext('edit'), value: 'edit' },
        ],
        group: gettext('Password Verify Function'),
        mode: ['create', 'edit'],
      },
      {
        id: 'prfpasswordverifyfuncdb',
        type: 'select',  // ✅ must be static string
        group: gettext('Password Verify Function'),
        label: gettext('Select Database...'),
        cell: 'text',
        editable: false,
        options: () => {
          return this.fieldOptions.getConnectionDatabaseList()
            .then((data) => {
              console.warn('database data fetched here:', data);
              return data;
            });
        },
        controlProps: { allowClear: true },
        disabled: (state) => !state.editMode,
      },
      {
        id: 'prfpasswordverifyfuncschema',
        type: (state) => {
          let fetchOptionsBasis = state.prfpasswordverifyfuncdb;
          return {
            type: 'select',
            options: obj.fieldOptions.getSchemaOption(
              state.prfpasswordverifyfuncdb
            ),
            optionsReloadBasis: fetchOptionsBasis,
          };
        },
        group: gettext('Password Verify Function'),
        label: gettext('Select Schema...'),
        cell: 'text',
        editable: false,
        deps: ['prfpasswordverifyfuncdb'],
        controlProps: { allowClear: true },
        disabled: (state) => {
          return !state.editMode;
        },
      },
      {
        id: 'prfpasswordverifyfunc',
        type: (state) => {
          let fetchOptionsBasis =
            state.prfpasswordverifyfuncdb + state.prfpasswordverifyfuncschema;
          return {
            type: 'select',
            options: obj.fieldOptions.getFunctionOption(
              state.prfpasswordverifyfuncdb,
              state.prfpasswordverifyfuncschema
            ),
            optionsReloadBasis: fetchOptionsBasis,
          };
        },
        group: gettext('Password Verify Function'),
        label: gettext('Select function...'),
        cell: 'text',
        editable: false,
        deps: ['prfpasswordverifyfuncdb', 'prfpasswordverifyfuncschema'],
        controlProps: { allowClear: true },
        disabled: function (state) {
          return state.editMode === 'new' || !state.editMode;
        },
      },
      {
        id: 'prfpasswordverifyfuncsql',
        type: 'sql',
        group: gettext('Password Verify Function'),
        label: gettext('Script PL/SQL'),
        cell: 'string',
        deps: [
          'editMode',
          'prfpasswordverifyfuncdb',
          'prfpasswordverifyfuncschema',
          'prfpasswordverifyfunc',
        ],
        controlProps: { className: ['custom_height_css_class'] },
        readonly: (state) => state.editMode === 'load',
        disabled: (state) => !state.editMode,
        getValue: (state) => {
          console.warn('[DEBUG] getValue state:', state);

          if (state.editMode === 'new') {
            return Promise.resolve('CREATE OR REPLACE FUNCTION');
          }

          if (state.prfpasswordverifyfuncdb &&
              state.prfpasswordverifyfuncschema &&
              state.prfpasswordverifyfunc) {
            return obj.fieldOptions.getFunctionSql(
              state.prfpasswordverifyfuncdb,
              state.prfpasswordverifyfuncschema,
              state.prfpasswordverifyfunc
            ).then(sql => {
              console.warn('[DEBUG] SQL fetched:', sql);
              return sql;
            });
          }

          return Promise.resolve('--Script Load Error (missing params)');
        },
      },
      // Associations
      {
        id: 'prfassociation',
        label: gettext('Associate User/Role'),
        group: gettext('Associations'),
        disabled: obj.readOnly,
        mode: ['edit', 'create', 'properties'],
        cell: 'text',
        type: 'select',
        options: [],
        controlProps: {
          multiple: true,
        },
      },
    ];
  }
}
