const test = require('node:test');
const assert = require('node:assert');
const {
  escapeHTML,
  sortByDateDesc,
  extractTags,
  filterByTag,
  parseTagFromHash,
  resolveTheme,
  renderTagBarHTML,
  renderPostListHTML
} = require('../assets/js/blog-core.js');

// ---- escapeHTML ----

test('escapeHTML 转义所有 HTML 特殊字符', () => {
  assert.strictEqual(
    escapeHTML('<script>alert("x")</script>'),
    '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;'
  );
});

test('escapeHTML 转义 & 和单引号', () => {
  assert.strictEqual(escapeHTML('a & b'), 'a &amp; b');
  assert.strictEqual(escapeHTML("it's"), 'it&#39;s');
});

test('escapeHTML 对普通文本原样返回', () => {
  assert.strictEqual(escapeHTML('普通文本 abc'), '普通文本 abc');
});

test('escapeHTML 对 null 和 undefined 返回空串', () => {
  assert.strictEqual(escapeHTML(null), '');
  assert.strictEqual(escapeHTML(undefined), '');
});

test('escapeHTML 把数字转成字符串', () => {
  assert.strictEqual(escapeHTML(42), '42');
});

// ---- sortByDateDesc ----

test('sortByDateDesc 按日期倒序排列', () => {
  const input = [
    { date: '2026-01-01', title: 'old' },
    { date: '2026-09-16', title: 'new' },
    { date: '2026-05-05', title: 'mid' }
  ];
  assert.deepStrictEqual(
    sortByDateDesc(input).map(p => p.title),
    ['new', 'mid', 'old']
  );
});

test('sortByDateDesc 不修改原数组', () => {
  const input = [{ date: '2026-01-01' }, { date: '2026-09-16' }];
  const before = input.map(p => p.date);
  sortByDateDesc(input);
  assert.deepStrictEqual(input.map(p => p.date), before);
});

// ---- extractTags ----

test('extractTags 去重并按中文拼音无关的字母序排列', () => {
  const posts = [
    { tags: ['JavaScript', 'CSS'] },
    { tags: ['JavaScript', 'TypeScript'] }
  ];
  assert.deepStrictEqual(extractTags(posts), ['CSS', 'JavaScript', 'TypeScript']);
});

test('extractTags 对空数组返回空数组', () => {
  assert.deepStrictEqual(extractTags([]), []);
});

// ---- filterByTag ----

test('filterByTag 返回含该标签的文章', () => {
  const posts = [
    { title: 'a', tags: ['JavaScript'] },
    { title: 'b', tags: ['CSS'] }
  ];
  assert.deepStrictEqual(filterByTag(posts, 'JavaScript').map(p => p.title), ['a']);
});

test('filterByTag 传入 null 或空串时返回全部', () => {
  const posts = [{ title: 'a', tags: ['JavaScript'] }];
  assert.strictEqual(filterByTag(posts, null).length, 1);
  assert.strictEqual(filterByTag(posts, '').length, 1);
  assert.strictEqual(filterByTag(posts, undefined).length, 1);
});

test('filterByTag 无匹配时返回空数组', () => {
  const posts = [{ title: 'a', tags: ['JavaScript'] }];
  assert.deepStrictEqual(filterByTag(posts, 'Rust'), []);
});

// ---- parseTagFromHash ----

test('parseTagFromHash 解析出标签', () => {
  assert.strictEqual(parseTagFromHash('#tag=JavaScript'), 'JavaScript');
});

test('parseTagFromHash 解码 URL 编码的标签', () => {
  assert.strictEqual(parseTagFromHash('#tag=C%2B%2B'), 'C++');
  assert.strictEqual(parseTagFromHash('#tag=%E5%B7%A5%E5%85%B7'), '工具');
});

