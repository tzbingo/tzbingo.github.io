---
title: "在Hugo博客中全屏运行一个HTML网页"
date: 2026-02-02T14:07:07+08:00
draft: false
---
### 缘起
前几天使用AI生成了一个黑客风的打字游戏，希望实现小学生课堂打字自由，但又不想部署服务器，想着能不能直接放到博客中，问了一下gemini，建议完整独立的网页内嵌到博客中，使用iframe的方式最简单，于是开始新建静态文件目录，上传打字游戏源文件，然后在博客中使用如下代码：
```markdown
<iframe src="/demos/my-game.html" width="100%" height="600px" style="border:none;"></iframe>
```

插入效果：

<iframe src="/html/typegame.html" width="100%" height="530px" style="border:none;"></iframe>

- 优点：样式完全隔离，不会破坏博客主题；脚本运行环境独立。
- 缺点：需要手动设置 height 高度，否则可能会出现滚动条。

虽然实现了网页内嵌，但由于博客主题正文部分比较窄，这个 Iframe 没有横向占满浏览器窗口，作为打字游戏来说，体验感很不好。
### 操刀
希望实现类似视频网站播放视频时的沉浸式全屏，页面上有一个按钮，点击后 Iframe 铺满整个显示器屏幕。

继续请出gemini，建议需要封装一个 **Hugo Shortcode** ，在 Iframe 上方添加一个控制条。

**1. 创建 Shortcode**

新建文件 layouts/shortcodes/iframe-fullscreen.html：
```html
<!-- layouts/shortcodes/iframe-fullscreen.html -->
<div class="iframe-container" id="container-{{ .Get "id" }}" style="position: relative; width: 100%; margin: 20px 0;">
    <!-- 工具栏 -->
    <div style="background: #f1f1f1; padding: 5px 10px; text-align: right; border: 1px solid #ddd; border-bottom: none;">
        <button onclick="toggleFullScreen('container-{{ .Get "id" }}')" style="cursor: pointer; padding: 5px 10px;">
            ⛶ 全屏运行
        </button>
    </div>
    
    <!-- Iframe 本体 -->
    <iframe 
        id="iframe-{{ .Get "id" }}"
        src="{{ .Get "src" }}" 
        width="100%" 
        height="{{ .Get "height" | default "500px" }}" 
        style="border: 1px solid #ddd; background: white; display: block;"
        allow="fullscreen"
    ></iframe>
</div>

<script>
function toggleFullScreen(containerId) {
    var elem = document.getElementById(containerId);
    var iframe = elem.querySelector('iframe');

    if (!document.fullscreenElement) {
        // 进入全屏
        elem.requestFullscreen().catch(err => {
            alert(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
        });
        // 全屏时调整 iframe 高度为 100vh 以占满屏幕
        iframe.style.height = "100vh";
    } else {
        // 退出全屏
        document.exitFullscreen();
        // 恢复默认高度
        iframe.style.height = "{{ .Get "height" | default "500px" }}";
    }
}

// 监听全屏变化事件，防止用户按 Esc 退出后高度未恢复
document.addEventListener('fullscreenchange', (event) => {
    // 检查哪个容器触发了事件
    // 这里为了简化，采用通用恢复逻辑，实际项目中可以更精细
    if (!document.fullscreenElement) {
         var iframes = document.querySelectorAll('.iframe-container iframe');
         iframes.forEach(f => {
             // 恢复原始高度，这里假设默认都是 500px，你可以改进代码通过 data 属性存储原始高度
             f.style.height = "500px"; 
         });
    }
});
</script>
```

**2. 在 Markdown 中使用**

```markdown
{{</* iframe-fullscreen src="/demos/game.html" id="game1" height="600px" */>}}
```

**效果：** 文章中会出现一个带“全屏运行”按钮的窗口，点击后网页会像 PPT 一样占满整个屏幕。

{{< iframe-fullscreen src="/html/typegame.html" id="game1" height="530px" >}}

全屏运行的目标是实现了，但总觉的欠点意思，跟专业的在线演示平台（如 CodePen）的体验差距较大。
### 提升
- 美化容器：使用卡片式设计（圆角 + 阴影），在文章中看起来更像一个专业的组件，而不是突兀的 iframe。
- 顶部标题栏：在未全屏时，页面显示标题和漂亮的“全屏体验”按钮。
- 智能感应区：全屏时，在屏幕顶部显示一个隐形退出全屏按钮。
    - 自动隐藏：平时完全看不到，不会遮挡网页内容。
    - 自动显示：当你把鼠标移到屏幕顶部边缘时，触发渐变动画显示“退出全屏”按钮。

**1. 创建 Shortcode**

