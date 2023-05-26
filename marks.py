import pygsheets as pygs
import pandas as pd
import re


INVISIBLE_SPACE = '\u200b'


def get_sheet(sheet_id, sheet_name):
    google_client = pygs.authorize(client_secret='credentials.json')
    spreadsheet = google_client.open_by_key(sheet_id)
    return spreadsheet.worksheet_by_title(sheet_name)


# check if tree follows rules
def check_tree(tree):
    # 0. starting category must be 'Summary'
    if tree.Category[0] != 'Summary':
        print("Starting category must be 'Summary'")
        return False
    # 1. category regex
    if not tree.Category.str.match(r'^([^#~]+(#([0-9]+)?)?)*$').all():
        print("Category doesn't match regex")
        return False
    # 2. subcategory regex
    if not tree.Subcategory.str.match(r'^([^#~]+(#([0-9]+)?)?)*([^#~]+(#([0-9]+(~[0-9]+)?)?)?)$').all():
        print("Subcategory doesn't match regex")
        return False
    # all index removed from cat and subcat for comparison
    cat_stripped = tree.Category.str.replace(r'#[0-9]+', '#', regex=True)
    subcat_stripped = tree.Subcategory.str.replace(
        r'#[0-9]+(~[0-9]+)?', '#', regex=True)
    # 3. categories must be created in previous subcategories
    for i, cat in cat_stripped[1:].items():
        if not subcat_stripped[:i].str.contains(cat).any():
            print(f"'{cat}' is referred before created in subcategory")
            return False
    # 4. back reference from subcategory to previous categories not allowed
    for i, subcat in subcat_stripped[1:].items():
        if cat_stripped[:i].str.contains(subcat).any():
            print(f"'{subcat}' back referenced a category possibly creating a loop")
            return False
    # 5. Non-Leaf nodes must be unique
    non_leaf = subcat_stripped.isin(cat_stripped).rename('NonLeaf')
    ans = pd.concat([cat_stripped, subcat_stripped, non_leaf], axis=1)
    ans = ans.set_index(subcat_stripped)
    for i in ans.index:
        cat_i = ans.Category[i]
        if type(cat_i) == pd.Series and len(cat_i.unique()) > 1 and ans.NonLeaf[i].any():
            print("Non-leaf nodes must be unique")
            return False
    # success
    return True


def create_df_from_tree(tree):
    if not check_tree(tree):
        return
    df = pd.DataFrame()

    def walk(tree, node, weight, parent, depth):
        interval_regex = r'(?<=#)[0-9]+~[0-9]+$'
        if re.search(interval_regex, node):
            # iterate over interval
            parts = re.search('#([0-9]+)~([0-9]+)$', node)
            start, end = int(parts[1]), int(parts[2])+1
            prefix = node.rsplit('#', maxsplit=1)[0]
            nodes = [f"{prefix}#{i}" for i in range(start, end)]
            for n in nodes:
                walk(tree, n, weight, parent, depth)
        else:
            # actually create a new node
            # fill in the indices if left blank
            blanks = re.findall('([^#\s]+)#[^0-9]', node)
            for blank in blanks:
                blank_esc = re.escape(blank)
                fill = re.search(fr'{blank_esc}#([0-9]+)', parent)
                if fill:
                    node = re.sub(fr'{blank_esc}#',
                                  fr'{blank}#{fill[1]}', node)
            # insert column to dataframe
            header = f"{INVISIBLE_SPACE*depth}{node}"
            full_node = f"{parent} ► {node}"
            df[full_node] = [header, weight]
            # print(f"{full_node}")
            # walk children
            # category '#' should match node '#[0-9]+' but category '#1' should only match node '#1'
            node_regexed = re.sub(
                r'#([0-9]+)', r'#(\1)?', re.escape(node)) + '$'
            children = tree[tree.Category.str.match(node_regexed)]
            for i, row in children.iterrows():
                walk(tree, tree.Subcategory[i],  tree.Weight[i], node, depth+1)
    # run inner function
    walk(tree, tree.Subcategory[0], tree.Weight[0], tree.Category[0], 0)
    return df


def extract_df_from_headers(headers):
    print(f"Extracting from marks sheet... ")
    df = pd.DataFrame()
    parents = ['Summary']
    prev_depth = -1
    for header, weight in headers:
        # print(f"{header}, ", end='')
        depth = header.count(INVISIBLE_SPACE)
        node = header.replace(INVISIBLE_SPACE, '')
        # pop if sibling or next parent
        if (delta := prev_depth - depth) >= 0:
            parents = parents[: -(delta+1)]
        # add to dataframe
        df[f"{parents[-1]} ► {node}"] = [header, weight]
        # print(f"{parents[-1]} ► {node}")
        # always append working node for future children
        parents.append(node)
        prev_depth = depth
    # print('\nExtracting complete.\n')
    return df


