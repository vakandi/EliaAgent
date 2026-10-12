/// Start every MCP server declared in the config and collect its tools.
///
/// Nothing called this before: the server booted with `default_tool_definitions()`
/// only, so every MCP an operator had configured was silently absent from every agent.
pub async fn start_configured_mcp(
    cwd: std::path::PathBuf,
) -> Vec<opencode_provider::ToolDefinition> {
    let Ok(config) = opencode_config::load_config(&cwd) else {
        return Vec::new();
    };
    let declared = config.mcp.clone().unwrap_or_default();
    if declared.is_empty() {
        return Vec::new();
    }

    let registry = opencode_mcp::McpClientRegistry::new();
    for (name, entry) in &declared {
        let opencode_config::McpServerConfig::Full(server) = entry else {
            continue;
        };
        if server.enabled == Some(false) {
            continue;
        }
        let Some(command) = server.command.first().cloned() else {
            continue;
        };
        let mut args: Vec<String> = server.command.iter().skip(1).cloned().collect();
        args.extend(server.args.iter().cloned());

        let cfg = opencode_mcp::McpServerConfig {
            name: name.clone(),
            command,
            args,
            env: server
                .environment
                .as_ref()
                .map(|m| m.iter().map(|(k, v)| (k.clone(), v.clone())).collect()),
            timeout_ms: server.timeout,
        };

        match registry.add_stdio(cfg).await {
            Ok(_) => tracing::info!(mcp = %name, "MCP server started"),
            Err(e) => tracing::warn!(mcp = %name, error = %e, "MCP server failed to start"),
        }
    }

    registry
        .tool_registry()
        .list()
        .await
        .into_iter()
        .map(|tool| opencode_provider::ToolDefinition {
            name: tool.full_name,
            description: tool.description,
            parameters: tool.input_schema,
        })
        .collect()
}
