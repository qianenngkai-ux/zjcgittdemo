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

// Node 测试用；浏览器中 module 未定义，此行跳过。
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
