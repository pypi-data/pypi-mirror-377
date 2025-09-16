/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2022, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////
import RowSecurityPolicySchema from './redaction_policy.ui';
import getApiInstance from '../../../../../../../../../static/js/api_instance';
import { getNodeListByName } from '../../../../../../../../static/js/node_ajax';


define('pgadmin.node.redaction_policy', [
  'sources/gettext', 'sources/url_for', 'jquery', 'underscore',
  'sources/pgadmin', 'pgadmin.browser',
  'pgadmin.backform', 'pgadmin.alertifyjs',
  'pgadmin.node.schema.dir/schema_child_tree_node',
  'pgadmin.browser.collection',
], function(
  gettext, url_for, $, _, pgAdmin, pgBrowser, Backform, alertify,
  SchemaChildTreeNode
) {

  if (!pgBrowser.Nodes['coll-redaction_policy']) {
    pgAdmin.Browser.Nodes['coll-redaction_policy'] =
      pgAdmin.Browser.Collection.extend({
        node: 'redaction_policy',
        label: gettext('RLS Policies'),
        type: 'coll-redaction_policy',
        columns: ['name', 'description'],
        canDrop: SchemaChildTreeNode.isTreeItemOfChildOfSchema,
        canDropCascade: SchemaChildTreeNode.isTreeItemOfChildOfSchema,
      });
  }

  if (!pgBrowser.Nodes['redaction_policy']) {
    pgAdmin.Browser.Nodes['redaction_policy'] = pgBrowser.Node.extend({
      parent_type: ['table', 'view', 'partition'],
      collection_type: ['coll-table', 'coll-view'],
      type: 'redaction_policy',
      label: gettext('RLS Policy'),
      hasSQL:  true,
      hasDepends: true,
      width: pgBrowser.stdW.sm + 'px',
      sqlAlterHelp: 'sql-alterpolicy.html',
      sqlCreateHelp: 'sql-createpolicy.html',
      dialogHelp: url_for('help.static', {'filename': 'rls_policy_dialog.html'}),
      url_jump_after_node: 'schema',
      Init: function() {
        /* Avoid mulitple registration of menus */
        if (this.initialized)
          return;

        this.initialized = true;        
      },
      canDrop: SchemaChildTreeNode.isTreeItemOfChildOfSchema,
      canDropCascade: SchemaChildTreeNode.isTreeItemOfChildOfSchema,
      getSchema: function(treeNodeInfo, itemNodeData) {
        // const transformData = (data) => {
        //   return data.map((item) => ({
        //     value: item._id,
        //     image: item.icon,
        //     label: item.label,
        //   }));
        // };
        const transformData_tables = (data) => {
          return data.map((item) => ({
            value: item.oid,
            image: item.icon,
            label: item.name,
          }));
        };
        return new RowSecurityPolicySchema(
          {
            role: ()=>getNodeListByName('role', treeNodeInfo, itemNodeData, {}, ()=>true, (res)=>{
              res.unshift({label: 'PUBLIC', value: 'public'});
              return res;
            }),
            getDatabases: () => {              
              return new Promise((resolve) => {
                const api = getApiInstance();
                const group = treeNodeInfo.server_group._id;
                const server = treeNodeInfo.server._id;
                const database = treeNodeInfo.database._id;
                const schema = treeNodeInfo.schema._id;
                api
                  .get(`/browser/table/obj/${group}/${server}/${database}/${schema}/`)
                  .then((res) => {
                    const data = transformData_tables(res.data);
                    resolve(data);
                  })
                  .catch(() => {
                    resolve([]);
                  });
              }); 
            },
            nodeInfo: treeNodeInfo
          }
        );
      },
      model: pgAdmin.Browser.Node.Model.extend({
        idAttribute: 'oid',
        defaults: {
          name: undefined,
        },
        schema: [{
          id: 'name',
          label: gettext('Name'),
          cell: 'text',
          editable: true,
          type: 'text',
          readonly: false,
          noEmpty: true,
        },{
          id: 'rdenable',
          label: gettext('Redaction Enable'),
          cell: 'string',
          editable: false,
          type: 'text',
          mode: ['properties'],
        },{
          id: 'rdexpr',
          label: gettext('Redaction policy expression'),
          cell: 'string',
          editable: false,
          type: 'text',
          mode: ['properties'],
        }],
      }),      
    });
  }

  return pgBrowser.Nodes['redaction_policy'];
});
