# ONIX diff fixtures

Test cases for a program that compares two versions of the ONIX record of **one
product** and reports what changed. Each case is a pair of ONIX 3.1 files, one
from before a change and one from after it, plus the list of changes a differ is
expected to report.

The folder is self-contained and does not depend on any language. You can copy it into any repository and write the
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
    └── 012-price-changed/
        ├── before.xml        ONIX message before the change
        ├── after.xml         ONIX message after the change
        └── expected.json     what changed
```

### expected.json

| key                | meaning |
|--------------------|---------|
| `id`               | folder name |
| `title`            | one-line name of the change |
| `description`      | what happened to the product, in business terms |
| `product.kind`     | `printed_book`, `preorder_book`, `ebook`, `audiobook`, `board_game`, `puzzle`, `map` or `open_access_book` (the base product the case was made from) |
| `product.record_reference` | the product's `RecordReference` |
| `changes`          | **the assertion**: the changes a differ must report (see [Output](#output)) |

## Where the data comes from

The cases were made with real records and the real ONIX generator of Elibri.
For each case a product's ONIX is rendered, one change is applied, and it is
rendered again.

The changes follow what publishers edit in practice. The most frequent edits are Thema codes, state changes,
attachments, contributors, texts, licence dates, titles, prices, languages,
series and publication dates. The less frequent ones are dimensions, imprint,
exclusive distribution and file formats. A few cases combine
edits that are often made together (new edition: edition statement + price +
date). Cases 001-061 are that first selection.

Cases 062 onwards cover every other product attribute that reaches the ONIX
record: they were found by walking the product edit forms (basic data, trade
data, texts, attachments, categories, files) and the ONIX generator, one case
per kind of change - identifiers, format details, toy safety, titles and
cycles, every part of a contributor, edition, languages, extent, subjects,
texts, images and widgets, publisher data, dates, sales rights, related
products, stock and prices. Cases 166–172 change only a contributor's ISNI or VIAF (added, corrected,
removed, linked to another person, hidden for a misspelled name) while the
name stays the same. Some cases show cascades (renaming the
publisher changes five items; changing the author's name in one edition breaks
the facsimile relation to the other one). Six cases contain no change at all.

Base products: a printed picture book (`printed_book`), a pre-order history
book (`preorder_book`), an EPUB+MOBI e-book (`ebook`), an MP3 audiobook
(`audiobook`), a board game with toy safety warnings (`board_game`), a jigsaw
puzzle (`puzzle`), a road map (`map`) and an open-access e-book under a
Creative Commons licence (`open_access_book`). Links point to `https://www.elibri.com.pl`. Checksums and sizes of
newly uploaded files are invented.

## Comparison rules

### 1. Parsing

- Parse both files as XML and ignore namespaces. Elements are identified by
  their local name (the files use the default namespace
  `http://ns.editeur.org/onix/3.1/reference`).
- Each message contains exactly one `<Product>`; compare those two. `<Header>` is
  ignored (it holds the sending date, not product data).
- **Attributes are ignored** (`datestamp`, `sourcename`, `language`,
  `dateformat`, ...). The only exception is `sourcename`, which is used *for
  matching* items (see the units table) but is never reported.
- **Text normalisation:** the value of a leaf element is its text content
  (CDATA and escaped text are the same thing). Every run of XML whitespace
  (space U+0020, tab U+0009, CR U+000D, LF U+000A) is collapsed into one space,
  and the result is trimmed of those characters. Other Unicode spaces (e.g.
  no-break space U+00A0, narrow no-break space U+202F) are data and are kept
  as they are. Beware: `\s` in many regex engines (Python, JavaScript, Java with
  UNICODE_CHARACTER_CLASS) also matches Unicode spaces; case 032 catches that
  (its old description has U+202F, which the edit replaced with plain spaces).
  Values are compared as strings: `46.9` and `46.90` are different.

### 2. Units

The product is split into **items**. Every item has a *type* (e.g. `price`). The
table lists the elements that are items, by path from `<Product>`:

