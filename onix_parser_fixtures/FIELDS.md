# ONIX parser output: field guide

What each field of the parser output means, for people using the data. For how
each field is read from the ONIX, see [README.md](README.md).

Every field is always present. A value that is missing is `null`, an empty list
is `[]`, and a flag that does not apply is `false`. `date` means `YYYY-MM-DD`.
The examples are real values from the cases in this folder; a trailing `…` means
the value is cut short, and `—` means no case fills the field. Paths use `[]` for
items of a list.

## Message

The object around the products.

| Field | Meaning | Type | Example |
|---|---|---|---|
| `release` | ONIX version of the message. | text | `"3.1"` |
| `header` | Information about the message itself; `null` if it has none. | object | see below |
| `header.sent_date_time` | When the message was sent, as sent in the ONIX. | text | `"20261019"` |
| `header.sender` | Who sent the message. | object | see below |
| `header.sender.sender_name` | Name of the sender. | text | `"Elibri sp. z o. o."` |
| `products` | The products in the message, each described by the fields below. | list | see below |

## Record

| Field | Meaning | Type | Example |
|---|---|---|---|
| `record_reference` | Elibri's permanent identifier of this product. Use it as your key. | text | `"fdb8fa072be774d97a97"` |
| `notification_type` | Kind of record: `01` announced, `02` pre-order, `03` published, `05` deleted. `current_state` gives this in plain form. | text | `"03"` |
| `deletion_text` | Why the record was deleted. | text | `"Błędnie założony rekord"` |

## Identifiers

| Field | Meaning | Type | Example |
|---|---|---|---|
| `isbn13` | ISBN-13 without hyphens. | text | `"9788324799992"` |
| `ean` | EAN barcode, when the product has one. | text | `"9788324788882"` |
| `doi` | Digital Object Identifier. | text | `"https://doi.org/10.31338/uw.9788323554943"` |
| `proprietary_identifiers` | Other identifiers, as `{system name: value}`. | object | `{"EDGARD": "126042"}` |

## Product form

What kind of product this is.

| Field | Meaning | Type | Example |
|---|---|---|---|
| `product_composition` | ONIX composition code; `00` is a single item. | text | `"00"` |
| `onix_product_form` | Form code exactly as sent, e.g. `BB` hardback, `BC` paperback, `EA` e-book, `AJ` audiobook. | text | `"BA"` |
| `product_form` | The form with every printed book unified as `BA`. | text | `"BA"` |
| `product_form_name` | Name of `product_form`. | text | `"BOOK"` |
| `product_form_details` | All detail codes: binding, finishing and file formats. | list | `["E101", "E127"]` |
| `cover_type` | Binding of a printed book, in Polish. | text | `"twarda"` |
| `finishings` | Finishing codes of a printed book, such as foil or a ribbon marker. | list | `["B419", "B506"]` |
| `finishing_names` | Names of `finishings`. | list | `["DECORATED_PAGE_EDGES", "RIBBON_MARKER"]` |
| `finishing_name_descriptions` | Polish descriptions of `finishings`. | list | `["barwione brzegi (złocone, nadrukowane)", "zakładka-wstążka…` |
| `product_packaging` | Packaging code, such as a slipcase. | text | `"10"` |
| `product_packaging_name` | Name of `product_packaging`. | text | `"SLIP_CASED"` |
| `product_packaging_name_description` | Polish description of `product_packaging`. | text | `"etui (na jedną książkę)"` |
| `digital_formats` | File formats an e-book is sold in. | list | `["EPUB", "MOBI"]` |
| `technical_protections` | How an e-book is protected. | list | `["WATERMARK"]` |
| `epub_license` | Licence of an e-book, such as Creative Commons. | object | see below |
| `epub_license.name` | Name of the licence. | text | `"Creative Commons Uznanie autorstwa 4.0 (CC BY 4.0)"` |
| `epub_license.link` | Link to the licence text. | text | `"https://creativecommons.org/licenses/by/4.0/deed.pl"` |

## Games and toy safety

