# Zimo Wen / nssmd 个人主页

网站：https://nssmd.github.io/ · 仓库：https://github.com/nssmd/nssmd.github.io

按用户要求，以 [Weiyang Jin 的公开主页源码](https://github.com/WayneJin0918/home) 为样式基础。保留其字体、圆形头像、章节标题、项目分类、Experience 和 Community Contribution 布局，替换为 Zimo Wen 的资料。原始样式来自提交 `7e17d7ede80eb8d7bb19a6644f2f267889ec182c`，页脚保留来源链接。

## 内容

- 11 个研究条目：Agentic Systems（5）、Multimodal Learning（1）、Time Series & Dynamics（3）、Technical Reports（2）。
- RoboRSI 放入 Agentic Systems；SenseNova-U1.5 和 Mage-Flow 放入 Technical Reports。没有独立 Blog 栏目。
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
