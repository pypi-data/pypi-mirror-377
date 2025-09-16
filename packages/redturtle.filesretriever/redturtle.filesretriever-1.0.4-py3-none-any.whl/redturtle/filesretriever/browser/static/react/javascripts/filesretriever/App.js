import React, { useState } from 'react';
import TranslationsWrapper from '../TranslationsContext';
import ApiWrapper from '../ApiContext';
import FilesRetrieverWrapper from './FilesRetrieverWrapper';
import './App.less';

const App = () => {
  const endpoint = 'files-list';


  return (
    <TranslationsWrapper>
      <ApiWrapper endpoint={endpoint}>
        <FilesRetrieverWrapper />
      </ApiWrapper>
    </TranslationsWrapper>
  );
};
export default App;
