/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2024, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////

/* The standard theme */
import { createTheme } from '@material-ui/core/styles';
import { alpha, darken } from '@material-ui/core/styles/colorManipulator';

export default function (basicSettings) {
  return createTheme(basicSettings, {
    palette: {
      default: {
        main: '#fff',
        contrastText: '#222',
        borderColor: '#bac1cd',
        disabledBorderColor: '#bac1cd',
        disabledContrastText: '#222',
        hoverMain: '#ebeef3',
        hoverContrastText: '#222',
        hoverBorderColor: '#bac1cd',
      },
      primary: {
        main: '#00197f',
        light: '#c3cfe2',
        contrastText: '#fff',
        hoverMain: darken('#bac1cd', 0.25),
        hoverBorderColor: darken('#dde0e6', 0.25),
        disabledMain: '#f3f5f9',
      },
      secondary: {
        main: '#00197f',
        buttonColor: '#FBCB09',
      },
      success: {
        main: '#049940',
        light: '#d0efde',
        contrastText: '#fff',
      },
      error: {
        main: '#CC0000',
        light: '#FAECEC',
        contrastText: '#fff',
      },
      warning: {
        main: '#f9a806',
        light: '#f9ebdc',
        contrastText: '#000',
      },
      info: {
        main: '#fde74c',
      },
      grey: {
        200: '#f3f5f9',
        400: '#ebeef3',
        600: '#bac1cd',
        800: '#848ea0',
      },
      text: {
        primary: '#000',
        muted: '#646B82',
      },
      checkbox: {
        disabled: '#ebeef3',
      },
      background: {
        paper: '#fff',
        default: '#fff',
      },
    },
    custom: {
      icon: {
        main: '#fff',
        contrastText: '#222',
        borderColor: '#bac1cd',
        disabledMain: '#fff',
        disabledContrastText: '#222',
        disabledBorderColor: '#bac1cd',
        hoverMain: '#ebeef3',
        hoverContrastText: '#222',
      },
    },
    otherVars: {
      reactSelect: {
        padding: '5px 8px',
      },
      borderColor: '#dde0e6',
      loader: {
        backgroundColor: alpha('#090d11', 0.6),
        color: '#fff',
      },
      errorColor: '#E53935',
      inputBorderColor: '#dde0e6',
      inputDisabledBg: '#f3f5f9',
      headerBg: '#fff',
      activeBorder: '#FBCB09',
      activeColor: '#FBCB09',
      tableBg: '#fff',
      activeStepBg: '#326690',
      activeStepFg: '#FFFFFF',
      stepBg: '#ddd',
      stepFg: '#000',
      toggleBtnBg: '#000',
      editorToolbarBg: '#ebeef3',
      qtDatagridBg: '#fff',
      qtDatagridSelectFg: '#222',
      cardHeaderBg: '#fff',
      emptySpaceBg: '#ebeef3',
      textMuted: '#646B82',
      erdCanvasBg: '#fff',
      erdGridColor: '#bac1cd',
      explain: {
        sev2: {
          color: '#222222',
          bg: '#FFEE88',
        },
        sev3: {
          color: '#FFFFFF',
          bg: '#EE8800',
        },
        sev4: {
          color: '#FFFFFF',
          bg: '#880000',
        },
      },
      schemaDiff: {
        diffRowColor: '#fff9c4',
        sourceRowColor: '#ffebee',
        targetRowColor: '#fbe3bf',
        diffColorFg: '#222',
        diffSelectFG: '#222',
        diffSelCheckbox: '#d6effc',
      },
    },
  });
}
