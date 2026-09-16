# 个人技术博客 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个零依赖、零构建的中文个人技术博客，双击 HTML 即可预览。

**Architecture:** 每篇文章是 `posts/` 下一个独立 HTML 文件，正文手写。首页的文章列表与标签栏由 `assets/js/posts.js` 中的 `POSTS` 数组驱动，通过 `blog-core.js` 里的纯函数生成 HTML 字符串，`home.js` 负责插入 DOM。所有脚本用普通 `<script src>` 加载（非 ES Module），以保证 `file://` 协议下可用。

**Tech Stack:** HTML5 + CSS + 原生 JavaScript。无框架、无构建、无 CDN、无 npm 运行时依赖。测试用 Node 22 内置的 `node:test` 与无头 Chrome，均为本地已有工具。

**设计文档:** `docs/superpowers/specs/2026-09-16-personal-tech-blog-design.md`

---

## 环境前提

本机已确认可用：

- Node `v22.22.0` — 自带 `node:test` 与 `node:assert`，无需 npm install
- Chrome 位于 `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` — 支持 `--headless --dump-dom` 与 `--headless --screenshot`

下文所有命令均从项目根目录 `/Users/blood/demo` 执行。

## 文件结构

| 文件 | 职责 |
|---|---|
| `assets/js/blog-core.js` | 纯函数：文本转义、排序、标签提取、筛选、URL 解析、主题解析、HTML 字符串生成。**不接触 DOM**，因此可在 Node 中直接测试 |
| `assets/js/posts.js` | 唯一的文章数据源。作者唯一需要维护的数据文件 |
| `assets/js/theme.js` | 主题切换。必须同步执行以防 FOUC |
| `assets/js/home.js` | 首页 DOM 接线：读取 `POSTS`、调用 `blog-core.js` 的渲染函数、绑定标签点击 |
| `assets/css/main.css` | 设计令牌、页面骨架、导航、标签栏、文章列表、响应式 |
| `assets/css/post.css` | 文章正文排版（标题层级、段落、代码块、引用、图片、表格） |
| `index.html` | 首页 |
| `about.html` | 关于我 |
| `posts/<slug>.html` | 文章页 |
| `template.html` | 新文章模板 |
| `tests/blog-core.test.js` | `blog-core.js` 的单元测试 |
| `tests/posts.test.js` | 文章数据完整性测试 |
| `tests/render-check.sh` | 无头 Chrome 端到端渲染断言 |
| `README.md` | 发布一篇新文章的流程 |

### 关于 `module.exports` 守卫

`blog-core.js` 与 `posts.js` 末尾各有一行：

```js
if (typeof module !== 'undefined') module.exports = { /* ... */ };
```

浏览器中 `module` 不存在，该行被跳过，顶层的 `function` / `const` 声明自然成为全局，供后续 `<script>` 使用。Node 中 `module` 存在，函数被导出以便 `require()` 测试。这是让「无构建的浏览器脚本」同时可被 Node 测试的最小代价，只有一个判断语句。

---

## Task 1: 文章数据文件

**Files:**
- Create: `assets/js/posts.js`
- Test: `tests/posts.test.js`

- [ ] **Step 1: 写失败的测试**

创建 `tests/posts.test.js`：

```js
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
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
node --test tests/posts.test.js
```

预期：FAIL，报 `Cannot find module '../assets/js/posts.js'`

- [ ] **Step 3: 写数据文件**

创建 `assets/js/posts.js`：

```js
/**
 * 文章元数据 —— 本站唯一需要维护的数据文件。
 *
 * 新增一篇文章的步骤：
 *   1. 复制 template.html 到 posts/<slug>.html 并写正文
 *   2. 在下面的数组里加一条记录，slug 必须与文件名（去掉 .html）一致
 *
 * 首页的文章列表和标签栏都由此数组渲染。
 */
const POSTS = [
  {
    slug: 'understanding-closures',
    title: '理解闭包到底在讲什么',
    date: '2026-09-16',
    tags: ['JavaScript'],
    summary: '从作用域链说起，聊聊闭包到底解决了什么问题，以及为什么它不只是「函数套函数」。',
    readingTime: 5
  },
  {
    slug: 'css-grid-tricks',
    title: 'Grid 布局的五个实用技巧',
    date: '2026-09-10',
    tags: ['CSS'],
    summary: '自动填充、负网格线、子网格——这些特性让 Grid 从「能用」变成「好用」。',
    readingTime: 8
  },
  {
    slug: 'array-generics-pitfall',
    title: 'Array<T> 与 Array<U> 的类型陷阱',
    date: '2026-09-02',
    tags: ['TypeScript', 'JavaScript'],
    summary: '泛型协变听起来很抽象，但它真的会让你的代码在运行时炸掉。',
    readingTime: 6
  }
];

// Node 测试用；浏览器中 module 未定义，此行跳过，POSTS 自然成为全局变量。
if (typeof module !== 'undefined') module.exports = { POSTS };
```

注意第三篇文章的标题里含有 `<T>` 与 `<U>`，这是**刻意**的——它会在 Task 4 中验证 `escapeHTML` 确实生效。同时 `JavaScript` 标签出现两次，用于验证标签去重。

- [ ] **Step 4: 运行测试，确认通过**

```bash
node --test tests/posts.test.js
```

预期：PASS，5 个测试全部通过。

- [ ] **Step 5: 提交**

```bash
git add assets/js/posts.js tests/posts.test.js
git commit -m "feat: 添加文章数据文件与完整性测试"
```

---

## Task 2: blog-core —— 转义与数据加工

**Files:**
- Create: `assets/js/blog-core.js`
- Test: `tests/blog-core.test.js`

- [ ] **Step 1: 写失败的测试**

创建 `tests/blog-core.test.js`：

```js
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
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
node --test tests/blog-core.test.js
```

预期：FAIL，报 `Cannot find module '../assets/js/blog-core.js'`

- [ ] **Step 3: 写实现**

创建 `assets/js/blog-core.js`：

