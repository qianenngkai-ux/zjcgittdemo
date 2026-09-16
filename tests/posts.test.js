const test = require('node:test');
const assert = require('node:assert');
const { POSTS } = require('../assets/js/posts.js');

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

test('POSTS 是非空数组', () => {
  assert.ok(Array.isArray(POSTS));
  assert.ok(POSTS.length > 0);
});

test('每篇文章都有全部必需字段且类型正确', () => {
  for (const p of POSTS) {
    assert.strictEqual(typeof p.slug, 'string', `slug 缺失: ${p.title}`);
    assert.strictEqual(typeof p.title, 'string');
    assert.strictEqual(typeof p.date, 'string');
    assert.strictEqual(typeof p.summary, 'string');
    assert.strictEqual(typeof p.readingTime, 'number');
    assert.ok(Array.isArray(p.tags), `tags 必须是数组: ${p.title}`);
  }
});

test('slug 唯一', () => {
  const slugs = POSTS.map(p => p.slug);
  assert.strictEqual(new Set(slugs).size, slugs.length, '存在重复 slug');
});

test('date 是 YYYY-MM-DD 格式', () => {
  for (const p of POSTS) {
    assert.match(p.date, ISO_DATE, `日期格式错误: ${p.title} -> ${p.date}`);
  }
});

test('每篇文章至少有一个标签', () => {
  for (const p of POSTS) {
    assert.ok(p.tags.length > 0, `没有标签: ${p.title}`);
  }
});
