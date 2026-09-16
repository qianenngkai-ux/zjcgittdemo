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
