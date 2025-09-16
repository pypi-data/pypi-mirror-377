import os
from langchain_core.messages import ToolMessage
from pathlib import Path

def parse_chat_interface_output(agent_executor_result):
    """
        Parses agent executor result into chat interface response
        return_intermediate_steps must be set as true on the AgentExecutor in order to properly parse plot and suggestions
    """
    messages = [{"role": "assistant", "content": [
                {
                    "type": "text",
                    "text": agent_executor_result["output"]
                }
            ]}]
    suggestions = []
    intermediate_steps = agent_executor_result.get('intermediate_steps', [])
    for step, output  in intermediate_steps:
        if step.tool == "generate_plot":
            messages.append({"role": "assistant", "content": [
                {
                    "type": "image",
                    "image": output
                }
            ]})
        if step.tool == "send_chat_suggestions":
            suggestions = output
        
        # Check if some tool message has artifact and raw_html attribute
        artifact = None
        is_tool_msg = isinstance(output, ToolMessage)
        if is_tool_msg:
            artifact = getattr(output, "artifact", None)
            if artifact is None:
                artifact = getattr(output, "additional_kwargs", {}).get("artifact")
            if artifact:
                artifact_id = artifact.get("artifact_id")
                if artifact_id:
                    base_dir = Path("/tmp") if Path("/tmp").exists() else Path.cwd()
                    artifact_path = base_dir / f"{artifact_id}.html"
                    messages.append({
                        "role": "assistant",
                        "content": [{
                            "type": "file",
                            "mimeType": "text/html",
                            "data": artifact_path.read_text(encoding="utf-8")
                        }]
                    })
                    if os.path.exists(artifact_path):
                        os.remove(artifact_path)
    return {
        "messages": messages,
        "suggestions": suggestions
    }