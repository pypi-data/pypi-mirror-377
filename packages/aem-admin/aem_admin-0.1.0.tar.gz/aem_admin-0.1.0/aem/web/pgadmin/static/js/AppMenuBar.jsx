/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2025, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////
import { Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import React, { useEffect } from 'react';
import { PrimaryButton } from './components/Buttons';
import { PgMenu, PgMenuDivider, PgMenuItem, PgSubMenu } from './components/Menu';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import AccountCircleRoundedIcon from '@mui/icons-material/AccountCircleRounded';
import { usePgAdmin } from 'sources/PgAdminProvider';
import { useForceUpdate } from './custom_hooks';


const StyledBox = styled(Box)(({theme}) => ({
  height: '30px',
  backgroundColor: theme.palette.primary.menubarBackground,
  color: theme.palette.primary.contrastText,
  padding: '0 0.5rem',
  display: 'flex',
  alignItems: 'center',
  '& .AppMenuBar-logo': {
    width: '96px',
    height: '100%',
    /*
       * Using the SVG postgresql logo, modified to set the background color as #FFF
       * https://wiki.postgresql.org/images/9/90/PostgreSQL_logo.1color_blue.svg
       * background: url("data:image/svg+xml,%3C%3Fxml version='1.0' encoding='utf-8'%3F%3E%3C!-- Generator: Adobe Illustrator 22.1.0, SVG Export Plug-In . SVG Version: 6.00 Build 0) --%3E%3Csvg version='1.1' id='Layer_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' viewBox='0 0 42 42' style='enable-background:new 0 0 42 42;' xml:space='preserve'%3E%3Cstyle type='text/css'%3E .st0%7Bstroke:%23000000;stroke-width:3.3022;%7D .st1%7Bfill:%23336791;%7D .st2%7Bfill:none;stroke:%23FFFFFF;stroke-width:1.1007;stroke-linecap:round;stroke-linejoin:round;%7D .st3%7Bfill:none;stroke:%23FFFFFF;stroke-width:1.1007;stroke-linecap:round;stroke-linejoin:bevel;%7D .st4%7Bfill:%23FFFFFF;stroke:%23FFFFFF;stroke-width:0.3669;%7D .st5%7Bfill:%23FFFFFF;stroke:%23FFFFFF;stroke-width:0.1835;%7D .st6%7Bfill:none;stroke:%23FFFFFF;stroke-width:0.2649;stroke-linecap:round;stroke-linejoin:round;%7D%0A%3C/style%3E%3Cg id='orginal'%3E%3C/g%3E%3Cg id='Layer_x0020_3'%3E%3Cpath class='st0' d='M31.3,30c0.3-2.1,0.2-2.4,1.7-2.1l0.4,0c1.2,0.1,2.8-0.2,3.7-0.6c2-0.9,3.1-2.4,1.2-2 c-4.4,0.9-4.7-0.6-4.7-0.6c4.7-7,6.7-15.8,5-18c-4.6-5.9-12.6-3.1-12.7-3l0,0c-0.9-0.2-1.9-0.3-3-0.3c-2,0-3.5,0.5-4.7,1.4 c0,0-14.3-5.9-13.6,7.4c0.1,2.8,4,21.3,8.7,15.7c1.7-2,3.3-3.8,3.3-3.8c0.8,0.5,1.8,0.8,2.8,0.7l0.1-0.1c0,0.3,0,0.5,0,0.8 c-1.2,1.3-0.8,1.6-3.2,2.1c-2.4,0.5-1,1.4-0.1,1.6c1.1,0.3,3.7,0.7,5.5-1.8l-0.1,0.3c0.5,0.4,0.4,2.7,0.5,4.4 c0.1,1.7,0.2,3.2,0.5,4.1c0.3,0.9,0.7,3.3,3.9,2.6C29.1,38.3,31.1,37.5,31.3,30'/%3E%3Cpath class='st1' d='M38.3,25.3c-4.4,0.9-4.7-0.6-4.7-0.6c4.7-7,6.7-15.8,5-18c-4.6-5.9-12.6-3.1-12.7-3l0,0 c-0.9-0.2-1.9-0.3-3-0.3c-2,0-3.5,0.5-4.7,1.4c0,0-14.3-5.9-13.6,7.4c0.1,2.8,4,21.3,8.7,15.7c1.7-2,3.3-3.8,3.3-3.8 c0.8,0.5,1.8,0.8,2.8,0.7l0.1-0.1c0,0.3,0,0.5,0,0.8c-1.2,1.3-0.8,1.6-3.2,2.1c-2.4,0.5-1,1.4-0.1,1.6c1.1,0.3,3.7,0.7,5.5-1.8 l-0.1,0.3c0.5,0.4,0.8,2.4,0.7,4.3c-0.1,1.9-0.1,3.2,0.3,4.2c0.4,1,0.7,3.3,3.9,2.6c2.6-0.6,4-2,4.2-4.5c0.1-1.7,0.4-1.5,0.5-3 l0.2-0.7c0.3-2.3,0-3.1,1.7-2.8l0.4,0c1.2,0.1,2.8-0.2,3.7-0.6C39,26.4,40.2,24.9,38.3,25.3L38.3,25.3z'/%3E%3Cpath class='st2' d='M21.8,26.6c-0.1,4.4,0,8.8,0.5,9.8c0.4,1.1,1.3,3.2,4.5,2.5c2.6-0.6,3.6-1.7,4-4.1c0.3-1.8,0.9-6.7,1-7.7'/%3E%3Cpath class='st2' d='M18,4.7c0,0-14.3-5.8-13.6,7.4c0.1,2.8,4,21.3,8.7,15.7c1.7-2,3.2-3.7,3.2-3.7'/%3E%3Cpath class='st2' d='M25.7,3.6c-0.5,0.2,7.9-3.1,12.7,3c1.7,2.2-0.3,11-5,18'/%3E%3Cpath class='st3' d='M33.5,24.6c0,0,0.3,1.5,4.7,0.6c1.9-0.4,0.8,1.1-1.2,2c-1.6,0.8-5.3,0.9-5.3-0.1 C31.6,24.5,33.6,25.3,33.5,24.6c-0.1-0.6-1.1-1.2-1.7-2.7c-0.5-1.3-7.3-11.2,1.9-9.7c0.3-0.1-2.4-8.7-11-8.9 c-8.6-0.1-8.3,10.6-8.3,10.6'/%3E%3Cpath class='st2' d='M19.4,25.6c-1.2,1.3-0.8,1.6-3.2,2.1c-2.4,0.5-1,1.4-0.1,1.6c1.1,0.3,3.7,0.7,5.5-1.8c0.5-0.8,0-2-0.7-2.3 C20.5,25.1,20,24.9,19.4,25.6L19.4,25.6z'/%3E%3Cpath class='st2' d='M19.3,25.5c-0.1-0.8,0.3-1.7,0.7-2.8c0.6-1.6,2-3.3,0.9-8.5c-0.8-3.9-6.5-0.8-6.5-0.3c0,0.5,0.3,2.7-0.1,5.2 c-0.5,3.3,2.1,6,5,5.7'/%3E%3Cpath class='st4' d='M18,13.8c0,0.2,0.3,0.7,0.8,0.7c0.5,0.1,0.9-0.3,0.9-0.5c0-0.2-0.3-0.4-0.8-0.4C18.4,13.6,18,13.7,18,13.8 L18,13.8z'/%3E%3Cpath class='st5' d='M32,13.5c0,0.2-0.3,0.7-0.8,0.7c-0.5,0.1-0.9-0.3-0.9-0.5c0-0.2,0.3-0.4,0.8-0.4C31.6,13.2,32,13.3,32,13.5 L32,13.5z'/%3E%3Cpath class='st2' d='M33.7,12.2c0.1,1.4-0.3,2.4-0.4,3.9c-0.1,2.2,1,4.7-0.6,7.2'/%3E%3Cpath class='st6' d='M2.7,6.6'/%3E%3C/g%3E%3C/svg%3E%0A")  0 0 no-repeat;
       */
    background: 'url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjIyIiBoZWlnaHQ9IjM2IiB2aWV3Qm94PSIwIDAgMjIyIDM2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPg0KPGcgY2xpcC1wYXRoPSJ1cmwoI2NsaXAwXzEwMV8yKSI+DQo8cGF0aCBkPSJNNTUuMTIgMjEuMDhWMTcuNjdIMzkuMTZWNi44N0g1Ny4wN1YzLjM4SDM1LjI0VjM1LjkySDU3LjdWMzIuNDNIMzkuMTVWMjEuMDlINTUuMTFMNTUuMTIgMjEuMDhaIiBmaWxsPSJ3aGl0ZSIvPg0KPHBhdGggZD0iTTkyLjQ5IDM1LjkxSDk2LjIyTDk2LjE4IDMuMzdIOTIuOTZMNzkuNjggMjcuMDFMNjYuMjIgMy4zN0g2M1YzNS45MUg2Ni43M1YxMS4wMkw3OC43MyAzMS44OUg4MC40NUw5Mi40NSAxMC44N0w5Mi41IDM1LjkxSDkyLjQ5WiIgZmlsbD0id2hpdGUiLz4NCjxwYXRoIGQ9Ik0xNS4yOSAwTDAgMzUuOTlMMjIuNyAyNy44MUwyNS44NyAzNS4yN0gzMC4zOEwxNS4yOSAwWk0yMS4yOCAyNC4zMkw3LjE1IDI5LjQyTDguMDYgMjcuMTdMMTUuMjggMTAuMjJMMjEuMjcgMjQuMzNMMjEuMjggMjQuMzJaIiBmaWxsPSJ3aGl0ZSIvPg0KPHBhdGggZD0iTTEyMC40NCAxNC41TDEyNC44MiAyNS41M0gxMTYuMDNMMTIwLjQ0IDE0LjVaTTExOC4zMyAxMC45M0wxMDcuOTYgMzUuOTlIMTExLjg3TDExNC43OCAyOC42NUgxMjYuMDRMMTI4Ljk1IDM1Ljk5SDEzMy4wNEwxMjIuNzUgMTAuOTNIMTE4LjM0SDExOC4zM1oiIGZpbGw9IiNGQkNCMDkiLz4NCjxwYXRoIGQ9Ik0xMzUuNDggMzUuOTlWMTAuOTNIMTQ0LjNDMTQ2LjEgMTAuOTEgMTQ3Ljg4IDExLjIzIDE0OS41NiAxMS44NkMxNTEuMTEgMTIuNDYgMTUyLjUzIDEzLjM1IDE1My43NCAxNC40OUMxNTYuMiAxNi44MiAxNTcuNTggMjAuMDcgMTU3LjU0IDIzLjQ2QzE1Ny41OCAyNi44NCAxNTYuMjEgMzAuMDkgMTUzLjc2IDMyLjQzQzE1Mi41NiAzMy41OCAxNTEuMTMgMzQuNDcgMTQ5LjU4IDM1LjA2QzE0Ny44OSAzNS43IDE0Ni4xMSAzNi4wMSAxNDQuMyAzNS45OUgxMzUuNDhaTTEzOS4yNSAzMi42M0gxNDQuMzhDMTQ1LjYzIDMyLjY0IDE0Ni44NyAzMi40MSAxNDguMDQgMzEuOTVDMTUwLjI3IDMxLjA2IDE1Mi4wNSAyOS4zMSAxNTIuOTcgMjcuMUMxNTMuNDQgMjUuOTYgMTUzLjY4IDI0LjczIDE1My42NyAyMy41QzE1My42OCAyMi4yNSAxNTMuNDQgMjEuMDEgMTUyLjk1IDE5Ljg1QzE1Mi4wMyAxNy42NCAxNTAuMjYgMTUuODkgMTQ4LjAzIDE1QzE0Ni44NiAxNC41MiAxNDUuNiAxNC4yOSAxNDQuMzQgMTQuM0gxMzkuMjVWMzIuNjRWMzIuNjNaIiBmaWxsPSIjRkJDQjA5Ii8+DQo8cGF0aCBkPSJNMTk1Ljg1IDEwLjkzSDE5Mi4wOFYzNS45OUgxOTUuODVWMTAuOTNaIiBmaWxsPSIjRkJDQjA5Ii8+DQo8cGF0aCBkPSJNMjAwLjggMzUuOTlWMTAuOTJIMjA0LjQ2TDIxOC40NSAyOS41NFYxMC45MkgyMjJWMzUuOThIMjE4LjY2TDIwNC4zNSAxNi44M1YzNS45OUgyMDAuOFoiIGZpbGw9IiNGQkNCMDkiLz4NCjxwYXRoIGQ9Ik0xODQuMjMgMTEuMzdMMTc0LjQ0IDMxLjg4TDE2NC40NyAxMS4zOEgxNjEuNVYzNS45OUgxNjQuNzRWMTguODdMMTczLjAyIDM1Ljk5SDE3NS43TDE4My45MiAxOC42VjM1Ljk5SDE4Ny4xN1YxMS4zN0gxODQuMjNaIiBmaWxsPSIjRkJDQjA5Ii8+DQo8L2c+DQo8ZGVmcz4NCjxjbGlwUGF0aCBpZD0iY2xpcDBfMTAxXzIiPg0KPHJlY3Qgd2lkdGg9IjIyMiIgaGVpZ2h0PSIzNiIgZmlsbD0id2hpdGUiLz4NCjwvY2xpcFBhdGg+DQo8L2RlZnM+DQo8L3N2Zz4NCg==) 0 0 no-repeat',
    backgroundPositionY: 'center',
    'background-size': 'contain',
  },
  '& .AppMenuBar-menus': {
    display: 'flex',
    alignItems: 'center',
    gap: '2px',
    marginLeft: '16px',

    '& .MuiButton-containedPrimary': {
      padding: '1px 8px',
      backgroundColor: theme.palette.primary.menubarBackground, // new background
      color: theme.palette.primary.contrastText, // text color
      '&:hover': {
        backgroundColor: theme.palette.primary.dark, // optional hover
      }
    }
  },
  '& .AppMenuBar-userMenu': {
    marginLeft: 'auto',
    '& .MuiButton-containedPrimary': {
      fontSize: '0.825rem',
      backgroundColor: theme.palette.primary.menubarBackground, // new background
      color: theme.palette.primary.contrastText, // text color
      '&:hover': {
        backgroundColor: theme.palette.primary.dark, // optional hover
      }
    },
    '& .AppMenuBar-gravatar': {
      marginRight: '4px',
      padding: '1px 8px',
      backgroundColor: theme.palette.primary.menubarBackground, // new background
      color: theme.palette.primary.contrastText, // text color
      '&:hover': {
        backgroundColor: theme.palette.primary.dark, // optional hover
      }
    }
  },
}));



export default function AppMenuBar() {

  const forceUpdate = useForceUpdate();
  const pgAdmin = usePgAdmin();

  useEffect(()=>{
    pgAdmin.Browser.Events.on('pgadmin:enable-disable-menu-items', _.debounce(()=>{
      forceUpdate();
    }, 100));
    pgAdmin.Browser.Events.on('pgadmin:refresh-app-menu', _.debounce(()=>{
      forceUpdate();
    }, 100));
  }, []);

  const getPgMenuItem = (menuItem, i)=>{
    if(menuItem.type == 'separator') {
      return <PgMenuDivider key={i}/>;
    }
    const hasCheck = typeof menuItem.checked == 'boolean';

    return <PgMenuItem
      key={i}
      disabled={menuItem.isDisabled}
      onClick={()=>{
        menuItem.callback();
        if(hasCheck) {
          forceUpdate();
        }
      }}
      hasCheck={hasCheck}
      checked={menuItem.checked}
      closeOnCheck={true}
    >{menuItem.label}</PgMenuItem>;
  };

  const userMenuInfo = pgAdmin.Browser.utils.userMenuInfo;

  const getPgMenu = (menu)=>{
    return menu.getMenuItems()?.map((menuItem, i)=>{
      const submenus = menuItem.getMenuItems();
      if(submenus) {
        return <PgSubMenu key={menuItem.label} label={menuItem.label}>
          {getPgMenu(menuItem)}
        </PgSubMenu>;
      }
      return getPgMenuItem(menuItem, i);
    });
  };

  return (
    <StyledBox data-test="app-menu-bar">
      <div className='AppMenuBar-logo' />
      <div className='AppMenuBar-menus'>
        {pgAdmin.Browser.MainMenus?.map((menu)=>{
          return (
            <PgMenu
              menuButton={<PrimaryButton key={menu.label} data-label={menu.label}>{menu.label}<KeyboardArrowDownIcon fontSize="small" /></PrimaryButton>}
              label={menu.label}
              key={menu.name}
            >
              {getPgMenu(menu)}
            </PgMenu>
          );
        })}
      </div>
      {userMenuInfo &&
        <div className='AppMenuBar-userMenu'>
          <PgMenu
            menuButton={
              <PrimaryButton data-test="loggedin-username">
                <div className='AppMenuBar-gravatar'>
                  {userMenuInfo.gravatar &&
                  <img src={userMenuInfo.gravatar} width = "18" height = "18"
                    alt ={`Gravatar for ${ userMenuInfo.username }`} />}
                  {!userMenuInfo.gravatar && <AccountCircleRoundedIcon />}
                </div>
                { userMenuInfo.username } ({userMenuInfo.auth_source})
                <KeyboardArrowDownIcon fontSize="small" />
              </PrimaryButton>
            }
            label={userMenuInfo.username}
            align="end"
          >
            {userMenuInfo.menus.map((menuItem, i)=>{
              return getPgMenuItem(menuItem, i);
            })}
          </PgMenu>
        </div>}
    </StyledBox>
  );
}
