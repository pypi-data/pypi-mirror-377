import React, { useState } from 'react';

const TitleRow = ({ row, index, updateTextRow }) => {
  const { text, created, ploneUrl } = row;

  if (created === true) {
    return (
      <a href={ploneUrl} target="_blank" rel="noreferrer">
        {text}
      </a>
    );
  }

  const [fieldValue, updateFieldValue] = React.useState(text);
  const [textTimeout, setTextTimeout] = useState(0);
  const delayTextSubmit = e => {
    const value = e.target.value;
    updateFieldValue(value);

    if (textTimeout) {
      clearInterval(textTimeout);
    }
    const timeout = setTimeout(() => {
      updateTextRow({ text: value, index });
    }, 1000);
    setTextTimeout(timeout);
  };

  return <input type="text" value={fieldValue} onChange={delayTextSubmit} />;
};
export default TitleRow;