```js
/**
 * blog-core —— 纯函数集合。
 *
 * 本文件不接触 DOM、不读取全局状态，因此既能在浏览器中作为
 * 普通脚本加载，也能被 Node 的测试直接 require。
 *
 * 浏览器中这些函数是全局的，供 theme.js / home.js 调用。
 */

/**
 * 转义 HTML 特殊字符。
 * 文章标题里出现 Array<T> 这类内容时必须转义，否则会破坏页面结构。
 */
function escapeHTML(value) {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * 按 date 字段倒序排列，返回新数组，不修改传入的数组。
 */
function sortByDateDesc(posts) {
  return posts.slice().sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0));
}

/**
 * 从所有文章中提取去重后的标签全集，按字母序排列。
 */
function extractTags(posts) {
  const seen = new Set();
  for (const post of posts) {
    for (const tag of post.tags || []) seen.add(tag);
  }
  return Array.from(seen).sort();
}

/**
 * 筛选含指定标签的文章。tag 为空时返回全部文章。
 */
function filterByTag(posts, tag) {
  if (!tag) return posts.slice();
  return posts.filter(post => (post.tags || []).includes(tag));
}

// Node 测试用；浏览器中 module 未定义，此行跳过。
if (typeof module !== 'undefined') {
  module.exports = { escapeHTML, sortByDateDesc, extractTags, filterByTag };
}
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
node --test tests/blog-core.test.js
```

预期：PASS，12 个测试全部通过。

- [ ] **Step 5: 提交**

```bash
git add assets/js/blog-core.js tests/blog-core.test.js
git commit -m "feat: 添加 blog-core 转义与数据加工函数"
```

---

## Task 3: blog-core —— URL 状态与主题解析

**Files:**
- Modify: `assets/js/blog-core.js`（在 `module.exports` 之前插入函数，并更新导出列表）
- Test: `tests/blog-core.test.js`（追加）

- [ ] **Step 1: 写失败的测试**

在 `tests/blog-core.test.js` 末尾追加：

```js
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
```

同时把文件顶部的 require 解构补上这两个函数：

```js
const {
  escapeHTML,
  sortByDateDesc,
  extractTags,
  filterByTag,
  parseTagFromHash,
  resolveTheme
} = require('../assets/js/blog-core.js');
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
node --test tests/blog-core.test.js
```

预期：FAIL，`parseTagFromHash is not a function`

- [ ] **Step 3: 写实现**

在 `assets/js/blog-core.js` 的 `filterByTag` 之后、`module.exports` 之前插入：

```js
/**
 * 从 URL hash 中解析标签，形如 #tag=JavaScript。
 * 无标签或格式不符时返回 null。
 */
function parseTagFromHash(hash) {
  if (!hash || typeof hash !== 'string') return null;
  const match = hash.match(/^#tag=(.+)$/);
  if (!match) return null;
  try {
    return decodeURIComponent(match[1]);
  } catch (err) {
    return null; // hash 中含非法百分号编码
  }
}

/**
 * 决定当前应使用的主题。
 * 用户的显式选择优先于系统偏好。
 */
function resolveTheme(storedTheme, prefersDark) {
  if (storedTheme === 'dark' || storedTheme === 'light') return storedTheme;
  return prefersDark ? 'dark' : 'light';
}
```

并把该文件末尾的导出更新为：

```js
if (typeof module !== 'undefined') {
  module.exports = {
    escapeHTML,
    sortByDateDesc,
    extractTags,
    filterByTag,
    parseTagFromHash,
    resolveTheme
  };
}
```

- [ ] **Step 4: 运行全部测试，确认通过**

```bash
node --test tests/
```

预期：PASS，24 个测试通过（posts 5 个 + blog-core 19 个）。

- [ ] **Step 5: 提交**

```bash
git add assets/js/blog-core.js tests/blog-core.test.js
git commit -m "feat: 添加 URL 标签解析与主题解析函数"
```

---

## Task 4: blog-core —— HTML 渲染函数

**Files:**
- Modify: `assets/js/blog-core.js`
- Test: `tests/blog-core.test.js`（追加）

这两个函数返回 HTML **字符串**而非操作 DOM，因此可以在 Node 中直接断言输出。

- [ ] **Step 1: 写失败的测试**

在 `tests/blog-core.test.js` 末尾追加，并把顶部 require 解构补上 `renderPostListHTML, renderTagBarHTML`：

```js
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
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
node --test tests/blog-core.test.js
```

预期：FAIL，`renderPostListHTML is not a function`

- [ ] **Step 3: 写实现**

在 `assets/js/blog-core.js` 的 `resolveTheme` 之后、`module.exports` 之前插入：

```js
/**
 * 生成标签栏的 HTML 字符串。
 * activeTag 对应的按钮 aria-pressed="true"，其余为 "false"。
 */
function renderTagBarHTML(tags, activeTag) {
  return tags
    .map(tag => {
      const pressed = tag === activeTag ? 'true' : 'false';
      return (
        `<button class="tag" type="button" data-tag="${escapeHTML(tag)}" aria-pressed="${pressed}">` +
        `${escapeHTML(tag)}</button>`
      );
    })
    .join('');
}

/**
 * 生成文章列表的 HTML 字符串。
 */
function renderPostListHTML(posts) {
  return posts
    .map(post => {
      const tags = (post.tags || [])
        .map(tag => `<span class="post-tag">${escapeHTML(tag)}</span>`)
        .join('');

      return (
        `<li class="post-item">` +
        `<a class="post-item__link" href="posts/${escapeHTML(post.slug)}.html">` +
        `<div class="post-meta">` +
        `<time datetime="${escapeHTML(post.date)}">${escapeHTML(post.date)}</time>` +
        `<span class="post-meta__sep">·</span>` +
        tags +
        `<span class="post-meta__sep">·</span>` +
        `<span class="post-item__reading">${escapeHTML(post.readingTime)} 分钟</span>` +
        `</div>` +
        `<h2 class="post-item__title">${escapeHTML(post.title)}</h2>` +
        `<p class="post-item__summary">${escapeHTML(post.summary)}</p>` +
        `</a>` +
        `</li>`
      );
    })
    .join('');
}
```

并把导出更新为：

```js
if (typeof module !== 'undefined') {
  module.exports = {
    escapeHTML,
    sortByDateDesc,
    extractTags,
    filterByTag,
    parseTagFromHash,
    resolveTheme,
    renderTagBarHTML,
    renderPostListHTML
  };
}
```

