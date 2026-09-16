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

模板里的资源路径已经写成 `../` 前缀，复制到 `posts/` 下后无需再改。

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
node --test tests/*.test.js
```

单元测试覆盖 `blog-core.js` 的纯函数与文章数据的完整性，用 Node 内置的测试运行器，无需 `npm install`。

> 注意：本项目在 Node 22.22.0 上验证通过。该版本下 `node --test tests/`（传目录）会把目录当作模块解析而报 `MODULE_NOT_FOUND`，所以要用上面的 glob 形式；不带参数直接跑 `node --test` 也可以。

端到端渲染检查：

```bash
bash tests/render-check.sh
```

这个脚本用无头 Chrome 加载真实页面，断言 JS 执行之后的 DOM，覆盖单元测试测不到的部分：脚本加载顺序、`home.js` 的 DOM 接线、文章页的相对路径。需要本机装有 Chrome。

## 标签筛选

首页点击任意标签即筛选列表，再点同一标签取消筛选。筛选状态会同步到地址栏（`index.html#tag=JavaScript`），可以直接把链接分享给别人。

## 主题

点击右上角按钮切换深色/浅色，选择保存在浏览器本地。首次访问时跟随系统偏好。

## 几个设计决定

**为什么用普通 `<script>` 而不是 ES Module。** `<script type="module">` 在 `file://` 协议下会被浏览器按 CORS 规则拦截，那样就必须起本地服务器才能预览。普通脚本没有这个限制。

**为什么文章是独立 HTML 而不是 Markdown。** 浏览器同样无法在 `file://` 下 `fetch` 本地 `.md` 文件。而且独立 HTML 让每篇文章能自由使用表格、图片、内嵌样式，不受 Markdown 语法限制。

**为什么代码块没有语法高亮。** 高亮需要引入 highlight.js 或手写数百行正则，与「零依赖」的目标冲突。深色底加等宽字体已经保证可读性。

**`blog-core.js` 末尾的 `module.exports` 是干什么的。** 浏览器里 `module` 不存在，这行被跳过，函数自然成为全局；Node 里它让测试可以 `require` 这个文件。一行代码换来纯函数的完整单元测试。

**主题初始化为什么放在 `<head>` 且不加 `defer`。** 脚本若延迟执行，浏览器会先用默认浅色渲染一帧再切到深色，产生白屏闪烁（FOUC）。同步执行保证首帧渲染前 `data-theme` 已经写在 `<html>` 上。
