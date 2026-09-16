/**
 * 首页接线：把 blog-core 生成的 HTML 插入 DOM，并绑定标签筛选交互。
 */
(function () {
  'use strict';

  const listEl = document.getElementById('post-list');
  const tagBarEl = document.getElementById('tag-bar');

  const allTags = extractTags(POSTS);
  const sorted = sortByDateDesc(POSTS);

  let activeTag = parseTagFromHash(window.location.hash);

  // 如果 hash 里的标签已不存在（比如文章被删或改名），忽略它
  if (activeTag && !allTags.includes(activeTag)) activeTag = null;

  function render() {
    const visible = filterByTag(sorted, activeTag);

    tagBarEl.innerHTML = renderTagBarHTML(allTags, activeTag);
    listEl.innerHTML = renderPostListHTML(visible);
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