- [ ] **Step 4: 运行全部测试，确认通过**

```bash
node --test tests/
```

预期：PASS，35 个测试通过（posts 5 个 + blog-core 30 个）。

- [ ] **Step 5: 提交**

```bash
git add assets/js/blog-core.js tests/blog-core.test.js
git commit -m "feat: 添加文章列表与标签栏的 HTML 渲染函数"
```

---

## Task 5: 首页结构与 home.js 接线

**Files:**
- Create: `index.html`
- Create: `assets/js/home.js`

- [ ] **Step 1: 写 index.html**

创建 `index.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>我的技术博客</title>
  <link rel="stylesheet" href="assets/css/main.css">
  <!-- 顺序不可调换：blog-core 提供函数，posts 提供数据，theme 依赖 blog-core -->
  <script src="assets/js/blog-core.js"></script>
  <script src="assets/js/posts.js"></script>
  <script src="assets/js/theme.js"></script>
</head>
<body>
  <header class="site-header">
    <div class="container site-header__inner">
      <a class="site-title" href="index.html">我的技术博客</a>
      <nav class="site-nav">
        <a class="site-nav__link" href="about.html">关于</a>
        <button class="theme-toggle" type="button" id="theme-toggle" aria-label="切换主题"></button>
      </nav>
    </div>
  </header>

  <main class="container">
    <div class="tag-bar" id="tag-bar" role="group" aria-label="按标签筛选"></div>
    <ul class="post-list" id="post-list"></ul>
    <p class="empty-state" id="empty-state" hidden>这个标签下还没有文章。</p>
  </main>

  <footer class="site-footer">
    <div class="container"><p>© 2026 我的技术博客</p></div>
  </footer>

  <script src="assets/js/home.js"></script>
</body>
</html>
```

注意 `theme.js` 在 `<head>` 中，且**不加 `defer`/`async`** —— 这是防 FOUC 的关键。`home.js` 放在 `</body>` 前，因为 DOM 需要先存在。

- [ ] **Step 2: 写 home.js**

创建 `assets/js/home.js`：

```js
/**
 * 首页接线：把 blog-core 生成的 HTML 插入 DOM，并绑定标签筛选交互。
 */
(function () {
  'use strict';

  const listEl = document.getElementById('post-list');
  const tagBarEl = document.getElementById('tag-bar');
  const emptyEl = document.getElementById('empty-state');

  const allTags = extractTags(POSTS);
  const sorted = sortByDateDesc(POSTS);

  let activeTag = parseTagFromHash(window.location.hash);

  // 如果 hash 里的标签已不存在（比如文章被删或改名），忽略它
  if (activeTag && !allTags.includes(activeTag)) activeTag = null;

  function render() {
    const visible = filterByTag(sorted, activeTag);

    tagBarEl.innerHTML = renderTagBarHTML(allTags, activeTag);
    listEl.innerHTML = renderPostListHTML(visible);
    emptyEl.hidden = visible.length > 0;
  }

  function setActiveTag(tag) {
    activeTag = tag;

    // 用 replaceState 避免每次点击都往历史记录里塞一条。
    // 已在 Chrome 的 file:// 下实测可用；但 file:// 属于不透明源，
    // 个别浏览器会在此抛 SecurityError，故退回直接改 hash——
    // 代价是每次点击多一条历史记录，功能本身不受影响。
    const url = tag
      ? window.location.pathname + '#tag=' + encodeURIComponent(tag)
      : window.location.pathname;
    try {
      window.history.replaceState(null, '', url);
    } catch (err) {
      window.location.hash = tag ? 'tag=' + encodeURIComponent(tag) : '';
    }

    render();
  }

  tagBarEl.addEventListener('click', function (event) {
    const button = event.target.closest('.tag');
    if (!button) return;
    const tag = button.dataset.tag;
    // 点击已选中的标签则取消筛选
    setActiveTag(tag === activeTag ? null : tag);
  });

  render();
})();
```

- [ ] **Step 3: 验证脚本顺序与全局可见性**

```bash
node --test tests/
```

预期：PASS（确认没有改坏已有函数）。

- [ ] **Step 4: 提交**

```bash
git add index.html assets/js/home.js
git commit -m "feat: 添加首页结构与列表渲染接线"
```

---

## Task 6: main.css —— 设计令牌与页面布局

**Files:**
- Create: `assets/css/main.css`

- [ ] **Step 1: 写样式**

创建 `assets/css/main.css`：

```css
/* ===== 设计令牌 ===== */
:root {
  --bg: #ffffff;
  --bg-subtle: #f6f7f9;
  --text: #1a1a1a;
  --text-muted: #6b7280;
  --border: #e5e7eb;
  --accent: #2563eb;
  --accent-hover: #1d4ed8;

  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;

  --measure: 42rem;
  --radius: 6px;
  --transition: 150ms ease;
}

[data-theme="dark"] {
  --bg: #0f1115;
  --bg-subtle: #171a21;
  --text: #e6e6e6;
  --text-muted: #9ca3af;
  --border: #262b36;
  --accent: #60a5fa;
  --accent-hover: #93c5fd;
}

/* ===== 基础 ===== */
*,
*::before,
*::after { box-sizing: border-box; }

html { -webkit-text-size-adjust: 100%; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  font-size: 17px;
  line-height: 1.7;
  transition: background-color var(--transition), color var(--transition);
}

a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-hover); }

/* 键盘焦点可见，鼠标点击不显示外框 */
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
  border-radius: 2px;
}

.container {
  max-width: var(--measure);
  margin: 0 auto;
  padding: 0 1.25rem;
}

/* ===== 页头 ===== */
.site-header {
  border-bottom: 1px solid var(--border);
  padding: 1.5rem 0;
}

.site-header__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.site-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
}
.site-title:hover { color: var(--accent); }

.site-nav {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.site-nav__link { color: var(--text-muted); font-size: 0.95rem; }
.site-nav__link:hover { color: var(--accent); }

.theme-toggle {
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0.35rem 0.5rem;
  transition: border-color var(--transition), background-color var(--transition);
}
.theme-toggle:hover { border-color: var(--accent); }

/* ===== 标签栏 ===== */
.tag-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 2rem 0 1rem;
}

.tag {
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.85rem;
  padding: 0.25rem 0.75rem;
  transition: all var(--transition);
}
.tag:hover { border-color: var(--accent); color: var(--accent); }

.tag[aria-pressed="true"] {
  background: var(--accent);
  border-color: var(--accent);
  color: #ffffff;
}

/* ===== 文章列表 ===== */
.post-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.post-item { border-top: 1px solid var(--border); }

.post-item__link {
  display: block;
  padding: 1.75rem 0;
  color: inherit;
}
.post-item__link:hover { color: inherit; }

.post-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-bottom: 0.4rem;
}

.post-meta__sep { color: var(--border); }
.post-tag { color: var(--text-muted); }

.post-item__title {
  font-size: 1.3rem;
  line-height: 1.4;
  margin: 0 0 0.4rem;
  transition: color var(--transition);
}
.post-item__link:hover .post-item__title { color: var(--accent); }

.post-item__summary {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin: 0;
}

.empty-state {
  color: var(--text-muted);
  padding: 2rem 0;
  text-align: center;
}

/* ===== 页脚 ===== */
.site-footer {
  border-top: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-top: 3rem;
  padding: 2rem 0;
}
.site-footer p { margin: 0; }

/* ===== 响应式 ===== */
@media (max-width: 480px) {
  body { font-size: 16px; }
  .post-item__title { font-size: 1.15rem; }
  .site-header { padding: 1.25rem 0; }
}

/* ===== 尊重系统的减少动效设置 ===== */
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}
```

