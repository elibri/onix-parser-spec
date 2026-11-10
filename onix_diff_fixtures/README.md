# ONIX diff fixtures

Test cases for a program that compares two versions of the ONIX record of **one
product** and reports what changed. Each case is a pair of ONIX 3.1 files, one
from before a change and one from after it, plus the list of changes a differ is
expected to report.

The differ is built on the parser of `../onix_parser_fixtures`: it parses both
files and compares the two parsed products. Every change is named after a
parser field and holds parser values, so a change and the parser output have
the same structure.

The folder does not depend on any language. You can copy it into any repository and write the
differ in any language. This README is the specification: an implementation
that follows the rules below produces exactly the `changes` in every
`expected.json`.

## Layout

```
onix_diff_fixtures/
├── README.md                 this file - format and comparison rules
├── expected.schema.json      JSON Schema of expected.json
├── cases.json                index: id, title and expected change types of every case
└── cases/
    └── price-changed/
        ├── before.xml        ONIX message before the change
        ├── after.xml         ONIX message after the change
        └── expected.json     what changed
```

### expected.json

| key                | meaning |
|--------------------|---------|
| `id`               | folder name, a short name of the change |
| `title`            | one-line name of the change |
| `description`      | what happened to the product, in business terms |
| `product.kind`     | `printed_book`, `preorder_book`, `ebook`, `audiobook`, `board_game`, `puzzle`, `map` or `open_access_book` (the base product the case was made from) |
| `product.record_reference` | the product's `record_reference` |
| `changes`          | **the assertion**: the changes a differ must report (see [Output](#5-output)) |

## Where the data comes from

The cases were made with real records and the real ONIX generator of Elibri.
For each case a product's ONIX is rendered, one change is applied, and it is
rendered again.

The changes follow what publishers edit in practice. The most frequent edits are Thema codes, state changes,
attachments, contributors, texts, licence dates, titles, prices, languages,
series and publication dates. The less frequent ones are dimensions, imprint,
exclusive distribution and file formats. A few cases combine
edits that are often made together (new edition: edition statement + price +
date).

The other cases cover every other product attribute that reaches the ONIX
record: they were found by walking the product edit forms (basic data, trade
data, texts, attachments, categories, files) and the ONIX generator, one case
per kind of change - identifiers, format details, toy safety, titles and
cycles, every part of a contributor, edition, languages, extent, subjects,
texts, images and widgets, publisher data, dates, sales rights, related
products, stock and prices. The `contributor-isni-*`, `contributor-viaf-*`,
`contributor-relinked-to-another-person` and `contributor-marked-misspelled`
cases change only a contributor's ISNI or VIAF while the name stays the same. Some cases show cascades (renaming the
publisher changes three fields; changing the author's name in one edition breaks
the facsimile relation to the other one). Six cases report no change at all.

Five cases change several sections in one edit, as a publisher does in one
session: `preorder-published-with-final-data`, `ebook-metadata-refreshed`,
`board-game-second-edition`, `printed-book-reprinted` and
`ebook-translator-and-cover-added`.

Base products: a printed picture book (`printed_book`), a pre-order history
book (`preorder_book`), an EPUB+MOBI e-book (`ebook`), an MP3 audiobook
(`audiobook`), a board game with toy safety warnings (`board_game`), a jigsaw
puzzle (`puzzle`), a road map (`map`) and an open-access e-book under a
Creative Commons licence (`open_access_book`). Links point to `https://www.elibri.com.pl`. Checksums and sizes of
newly uploaded files are invented.

## Comparison rules

### 1. Parse

Parse `before.xml` and `after.xml` with the parser described in
`../onix_parser_fixtures/README.md`. Each message holds exactly one product;
compare those two products (the `products[0]` of each output). Everything below
refers to parser fields by their names in that README and in
`../onix_parser_fixtures/FIELDS.md`.

### 2. What is compared

Every field of the product is compared, except these:

| left out | why | compare instead |
|---|---|---|
| `record_reference` | identifies the record, never changes | – |
| `notification_type`, `publishing_status` | make up the state | `current_state` |
| `product_form`, `product_form_name` | derived from the form and its details | `onix_product_form`, `product_form_details` |

Inside objects, at any depth, three keys are left out as well, so they never
appear in a change: `datestamp`, `ai_generated_voice` (from `unnamed_persons`)
and `parsed` (from `publishing_date.date`).

The names and descriptions of a code are compared like any other field, so they
change together with their code: `product_packaging` with
`product_packaging_name` and `product_packaging_name_description`, `proximity`
with `proximity_name`, a language's `code` with `language`, and so on.

These fields are compared although the parser derives them, because
they are what a reader of the record uses:

- `cover_type`, derived from `onix_product_form` and `product_form_details`: a
  change of binding is reported in those fields and in `cover_type`.
- `issn_with_hyphens`, the `issn` written with a hyphen: an ISSN added is
  reported as `issn.added` and `issn_with_hyphens.added`.
- `premiere`, the full `publishing_date`, or the end of an exclusive sale in
  `sales_restrictions_info`: it changes with either of them, and disappears
  when the publishing date loses its day.
- `sales_restrictions`, true when there is `sales_restrictions_info`.
- `preview_exists`, true when `supporting_resources` has an online preview
  (`content_type` 16).
- `sale_restricted_to_poland`, true when `territory_countries` is just `PL`.
- `unlimited_licence`, true when there is no `licence_limited_to`: a licence
  expiry date set is reported as `licence_limited_to.added` and
  `unlimited_licence.changed`.
- `digital_formats`, the names of the e-book formats in `product_form_details`:
  a PDF format added is reported as `product_form_details.added` and
  `digital_formats.added`.
- `finishings`, `finishing_names` and `finishing_name_descriptions`, picked from
  `product_form_details`: a finishing added is reported in all four lists.
- `cover_price`, `current_price_until`, `future_cover_price`,
  `future_price_from`, `vat` and `additional_trade_information`, picked from
  `supply_details`: a price change is reported both as `supply_details.changed`
  and as a change of these fields.

Two values are equal when they are equal as JSON: strings and numbers by value,
objects key by key, lists element by element in order.

### 3. Fields

For each compared field whose value differs:

- **A single value or an object** (strings, numbers, `true`/`false`, objects
  such as `publishing_date`, `description` or `front_cover`, and
  `proprietary_identifiers`): `null` before → `<field>.added`; `null` after →
  `<field>.removed`; otherwise `<field>.changed`. So a flag going from `false` to
  `true` is `.changed`.
- **A list of plain values** (`product_form_details`, `technical_protections`,
  `edition_types`, `keywords`, `territory_countries`, `territory_regions`,
  `alternative_format_record_references`): compared as a multiset. Every value
  that is in *before* more times than in *after* is a `<field>.removed`, every
  value in *after* more times than in *before* a `<field>.added`, each with that
  one value. Order alone is never a change.
- **A list of objects** (the lists of section 4): entries are paired as below.
  A pair whose values differ is a `<field>.changed`; an unpaired *before*
  entry is a `<field>.removed`, an unpaired *after* entry a `<field>.added`.
  Each holds one entry. Order alone is never a change.

### 4. Pairing list entries

| list | identity | fallback group |
|---|---|---|
| `contributors` | `id`; when it is `null`, `role` + `person_name` | – |
| `series` | `name` | *one group* |
| `languages` | `role` + `code` | `code` |
| `thema_subjects` | `code` | *one group* |
| `publisher_categories` | `code` | *one group* |
| `names_as_subject` | `person_name` + `corporate_name` | – |
| `excerpts` | `id` | *one group* |
| `supporting_resources` | `id` | `content_type` + `mode` |
| `excerpt_infos` | `file_type` | – |
| `file_infos` | `file_type` | – |
| `supply_details` | `supplier.role` | – |

1. **By identity.** Entries whose identity values are equal are the same entry.
   If several on one side share an identity, they are paired in list order (1st
   with 1st); any surplus is unpaired.
2. **By fallback group.** An entry still unpaired is paired with an unpaired
   entry of the other side only if both are in the same group **and that group
   has exactly one entry in *before* and exactly one in *after***, counting all
   entries. *One group* means the whole list is one group. "–" means no
   fallback.

So a renamed series of a product in one series is one `series.changed`, while
replacing one Thema code among several is `thema_subjects.removed` +
`thema_subjects.added`.

### 5. Output

`changes` is a JSON array of change objects:

```json
{ "type": "toy_safety_warning.changed", "before": "Zawiera małe elementy", "after": "Dla dzieci od 3 lat" }
{ "type": "map_scale.changed", "before": 700000, "after": 750000 }
{ "type": "current_state.changed", "before": "preorder", "after": "published" }
{ "type": "keywords.added", "after": "mafia" }
{ "type": "finishings.added", "after": "B422" }
{ "type": "cover_price.changed", "before": 46.9, "after": 49.9 }
{ "type": "thema_subjects.added", "after": { "code": "FRH", "heading_texts": ["..."] } }
{ "type": "supply_details.changed",
  "changed_fields": ["prices.0.amount"],
  "before": { "supplier": { "role": "01", "...": "..." }, "prices": [{ "type": "02", "amount": 46.9, "...": "..." }], "...": "..." },
  "after":  { "supplier": { "role": "01", "...": "..." }, "prices": [{ "type": "02", "amount": 49.9, "...": "..." }], "...": "..." } }
```

- `type` is `<field>.added`, `<field>.removed` or `<field>.changed`.
- `.added` has only `after`, `.removed` only `before`, and `.changed` has both:
  the value of the field, of one list value, or of one list entry, as the
  parser gives it (without the keys left out in section 2).
- `changed_fields` is present only when both values are objects. It lists the
  full path of every difference: object keys and list positions (counted from
  0) joined with `.`, as in `prices.0.vat` or `outlet_identifier.value`.
  Objects and lists present on both sides are followed down to what differs. A
  path stops at a key or list position present on one side only (a second price
  added is `prices.1`), at two different plain values, and where an object or
  list stands against a value of another kind. Order: depth first, at each level
  the keys of `before` in their order, then the keys only in `after`, and list
  positions in order.
- Order in `expected.json`: the fields in the order of the parser output, and
  within a list: changed pairs (in *before* order), then removed, then added. A
  test harness should compare changes as an **unordered multiset**; order is
  not part of the contract.

## Using the cases as tests

For every directory in `cases/`:

1. Run your differ on `before.xml` and `after.xml`.
2. Compare the result with `expected.json` → `changes` as a multiset of JSON
   values. Changes are equal when `type`, `changed_fields` (as an ordered list),
   `before` and `after` are equal. Object keys are compared as sets, so key
   order does not matter.

If you only need a coarse classifier (e.g. "price changed", "cover changed"),
compare just the multiset of `type` values; `cases.json` lists them per case.

## Change types in the cases

The change types that occur in the cases. `cases.json` lists the types of every
case.

- `isbn13.*`, `ean.*`, `proprietary_identifiers.changed` (publisher's code, streaming ID)
- `onix_product_form.*`, `product_form_details.*` (binding, finishing, e-book formats), `cover_type.*`, `digital_formats.*`, `finishings.*`, `finishing_names.*`, `finishing_name_descriptions.*`, `product_packaging.*`, `product_packaging_name.*`, `product_packaging_name_description.*`, `technical_protections.*`, `epub_license.*`
- `number_of_pieces.*`, `players_number_to.*`, `playing_time_from.*`, `playing_time_to.*`
- `carries_ce_logo.changed`, `carries_en71_logo.changed`, `toy_safety_warning.*`, `declaration_of_conformity_url.*` (toy safety)
- `height.*`, `width.*`, `thickness.*`, `weight.*`, `map_scale.*`, `country_of_manufacture.*`, `cn_code.*`
- `series.*`, `issn.*`, `issn_with_hyphens.added`, `title.*`, `subtitle.*`, `collection_title.*`, `collection_part_number.*`, `title_eng.*`, `original_title.*`
- `contributors.*` (also changes of ISNI / VIAF alone), `no_contributor.changed`
- `edition_statement.*`, `edition_types.*`, `edition_type_names.*`, `edition_type_descriptions.*`, `languages.*`, `number_of_pages.*`, `duration.*`, `number_of_characters.*`, `number_of_illustrations.*`
- `thema_subjects.*`, `publisher_categories.*`, `keywords.*`, `names_as_subject.*`, `reading_age_from.*`, `reading_age_to.*`
- `description.*`, `short_description.*`, `table_of_contents.*`, `list_of_contents.*`, `excerpts.*`
- `front_cover.*`, `supporting_resources.*` (samples, rules, preview widget), `preview_exists.changed`, `excerpt_infos.*`, `file_infos.*`
- `imprint_id.*`, `imprint_name.*`, `publisher_name.*`, `publisher_website.*`, `city_of_publication.*`, `safety_contact.*`
- `current_state.changed` (announced, pre-order, published, postponed, cancelled, out of print, deleted)
- `publishing_date.*`, `distribution_start.*`, `licence_limited_to.*`, `unlimited_licence.changed`, `premiere.*`
- `sales_restrictions_info.*`, `sales_restrictions.changed`, `sale_restricted_to_poland.changed`, `territory_countries.*`, `territory_regions.*`, `alternative_format_record_references.*` (facsimile)
- `supply_details.*` (availability, stock, pack, supplier, prices), `cover_price.*`, `current_price_until.*`, `future_cover_price.*`, `future_price_from.*`, `vat.*`, `additional_trade_information.*`
- no change: datestamps, identical, re-serialised, reordered, internal fields, spaces the parser strips
