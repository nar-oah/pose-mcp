# Blender Pose MCP

一个极简、专用的 Blender Pose MCP，只操作当前场景中唯一一个已存在的
Armature 的 Pose。它不提供建模、材质、权重、骨骼编辑、对象创建/删除或任意
Python 执行能力。

```text
Codex -> MCP stdio server -> 127.0.0.1:8766 JSON/TCP -> Blender add-on
```

## 组件

- `blender_pose_bridge/`：安装到 Blender 的独立 Add-on。启用后自动监听
  `127.0.0.1:8766`，禁用时关闭 socket、后台线程和 timer。
- `blender_pose_mcp/`：在普通 Python venv 中运行的官方 MCP Python SDK v2
  stdio Server。
- `reference/main.py`：原始且不修改的 `SMPLest-X Loader` 参考实现。

Bridge 网络线程只收发 JSON 并把请求放入线程安全队列。所有 `bpy` 操作由
`bpy.app.timers` 回到 Blender 主线程执行。场景中没有 Armature 或存在多个
Armature 时，调用会明确失败；多个对象时错误中包含全部 Armature 名称。

## 安装 Blender Add-on

可直接压缩 `blender_pose_bridge` 文件夹：

```bash
ditto -c -k --sequesterRsrc --keepParent blender_pose_bridge blender_pose_bridge.zip
```

在 Blender 中打开 `Edit > Preferences > Add-ons > Install from Disk`，选择
`blender_pose_bridge.zip`，然后启用 **Blender Pose Bridge**。它与原有
**SMPLest-X Loader (Simplified)** 使用不同的类名、Panel、PropertyGroup 和
Operator ID，可以同时启用。3D View 侧栏的 `Pose Bridge` 页会显示在线状态。

## 安装 MCP Python 环境（macOS）

MCP Server 要在普通 Python 中运行，不使用 Blender 自带 Python：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
```

依赖只有官方 `mcp` 包及其运行时依赖。不需要 PyTorch、Transformers、
sentence-transformers、LaBSE、Ollama、embedding/vector database 或本地 LLM。
如果 macOS/Homebrew Python 受 PEP 668 管理，必须使用上面的 venv；不要使用
`--break-system-packages`。

## 添加到 Codex

把 `/ABSOLUTE/PATH/blender-pose-tools` 替换成仓库绝对路径：

```bash
codex mcp add blender-pose -- /ABSOLUTE/PATH/blender-pose-tools/.venv/bin/python -m blender_pose_mcp
```

也可以写入 `~/.codex/config.toml` 或可信项目的 `.codex/config.toml`：

```toml
[mcp_servers.blender-pose]
command = "/ABSOLUTE/PATH/blender-pose-tools/.venv/bin/python"
args = ["-m", "blender_pose_mcp"]
cwd = "/ABSOLUTE/PATH/blender-pose-tools"
startup_timeout_sec = 10
tool_timeout_sec = 60
```

重启 Codex 后使用 `/mcp`，应看到 `blender-pose` 和下列工具：`ping`、
`get_rig`、`get_pose`、`set_bone_pose`、`set_pose_batch`、`apply_smplx_pose`、
`reset_pose`、`undo`、`get_viewport`、`save_blend`。

## 工具语义

- `set_bone_pose` / `set_pose_batch` 接收本地 Pose Bone 的 XYZ degree。
  `absolute` 替换当前本地 rotation，`delta` 将增量 quaternion 右乘到当前本地
  rotation；两者都不会重置其他骨骼。一个 batch 只创建一个 Blender Undo step。
- `apply_smplx_pose` 会像原脚本一样先重置 Pose，再完整导入 SMPL-X JSON。
  它保留原脚本的 rotvec、Root、Hand、坐标系和 `matrix_local` basis 转换。
- `reset_pose` 当前只接受 `{"scope": "all"}`，用 `matrix_basis` 恢复基础 Pose，
  不修改 Rest Pose。
- `get_viewport` 从当前 `VIEW_3D` 做 OpenGL viewport render，PNG 写入系统临时
  目录并返回路径，不污染项目。
- `save_blend` 永不自动调用。未曾保存过、没有文件路径的项目会返回错误。

完整 SMPL-X 参数形状与原脚本一致，例如：

```json
{
  "body_root_pose": [[0.0, 0.0, 0.0]],
  "body_pose": [[0.0, 0.0, 0.0]],
  "lhand_pose": [],
  "rhand_pose": []
}
```

## 测试

普通 Python 自动测试覆盖 tools/list、ping、参数校验、Blender 离线、无 Armature
和多个 Armature 错误：

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

真实 Blender 后台测试只创建测试 Armature，不创建或修改 Mesh：

```bash
blender --background --factory-startup --python tests/blender_automated_test.py
blender --background --factory-startup --python tests/blender_conversion_test.py
blender --background --factory-startup --python tests/blender_tcp_test.py
```

手动 smoke test：在一个包含唯一目标 Armature（且含 `head`）的 Blender 中，
从 Text Editor 打开并运行 `tests/blender_smoke_test.py`。它依次执行 ping、
get_rig、get_pose、修改 head、undo、reset。**最后一步会重置当前 Pose**，但脚本
不会保存 `.blend`。

## 卸载

```bash
codex mcp remove blender-pose
```

然后在 Blender Preferences 中禁用并移除 **Blender Pose Bridge**。需要彻底删除
Python 环境时，可删除仓库内 `.venv/`；项目或 `.blend` 不受影响。

## 原始 main.py 与转换复用

不需要修改 `reference/main.py`。`blender_pose_bridge/smplx.py` 直接保留其
`ROOT_BONE`、`BODY_BONES`、`HAND_BONES`、`BODY_OFFSETS`、
`rotvec_to_quaternion`、`set_bone_rot`、Root 180° 修正、Hand rotvec 符号反转、
SMPL-X 到 Blender 的 X 轴 90° quaternion 转换，以及
`bone.matrix_local.to_quaternion()` basis 转换。交互式 degree 接口是独立逻辑，
不会改变完整 JSON 导入行为。
