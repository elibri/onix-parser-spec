# ONIX parser fixtures

Test cases for a program that parses the ONIX messages sent by the Elibri API
into product objects. Each case is one ONIX message and the exact result the
parser must produce, as JSON.

The folder is self-contained and does not depend on any language. You can copy
it into any repository and write the parser in any language. This README is the
specification: a parser that follows the rules below produces exactly the
`message` in every `expected.json`. [FIELDS.md](FIELDS.md) explains what each
field means, with examples.

The field names to implement are the ones in this README and in
`expected.schema.json`. If you use elibriPHP, our previous PHP parser for this
ONIX, see [Differences from elibriPHP](#differences-from-elibriphp).

## Layout

```
onix_parser_fixtures/
├── README.md               this file - the output format and the parsing rules
├── FIELDS.md               what each output field means, with examples
├── expected.schema.json    JSON Schema of expected.json; lists every field of every object
├── code_lists.json         the ONIX code lists behind the *_name fields
├── cases.json              index: id, title and source of every case
└── cases/
    └── 051-audiobook/
        ├── onix.xml        the ONIX message
        └── expected.json   what the parser must return
```

### expected.json

| key           | meaning |
|---------------|---------|
| `id`          | folder name |
| `title`       | one-line name of the case |
| `description` | what the case shows |
| `source`      | informational: where the ONIX comes from (`example` - a synthetic record, `record` - a real product, `message` - a message put together for the case) and the record references |
| `message`     | **the assertion**: the parsed message (see [Output](#output)) |

## Using the cases as tests

For every directory in `cases/`: parse `onix.xml` and compare the result with
`expected.json` → `message` as JSON values. Object key order does not matter;
array order does. Numbers are compared as numbers (`39.9` equals `39.90`).

Every field is always present: a missing value is `null`, an empty list `[]`, an
absent flag `false`. `expected.schema.json` forbids fields it does not list, so
validating your output against `$defs/product` catches typos in field names.

## Where the data comes from

The ONIX is produced by the real ONIX generator of elibri, in the dialect the API
sends to clients (header `X-eLibri-API-ONIX-dialect: 3.0.2`): ONIX for Books 3.1,
namespace `http://ns.editeur.org/onix/3.1/reference`, without Elibri extensions.

- **001–047** are synthetic records, one ONIX feature each.
- **048–086** are real products: a printed picture book, a pre-order history book,
  an EPUB+MOBI e-book, an MP3 audiobook, a board game, a jigsaw puzzle, a road
  map and an open-access e-book. Most cases change the product first, to show one feature. Links point to
  `https://www.elibri.com.pl`.
- **087–091** are whole messages: three products in one message, the ONIX 3.0
  namespace, the same record without indentation and with escaped HTML, elements
  the parser does not know, and a message without products.
- **092–094** are contributor identifiers on real products: a contributor with
  only an ISNI, one with only a VIAF, and three contributors each identified
  differently (see also 027 and 060, which have both).
- **095–098** are cycles (the collection level of the title): a part that is
  not a number, no part number, a cycle next to a series with another name, and
  a cycle name ending with a dot (see also 023, 050, 051 and 074).
- **099–100** are fields no other case fills: a DOI and a short collection
  description.
- **101** is case 097 with the cycle's `PartNumber` in the level `01` element
  instead of level `02`; its output is the same.
- **102–104** are AI voices as narrators: the marker alone (`UnnamedPersons` `07`),
  a named male voice (`05`) and a named female voice (`06`). A voice cloned from a
  real person (`08`) is in 031 and 062; a male voice without a name is in 030.
- **105** is case 049 with `ProductRelationCode` `06` instead of `24`; its output
  is the same.

## Parsing rules

### XML

- Parse the XML and **ignore namespaces**: elements are identified by local
  name. Messages come in the 3.1 namespace, but older ones use 3.0 (case 088).
- `message.release` is the `release` attribute of `<ONIXMessage>`.
- Every `<Product>` that is a direct child of `<ONIXMessage>` becomes one entry of
  `products`, in document order.
- **Read only the paths given below.** Paths are relative to the element being
  parsed (`<Product>`, a `<Contributor>`, ...), and every step is a **direct
  child**. Never search descendants: a `<ProductIdentifier>` inside
  `<RelatedProduct>` is not an identifier of the product, and the `<PersonName>`
  inside a contributor's `<AlternativeName>` is not the contributor's name.
- When a path matches several elements but the field holds one value, take the
  **first** in document order.
- **Text value:** the text content of the element (CDATA and escaped text are the
  same thing), with XML whitespace (space, tab, CR, LF) stripped from both
  ends. Inner whitespace and other Unicode spaces are kept. HTML in texts stays
  as it is (a string, not parsed). Case 089 is case 050 written without
  indentation and with escaped HTML; the results are the same.
- An element that is not there gives `null`. An empty element gives `""`.
- Unknown elements are ignored (case 090).

### Value types

- Codes and texts are **strings**, exactly as in ONIX: `"03"` stays `"03"`.
- Quantities are **numbers**: measurements, extents, the number of
  illustrations, pieces, players and playing time, ages, the map scale, stock
  on hand, pack quantity, amounts, tax rates, file
  sizes, sequence numbers and the numeric ids taken from `sourcename` attributes,
  links and `IDValue`s.
- Dates:
  - `YYYY-MM-DD` for full dates (`premiere`, `distribution_start`,
    `licence_limited_to`, `price_date_value`, `current_price_until`,
    `future_price_from`).
  - `YYYY-MM-DDTHH:MM` for `datestamp` attributes (sender's local time, no zone;
    `20260914T1632` → `2026-09-14T16:32`).
  - `YYYY-MM-DDTHH:MM:00Z` for last-updated dates of files (`20261014T1122Z`
    → `2026-10-14T11:22:00Z`).
  - Raw strings where the field says so (`publishing_date.date`,
    `sales_restrictions_info.end_date`).
- `*_name` fields: the `const_name` of the code in the list given in
  `code_lists.json`, or `null` if the code is not in the list (the lists hold
  only the codes elibri uses). `language` (of a `Language`) and
  `edition_type_descriptions`, `finishing_name_descriptions`,
  `product_packaging_name_description`, `ai_voice_description` and the supplier's
  `role_description` are the Polish `name`s from the same file.

### Ids from `sourcename`

Contributors, texts and supporting resources carry `sourcename="contributorid:513210"`,
`"textid:…"`, `"resourceid:…"`. `id` is the number after the colon; `null`
without the attribute. `datestamp` comes from the `datestamp` attribute.

## Output

```json
{
  "release": "3.1",
  "header": { "sent_date_time": "20261019", "sender": { "sender_name": "Elibri sp. z o. o." } },
  "products": [ { "record_reference": "...", ... } ]
}
```

`header` is `null` when there is no `<Header>`. `header.sent_date_time` is the
raw `SentDateTime`; `sender.sender_name` is `Header/Sender/SenderName`.

The product fields are listed below in the order they appear in `expected.json`.
`expected.schema.json` has the complete list with types.

### Record

| field | source / rule |
|---|---|
| `record_reference` | `RecordReference` |
| `notification_type` | `NotificationType` |
| `deletion_text` | `DeletionText` |

### Identifiers

| field | source / rule |
|---|---|
| `isbn13` | `IDValue` of the first `ProductIdentifier` with `ProductIDType` `15` |
| `ean` | … with `ProductIDType` `03` |
| `doi` | … with `ProductIDType` `06` |
| `proprietary_identifiers` | object `{IDTypeName: IDValue}` of the `ProductIdentifier`s with `ProductIDType` `01` |

### Product form

All paths under `DescriptiveDetail`.

| field | source / rule |
|---|---|
| `product_composition` | `ProductComposition` |
| `onix_product_form` | `ProductForm` as sent |
| `product_form` | `ProductForm`, but every form starting with `B` (BB, BC, ...) becomes `BA` (printed book) |
| `product_form_name` | name of `product_form` (ProductFormCode) |
| `product_form_details` | every `ProductFormDetail` (binding, finishing, file formats) |
| `cover_type` | for `B*` forms, from the form and the binding detail (table below); otherwise `null` |
| `finishings` / `finishing_names` / `finishing_name_descriptions` | for `B*` forms: the `ProductFormDetail` codes that are in list Finishing, their names and their Polish descriptions |
| `product_packaging` / `product_packaging_name` / `product_packaging_name_description` | `ProductPackaging`, its name and its Polish description (list ProductPackaging) |
| `digital_formats` | only when `product_form` is `EA`: names (ProductFormDetail) of the `ProductFormDetail` codes, with `MOBIPOCKET` written `MOBI`, e.g. `["EPUB","MOBI"]` |
| `technical_protections` | names (EpubTechnicalProtection) of every `EpubTechnicalProtection` |
| `epub_license` | `EpubLicense`: `{name: EpubLicenseName, link: EpubLicenseExpression/EpubLicenseExpressionLink}`, or `null` |

`cover_type` (the binding detail is the first `ProductFormDetail` listed for the form):

| ProductForm | binding detail → cover_type | otherwise |
|---|---|---|
| BB | B501 `twarda z obwolutą`, B415 `twarda lakierowana`, B413 `plastikowa` | `twarda` |
| BC | B504 `miękka ze skrzydełkami`, B412 `zintegrowana` | `miękka` |
| BG | | `skórzana` |
| BP | | `gąbka` |
| other B* | | `null` |

### Features: games and toy safety

From `ProductFormFeature`: its type is `ProductFormFeatureType`, its value
`ProductFormFeatureValue`, its description `ProductFormFeatureDescription`.

| field | source / rule |
|---|---|
| `number_of_pieces` | feature type `22` |
| `players_number_from`, `players_number_to` | feature type `23` |
| `playing_time_from`, `playing_time_to` | feature type `24` |
| `carries_ce_logo` | a type-`13` feature with value `01` exists |
| `carries_unsuitable_for_children_below_3_logo` | … value `03` |
| `carries_en71_logo` | … value `08` |
| `minimum_age_warning` | description of the type-`13` feature with value `02` |
| `toy_safety_warning` | … value `04` |
| `declaration_of_conformity_url` | … value `07` |

Pieces, players and playing time are read from the value, or if there is none,
from the description: the text is split at the first `-`, the part before is
`*_from`, the first word after it is `*_to` (`"2-5 graczy"` → 2, 5;
`"20-40 min."` → 20, 40; `"2"` → 2, `null`).

### Measures, classification

| field | source / rule |
|---|---|
| `height`, `width`, `thickness` (mm), `weight` (grams) | `Measurement` of the `Measure` with `MeasureType` `01`, `02`, `03`, `08` |
| `map_scale` | `MapScale` |
| `country_of_manufacture` | `CountryOfManufacture` |
| `cn_code` | `ProductClassificationCode` of the `ProductClassification` with `ProductClassificationType` `01` |

### Collections and titles

A *title detail* is a `TitleDetail` directly in `DescriptiveDetail`: its `TitleType` is its type, and each `TitleElement` has a `level` (`TitleElementLevel`), `title` (`TitleText`), `subtitle` (`Subtitle`), `part_number` (`PartNumber`) and `language` (`language` attribute of `TitleText`). If the element of level `01` has a `PartNumber`, the element of level `02` exists and has none, the number belongs to level `02`: both places parse the same (cases 097 and 101).

| field | source / rule |
|---|---|
| `series` | per `Collection`: `name` (`TitleText`) and `number_within_series` (`PartNumber`, a string) of the first `TitleElement` of its first `TitleDetail` |
| `issn_with_hyphens` | `IDValue` of the first `CollectionIdentifier` with `CollectionIDType` `02`, in the first `Collection` that has one |
| `issn` | the same with everything except digits and `X` removed |
| `title`, `subtitle` | of the product-level element (`level` `01`) of the **first** title detail of type `01` |
| `collection_title`, `collection_part_number` | `title` and `part_number` of the collection-level element (`02`) of that title detail |
| `title_eng` | `title` of the product-level element of a **later** type-`01` title detail whose `language` is `eng` |
| `original_title` | full title of the first title detail of type `03` |

Used by `original_title`. Full title of an element: `title`; if there is a subtitle, add `.` unless the
title ends with one, then a space and the subtitle; if there is a part number,
add ` (#N)` when it is a number or ` (N)` otherwise. Full title of a title detail:
the full title of its collection-level element and of its product-level
element, joined with `. ` (no second dot if the first ends with `.`); either one
alone if the other is missing.

### Contributors

| field | source / rule |
|---|---|
| `contributors` | every `Contributor` (shape below) |
| `no_contributor` | a `NoContributor` element exists |

Contributor: `id`, `datestamp` (from the attributes); `number`
(`SequenceNumber`); `role` (`ContributorRole`), `role_name`; `from_language`
(`FromLanguage`, for any role); `person_name`, `titles_before_names`,
`names_before_key`, `prefix_to_key`, `key_names`, `names_after_key`,
`biographical_note` (`PersonName`, `TitlesBeforeNames`, …, `BiographicalNote`);
`unnamed_persons` (`UnnamedPersons`); `ai_generated_voice` (`unnamed_persons`
is `05`, `06`, `07` or `08`); `ai_voice_description` (when `ai_generated_voice`,
the Polish name of `unnamed_persons` from list UnnamedPersons, else `null`); `voice_name` (`PersonName` of the first
`AlternativeName` whose `NameType` is not `00`); `isni` / `viaf` (`IDValue` of
the `NameIdentifier` with `NameIDType` `16` / `31`); `alternative_names` (the `PersonName` of every `AlternativeName` with
`NameType` `00`).

### Edition, language, extent

| field | source / rule |
|---|---|
| `edition_statement` | `EditionStatement` |
| `edition_types`, `edition_type_names`, `edition_type_descriptions` | every `EditionType`; names and Polish descriptions from list EditionType |
| `languages` | every `Language`: `role` (`LanguageRole`), `role_name`, `code` (`LanguageCode`), `language` (Polish name, list LanguageCode) |
| `number_of_pages`, `number_of_characters`, `duration` (minutes) | `ExtentValue` of the `Extent` with `ExtentType` `00`, `02`, `09` |
| `number_of_illustrations` | `NumberOfIllustrations` |

### Subjects

| field | source / rule |
|---|---|
| `thema_subjects` | every `Subject` with `SubjectSchemeIdentifier` `93`–`99`: `code` (`SubjectCode`); `heading_texts` (the text of every `SubjectHeadingText`, as a list of strings) |
| `thema_version` | `SubjectSchemeVersion` of the first of those subjects, or `null` when there are none |
| `publisher_categories` | every `Subject` with `SubjectSchemeIdentifier` `24`: `code` (`SubjectCode`), `name` (first `SubjectHeadingText`) |
| `keywords` | from every `Subject` with `SubjectSchemeIdentifier` `20`, in every language: each `SubjectHeadingText` is split at `;`, every part stripped of XML whitespace, empty parts dropped; all parts in document order |
| `names_as_subject` | every `NameAsSubject`: `person_name`, `corporate_name`, `alternative_names` (`PersonName` or `CorporateName` of every `AlternativeName` with `NameType` `00`) |

### Audience

| field | source / rule |
|---|---|
| `reading_age_from` / `reading_age_to` | `AudienceRangeValue` of the `AudienceRange` with `AudienceRangePrecision` `03` / `04` |

### Texts

Under `CollateralDetail`.

Only a `TextContent` with `ContentAudience` `00` is read. Each is an object: `id`, `datestamp`; `text` (first `Text`); `text_eng` (the first later `Text` with `language="eng"`).

| field | source / rule |
|---|---|
| `table_of_contents`, `description`, `short_description`, `short_collection_description`, `list_of_contents`, `open_access_statement` | the first text of type `04`, `03`, `02`, `16`, `32`, `20` (or `null`) |
| `excerpts` | all texts of type `14` |

### Supporting resources

| field | source / rule |
|---|---|
| `supporting_resources` | every `SupportingResource` except the front covers (content type `01`) and the excerpts listed in `excerpt_infos`: `id`, `datestamp`; `content_type` (`ResourceContentType`), `mode` (`ResourceMode`) and their names; from its first `ResourceVersion`: `form` (`ResourceForm`), `form_name`, `link` (`ResourceLink`), `md5` / `file_size` (`FeatureValue` of the `ResourceVersionFeature` of type `06` / `07`) |
| `front_cover` | the first `SupportingResource` with content type `01`, or `null`: `id`, `datestamp`; from its first `ResourceVersion`: `link` (`ResourceLink`), `md5` / `file_size` (`FeatureValue` of the `ResourceVersionFeature` of type `06` / `07`) |
| `preview_exists` | a resource with content type `16` exists |
| `excerpt_infos` | only when `product_form` is `EA` or `AJ`: one entry per `ResourceVersion` of every resource with content type `15`: `id` (5th `/`-separated part of `ResourceLink`, e.g. `https://www.elibri.com.pl/excerpt/366213/…` → 366213), `file_type` (text after the last `.` of the link + `_excerpt`), `file_size` / `md5` (`FeatureValue` of the `ResourceVersionFeature` of type `07` / `06`), `link` (`ResourceLink`), `updated_at` (`Date` of the `ContentDate` with role `17`) |

### Publishing

Under `PublishingDetail`.

| field | source / rule |
|---|---|
| `imprint_name` | `Imprint/ImprintName`, present in every product |
| `imprint_id` | `Imprint/ImprintIdentifier/IDValue`, present in every product |
| `publisher_name` | `Publisher/PublisherName` |
| `publisher_id` | `Publisher/PublisherIdentifier/IDValue` |
| `publisher_website` | `Publisher/Website/WebsiteLink` |
| `city_of_publication` | `CityOfPublication` |
| `safety_contact` | the `ProductContact` with role `10`: `company_name` (`ProductContactName`), `phone` (`TelephoneNumber`), `email` (`EmailAddress`), `street` (`StreetAddress`), `city` (`LocationName`), `postal_code`, `country_code` |
| `publishing_status` | `PublishingStatus` |
| `current_state` | from `notification_type` and `publishing_status` (below) |
| `publishing_date` | the `PublishingDate` with role `01`, or `null`: `format` (`dateformat` attribute of `Date`, else a `DateFormat` element), `format_name` (DateFormat); `date` (raw); `parsed` (below) |
| `premiere` | `publishing_date.parsed` as `YYYY-MM-DD` when it has three parts, else `null` - **but see sales restrictions** |
| `distribution_start` | `Date` of the `PublishingDate` with role `27` as `YYYY-MM-DD` |
| `licence_limited_to` | … role `13` (end of the e-book licence) |
| `unlimited_licence` | `licence_limited_to` is `null` |
| `sales_restrictions` | a `SalesRights/SalesRestriction` exists |
| `sales_restrictions_info` | the first of them: `type` (`SalesRestrictionType`), `type_name`, `outlet_name` (`SalesOutlet/SalesOutletName`), `outlet_identifier` (`SalesOutlet/SalesOutletIdentifier`: `{type: SalesOutletIDType, value: IDValue}`), `end_date` (`EndDate`, raw) |
| `territory_countries` / `territory_regions` | every `SalesRights/Territory/CountriesIncluded` / `RegionsIncluded`, split at whitespace |
| `sale_restricted_to_poland` | `territory_countries` is exactly `["PL"]` |

`parsed` splits the date by its format: `YYYYMMDD` (`00`) → `["2026","11","10"]`,
`YYYYMM` (`01`) → `["2026","11"]`, `YYYY` (`05`) → `["2026"]`, other formats → `[]`.

**Sales restrictions and premiere** (elibriPHP behaviour, kept on purpose):
while a book is sold exclusively by one retailer, everyone else gets it when the
exclusivity ends. So when `sales_restrictions_info.end_date` is set, `premiere`
is that date. `publishing_date` keeps the real publication date (case 070).

`current_state`:

| NotificationType | PublishingStatus | current_state |
|---|---|---|
| 01 | any | `announced` |
| 02 | 02 / 03 / 01 | `preorder` / `indefinitely_postponed` / `cancelled` |
| 05 | any | `deleted` |
| other | 04 / 07 | `published` / `out_of_print` |
| anything else | | `null` |

### Related products and files

| field | source / rule |
|---|---|
| `alternative_format_record_references` | the record references of the same book in other formats (e-book, audiobook, printed book): for every `RelatedMaterial/RelatedProduct` with `ProductRelationCode` `06` or `24`, `IDValue` of its `ProductIdentifier`s with `ProductIDType` `01`. Elibri currently sends `24`; both codes parse the same (cases 049 and 105) |
| `file_infos` | every `ProductionDetail/ProductionManifest/BodyManifest/BodyResource` (master files): `id` (`IDValue` of the `ResourceIdentifier` with `ResourceIDType` `01`), `file_type` (extension of `ResourceFileLink`; `zip` → `mp3_in_zip`), `file_size` / `md5` (`ResourceFileFeatureValue` of the `ResourceFileFeature` of type `07` / `06`), `updated_at` (`Date` of the `ResourceFileDate` with role `17`) |

### Supply and prices

| field | source / rule |
|---|---|
| `supply_details` | every `ProductSupply/SupplyDetail` (shape below) |
| `cover_price`, `current_price_until`, `future_cover_price`, `future_price_from`, `vat` | from the **consumer prices**, below |
| `additional_trade_information` | the last non-null `supplier_own_coding` |

Supply detail: `supplier` (`Supplier`: `role` (`SupplierRole`), `role_name` and
`role_description` (name and Polish description, list SupplierRole), `vat_id`
(`IDValue` of the first `SupplierIdentifier`), `name`, `website`
(`Website/WebsiteLink`)); `product_availability`, `product_availability_name`;
`supplier_own_coding` (`SupplierOwnCoding/SupplierCodeValue`); `on_hand`,
`proximity`, `proximity_name` (`Stock/OnHand`, `Stock/Proximity`);
`pack_quantity`; `unpriced_item_type` (`UnpricedItemType` of the supply
detail, e.g. free open-access books); `prices`.

Price (every `Price`): `type` (`PriceType`), `type_name` (PriceTypeCode);
`qualifier` (`PriceQualifier`; `05` is the consumer price); `amount` (`PriceAmount`);
`tax_type` (`Tax/TaxType`); `vat` (`Tax/TaxRatePercent` when the tax type is
`01`); `currency_code`; `printed_on_product`,
`printed_on_product_name`, `position_on_product`; `price_date_type`
(`PriceDate/PriceDateRole`), `price_date_value` (`PriceDate/Date` as
`YYYY-MM-DD`).

Consumer prices are the prices of all supply details whose `type` is `02` and
whose `qualifier` is `null` or `05`. Going through them in order: a price with date role `15` (until) sets
`cover_price` and `current_price_until`; with role `14` (from) it sets
`future_cover_price` and `future_price_from`; otherwise it sets `cover_price`.
Each of them sets the product's `vat` to its own `vat`.

## Differences from elibriPHP

elibriPHP is our previous PHP parser for Elibri ONIX. This section is for you
only if you already use it and are moving to an implementation of this spec; if
you are starting from scratch, skip it.

Many field names, and most values, are the same as elibriPHP's. Where a field
exists in both, these are the differences:

| what | elibriPHP | fixtures | cases |
|---|---|---|---|
| e-book exclusive to a retailer (`SalesOutletIdentifier`, no `EndDate`) | throws | `outlet_identifier`, `end_date` null | 069 |
| `title`, `original_title` with several title details of a type | the last one | the first one; an English one goes to `title_eng` | 055, 056 |
| keywords in several languages | first `SubjectHeadingText` only | all of them | 057 |
| spaces around keywords (`"przebudzenie "`) and heading texts | kept | stripped | 048, 053 … |
| alternative names of a `CorporateName` subject | lost | read | 059 |
| identifiers of related products | added to the product's `proprietary_identifiers` | ignored (direct children only) | 041, 049 … |
| master file in a ZIP | `file_type` null (`==` instead of `=`) | `mp3_in_zip` | 051 … |
| `PartNumber` of a cycle in the level `01` element | `collection_part` null | `collection_part_number` as if it were in level `02` | 101 |
| `series` | list of `[title, part]` pairs | list of `{name, number_within_series}` | 024, 048 … |
| `supporting_resources` | every resource | without front covers (in `front_cover`) and excerpts of e-books and audiobooks (in `excerpt_infos`) | 015, 040, 048 … |
| `FromLanguage` | read only for translators | read for every role | – |
| a `SupplyDetail` without a price | `prices` null (PHP warning) | `[]` | 055 |
| types | numbers and codes as strings, some codes as ints (`proximity` 3), floats/ints chosen per field, dates as `DateTime` | see [Value types](#value-types) | all |

Fields the fixtures add (elibriPHP does not parse them): `onix_product_form`,
`technical_protections`, `epub_license`, `map_scale`, `title_eng`,
`no_contributor`, `number_of_characters`, `heading_texts`,
`text_eng`,
`doi`, `imprint_id`, `publisher_website`, `distribution_start`,
`publisher_categories`, `thema_version`, `ai_voice_description`,
supplier `role_name`, `role_description` and `vat_id`, `finishing_name_descriptions`,
`product_packaging_name_description`, `short_collection_description`,
`list_of_contents`, `open_access_statement`, `outlet_identifier`,
supply detail `unpriced_item_type` and price `qualifier`.
`collection_part` is `collection_part_number` here, and the misspelt
`currrent_price_until` is `current_price_until`.

Not covered: the 3.0.1 dialect with Elibri extensions (`elibri:*` elements,
`EpubUsageConstraint`), which the API sends only on request.
