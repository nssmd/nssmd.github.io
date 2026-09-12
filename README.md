# Zimo Wen / nssmd 个人主页

网站：https://nssmd.github.io/ 。发布仓库：https://github.com/nssmd/nssmd.github.io 。

参考 https://waynejin0918.github.io/home/ 的学术主页结构重新实现。纯静态 HTML/CSS/JavaScript，无 npm 依赖，不需要构建服务即可浏览。9 篇论文按 Agentic Systems、Embodied AI & 3D Understanding、Multimodal Learning、Time Series & Dynamics 分类。

## 预览

直接打开 `index.html`，或运行：

```bash
cd /data/yijia/zimo/nssmd-homepage
python -m http.server 8765 --bind 0.0.0.0
```

浏览器访问 `http://localhost:8765`；在远程服务器上可通过 SSH 转发端口后访问。

## 修改内容

- `data/profile.json`：姓名、单位、简介、研究方向、社交链接及更新时间。可填写 `email` 显示邮件按钮。
- `data/publications.json`：论文题目、作者、分类、年份和链接。
- `assets/avatar.png`：替换为自己的照片。
- `style.css`：配色与响应式布局。
- `build.py`：页面模板、近期论文动态及缺少公开配图时的主题示意图。
- `assets/media/`：官方项目视频、视频封面与论文图。视频静音播放，提供原生播放和音量控件。
- `SOURCES.md`：论文、项目、代码和媒体的公开来源。

修改 JSON 或模板后运行 `python build.py` 生成静态页面。修改 CSS、JS 或头像直接生效。

## 部署到 GitHub Pages

1. 在 GitHub 创建 `nssmd.github.io` 仓库，将本目录网页文件上传到仓库根目录。
2. 在 Settings → Pages 选择 Deploy from a branch，分支选择 `main`，目录选择 `/ (root)`。
3. 等待发布完成后访问 `https://nssmd.github.io/`。

也支持部署到项目仓库子路径，页面资源使用相对路径。`preview/` 仅用于本地截图，无需上传。

## 内容来源与待补充项

- 姓名、单位和 9 篇论文来自用户提供的 Google Scholar： https://scholar.google.ca/citations?user=H0r0cJkAAAAJ&hl=en ，读取日期为 2026-09-11。
- GitHub 链接与头像来自 `https://github.com/nssmd` 的公开账户资料。
- 简介和研究分组依据 Scholar 研究标签及论文标题整理，是可修改的初稿，未添加学位、导师、个人履历、录用消息或私人邮箱。
- 作者列表已按 arXiv 和 Scholar 论文详情补全，Zimo Wen 加粗。Argus 采用 arXiv 当前版本的标题与作者顺序。
- News 仅展示 arXiv 编号对应的预印本发布月份。会议标签采用 Scholar 的公开记录。
- Argus、Resource2Skill、LIFT 使用官方项目视频；Tri-MARF、UniG2U、Mage-Flow、PAST 使用论文原图。DANet 与 PI-GNN 暂用主题示意图，不表示实验结果。
- Website / Code 仅在已核实公开地址时显示，未公开或未找到的资源不伪造链接。
- 参考网站仅用于布局参考，未使用其个人照片、介绍或论文素材。
- 网站不实时抓取 Scholar；新增论文需要更新 JSON 并重新生成。

## 保留原站文件

发布时保留仓库已有的全部视频、实验文件和静态资源。原首页另存为 `previous-homepage-20260911.html`；只将根目录 `index.html` 更新为个人主页。
