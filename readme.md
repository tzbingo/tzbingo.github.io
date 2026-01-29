### 标准写作流程（每次写文章都按这个来）
#### 1. 打开项目与同步（第一步必做！）
每次准备写博客前，先打开 VS Code，确保打开的是 E:\blog 文件夹。打开终端（Ctrl + `），输入：
```Bash
git pull
```
- **为什么要这么做？**
哪怕你只用这一台 Windows 电脑，也要养成这个习惯。万一你哪天在 Linux Mint 上改了一个错别字，或者在 GitHub 网页上修了个 bug，不拉取（pull）下来直接写新文章，以后提交就会报错（冲突）。
#### 2. 新建文章
在终端里输入 Hugo 的命令来生成文章模板（这样会自动带上时间、标题等信息）：
```Bash
hugo new posts/myblog.md
```
(注意：如果不习惯用命令，你也可以直接在左侧文件栏 content/posts 文件夹上右键 -> 新建文件，自己复制粘贴头部的格式)
#### 3. 撰写与修改设置（关键点）
在左侧文件栏找到刚才新建的 content/posts/myblog.md，开始写作。
**⚠️ 这里有一个新手最容易踩的坑：**
请看文件最上面的内容（Front Matter），通常长这样：
```Yaml
---
title: "我的博客"
date: 2026-01-xx...
draft: true  <-- 注意这里！！
---
```
- draft: true 意思是“草稿”。只要这一行是 true，你推送到 GitHub 后，**网页上是不会显示这篇文章的。**
- **解决方法：** 当你觉得写好了，准备发布时，把 true 改成 false。
#### 4. 本地预览（所见即所得）
在推送到网上之前，先在本地看看效果。在终端输入：
``` Bash
hugo server -D
```
- (加 -D 的意思是即使是草稿也预览)
- 终端会显示一个地址，通常是 http://localhost:1313。
- 按住 **Ctrl** 点击这个链接，浏览器就会打开预览页面。
- 你可以一边改文字，浏览器会自动刷新，非常爽。
- **退出预览：** 在终端里按 **Ctrl + C** 停止运行。
#### 5. 发布上线
文章写好、draft 改成 false、预览也没问题了，就可以发布了。
在终端依次执行这三行：
```Bash
git add .
git commit -m "新增文章：我的博客"
git push
```
### 此时发生了什么？
1. 你的源码被上传到了 GitHub。
2. GitHub Actions 检测到更新，自动启动一台虚拟服务器。
3. 它安装 Hugo，编译你的网站，生成 HTML。
4. 自动部署到你的网址。
5. 喝口水（约 1 分钟后），刷新你的博客，新文章就出现了。

### 以后去 Linux Mint 上怎么写？
完全一样！
1. 打开终端进入目录。
2. git pull (把刚才在 Windows 写的文章同步下来)。
3. hugo new ... 或直接写。
4. git add / commit / push。
享受你的写作吧！如果遇到问题随时问我。

### 创建图片仓库
Hugo 有一个约定：放在 static 文件夹里的任何文件，生成网站时都会被直接复制到网站根目录。
在你的博客根目录 E:\blog 下，找到 static 文件夹（如果没有就新建一个）。
为了条理清晰，建议在里面新建一个 images 文件夹。
目录结构看起来是这样的：
```Text
E:\blog
├── content
├── themes
└── static
    └── images
        ├── 2023
        │   └── my-cat.jpg  <-- 你把图片放在这里
        └── avatar.png
```
### 在文章中引用图片
假设你把一张名为 cat.jpg 的图片放到了 E:\blog\static\images\cat.jpg。
在 Markdown 文章里，你应该这样写（注意前面的斜杠 /）：
```Markdown
![这是图片的描述](/images/cat.jpg)
```
- 原理： Hugo 编译时，会把 static/images/cat.jpg 搬运到网站的 https://你的域名/images/cat.jpg，所以引用路径要写 /images/...。

### 使用 Paste Image插件
手动复制粘贴图片到文件夹太麻烦了。VS Code 有一个神级插件，可以让你像在 Word 里一样，截图 -> 粘贴 -> 自动保存图片并插入代码。
1. 用微信截图或者系统截图截一张图（图片在剪贴板里）。
2. 在 VS Code 里正在写的 Markdown 文章中，光标停在你想要插图的位置。
3. 按快捷键 Ctrl + Alt + V。
4. 神奇的事情发生了：
    - VS Code 会自动把剪贴板里的图片保存到 static/images 文件夹下（文件名通常是时间戳）。
    - Markdown 文章里自动插入了 ![](/images/2023-xx-xx.png) 的代码。
    
你只需要按下 Ctrl+Alt+V，一切自动搞定。