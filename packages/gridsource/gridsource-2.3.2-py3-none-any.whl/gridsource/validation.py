# -*- coding: utf-8 -*-

"""Validator module.
"""

import logging
import re
import shutil
import string
import tempfile
from collections import Counter, defaultdict, namedtuple
from io import StringIO
from numbers import Number
from pathlib import Path
from pprint import pprint  # used in docstrings

import jsonschema
import numpy as np
import pandas as pd
import pint
import pint_pandas as pintpandas
import simplejson as json
import yaml

from gridsource.utils import field_status, fmt_dict, safe_isnan

ureg = pint.UnitRegistry()
UNIQUENESS_SEP = " & "


Validation = namedtuple("Validation", ["df", "isok", "report"])


def yamlcat(*files):
    """concat YAML files and returns a StringIO object

    files is an iterable of possibly:
      * StringIO object
      * strings:
        - YAML content (shall begin with "---")
        - path (str) to an existing valid YAML file
        - path (Path obj) to an existing valid YAML file

    >>> f1 = StringIO('''
    ... ---
    ... _length: &length
    ...   units: mm
    ...   default: 0
    ... key1: 5
    ... ''')
    >>> f2 = '''
    ... ---
    ... key2: 15
    ... key3:
    ...   <<: *length
    ... '''
    >>> print(yamlcat(f1, f2).getvalue())
    ---
    _length: &length
      units: mm
      default: 0
    key1: 5
    key2: 15
    key3:
      <<: *length

    """
    out = StringIO()
    out.write("---")
    for i, fh in enumerate(files):
        if isinstance(fh, str):
            if fh.strip().startswith("---"):
                # YAML was passed as a text string
                fh = StringIO(fh)
            else:
                fh = open(fh)  # assume we have a path (str) to a YAML file
        elif isinstance(fh, Path):
            fh = open(fh)  # assume we have a Path to a YAML file
        out.write(fh.read().strip().strip("---"))
        fh.close()
    out.seek(0)
    return out


def load_yaml(*files, clean=True, debug=False):
    """concatenate and load yaml files
    Wrapper for:
    * yamlcat(*files)
    * yaml.load()

    if `debug` is True, return a tuple:
        (YAML dictionnary translation, YAML concatenated file)
    otherwise, return the YAML dictionnary translation

    >>> f1 = StringIO('''
    ... ---
    ... _length: &length
    ...   units: mm
    ...   default: 0
    ... key1: 5
    ... ''')
    >>> f2 = '''
    ... ---
    ... key2: 15
    ... key3:
    ...   <<: *length
    ... key4:
    ...   <<: *length
    ...   default: 1
    ... '''
    >>> load_yaml(f1, f2) == {'key1': 5,
    ...                       'key2': 15,
    ...                       'key3': {'units': 'mm', 'default': 0},
    ...                       'key4': {'units': 'mm', 'default': 1}}
    True
    """
    src = yamlcat(*files)
    try:
        specs = yaml.load(src, Loader=yaml.FullLoader)
    except yaml.scanner.ScannerError as exc:
        _, path = tempfile.mkstemp(suffix=".yaml")
        src.seek(0)
        with open(path, "w") as fp:
            shutil.copyfileobj(src, fp)
        logging.critical(f"cannot parse {fp.name} {exc}")
        raise
    if clean:
        # clean keys beginning with "_" if required
        specs = {k: v for k, v in specs.items() if not k.startswith("_")}
    if debug:
        src.seek(0)
        return specs, src.getvalue()
    return specs


def quantify_df(df, target_units, errors):
    """preprocess a dataframe assuming units strings are on first line"""
    df = df.copy()
    df.columns = pd.MultiIndex.from_tuples(zip(df.columns, df.iloc[0]))
    df = df.iloc[1:]  # drop first line which has been merged previously
    _source_units = {}  # {col: u for col, u in df.columns if isinstance(u, str)}
    _units_to_col = defaultdict(list)
    # -------------------------------------------------------------------------
    # split df between numeric / non-numeric columns
    df_num = pd.DataFrame(index=df.index)
    df_nonnum = pd.DataFrame(index=df.index)
    # -------------------------------------------------------------------------
    # test each column and column units
    for col, col_units in df.columns:
        if isinstance(col_units, str):
            # found a column with a specified units.
            # test specified units for being known by pint
            if col_units.strip() != "":
                try:
                    getattr(ureg, col_units)
                except AttributeError:
                    errors[(col, None)].append("undefined units '%s'" % col_units)
                    df_nonnum[(col, col_units)] = df[(col, col_units)]
                    continue
            # Try to convert the whole column # to numeric:
            try:
                df_num[(col, col_units)] = pd.to_numeric(df[(col, col_units)])
            except ValueError:
                errors[(col, "?")].append("cannot convert some values to numeric")
                df_nonnum[(col, col_units)] = df[(col, col_units)]
                continue
        else:
            df_nonnum[(col, col_units)] = df[(col, col_units)]
            if col in target_units:
                errors[(col, None)].append("no units specified in source file")
    # -------------------------------------------------------------------------
    # calculate source units
    for col, u in df_num.columns:
        _source_units[col] = u
        _units_to_col[u].append(col)
    if len(df_num.columns) > 0:
        df_num.columns = pd.MultiIndex.from_tuples(df_num.columns)
    if len(df_nonnum.columns) > 0:
        df_nonnum.columns = pd.MultiIndex.from_tuples(df_nonnum.columns)
    return df_num, df_nonnum, _source_units, _units_to_col


