# Zimo Wen / nssmd 个人主页

网站：https://nssmd.github.io/ · 仓库：https://github.com/nssmd/nssmd.github.io

按用户要求，以 [Weiyang Jin 的公开主页源码](https://github.com/WayneJin0918/home) 为样式基础。保留其字体、圆形头像、章节标题、项目分类、Experience 和 Community Contribution 布局，替换为 Zimo Wen 的资料。原始样式来自提交 `7e17d7ede80eb8d7bb19a6644f2f267889ec182c`，页脚保留来源链接。

## 内容

- 11 个研究条目：Agentic Systems（5）、Multimodal Learning（1）、Time Series & Dynamics（3）、Technical Reports（2）。
- RoboRSI 放入 Agentic Systems；SenseNova-U1.5 和 Mage-Flow 放入 Technical Reports。Blog 栏目提供研究长文、case 视频与 Markdown 写作入口。
- News 包含 RoboRSI、SenseNova-U1.5 及先前预印本动态。
- Experience 根据本人 GitHub 历史 CV 资料填写，详见 `SOURCES.md`。
- Community Contribution 包含 Argus、lmms-eval、lmms-engine 和 Flash Linear Attention。
- 联系邮箱由用户明确提供：`2581235653@qq.com`。

## 修改与预览

- `data/profile.json`：简介、学籍、邮箱及个人信息。
- `data/publications.json`：研究条目、分类、作者与官方链接。
- `data/news.json`：新闻。
- `data/experience.json`：实验室经历及时间。
- `data/community.json`：社区贡献项目。
- `style.css`：从参考仓库提取的基础样式；`custom.css`：视频、筛选、无障碍等本地补充。
- `assets/media/`：官方项目视频、配图与封面；`assets/avatar.png`：GitHub 头像。

更新 JSON 或模板后运行 `python build.py`，生成 `index.html`。生成器只依赖 Python 标准库。

```bash
python build.py
python -m http.server 8765
```

访问 `http://localhost:8765`。也可以直接打开 `index.html`。Google Fonts 用于还原参考站字体；断网时使用字体回退。内容和链接不依赖 JavaScript，年份/关键词筛选和视频自动播放为渐进增强。

GitHub Pages 从 `main` 分支根目录发布，无需额外构建。页面路径使用相对资源地址。

## 资料与既有文件

公开来源、媒体来源与经历出处记录在 `SOURCES.md`。缺少公开视频时使用官方配图；DANet、PI-GNN 的主题示意图不代表实验结果。未核实的 Code/Scholar 链接不伪造。

原站所有视频和实验文件均保留，原首页归档为 `previous-homepage-20260911.html`。`preview/` 仅存本地预览截图，不参与发布。


## Blog 写作

访问 https://nssmd.github.io/blog/ 。COMPASS 文章位于 `/blog/compass/`。

1. 复制 `content/blog/_template.md`，以日期和标题命名，例如 `2026-11-06-my-note.md`。
2. 填写标题、slug、简介、日期和标签；正文用 Markdown，可加入图片、表格、代码和视频 HTML。
3. 写好后设 `published: true`，推送到 `main`，GitHub Actions 自动构建并发布。`published: false` 和未来日期的文章不进入网站和 RSS。

本地预览：

```bash
pip install Markdown==3.8.2 PyYAML==6.0.2 Pygments==2.19.2 beautifulsoup4==4.13.4
python build.py
python tools/build_blog.py
python -m http.server 8766
```

博客样式与交互位于 `blog/blog.css` 和 `blog/blog.js`。COMPASS 视频与精选执行数据位于 `blog/assets/compass/`；所有 case 来自 COMPASS 自身的 t2v3 运行，参考 RoboRSI 的展示结构，没有使用其视频作为 COMPASS 结果。

发布现在由 `.github/workflows/pages.yml` 完成，沿用原静态文件和 `.nojekyll`，保留原站项目资源路径。

Blog 用于初步设想（Ideas）、论文解读（Paper notes）和研究随想（Reflections）；`content/blog/` 已准备三类草稿模板。主页导航、Blog 区域以及 Research 标题旁均有入口。


## COMPASS 方法文章与批注

交互评审副本 `/review/compass/` 包含 SceneCode 字段说明、完整 pipeline、encoder 网络与训练机制、三个同步 case study 和 11 类执行视频。三个播放器使用控制步与视频帧的一一对应关系，在记录的 review 时间更新 SceneCode；可切换场景代码、命令、检查和 3D 目标，也可打开已经将代码渲染在旁边的 MP4。

- 页面组件：`tools/compass_components.py`。
- 记录数据：`blog/assets/compass/scenecode-traces.json`。
- 原始图像锚点使用 640×480 坐标，覆盖到 640×360 视频时按两个方向分别缩放。
- 在 HTML 选中文字或点击视频的 **Comment at this moment**，会复制对应段落、时间和网页链接，并打开原英文 Google Doc；将上下文粘贴到 Doc 评论即可讨论。共享评论在 Google Doc 中完成。
- Google Doc 使用正文结构，没有附录；普通共享访问者可批注，账号所有者保留编辑权限。

公共页面只包含展示所需的 SceneCode 数据，不包含 API 响应身份、认证信息或原始内部日志。


## 两个展示版本

- 官网 `/blog/compass/` 是静态文章：关键帧与 SceneCode 摘录顺序展示，视频使用普通链接。公开 Blog 不包含播放器、筛选、弹窗或选文批注脚本。
- `/review/compass/` 是给老师的交互评审副本：保留同步视频、SceneCode 切换、时间轴和 Google Doc 批注上下文复制。该路径不进入 Blog 列表或 RSS，并标记 noindex；它是通过链接访问的评审副本，不是访问受限页面。
- Google Colab 保存交互页面的预览输出，可通过 Google 分享与评论；原 Google Doc 专门记录实验结果、token 实测和后续资源。
