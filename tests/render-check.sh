#!/usr/bin/env bash
#
# 端到端渲染检查：用无头 Chrome 加载真实页面，断言 JS 执行后的 DOM。
# 覆盖单元测试测不到的部分：脚本加载顺序、home.js 的 DOM 接线、相对路径。
#
# 用法：bash tests/render-check.sh

set -uo pipefail

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -x "$CHROME" ]; then
  echo "找不到 Chrome：$CHROME"
  exit 1
fi

pass=0
fail=0

# dump_dom <文件相对路径> —— 输出浏览器执行 JS 后的 DOM
dump_dom() {
  "$CHROME" --headless --disable-gpu --dump-dom "file://$ROOT/$1" 2>/dev/null
}

# check <描述> <期望出现次数> <实际内容> <匹配模式>
#
# 必须用 grep -o | wc -l 而不是 grep -c：渲染函数返回的 HTML 是单行字符串，
# 所有匹配项挤在同一行，grep -c 统计的是「匹配的行数」，永远只会返回 1。
# 注意：${desc} 必须带花括号。macOS 自带 bash 3.2，变量名后紧跟中文标点时
# 会把多字节字符的首字节当成变量名的一部分，从而报 unbound variable。
check() {
  local desc="$1" want="$2" haystack="$3" pattern="$4"
  local got
  got=$(printf '%s' "$haystack" | grep -o -- "$pattern" | wc -l | tr -d ' ')
  if [ "$got" = "$want" ]; then
    echo "  ✓ ${desc}"
    pass=$((pass + 1))
  else
    echo "  ✗ ${desc}（期望 ${want} 处，实际 ${got} 处）"
    fail=$((fail + 1))
  fi
}

echo "首页 render"
HOME_DOM=$(dump_dom index.html)
check "渲染出 3 条文章"            3 "$HOME_DOM" 'class="post-item"'
check "文章链接指向 posts/"        3 "$HOME_DOM" 'href="posts/'
check "渲染出 3 个标签按钮"        3 "$HOME_DOM" 'class="tag"'
check "标签按字母序，CSS 在最前"   1 "$HOME_DOM" 'data-tag="CSS"'
check "标题尖括号已转义"           1 "$HOME_DOM" 'Array&lt;T&gt;'
check "未泄漏原始尖括号"           0 "$HOME_DOM" 'Array<T>'
check "html 上写入了 data-theme"   1 "$HOME_DOM" 'data-theme="light"'
check "空状态默认隐藏"             1 "$HOME_DOM" 'id="empty-state" hidden=""'
check "引入了 main.css"            1 "$HOME_DOM" 'assets/css/main.css'
check "引入了 home.js"             1 "$HOME_DOM" 'assets/js/home.js'

echo "文章页 render"
POST_DOM=$(dump_dom posts/understanding-closures.html)
# 断言 h1 而非裸标题文本：同一标题在 <title> 里也会出现一次，裸匹配会数出 2 处。
check "正文标题已渲染"             1 "$POST_DOM" '<h1 class="post-header__title">理解闭包到底在讲什么</h1>'
check "代码块已渲染"               1 "$POST_DOM" 'class="post-body"'
check "上一篇/下一篇导航存在"      1 "$POST_DOM" 'class="post-nav"'
check "资源路径带 ../ 前缀"        1 "$POST_DOM" 'href="../assets/css/main.css"'
check "文章页也有主题按钮"         1 "$POST_DOM" 'id="theme-toggle"'
check "文章页也写入 data-theme"    1 "$POST_DOM" 'data-theme="light"'

echo "关于页 render"
ABOUT_DOM=$(dump_dom about.html)
check "关于页标题存在"             1 "$ABOUT_DOM" 'class="post-header__title"'
check "关于页样式已引入"           1 "$ABOUT_DOM" 'assets/css/post.css'
check "关于页也有主题按钮"         1 "$ABOUT_DOM" 'id="theme-toggle"'

echo "模板 render"
TPL_DOM=$(dump_dom template.html)
check "模板有主题按钮"             1 "$TPL_DOM" 'id="theme-toggle"'

echo
echo "通过 $pass 项，失败 $fail 项"
[ "$fail" -eq 0 ] || exit 1