- [ ] **Step 2: 截图检查页面外观**

```bash
mkdir -p /tmp/blog-shots
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --window-size=900,1200 \
  --screenshot=/tmp/blog-shots/home-light.png \
  "file:///Users/blood/demo/index.html" 2>/dev/null
```

然后用 Read 工具打开 `/tmp/blog-shots/home-light.png` 查看。

预期：能看到站点标题、导航、「关于」链接、标签栏（CSS / JavaScript / TypeScript 三个标签）、以及三条文章列表，日期与标签在标题上方一行灰色小字。第三篇标题应显示为 `Array<T> 与 Array<U> 的类型陷阱`（尖括号正常显示，未被转义吃掉，也没有破坏布局）。

若列表为空，说明 `home.js` 或脚本加载顺序有问题——检查控制台：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --enable-logging=stderr --v=0 \
  --dump-dom "file:///Users/blood/demo/index.html" 2>&1 >/dev/null | grep -iE 'error|refused|undefined' | head -20
```

- [ ] **Step 3: 提交**

```bash
git add assets/css/main.css
git commit -m "feat: 添加设计令牌与页面布局样式"
```

---

## Task 7: 主题切换

**Files:**
- Create: `assets/js/theme.js`
- Modify: `assets/css/main.css`（追加图标切换规则）

- [ ] **Step 1: 写 theme.js**

创建 `assets/js/theme.js`：

```js
/**
 * 主题切换。
 *
 * 本文件在 <head> 中同步加载（无 defer/async），因为在解析 <body> 之前
 * 就必须把 data-theme 写到 <html> 上，否则页面会先以浅色渲染一帧再切换，
 * 产生白屏闪烁（FOUC）。
 *
 * 依赖：blog-core.js（resolveTheme）必须先加载。
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'blog-theme';
  var root = document.documentElement;

  function readStoredTheme() {
    try {
      return window.localStorage.getItem(STORAGE_KEY);
    } catch (err) {
      return null; // 隐私模式等场景下 localStorage 可能抛异常
    }
  }

  function prefersDark() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  // ---- 立即执行：在首帧渲染前定好主题 ----
  var theme = resolveTheme(readStoredTheme(), prefersDark());
  root.setAttribute('data-theme', theme);

  function updateButton(button) {
    // 按钮显示的是「点击后会变成什么」，而不是当前状态
    button.textContent = theme === 'dark' ? '☀️' : '🌙';
    button.setAttribute('aria-label', theme === 'dark' ? '切换到浅色主题' : '切换到深色主题');
  }

  // ---- 按钮此时还不存在，等 DOM 就绪后再绑定 ----
  document.addEventListener('DOMContentLoaded', function () {
    var button = document.getElementById('theme-toggle');
    if (!button) return;

    updateButton(button);

    button.addEventListener('click', function () {
      theme = theme === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', theme);
      try {
        window.localStorage.setItem(STORAGE_KEY, theme);
      } catch (err) {
        // 存不进去也不影响本次切换
      }
      updateButton(button);
    });
  });
})();
```

- [ ] **Step 2: 验证默认主题被正确写入**

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --dump-dom "file:///Users/blood/demo/index.html" 2>/dev/null \
  | grep -o '<html[^>]*data-theme="[^"]*"' | head -1
```

预期：输出 `<html lang="zh-CN" data-theme="light"`（无头 Chrome 默认浅色偏好）。

- [ ] **Step 3: 验证深色主题下的渲染**

```bash
mkdir -p /tmp/blog-shots
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --window-size=900,1200 \
  --force-dark-mode --enable-features=WebContentsForceDark \
  --screenshot=/tmp/blog-shots/home-dark.png \
  "file:///Users/blood/demo/index.html" 2>/dev/null
```

用 Read 工具查看 `/tmp/blog-shots/home-dark.png`。

预期：页面为深色背景、浅色文字。

若该 flag 组合未能触发 `prefers-color-scheme: dark`，改用下面的方法强制验证：临时把 `index.html` 里的 `data-theme` 属性手写成 `dark`，截图确认配色无误后改回。CSS 变量本身的正误与触发方式无关，两种路径都能验证到。

- [ ] **Step 4: 提交**

```bash
git add assets/js/theme.js
git commit -m "feat: 添加主题切换与防 FOUC 的首帧初始化"
```

---

## Task 8: 文章页样式与模板

**Files:**
- Create: `assets/css/post.css`
- Create: `template.html`

- [ ] **Step 1: 写 post.css**

创建 `assets/css/post.css`：

```css
/* ===== 文章页正文排版 ===== */

.post-header { padding: 2.5rem 0 1.5rem; }

