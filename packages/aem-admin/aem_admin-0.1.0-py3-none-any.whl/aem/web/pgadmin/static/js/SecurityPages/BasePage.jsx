import { Box, Button, darken } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useSnackbar } from 'notistack';
import React, { useEffect } from 'react';
import { MESSAGE_TYPE, NotifierMessage } from '../components/FormComponents';
import { FinalNotifyContent } from '../helpers/Notifier';
import PropTypes from 'prop-types';
import CustomPropTypes from '../custom_prop_types';

const StyledBox = styled(Box)(({theme}) => ({
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  display: 'flex',
  justifyContent: 'center',
  height: '100%',
  '& .BasePage-pageContent': {
    display: 'flex',
    flexDirection: 'column',
    padding: '16px',
    backgroundColor: contentBg,
    borderRadius: theme.shape.borderRadius,
    maxHeight: '100%',
    minWidth: '450px',
    maxWidth: '450px',
    '& .BasePage-item': {
      display: 'flex',
      justifyContent: 'center',
      marginBottom: '15px',
      fontSize: '1.2rem',
      width: '100%',
      height: '30px',
      '& .BasePage-logo': {
        width: '96px',
        height: '40px',
        background: 'url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjIyIiBoZWlnaHQ9IjM2IiB2aWV3Qm94PSIwIDAgMjIyIDM2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPg0KPGcgY2xpcC1wYXRoPSJ1cmwoI2NsaXAwXzEwMV8yKSI+DQo8cGF0aCBkPSJNNTUuMTIgMjEuMDhWMTcuNjdIMzkuMTZWNi44N0g1Ny4wN1YzLjM4SDM1LjI0VjM1LjkySDU3LjdWMzIuNDNIMzkuMTVWMjEuMDlINTUuMTFMNTUuMTIgMjEuMDhaIiBmaWxsPSJ3aGl0ZSIvPg0KPHBhdGggZD0iTTkyLjQ5IDM1LjkxSDk2LjIyTDk2LjE4IDMuMzdIOTIuOTZMNzkuNjggMjcuMDFMNjYuMjIgMy4zN0g2M1YzNS45MUg2Ni43M1YxMS4wMkw3OC43MyAzMS44OUg4MC40NUw5Mi40NSAxMC44N0w5Mi41IDM1LjkxSDkyLjQ5WiIgZmlsbD0id2hpdGUiLz4NCjxwYXRoIGQ9Ik0xNS4yOSAwTDAgMzUuOTlMMjIuNyAyNy44MUwyNS44NyAzNS4yN0gzMC4zOEwxNS4yOSAwWk0yMS4yOCAyNC4zMkw3LjE1IDI5LjQyTDguMDYgMjcuMTdMMTUuMjggMTAuMjJMMjEuMjcgMjQuMzNMMjEuMjggMjQuMzJaIiBmaWxsPSJ3aGl0ZSIvPg0KPHBhdGggZD0iTTEyMC40NCAxNC41TDEyNC44MiAyNS41M0gxMTYuMDNMMTIwLjQ0IDE0LjVaTTExOC4zMyAxMC45M0wxMDcuOTYgMzUuOTlIMTExLjg3TDExNC43OCAyOC42NUgxMjYuMDRMMTI4Ljk1IDM1Ljk5SDEzMy4wNEwxMjIuNzUgMTAuOTNIMTE4LjM0SDExOC4zM1oiIGZpbGw9IiNGQkNCMDkiLz4NCjxwYXRoIGQ9Ik0xMzUuNDggMzUuOTlWMTAuOTNIMTQ0LjNDMTQ2LjEgMTAuOTEgMTQ3Ljg4IDExLjIzIDE0OS41NiAxMS44NkMxNTEuMTEgMTIuNDYgMTUyLjUzIDEzLjM1IDE1My43NCAxNC40OUMxNTYuMiAxNi44MiAxNTcuNTggMjAuMDcgMTU3LjU0IDIzLjQ2QzE1Ny41OCAyNi44NCAxNTYuMjEgMzAuMDkgMTUzLjc2IDMyLjQzQzE1Mi41NiAzMy41OCAxNTEuMTMgMzQuNDcgMTQ5LjU4IDM1LjA2QzE0Ny44OSAzNS43IDE0Ni4xMSAzNi4wMSAxNDQuMyAzNS45OUgxMzUuNDhaTTEzOS4yNSAzMi42M0gxNDQuMzhDMTQ1LjYzIDMyLjY0IDE0Ni44NyAzMi40MSAxNDguMDQgMzEuOTVDMTUwLjI3IDMxLjA2IDE1Mi4wNSAyOS4zMSAxNTIuOTcgMjcuMUMxNTMuNDQgMjUuOTYgMTUzLjY4IDI0LjczIDE1My42NyAyMy41QzE1My42OCAyMi4yNSAxNTMuNDQgMjEuMDEgMTUyLjk1IDE5Ljg1QzE1Mi4wMyAxNy42NCAxNTAuMjYgMTUuODkgMTQ4LjAzIDE1QzE0Ni44NiAxNC41MiAxNDUuNiAxNC4yOSAxNDQuMzQgMTQuM0gxMzkuMjVWMzIuNjRWMzIuNjNaIiBmaWxsPSIjRkJDQjA5Ii8+DQo8cGF0aCBkPSJNMTk1Ljg1IDEwLjkzSDE5Mi4wOFYzNS45OUgxOTUuODVWMTAuOTNaIiBmaWxsPSIjRkJDQjA5Ii8+DQo8cGF0aCBkPSJNMjAwLjggMzUuOTlWMTAuOTJIMjA0LjQ2TDIxOC40NSAyOS41NFYxMC45MkgyMjJWMzUuOThIMjE4LjY2TDIwNC4zNSAxNi44M1YzNS45OUgyMDAuOFoiIGZpbGw9IiNGQkNCMDkiLz4NCjxwYXRoIGQ9Ik0xODQuMjMgMTEuMzdMMTc0LjQ0IDMxLjg4TDE2NC40NyAxMS4zOEgxNjEuNVYzNS45OUgxNjQuNzRWMTguODdMMTczLjAyIDM1Ljk5SDE3NS43TDE4My45MiAxOC42VjM1Ljk5SDE4Ny4xN1YxMS4zN0gxODQuMjNaIiBmaWxsPSIjRkJDQjA5Ii8+DQo8L2c+DQo8ZGVmcz4NCjxjbGlwUGF0aCBpZD0iY2xpcDBfMTAxXzIiPg0KPHJlY3Qgd2lkdGg9IjIyMiIgaGVpZ2h0PSIzNiIgZmlsbD0id2hpdGUiLz4NCjwvY2xpcFBhdGg+DQo8L2RlZnM+DQo8L3N2Zz4NCg==) 0 0 no-repeat',
        backgroundPositionY: 'center',
        'background-size': 'contain',
      },
    },
    '& .BasePage-button': {
      backgroundColor: loginBtnBg,
      color: '#fff',
      padding: '4px 8px',
      width: '100%',
      '&:hover': {
        backgroundColor: darken(loginBtnBg, 0.1),
      },
      '&.Mui-disabled': {
        opacity: 0.60,
        color: '#fff'
      },
    }
  },
}));