# use short units
pintpandas.PintType.ureg.formatter.default_format = "~P"


class DataFrameSchematizer:
    """
    utility class to build a schema (jsonschema) for a Pandas DataFrame

    Given a DataFrame like:

    >>> df = pd.DataFrame({ "id": {7: 0, 1: 1, 2:5},
    ...                    "name": {7: "Doe", 1: "Fante", 2: "Mercury"},
    ...                    "firstname": {7: "John", 2: "Freddy", 1:"Richard"},
    ...                    "age": {7: '42', 1: 22},
    ...                    "life_nb": {7: 5, 1: 'hg', 2: 15}})

    We can build a column-wise schema:

    >>> v = DataFrameSchematizer()
    >>> v.add_column(name='id', types='integer', unique=True, mandatory=True)
    >>> v.add_column(name='name', types='string', mandatory=True)
    >>> v.add_column(name='firstname', types='string')
    >>> v.add_column(name='age', types='integer', mandatory=False, default=0)
    >>> v.add_column(name='life_nb', types='integer', mandatory=True, maximum=4)
    >>> v._is_units  # no units declared in any column
    False

    And validate the DataFrame:

    >>> df, is_valid, errors = v.validate_dataframe(df)
    >>> pprint(errors)
    {('age', 0): ["'42' is not valid under any of the given schemas",
                  "'42' is not of type 'integer'",
                  "'42' is not of type 'null'"],
     ('life_nb', 0): ['5 is greater than the maximum of 4'],
     ('life_nb', 1): ["'hg' is not of type 'integer'"],
     ('life_nb', 2): ['15 is greater than the maximum of 4']}

    validate_dataframe returned a namedtuple:

    >>> val = v.validate_dataframe(df)
    >>> val._fields
    ('df', 'isok', 'report')
    >>> val.isok
    False

    The schema used for validation can be accessed by:

    >>> schema = v.build()
    >>> pprint(schema)
    {'$schema': 'http://json-schema.org/draft-07/schema#',
     'properties': {'age': {'items': {'anyOf': [{'type': 'integer'},
                                                {'type': 'null'}],
                                      'default': 0},
                            'type': 'array',
                            'uniqueItems': False},
                    'firstname': {'items': {'anyOf': [{'type': 'string'},
                                                      {'type': 'null'}]},
                                  'type': 'array',
                                  'uniqueItems': False},
                    'id': {'items': {'type': 'integer'},
                           'type': 'array',
                           'uniqueItems': True},
                    'life_nb': {'items': {'maximum': 4, 'type': 'integer'},
                                'type': 'array',
                                'uniqueItems': False},
                    'name': {'items': {'type': 'string'},
                             'type': 'array',
                             'uniqueItems': False}},
     'required': ['id', 'name', 'life_nb'],
     'type': 'object'}

    We can also build a basic schema and populate `DataFrameSchematizer` with it:

    >>> schema = {
    ...           'id': {'types': 'integer', 'unique': True, 'mandatory': True},
    ...           'name': {'types': 'string', 'mandatory': True},
    ...           'firstname': {'types': 'string'},
    ...           'age': {'types': 'integer', 'minimum': 0, 'default':0},
    ...           'life_nb': {'types': 'integer', 'mandatory': True, 'maximum': 4}
    ...           }

    >>> v = DataFrameSchematizer()
    >>> v.add_columns(schema)

    Or via a JSON string

    >>> schema = (
    ...   '{"id": {"types": "integer", "unique": true, "mandatory": true}, "name": '
    ...   '{"types": "string", "mandatory": true}, "firstname": {"types": "string"}, '
    ...   '"age": {"types": "integer", "minimum": 0, "default": 0}, "life_nb": {"types": "integer", '
    ...   '"mandatory": true, "maximum": 4}}')
    >>> v.add_columns(schema)
    >>> df, is_valid, errors = v.validate_dataframe(df)
    >>> pprint(errors)
    {('age', 0): ["'42' is not valid under any of the given schemas",
                  "'42' is not of type 'integer'",
                  "'42' is not of type 'null'"],
     ('life_nb', 0): ['5 is greater than the maximum of 4'],
     ('life_nb', 1): ["'hg' is not of type 'integer'"],
     ('life_nb', 2): ['15 is greater than the maximum of 4']}

    Or via a YAML string

    >>> schema = '''
    ... ---
    ... id:
    ...   types: integer
    ...   unique: true
    ...   mandatory: true
    ... name:
    ...   types: string
    ...   mandatory: true
    ... firstname:
    ...   types: string
    ... age:
    ...   types: integer
    ...   minimum: 0
    ...   default: 0
    ... life_nb:
    ...   types: integer
    ...   mandatory: true
    ...   maximum: 4
    ... '''
    >>> v.add_columns(schema)

    And validate the DataFrame:

    >>> df, is_valid, errors = v.validate_dataframe(df)
    >>> pprint(errors)
    {('age', 0): ["'42' is not valid under any of the given schemas",
                  "'42' is not of type 'integer'",
                  "'42' is not of type 'null'"],
     ('life_nb', 0): ['5 is greater than the maximum of 4'],
     ('life_nb', 1): ["'hg' is not of type 'integer'"],
     ('life_nb', 2): ['15 is greater than the maximum of 4']}
    """

    def __init__(self, meta={}):
        self.columns_specs = {}
        self.required = []
        self._is_units = False
        self._source_units = None
        self._target_units = None
        self.uniqueness_sets = defaultdict(list)
        self.xcalling = {}
        self.mandatory_if_checks = {}
        self._meta = meta

    def build(self, as_type=None):
        """build and return schema"""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
            # "required": []
        }
        for colname, desc in self.columns_specs.items():
            schema["properties"][colname] = desc
        schema["required"] = self.required
        for uniqueness_tag, columns in self.uniqueness_sets.items():
            dummy_col = UNIQUENESS_SEP.join(columns)
            schema["properties"][dummy_col] = {
                "items": {"type": "string"},
                "type": "array",
                "uniqueItems": True,
            }

        for colname, (ext_tabname, ext_colname, func) in self.xcalling.items():
            if "xcalls" not in schema:
                schema["xcalls"] = {}
            schema["xcalls"][colname] = {
                "tabname": ext_tabname,
                "colname": ext_colname,
                "func": func,
            }
        for colname, query in self.mandatory_if_checks.items():
            if "mandatory_if" not in schema:
                schema["mandatory_if"] = {}
            schema["mandatory_if"][colname] = query
        if as_type:
            if as_type == "json":
                return json.dumps(schema)
            elif as_type in ("yaml", "yml"):
                tokens = yaml.dump(schema).split("\n")
                # replace 1st line ("$schema: http://...")
                tokens[0] = "---"
                return "\n".join(tokens)
            else:
                logging.waring(f"cannot convert to {as_type=}")
        return schema

    def _add_columns_from_json(self, jsontxt):
        specs = json.loads(jsontxt)
        self.add_columns(specs)

    def _add_columns_from_yaml(self, yamltxt):
        specs = load_yaml(yamltxt)
        self.add_columns(specs)

    def add_columns_from_string(self, txt):
        """create columns checker from string. First test json, then yaml"""
        try:
            self._add_columns_from_json(jsontxt=txt)
        except:
            self._add_columns_from_yaml(yamltxt=txt)

    def add_columns(self, specs):
        if isinstance(specs, str):
            self.add_columns_from_string(specs)
            return
        # --------------------------------------------------------------------
        # specs is a dictionnary mapping DataFrame columns to its spec
        for colname, colspec in specs.items():
            self.add_column(name=colname, **colspec)

    def add_column(
        self,
        name,
        types=("integer",),
        unique=False,
        mandatory=False,
        uniqueness_id=None,
        must_exist_in=None,
        must_not_exist_in=None,
        mandatory_if=None,
        units=None,
        **kwargs,
    ):
        """add a column to the schema"""
        if isinstance(types, str):
            types = (types,)
        types = list(types)
        if mandatory:
            self.required.append(name)
        else:
            types.append("null")
        if uniqueness_id:
            self.uniqueness_sets[uniqueness_id].append(name)
        if must_exist_in:
            self.xcalling[name] = tuple(must_exist_in.split("::") + ["isin"])
        if must_not_exist_in:
            self.xcalling[name] = tuple(must_not_exist_in.split("::") + ["~isin"])
        if mandatory_if:
            self.mandatory_if_checks[name] = mandatory_if
        # ---------------------------------------------------------
        if len(types) > 1:
            items = {"anyOf": [{"type": typ} for typ in types]}
            kwargs.pop("type", None)
        else:
            items = {"type": types[0]}
        items.update(kwargs)
        ref = {
            "type": "array",
            "items": items,
            "uniqueItems": unique,
        }
        # ---------------------------------------------------------------------
        # handle units specifications
        if units:
            ref["units"] = units
            self._is_units = True

        self.columns_specs[name] = ref

    def validate_dataframe(self, df):
        """validate dataframe against self.schema():

        1. type validation
        2. units conversion
        3. default values are applied
        4. final validation
        """
        # _df_debug = df.copy()
        schema = self.build()
        validator = jsonschema.Draft7Validator(schema)
        # =====================================================================
        # 1. Early validation for typing
        # This is usefull since validation should occures at last,
        # after units conversion and holes filling.
        # If a data has the wrong type, this process would fail before reaching
        # validation
        # =====================================================================
        # ensure line#0 is first line of data
        offset = {True: -1, False: 0}
        df = df.reset_index(drop=True)
        df.index += offset[self._is_units]
        initial_without_urow = df.copy()
        if self._is_units:
            initial_without_urow = initial_without_urow.iloc[1:]
        # check **types only** before any further DataFrame transformation
        # this will catch any type error
        early_report = _validate(
            json.loads(
                json.dumps(initial_without_urow.to_dict(orient="list"), ignore_nan=True)
            ),
            validator,
            check_types=True,
        )
        # =====================================================================
        # builds multi-header from dataframes if schemas are units-aware
        # =====================================================================
        if self._is_units:
            # recover target units as specified in the validation schema
            _props = schema["properties"]
            # python >= 3.8 only
            # self._target_units = {k: v for k in _props if (v := _props[k].get("units"))}
            self._target_units = {}
            for k in _props:
                v = _props[k].get("units")
                if v:
                    self._target_units[k] = v
            # split dataframe in two parts: one that will be quantified, the other not
            # will be quantified the columns:
            #  * have a specified unit (source units)
            #  * are pd.to_numeric compliant
            df_num, df_nonnum, self._source_units, u2cols = quantify_df(
                df, self._target_units, early_report
            )
            try:
                df_num = df_num.pint.quantify(level=-1)
            except Exception as exc:
                early_report["uncatched unit error"].extend(list(exc.args))
                self._is_units = False
                df = df[1:]
        # =====================================================================
        # convert read units to schema expected units (if required)
        # =====================================================================
        if self._is_units:
            # at this point, we still have df_num and df_nonnum
            for col, units in self._target_units.copy().items():
                if col not in df_num.columns:
                    continue
                df_num[col] = df_num[col].pint.to(units)
            df = pd.concat((df_num.pint.dequantify(), df_nonnum), axis=1)
            # re-arrange columns: restrict to level 0 and reorder as initially
            df.columns = [t[0] for t in df.columns.tolist()]
            df = df[[c for c in initial_without_urow.columns]]
        # =====================================================================
        # fill empty values as requested by schema
        # =====================================================================
        _fillnas = {
            k: schema["properties"][k]["items"].get("default")
            for k, v in schema["properties"].items()
        }
        padded_columns = [
            colname for colname, value in _fillnas.items() if value == "_pad_"
        ]
        fillnas = {
            k: v for k, v in _fillnas.items() if k in df.columns and v is not None
        }
        with pd.option_context("future.no_silent_downcasting", True):
            if fillnas:
                df = df.fillna(value=fillnas).infer_objects(copy=False)
            if padded_columns:
                df = df.replace({"_pad_": np.nan}).infer_objects(copy=False)
                df[padded_columns] = df[padded_columns].ffill()
        # =====================================================================
        # build dummy columns if required by the multiple-columns uniqueness
        # =====================================================================
        dummies = []
        for uniqueness_tag, columns in self.uniqueness_sets.items():
            _df = df[columns].ffill().astype(str)
            dummy_col = UNIQUENESS_SEP.join(columns)
            dummies.append(dummy_col)  # to delete them later on
            _c = _df.apply(UNIQUENESS_SEP.join, axis=1)
            if len(_c) > 0:
                df[dummy_col] = _c
            else:
                df[dummy_col] = None
        # =====================================================================
        # lines dropping
        # =====================================================================
        _DISCARDED_ROWS = False
        if discard_col := self._meta.get("discard_column"):
            if discard_col in df:
                _DISCARDED_ROWS = True
                df = _discard_rows(df, discard_col=discard_col)
        # =====================================================================
        # second validation
        # =====================================================================
        # df -> dict -> json -> dict to convert NaN to None
        report = _validate(
            json.loads(json.dumps(df.to_dict(orient="list"), ignore_nan=True)),
            validator=validator,
            check_types=False,
            # report=early_report,
        )
        if dummies:
            df.drop(columns=dummies, inplace=True)
        report = {**early_report, **report}
        # if _DISCARDED_ROWS:
        #     breakpoint()
        val = Validation(df, len(report) == 0, dict(report))
        return val


