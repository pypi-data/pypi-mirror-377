/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2024, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////

import AsqlVarSchema from './asqlvar.ui';

/* Create and Register Function Collection and Node. */
define('pgadmin.node.asqlvar', [
  'sources/gettext',
  'sources/url_for',
  'pgadmin.browser',
  'pgadmin.browser.collection',
], function (gettext, url_for, pgBrowser) {
  if (!pgBrowser.Nodes['coll-asqlvar']) {
    pgBrowser.Nodes['coll-asqlvar'] = pgBrowser.Collection.extend({
      node: 'asqlvar',
      label: gettext('Variables'),
      type: 'coll-asqlvar',
      columns: ['name', 'funcowner', 'description'],
      canDrop: false,
      canDropCascade: false,
    });
  }

  if (!pgBrowser.Nodes['asqlvar']) {
    pgBrowser.Nodes['asqlvar'] = pgBrowser.Node.extend({
      type: 'asqlvar',
      dialogHelp: url_for('help.static', { filename: 'asqlvar_dialog.html' }),
      label: gettext('Function'),
      collection_type: 'coll-asqlvar',
      canEdit: false,
      hasSQL: true,
      hasScriptTypes: [],
      parent_type: ['package'],
      Init: function () {
        /* Avoid mulitple registration of menus */
        if (this.initialized) return;

        this.initialized = true;
      },
      canDrop: false,
      canDropCascade: false,
      getSchema: () => {
        return new AsqlVarSchema();
      },
    });
  }

  return pgBrowser.Nodes['asqlvar'];
});
