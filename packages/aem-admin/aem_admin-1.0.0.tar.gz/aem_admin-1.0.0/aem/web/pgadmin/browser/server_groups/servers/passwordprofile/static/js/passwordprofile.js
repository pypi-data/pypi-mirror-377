/////////////////////////////////////////////////////////////
//
// AEM
//
// AgensSQL, AgensGraph, AGE tool
//
//////////////////////////////////////////////////////////////

import PasswordProfileSchema from './passwordprofile.ui';
import getApiInstance from '../../../../../../static/js/api_instance';
import {
// getNodeListByName,
// getNodeIdListByName,
} from '../../../../../static/js/node_ajax';

define('pgadmin.node.password_profile', [
  'sources/gettext',
  'sources/url_for',
  'sources/pgadmin',
  'pgadmin.browser',
], function (gettext, _, pgAdmin, pgBrowser) {
  if (!pgBrowser.Nodes['coll-password_profile']) {
    pgAdmin.Browser.Nodes['coll-password_profile'] =
      pgAdmin.Browser.Collection.extend({
        node: 'password_profile',
        label: gettext('Password Profile'),
        type: 'coll-password_profile',
        columns: ['oid', 'prfname'],
        canDrop: true,
        canDropCascade: false,
      });
  }

  if (!pgBrowser.Nodes['password_profile']) {
    pgAdmin.Browser.Nodes['password_profile'] = pgAdmin.Browser.Node.extend({
      parent_type: 'server',
      type: 'password_profile',
      // sqlAlterHelp: 'sql-alterrole.html',
      // sqlCreateHelp: 'sql-createrole.html',
      // dialogHelp: url_for('help.static', {'filename': 'role_dialog.html'}),
      label: gettext('Password Profile'),
      hasSQL: true,
      width: '550px',
      canDrop: true,
      hasDepends: true,
      node_label: function (r) {
        return r.label;
      },
      node_image: function (r) {
        if (!r) return 'icon-role';
        return r.can_login ? 'icon-role' : 'icon-group';
      },
      title: function (d) {
        if (d) {
          return `Password Profile - ${d._label}`;
        }
      },
      Init: function () {
        /* Avoid mulitple registration of menus */
        if (this.initialized) return;

        this.initialized = true;

        pgBrowser.add_menus([
          {
            name: 'create_password_profile_on_server',
            node: 'server',
            module: this,
            applies: ['context', 'object'],
            callback: 'show_obj_properties',
            category: 'create',
            priority: 5,
            label: gettext('Password Profile...'),
            data: { action: 'create' },
            enable: 'can_create_password_profile',
          },
          {
            name: 'create_password_profile_profiles',
            node: 'coll-password_profile',
            module: this,
            applies: ['context'],
            callback: 'show_obj_properties',
            category: 'create',
            priority: 4,
            label: gettext('Create Password Profile...'),
            data: { action: 'create' },
            enable: 'can_create_password_profile',
          },
        ]);
      },
      can_create_password_profile: function (node, item) {
        var treeData = pgBrowser.tree.getTreeNodeHierarchy(item),
          server = treeData['server'];
        // role 생성 및 수정 권한과 동일한 레벨의 권한이면 password profile 사용가능
        return server.connected && server.user.can_create_role;
      },
      getSchema: function (treeNodeInfo, itemNodeData) {
        const transformData = (data) => {
          return data.map((item) => ({
            value: item._id,
            image: item.icon,
            label: item.label,
          }));
        };

        return new PasswordProfileSchema({
          nodeInfo: treeNodeInfo,
          getConnectionDatabaseList: () => {
            const api = getApiInstance();
            const group = treeNodeInfo.server_group._id;
            const server = treeNodeInfo.server._id;

            return api.get(`/browser/database/nodes/${group}/${server}`)
              .then((res) => {
                const data = res.data.data || [];
                const transformed = transformData(data);
                console.warn('database list fetched here:', transformed);
                return transformed;
              })
              .catch(() => {
                console.warn('catch raised while fetching database list.');
                return [];
              });
          },
          getSchemaOption: (database) => {
            if (!database) return [];
            return new Promise((resolve) => {
              const api = getApiInstance();
              const group = treeNodeInfo.server_group._id;
              const server = treeNodeInfo.server._id;
              api
                .get(`/browser/schema/nodes/${group}/${server}/${database}`)
                .then((res) => {
                  const data = transformData(res.data.data);
                  resolve(data);
                })
                .catch(() => {
                  resolve([]);
                });
            });
          },
          getFunctionOption: (database, schema) => {
            if (!database || !schema) return [];
            return new Promise((resolve) => {
              const api = getApiInstance();
              const group = treeNodeInfo.server_group._id;
              const server = treeNodeInfo.server._id;
              api
                .get(
                  `/browser/function/nodes/${group}/${server}/${database}/${schema}`
                )
                .then((res) => {
                  const data = transformData(res.data.data);
                  resolve(data);
                })
                .catch(() => {
                  resolve([]);
                });
            });
          },
          getFunctionSql: (dbId, schemaId, funcId) => {
            console.warn('[DEBUG] getFunctionSql args:', dbId, schemaId, funcId);

            if (!dbId || !schemaId || !funcId) {
              return Promise.resolve('--Script Load Error (invalid args)');
            }

            const api = getApiInstance();
            const group = treeNodeInfo.server_group._id;
            const server = treeNodeInfo.server._id;

            return api.get(`/browser/function/sql/${group}/${server}/${dbId}/${schemaId}/${funcId}`)
              .then((res) => {
                console.warn('[DEBUG] API Response:', res.data);
                return res.data?.data?.sql || '--No SQL Returned';
              })
              .catch((err) => {
                console.error('[DEBUG] getFunctionSql failed:', err);
                return '--Script Load Error (API failed)';
              });
          }
          // password_profile: () =>
          //   getNodeIdListByName('password_profile', treeNodeInfo, itemNodeData, {
          //     cacheLevel: 'database',
          //     cacheNode: 'database',
          //   }),
        });
      },
      // model: pgAdmin.Browser.Node.Model.extend({
      //   idAttribute: 'oid',
      //   defaults: {
      //     oid: null,
      //     prfname: null,
      //   },
      //   schema: [
      //     {
      //       id: 'oid',
      //       label: gettext('ID'),
      //       cell: 'string',
      //       mode: ['properties'],
      //       editable: false,
      //       type: 'text',
      //       visible: true,
      //     },
      //     {
      //       id: 'prfname',
      //       label: gettext('Profile Name'),
      //       editable: false,
      //       type: 'text',
      //       readonly: 'readonly',
      //       mode: ['properties'],
      //     },
      //   ],
      //   readonly: function (m) {
      //     if (!m.has('read_only')) {
      //       var user = this.node_info.server.user;

      //       m.set('read_only', !(user.is_superuser || user.can_create_role));
      //     }

      //     return m.get('read_only');
      //   },
      //   validate: function () {
      //     var err = {},
      //       errmsg,
      //       seclabels = this.get('seclabels');

      //     if (
      //       _.isUndefined(this.get('profileName')) ||
      //       String(this.get('profileName')).replace(/^\s+|\s+$/g, '') == ''
      //     ) {
      //       err['name'] = gettext('Name cannot be empty.');
      //       errmsg = err['name'];
      //     }

      //     if (seclabels) {
      //       var secLabelsErr;
      //       for (var i = 0; i < seclabels.models.length && !secLabelsErr; i++) {
      //         secLabelsErr = seclabels.models[i].validate.apply(
      //           seclabels.models[i]
      //         );
      //         if (secLabelsErr) {
      //           err['seclabels'] = secLabelsErr;
      //           errmsg = errmsg || secLabelsErr;
      //         }
      //       }
      //     }

      //     this.errorModel.clear().set(err);

      //     if (_.size(err)) {
      //       this.trigger('on-status', { msg: errmsg });
      //       return errmsg;
      //     }

      //     return null;
      //   },
      // }),
    });
  }

  return pgBrowser.Nodes['password_profile'];
});