def init(marks_sheet_id):
    # sheets
    info_sheet = get_sheet(marks_sheet_id, 'Info')
    marks_sheet = get_sheet(marks_sheet_id, 'Marks')

    # write marks sheet from tree source
    tree = info_sheet.get_as_df(start='D1', end='F')
    df_headers_new = create_df_from_tree(tree)
    # marks_sheet.set_dataframe(df_headers_new, copy_head=False, start='G1')

    # generate dataframe from headers
    # headers_curr = marks_sheet.get_values(start='1', end='2', majdim='COLS', include_tailing_empty_rows=True, include_tailing_empty=False)[6:]
    headers_curr = marks_sheet.get_as_df(start='G1', end=(
        2, marks_sheet.cols), has_header=False, include_tailing_empty_rows=True)
    headers_curr = headers_curr.transpose().values.tolist()
    df_headers_curr = extract_df_from_headers(headers_curr)
    # marks_sheet.set_dataframe(df_headers_curr, copy_head=True, start='G2')

    # compare new vs existing tree
    # to_add = df_headers_new.columns[~df_headers_new.columns.isin(df_headers_curr.columns)]
    # to_rmv = df_headers_curr.columns[~df_headers_curr.columns.isin(df_headers_new.columns)]
    to_add_col_num = (~df_headers_new.columns.isin(
        df_headers_curr.columns)).nonzero()[0]
    print(to_add_col_num)

    # print(to_add)
    # print(to_rmv)
    # print(type(df_headers_new.columns))

    marks_curr = marks_sheet.get_as_df(start='G1', value_render='FORMULA')
    marks_curr.columns = df_headers_curr.columns

    marks_new = marks_curr.reindex(columns=df_headers_new.columns, copy=True,
                                   fill_value='', index=range(marks_sheet.rows-1) if len(marks_curr) < 2 else None)
    marks_new.iloc[0] = df_headers_new.iloc[1]

    marks_new.columns = pd.MultiIndex.from_tuples([(*col.split(' ► '), pygs.Address((0, i+7)).label)
                                                   for i, col in enumerate(df_headers_new.columns)],
                                                  names=['parent', 'child', 'sheet'])

    # set formulas
    for category, subcategory, sheet_col in marks_new:
        # print(f"{parent} -> {child} -> ")
        # check for numeric grandchildren, we might need to sum them
        if subcategory in marks_new:
            to_sum = []
            to_sum_best = []
            for subcat_child, subcat_child_col in marks_new[subcategory].columns:
                subcat_child_type: str = marks_new[subcategory,
                                                   subcat_child, subcat_child_col][0]
                # if percentage weighted, clip
                if re.match(r'[0-9.]+%', subcat_child_type):
                    to_sum.append('CLIP(' + subcat_child_col +
                                  '{sheet_row}' + ',' + subcat_child_type.replace('%', '') + ')')
                # elif must count, simply add
                elif subcat_child_type == 'must count':
                    to_sum.append(subcat_child_col + '{sheet_row}')
                # else count if best, use SUMBEST
                elif re.match(r'count if in best [0-9]+', subcat_child_type):
                    to_sum_best.append(subcat_child_col + '{sheet_row}')
                    best_k = int(re.search('[0-9]+', subcat_child_type)[0])

            if to_sum_best:
                if best_k > len(to_sum_best):
                    best_k = len(to_sum_best) - 1
                to_sum_best = 'SUMBEST(' + str(best_k) + \
                    ', {{' + ', '.join(to_sum_best) + '}})'
                to_sum.append(to_sum_best)

            # marks_new[category, subcategory, sheet_col][1] = ('= ' + ' + '.join(t.format(sheet_row=3) for t in to_sum)) if to_sum else ''
            # def formula(row): return ('= ' + ' + '.join(t.format(sheet_row=row.name+2)
            #                                             for t in to_sum)) if to_sum else None
            # end_index = None if marks_new.columns.get_loc(
            #     (category, subcategory, sheet_col)) in to_add_col_num else 2
            if marks_new.columns.get_loc((category, subcategory, sheet_col)) in to_add_col_num:
                end_index = None
            else:
                end_index = 2
            if to_sum:
                def formula(row): return (
                    '= ' + ' + '.join(t.format(sheet_row=row.name+2) for t in to_sum))
                marks_new[category, subcategory, sheet_col][1:end_index] = marks_new.iloc[1:end_index].apply(
                    formula, axis=1)

            print(subcategory, marks_new[category, subcategory, sheet_col][1])

    # PUBLISH CHANGES
    # backup before any change
    marks_sheet.copy_to(marks_sheet_id).hidden = True
    print("Backup complete")
    # set data
    marks_sheet.set_dataframe(
        df_headers_new[:1], start='G1', copy_head=False, extend=True)
    print("Headers published")
    marks_sheet.set_dataframe(marks_new, start='G2', copy_head=False)
    print("Data published")

    # set data validation
    print("Setting data validation...")
    for category, subcategory, sheet_col in marks_new:
        # check for subcategory type, might need to clip to full marks
        subcat_type = marks_new[category, subcategory, sheet_col][0]
        # print(subcat_type, ':', type(subcat_type))
        if re.match(r'[0-9.]+%', subcat_type):
            print('\t', subcategory, ' -> ', subcat_type)
            marks_sheet.set_data_validation(start=f'{sheet_col}3',
                                            end=f'{sheet_col}{marks_sheet.rows}',
                                            condition_type="NUMBER_BETWEEN",
                                            condition_values=[0, int(subcat_type.replace('%', ''))])
        elif subcat_type == 'bool':
            print('\t', subcategory, ' -> ', subcat_type)
            marks_sheet.set_data_validation(start=f'{sheet_col}3',
                                            end=f'{sheet_col}{marks_sheet.rows}',
                                            condition_type='BOOLEAN')
        elif subcat_type:
            # print('\t', subcategory, ' -> ', subcat_type)
            marks_sheet.set_data_validation(start=f'{sheet_col}3',
                                            end=f'{sheet_col}{marks_sheet.rows}')
    print("Done publishing.")


if __name__ == '__main__':
    # remove hard coded value and ask for input
    # marks_sheet_id = '1DHMw2vdguY7jt36XG5e4P9rULFYPNz-4K3s-4LxIPww'
    marks_sheet_id = input('Spreadsheet key: ')
    init(marks_sheet_id)
