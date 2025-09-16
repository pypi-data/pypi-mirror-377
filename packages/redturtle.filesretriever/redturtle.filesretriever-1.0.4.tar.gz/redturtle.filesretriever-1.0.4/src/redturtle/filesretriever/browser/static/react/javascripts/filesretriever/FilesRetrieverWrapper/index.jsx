import React, { useContext } from 'react';
import { ApiContext } from '../../ApiContext';
import SearchForm from '../SearchForm';
import FilesListWrapper from '../FilesListWrapper';

import './index.less';

const FilesRetrieverWrapper = () => {
  const { fetchApi } = useContext(ApiContext);
  return (
    <React.Fragment>
      <SearchForm
        onSubmit={params =>
          fetchApi({ endpoint: 'files-list', params, method: 'POST' })
        }
      ></SearchForm>
      <FilesListWrapper></FilesListWrapper>
    </React.Fragment>
  );
};
export default FilesRetrieverWrapper;