.post-header__title {
  font-size: 1.9rem;
  line-height: 1.35;
  margin: 0 0 0.75rem;
}

.back-link {
  color: var(--text-muted);
  display: inline-block;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}
.back-link:hover { color: var(--accent); }

.post-body { padding-bottom: 1rem; }

.post-body h2 {
  font-size: 1.4rem;
  line-height: 1.4;
  margin: 2.5rem 0 0.75rem;
}

.post-body h3 {
  font-size: 1.15rem;
  line-height: 1.4;
  margin: 2rem 0 0.6rem;
}

.post-body p { margin: 0 0 1.25rem; }

.post-body ul,
.post-body ol { margin: 0 0 1.25rem; padding-left: 1.5rem; }
.post-body li { margin-bottom: 0.4rem; }

.post-body img {
  border-radius: var(--radius);
  display: block;
  height: auto;
  margin: 1.75rem 0;
  max-width: 100%;
}

.post-body blockquote {
  border-left: 3px solid var(--border);
  color: var(--text-muted);
  margin: 1.75rem 0;
  padding: 0.25rem 0 0.25rem 1.25rem;
}
.post-body blockquote p:last-child { margin-bottom: 0; }

/* 行内代码 */
.post-body code {
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.88em;
  padding: 0.1em 0.35em;
}

/* 代码块：深色底 + 横向滚动，不做语法高亮 */
.post-body pre {
  background: #1e1e24;
  border-radius: var(--radius);
  color: #e5e7eb;
  font-size: 0.88rem;
  line-height: 1.6;
  margin: 1.75rem 0;
  overflow-x: auto;
  padding: 1.1rem 1.25rem;
}

.post-body pre code {
  background: none;
  border: none;
  color: inherit;
  font-size: inherit;
  padding: 0;
}

.post-body table {
  border-collapse: collapse;
  display: block;
  margin: 1.75rem 0;
  overflow-x: auto;
  width: 100%;
}
.post-body th,
.post-body td {
  border: 1px solid var(--border);
  padding: 0.5rem 0.75rem;
  text-align: left;
}
.post-body th { background: var(--bg-subtle); }

.post-body hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2.5rem 0;
}

/* ===== 上一篇 / 下一篇 ===== */
.post-nav {
  border-top: 1px solid var(--border);
  display: flex;
  gap: 1rem;
  justify-content: space-between;
  margin-top: 3rem;
  padding: 1.5rem 0;
}
.post-nav a { max-width: 48%; }
.post-nav__label {
  color: var(--text-muted);
  display: block;
  font-size: 0.8rem;
  margin-bottom: 0.2rem;
}
.post-nav__next { margin-left: auto; text-align: right; }

@media (max-width: 480px) {
  .post-header__title { font-size: 1.5rem; }
  .post-body h2 { font-size: 1.25rem; }
}
```

- [ ] **Step 2: 写 template.html**

创建 `template.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- 改这里：文章标题 -->
  <title>文章标题 — 我的技术博客</title>
  <link rel="stylesheet" href="assets/css/main.css">
  <link rel="stylesheet" href="assets/css/post.css">
  <script src="assets/js/blog-core.js"></script>
  <script src="assets/js/posts.js"></script>
  <script src="assets/js/theme.js"></script>
</head>
<body>
  <header class="site-header">
    <div class="container site-header__inner">
      <a class="site-title" href="../index.html">我的技术博客</a>
      <nav class="site-nav">
        <a class="site-nav__link" href="../about.html">关于</a>
        <button class="theme-toggle" type="button" id="theme-toggle" aria-label="切换主题"></button>
      </nav>
    </div>
  </header>

  <main class="container">
    <article>
      <a class="back-link" href="../index.html">← 返回首页</a>

      <header class="post-header">
        <!-- 改这里：标题 -->
        <h1 class="post-header__title">文章标题</h1>
        <div class="post-meta">
          <!-- 改这里：日期 -->
          <time datetime="2026-01-01">2026-01-01</time>
          <span class="post-meta__sep">·</span>
          <!-- 改这里：标签，可有多个 -->
          <span class="post-tag">标签</span>
          <span class="post-meta__sep">·</span>
          <!-- 改这里：阅读时长 -->
          <span>5 分钟</span>
        </div>
      </header>

      <div class="post-body">
        <!-- 改这里：正文 -->
        <p>正文从这里开始。</p>

        <h2>二级标题</h2>
        <p>段落文字。<code>行内代码</code> 长这样。</p>

        <pre><code>// 代码块长这样，深色底、可横向滚动
const answer = 42;</code></pre>

        <blockquote><p>引用长这样。</p></blockquote>

        <ul>
          <li>无序列表项</li>
          <li>另一项</li>
        </ul>
        <!-- 正文结束 -->
      </div>
    </article>

    <nav class="post-nav">
      <!-- 改这里：上一篇 / 下一篇链接，没有就删掉对应的 <a> -->
      <a href="../index.html">
        <span class="post-nav__label">← 上一篇</span>
        <span>上一篇标题</span>
      </a>
      <a class="post-nav__next" href="../index.html">
        <span class="post-nav__label">下一篇 →</span>
        <span>下一篇标题</span>
      </a>
    </nav>
  </main>

  <footer class="site-footer">
    <div class="container"><p>© 2026 我的技术博客</p></div>
  </footer>
</body>
</html>
```

**注意模板中的相对路径**：本文件在项目根目录，而复制后的文章在 `posts/` 下，所以模板里的路径都写成 `../` 前缀（`../index.html`、`../about.html`、`../assets/...`）。上面给出的已经是正确的文章页路径，直接复制即可用。

- [ ] **Step 3: 提交**

```bash
git add assets/css/post.css template.html
git commit -m "feat: 添加文章正文排版样式与新文章模板"
```

---

## Task 9: 示例文章

**Files:**
- Create: `posts/understanding-closures.html`
- Create: `posts/css-grid-tricks.html`
- Create: `posts/array-generics-pitfall.html`

- [ ] **Step 1: 写第一篇**

复制 `template.html` 为 `posts/understanding-closures.html`，替换标题、元信息、正文：

- `<title>` → `理解闭包到底在讲什么 — 我的技术博客`
- `<h1 class="post-header__title">` → `理解闭包到底在讲什么`
- `<time datetime="2026-09-16">2026-09-16</time>`
- 标签 → `JavaScript`
- 阅读时长 → `5 分钟`

正文用下面内容替换 `<div class="post-body">` 内部：

```html
<p>提到闭包，最常见的解释是「函数里套函数，内层函数能访问外层函数的变量」。这句话没错，但它只描述了现象，没解释为什么这件事值得单独有个名字。</p>

