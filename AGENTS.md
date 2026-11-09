# ONIX parser and differ

Build two programs that read the ONIX for Books messages sent by the Elibri API
(ONIX 3.1):

- **parser**: one ONIX message → the message as JSON.
  Spec: `onix_parser_fixtures/README.md`.
- **differ**: two versions of one product's ONIX → the list of changes as JSON.
  Spec: `onix_diff_fixtures/README.md`.

They are independent: the differ compares XML items, never parser output, so
each can be built, tested and shipped alone. Use the language you were asked
for, and keep the code outside the two fixture folders.

## The contract

The READMEs are the spec and the cases prove it. Every field, path and rule is
in the README; a case only exercises one.

| README | Normative sections | Background only |
|---|---|---|
| parser | Layout, Using the cases as tests, Parsing rules, Output | Where the data comes from, Differences from elibriPHP |
| differ | Layout, Comparison rules, Using the cases as tests, Change types in the cases | Where the data comes from |

The code derives everything from the ONIX content and, for the parser,
`code_lists.json`. It must work on records it has never seen, so case ids,
record references and file names stay out of it.

## Steps

Do these for each component you were asked to build.

1. **Read the normative sections in full** before writing code. Done when you
   can name the rule behind any field of an `expected.json` you open.
2. **Expose the command** the runner calls; `tools/check.py --help` has the
   contract. On success it exits 0 and stdout holds only the JSON. The parser
   needs `code_lists.json` at runtime for its `*_name` and Polish description
   fields, so ship a copy with it or embed it.
3. **Get a tracer bullet through.** Run one small case end to end:
   `tools/check.py parser --only empty-message -- <your command>` or
   `tools/check.py diff --only identical -- <your command>`. Done when it
   passes.
4. **Make the runner green one family at a time.** Follow the order of the
   README, use `--only TEXT` to focus, fix the rule rather than the case, and
   rerun the whole suite after each family.
5. **Validate field names.** For the parser, check output against `$defs/product`
   in `onix_parser_fixtures/expected.schema.json`; it lists every field of every
   object and forbids the rest. Done when no output violates it.
6. **Finish** when the runner prints `N/N cases pass` for every case of the
   component, exits 0, and step 5 is clean.

## Rules

- `onix_parser_fixtures/` and `onix_diff_fixtures/` are read-only. When a case
  contradicts its README, stop and report the case id, the README rule and the
  expected value: the spec and the cases are corrected together, at their
  source.
- Whitespace in the XML files is data, and `.gitattributes` keeps it byte-exact.
  Read them as UTF-8 bytes with no newline translation.
