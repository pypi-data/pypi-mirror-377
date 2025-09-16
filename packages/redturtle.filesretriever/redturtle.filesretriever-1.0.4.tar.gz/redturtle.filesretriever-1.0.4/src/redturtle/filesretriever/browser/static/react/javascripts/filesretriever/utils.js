export const getTranslations = getTranslationFor => {
  return {
    url: getTranslationFor('label_url', 'Url'),
    title: getTranslationFor('label_title', 'Title'),
    status: getTranslationFor('label_status', 'Status'),
    tableTitle: getTranslationFor('table_title_label', 'Files to import'),
    save: getTranslationFor('save_label', 'Save'),
    search: getTranslationFor('search_label', 'Search'),
    saveConfirm: getTranslationFor(
      'save_confirm_label',
      'Are you sure you want to save these files?',
    ),
    noFiles: getTranslationFor('no_files_found_label', 'No files found.'),
    singularSelected: getTranslationFor('item_selected', 'item selected'),
    pluralSelected: getTranslationFor('items_selected', 'items selected'),
    urlLabel: getTranslationFor('url_label', 'Source page.'),
    urlHelp: getTranslationFor(
      'url_help',
      'Enter the url of the page where you want to search files to import.',
    ),
    cssClassLabel: getTranslationFor('css_class_label', 'CSS Class'),
    cssClassHelp: getTranslationFor(
      'css_class_help',
      'Insert a CSS class selector that contains the list of links in source page.',
    ),
    cssIdLabel: getTranslationFor('css_id_label', 'CSS Id'),
    cssIdHelp: getTranslationFor(
      'css_id_help',
      'Insert a CSS id selector that contains the list of links in source page. This one has priority over the CSS class selector.',
    ),
  };
};
