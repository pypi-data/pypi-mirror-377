/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2024, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////
import React from 'react';
import Welcome_Logo from '../img/welcome_logo.svg';
import { Box } from '@material-ui/core';

export default function PgAdminLogo() {

  return (
    <div className="welcome-logo" aria-hidden="true">
      <Box
        component={'img'}
        src={Welcome_Logo}
        sx={{ width: '80%', height: '80%' }}
      />
    </div>
  );
}
