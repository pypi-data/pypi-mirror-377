import axios from 'axios';

const apiFetch = ({ url, params, method }) => {
  if (!method) {
    method = 'GET';
  }
  var headers = { Accept: 'application/json' };

  return axios({
    method,
    url,
    params: method == 'GET' ? params : null,
    data: ['POST', 'PATCH'].indexOf(method) >= 0 ? params : null,
    headers,
  });
};

export default apiFetch;
