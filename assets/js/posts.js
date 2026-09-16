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
