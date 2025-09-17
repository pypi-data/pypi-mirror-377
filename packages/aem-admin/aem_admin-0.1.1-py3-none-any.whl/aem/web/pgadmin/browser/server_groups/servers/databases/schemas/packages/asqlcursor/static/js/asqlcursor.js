/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2024, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////

import AsqlCursorSchema from './asqlcursor.ui';

/* Create and Register Function Collection and Node. */
define('pgadmin.node.asqlcursor', [
  'sources/gettext',
  'sources/url_for',
  'pgadmin.browser',
  'pgadmin.browser.collection',
], function (gettext, url_for, pgBrowser) {

  if (!pgBrowser.Nodes['coll-asqlcursor']) {
    pgBrowser.Nodes['coll-asqlcursor'] = pgBrowser.Collection.extend({
      node: 'asqlcursor',
      label: gettext('Cursors'),
      type: 'coll-asqlcursor',
      columns: ['name', 'funcowner', 'description'],
      canDrop: false,
      canDropCascade: false,
    });
  }

  if (!pgBrowser.Nodes['asqlcursor']) {
    pgBrowser.Nodes['asqlcursor'] = pgBrowser.Node.extend({
      type: 'asqlcursor',
      dialogHelp: url_for('help.static', { filename: 'asqlcursor_dialog.html' }),
      label: gettext('Function'),
      collection_type: 'coll-asqlcursor',
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
        return new AsqlCursorSchema();
      },
    });
  }

  return pgBrowser.Nodes['asqlcursor'];
});