Filled for board games, puzzles and toys.

| Field | Meaning | Type | Example |
|---|---|---|---|
| `number_of_pieces` | Number of pieces in a game or puzzle. | number | `60` |
| `players_number_from` | Minimum number of players. | number | `2` |
| `players_number_to` | Maximum number of players; `null` if there is only one number. | number | `5` |
| `playing_time_from` | Minimum playing time, in minutes. | number | `20` |
| `playing_time_to` | Maximum playing time, in minutes. | number | `40` |
| `carries_ce_logo` | The product carries the CE mark. | yes or no | `true` |
| `carries_unsuitable_for_children_below_3_logo` | The product carries the "not for children under 3" symbol. | yes or no | `true` |
| `carries_en71_logo` | The product carries the EN 71 toy safety mark. | yes or no | `true` |
| `minimum_age_warning` | Text of the minimum age warning. | text | `"Dla dzieci od 6 lat"` |
| `toy_safety_warning` | Text of the safety warning. | text | `"Zawiera małe elementy"` |
| `declaration_of_conformity_url` | Link to the declaration of conformity. | text | `"https://www.hseni.gov.uk/publications/example-declaration-c…` |

## Physical details

| Field | Meaning | Type | Example |
|---|---|---|---|
| `height` | Height in millimetres. | number | `300` |
| `width` | Width in millimetres. | number | `240` |
| `thickness` | Thickness in millimetres. | number | `20` |
| `weight` | Weight in grams. | number | `620` |
| `map_scale` | Scale of a map, as the number after `1:`. | number | `50000` |
| `country_of_manufacture` | Country where the product was made. | text | `"PL"` |
| `cn_code` | Combined Nomenclature customs code. | text | `"4901"` |

## Series and titles

A *series* is a publisher's collection, such as a list of school readings. A *cycle* is a set of connected volumes, and is part of the title.

| Field | Meaning | Type | Example |
|---|---|---|---|
| `series` | Series the product belongs to. | list | see below |
| `series[].name` | Name of the series. | text | `"Morally Gray"` |
| `series[].number_within_series` | Volume number in the series, as text. | text | `"1"` |
| `issn` | ISSN without hyphens. | text | `"01378929"` |
| `issn_with_hyphens` | ISSN as printed. | text | `"0137-8929"` |
| `title` | Title of the product, without the cycle. | text | `"Nielegalni"` |
| `subtitle` | Subtitle. | text | `"Zwyczajne losy mieszkańców Korei Północnej."` |
| `collection_title` | Name of the cycle. | text | `"Morally Gray"` |
| `collection_part_number` | Volume number in the cycle, as text. | text | `"1"` |
| `title_eng` | English title. | text | `"Rękopisy Iwana Dniprowskiego i historia „rozstrzelanego odr…` |
| `original_title` | Title in the original language. | text | `"Ricochets"` |

## Contributors

Authors, translators, narrators and other people involved.

