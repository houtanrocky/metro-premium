# Sharing and figure workflow

Do not publish Story A (price differences) or B (affordability/access comparisons) until validated empirical outputs exist. Story C may currently be illustrated only with a conspicuously conceptual example; the interactive graph is labeled synthetic and cannot be captioned as a Tehran finding.

An evidence-supported initial story is the dataset audit:

**Persian headline:** «قبل از پرسیدن قیمت خانه نزدیک مترو، باید مکان آگهی را بشناسیم.»

**Explanation:** «در ۸۴٬۵۸۶ آگهی فروش آپارتمان تهران در فایل رسمی دیوار، برای ۴۳٬۳۴۹ آگهی شعاع مکان ثبت نشده است. شایع‌ترین شعاعِ ثبت‌شده ۵۰۰ متر است. این عدم‌قطعیت، مقایسه فاصله تا مترو را دشوار می‌کند.»

**Scope/caveat:** Historical asking advertisements, not transactions or today's housing market. No metro price association is estimated. Counts refer to the entire category-selected source before period/area filtering.

**Figure:** `artifacts/figures/source-months.png` (2880×1440, actual source-month counts), with SVG companion. The graph shows month composition, not prices or the universe of all market listings. The website download button exports this exact precomputed PNG, not a screenshot with hidden different filters. The filename/caption should always say “source-month audit”; selecting a different on-screen audit view does not change that download.

**Persian alt text:** «نمودار شمار آگهی‌های فروش آپارتمان تهران بر حسب ماه؛ بیشتر نمونه در ماه‌های مه تا دسامبر ۲۰۲۴ است، اما ماه‌های دیگری نیز وجود دارند.»

Source: [official dataset](https://huggingface.co/datasets/divarofficial/real_estate_ads), pinned revision in the figure metadata/public JSON. Audit date: 22 October 2026; listing months are historical Gregorian months. Link a shared graphic to [findings](../research/findings.md) and [methodology](../research/methodology.md). Preserve ODbL/source attribution.

For future empirical stories, use an allowlisted export with headline, chart, actual n, month, source revision, method label, effect/interval where appropriate, caveat, alt text and technical link. `node scripts/task.mjs report` regenerates current audit figures. `node scripts/task.mjs smoke` emits separately labeled synthetic figures in its private run directory. Neither command posts anything to a social platform.