| type | element path from `<Product>` | identity | fallback group | context fields |
|---|---|---|---|---|
| `notification_type` | `NotificationType` | value | *one group* | |
| `deletion_text` | `DeletionText` | value | *one group* | |
| `product_identifier` | `ProductIdentifier` | `ProductIDType`, `IDTypeName` | – | |
| `product_composition` | `DescriptiveDetail/ProductComposition` | value | *one group* | |
| `product_form` | `DescriptiveDetail/ProductForm` | value | *one group* | |
| `product_form_detail` | `DescriptiveDetail/ProductFormDetail` | value | – | |
| `product_form_feature` | `DescriptiveDetail/ProductFormFeature` | `ProductFormFeatureType`, `ProductFormFeatureValue` | `ProductFormFeatureType` | |
| `epub_technical_protection` | `DescriptiveDetail/EpubTechnicalProtection` | value | – | |
| `measure` | `DescriptiveDetail/Measure` | `MeasureType` | – | |
| `country_of_manufacture` | `DescriptiveDetail/CountryOfManufacture` | value | *one group* | |
| `product_classification` | `DescriptiveDetail/ProductClassification` | `ProductClassificationType`, `ProductClassificationCode` | `ProductClassificationType` | |
| `collection` | `DescriptiveDetail/Collection` | `CollectionType`, first `TitleText` anywhere inside | `CollectionType` | |
| `title` | `DescriptiveDetail/TitleDetail/TitleElement` | parent's `TitleType`, `TitleElementLevel` | – | `TitleType` (from `TitleDetail`) |
| `contributor` | `DescriptiveDetail/Contributor` | `@sourcename` if present, else `ContributorRole`, `PersonName` | – | |
| `edition_type` | `DescriptiveDetail/EditionType` | value | – | |
| `edition_number` | `DescriptiveDetail/EditionNumber` | value | *one group* | |
| `edition_statement` | `DescriptiveDetail/EditionStatement` | value | *one group* | |
| `language` | `DescriptiveDetail/Language` | `LanguageRole`, `LanguageCode` | `LanguageCode` | |
| `extent` | `DescriptiveDetail/Extent` | `ExtentType` | – | |
| `number_of_illustrations` | `DescriptiveDetail/NumberOfIllustrations` | value | *one group* | |
| `subject` | `DescriptiveDetail/Subject` | `SubjectSchemeIdentifier`, `SubjectSchemeName`, `SubjectCode` | `SubjectSchemeIdentifier`, `SubjectSchemeName` | |
| `name_as_subject` | `DescriptiveDetail/NameAsSubject` | `NameType`, `PersonName`, `CorporateName` | – | |
| `audience` | `DescriptiveDetail/Audience` | `AudienceCodeType` | – | |
| `audience_range` | `DescriptiveDetail/AudienceRange` | `AudienceRangeQualifier`, `AudienceRangePrecision` | – | |
| `text_content` | `CollateralDetail/TextContent` | `@sourcename` if present, else `TextType` | `TextType` | |
| `supporting_resource` | `CollateralDetail/SupportingResource/ResourceVersion` | owner + format (below) | `ResourceContentType`, `ResourceMode`, format | `ResourceContentType`, `ContentAudience`, `ResourceMode` (from `SupportingResource`) |
| `imprint` | `PublishingDetail/Imprint` | `ImprintName` | *one group* | |
| `publisher` | `PublishingDetail/Publisher` | `PublishingRole` | – | |
| `city_of_publication` | `PublishingDetail/CityOfPublication` | value | *one group* | |
| `country_of_publication` | `PublishingDetail/CountryOfPublication` | value | *one group* | |
| `product_contact` | `PublishingDetail/ProductContact` | `ProductContactRole` | – | |
| `publishing_status` | `PublishingDetail/PublishingStatus` | value | *one group* | |
| `publishing_date` | `PublishingDetail/PublishingDate` | `PublishingDateRole` | – | |
| `sales_rights` | `PublishingDetail/SalesRights` | `SalesRightsType` | – | |
| `sales_restriction` | `PublishingDetail/SalesRights/SalesRestriction` | `SalesRestrictionType` | – | |
| `related_product` | `RelatedMaterial/RelatedProduct` | `ProductRelationCode` + every `ProductIdentifier/IDValue` | – | |
| `body_resource` | `ProductionDetail/ProductionManifest/BodyManifest/BodyResource` | `ResourceIdentifier/IDValue` | – | |
| `supply_detail` | `ProductSupply/SupplyDetail` | `Supplier/SupplierRole` | – | |
| `price` | `ProductSupply/SupplyDetail/Price` | `SupplierRole` (of the parent `SupplyDetail`), `PriceType`, `PriceQualifier`, `CurrencyCode` | – | `SupplierRole` (from the parent's `Supplier/SupplierRole`) |

How to read the table:

- **Identity** lists the values (child elements, read relative to the item;
  missing → null) that must be equal for an item in *before* and an item in
  *after* to count as the same item. "value" means the whole item value.
- **Supporting resources.** Every `ResourceVersion` is a separate item. Its
  *owner* is the `sourcename` attribute of the enclosing `SupportingResource`
  if there is one, otherwise that resource's `ResourceContentType` +
  `ResourceMode`. Its *format* is the `FeatureValue` of the
  `ResourceVersionFeature` whose `ResourceVersionFeatureType` is `01` (null if
  there is none).
- **Context fields** are copied from the parent element into the item value, so
  that the reported item describes itself. Context elements are not items of
  their own.
- **Nested items.** `SalesRestriction` inside `SalesRights` and `Price` inside
  `SupplyDetail` are items of their own. They are left out of the value of
  their parent item, so a price change is not also a `supply_detail` change.
- **Containers.** Elements that only lead to items (`DescriptiveDetail`,
  `CollateralDetail`, `PublishingDetail`, `TitleDetail`, `SupportingResource`,
  `RelatedMaterial`, `ProductionDetail`, `ProductionManifest`, `BodyManifest`,
  `ProductSupply`) are not items. Their other children (not items, not
  context) fall under the default rule below.
- **Default rule.** Any other element that is a direct child of `<Product>`
  or of a container is an item whose type is its tag name in snake_case (e.g.
  `RecordSourceName` → `record_source_name`). Its identity is its whole value
  and its fallback is *one group*.

### 3. Item value

- A **leaf** item (no child elements) has a string value: its normalised text.
- A **composite** item has a value that is a flat JSON object. The context
  fields come first, then every leaf below the item in document order, keyed by
  its path relative to the item:
  - Path segments are tag names joined with `/`, e.g. `Stock/OnHand`.
  - **Typed composites.** If a child composite's first child is a leaf whose
    tag ends with `Type`, `Role` or `Level`, the segment becomes
    `Tag[code]`, and that first child is left out (its code is now in the
    path). Examples: `Tax[01]/TaxRatePercent`, `PriceDate[15]/Date`,
    `ResourceVersionFeature[06]/FeatureValue`,
    `TitleDetail[01]/TitleElement[02]/PartNumber`.
    This applies only when every same-named sibling has such a code and the
    codes are unique among them. Otherwise the next rule is used.
  - **Repeated untyped elements** get a 1-based position:
    `PriceConstraintLimit[1]/Quantity`.
  - Otherwise the plain tag name is used.
  - The item root itself never gets a suffix. Its own `*Type` child stays a
    normal field (`"MeasureType": "01"`).

### 4. Matching

Compare the items of each type separately:

1. **By identity.** Items with equal identity are paired. If several items on
   one side share an identity, they are paired in document order (1st with 1st,
   2nd with 2nd); any surplus is unpaired.
2. **By fallback group.** An item still unpaired is paired with an unpaired
   item from the other side only if the two share a fallback group **and that
   group has exactly one item in *before* and exactly one item in *after*,
   counting all items, not just unpaired ones**. "*One group*" means all items
   of the type form a single group, so a single-occurrence element that changed
   its value is "changed", not "removed + added". "–" means no fallback.

   This is why a replaced cover (new `sourcename`, but still the only
   `ResourceContentType 01`) is one `supporting_resource.changed`, while
   replacing one Thema code among several is `subject.removed` +
   `subject.added`.
3. A pair whose values differ is **changed**. A pair whose values are equal is
   not reported. An unpaired *before* item was **removed**; an unpaired
   *after* item was **added**.

The position of an item is never a change in itself. Contributors carry their
order in `SequenceNumber`, so removing a contributor also changes the
`SequenceNumber` of the ones after it (case 028).

### 5. Output

`changes` is a JSON array of change objects:

```json
{ "type": "price.changed",
  "changed_fields": ["PriceAmount"],
  "before": { "SupplierRole": "01", "PriceType": "02", "PriceAmount": "46.9", "...": "..." },
  "after":  { "SupplierRole": "01", "PriceType": "02", "PriceAmount": "49.9", "...": "..." } }

{ "type": "publishing_status.changed", "before": "04", "after": "07" }
{ "type": "subject.added",   "after":  { "SubjectSchemeIdentifier": "93", "SubjectCode": "FRH", "...": "..." } }
{ "type": "contributor.removed", "before": { "ContributorRole": "E07", "PersonName": "Diana Giurow", "...": "..." } }
```

- `type` is `<item type>.added`, `<item type>.removed` or `<item type>.changed`.
- `.added` has only `after`, `.removed` only `before`, and `.changed` has both.
  Each is the full item value (string or object).
- `changed_fields` is present only on `.changed` with object values. It lists
  every key whose value differs (including keys present on one side only):
  first the keys of `before` in their order, then the keys only in `after`.
- Order in `expected.json`: grouped by type in the order of the units table
  (default-rule types after the table types), and within a type: changed
  pairs (in *before* order), then removed, then added. A test harness should
  compare changes as an **unordered multiset**; order is not part of the
  contract.

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

| change type | cases |
|---|---|
| `product_identifier.*` (ISBN, EAN, publisher's code, streaming ID) | 062–068 |
| `notification_type.changed`, `publishing_status.changed` | 007–011, 058, 143–145 |
| `product_form.*`, `product_form_detail.*` (binding, finishing, e-book formats) | 039, 045, 069, 072 |
| `product_form_feature.*` (players, playing time, pieces, toy safety) | 075–078, 080–083 |
| `product_packaging.*`, `map_scale.*`, `epub_license.*` (default rule) | 070, 071, 074, 164 |
| `epub_technical_protection.added` | 073 |
| `measure.*`, `country_of_manufacture.*`, `product_classification.*` | 042, 043, 084–087 |
| `collection.*` (series, cycle with ISSN) | 049–051, 093, 094 |
| `title.*` (title, subtitle, English, original, trade title, cycle) | 023–025, 057, 088–093, 173–175 |
| `contributor.*`, `no_contributor.added` (166–172: only ISNI / VIAF change, the name stays) | 027–031, 095–105, 166–172 |
| `edition_type.*`, `edition_statement.*` | 026, 056, 057, 106, 107 |
| `language.*` | 052, 053, 108, 109 |
| `extent.*`, `number_of_illustrations.*`, `audience_range.*` | 041, 044, 046, 110–115 |
| `subject.*` (Thema, keywords, publisher category), `name_as_subject.*` | 001–006, 116–120, 140 |
| `text_content.*` | 032–034, 079, 122–125, 127, 128 |
| `supporting_resource.*` (cover, samples, rules, preview widget, excerpts) | 035–039, 129–136, 178 |
| `body_resource.*` | 039, 040, 137 |
| `imprint.*`, `publisher.*`, `city_of_publication.*`, `product_contact.*` | 048, 138–141, 176, 177 |
| `publishing_date.*` (premiere, distribution start, licence expiry) | 017–022, 056, 058, 146–148 |
| `sales_rights.*`, `sales_restriction.*` | 054, 055, 149–153 |
| `related_product.*` (facsimile) | 057, 098, 154, 155 |
| `supply_detail.*` (availability, stock, pack, supplier) | 008, 010, 047, 140, 142, 156–160, 162 |
| `price.*` (amount, VAT, scheduled price, printed on product) | 012–016, 056, 161–163 |
| no change (datestamps, identical, re-serialised, reordered, attribute-only, internal fields) | 059–061, 121, 126, 165 |