| Field | Meaning | Type | Example |
|---|---|---|---|
| `contributors` | People and voices, in display order. | list | see below |
| `contributors[].id` | Elibri's identifier of this contributor on this product. | number | `513210` |
| `contributors[].datestamp` | When the contributor was last changed, in the sender's local time. | date | `"2026-09-14T16:32"` |
| `contributors[].number` | Position in the list. | number | `1` |
| `contributors[].role` | ONIX role code. | text | `"A01"` |
| `contributors[].role_name` | Name of the role. | text | `"AUTHOR"` |
| `contributors[].from_language` | Language translated from, for a translator. | text | `"eng"` |
| `contributors[].person_name` | Full name. | text | `"Joanna Concejo"` |
| `contributors[].titles_before_names` | Titles such as `dr`. | text | `"prof. ks."` |
| `contributors[].names_before_key` | First names. | text | `"Gilles"` |
| `contributors[].prefix_to_key` | Surname prefix such as `von`. | text | `"von"` |
| `contributors[].key_names` | Surname. | text | `"Baum"` |
| `contributors[].names_after_key` | Suffix after the surname, such as `Jr.`. | text | `"OP"` |
| `contributors[].biographical_note` | Biography, as HTML. | text | `"<p>Gilles Baum urodził się w 1975 roku w Miluzie, we Francj…` |
| `contributors[].unnamed_persons` | Set when there is no named person: `04` various authors, `05` male AI voice, `06` female AI voice, `07` AI voice, `08` AI voice based on a real person's voice. | text | `"04"` |
| `contributors[].ai_generated_voice` | The narrator is an AI voice. | yes or no | `true` |
| `contributors[].ai_voice_description` | Polish description of the AI voice; `null` if this is not one. | text | `"Głos syntetyzowany - męski"` |
| `contributors[].voice_name` | Name of the AI voice, or of the person it is based on. | text | `"Wojtek"` |
| `contributors[].isni` | ISNI identifier of the person. | text | `"0000000123456789"` |
| `contributors[].viaf` | VIAF identifier of the person. | text | `"96994048"` |
| `contributors[].alternative_names` | Other forms of the person's name. | list | `["William Szekspir"]` |
| `no_contributor` | The publisher states that the product has no contributors. | yes or no | `true` |

## Edition, language and size

| Field | Meaning | Type | Example |
|---|---|---|---|
| `edition_statement` | Edition as printed in the book. | text | `"wydanie 1"` |
| `edition_types` | Edition type codes. | list | `["LTE", "ILL"]` |
| `edition_type_names` | Names of `edition_types`. | list | `["LARGE_TYPE_EDITION", "ILLUSTRATED_EDITION"]` |
| `edition_type_descriptions` | Polish descriptions of `edition_types`. | list | `["edycja z powiększoną czcionką", "wydanie ilustrowane"]` |
| `languages` | Languages of the product. | list | see below |
| `languages[].role` | What the language applies to, as a code. | text | `"01"` |
| `languages[].role_name` | Name of the role: the text, the original or the abstracts. | text | `"LANGUAGE_OF_TEXT"` |
| `languages[].code` | Language code. | text | `"pol"` |
| `languages[].language` | Language name in Polish. | text | `"polski"` |
| `number_of_pages` | Number of pages. | number | `448` |
| `duration` | Length of an audiobook, in minutes. | number | `59` |
| `number_of_characters` | Length of the text, in characters. | number | `500000` |
| `number_of_illustrations` | Number of illustrations. | number | `48` |

## Subjects and audience

| Field | Meaning | Type | Example |
|---|---|---|---|
| `thema_subjects` | Thema subject categories. | list | see below |
| `thema_subjects[].code` | Thema code. | text | `"5LC"` |
| `thema_subjects[].heading_texts` | Names of the category. | list | `["Kwalifikatory grup docelowych i okolicznościowe / Związane…` |
| `thema_version` | Version of Thema the codes come from. | text | `"1.6"` |
| `publisher_categories` | The publisher's own categories. | list | see below |
| `publisher_categories[].code` | Category code. | text | `"181"` |
| `publisher_categories[].name` | Category name. | text | `"Historia"` |
| `keywords` | Keywords in every language, in the order sent. | list | `["romans"]` |
| `names_as_subject` | People or organisations the book is about. | list | see below |
| `names_as_subject[].person_name` | Name of the person. | text | `"Maria Skłodowska-Curie"` |
| `names_as_subject[].corporate_name` | Name of the organisation. | text | `"Templariusze"` |
| `names_as_subject[].alternative_names` | Other forms of the name. | list | `["Marie Curie"]` |
| `reading_age_from` | Minimum reader age, in years. | number | `7` |
| `reading_age_to` | Maximum reader age, in years. | number | `107` |

## Texts

Each of `table_of_contents`, `description`, `short_description`, `short_collection_description`, `list_of_contents`, `open_access_statement` and every item of `excerpts` is an object of the same shape, shown here as `<text>`.

