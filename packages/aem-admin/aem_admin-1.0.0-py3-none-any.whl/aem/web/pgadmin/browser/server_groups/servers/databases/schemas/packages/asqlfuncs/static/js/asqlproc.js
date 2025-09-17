/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2024, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////

import AsqlFuncSchema from './asqlfunc.ui';

/* Create and Register Procedure Collection and Node. */
define('pgadmin.node.asqlproc', [
  'sources/gettext', 'sources/url_for',
  'sources/pgadmin', 'pgadmin.browser',
  'pgadmin.browser.collection',
], function(
  gettext, url_for, pgAdmin, pgBrowser
) {

  if (!pgBrowser.Nodes['coll-asqlproc']) {
    pgAdmin.Browser.Nodes['coll-asqlproc'] =
      pgAdmin.Browser.Collection.extend({
        node: 'asqlproc',
        label: gettext('Procedures'),
        type: 'coll-asqlproc',
        columns: ['name', 'funcowner', 'description'],
        hasStatistics: true,
        canDrop: false,
        canDropCascade: false,
      });
  }

  // Inherit Functions Node
  if (!pgBrowser.Nodes['asqlproc']) {
    pgAdmin.Browser.Nodes['asqlproc'] = pgBrowser.Node.extend({
      type: 'asqlproc',
      dialogHelp: url_for('help.static', {'filename': 'asqlproc_dialog.html'}),
      label: gettext('Procedure'),
      collection_type: 'coll-asqlproc',
      hasDepends: true,
      canEdit: false,
      hasSQL: true,
      hasScriptTypes: [],
      parent_type: ['package'],
      Init: function() {
        /* Avoid multiple registration of menus */
        if (this.proc_initialized)
          return;

        this.proc_initialized = true;

      },
      canDrop: false,
      canDropCascade: false,
      getSchema: () => {
        return new AsqlFuncSchema(
          {}, {
            name: 'sysproc'
          }
        );
      }
    });

  }

  return pgBrowser.Nodes['asqlproc'];
});