<h2>从作用域链说起</h2>
<p>JavaScript 的函数在<strong>定义时</strong>就确定了自己的作用域链，而不是调用时。这意味着内层函数无论被带到哪里执行，它记住的始终是定义位置的外层变量。</p>

<pre><code>function makeCounter() {
  let count = 0;
  return function () {
    count += 1;
    return count;
  };
}

const next = makeCounter();
next(); // 1
next(); // 2</code></pre>

<p>函数返回之后，<code>makeCounter</code> 的局部变量 <code>count</code> 本该被回收，但它没有。因为返回的那个函数仍然引用着它——这就是闭包。</p>

<h2>它到底解决了什么</h2>
<p>在模块和 <code>let</code> 出现之前，闭包是 JavaScript 里唯一的「私有变量」方案。它让数据可以被一组函数共享，又不暴露到全局。</p>
<p>另一个常见用途是固定循环变量的值：</p>

<pre><code>// 全部输出 3（var 是函数作用域，共享同一个变量）
for (var i = 0; i &lt; 3; i++) {
  setTimeout(() => console.log(i));
}

// 输出 0 1 2（每次迭代都有新的绑定）
for (let i = 0; i &lt; 3; i++) {
  setTimeout(() => console.log(i));
}</code></pre>

<h2>代价</h2>
<p>闭包会让被引用的变量无法被垃圾回收。绝大多数情况下这不是问题，但如果你在一个长生命周期的事件回调里闭包了一个大对象，那块内存就一直不会释放。</p>
<p>诊断方法很直接：在 DevTools 的 Memory 面板里拍两次快照，对比找那些「本该消失却没消失」的对象。</p>
```

同时把底部的 `post-nav` 改为：上一篇指向 `array-generics-pitfall.html`，下一篇指向 `css-grid-tricks.html`。

注意代码块里的 `<` 必须写成 `&lt;`，否则浏览器会把它当成标签开始。

- [ ] **Step 2: 写第二篇**

复制 `template.html` 为 `posts/css-grid-tricks.html`：

- `<title>` → `Grid 布局的五个实用技巧 — 我的技术博客`
- `<h1>` → `Grid 布局的五个实用技巧`
- 日期 → `2026-09-10`
- 标签 → `CSS`
- 阅读时长 → `8 分钟`

正文用下面内容替换 `<div class="post-body">` 内部：

```html
<p>Flexbox 解决一维排布，Grid 解决二维。但多数人对 Grid 的用法停留在 <code>grid-template-columns: repeat(3, 1fr)</code>，没用上它真正省事的那几个特性。</p>

<h2>1. auto-fit 代替媒体查询</h2>
<p>不需要为「平板上两列、手机上单列」写断点，交给浏览器算：</p>

<pre><code>.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}</code></pre>

<p>容器放得下几个 240px 的列，就排几列。窗口一缩，列数自动减少。</p>

<h2>2. 负网格线</h2>
<p><code>-1</code> 永远代表最后一条网格线，不管实际有多少列。这让「撑满整行」不依赖具体的列数：</p>

<pre><code>.full-bleed {
  grid-column: 1 / -1;
}</code></pre>

<h2>3. 用 gap 代替 margin</h2>
<p><code>gap</code> 只作用于项目之间，不会在最外侧产生多余间距。以前用 <code>margin-right</code> 再给最后一个子元素写 <code>:last-child { margin-right: 0 }</code> 的做法可以彻底删掉。</p>

<h2>4. 网格区域命名</h2>
<p>用 <code>grid-template-areas</code> 画 ASCII 图，比记行列号可读得多，改版式时也只需要挪动那几个单词：</p>

<pre><code>.layout {
  display: grid;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  grid-template-columns: 200px 1fr;
}

.layout > header { grid-area: header; }
.layout > aside  { grid-area: sidebar; }
.layout > main   { grid-area: main; }</code></pre>

<h2>5. minmax 与 auto 配合</h2>
<p>侧边栏固定宽度在窄屏会挤扁主内容。<code>minmax(200px, auto)</code> 让它有下限也能撑开：</p>

<pre><code>grid-template-columns: minmax(200px, auto) 1fr;</code></pre>

<h2>小结</h2>
<p>这几个特性都不需要 JavaScript，也不需要预处理器。Grid 的能力比大多数人日常用到的多得多。</p>
```

`post-nav`：上一篇指向 `understanding-closures.html`，下一篇指向 `array-generics-pitfall.html`。

- [ ] **Step 3: 写第三篇**

复制 `template.html` 为 `posts/array-generics-pitfall.html`：

- `<title>` → `Array&lt;T&gt; 与 Array&lt;U&gt; 的类型陷阱 — 我的技术博客`（标题里含尖括号，在 HTML 源码里必须转义）
- `<h1>` → `Array&lt;T&gt; 与 Array&lt;U&gt; 的类型陷阱`
- 日期 → `2026-09-02`
- 标签 → `TypeScript` 和 `JavaScript` 两个 `<span class="post-tag">`
- 阅读时长 → `6 分钟`

正文用下面内容替换 `<div class="post-body">` 内部：

```html
<p>泛型的协变与逆变是 TypeScript 里最容易被跳过的一节。跳过它的代价是：某天你会写出一段编译通过、运行时报错的代码。</p>

<h2>数组是协变的，这是个问题</h2>
<p>TypeScript 默认认为数组是协变的：如果 <code>Dog</code> 是 <code>Animal</code> 的子类型，那么 <code>Array&lt;Dog&gt;</code> 也可以赋给 <code>Array&lt;Animal&gt;</code>。</p>

<pre><code>interface Animal { name: string }
interface Dog extends Animal { bark(): void }