| Field | Meaning | Type | Example |
|---|---|---|---|
| `table_of_contents` | Table of contents. | object | see below |
| `description` | Main description of the book. | object | see below |
| `short_description` | Short description. | object | see below |
| `short_collection_description` | Description of the series or cycle. | object | see below |
| `list_of_contents` | What is inside a box, such as the pieces of a game. | object | see below |
| `open_access_statement` | Statement about open access. | object | see below |
| `excerpts` | Text excerpts. | list | see below |
| `<text>.id` | Elibri's identifier of the text; `null` for texts generated from a product field. | number | `319378` |
| `<text>.datestamp` | When the text was last changed, in the sender's local time. | date | `"2026-10-14T13:24"` |
| `<text>.text` | The text, usually as HTML. | text | `"<p>Młoda kobieta stojąca na skraju bankructwa.</p>\n<p>Taje…` |
| `<text>.text_eng` | English version of the text. | text | `"<p>This book comprises a presentation of research on the li…` |

## Files and images

| Field | Meaning | Type | Example |
|---|---|---|---|
| `front_cover` | Front cover image. | object | see below |
| `front_cover.id` | Elibri's identifier of the image. | number | `480045` |
| `front_cover.datestamp` | When the image was last changed, in the sender's local time. | date | `"2026-10-02T07:59"` |
| `front_cover.link` | Where to download it. | text | `"https://www.elibri.com.pl/attachments/260e49e9df9407937371/…` |
| `front_cover.md5` | Checksum. It changes only when the file changes, so use it to detect a new cover. | text | `"119c3a871ef1e47860f5f9f7b40d3122"` |
| `front_cover.file_size` | Size in bytes. | number | `660092` |
| `supporting_resources` | Other images and resources, such as back covers, sample spreads and preview widgets. Excerpts of e-books and audiobooks are in `excerpt_infos`. | list | see below |
| `supporting_resources[].id` | Elibri's identifier of the resource. | number | `477932` |
| `supporting_resources[].datestamp` | When it was last changed, in the sender's local time. | date | `"2026-09-14T14:49"` |
| `supporting_resources[].content_type` | Kind of resource, as a code. | text | `"15"` |
| `supporting_resources[].content_type_name` | Name of the kind, such as `BACK_COVER`. | text | `"SAMPLE_CONTENT"` |
| `supporting_resources[].mode` | Media type, as a code. | text | `"03"` |
| `supporting_resources[].mode_name` | Name of the media type. | text | `"IMAGE"` |
| `supporting_resources[].form` | How it is delivered, as a code. | text | `"02"` |
| `supporting_resources[].form_name` | Name of the delivery form. | text | `"DOWNLOADABLE_FILE"` |
| `supporting_resources[].link` | Where to get it. | text | `"https://www.elibri.com.pl/attachments/c937e645aeb6050c0246/…` |
| `supporting_resources[].md5` | Checksum of the file. | text | `"3ccd9c1e5f8c7b44849f0eb3d6e5db8c"` |
| `supporting_resources[].file_size` | Size in bytes. | number | `1044907` |
| `preview_exists` | An interactive preview widget is available. | yes or no | `true` |
| `excerpt_infos` | Excerpt files of an e-book or audiobook, one entry per format. | list | see below |
| `excerpt_infos[].id` | Elibri's identifier of the file. | number | `366961` |
| `excerpt_infos[].file_type` | Format, such as `epub_excerpt`. | text | `"epub_excerpt"` |
| `excerpt_infos[].file_size` | Size in bytes. | number | `2429768` |
| `excerpt_infos[].md5` | Checksum of the file. | text | `"e3c74e50bc2ac48c8b40f1c219b74824"` |
| `excerpt_infos[].link` | Where to download it. | text | `"https://www.elibri.com.pl/excerpt/366961/e3c74e50bc2ac48c8b…` |
| `excerpt_infos[].updated_at` | When the file was last changed, in UTC. | date | `"2026-10-02T08:03:00Z"` |
| `file_infos` | The full files of an e-book or audiobook. This list describes them and has no download links. | list | see below |
| `file_infos[].id` | Elibri's identifier of the file. | number | `366962` |
| `file_infos[].file_type` | Format: `epub`, `mobi`, `pdf` or `mp3_in_zip`. | text | `"epub"` |
| `file_infos[].file_size` | Size in bytes. | number | `2700833` |
| `file_infos[].md5` | Checksum of the file. | text | `"d51a4e4c0b81fd67c15945d67657a89d"` |
| `file_infos[].updated_at` | When the file was last changed, in UTC. | date | `"2026-10-02T08:03:00Z"` |

