#!/usr/bin/env bash
# 修改合成页中文后运行：按 comp*.html 中实际用到的字符，重新生成短片用的仓耳渔阳体子集（三个版本共用）。
# 需要 fonttools（pip install fonttools brotli）与 contexta-client 仓库中的完整字体。
set -euo pipefail
cd "$(dirname "$0")"
FULL="${CTXA_FONT_DIR:-../../contexta-client/resources/fonts/full}"
CHARS="$(mktemp)"
python3 - "$CHARS" comp*.html <<'PY'
import sys
text = ''.join(open(f, encoding='utf-8').read() for f in sys.argv[2:])
chars = {c for c in text if ord(c) > 127} | set('０１２３４５６７８９，。！？：；、「」『』（）《》—…·｜')
open(sys.argv[1], 'w', encoding='utf-8').write(''.join(sorted(chars)))
PY
for pair in "W02-400:400" "W05-700:700"; do
  pyftsubset "$FULL/tsanger-yuyang-${pair%%:*}.woff2" --text-file="$CHARS" --unicodes="U+0020-007E" \
    --flavor=woff2 --layout-features='*' --output-file="fonts/tsanger-yuyang-${pair##*:}.subset.woff2"
done
rm -f "$CHARS"
echo "done"