const dogs: Dog[] = [{ name: 'Rex', bark() {} }];
const animals: Animal[] = dogs;  // 编译通过

animals.push({ name: 'Cat' });   // 编译通过
dogs[1].bark();                  // 运行时崩溃：bark is not a function</code></pre>

<p>问题出在最后一行——<code>dogs</code> 里混进了一个没有 <code>bark</code> 的对象。类型系统本该拦住这件事。</p>

<h2>为什么 TypeScript 允许</h2>
<p>这是为实用性做的妥协。数组的可读用法（遍历、<code>map</code>）远多于可写用法，如果严格用不变（invariant）处理，大量正常代码会报错。官方在文档里称这是「刻意的不健全」。</p>

<h2>怎么规避</h2>
<p>需要可写时，用 <code>readonly</code> 明确表达意图：</p>

<pre><code>function sum(values: readonly number[]): number {
  return values.reduce((a, b) =&gt; a + b, 0);
}</code></pre>

<p><code>readonly T[]</code> 不允许 <code>push</code>，因此协变是安全的。函数参数位置上的数组，默认写成 <code>readonly</code> 能避免这类问题。</p>

<h2>小结</h2>
<p>看到 <code>Array&lt;T&gt;</code> 出现在会被修改的位置时，多问一句「这里真的需要往里写吗」。不需要的话就加 <code>readonly</code>。</p>
```

`post-nav`：上一篇指向 `css-grid-tricks.html`，下一篇指向 `understanding-closures.html`。

- [ ] **Step 4: 截图检查文章页**

```bash
mkdir -p /tmp/blog-shots
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --window-size=900,2000 \
  --screenshot=/tmp/blog-shots/post.png \
  "file:///Users/blood/demo/posts/understanding-closures.html" 2>/dev/null
```

用 Read 工具查看 `/tmp/blog-shots/post.png`。

预期：能看到返回首页链接、文章标题、日期与标签、正文、深色底的代码块（内容为等宽字体、不换行而是横向滚动）、引用块、以及底部的上一篇/下一篇。

- [ ] **Step 5: 验证相对路径正确**

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --dump-dom \
  "file:///Users/blood/demo/posts/understanding-closures.html" 2>/dev/null \
  | grep -c 'href="../assets/css/main.css"'
```

预期：输出 `1`。若为 `0`，说明文章页里的资源路径没加 `../`，页面的 CSS 和 JS 都会加载失败（页面会是无样式的裸 HTML）。

- [ ] **Step 6: 提交**

```bash
git add posts/
git commit -m "feat: 添加三篇示例文章"
```

---

## Task 10: 关于页

**Files:**
- Create: `about.html`

- [ ] **Step 1: 写 about.html**

创建 `about.html`（在项目根目录，路径与首页同级，不需 `../` 前缀）：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>关于 — 我的技术博客</title>
  <link rel="stylesheet" href="assets/css/main.css">
  <link rel="stylesheet" href="assets/css/post.css">
  <script src="assets/js/blog-core.js"></script>
  <script src="assets/js/posts.js"></script>
  <script src="assets/js/theme.js"></script>
</head>
<body>
  <header class="site-header">
    <div class="container site-header__inner">
      <a class="site-title" href="index.html">我的技术博客</a>
      <nav class="site-nav">
        <a class="site-nav__link" href="about.html">关于</a>
        <button class="theme-toggle" type="button" id="theme-toggle" aria-label="切换主题"></button>
      </nav>
    </div>
  </header>

  <main class="container">
    <article>
      <header class="post-header">
        <h1 class="post-header__title">关于</h1>
      </header>

      <div class="post-body">
        <!-- 改这里：换成你自己的介绍 -->
        <p>你好，我是一名后端工程师，平时写 Go 和 TypeScript，偶尔碰前端。</p>
        <p>这个博客用来记录那些「当时搞懂了，过两个月又忘了」的东西。写作对我来说是把理解压实的过程——如果一篇文章没法讲清楚，通常说明我自己还没真懂。</p>

        <h2>写什么</h2>
        <ul>
          <li>语言与类型系统里那些反直觉的地方</li>
          <li>调试和性能问题的排查过程</li>
          <li>工具链配置，以及为什么这么配</li>
        </ul>

        <h2>联系我</h2>
        <ul>
          <li>GitHub：<a href="https://github.com/">github.com/yourname</a></li>
          <li>邮箱：<a href="mailto:you@example.com">you@example.com</a></li>
        </ul>

        <h2>关于本站</h2>
        <p>纯 HTML、CSS 和原生 JavaScript，没有框架、没有构建步骤、没有外部依赖。双击任意页面就能在本地打开。</p>
        <!-- 介绍结束 -->
      </div>
    </article>
  </main>

  <footer class="site-footer">
    <div class="container"><p>© 2026 我的技术博客</p></div>
  </footer>
</body>
</html>
```

- [ ] **Step 2: 截图检查**

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --window-size=900,1400 \
  --screenshot=/tmp/blog-shots/about.png \
  "file:///Users/blood/demo/about.html" 2>/dev/null
```

用 Read 工具查看 `/tmp/blog-shots/about.png`。

预期：与文章页排版一致，标题为「关于」，正文为介绍内容，样式与首页统一。

- [ ] **Step 3: 验证主题按钮存在于全部页面**

```bash
for f in index.html about.html posts/understanding-closures.html posts/css-grid-tricks.html posts/array-generics-pitfall.html; do
  n=$("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
      --dump-dom "file:///Users/blood/demo/$f" 2>/dev/null | grep -c 'id="theme-toggle"')
  echo "$f: theme-toggle x$n"
done
```

预期：每个文件都输出 `theme-toggle x1`。

- [ ] **Step 4: 提交**

```bash
git add about.html
git commit -m "feat: 添加关于页"
```

---

## Task 11: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: 写 README.md**

创建 `README.md`：