## Publisher

| Field | Meaning | Type | Example |
|---|---|---|---|
| `imprint_name` | Brand the book is published under. | text | `"Tylko Bestsellery"` |
| `imprint_id` | Elibri's identifier of the brand. It stays the same when the brand is renamed. | number | `312` |
| `publisher_name` | Name of the publisher. | text | `"Tylko Bestsellery"` |
| `publisher_id` | Elibri's identifier of the publisher. | number | `11` |
| `publisher_website` | Link to this book on the publisher's site. | text | `"https://www.wuw.pl/product-pol-20777-%D0%A0%D1%83%D0%BA%D0%…` |
| `city_of_publication` | City of publication. | text | `"Warszawa"` |
| `safety_contact` | Company to contact about product safety. | object | see below |
| `safety_contact.company_name` | Company name. | text | `"Tylko Bestsellery"` |
| `safety_contact.phone` | Phone number. | text | `"220000000"` |
| `safety_contact.email` | Email address. | text | `"list@wydawnictwoformat.pl"` |
| `safety_contact.street` | Street address. | text | `"Puławska 5"` |
| `safety_contact.city` | City. | text | `"Warszawa"` |
| `safety_contact.postal_code` | Postal code. | text | `"00-876"` |
| `safety_contact.country_code` | Country code. | text | `"PL"` |

## Status and dates

| Field | Meaning | Type | Example |
|---|---|---|---|
| `publishing_status` | ONIX status code. `current_state` gives this in plain form. | text | `"04"` |
| `current_state` | Where the product is in its life: `announced`, `preorder`, `indefinitely_postponed`, `cancelled`, `published`, `out_of_print` or `deleted`. | text | `"published"` |
| `publishing_date` | Publication date as stated in the record. It may be only a year or a month. | object | see below |
| `publishing_date.format` | Date format, as a code. | text | `"00"` |
| `publishing_date.format_name` | Name of the date format. | text | `"YYYYMMDD"` |
| `publishing_date.date` | The date as sent. | text | `"20261016"` |
| `publishing_date.parsed` | The date split into parts. | list | `["2026", "10", "16"]` |
| `premiere` | When the book becomes available to everyone. During an exclusive sale with an end date, that is the end date. `null` when only part of the date is known. | date | `"2026-10-02"` |
| `distribution_start` | Earliest date retailers may ship the book. | date | `"2026-10-16"` |
| `licence_limited_to` | When the e-book licence ends. | date | `"2034-03-07"` |
| `unlimited_licence` | The e-book licence has no end date. | yes or no | `true` |

## Sales rights

| Field | Meaning | Type | Example |
|---|---|---|---|
| `sales_restrictions` | The product is sold exclusively by one retailer. | yes or no | `true` |
| `sales_restrictions_info` | Details of the exclusive sale. | object | see below |
| `sales_restrictions_info.type` | Restriction code. | text | `"04"` |
| `sales_restrictions_info.type_name` | Name of the restriction. | text | `"RETAILER_EXCLUSIVE"` |
| `sales_restrictions_info.outlet_name` | Name of the retailer. | text | `"Empik"` |
| `sales_restrictions_info.outlet_identifier` | Code of the retailer, used for e-books. | object | see below |
| `sales_restrictions_info.outlet_identifier.type` | Kind of code. | text | `"03"` |
| `sales_restrictions_info.outlet_identifier.value` | The code. | text | `"EMP"` |
| `sales_restrictions_info.end_date` | When the exclusivity ends, as sent (`YYYYMMDD`). | text | `"20120722"` |
| `territory_countries` | Countries where it may be sold. | list | `["PL"]` |
| `territory_regions` | Regions where it may be sold. | list | `["WORLD"]` |
| `sale_restricted_to_poland` | It may be sold only in Poland. | yes or no | `true` |
| `alternative_format_record_references` | `record_reference` values of the same book in other formats: e-book, audiobook, printed book. | list | `["7d6c25db7d0624eac69b"]` |