test('parseTagFromHash 对空 hash 或无关 hash 返回 null', () => {
  assert.strictEqual(parseTagFromHash(''), null);
  assert.strictEqual(parseTagFromHash('#'), null);
  assert.strictEqual(parseTagFromHash('#other=1'), null);
});

test('parseTagFromHash 对 null 返回 null', () => {
  assert.strictEqual(parseTagFromHash(null), null);
});

// ---- resolveTheme ----

test('resolveTheme 优先采用已保存的主题', () => {
  assert.strictEqual(resolveTheme('dark', false), 'dark');
  assert.strictEqual(resolveTheme('light', true), 'light');
});

test('resolveTheme 无保存值时跟随系统偏好', () => {
  assert.strictEqual(resolveTheme(null, true), 'dark');
  assert.strictEqual(resolveTheme(null, false), 'light');
});

test('resolveTheme 忽略非法的保存值', () => {
  assert.strictEqual(resolveTheme('purple', true), 'dark');
  assert.strictEqual(resolveTheme('', false), 'light');
});

// ---- renderPostListHTML ----

const SAMPLE = [
  {
    slug: 'array-generics-pitfall',
    title: 'Array<T> 的类型陷阱',
    date: '2026-09-02',
    tags: ['TypeScript'],
    summary: '泛型协变 & 逆变',
    readingTime: 6
  }
];

test('renderPostListHTML 生成指向 posts/<slug>.html 的链接', () => {
  const html = renderPostListHTML(SAMPLE);
  assert.ok(html.includes('href="posts/array-generics-pitfall.html"'));
});

test('renderPostListHTML 转义标题中的尖括号（回归测试）', () => {
  const html = renderPostListHTML(SAMPLE);
  assert.ok(html.includes('Array&lt;T&gt; 的类型陷阱'), '标题未被转义');
  assert.ok(!html.includes('Array<T>'), '原始尖括号泄漏到 HTML 中');
});

test('renderPostListHTML 转义摘要中的 &', () => {
  const html = renderPostListHTML(SAMPLE);
  assert.ok(html.includes('泛型协变 &amp; 逆变'));
});

test('renderPostListHTML 输出 time 元素的 datetime 属性', () => {
  const html = renderPostListHTML(SAMPLE);
  assert.ok(html.includes('<time datetime="2026-09-02">2026-09-02</time>'));
});

test('renderPostListHTML 输出阅读时长', () => {
  assert.ok(renderPostListHTML(SAMPLE).includes('6 分钟'));
});

test('renderPostListHTML 对空数组返回空串', () => {
  assert.strictEqual(renderPostListHTML([]), '');
});

test('renderPostListHTML 渲染多个标签', () => {
  const post = Object.assign({}, SAMPLE[0], { tags: ['JavaScript', 'CSS'] });
  const html = renderPostListHTML([post]);
  assert.ok(html.includes('JavaScript'));
  assert.ok(html.includes('CSS'));
});

// ---- renderTagBarHTML ----

test('renderTagBarHTML 为每个标签生成按钮', () => {
  const html = renderTagBarHTML(['CSS', 'JavaScript'], null);
  assert.ok(html.includes('data-tag="CSS"'));
  assert.ok(html.includes('data-tag="JavaScript"'));
});

test('renderTagBarHTML 未选中时所有按钮 aria-pressed 为 false', () => {
  const html = renderTagBarHTML(['CSS'], null);
  assert.ok(html.includes('aria-pressed="false"'));
  assert.ok(!html.includes('aria-pressed="true"'));
});

test('renderTagBarHTML 选中项 aria-pressed 为 true 且仅有一个', () => {
  const html = renderTagBarHTML(['CSS', 'JavaScript'], 'JavaScript');
  const active = html.match(/aria-pressed="true"/g);
  assert.strictEqual(active.length, 1);
});

test('renderTagBarHTML 转义标签名', () => {
  const html = renderTagBarHTML(['a<b'], null);
  assert.ok(html.includes('a&lt;b'));
});
