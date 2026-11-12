# Wude Story Video V2

作者：WUDE。技能标识：`wude-story-video`。版本：2.0.0。

把主题、脑洞或故事制作成原创三维剧情短片。用人物愿望、阻力、选择和后果推动故事，配合角色表演、场景互动、镜头调度与音画同步，完成配音、字幕、音效、质检和可编辑工程交付。

这是第二条视频制作流程；知识课程继续使用 [Wude Video Studio](../wude-video-studio/)。造型、美术与镜头按主题设计，不固定使用某一套人物或场景。

## 安装与调用

将本目录完整放入 Codex 的 `~/.codex/skills/wude-story-video/`，保留 `references`、`scripts` 和 `agents`。已有同名目录时先核对并备份，再更新。新会话调用：

```text
使用 $wude-story-video，根据我的主题制作原创三维剧情短片，免费完成并交付成片、脚本、字幕和可编辑工程。
```

可以只要求故事设计、脚本、修改或检查；批准制作后按范围完成整片。需要 Python 3，以及按任务准备的 FFmpeg/ffprobe、浏览器、三维渲染和语音工具。工具本体、模型、字体和在线服务额度不包含在技能里；免费是制作预算约束，不保证在线服务永久免费。

## 文件与工具

- [SKILL.md](./SKILL.md)：工作流入口与适用范围。
- [叙事与三维分镜](./references/story-and-scenes.md)：故事、状态连续性、人物动作、镜头与材质。
- [免费制作与时间线](./references/free-production.md)：工具选择、配音、字幕锚点、确定性渲染和缓存。
- [成片检查与交付](./references/qa-and-delivery.md)：接触、遮挡、字幕、声音、完整解码和工程包。
- [字幕对齐工具](./scripts/align_subtitles.py)：Python 标准库，将语义字幕短句与事件对齐到真实词边界；输入格式见制作参考。
- [交付校验工具](./scripts/check_delivery.py)：Python 标准库，校验哈希和 ZIP，可选 ffprobe 元数据检查。

```sh
python3 scripts/align_subtitles.py timeline-input.json --out-dir timeline
python3 scripts/check_delivery.py /path/to/delivery --write-manifest
python3 scripts/check_delivery.py /path/to/delivery --verify-manifest
```

字幕工具不推断 token 内部的时间。交付校验不替代完整解码、视觉审查或监听；Finder 的 `.DS_Store` 单独报告并忽略，其他实际文件仍参加清单核对。普通制作不自动触发发布、网盘上传或本地清理。

[返回技能索引](../README.md) · [仓库首页](../../README.md)