## Supply and prices

| Field | Meaning | Type | Example |
|---|---|---|---|
| `supply_details` | Who supplies the product and on what terms. | list | see below |
| `supply_details[].supplier` | The supplier. | object | see below |
| `supply_details[].supplier.role` | Supplier role, as a code. | text | `"01"` |
| `supply_details[].supplier.role_name` | Name of the role. | text | `"PUB_TO_RET"` |
| `supply_details[].supplier.role_description` | Polish description of the role. | text | `"sprzedaż wydawnictwa do detalu"` |
| `supply_details[].supplier.vat_id` | VAT number, with the country prefix. | text | `"PL6782821670"` |
| `supply_details[].supplier.name` | Name of the supplier. | text | `"Tylko Bestsellery"` |
| `supply_details[].supplier.website` | Website, or a download link for open-access books. | text | `"https://www.elibri.com.pl/open-access/download/265a6c79a122…` |
| `supply_details[].product_availability` | Availability, as a code. | text | `"99"` |
| `supply_details[].product_availability_name` | Name of the availability. | text | `"CONTACT_SUPPLIER"` |
| `supply_details[].supplier_own_coding` | Short note from the supplier to the trade. | text | `"PROMO 20"` |
| `supply_details[].on_hand` | Copies in stock. | number | `1500` |
| `supply_details[].proximity` | How exact `on_hand` is, as a code. | text | `"03"` |
| `supply_details[].proximity_name` | `EXACTLY` or `MORE_THAN`. | text | `"EXACTLY"` |
| `supply_details[].pack_quantity` | Copies in the publisher's pack. | number | `18` |
| `supply_details[].unpriced_item_type` | Why there is no price, as a code; `01` means free of charge. | text | `"01"` |
| `supply_details[].prices` | Prices. | list | see below |
| `supply_details[].prices[].type` | Price type, as a code. | text | `"02"` |
| `supply_details[].prices[].type_name` | Name of the price type. | text | `"RRP_WITH_TAX"` |
| `supply_details[].prices[].qualifier` | Who the price is for; `05` is the consumer price. | text | `"05"` |
| `supply_details[].prices[].amount` | The price. For type `02` it includes tax. | number | `12.99` |
| `supply_details[].prices[].tax_type` | Tax type, as a code; `01` is VAT. | text | `"01"` |
| `supply_details[].prices[].vat` | VAT rate, in percent. | number | `5` |
| `supply_details[].prices[].currency_code` | Currency. | text | `"PLN"` |
| `supply_details[].prices[].printed_on_product` | Whether the price is printed on the product, as a code. | text | `"02"` |
| `supply_details[].prices[].printed_on_product_name` | `YES` or `NO`. | text | `"YES"` |
| `supply_details[].prices[].position_on_product` | Where the price is printed, as a code. | text | `"00"` |
| `supply_details[].prices[].price_date_type` | Meaning of the price date: `14` valid from, `15` valid until. | text | `"15"` |
| `supply_details[].prices[].price_date_value` | The price date. | date | `"2022-03-31"` |
| `cover_price` | Current consumer price, including tax. | number | `12.99` |
| `current_price_until` | Last day of `cover_price`, when a change is scheduled. | date | `"2022-03-31"` |
| `future_cover_price` | Price after a scheduled change. | number | `13.99` |
| `future_price_from` | First day of `future_cover_price`. | date | `"2022-04-01"` |
| `vat` | VAT rate of the consumer price, in percent. | number | `5` |
| `additional_trade_information` | Supplier's short note to the trade. | text | `"PROMO 20"` |
