#!/usr/bin/env bash
# 改了 index.html 里的中文后运行：按实际用字重新生成仓耳渔阳体子集 → assets/fonts/tsanger-yuyang-*.subset.woff2。
# 需要 fonttools 与 brotli，完整字体读取自 contexta-client。
set -euo pipefail
cd "$(dirname "$0")/.."
FULL="${CTXA_FONT_DIR:-../../../contexta-client/resources/fonts/full}"
CHARS="$(mktemp)"
python3 - "$CHARS" index.html <<'PY'
import sys
text = "".join(open(f, encoding="utf-8").read() for f in sys.argv[2:])
chars = {c for c in text if ord(c) > 127} | set('０１２３４５６７８９，。！？：；、「」『』（）《》—…·｜“”')
open(sys.argv[1], 'w', encoding='utf-8').write(''.join(sorted(chars)))
PY
for pair in "W02-400:400" "W05-700:700"; do
  pyftsubset "$FULL/tsanger-yuyang-${pair%%:*}.woff2" --text-file="$CHARS" --unicodes="U+0020-007E" \
    --flavor=woff2 --layout-features='*' --output-file="assets/fonts/tsanger-yuyang-${pair##*:}.subset.woff2"
done
rm -f "$CHARS"
echo "done"
