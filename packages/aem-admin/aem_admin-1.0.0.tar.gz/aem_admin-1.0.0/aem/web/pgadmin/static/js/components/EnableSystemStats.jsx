/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { Box, Typography, makeStyles } from '@material-ui/core';
import { DefaultButton, PgIconButton, PrimaryButton } from './Buttons';
import CloseIcon from '@material-ui/icons/Close';
import CheckIcon from '@material-ui/icons/Check';
import DeleteIcon from '@material-ui/icons/Delete';
import InfoIcon from '@material-ui/icons/InfoRounded';
import HelpIcon from '@material-ui/icons/HelpRounded';
import Loader from 'sources/components/Loader';
import getApiInstance from 'sources/api_instance';
import gettext from 'sources/gettext';
import { set } from 'lodash';


const useDialogStyles = makeStyles((theme) => ({
    root: {
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        position: 'relative',
    },
    body: {
        padding: '1em',
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
        position: 'absolute',
        bottom: 0,
        width: '100%',
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

export default function EnableSystemStats(props) {
    const { onClose, serverId, pgAdmin } = props;
    const [loaderText, setLoaderText] = useState();
    const [systemStatsExists, setSystemStatsExists] = useState(false);
    const classes = useDialogStyles();
    const api = getApiInstance();


    useEffect(() => {
        setLoaderText('Loading...');
        api.get(`/dashboard/check_extension/system_statistics/${serverId}`)
            .then((res) => {
                setSystemStatsExists(res?.data?.ss_present)
                setLoaderText('');
            }).catch((error) => {
                pgAdmin.Browser.notifier.error(error?.response?.data);
            })
    }, [])

    const enableSystemStats = async () => {
        try {
            const sid = serverId
            const res = await api.get(`/dashboard/enable_system_stats/system_statistics/${sid}`);
            pgAdmin.Browser.notifier.success(res?.data)
            onClose();
        } catch (error) {
            pgAdmin.Browser.notifier.error(error?.response?.data)
        }
    }

    const disableSystemStats = async () => {
        try {
            const sid = serverId
            const res = await api.get(`/dashboard/disable_system_stats/system_statistics/${sid}`);
            pgAdmin.Browser.notifier.success(res?.data)
            onClose();
        } catch (error) {
            pgAdmin.Browser.notifier.error(error?.response?.data)
        }
    }

    const onHelp = () => {
        window.open('https://techsupport.skaiworldwide.com/', '_blank');
    };

    return (
        <Box className={classes.root}>
            <Loader message={loaderText} />
            <Box className={classes.body}>
                <Typography variant="body2">
                    {gettext(systemStatsExists ? 'Are you sure you want disable System Stats.' : 'This will enable the System Stats.')}
                </Typography>
            </Box>
            <Box className={classes.footer}>
                <Box>
                    <PgIconButton
                        data-test="sql-help"
                        icon={<InfoIcon />}
                        onClick={onHelp}
                        className={classes.buttonMargin}
                        title="SQL help for this object type."
                    />
                    <PgIconButton
                        data-test="dialog-help"
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
                    <PrimaryButton
                        data-test="Close"
                        startIcon={systemStatsExists ? <DeleteIcon /> : <CheckIcon />}
                        onClick={systemStatsExists ? disableSystemStats : enableSystemStats}
                        className={classes.buttonMargin}
                    >
                        {gettext(systemStatsExists ? 'Disable System Stats' : 'Enable System Stats')}
                    </PrimaryButton>
                </Box>
            </Box>
        </Box>
    );
}
