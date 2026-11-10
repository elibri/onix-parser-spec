# ONIX parser and differ specification

Specification and language-neutral test cases for reading the ONIX for Books
messages sent by the Elibri API (ONIX 3.1). Use them to build an integration in
any language, by hand or with a coding agent. The HTTP API itself (endpoints,
authentication, queues) is described in its OpenAPI specification:
<https://www.elibri.com.pl/doc/metadata.yaml>.

| Path | Contents |
|---|---|
| `AGENTS.md` | Step-by-step brief for an implementing agent |
| `onix_parser_fixtures/` | Parser spec (`README.md`), JSON Schema of the output, code lists and cases (`onix.xml`, `expected.json`) |
| [`onix_parser_fixtures/FIELDS.md`](onix_parser_fixtures/FIELDS.md) | What each field of the parser output means, with examples |
| `onix_diff_fixtures/` | Differ spec (`README.md`) and cases (`before.xml`, `after.xml`, `expected.json`) |
| `tools/check.py` | Test runner (Python 3, no dependencies) |

## Rust implementation

The two commands build their Rust binaries with Cargo and print JSON to stdout:

```sh
bin/onix-parse message.xml
bin/onix-diff before.xml after.xml
```

Rust and Cargo (edition 2024, Rust 1.88 or newer) are required. The first build
fetches the dependencies pinned in `Cargo.lock`. Implementation and embedded
code lists are in `src/`; the differ compares XML independently of the parser.

```sh
tools/check.py parser -- bin/onix-parse
tools/check.py diff -- bin/onix-diff
cargo test
cargo clippy --all-targets -- -D warnings
```

## Example prompt

To build an integration with a coding agent, open it in this repository and
adjust the language and paths:

```
Read AGENTS.md and follow it. Build the ONIX parser and the differ in Python 3.12,
under src/, with two commands: bin/onix-parse and bin/onix-diff. Add no code to
the fixture folders.

You are done when `tools/check.py parser -- bin/onix-parse` and
`tools/check.py diff -- bin/onix-diff` pass every case. If a case contradicts its
README, stop and report it instead of working around it.
```

## Testing an implementation

Your program is called as a command and prints JSON on stdout:

```
tools/check.py parser -- ./my-parser                # my-parser onix.xml
tools/check.py diff -- ./my-differ                  # my-differ before.xml after.xml
tools/check.py parser --only contributor -- ./my-parser
```

The runner exits 0 when every case passes.

## Recommended architecture

One way to store what the API sends, shown for PostgreSQL; adapt it to your
stack. Keep the raw ONIX as the source of truth and treat the JSON as something
you can rebuild, so a new parser version only needs a re-parse. Query `data`, and
compare `onix` to find what changed.

```sql
CREATE TABLE elibri_data (
  record_reference text PRIMARY KEY,
  onix             text NOT NULL,   -- one-product ONIX message, as received
  data             jsonb NOT NULL,  -- parser output for this product
  received_at      timestamptz NOT NULL
);
CREATE INDEX elibri_data_data_idx ON elibri_data USING gin (data jsonb_path_ops);

CREATE TABLE elibri_changes (
  id               bigserial PRIMARY KEY,
  record_reference text NOT NULL,
  changes          jsonb NOT NULL,  -- differ output
  received_at      timestamptz NOT NULL
);
CREATE INDEX elibri_changes_record_idx ON elibri_changes (record_reference, received_at);
```

For each product in a batch from the `meta` queue, in one transaction:

1. Parse it.
2. If a row already exists, run the differ on the stored and the new ONIX.
3. If the differ reports changes, insert them into `elibri_changes`.
4. Insert or update the row in `elibri_data`.

The diff has to run here: once the row is updated, the previous version is gone.

- **Split the batches.** `POST /api/v1/queues/{queue_name}/pop` returns up to 30
  products in one message, and the differ takes exactly one `<Product>` per
  message. Store each product as its own message.
- **Save a batch before doing anything slow.** `pop` removes the products from the
  queue. After a failure, `GET /api/v1/queues/{queue_name}/last_pop` returns the
  last batch again. Processing a product twice is harmless: the differ ignores
  datestamps and reports no changes.
- **Handle the `stocks` queue separately.** It returns only `RecordReference` and
  stock and price data, so it must not overwrite the full ONIX in `onix`.
- **Read each queue with one consumer at a time.** Concurrent `pop` requests get
  an HTTP 429.
- **Use `text` for the `onix` column.** It keeps the document exactly as received,
  and PostgreSQL's `xml` type cannot be compared for equality.
- **Keep deleted products.** A record with `NotificationType` `05` stays in the
  table, with `current_state` set to `deleted`.

Fields you query constantly, such as `isbn13` or `current_state`, can become
ordinary indexed columns later.
