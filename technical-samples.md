# Two personal technical-writing samples

These are original educational samples prepared with OpenAI Codex. All inputs are synthetic. They are personal portfolio examples, with no client work, commission, or income claimed.

- [Plan a Batch Rename Without Touching the Files](rename-plan.md) explains a read-only prefix-removal planner and its comparison limits.
- [Review a JSON Configuration Change Before a Restart](config-diff.md) explains presence, null, and type-aware scalar comparisons.

The recorded run used CPython 3.12.14 on Windows. Thirty named assertions passed: 13 rename-planner checks, 12 configuration-review checks, and 5 command/input-file checks. Two CLI commands were actually executed; neither changed its input files.

Run the examples with a local Python 3.12 installation:

```shell
python -X utf8 rename_plan.py names.synthetic.json
python -X utf8 config_diff.py before.synthetic.json after.synthetic.json
```

To reproduce the verification, which writes only generated reports inside this sample directory:

```shell
python -X utf8 check_samples.py
```

The mechanisms perform no rename, configuration update, service restart, account action, or network request. Their supported input shapes and comparison policies are described in the articles and source files.

The technical reference used while preparing the JSON example is the [official Python 3.12 json documentation](https://docs.python.org/3.12/library/json.html). These samples use Python's standard library and do not include copied third-party prose or code.