在 layouts/shortcodes/ 目录下再次新建一个文件，命名为 iframe-pro.html，然后填入以下代码。
```html
<!-- layouts/shortcodes/iframe-pro.html -->
<!-- 1. 生成唯一ID (使用路径+序号，不依赖Inner，无需闭合标签) -->
{{ $uid := substr (md5 (printf "%s-%d" (.Get "src") .Ordinal)) 0 8 }}

<div id="wrapper-{{ $uid }}" class="iframe-pro-wrapper" style="position: relative; margin: 2rem 0;">
    
    <!-- 顶部工具栏 -->
    <div class="iframe-toolbar">
        <span class="toolbar-title">{{ .Get "title" | default "演示页面" }}</span>
        <!-- 注意：这里去掉了 onclick，改用 class 绑定 -->
        <button class="btn-enter-fs" title="全屏运行">
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path></svg>
            全屏体验
        </button>
    </div>

    <!-- Iframe 本体 -->
    <iframe 
        class="iframe-body"
        src="{{ .Get "src" }}" 
        width="100%" 
        height="{{ .Get "height" | default "500px" }}"
        frameborder="0"
        allow="fullscreen"
        style="background: #fff; display: block; width: 100%;"
    ></iframe>

    <!-- 悬浮退出按钮 -->
    <div class="floating-exit-zone">
        <button class="btn-exit-fs">
            <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            退出全屏
        </button>
    </div>

</div>

<!-- CSS 样式 (保持不变，为了完整性再次列出) -->
<style>
    .iframe-pro-wrapper {
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        background: #f6f8fa;
    }
    .iframe-toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 15px;
        background: #f6f8fa;
        border-bottom: 1px solid #e1e4e8;
    }
    .toolbar-title { font-weight: 600; color: #444; font-size: 0.9rem; }
    .btn-enter-fs {
        display: flex; align-items: center; gap: 6px;
        background-color: #007bff; color: white; border: none;
        padding: 6px 12px; border-radius: 4px; font-size: 0.85rem;
        cursor: pointer; transition: background 0.2s;
    }
    .btn-enter-fs:hover { background-color: #0056b3; }
    
    /* 全屏逻辑样式 */
    .floating-exit-zone { display: none; }
    .iframe-pro-wrapper.is-fullscreen {
        position: fixed !important; top: 0; left: 0;
        width: 100vw; height: 100vh; z-index: 9999;
        border: none; border-radius: 0;
    }
    .iframe-pro-wrapper.is-fullscreen .iframe-body { height: 100vh !important; }
    .iframe-pro-wrapper.is-fullscreen .iframe-toolbar { display: none; }
    .iframe-pro-wrapper.is-fullscreen .floating-exit-zone {
        display: flex; justify-content: center; position: absolute;
        top: 0; left: 0; width: 100%; height: 80px; z-index: 10000;
        background: linear-gradient(to bottom, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 100%);
        opacity: 0; transition: opacity 0.4s ease; pointer-events: none;
    }
    .iframe-pro-wrapper.is-fullscreen .floating-exit-zone:hover { opacity: 1; pointer-events: auto; }
    .btn-exit-fs {
        margin-top: 15px; background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.4);
        color: white; padding: 8px 20px; border-radius: 20px;
        cursor: pointer; display: flex; align-items: center; gap: 8px;
        font-size: 0.9rem; height: 40px; transition: background 0.2s;
    }
    .btn-exit-fs:hover { background: rgba(255, 255, 255, 0.4); }
</style>

<!-- JS 逻辑 (使用 IIFE 闭包，彻底解决变量名/函数名冲突问题) -->
<script>
(function() {
    var wrapperId = "wrapper-{{ $uid }}";
    var wrapper = document.getElementById(wrapperId);
    
    // 如果页面上有多个组件，防止找不到元素
    if (!wrapper) return;

    var btnEnter = wrapper.querySelector('.btn-enter-fs');
    var btnExit = wrapper.querySelector('.btn-exit-fs');
    
    // 定义全屏切换逻辑
    function toggleFullScreen() {
        if (!document.fullscreenElement) {
            // 进入全屏
            if(wrapper.requestFullscreen) { wrapper.requestFullscreen(); }
            else if(wrapper.webkitRequestFullscreen) { wrapper.webkitRequestFullscreen(); }
            else if(wrapper.msRequestFullscreen) { wrapper.msRequestFullscreen(); }
        } else {
            // 退出全屏
            if(document.exitFullscreen) { document.exitFullscreen(); }
            else if(document.webkitExitFullscreen) { document.webkitExitFullscreen(); }
            else if(document.msExitFullscreen) { document.msExitFullscreen(); }
        }
    }

    // 绑定点击事件 (不使用 onclick 属性)
    if(btnEnter) btnEnter.addEventListener('click', toggleFullScreen);
    if(btnExit) btnExit.addEventListener('click', toggleFullScreen);

    // 监听全屏状态变化
    function handleFsChange() {
        if (document.fullscreenElement === wrapper || document.webkitFullscreenElement === wrapper) {
            wrapper.classList.add("is-fullscreen");
        } else {
            wrapper.classList.remove("is-fullscreen");
        }
    }

    document.addEventListener('fullscreenchange', handleFsChange);
    document.addEventListener('webkitfullscreenchange', handleFsChange);

})();
</script>
```

**2. 在 Markdown 中使用**

在博客文章中，使用 iframe-pro 标签引用：
```markdown
{{</* iframe-pro src="/demos/my-game.html" height="600px" title="超级马里奥演示" */>}}
```
{{< iframe-pro src="/html/typegame.html" height="530px" title="代码守护打字" >}}