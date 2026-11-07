# WUDE / Skill Hub

公开 Agent Skills 的收录与实践目录。记录一个技能能做什么、由谁维护、应该去哪里阅读和使用。

博客入口：[Skill Hub](https://cs-wude.github.io/skills.html)（页面开发中，随博客发布后可访问）。

## 公开来源

| 技能 | 用途 | 来源 |
| --- | --- | --- |
| Skill Creator | 创建、评测和迭代技能 | [Anthropic](https://github.com/anthropics/skills/tree/main/skills/skill-creator) |
| Frontend Design | 有明确视觉方向的前端界面设计 | [Anthropic](https://github.com/anthropics/skills/tree/main/skills/frontend-design) |
| Web App Testing | 使用 Playwright 验证本地 Web 应用 | [Anthropic](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) |
| PDF | PDF 提取、合并、拆分与生成 | [Anthropic](https://github.com/anthropics/skills/tree/main/skills/pdf) |

以上是原作者公开的技能入口，未复制其完整内容。许可、支持的工具、安装方法与更新请以原始仓库为准。收录不代表本站逐项完成兼容性验证。

## 自己维护的 Skills

`skills/` 用于逐项加入决定公开的原创技能，目前尚未收录可安装的原创技能。不要把模板当作已完成的技能安装。

- [技能写作模板](./templates/SKILL.md.example)
- [收录与贡献说明](./CONTRIBUTING.md)

## 如何更新博客目录

博客的唯一目录数据源位于 [CS-wude.github.io/data/skills.js](https://github.com/CS-wude/CS-wude.github.io/blob/main/data/skills.js)（随博客代码发布）。添加名称、中文用途、分类、作者、来源链接与标签，然后在博客仓库执行 `npm test` 和 `npm run build`。

目录由构建生成静态 HTML，访客可直接打开来源。浏览器只做搜索与筛选，不读取 GitHub API，也不使用 Issues 同步。