const contentBg = '#000';
const loginBtnBg = '#292928';

export function SecurityButton({...props}) {

  return <Button type="submit" className='BasePage-button' {...props} />;
}

export default function BasePage({pageImage, title,  children, messages}) {
  const snackbar = useSnackbar();
  useEffect(()=>{
    messages?.forEach((message)=>{
      let options = {
        autoHideDuration: null,
        content:(key)=>{
          if(Array.isArray(message[0])) message[0] = message[0][0];
          const type = Object.values(MESSAGE_TYPE).includes(message[0]) ? message[0] : MESSAGE_TYPE.INFO;
          return <FinalNotifyContent>
            <NotifierMessage type={type} message={message[1]} closable={true} onClose={()=>{snackbar.closeSnackbar(key);}} style={{maxWidth: '400px'}} />
          </FinalNotifyContent>;
        }
      };
      options.content.displayName = 'content';
      snackbar.enqueueSnackbar(options);
    });
  }, [messages]);
  return (
    <StyledBox >
      <Box display="flex" minWidth="80%" gap="40px" alignItems="center" padding="20px 80px">
        <Box flexGrow={1} height="80%" textAlign="center">
          {pageImage}
        </Box>
        <Box className='BasePage-pageContent'>
          <Box className='BasePage-item'><div className='BasePage-logo' /></Box>
          <Box className='BasePage-item'>{title}</Box>
          <Box display="flex" flexDirection="column" minHeight={0}>{children}</Box>
        </Box>
      </Box>
    </StyledBox>
  );
}

BasePage.propTypes = {
  pageImage: CustomPropTypes.children,
  title: PropTypes.string,
  children: CustomPropTypes.children,
  messages: PropTypes.arrayOf(PropTypes.array)
};
