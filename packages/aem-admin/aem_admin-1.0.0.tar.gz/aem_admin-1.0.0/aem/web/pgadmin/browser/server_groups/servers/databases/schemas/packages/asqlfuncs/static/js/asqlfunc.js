/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2024, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////

import AsqlFuncSchema from './asqlfunc.ui';

/* Create and Register Function Collection and Node. */
define('pgadmin.node.asqlfunc', [
  'sources/gettext', 'sources/url_for', 'pgadmin.browser',
  'pgadmin.browser.collection',
], function(gettext, url_for, pgBrowser) {

  if (!pgBrowser.Nodes['coll-asqlfunc']) {
    pgBrowser.Nodes['coll-asqlfunc'] =
      pgBrowser.Collection.extend({
        node: 'asqlfunc',
        label: gettext('Functions'),
        type: 'coll-asqlfunc',
        columns: ['name', 'funcowner', 'description'],
        canDrop: false,
        canDropCascade: false,
      });
  }

  if (!pgBrowser.Nodes['asqlfunc']) {
    pgBrowser.Nodes['asqlfunc'] = pgBrowser.Node.extend({
      type: 'asqlfunc',
      dialogHelp: url_for('help.static', {'filename': 'asqlfunc_dialog.html'}),
      label: gettext('Function'),
      collection_type: 'coll-asqlfunc',
      hasDepends: true,
      canEdit: false,
      hasSQL: true,
      hasScriptTypes: [],
      parent_type: ['package'],
      Init: function() {
        /* Avoid multiple registration of menus */
        if (this.initialized)
          return;

        this.initialized = true;

      },
      canDrop: false,
      canDropCascade: false,
      getSchema: () => {
        return new AsqlFuncSchema(
          {}, {
            name: 'sysfunc'
          }
        );
      }
    });

  }

  return pgBrowser.Nodes['asqlfunc'];
});
