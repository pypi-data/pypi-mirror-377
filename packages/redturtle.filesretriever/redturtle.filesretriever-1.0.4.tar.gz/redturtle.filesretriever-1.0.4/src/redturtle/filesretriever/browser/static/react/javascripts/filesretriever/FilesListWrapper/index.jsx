import React, { useState, useContext } from 'react';
import DataTable from 'react-data-table-component';
import { TranslationsContext } from '../../TranslationsContext';
import { ApiContext } from '../../ApiContext';
import { getTranslations } from '../utils';
import TitleRow from '../TitleRow';
import ReactTooltip from 'react-tooltip';

import './index.less';

const FilesListWrapper = () => {
  const getTranslationFor = useContext(TranslationsContext);
  const labels = getTranslations(getTranslationFor);
  const [toggleCleared, setToggleCleared] = useState(false);
  const [selectedRows, setSelectedRows] = React.useState([]);
  const { data, loading, updateTextRow, saveFiles } = useContext(ApiContext);

  //------------------COLUMNS----------------------
  const StatusCell = row => {
    let statusIcon = '';
    if (row.created === true) {
      statusIcon = (
        <span className="glyphicon glyphicon-ok-sign success"></span>
      );
    } else if (row.created === false) {
      statusIcon = (
        <span
          className="glyphicon glyphicon-alert error"
          data-tip={row.error}
        ></span>
      );
    }
    return (
      <div className="status">
        {statusIcon}
        <ReactTooltip place="bottom" type="dark" effect="solid" />
      </div>
    );
  };

  const columns = [
    {
      name: labels.url,
      cell: row => (
        <div>
          <a href={row.href} target="_blank" rel="noopener noreferrer">
            <span
              className="glyphicon glyphicon-link"
              data-tip={row.href}
            ></span>
          </a>
          <ReactTooltip place="bottom" type="dark" effect="solid" />
        </div>
      ),
      width: '80px',
    },
    {
      name: labels.title,
      cell: (row, index) => (
        <TitleRow
          row={row}
          index={index}
          updateTextRow={updateTextRow}
        ></TitleRow>
      ),
    },
    {
      name: labels.status,
      cell: StatusCell,
      width: '100px',
    },
  ];

  //------------------ACTIONS----------------------
  const handleRowSelected = React.useCallback(state => {
    setSelectedRows(state.selectedRows);
  }, []);

  const contextActions = React.useMemo(() => {
    const handleSave = () => {
      // eslint-disable-next-line no-alert
      if (
        window.confirm(
          `${labels.saveConfirm} \n${selectedRows
            .map(r => '> ' + r.text)
            .join('\n')}`,
        )
      ) {
        const params = { urls: selectedRows };
        saveFiles({ endpoint: 'save-files', params, method: 'POST' });
        setToggleCleared(!toggleCleared);
      }
    };

    return (
      <button
        key="save"
        onClick={handleSave}
        className="plone-btn plone-btn-info"
      >
        {labels.save}
      </button>
    );
  }, [selectedRows, toggleCleared]);

  //------------------TABLE----------------------

  return (
    <div className="files-list">
      <DataTable
        title={labels.tableTitle}
        columns={columns}
        data={data.links}
        striped={true}
        highlightOnHover={true}
        pointerOnHover={false}
        noDataComponent={labels.noFiles}
        responsive={true}
        progressPending={loading}
        selectableRows
        onSelectedRowsChange={handleRowSelected}
        clearSelectedRows={toggleCleared}
        selectableRowDisabled={row => row.created === true || row.text === ''}
        contextActions={contextActions}
        contextMessage={{
          singular: labels.singularSelected,
          plural: labels.pluralSelected,
          message: '',
        }}
      />
    </div>
  );
};
export default FilesListWrapper;
