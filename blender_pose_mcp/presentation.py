import base64
import json
from pathlib import Path

from mcp.types import CallToolResult, ImageContent, TextContent


def pose_inspection_result(snapshot: dict) -> CallToolResult:
    content = [
        TextContent(
            text=json.dumps(
                {
                    "armature": snapshot["armature"],
                    "pose": snapshot["pose"],
                    "views": snapshot["views"],
                },
                ensure_ascii=False,
            )
        )
    ]
    for view in snapshot["views"]:
        content.extend(
            [
                TextContent(
                    text=(
                        f"Fixed {view['name']} view: {view['axis']} "
                        f"{view['projection']}"
                    )
                ),
                ImageContent(
                    data=base64.b64encode(Path(view["path"]).read_bytes()).decode(),
                    mimeType=view["mime_type"],
                ),
            ]
        )
    return CallToolResult(content=content, structuredContent=snapshot)