def _is_typing_error(error):
    """check if error is type-checking error
    return True if error is type-checking related
    """
    msgs = [error.message] + [e.message for e in error.context]
    for msg in msgs:
        if "is not of type" in msg:
            return True
    return False


def _validate(document, validator, check_types=None, report=None):
    """if check_types is:
    * None (default) report everythong
    * True: will only report typing
    * False: will NOT report typing
    """
    if report is None:
        report = defaultdict(list)
    for error in validator.iter_errors(document):
        if _is_typing_error(error):
            # if error reports a type checking issue, we skip in case
            # `check_types` is False
            if check_types is False:
                continue
        elif check_types is True:
            # otherwise, for non-typing related issue, we skip if we **only**
            # want typing-related issues
            continue
        try:
            # generic regular validation catcher
            col, row, *rows = error.absolute_path
        except ValueError:
            if error.absolute_schema_path[-1] == "uniqueItems":
                non_uniques = {k for k, v in Counter(error.instance).items() if v > 1}
                col = error.absolute_schema_path[-2]
                row = "?"
                if len(non_uniques) > 1:
                    error.message = "values %s are not unique" % non_uniques
                else:
                    error.message = "value %s is not unique" % non_uniques
            else:
                report["general"].append(error.message)
                continue
        if error.message not in report[(col, row)]:
            report[(col, row)].append(error.message)
            report[(col, row)].extend([e.message for e in error.context])
    return report


