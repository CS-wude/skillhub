# Wude Video Studio

作者：WUDE。技能标识：`wude-video-studio`。

将主题、教材或技术资料转成课程设计、口播分镜、动画、配音字幕及可编辑交付包；按请求归档与清理。

## 安装与调用

将本目录完整放入 Codex 的 `~/.codex/skills/wude-video-studio/`，包含 references、scripts 和 agents。已有同名版本时先核对并备份再更新。新会话中调用：

```text
使用 $wude-video-studio，根据我的主题和资料制作知识视频。
```

也可只要求设计、脚本或修改。免费是制作预算约束，不附带托管额度或保证第三方服务永久免费。按任务准备 Python 3、FFmpeg/ffprobe、浏览器/渲染与配音工具，工具本体不包含在技能中。

## 文件索引

- [SKILL.md](./SKILL.md)：工作流入口。
- [课程与画面规范](./references/content-and-visuals.md)。
- [制作与技术质检](./references/production-and-qa.md)。
- [归档与清理](./references/archive-and-cleanup.md)。
- [交付检查脚本](./scripts/check_delivery.py)：Python 标准库，ffprobe 可选。

```sh
python3 scripts/check_delivery.py /absolute/path/to/delivery
python3 scripts/check_delivery.py /absolute/path/to/delivery --write-manifest
python3 scripts/check_delivery.py /absolute/path/to/delivery --verify-manifest
```

默认只读，写清单需显式参数；哈希、ZIP 和媒体元数据不能替代完整解码、视觉审查、监听或云端备份验证。上传和清理依照具体任务授权。

[返回技能索引](../README.md) · [博客 Skill Hub](https://cs-wude.github.io/skills.html?q=wude-video-studio)
