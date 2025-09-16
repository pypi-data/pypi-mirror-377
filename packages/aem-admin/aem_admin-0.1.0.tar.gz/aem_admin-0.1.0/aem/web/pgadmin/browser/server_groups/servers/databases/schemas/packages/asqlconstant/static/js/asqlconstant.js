/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2024, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////

import AsqlConstantSchema from './asqlconstant.ui';

/* Create and Register Function Collection and Node. */
define('pgadmin.node.asqlvar', [
  'sources/gettext',
  'sources/url_for',
  'pgadmin.browser',
  'pgadmin.browser.collection',
], function (gettext, url_for, pgBrowser) {
  
  if (!pgBrowser.Nodes['coll-asqlconstant']) {
    pgBrowser.Nodes['coll-asqlconstant'] = pgBrowser.Collection.extend({
      node: 'asqlconstant',
      label: gettext('Constants'),
      type: 'coll-asqlconstant',
      columns: ['name', 'funcowner', 'description'],
      canDrop: false,
      canDropCascade: false,
    });
  }

  if (!pgBrowser.Nodes['asqlconstant']) {
    pgBrowser.Nodes['asqlconstant'] = pgBrowser.Node.extend({
      type: 'asqlconstant',
      dialogHelp: url_for('help.static', { filename: 'asqlconstant_dialog.html' }),
      label: gettext('Function'),
      collection_type: 'coll-asqlconstant',
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
        return new AsqlConstantSchema();
      },
    });
  }

  return pgBrowser.Nodes['asqlconstant'];
});