def _discard_rows(df, discard_col):
    """drop rows based on discarding specs"""
    nb_rows_ini = len(df)
    # remove single discarded row
    df = df[df[discard_col] != 1]
    # remove line by group of columns values
    discarded = set()
    df_with_discard = df[~df[discard_col].isnull()]
    for ix, row in df_with_discard.iterrows():
        query = []
        for colname in row[discard_col].split(","):
            colname = colname.strip()
            value = row[colname]
            if not isinstance(value, Number):
                value = f"'{value}'"
            query.append(f"{colname}=={value}")
        query = " & ".join(query)
        discarded |= set(df.query(query).index)
    df = df.loc[sorted(set(df.index) - discarded)]
    nb_rows_final = len(df)
    logging.info(f"dropped {nb_rows_final-nb_rows_ini} rows")
    df = df.drop(columns=[discard_col])
    return df


class ValidatorMixin:
    """mixin class built on top of jsonschema"""

    def validator_mixin_init(self):
        """called by Base class __init__()"""
        self._schemas = {}
        self._meta = {}

    def get_all_units(self, key="default_units"):
        """return a dictionnary of default units"""
        props = self._schemas[key].build()["properties"]
        units = {}
        for dim, data in props.items():
            _units = data.get("units")
            if _units:
                units[dim] = _units
        return units

    def getunits(self, tabname, key=None):
        """retrieve from schema the working units. Raise KeyError the the
        column is not units-aware.

        if `key` is provided, the relevant units is returned (eg. "length" -> "mm")
        otherwise, the whole dict is returned
        """
        props = self.get(tabname, "schemas").build()["properties"]
        # python >= 3.8 only
        # units = {
        #     dim: units for dim, data in props.items() if (units := data.get("units"))
        # }
        units = {}
        for dim, data in props.items():
            _units = data.get("units")
            if _units:
                units[dim] = _units

        if key:
            return units[key]
        return units

    def getrow(self, tabname, key, search_by=None, remove_hidden_cols=True):
        """retrieve a row from any tabname, eventually sorting by `search_by`"""
        df = self.get(tabname, remove_hidden_cols=remove_hidden_cols).copy()
        if search_by:
            df.set_index(search_by, inplace=True)
        return df.loc[key]

    def getvalue(self, tabname, key, column, search_by=None, as_quantity=True):
        """retrive a cell content by intersecting row/column index

        if as_quantity is:
          * `True`: return a quantity argument *if possible*
          * `False`: return magnitude
        """
        row = self.getrow(tabname, key, search_by)
        value = row[column]
        if as_quantity:
            units = self.getunits(tabname, column)
            return value * ureg.parse_expression(units)
        else:
            return value

    def quantify(self, tabname, restrict_to_units=False):
        df = self._data[tabname].copy()
        schema = self._schemas[tabname]
        if not schema._is_units:
            raise ValueError(f"tab {tabname} is not units-aware'")
        units = {k: v for k, v in schema._target_units.items() if v}
        # add dummy rows
        dummy_row = pd.DataFrame({c: [units.get(c, "")] for c in df.columns})
        df = pd.concat((dummy_row, df))
        if restrict_to_units:
            df = df[[c for c in df.columns if c in units]]
        df.columns = pd.MultiIndex.from_tuples(zip(df.columns, df.iloc[0].fillna("")))
        df = df.iloc[1:]
        df = df.pint.quantify(level=-1)
        return df

    def convert_to(self, tabname, units=None):
        """convert units-aware dataframe to units
        units can be:
        * None: will convert to base units
        * string: eg. 'm^3'
        * a dict mapping columns to units
        """
        df = self.quantify(tabname, restrict_to_units=True)
        if units is None:
            df_c = df.pint.to_base_units()
        else:
            if isinstance(units, str):
                units = {c: units for c in df.columns}
            df_c = pd.DataFrame(
                {col: df[col].pint.to(units) for col, units in units.items()}
            )
        return df_c

    def _set_schema(self, tabname, schema):
        """assign a schema to a tab"""
        tabnames = []
        # ---------------------------------------------------------------------
        # generic tabname regex: collect _data tabnames
        if tabname.startswith("^") and tabname.endswith("$"):
            for data_tabname in self._data.keys():
                if re.match(tabname, data_tabname):
                    tabnames.append(data_tabname)
        # ---------------------------------------------------------------------
        # general case. Only one tabname to fill
        else:
            tabnames = [tabname]
        # ---------------------------------------------------------------------
        # iterate over tabnames (usually only one if no regex-tabname supplied)
        # to instanciate a DataFrameSchematizer and fill with a schema
        for tabname in tabnames:
            self._schemas[tabname] = DataFrameSchematizer(self._meta)
            self._schemas[tabname].add_columns(schema)

    def read_schema(self, *files):
        """assign a global schema by parsing the given filepath"""
        self._schemas_filepaths = tuple(files)
        schemas = load_yaml(*files)
        # ---------------------------------------------------------------------
        # process `meta` parameters, prefixed with "."
        meta = {
            k[1:]: schemas.pop(k)
            for k, v in schemas.copy().items()
            if k.startswith(".")
        }
        self._meta = meta
        for tabname, schema in schemas.items():
            try:
                self._set_schema(tabname, schema)
            except Exception as exc:
                raise ValueError(f"error while setting {tabname}: {exc}")

    def _validate_tab(self, tabname):
        """validate a tab using the provided scheme"""
        if tabname not in self._schemas:
            return Validation(None, True, {})
        # if dataframe is empty, nothing to validate
        if len(self._data[tabname]) == 0:
            return Validation(self._data[tabname], True, {})
        schema = self._schemas[tabname]
        result = schema.validate_dataframe(self._data[tabname])
        # if tabname == "test_discard":
        #     breakpoint()
        return result

    def validate(self, row_reporting_offset="data", readonly=False):
        """
        iterate through all tabs and validate eachone

        `row_reporting_offset` can be used to offset rows reporting
        `readonly` is mainly usefull for testing purpose, to chain validation
        """
        # keep initial data before processing them
        if not hasattr(self, "_raw_data"):
            self._raw_data = {tabname: df.copy() for tabname, df in self._data.items()}
        ret = defaultdict(dict)
        xcallings = {}
        mandatory_if_checks = {}
        for tabname, df in self._data.copy().items():
            df, is_ok, report = self._validate_tab(tabname)
            if tabname in self._schemas:
                if xcalling := self._schemas[tabname].xcalling:
                    xcallings[tabname] = xcalling
                if mandatory_if_check := self._schemas[tabname].mandatory_if_checks:
                    mandatory_if_checks[tabname] = mandatory_if_check
            if df is None:
                # tabname not described in schema; drop it
                logging.warning(
                    'drop tab "%s" which is not described in schema.', tabname
                )
                self._data.pop(tabname)
                continue
            self._data[tabname] = df  # override with filled (fillna) dataframe
            if not is_ok:
                ret[tabname] = report
        # ---------------------------------------------------------------------
        # mandatory_if_checks
        for tabname, specs in mandatory_if_checks.items():
            df = self._data[tabname]
            for colname, check_expr in specs.items():
                required_missing_values = df.query(check_expr)[colname]
                required_missing_values = required_missing_values[
                    required_missing_values.isnull()
                ]
                for row_nb in required_missing_values.index:
                    ret[tabname][
                        (colname, row_nb)
                    ] = f"This value is mandatory for `{check_expr}`"

        # ---------------------------------------------------------------------
        # check cross-references calls
        for src_tabname, targets in xcallings.items():
            for src_colname, (target_tabname, target_colname, func) in targets.items():
                try:
                    src = self._data[src_tabname][src_colname]
                except KeyError:
                    # colname is probably missing. This may not be an issue
                    # if the given column is not mandatory
                    if (
                        self._schemas[src_tabname]
                        .columns_specs[src_colname]
                        .get("mandatory")
                    ):
                        logging.warning(
                            f"cannot check xcallings for {src_tabname}/{src_colname}."
                        )
                    continue
                else:
                    target = self._data[target_tabname][target_colname]
                    # calculating missing and applying dropna since we may allow empty value
                    if func.startswith("~"):
                        # must NOT exist in
                        overlapping = src[src.isin(target)].dropna()
                    else:
                        # must exist in...
                        missing = src[~src.isin(target)].dropna()
                report = ret[src_tabname]
                if func.startswith("~"):
                    for row_nb, _overlapping_ref in overlapping.items():
                        if (src_colname, row_nb) not in ret[src_tabname]:
                            ret[src_tabname][(src_colname, row_nb)] = []
                        ret[src_tabname][(src_colname, row_nb)].append(
                            f"'value `{_overlapping_ref}` unexpectidely found in `{target_tabname}::{target_colname}`"
                        )
                else:
                    for row_nb, _missing_ref in missing.items():
                        if (src_colname, row_nb) not in ret[src_tabname]:
                            ret[src_tabname][(src_colname, row_nb)] = []
                        ret[src_tabname][(src_colname, row_nb)].append(
                            f"'value `{_missing_ref}` not found in `{target_tabname}::{target_colname}`"
                        )
        # ---------------------------------------------------------------------
        # apply offset
        if row_reporting_offset:
            offset_ret = defaultdict(dict)
            for tabname, report in ret.items():
                for index, _ in report.items():
                    try:
                        (colname, rownb) = index
                        if rownb in (None, "?"):
                            raise ValueError("switch...")
                    except:
                        # "general" section, without row clue
                        offset_ret[tabname][index] = report[index]
                    else:
                        msgs = report[(colname, rownb)]
                        # row_reporting_offset == "spreadsheet"
                        reported_rownb = self.get_reported_rownb(
                            tabname, rownb, row_reporting_offset=row_reporting_offset
                        )
                        offset_ret[tabname][(colname, reported_rownb)] = msgs
            ret = offset_ret
        if readonly:
            # revert to initial dataframe
            self._data = {tabname: df.copy() for tabname, df in self._raw_data.items()}
        return dict(ret)

    def get_reported_rownb(self, tabname, ix, row_reporting_offset="data"):
        """return user-friendly row index"""
        if not row_reporting_offset:
            return ix
        try:
            reported_rownb = self._data[tabname].loc[ix]["__rownb_xlsx"]
        except KeyError:
            # no `__rownb_xlsx` field
            reported_rownb = "?"
        else:
            if row_reporting_offset == "data":
                is_units = len(self.getunits(tabname)) > 0
                if is_units:
                    reported_rownb -= 2
                else:
                    reported_rownb -= 1
        return reported_rownb

    def dump_template(self):
        """return list of columns ready to be dumped as XLSX template"""
        dic = defaultdict(dict)
        for tabname, schema in self._schemas.items():
            df = pd.DataFrame(
                {k: [v.get("units")] for k, v in schema.columns_specs.items()}
            )
            df.dropna(axis=0, how="all", inplace=True)
            dic[tabname]["df"] = df
            dic[tabname]["schema"] = schema.columns_specs
            dic[tabname]["required"] = schema.required
            dic[tabname]["xcalling"] = schema.xcalling
            dic[tabname]["uniqueness"] = schema.uniqueness_sets
        dic = dict(dic)
        return dic

    def _dump_xlsx_template(self, tabs=(), excluded_tabs=None):
        # -------------------------------------------------------------------------
        # eventually filter with tabs wishlist
        schemas = self._schemas.copy()
        if tabs:
            # restrict schemas to provided tabs
            schemas = {k: v for k, v in schemas.items() if k in tabs}
        else:
            # get all tabs
            tabs = list(schemas.keys())
        if excluded_tabs:
            schemas = {k: v for k, v in schemas.items() if k not in excluded_tabs}
        # -------------------------------------------------------------------------
        # check implicit tabs xcalls
        tabs = list(tabs)
        _additional_tabs = []
        for tabname, schema in schemas.items():
            for referencing_col, (
                referenced_tab,
                referenced_col,
                check_func,
            ) in schema.xcalling.items():
                if referenced_tab not in tabs:
                    logging.warning(f"add referenced {referenced_tab}")
                    _additional_tabs.append(referenced_tab)
                    tabs.append(referenced_tab)
        # update filtered schema with additional_tabs
        schemas.update(
            {k: v for k, v in self._schemas.items() if k in _additional_tabs}
        )
        return schemas

    def dump_xlsx_template(
        self, output, tabs=(), excluded_tabs=None, include_data=False
    ):
        """creates a blank XSLX spreadsheet based on provided schema"""
        data_schemas = self._dump_xlsx_template(tabs, excluded_tabs)
        cols = self.dump_template()  # get columns and attributes
        if tabs:
            cols = {k: cols[k] for k in tabs}  # reorder as required by `tabs` order
        with pd.ExcelWriter(output) as writer:
            workbook = writer.book
            # prepare formats
            default_format = workbook.add_format(fmt_dict())
            mandatory_format = workbook.add_format(fmt_dict(["mandatory"]))
            padded_format = workbook.add_format(fmt_dict(["padded"]))
            units_format = workbook.add_format(fmt_dict(["units"]))
            for tabname, data in cols.items():
                df = data["df"]
                if include_data:
                    if tabname not in self._data.keys():
                        continue
                    content = self.get(tabname)
                    if content is not None:
                        df = pd.concat((df.fillna(""), content))
                colspecs = data["schema"]
                xcallings = data["xcalling"]
                df.to_excel(
                    writer, sheet_name=tabname, startrow=1, header=False, index=False
                )
                worksheet = workbook.sheetnames[tabname]
                # -----------------------------------------------------------------
                # format header
                # worksheet.set_row(0, height=None, cell_format=mandatory_format)
                ws_has_units = {cs.get("units") for _, cs in colspecs.items()} != {None}
                _var = data_schemas.get(tabname)
                for i, colname in enumerate(df.columns):
                    try:
                        colname_status = field_status(colname, _var)
                    except KeyError:
                        continue
                    if colname_status == "default":
                        fmt = default_format
                    elif colname_status == "padded":
                        fmt = padded_format
                    elif colname_status == "mandatory":
                        fmt = mandatory_format
                    else:
                        raise ValueError(f"dont know anything about {colname_status=}")
                    # is_mandatory = colname in required
                    pattern = colspecs[colname]["items"].get("pattern")
                    default = colspecs[colname]["items"].get("default")
                    xcalling = xcallings.get(colname)
                    worksheet.write_string(0, i, colname, cell_format=fmt)
                    if ws_has_units:
                        units = df[colname].iloc[0]
                        if units and not safe_isnan(units):
                            worksheet.write_string(
                                1, i, units, cell_format=units_format
                            )
                        else:
                            worksheet.write_blank(1, i, units, cell_format=units_format)
                    cell_header = "{col}{row}".format(
                        col=string.ascii_uppercase[i], row=1
                    )
                    # -------------------------------------------------------------
                    # process comments
                    types = set((colspecs[colname]["items"].get("type"),))
                    for typ in colspecs[colname]["items"].get("anyOf", []):
                        types.add(typ["type"])
                    types.discard(None)
                    if "null" in types:
                        types.remove("null")
                        types = ["Empty"] + list(types)
                    types_str = ", ".join(types)
                    comment = f"Type(s): {types_str}"
                    if colspecs[colname]["uniqueItems"]:
                        comment += f"\nMust be Unique"
                    if pattern:
                        comment += f"\nPattern: {pattern}"
                    if xcalling:
                        comment += f"\ncross-ref: {xcalling[0]}/{xcalling[1]}"
                    if default is not None:
                        if isinstance(default, str):
                            comment += f'\ndefault: "{default}"'
                        else:
                            comment += f"\ndefault: {default}"
                    if enum := colspecs[colname]["items"].get("enum"):
                        comment += f"\nOne value of {enum}"
                    worksheet.write_comment(
                        cell_header,
                        comment,
                        {
                            "author": "numeric-GmbH",
                            "color": "#b3ceeb",
                            "visible": False,
                            "x_scale": 2,
                            "font_size": 10,
                        },
                    )
                if ws_has_units:
                    worksheet.freeze_panes(2, 1)
                else:
                    worksheet.freeze_panes(1, 1)
                # -----------------------------------------------------------------
                # autofit
                worksheet.autofit()
        logging.info(f"finilized {output}")
        return output


if __name__ == "__main__":
    import doctest

    doctest.testmod(
        optionflags=doctest.ELLIPSIS
        | doctest.IGNORE_EXCEPTION_DETAIL
        | doctest.NORMALIZE_WHITESPACE
    )
