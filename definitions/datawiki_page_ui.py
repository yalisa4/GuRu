import pandas as pd
from shiny import ui, render, reactive
from faicons import icon_svg

# from definitions.ui_elements import file_selector

from definitions.terms_and_styles import user_input_panel_style, banner_panel


# ==========================================================================================
page_id = 'datawiki'

INPUT_FILE = 'assets/datawiki_scrape_20260629.csv'
# Read cleaned datawiki scrape

datawiki_scrape = pd.read_csv(INPUT_FILE)

col_map = {
    "period": "Period",
    "data_type": "Data type",
    "file_name": "File name",
    "wiki_path": "Location",
    "file_url": " ",
    "pi": "PI(s)",
    "other_notes": "Notes"
}

datawiki_table = datawiki_scrape[col_map.keys()].rename(columns=col_map)

download_icon = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<polyline points="7 10 12 15 17 10"/>'
        '<line x1="12" y1="15" x2="12" y2="3"/>'
        '</svg>'
    )

datawiki_table[' '] = [
        ui.HTML(f'<a href="{url}" target="_blank">{download_icon}</a>')
        if url and str(url).strip() not in ("", "nan", "None")
        else ""
        for url in datawiki_table[' ']
    ]

# datawiki_sheets = pd.read_excel('assets/DataWiki_scrape_120922.xlsx', sheet_name=None, index_col=0)
# combine all sheets to a single dataframe
# datawiki_table = pd.concat(datawiki_sheets.values()).rename(columns={
    # 'Period': 'Period', 'Type': 'Data type', 'Sub1': 'Sub-header 1', 'Sub2': 'Sub-header 2',
    # 'File': 'File name', 'PIs': 'PIs'})


def file_selector(page_id):
    file_options = list(datawiki_table['File name'].unique())

    return ui.input_selectize(id=f'{page_id}_selected_files',
                              label=ui.tooltip(ui.h6('File(s) ', icon_svg('circle-info')),
                                               'Type or select a file name. When none is selected, all files are shown.',
                                               id=f'{page_id}_files_info_tooltip',
                                               placement='right'),
                              choices=file_options,
                              selected=[],
                              multiple=True,
                              width='100%')


def period_selector(page_id):
    period_options = list(datawiki_table['Period'].unique())

    return ui.input_selectize(id=f'{page_id}_selected_periods',
                              label=ui.h6('Period'),
                              choices=period_options,
                              selected=[],
                              multiple=True,
                              width='95%')


def datatype_selector(page_id):
    datatype_options = list(datawiki_table['Data type'].unique())

    return ui.input_selectize(id=f'{page_id}_selected_datatypes',
                              label=ui.h6('Data type'),
                              choices=datatype_options,
                              selected=[],
                              multiple=True,
                              width='95%')


def datawiki_page(tab_name):
    return ui.nav_panel(" DataWiki map",
                        banner_panel,
                        # Selection pane
                        ui.div(
                            ui.layout_columns(
                                period_selector(page_id=page_id),
                                datatype_selector(page_id=page_id),
                                file_selector(page_id=page_id),
                                col_widths=(3, 3, 6),
                                gap='15px'),
                            style=user_input_panel_style),
                        # Output
                        ui.output_data_frame(id=f'{page_id}_df'),

                        icon=icon_svg('book-atlas'),
                        value=tab_name)

datawiki_table_style = [
    # Period column — short, fixed narrow width
    {'cols': [0],
     'style': {'min-width': '90px', 'max-width': '120px', 'padding-right': '4px'}},
    
    # Data type column — compact but readable
    {'cols': [1],
     'style': {'min-width': '140px', 'max-width': '160px', 'padding-right': '4px'}},
    
    # File name and location column — most important, give it maximum space
    {'cols': [2,3],
     'style': {'width': '25%', 'min-width': '300px', 'padding-right': '4px'}},
    
    # Download column
    {'cols': [4],
    'style': {'width': '5%','min-width': '10px','max-width': '20px',
             'padding': '2px 2px', 'text-align': 'center', 'overflow': 'hidden'}},

    # PIs , Notes column
    {'cols': [5,6],
     'style': {'min-width': '60px', 'max-width': '100px', 'padding-right': '4px'}},

    # All cells: prevent overlap, allow wrapping
    {'rows': None, 'cols': None,
     'style': {'white-space': 'normal', 'word-break': 'break-word',
               'vertical-align': 'top', 'padding-top': '4px', 'padding-bottom': '4px'}},
]

# Server side ==================


def filter_datawiki_table(selected_periods,
                          selected_datatypes,
                          selected_filenames,
                          table=datawiki_table):

    if len(selected_periods) > 0:
        table = table.loc[table['Period'].str.contains('|'.join(list(selected_periods)), na=False, regex=False), ]

    if len(selected_datatypes) > 0:
        table = table.loc[table['Data type'].str.contains('|'.join(list(selected_datatypes)), na=False, regex=False), ]

    if len(selected_filenames) > 0:
        table = table.loc[table['File name'].str.contains('|'.join(list(selected_filenames)), na=False, regex=False), ]

    return table


def datawiki_reactivity(input, output):

    # Update the variable table ----------------------------------------------------
    @reactive.Calc
    def _filter_datawiki_table():
        return filter_datawiki_table(selected_periods=input.datawiki_selected_periods(),
                                     selected_datatypes=input.datawiki_selected_datatypes(),
                                     selected_filenames=input.datawiki_selected_files())

    @render.data_frame
    def datawiki_df():
        # table_style = variable_table_style(_filter_variable_table())
        # table_height = variable_table_height(_filter_variable_table().shape[0])

        return render.DataTable(data=_filter_datawiki_table(),
                                selection_mode='rows',
                                width='98%', height='600px',
                                styles=datawiki_table_style)