```markdown
# 我的技术博客

纯 HTML5 + CSS + 原生 JavaScript 的静态博客。没有框架、没有构建步骤、没有 npm 依赖、没有外部 CDN 请求。

## 本地预览

直接双击 `index.html` 就能在浏览器里打开——不需要启动任何服务器。

## 发布一篇新文章

**第一步**，复制模板并写正文：

```bash
cp template.html posts/my-new-post.html
```

打开 `posts/my-new-post.html`，按文件里 `<!-- 改这里 -->` 注释的提示替换标题、日期、标签、正文，以及底部的上一篇/下一篇链接。

文件名（去掉 `.html`）就是文章的 slug，例如 `my-new-post.html` 对应 slug `my-new-post`。

**第二步**，在 `assets/js/posts.js` 的数组里加一条记录：

```js
{
  slug: 'my-new-post',              // 必须与文件名一致，否则首页链接会 404
  title: '文章标题',
  date: '2026-09-20',               // YYYY-MM-DD，首页按此倒序排列
  tags: ['JavaScript'],             // 至少一个；标签栏会自动收集所有标签
  summary: '一句话摘要，显示在首页列表里。',
  readingTime: 5                    // 分钟，自己估
}
```

保存后刷新首页，新文章就出现在列表里了。标签栏也会自动包含新标签，不需要手动维护。

## 目录结构

```
├── index.html            首页
├── about.html            关于
├── template.html         新文章模板
├── posts/                文章页，一篇一个 HTML 文件
├── assets/
│   ├── css/
│   │   ├── main.css      设计令牌、布局、导航、列表
│   │   └── post.css      正文排版
│   └── js/
│       ├── blog-core.js  纯函数（可测试，不碰 DOM）
│       ├── posts.js      文章数据 —— 唯一要维护的数据文件
│       ├── theme.js      主题切换
│       └── home.js       首页渲染与标签筛选
└── tests/                测试
```

## 运行测试

```bash
node --test tests/
```

单元测试覆盖 `blog-core.js` 的纯函数与文章数据的完整性，用 Node 内置的测试运行器，无需 `npm install`。

端到端渲染检查：

```bash
bash tests/render-check.sh
```

## 标签筛选

首页点击任意标签即筛选列表，再点同一标签取消筛选。筛选状态会同步到地址栏（`index.html#tag=JavaScript`），可以直接把链接分享给别人。

## 主题

点击右上角按钮切换深色/浅色，选择保存在浏览器本地。首次访问时跟随系统偏好。

## 几个设计决定

**为什么用普通 `<script>` 而不是 ES Module。** `<script type="module">` 在 `file://` 协议下会被浏览器按 CORS 规则拦截，那样就必须起本地服务器才能预览。普通脚本没有这个限制。

**为什么文章是独立 HTML 而不是 Markdown。** 浏览器同样无法在 `file://` 下 `fetch` 本地 `.md` 文件。而且独立 HTML 让每篇文章能自由使用表格、图片、内嵌样式，不受 Markdown 语法限制。

**为什么代码块没有语法高亮。** 高亮需要引入 highlight.js 或手写数百行正则，与「零依赖」的目标冲突。深色底加等宽字体已经保证可读性。

**`blog-core.js` 末尾的 `module.exports` 是干什么的。** 浏览器里 `module` 不存在，这行被跳过，函数自然成为全局；Node 里它让测试可以 `require` 这个文件。一行代码换来纯函数的完整单元测试。
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: 添加 README 与发布流程说明"
```

---

## Task 12: 端到端渲染检查脚本

**Files:**
- Create: `tests/render-check.sh`

这个脚本断言「浏览器执行 JS 之后」的真实 DOM，补上单元测试覆盖不到的部分：脚本加载顺序、`home.js` 的 DOM 接线、资源路径。

- [ ] **Step 1: 写检查脚本**

创建 `tests/render-check.sh`：

```bash
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
check() {
  local desc="$1" want="$2" haystack="$3" pattern="$4"
  local got
  got=$(printf '%s' "$haystack" | grep -o -- "$pattern" | wc -l | tr -d ' ')
  if [ "$got" = "$want" ]; then
    echo "  ✓ $desc"
    pass=$((pass + 1))
  else
    echo "  ✗ $desc（期望 $want 处，实际 $got 处）"
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
check "正文标题已渲染"             1 "$POST_DOM" '理解闭包到底在讲什么'
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
```

- [ ] **Step 2: 运行检查脚本**

```bash
bash tests/render-check.sh
```

预期：全部 `✓`，最后一行为 `通过 20 项，失败 0 项`。

若某项失败，常见原因：

- **「渲染出 3 条文章」为 0** —— `home.js` 没执行。检查 `index.html` 里 `blog-core.js` 是否排在 `posts.js` 之前，以及 `home.js` 是否在 `</body>` 前。
- **「标题尖括号已转义」失败** —— `escapeHTML` 没有应用到 `title` 字段。
- **文章页「资源路径带 ../ 前缀」失败** —— 文章页里的路径漏了 `../`，页面会是无样式的裸 HTML。

- [ ] **Step 3: 提交**

```bash
chmod +x tests/render-check.sh
git add tests/render-check.sh
git commit -m "test: 添加无头 Chrome 端到端渲染检查"
```

---

## Task 13: 最终验证

- [ ] **Step 1: 跑全部单元测试**

```bash
node --test tests/
```

预期：PASS，35 个测试全部通过，0 失败。

- [ ] **Step 2: 跑端到端检查**

```bash
bash tests/render-check.sh
```

预期：`通过 20 项，失败 0 项`。

- [ ] **Step 3: 确认工作区干净**

```bash
git status --short
```

预期：无输出（所有文件都已提交）。

- [ ] **Step 4: 手动确认清单一遍**

对照设计文档逐项确认：

- [ ] 双击 `index.html` 能打开且样式、列表正常（不是裸 HTML）
- [ ] 点击标签能筛选，再点一次能取消
- [ ] 筛选后刷新页面，筛选状态保留（URL hash 生效）
- [ ] 右上角按钮能切换深色/浅色，刷新后保持
- [ ] 深色模式下没有白屏闪烁
- [ ] 文章页的代码块横向滚动而非撑破布局
- [ ] 窄窗口（约 375px）下排版不错乱
- [ ] 用键盘 Tab 能依次聚焦到所有链接和按钮，焦点框可见

- [ ] **Step 5: 确认设计文档中的「非目标」确实没做**

确认不存在：搜索框、目录、评论区、RSS 链接、分页控件、任何外部 CDN 请求。
