import React, { useState, useEffect } from 'react';
import { object } from 'prop-types';

import apiFetch from './utils/apiFetch';

export const ApiContext = React.createContext({});

export const ApiProvider = ApiContext.Provider;
export const ApiConsumer = ApiContext.Consumer;

function ApiWrapper({ children }) {
  const [data, setData] = useState({});
  const [contextlUrl, setContextlUrl] = useState(null);

  const [apiErrors, setApiErrors] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleApiResponse = res => {
    if (res?.status != 204 || res?.status != 200) {
      setApiErrors(
        res
          ? { status: res.status, statusText: res.statusText }
          : { status: '404', statusText: '' },
      );
    }
  };

  const fetchApi = ({ endpoint, params = {}, method = 'GET' }) => {
    if (contextlUrl) {
      setLoading(true);
      apiFetch({
        url: contextlUrl + '/@' + endpoint,
        params,
        method,
      })
        .then(data => {
          if (data === undefined) {
            setApiErrors({ status: 500, statusText: 'Error' });
            setLoading(false);
            return;
          }
          handleApiResponse(data);
          setData(data.data);
          setLoading(false);
        })
        .catch(error => {
          setLoading(false);
          if (error && error.response) {
            setApiErrors({
              status: error.response.status,
              statusText: error.message,
            });
          }
        });
    }
  };

  const saveFiles = ({ endpoint, params = {}, method = 'GET' }) => {
    if (contextlUrl) {
      setLoading(true);
      apiFetch({
        url: contextlUrl + '/@' + endpoint,
        params,
        method,
      })
        .then(newData => {
          if (newData === undefined) {
            setApiErrors({ status: 500, statusText: 'Error' });
            setLoading(false);
            return;
          }
          handleApiResponse(newData);

          let newLinks = data.links.map(link => {
            newData.data.forEach(updatedLink => {
              if (updatedLink.href === link.href) {
                link = updatedLink;
              }
            });
            return link;
          });
          setData({ ...data, links: newLinks });
          setLoading(false);
        })
        .catch(error => {
          setLoading(false);
          if (error && error.response) {
            setApiErrors({
              status: error.response.status,
              statusText: error.message,
            });
          }
        });
    }
  };

  const updateTextRow = ({ text, index }) => {
    let updatedLinks = data.links.map((link, linkIndex) => {
      if (linkIndex === index) {
        link.text = text;
      }
      return link;
    });
    setData({ ...data, links: updatedLinks });
  };

  useEffect(() => {
    const contextlUrl = document
      .querySelector('body')
      .getAttribute('data-base-url');
    if (!contextlUrl) {
      return;
    }

    setContextlUrl(contextlUrl);
  }, []);

  // useEffect(() => {
  //   if (contextlUrl) {
  //     fetchApi();
  //   }
  // }, [contextlUrl]);

  return (
    <ApiProvider
      value={{
        fetchApi,
        saveFiles,
        data,
        contextlUrl,
        handleApiResponse,
        apiErrors,
        setApiErrors,
        loading,
        updateTextRow,
      }}
    >
      {children}
    </ApiProvider>
  );
}

ApiWrapper.propTypes = {
  children: object,
};

export default ApiWrapper;
