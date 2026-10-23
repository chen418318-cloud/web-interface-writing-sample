# Review a JSON Configuration Change Before a Restart

*Personal portfolio example prepared with OpenAI Codex. All settings and values are invented. The code was tested locally on Windows with CPython 3.12.14. No application configuration was changed and no service was restarted.*

A configuration review needs more than a list of unequal values. A missing setting, an explicit `null`, and the number `0` can represent different decisions. The review output should preserve those distinctions so that someone who understands the application can decide what to do next.

This example compares two small, flat JSON objects. It produces a table of added, removed, changed, and unchanged keys. It helps explain a proposed update without applying it.

## Separate presence from value

Suppose an invented configuration contains:

```json
{"support_note": null}
```

The key exists and its value is null. Compare that with an empty object, where the key does not exist at all.

A tempting implementation uses `before.get(key)` and `after.get(key)`. With the usual default, both a missing key and an explicit null can appear as Python `None`. That removes information we need to explain a change.

The [complete script](config_diff.py) checks membership first:

```python
was = key in before
now = key in after
```

Each side of a review row then carries a `present` flag. It contains a value and a kind only when the key exists. Removing an explicit null therefore looks like this:

```json
{
  "before": {"present": true, "value": null, "kind": "null"},
  "after": {"present": false}
}
```

The absent side does not acquire an invented null value. This lets a reader distinguish removing a setting from assigning a value to it. The script does not decide whether those operations mean the same thing to the application; that question belongs to the application's configuration contract.

## Compare kinds before values

The second trap appears after parsing JSON into Python objects. In the tested runtime, this expression evaluates to true:

```python
False == 0
```

That behavior is useful in some Python operations, but a configuration reviewer may need to see a Boolean-to-number change. Comparing values alone would hide it.

The example assigns a JSON-oriented kind to each supported value: null, Boolean, number, or string. A row is unchanged only when the kinds match and the values compare equal. Under this rule, `false` becoming `0` is a change.

The number category intentionally groups Python integers and floats. The fixture treats `3` becoming `3.0` as unchanged. This is a review policy, not proof that every configuration schema accepts both forms. An application requiring integers needs a schema check in addition to this table.

The implementation accepts flat objects with scalar values and rejects nested objects, arrays, and nonfinite numbers. Keeping that boundary small makes the example easier to inspect. A recursive configuration tool would need additional decisions about paths, array order, and the meaning of a changed element.

## Read the complete result

Run the supplied fixtures from the directory containing the scripts:

```shell
python -X utf8 config_diff.py before.synthetic.json after.synthetic.json
```

The command prints a row for each key in the union of both objects. The recorded result is:

| Key | Result | Reason to inspect it |
| --- | --- | --- |
| `include_archived` | changed | Boolean `false` became number `0` |
| `legacy_mode` | removed | A previously present string is absent |
| `max_retries` | unchanged | Both values are the same number under this policy |
| `new_hint` | added | A newly present key has an explicit null value |
| `support_note` | removed | The old null-valued key is now absent |
| `theme` | changed | `light` became `dark` |

The summary accounts for all six keys: **1 added + 2 removed + 2 changed + 1 unchanged = 6**. Keeping the unchanged row helps demonstrate that the comparison covered the whole union rather than printing only the changes it happened to notice.

The keys are sorted for repeatable review output. That ordering does not describe the application's load order or the original formatting of either JSON file.

## Test the reviewer's assumptions

The [verification harness](check_samples.py) includes twelve checks for this mechanism. They cover the six-key summary, Boolean-versus-number changes, the chosen number policy, added and removed nulls, absent-side representation, stable ordering, and unchanged input objects. Unsupported shapes and nonfinite numbers have explicit rejection checks. The harness also records the original `False == 0` behavior that motivated the type check.

Even the input-preservation check needs care. Ordinary Python container equality could overlook a Boolean-to-number mutation for the same reason. The harness compares JSON serializations of saved input copies to preserve that distinction in its own check.

The bundle's recorded run passed thirty assertions: thirteen for rename planning, twelve for configuration review, and five for the two command invocations and unchanged input-file hashes. These are bounded offline checks using invented data. They establish neither production schema compatibility nor application behavior after loading the settings.

Use the output to ask precise questions. Was that null deliberately removed? Should the Boolean remain a Boolean? Does the application's schema require an integer? The table preserves the evidence for those decisions while leaving the actual configuration and running service untouched.

References: [Python 3.12 json documentation](https://docs.python.org/3.12/library/json.html), [synthetic before file](before.synthetic.json), [synthetic after file](after.synthetic.json), and [actual verification report](validation.json). The script, fixtures, explanations, and checks are original Codex-assisted work.
