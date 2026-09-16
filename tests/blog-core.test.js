const test = require('node:test');
const assert = require('node:assert');
const {
  escapeHTML,
  sortByDateDesc,
  extractTags,
  filterByTag
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
