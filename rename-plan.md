# Plan a Batch Rename Without Touching the Files

*Personal portfolio example prepared with OpenAI Codex. All filenames are invented. The accompanying commands were tested locally on Windows with CPython 3.12.14. This is educational work, with no client deployment or performance claim.*

Removing a prefix from a list of filenames looks simple until one of the proposed names already exists. Before writing a renaming loop, make the decisions visible in a table. A small planning function can show which names would change, which stay the same, and which require attention.

The example here removes one leading `draft-` prefix. It reads a JSON list and prints a plan. It does not walk a directory, rename a file, or restart anything. That separation lets us inspect the naming rule without giving the example permission to change our working files.

## Define what the plan means

The [complete implementation](rename_plan.py) takes a list of unique, nonempty strings. Its comparison policy is exact and case-sensitive. It removes the prefix only when it appears at the start, and removes it once.

Those choices are part of the contract. `my-draft-file.txt` stays unchanged. `draft-draft-note.txt` proposes `draft-note.txt`. The planner preserves the rest of each string, including its extension and non-Latin characters.

Each row receives one of three states:

- `ready`: the proposed target is nonempty and is absent from the original name list under the chosen comparison policy.
- `unchanged`: the source does not start with the prefix.
- `blocked`: removing the prefix produces an empty string or an already occupied target.

Here, `ready` describes a result of the model. Applying a plan to a real filesystem would require additional checks for that filesystem's naming rules, comparison behavior, permissions, and current state. This example deliberately ends at review.

## Keep the original names in view

A useful implementation starts by collecting the source names into a set:

```python
occupied = set(names)
target = source[len(prefix):] if source.startswith(prefix) else source
```

The set represents the names that exist at the beginning of the exercise. We keep that reference stable while evaluating every row.

Consider these two invented inputs:

```text
draft-report.txt
report.txt
```

The first string proposes `report.txt`, which is already occupied. The planner blocks that change and leaves the second row unchanged. It does not choose a new suffix, overwrite the existing name, or quietly omit either row from the result.

Another case is less obvious:

```text
draft-draft-note.txt
draft-note.txt
```

The second row could propose `note.txt`, but the first row still targets an original source name. This planner blocks the first row. It does not schedule dependent moves or temporarily clear a destination. A reader can see that restriction in the output instead of discovering an ordering assumption after files have moved.

## Run the supplied example

The [fixture](names.synthetic.json) contains nine invented names. From the directory containing the scripts, run:

```shell
python -X utf8 rename_plan.py names.synthetic.json
```

The command prints every source, proposed target, status, and reason. Its summary is:

```json
{"ready": 4, "unchanged": 2, "blocked": 3}
```

The buckets account for all nine inputs: **4 + 2 + 3 = 9**. The four ready proposals are `plan.csv`, `note.txt`, `茶.txt`, and `map.csv`. Two names lack the leading prefix. The three blocked proposals cover an occupied report name, an occupied intermediate name, and an empty target.

Keeping unchanged and blocked rows is useful. A summary containing only proposed successes would conceal whether some inputs were forgotten or rejected. The complete table supports a more useful question: can we explain the outcome for every source?

## Check the boundary cases

The [verification harness](check_samples.py) includes thirteen checks for this mechanism. It checks the nine-row result, existing destinations, the conservative dependent-move rule, one-prefix removal, an empty target, non-Latin text, and unchanged input data. It also checks a prefix in the middle of a name and verifies that the ready targets are unique and unoccupied within this model.

An explicit case-sensitivity check is especially useful. `Report.txt` and `report.txt` are different strings under this contract. Recording that behavior makes the model's limits visible; it does not establish how any particular disk will treat those names.

Invalid inputs have their own checks. Duplicate source names, nonstring entries, and an empty prefix are rejected rather than turned into partially usable plans. The full bundle adds configuration-review checks and command checks, for thirty passing assertions in the recorded run. See [validation.json](validation.json) for the named results and runtime.

Both documented commands were also executed as subprocesses. The fixture files retained their SHA-256 hashes after those runs. The test report establishes the behavior of these small examples; it does not establish cross-platform filesystem safety.

The planning output is a review artifact. A real renaming tool would need to recheck conditions immediately before applying changes and handle failures during execution. Making that a separate operation keeps this example focused: understand the proposed transformation, account for every input, and identify the rows that need a decision.

Source for JSON input/output behavior: [Python 3.12 json documentation](https://docs.python.org/3.12/library/json.html). The planning algorithm, fixtures, explanations, and checks are original Codex-assisted work.
