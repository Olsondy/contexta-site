#!/usr/bin/env bash
# 修改页面中文文案后运行：按 index.html 与 assets/*.js 中实际用到的字符，重新生成仓耳渔阳体子集。
# 需要 fonttools（pip install fonttools brotli）与 contexta-client 仓库中的完整字体。
set -euo pipefail
cd "$(dirname "$0")/.."
FULL="${CTXA_FONT_DIR:-../contexta-client/resources/fonts/full}"
CHARS="$(mktemp)"
python3 - "$CHARS" <<'PY'
import sys
from pathlib import Path
text = Path('index.html').read_text(encoding='utf-8') + ''.join(
    path.read_text(encoding='utf-8') for path in sorted(Path('assets').glob('*.js'))
)
chars = {c for c in text if ord(c) > 127} | set('０１２３４５６７８９，。！？：；、「」『』（）《》—…·｜')
open(sys.argv[1], 'w', encoding='utf-8').write(''.join(sorted(chars)))
PY
for pair in "W02-400:400" "W05-700:700"; do
  pyftsubset "$FULL/tsanger-yuyang-${pair%%:*}.woff2" --text-file="$CHARS" --unicodes="U+0020-007E" \
    --flavor=woff2 --layout-features='*' --output-file="assets/fonts/tsanger-yuyang-${pair##*:}.subset.woff2"
done
rm -f "$CHARS"
echo "done"
