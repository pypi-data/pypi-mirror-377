/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { Box, Typography, makeStyles } from '@material-ui/core';
import { DefaultButton, PgIconButton } from './Buttons';
import CloseIcon from '@material-ui/icons/Close';
import InfoIcon from '@material-ui/icons/InfoRounded';
import HelpIcon from '@material-ui/icons/HelpRounded';
import Loader from 'sources/components/Loader';
import getApiInstance from 'sources/api_instance';
import gettext from 'sources/gettext';
import { generateNodeUrl } from '../../../browser/static/js/node_ajax';
import { usePgAdmin } from '../BrowserComponent';
import { InputSQL } from './FormComponents';

const useDialogStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
  },
  body: {
    height: '90%',
    padding: '1em',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  textStyle: {
    color: theme.palette.secondary.buttonColor,
    fontSize: 'bold',
  },
  footer: {
    padding: theme.spacing(1),
    background: theme.otherVars.headerBg,
    display: 'flex',
    zIndex: 1010,
    ...theme.mixins.panelBorder.top,
  },
  // mappedControl: {
  //   paddingBottom: theme.spacing(1),
  // },
  buttonMargin: {
    marginRight: '0.5rem',
  },
  sqlTabInput: {
    border: 0,
  },
}));

export default function PackagePreview(props) {
  const { nodeData, onClose, panelId, node, actionType, treeNodeInfo } = props;
  const api = getApiInstance();
  const classes = useDialogStyles();
  const [loaderText, setLoaderText] = useState();
  const [packageDetails, setPackageDetails] = useState();
  let urlBase = generateNodeUrl.call(
    node,
    treeNodeInfo,
    actionType,
    nodeData,
    false,
    node.url_jump_after_node
  );
  const handleFetchPackage = async () => {
    setLoaderText('Loading...');

    try {
      const response = await api.get(urlBase + `${nodeData?._id}`);
      setPackageDetails(response?.data);
      setLoaderText();
    } catch (error) {
      setLoaderText();
      console.log(error?.response);
    }
  };

  useEffect(() => {
    handleFetchPackage();
  }, []);

  const onHelp = () => {
    window.open('https://techsupport.skaiworldwide.com/', '_blank');
  };

  return (
    <Box className={classes.root}>
      <Loader message={loaderText} />
      {!loaderText && (
        <Box className={classes.body}>
          {packageDetails && (
            <>
              <InputSQL
                value={`${packageDetails?.pkgspec}\n \n \n${packageDetails?.pkgbody}`}
                options={{
                  readOnly: true,
                }}
                readonly={true}
                className={classes.sqlTabInput}
              />
              ;
            </>
          )}
        </Box>
      )}
      <Box className={classes.footer}>
        <Box>
          <PgIconButton
            data-test="sql-help"
            onClick={() => onHelp()}
            icon={<InfoIcon />}
            className={classes.buttonMargin}
            title="SQL help for this object type."
          />
          <PgIconButton
            data-test="dialog-help"
            onClick={() => onHelp()}
            icon={<HelpIcon />}
            title="Help for this dialog."
          />
        </Box>
        <Box marginLeft="auto">
          <DefaultButton
            data-test="Close"
            onClick={onClose}
            startIcon={<CloseIcon />}
            className={classes.buttonMargin}
          >
            {gettext('Close')}
          </DefaultButton>
        </Box>
      </Box>
    </Box>
  );
}
