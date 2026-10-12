#!/usr/bin/env bash
set -euo pipefail

# Standalone installer. Translations are generated from locales/*/installer.json;
# runtime locale data is never sourced or evaluated. Bash 3.2 is supported.
# BEGIN GENERATED INSTALLER MESSAGES
# Generated from claude_ads_core/locales/{en,zh-CN}/installer.json. Do not edit.
locale_template() {
    case "$CLAUDE_ADS_SELECTED_LOCALE:$1" in
        en:installer.agent_count) LOCALE_TEMPLATE='{count} agents' ;;
        en:installer.agent_root_missing) LOCALE_TEMPLATE='Agent root not found: {path}' ;;
        en:installer.agents_path) LOCALE_TEMPLATE='Agents: {path}' ;;
        en:installer.authority_not_owned) LOCALE_TEMPLATE='Ownership authority is not owned by the current Windows identity: {path}' ;;
        en:installer.bash_manifest) LOCALE_TEMPLATE='Bash ownership manifest detected: {path}. Continue with install.sh, or uninstall with uninstall.sh before switching installers.' ;;
        en:installer.bundled) LOCALE_TEMPLATE='Bundled:' ;;
        en:installer.cleanup_refused) LOCALE_TEMPLATE='Exact hashed dependency installation failed; unsafe managed environment cleanup was refused: {detail}' ;;
        en:installer.continue_powershell) LOCALE_TEMPLATE='Continue with install.ps1, or uninstall with uninstall.ps1 before switching installers.' ;;
        en:installer.copy_failed) LOCALE_TEMPLATE='Could not install resource: {path}' ;;
        en:installer.dependencies_failed) LOCALE_TEMPLATE='Exact hashed dependency installation failed; no moving-range fallback was attempted.' ;;
        en:installer.dependencies_installed) LOCALE_TEMPLATE='Exact locked Python dependencies installed in {path}' ;;
        en:installer.destination_escape) LOCALE_TEMPLATE='Install destination escapes configured roots: {path}' ;;
        en:installer.destination_not_directory) LOCALE_TEMPLATE='Install directory destination is not a directory: {path}' ;;
        en:installer.directory_changed) LOCALE_TEMPLATE='Owned directory changed type before deletion: {path}' ;;
        en:installer.directory_escape) LOCALE_TEMPLATE='Install directory escapes configured roots: {path}' ;;
        en:installer.directory_is_file) LOCALE_TEMPLATE='Owned directory entry is not a directory: {path}' ;;
        en:installer.downloading) LOCALE_TEMPLATE='Downloading Claude Ads with authenticated Git...' ;;
        en:installer.duplicate_manifest_directory) LOCALE_TEMPLATE='Duplicate ownership-manifest directory: {path}' ;;
        en:installer.duplicate_manifest_file) LOCALE_TEMPLATE='Duplicate ownership-manifest file: {path}' ;;
        en:installer.duplicate_manifest_path) LOCALE_TEMPLATE='Duplicate ownership-manifest path: {path}' ;;
        en:installer.duplicate_manifest_recursive) LOCALE_TEMPLATE='Duplicate recursive ownership-manifest directory: {path}' ;;
        en:installer.duplicate_planned_file) LOCALE_TEMPLATE='Duplicate planned install file: {path}' ;;
        en:installer.empty_manifest_path) LOCALE_TEMPLATE='Invalid empty ownership-manifest path' ;;
        en:installer.file_changed) LOCALE_TEMPLATE='Owned file changed type before deletion: {path}' ;;
        en:installer.file_is_directory) LOCALE_TEMPLATE='Owned file entry is a directory: {path}' ;;
        en:installer.git_failed) LOCALE_TEMPLATE='Git clone failed' ;;
        en:installer.git_required) LOCALE_TEMPLATE='Git is required for {option}.' ;;
        en:installer.help_install_ps) LOCALE_TEMPLATE='Claude Ads Installer
Usage: .\install.ps1 [-Target <host>] [-SkillDir <path>] [-AgentDir <path>]
                     [-Source auto|local|git] [-RepoDir <path>] [-NoDeps]
                     [-Locale zh-CN|en] [-Help]
Targets: claude (default, verified); codex, cursor, windsurf, gemini, goose (experimental).
-RepoDir selects a local checkout; -NoDeps skips the managed Python environment.
Language: explicit -Locale > CLAUDE_ADS_LOCALE > prior install > zh-CN.
This changes operator language, not advertising or creative delivery language.
Prefer native installation or a locally inspected, checksum-verified release.
Never pipe remote content to PowerShell.' ;;
        en:installer.help_install_sh) LOCALE_TEMPLATE='Claude Ads Installer

Usage:
  bash install.sh [--target=<host>] [--skill-dir=<path>] [--agent-dir=<path>]
                  [--source=<auto|local|git>] [--repo-dir=<path>] [--no-deps]
                  [--locale=<zh-CN|en>]

Targets (default: claude):
  claude     Claude Code (verified)
  codex      OpenAI Codex CLI (experimental)
  cursor     Cursor IDE (experimental)
  windsurf   Windsurf IDE (experimental)
  gemini     Gemini CLI (experimental)
  goose      Goose CLI (experimental)

Overrides:
  --skill-dir=<path>   Override the target'"'"'s default skill install root
  --agent-dir=<path>   Override the target'"'"'s default agent install root
  --source=<mode>      auto uses this checkout when available, otherwise authenticated Git
  --repo-dir=<path>    Local checkout to install (implies --source=local)
  --no-deps            Do not create the verified managed Python environment
  --locale=<locale>    Operator language: explicit flag > CLAUDE_ADS_LOCALE > prior install > zh-CN
                      Does not change advertising or creative delivery language.

Examples:
  bash install.sh --source=local --no-deps
  bash install.sh --locale=en --source=local --no-deps
  bash install.sh --target=codex

Security:
  Prefer a host-native plugin install or a signed release archive with a
  verified SHA-256 checksum. Never pipe a remote installer directly to a shell.' ;;
        en:installer.help_uninstall_ps) LOCALE_TEMPLATE='Usage: .\uninstall.ps1 [-Target <host>] [-SkillDir <path>] [-AgentDir <path>] [-Locale zh-CN|en] [-Help]
Language: explicit -Locale > CLAUDE_ADS_LOCALE > prior install > zh-CN.
Only ownership-manifest paths are removed; the owned locale preference is removed too.' ;;
        en:installer.help_uninstall_sh) LOCALE_TEMPLATE='Usage: bash uninstall.sh [--target=<host>] [--skill-dir=<path>] [--agent-dir=<path>] [--locale=<zh-CN|en>]
Language: explicit flag > CLAUDE_ADS_LOCALE > prior install > zh-CN.
Only ownership-manifest paths are removed; the owned locale preference is removed too.' ;;
        en:installer.home_unknown) LOCALE_TEMPLATE='Cannot determine the current user'"'"'s home directory.' ;;
        en:installer.host_skip_dependencies) LOCALE_TEMPLATE='Skipping Python dependencies - {host} host runtime may not execute Python skills directly.' ;;
        en:installer.image_provider_required) LOCALE_TEMPLATE='Image generation requires an explicitly configured eligible provider/model with capability evidence; Claude Ads does not probe or recommend a default.' ;;
        en:installer.install_agents) LOCALE_TEMPLATE='Installing subagents...' ;;
        en:installer.install_dependencies) LOCALE_TEMPLATE='Installing exact hashed Python dependencies into a managed virtual environment...' ;;
        en:installer.install_guarded) LOCALE_TEMPLATE='Installing guarded skill, sub-skill, agent, and runtime files...' ;;
        en:installer.install_parent_not_directory) LOCALE_TEMPLATE='Install path parent is not a directory: {path}' ;;
        en:installer.install_scripts) LOCALE_TEMPLATE='Installing Python scripts and locale resources...' ;;
        en:installer.install_skills) LOCALE_TEMPLATE='Installing skill files...' ;;
        en:installer.install_subskills) LOCALE_TEMPLATE='Installing sub-skills...' ;;
        en:installer.installed) LOCALE_TEMPLATE='Claude Ads installed successfully for {host}!' ;;
        en:installer.installed_paths) LOCALE_TEMPLATE='Installed to:' ;;
        en:installer.invalid_distribution) LOCALE_TEMPLATE='Local source is not a Claude Ads distribution: {path}' ;;
        en:installer.invalid_locale) LOCALE_TEMPLATE='Unsupported locale: {locale}. Use zh-CN or en.' ;;
        en:installer.invalid_manifest) LOCALE_TEMPLATE='Invalid ownership manifest: {path}' ;;
        en:installer.invalid_manifest_entry) LOCALE_TEMPLATE='Invalid ownership-manifest entry in {property}: {path}' ;;
        en:installer.invalid_manifest_path) LOCALE_TEMPLATE='Invalid ownership manifest path: {path}' ;;
        en:installer.invalid_path_option) LOCALE_TEMPLATE='Invalid {option}: contains forbidden characters or traversal' ;;
        en:installer.invalid_repository_path) LOCALE_TEMPLATE='Invalid local repository path' ;;
        en:installer.invalid_source) LOCALE_TEMPLATE='Invalid source: {value}. Use auto, local, or git.' ;;
        en:installer.io_failed) LOCALE_TEMPLATE='Filesystem operation failed; no further changes were attempted.' ;;
        en:installer.legacy_detected) LOCALE_TEMPLATE='Existing Claude Ads files without an ownership manifest detected:' ;;
        en:installer.legacy_explanation) LOCALE_TEMPLATE='Installs older than v2.0.0 wrote no ownership manifest, so this installer cannot verify what it may overwrite.' ;;
        en:installer.legacy_manifest_missing) LOCALE_TEMPLATE='Installs older than v2.0.0 wrote no ownership manifest.' ;;
        en:installer.legacy_removal) LOCALE_TEMPLATE='Remove the old install manually, then re-run. Paths this installer would own for target {target}:' ;;
        en:installer.locale_file_invalid) LOCALE_TEMPLATE='Invalid locale preference data: {path}. Expected exactly en or zh-CN followed by one newline.' ;;
        en:installer.locale_file_unsafe) LOCALE_TEMPLATE='Locale preference is not a safe, owned regular file: {path}' ;;
        en:installer.main_count) LOCALE_TEMPLATE='1 main skill (ads orchestrator)' ;;
        en:installer.manifest_array) LOCALE_TEMPLATE='Ownership manifest property must be an array: {property}' ;;
        en:installer.manifest_changed) LOCALE_TEMPLATE='Ownership manifest changed before deletion: {path}' ;;
        en:installer.manifest_missing) LOCALE_TEMPLATE='Ownership manifest not found: {path}' ;;
        en:installer.manifest_missing_unsafe) LOCALE_TEMPLATE='Ownership manifest not found or unsafe: {path}. Refusing namespace-based deletion.' ;;
        en:installer.manifest_not_owned) LOCALE_TEMPLATE='Ownership manifest is not owned by the current principal: {path}' ;;
        en:installer.manifest_owns_root) LOCALE_TEMPLATE='Ownership manifest cannot own a configured root: {path}' ;;
        en:installer.manifest_written) LOCALE_TEMPLATE='Ownership manifest: {path}' ;;
        en:installer.mismatched_manifest) LOCALE_TEMPLATE='Invalid or mismatched ownership manifest: {path}' ;;
        en:installer.musl_unsupported) LOCALE_TEMPLATE='Managed dependencies require glibc >=2.17; musl Linux is unsupported. Re-run with --no-deps.' ;;
        en:installer.noncanonical_manifest_path) LOCALE_TEMPLATE='Non-canonical ownership-manifest path: {path}' ;;
        en:installer.operator_language_rule) LOCALE_TEMPLATE='<!-- claude-ads:operator-language -->
## Operator language

Use English for operator-facing explanations, questions, summaries, help, and reports unless the operator explicitly requests another language. This preference must not change campaign targeting, advertising language, creative copy language, locale identifiers, machine-readable keys, or account data. Ask for the advertising delivery language separately when it is not specified.
' ;;
        en:installer.powershell_manifest) LOCALE_TEMPLATE='PowerShell ownership manifest detected: {path}' ;;
        en:installer.python_lock_required) LOCALE_TEMPLATE='Python helpers require the packaged exact-hash lock on a supported CPython wheel target.' ;;
        en:installer.python_missing) LOCALE_TEMPLATE='{command} not found. Re-run with {option} to install without Python helpers.' ;;
        en:installer.receipt_invalidate_failed) LOCALE_TEMPLATE='Could not invalidate the prior managed runtime receipt.' ;;
        en:installer.recursive_not_directory) LOCALE_TEMPLATE='Managed recursive path is not a directory: {path}' ;;
        en:installer.recursive_reparse) LOCALE_TEMPLATE='Refusing reparse point inside managed recursive directory: {path}' ;;
        en:installer.reference_count) LOCALE_TEMPLATE='{count} reference files' ;;
        en:installer.refuse_namespace) LOCALE_TEMPLATE='Refusing namespace-based deletion. Remove a legacy install manually after reviewing its files.' ;;
        en:installer.reparse_install) LOCALE_TEMPLATE='Refusing reparse-point install path: {path}' ;;
        en:installer.reparse_uninstall) LOCALE_TEMPLATE='Refusing reparse-point uninstall path: {path}' ;;
        en:installer.repository_missing) LOCALE_TEMPLATE='Local repository does not exist: {path}' ;;
        en:installer.requires_value) LOCALE_TEMPLATE='{option} requires a value' ;;
        en:installer.root_not_directory) LOCALE_TEMPLATE='Configured install root is not a directory: {path}' ;;
        en:installer.roots_overlap) LOCALE_TEMPLATE='Skill and agent install roots must not overlap: {skills} ; {agents}' ;;
        en:installer.run_commands) LOCALE_TEMPLATE='2. Run commands: /ads audit; /ads plan saas; /ads google' ;;
        en:installer.run_help) LOCALE_TEMPLATE='Run: {command}' ;;
        en:installer.selected_locale) LOCALE_TEMPLATE='Operator language: {locale}. Advertising delivery language is unchanged.' ;;
        en:installer.skill_root_missing) LOCALE_TEMPLATE='Skill root not found: {path}' ;;
        en:installer.skills_path) LOCALE_TEMPLATE='Skills: {path}' ;;
        en:installer.skip_dependencies) LOCALE_TEMPLATE='Skipping Python dependencies ({option}).' ;;
        en:installer.source) LOCALE_TEMPLATE='Distribution source: {source}' ;;
        en:installer.source_escape) LOCALE_TEMPLATE='Source path is outside its declared base: {path}' ;;
        en:installer.source_not_file) LOCALE_TEMPLATE='Distribution resource is not a regular file: {path}' ;;
        en:installer.source_symlink) LOCALE_TEMPLATE='Refusing symlink or reparse point in distribution resources: {path}' ;;
        en:installer.source_too_deep) LOCALE_TEMPLATE='Distribution resource tree exceeds the maximum depth: {path}' ;;
        en:installer.source_too_large) LOCALE_TEMPLATE='Distribution resource tree exceeds the file limit: {path}' ;;
        en:installer.start_host) LOCALE_TEMPLATE='1. Start your host CLI' ;;
        en:installer.subskill_count) LOCALE_TEMPLATE='{count} sub-skills (platform + lifecycle + functional + creative)' ;;
        en:installer.symlink_directory) LOCALE_TEMPLATE='Refusing symlinked install directory: {path}' ;;
        en:installer.symlink_file) LOCALE_TEMPLATE='Refusing symlinked install file: {path}' ;;
        en:installer.target) LOCALE_TEMPLATE='Target: {host}' ;;
        en:installer.template_count) LOCALE_TEMPLATE='{count} industry templates' ;;
        en:installer.title) LOCALE_TEMPLATE='Claude Ads Installer' ;;
        en:installer.uninstall_command) LOCALE_TEMPLATE='To uninstall: {command}' ;;
        en:installer.uninstall_parent_not_directory) LOCALE_TEMPLATE='Uninstall path parent is not a directory: {path}' ;;
        en:installer.uninstall_recursive_not_directory) LOCALE_TEMPLATE='Recursive ownership entry is not a directory: {path}' ;;
        en:installer.uninstall_recursive_reparse) LOCALE_TEMPLATE='Refusing reparse point inside recursive ownership directory: {path}' ;;
        en:installer.uninstalled) LOCALE_TEMPLATE='Claude Ads uninstalled.' ;;
        en:installer.uninstalling) LOCALE_TEMPLATE='Uninstalling Claude Ads from {skills} and {agents}...' ;;
        en:installer.unknown_argument) LOCALE_TEMPLATE='Unknown argument: {value}' ;;
        en:installer.unknown_manifest_record) LOCALE_TEMPLATE='Unknown ownership-manifest record: {kind}' ;;
        en:installer.unknown_target) LOCALE_TEMPLATE='Unknown target: {value}' ;;
        en:installer.unowned_environment) LOCALE_TEMPLATE='Refusing to reuse unowned managed environment: {path}' ;;
        en:installer.unowned_file) LOCALE_TEMPLATE='Refusing to overwrite unowned file: {path}' ;;
        en:installer.unsafe_manifest_path) LOCALE_TEMPLATE='Unsafe ownership-manifest path: {path}' ;;
        en:installer.unsupported_lock) LOCALE_TEMPLATE='No verified dependency lock target for {target}. Re-run with {option}; moving-range fallback is disabled.' ;;
        en:installer.usage) LOCALE_TEMPLATE='Usage:' ;;
        en:installer.valid_targets) LOCALE_TEMPLATE='Valid targets: claude, codex, cursor, windsurf, gemini, goose' ;;
        en:installer.windows_python) LOCALE_TEMPLATE='install.sh does not manage Windows Python dependencies. Use install.ps1 -Source local.' ;;
        zh-CN:installer.agent_count) LOCALE_TEMPLATE='{count} 个代理' ;;
        zh-CN:installer.agent_root_missing) LOCALE_TEMPLATE='未找到代理根目录：{path}' ;;
        zh-CN:installer.agents_path) LOCALE_TEMPLATE='代理：{path}' ;;
        zh-CN:installer.authority_not_owned) LOCALE_TEMPLATE='所有权凭据不属于当前 Windows 身份：{path}' ;;
        zh-CN:installer.bash_manifest) LOCALE_TEMPLATE='检测到 Bash 所有权清单：{path}。请继续使用 install.sh，或先运行 uninstall.sh 卸载，再切换安装器。' ;;
        zh-CN:installer.bundled) LOCALE_TEMPLATE='已包含：' ;;
        zh-CN:installer.cleanup_refused) LOCALE_TEMPLATE='精确哈希依赖安装失败；已拒绝不安全的托管环境清理：{detail}' ;;
        zh-CN:installer.continue_powershell) LOCALE_TEMPLATE='请继续使用 install.ps1，或先运行 uninstall.ps1 卸载，再切换安装器。' ;;
        zh-CN:installer.copy_failed) LOCALE_TEMPLATE='无法安装资源：{path}' ;;
        zh-CN:installer.dependencies_failed) LOCALE_TEMPLATE='精确哈希依赖安装失败；未尝试回退到浮动版本范围。' ;;
        zh-CN:installer.dependencies_installed) LOCALE_TEMPLATE='已在 {path} 安装精确锁定的 Python 依赖' ;;
        zh-CN:installer.destination_escape) LOCALE_TEMPLATE='安装目标超出配置的根目录：{path}' ;;
        zh-CN:installer.destination_not_directory) LOCALE_TEMPLATE='安装目录的目标不是目录：{path}' ;;
        zh-CN:installer.directory_changed) LOCALE_TEMPLATE='已拥有的目录在删除前改变了类型：{path}' ;;
        zh-CN:installer.directory_escape) LOCALE_TEMPLATE='安装目录超出配置的根目录：{path}' ;;
        zh-CN:installer.directory_is_file) LOCALE_TEMPLATE='已拥有的目录条目实际不是目录：{path}' ;;
        zh-CN:installer.downloading) LOCALE_TEMPLATE='正在通过已认证的 Git 下载 Claude Ads...' ;;
        zh-CN:installer.duplicate_manifest_directory) LOCALE_TEMPLATE='重复的所有权清单目录：{path}' ;;
        zh-CN:installer.duplicate_manifest_file) LOCALE_TEMPLATE='重复的所有权清单文件：{path}' ;;
        zh-CN:installer.duplicate_manifest_path) LOCALE_TEMPLATE='重复的所有权清单路径：{path}' ;;
        zh-CN:installer.duplicate_manifest_recursive) LOCALE_TEMPLATE='重复的递归所有权清单目录：{path}' ;;
        zh-CN:installer.duplicate_planned_file) LOCALE_TEMPLATE='重复的计划安装文件：{path}' ;;
        zh-CN:installer.empty_manifest_path) LOCALE_TEMPLATE='所有权清单路径为空，无效' ;;
        zh-CN:installer.file_changed) LOCALE_TEMPLATE='已拥有的文件在删除前改变了类型：{path}' ;;
        zh-CN:installer.file_is_directory) LOCALE_TEMPLATE='已拥有的文件条目实际是目录：{path}' ;;
        zh-CN:installer.git_failed) LOCALE_TEMPLATE='Git 克隆失败' ;;
        zh-CN:installer.git_required) LOCALE_TEMPLATE='{option} 需要 Git。' ;;
        zh-CN:installer.help_install_ps) LOCALE_TEMPLATE='Claude Ads 安装器
用法：.\install.ps1 [-Target <host>] [-SkillDir <path>] [-AgentDir <path>]
                     [-Source auto|local|git] [-RepoDir <path>] [-NoDeps]
                     [-Locale zh-CN|en] [-Help]
目标宿主：claude（默认，已验证）；codex、cursor、windsurf、gemini、goose（实验性）。
-RepoDir 选择本地源码；-NoDeps 跳过托管 Python 环境。
语言优先级：明确 -Locale 参数 > CLAUDE_ADS_LOCALE > 上次安装选择 > zh-CN。
此选项改变操作语言，不改变广告投放语言或创意文案语言。
优先使用原生安装，或已在本地审查并验证校验和的发行包。
绝不可通过管道将远程内容传给 PowerShell 执行。' ;;
        zh-CN:installer.help_install_sh) LOCALE_TEMPLATE='Claude Ads 安装器

用法：
  bash install.sh [--target=<host>] [--skill-dir=<path>] [--agent-dir=<path>]
                  [--source=<auto|local|git>] [--repo-dir=<path>] [--no-deps]
                  [--locale=<zh-CN|en>]

目标宿主（默认：claude）：
  claude     Claude Code（已验证）
  codex      OpenAI Codex CLI（实验性）
  cursor     Cursor IDE（实验性）
  windsurf   Windsurf IDE（实验性）
  gemini     Gemini CLI（实验性）
  goose      Goose CLI（实验性）

选项：
  --skill-dir=<path>   覆盖目标宿主默认的技能安装根目录
  --agent-dir=<path>   覆盖目标宿主默认的代理安装根目录
  --source=<mode>      auto 优先使用当前源码，否则使用已认证的 Git
  --repo-dir=<path>    要安装的本地源码目录（同时启用 --source=local）
  --no-deps            不创建已验证的托管 Python 环境
  --locale=<locale>    操作语言优先级：明确参数 > CLAUDE_ADS_LOCALE > 上次安装选择 > zh-CN
                      不改变广告投放语言或创意文案语言。

示例：
  bash install.sh --source=local --no-deps
  bash install.sh --locale=en --source=local --no-deps
  bash install.sh --target=codex

安全：
  优先使用宿主原生插件安装，或具有已验证 SHA-256 校验和的签名发行包。
  绝不可通过管道将远程安装器直接传给 Shell 执行。' ;;
        zh-CN:installer.help_uninstall_ps) LOCALE_TEMPLATE='用法：.\uninstall.ps1 [-Target <host>] [-SkillDir <path>] [-AgentDir <path>] [-Locale zh-CN|en] [-Help]
语言优先级：明确 -Locale 参数 > CLAUDE_ADS_LOCALE > 上次安装选择 > zh-CN。
仅删除所有权清单记录的路径；已拥有的语言选择文件也会删除。' ;;
        zh-CN:installer.help_uninstall_sh) LOCALE_TEMPLATE='用法：bash uninstall.sh [--target=<host>] [--skill-dir=<path>] [--agent-dir=<path>] [--locale=<zh-CN|en>]
语言优先级：明确参数 > CLAUDE_ADS_LOCALE > 上次安装选择 > zh-CN。
仅删除所有权清单记录的路径；已拥有的语言选择文件也会删除。' ;;
        zh-CN:installer.home_unknown) LOCALE_TEMPLATE='无法确定当前用户的主目录。' ;;
        zh-CN:installer.host_skip_dependencies) LOCALE_TEMPLATE='已跳过 Python 依赖——{host} 宿主运行时可能无法直接执行 Python 技能。' ;;
        zh-CN:installer.image_provider_required) LOCALE_TEMPLATE='图像生成需要明确配置符合条件的服务商和模型，并提供能力证据；Claude Ads 不会探测或推荐默认选项。' ;;
        zh-CN:installer.install_agents) LOCALE_TEMPLATE='正在安装子代理...' ;;
        zh-CN:installer.install_dependencies) LOCALE_TEMPLATE='正在托管虚拟环境中安装经过精确哈希校验的 Python 依赖...' ;;
        zh-CN:installer.install_guarded) LOCALE_TEMPLATE='正在安装经过安全检查的技能、子技能、代理和运行时文件...' ;;
        zh-CN:installer.install_parent_not_directory) LOCALE_TEMPLATE='安装路径的父级不是目录：{path}' ;;
        zh-CN:installer.install_scripts) LOCALE_TEMPLATE='正在安装 Python 脚本和语言资源...' ;;
        zh-CN:installer.install_skills) LOCALE_TEMPLATE='正在安装主技能文件...' ;;
        zh-CN:installer.install_subskills) LOCALE_TEMPLATE='正在安装子技能...' ;;
        zh-CN:installer.installed) LOCALE_TEMPLATE='已成功为 {host} 安装 Claude Ads！' ;;
        zh-CN:installer.installed_paths) LOCALE_TEMPLATE='安装位置：' ;;
        zh-CN:installer.invalid_distribution) LOCALE_TEMPLATE='本地来源不是 Claude Ads 发行包：{path}' ;;
        zh-CN:installer.invalid_locale) LOCALE_TEMPLATE='不支持的语言：{locale}。请使用 zh-CN 或 en。' ;;
        zh-CN:installer.invalid_manifest) LOCALE_TEMPLATE='无效的所有权清单：{path}' ;;
        zh-CN:installer.invalid_manifest_entry) LOCALE_TEMPLATE='{property} 中的所有权清单条目无效：{path}' ;;
        zh-CN:installer.invalid_manifest_path) LOCALE_TEMPLATE='无效的所有权清单路径：{path}' ;;
        zh-CN:installer.invalid_path_option) LOCALE_TEMPLATE='无效的 {option}：包含禁止字符或路径穿越' ;;
        zh-CN:installer.invalid_repository_path) LOCALE_TEMPLATE='无效的本地源码路径' ;;
        zh-CN:installer.invalid_source) LOCALE_TEMPLATE='无效的安装来源：{value}。请使用 auto、local 或 git。' ;;
        zh-CN:installer.io_failed) LOCALE_TEMPLATE='文件系统操作失败；未继续进行更改。' ;;
        zh-CN:installer.legacy_detected) LOCALE_TEMPLATE='检测到没有所有权清单的现有 Claude Ads 文件：' ;;
        zh-CN:installer.legacy_explanation) LOCALE_TEMPLATE='v2.0.0 之前的安装不会写入所有权清单，因此本安装器无法确认哪些文件可以覆盖。' ;;
        zh-CN:installer.legacy_manifest_missing) LOCALE_TEMPLATE='v2.0.0 之前的安装不会写入所有权清单。' ;;
        zh-CN:installer.legacy_removal) LOCALE_TEMPLATE='请手动删除旧版安装，再重新运行。目标 {target} 下本安装器将拥有的路径：' ;;
        zh-CN:installer.locale_file_invalid) LOCALE_TEMPLATE='语言选择文件数据无效：{path}。必须仅包含 en 或 zh-CN，并以一个换行符结尾。' ;;
        zh-CN:installer.locale_file_unsafe) LOCALE_TEMPLATE='语言选择文件不是安全且已拥有的普通文件：{path}' ;;
        zh-CN:installer.main_count) LOCALE_TEMPLATE='1 个主技能（ads 编排器）' ;;
        zh-CN:installer.manifest_array) LOCALE_TEMPLATE='所有权清单属性必须是数组：{property}' ;;
        zh-CN:installer.manifest_changed) LOCALE_TEMPLATE='所有权清单在删除前发生了变化：{path}' ;;
        zh-CN:installer.manifest_missing) LOCALE_TEMPLATE='未找到所有权清单：{path}' ;;
        zh-CN:installer.manifest_missing_unsafe) LOCALE_TEMPLATE='未找到所有权清单或其不安全：{path}。拒绝按命名空间删除。' ;;
        zh-CN:installer.manifest_not_owned) LOCALE_TEMPLATE='所有权清单不属于当前用户主体：{path}' ;;
        zh-CN:installer.manifest_owns_root) LOCALE_TEMPLATE='所有权清单不能拥有配置的根目录：{path}' ;;
        zh-CN:installer.manifest_written) LOCALE_TEMPLATE='所有权清单：{path}' ;;
        zh-CN:installer.mismatched_manifest) LOCALE_TEMPLATE='所有权清单无效或不匹配：{path}' ;;
        zh-CN:installer.musl_unsupported) LOCALE_TEMPLATE='托管依赖要求 glibc >=2.17；不支持 musl Linux。请加上 --no-deps 重新运行。' ;;
        zh-CN:installer.noncanonical_manifest_path) LOCALE_TEMPLATE='所有权清单路径不规范：{path}' ;;
        zh-CN:installer.operator_language_rule) LOCALE_TEMPLATE='<!-- claude-ads:operator-language -->
## 操作语言

除非操作者明确要求其他语言，否则面向操作者的解释、问题、摘要、帮助和报告均使用简体中文。此偏好不得改变广告定向、广告投放语言、创意文案语言、语言标识符、机器可读键名或账户数据。未指定广告投放语言时，应单独询问。
' ;;
        zh-CN:installer.powershell_manifest) LOCALE_TEMPLATE='检测到 PowerShell 所有权清单：{path}' ;;
        zh-CN:installer.python_lock_required) LOCALE_TEMPLATE='Python 辅助工具要求受支持的 CPython wheel 目标及发行包内的精确哈希锁定文件。' ;;
        zh-CN:installer.python_missing) LOCALE_TEMPLATE='未找到 {command}。请加上 {option} 重新运行，以跳过 Python 辅助工具的依赖安装。' ;;
        zh-CN:installer.receipt_invalidate_failed) LOCALE_TEMPLATE='无法使之前的托管运行时凭据失效。' ;;
        zh-CN:installer.recursive_not_directory) LOCALE_TEMPLATE='托管递归路径不是目录：{path}' ;;
        zh-CN:installer.recursive_reparse) LOCALE_TEMPLATE='拒绝托管递归目录内的重解析点：{path}' ;;
        zh-CN:installer.reference_count) LOCALE_TEMPLATE='{count} 个参考文件' ;;
        zh-CN:installer.refuse_namespace) LOCALE_TEMPLATE='拒绝按命名空间删除。请先审查旧版安装的文件，再手动删除。' ;;
        zh-CN:installer.reparse_install) LOCALE_TEMPLATE='拒绝使用重解析点安装路径：{path}' ;;
        zh-CN:installer.reparse_uninstall) LOCALE_TEMPLATE='拒绝使用重解析点卸载路径：{path}' ;;
        zh-CN:installer.repository_missing) LOCALE_TEMPLATE='本地源码目录不存在：{path}' ;;
        zh-CN:installer.requires_value) LOCALE_TEMPLATE='{option} 必须指定值' ;;
        zh-CN:installer.root_not_directory) LOCALE_TEMPLATE='配置的安装根路径不是目录：{path}' ;;
        zh-CN:installer.roots_overlap) LOCALE_TEMPLATE='技能和代理的安装根目录不能重叠：{skills}；{agents}' ;;
        zh-CN:installer.run_commands) LOCALE_TEMPLATE='2. 运行命令：/ads audit；/ads plan saas；/ads google' ;;
        zh-CN:installer.run_help) LOCALE_TEMPLATE='运行：{command}' ;;
        zh-CN:installer.selected_locale) LOCALE_TEMPLATE='操作语言：{locale}。广告投放语言保持不变。' ;;
        zh-CN:installer.skill_root_missing) LOCALE_TEMPLATE='未找到技能根目录：{path}' ;;
        zh-CN:installer.skills_path) LOCALE_TEMPLATE='技能：{path}' ;;
        zh-CN:installer.skip_dependencies) LOCALE_TEMPLATE='已跳过 Python 依赖（{option}）。' ;;
        zh-CN:installer.source) LOCALE_TEMPLATE='发行包来源：{source}' ;;
        zh-CN:installer.source_escape) LOCALE_TEMPLATE='来源路径超出其声明的根目录：{path}' ;;
        zh-CN:installer.source_not_file) LOCALE_TEMPLATE='发行包资源不是普通文件：{path}' ;;
        zh-CN:installer.source_symlink) LOCALE_TEMPLATE='拒绝发行包资源中的符号链接或重解析点：{path}' ;;
        zh-CN:installer.source_too_deep) LOCALE_TEMPLATE='发行包资源树超过最大深度：{path}' ;;
        zh-CN:installer.source_too_large) LOCALE_TEMPLATE='发行包资源树超过文件数量限制：{path}' ;;
        zh-CN:installer.start_host) LOCALE_TEMPLATE='1. 启动宿主 CLI' ;;
        zh-CN:installer.subskill_count) LOCALE_TEMPLATE='{count} 个子技能（平台、生命周期、功能与创意）' ;;
        zh-CN:installer.symlink_directory) LOCALE_TEMPLATE='拒绝使用符号链接安装目录：{path}' ;;
        zh-CN:installer.symlink_file) LOCALE_TEMPLATE='拒绝使用符号链接安装文件：{path}' ;;
        zh-CN:installer.target) LOCALE_TEMPLATE='目标宿主：{host}' ;;
        zh-CN:installer.template_count) LOCALE_TEMPLATE='{count} 个行业模板' ;;
        zh-CN:installer.title) LOCALE_TEMPLATE='Claude Ads 安装器' ;;
        zh-CN:installer.uninstall_command) LOCALE_TEMPLATE='卸载命令：{command}' ;;
        zh-CN:installer.uninstall_parent_not_directory) LOCALE_TEMPLATE='卸载路径的父级不是目录：{path}' ;;
        zh-CN:installer.uninstall_recursive_not_directory) LOCALE_TEMPLATE='递归所有权条目不是目录：{path}' ;;
        zh-CN:installer.uninstall_recursive_reparse) LOCALE_TEMPLATE='拒绝递归所有权目录内的重解析点：{path}' ;;
        zh-CN:installer.uninstalled) LOCALE_TEMPLATE='Claude Ads 已卸载。' ;;
        zh-CN:installer.uninstalling) LOCALE_TEMPLATE='正在从 {skills} 和 {agents} 卸载 Claude Ads...' ;;
        zh-CN:installer.unknown_argument) LOCALE_TEMPLATE='未知参数：{value}' ;;
        zh-CN:installer.unknown_manifest_record) LOCALE_TEMPLATE='未知的所有权清单记录：{kind}' ;;
        zh-CN:installer.unknown_target) LOCALE_TEMPLATE='未知目标宿主：{value}' ;;
        zh-CN:installer.unowned_environment) LOCALE_TEMPLATE='拒绝复用无所有权的托管环境：{path}' ;;
        zh-CN:installer.unowned_file) LOCALE_TEMPLATE='拒绝覆盖无所有权的文件：{path}' ;;
        zh-CN:installer.unsafe_manifest_path) LOCALE_TEMPLATE='不安全的所有权清单路径：{path}' ;;
        zh-CN:installer.unsupported_lock) LOCALE_TEMPLATE='{target} 没有已验证的依赖锁定目标。请加上 {option} 重新运行；禁止回退到浮动版本范围。' ;;
        zh-CN:installer.usage) LOCALE_TEMPLATE='用法：' ;;
        zh-CN:installer.valid_targets) LOCALE_TEMPLATE='有效目标宿主：claude、codex、cursor、windsurf、gemini、goose' ;;
        zh-CN:installer.windows_python) LOCALE_TEMPLATE='install.sh 不管理 Windows Python 依赖。请使用 install.ps1 -Source local。' ;;
        *) return 1 ;;
    esac
}
# END GENERATED INSTALLER MESSAGES

CLAUDE_ADS_SELECTED_LOCALE=zh-CN
LOCALE_EXPLICIT=0

# Consume only template text while substituting values, never substituted values.
# This also keeps {name}, $, backticks, %, and backslashes in arguments literal.
locale_message() {
    local key="$1" text prefix name found value arg
    shift
    locale_template "$key" || return 1
    text="$LOCALE_TEMPLATE"
    while [[ "$text" == *'{'* ]]; do
        prefix="${text%%\{*}"
        printf '%s' "$prefix"
        text="${text#*\{}"
        name="${text%%\}*}"
        text="${text#*\}}"
        found=0
        for arg in "$@"; do
            if [ "${arg%%=*}" = "$name" ]; then
                value="${arg#*=}"
                printf '%s' "$value"
                found=1
                break
            fi
        done
        [ "$found" = 1 ] || return 1
    done
    printf '%s\n' "$text"
}
fail() { locale_message "$@" >&2; return 1; }

# Scan all arguments first so --locale=en also localizes an earlier error/help.
select_cli_locale() {
    local requested="${CLAUDE_ADS_LOCALE:-zh-CN}" missing=0
    [ -z "${CLAUDE_ADS_LOCALE:-}" ] || LOCALE_EXPLICIT=1
    while [ $# -gt 0 ]; do
        case "$1" in
            --locale=*) requested="${1#*=}"; LOCALE_EXPLICIT=1 ;;
            --locale)
                shift
                if [ $# -eq 0 ]; then missing=1; break; fi
                requested="$1"; LOCALE_EXPLICIT=1 ;;
            --target|--skill-dir|--agent-dir|--source|--repo-dir)
                shift; [ $# -gt 0 ] || break ;;
        esac
        shift
    done
    case "$requested" in
        en|zh-CN) CLAUDE_ADS_SELECTED_LOCALE="$requested" ;;
        *) fail installer.invalid_locale "locale=$requested"; return 1 ;;
    esac
    [ "$missing" = 0 ] || { fail installer.requires_value 'option=--locale'; return 1; }
}

resolve_target_paths() {
    case "$1" in
        claude) SKILL_BASE="${HOME}/.claude/skills"; AGENT_DIR="${HOME}/.claude/agents"; ALLOW_PIP=1; HOST_LABEL='Claude Code' ;;
        codex) SKILL_BASE="${HOME}/.codex/skills"; AGENT_DIR="${HOME}/.codex/agents"; ALLOW_PIP=1; HOST_LABEL='OpenAI Codex CLI' ;;
        cursor) SKILL_BASE="${HOME}/.cursor/extensions/claude-ads/skills"; AGENT_DIR="${HOME}/.cursor/extensions/claude-ads/agents"; ALLOW_PIP=0; HOST_LABEL='Cursor IDE' ;;
        windsurf) SKILL_BASE="${HOME}/.windsurf/skills"; AGENT_DIR="${HOME}/.windsurf/agents"; ALLOW_PIP=0; HOST_LABEL='Windsurf IDE' ;;
        gemini) SKILL_BASE="${HOME}/.gemini/extensions/claude-ads/skills"; AGENT_DIR="${HOME}/.gemini/extensions/claude-ads/agents"; ALLOW_PIP=0; HOST_LABEL='Gemini CLI' ;;
        goose) SKILL_BASE="${HOME}/.config/goose/skills"; AGENT_DIR="${HOME}/.config/goose/agents"; ALLOW_PIP=0; HOST_LABEL='Goose CLI' ;;
        *) return 1 ;;
    esac
}
validate_install_path() {
    [ -n "$1" ] || return 1
    case "$1" in -*|*[\;\&\|\$\(\)\<\>\`\\]*|*..*|//*|*$'\n'*|*$'\r'*|*$'\t'*) return 1 ;; esac
}
normalize_root() {
    local path="$1" suffix='' part current="$1"
    while :; do
        [ ! -L "$current" ] || { fail installer.symlink_directory "path=$current"; return 1; }
        part=$(dirname -- "$current")
        [ "$part" != "$current" ] || break
        current="$part"
    done
    while [ ! -d "$path" ]; do
        if [ -e "$path" ]; then fail installer.root_not_directory "path=$path"; return 1; fi
        part=$(basename -- "$path")
        suffix="/$part$suffix"
        path=$(dirname -- "$path")
    done
    path=$(CDPATH= cd -- "$path" && pwd -P)
    printf '%s\n' "${path%/}$suffix"
}
previously_owned_file() {
    local destination="$1" kind path
    [ -f "$MANIFEST_PATH" ] && [ ! -L "$MANIFEST_PATH" ] || return 1
    while IFS=$'\t' read -r kind path; do
        if [ "$kind" = F ] && [ "$path" = "$destination" ]; then return 0; fi
    done < "$MANIFEST_PATH"
    return 1
}
select_prior_locale() {
    local value size
    if [ -e "$LOCALE_PATH" ] || [ -L "$LOCALE_PATH" ]; then
        [ -f "$LOCALE_PATH" ] && [ ! -L "$LOCALE_PATH" ] && [ -O "$LOCALE_PATH" ] &&
            [ -f "$MANIFEST_PATH" ] && [ ! -L "$MANIFEST_PATH" ] && [ -O "$MANIFEST_PATH" ] &&
            previously_owned_file "$LOCALE_PATH" || { fail installer.locale_file_unsafe "path=$LOCALE_PATH"; return 1; }
        size=$(wc -c < "$LOCALE_PATH" | tr -d ' ')
        # Byte length plus exact read rejects extra lines, CR, NUL, and executable text.
        value=''
        IFS= read -r value < "$LOCALE_PATH" || { fail installer.locale_file_invalid "path=$LOCALE_PATH"; return 1; }
        case "$size:$value" in 3:en|6:zh-CN) ;; *) fail installer.locale_file_invalid "path=$LOCALE_PATH"; return 1 ;; esac
        [ "$LOCALE_EXPLICIT" = 1 ] || CLAUDE_ADS_SELECTED_LOCALE="$value"
    fi
}

main() {
    select_cli_locale "$@"
    local TARGET=claude SKILL_DIR_OVERRIDE='' AGENT_DIR_OVERRIDE='' SOURCE_MODE=auto REPO_DIR='' INSTALL_DEPS=1 HELP=0
    while [ $# -gt 0 ]; do
        case "$1" in
            --target=*|--skill-dir=*|--agent-dir=*|--source=*|--repo-dir=*|--locale=*)
                option="${1%%=*}"; value="${1#*=}" ;;
            --target|--skill-dir|--agent-dir|--source|--repo-dir|--locale)
                option="$1"; shift
                [ $# -gt 0 ] || { fail installer.requires_value "option=$option"; return 1; }
                value="$1" ;;
            --no-deps) INSTALL_DEPS=0; shift; continue ;;
            --help|-h) HELP=1; shift; continue ;;
            *) fail installer.unknown_argument "value=$1"; return 1 ;;
        esac
        case "$option" in
            --target) TARGET="$value" ;;
            --skill-dir) SKILL_DIR_OVERRIDE="$value" ;;
            --agent-dir) AGENT_DIR_OVERRIDE="$value" ;;
            --source) SOURCE_MODE="$value" ;;
            --repo-dir) REPO_DIR="$value" ;;
        esac
        shift
    done
    resolve_target_paths "$TARGET" || { fail installer.unknown_target "value=$TARGET"; return 1; }
    if [ -n "$SKILL_DIR_OVERRIDE" ]; then
        validate_install_path "$SKILL_DIR_OVERRIDE" || { fail installer.invalid_path_option 'option=--skill-dir'; return 1; }
        SKILL_BASE="$SKILL_DIR_OVERRIDE"
    fi
    if [ -n "$AGENT_DIR_OVERRIDE" ]; then
        validate_install_path "$AGENT_DIR_OVERRIDE" || { fail installer.invalid_path_option 'option=--agent-dir'; return 1; }
        AGENT_DIR="$AGENT_DIR_OVERRIDE"
    fi
    SKILL_BASE=$(normalize_root "$SKILL_BASE")
    AGENT_DIR=$(normalize_root "$AGENT_DIR")
    case "$SKILL_BASE/" in "$AGENT_DIR/"*) fail installer.roots_overlap "skills=$SKILL_BASE" "agents=$AGENT_DIR"; return 1 ;; esac
    case "$AGENT_DIR/" in "$SKILL_BASE/"*) fail installer.roots_overlap "skills=$SKILL_BASE" "agents=$AGENT_DIR"; return 1 ;; esac
    local SKILL_DIR="$SKILL_BASE/ads" MANIFEST_PATH="$SKILL_BASE/.claude-ads-$TARGET.manifest"
    local LOCALE_PATH="$SKILL_BASE/.claude-ads-$TARGET.locale"
    select_prior_locale
    if [ "$HELP" = 1 ]; then locale_message installer.help_install_sh; return 0; fi
    if [ -e "$MANIFEST_PATH.json" ] || [ -L "$MANIFEST_PATH.json" ]; then
        locale_message installer.powershell_manifest "path=$MANIFEST_PATH.json" >&2
        fail installer.continue_powershell; return 1
    fi
    [ ! -L "$MANIFEST_PATH" ] || { fail installer.invalid_manifest_path "path=$MANIFEST_PATH"; return 1; }
    local SCRIPT_DIR SOURCE_DIR='' REPO_URL='https://github.com/AgriciDaniel/claude-ads'
    SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
    [ -z "$REPO_DIR" ] || SOURCE_MODE=local
    case "$SOURCE_MODE" in
        auto) if [ -f "$SCRIPT_DIR/ads/SKILL.md" ] && [ -d "$SCRIPT_DIR/skills" ]; then SOURCE_MODE=local; else SOURCE_MODE=git; fi ;;
        local|git) ;;
        *) fail installer.invalid_source "value=$SOURCE_MODE"; return 1 ;;
    esac
    if [ "$SOURCE_MODE" = local ]; then
        SOURCE_DIR="${REPO_DIR:-$SCRIPT_DIR}"
        validate_install_path "$SOURCE_DIR" || { fail installer.invalid_repository_path; return 1; }
        SOURCE_DIR=$(CDPATH= cd -- "$SOURCE_DIR" 2>/dev/null && pwd -P) || { fail installer.repository_missing "path=${REPO_DIR:-$SCRIPT_DIR}"; return 1; }
        [ -f "$SOURCE_DIR/ads/SKILL.md" ] && [ -d "$SOURCE_DIR/skills" ] || { fail installer.invalid_distribution "path=$SOURCE_DIR"; return 1; }
    fi
    if [ "$ALLOW_PIP" = 1 ] && [ "$INSTALL_DEPS" = 1 ]; then
        command -v python3 >/dev/null 2>&1 || { fail installer.python_missing 'command=python3' 'option=--no-deps'; return 1; }
        PYTHON_TARGET=$(python3 -c 'import platform,sys
system=platform.system().lower(); machine=platform.machine().lower(); libc_name,libc_version=platform.libc_ver(); mac_version=platform.mac_ver()[0]
def pair(value):
    try: return tuple(int(part) for part in value.split(".")[:2])
    except ValueError: return (0,0)
boundary_ok=(system=="linux" and libc_name=="glibc" and pair(libc_version)>=(2,17)) or (system=="darwin" and pair(mac_version)>=(11,0))
print("|".join((sys.implementation.name, f"{sys.version_info.major}.{sys.version_info.minor}", system, machine, libc_name or "none", libc_version or mac_version or "none", "supported" if boundary_ok else "unsupported")))')
        case "$PYTHON_TARGET" in
            cpython\|3.11\|linux\|x86_64\|glibc\|*\|supported) DEPENDENCY_TARGET_ID=runtime-linux-cp311 ;;
            cpython\|3.12\|linux\|x86_64\|glibc\|*\|supported) DEPENDENCY_TARGET_ID=runtime-linux-cp312 ;;
            cpython\|3.11\|darwin\|x86_64\|*\|*\|supported) DEPENDENCY_TARGET_ID=runtime-macos-x86-cp311 ;;
            cpython\|3.12\|darwin\|x86_64\|*\|*\|supported) DEPENDENCY_TARGET_ID=runtime-macos-x86-cp312 ;;
            cpython\|3.11\|darwin\|arm64\|*\|*\|supported) DEPENDENCY_TARGET_ID=runtime-macos-arm-cp311 ;;
            cpython\|3.12\|darwin\|arm64\|*\|*\|supported) DEPENDENCY_TARGET_ID=runtime-macos-arm-cp312 ;;
            *\|windows\|*) fail installer.windows_python; return 1 ;;
            *\|linux\|*\|musl\|*\|unsupported) fail installer.musl_unsupported; return 1 ;;
            *) fail installer.unsupported_lock "target=$PYTHON_TARGET" 'option=--no-deps'; return 1 ;;
        esac
    fi
    locale_message installer.title
    locale_message installer.target "host=$HOST_LABEL"
    locale_message installer.selected_locale "locale=$CLAUDE_ADS_SELECTED_LOCALE"
    TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/claude-ads-install.XXXXXX")
    MANIFEST_TMP=''
    trap 'status=$?; rm -rf -- "${TEMP_DIR:-}"; [ -z "${MANIFEST_TMP:-}" ] || rm -f -- "$MANIFEST_TMP"; exit "$status"' EXIT
    if [ "$SOURCE_MODE" = git ]; then
        command -v git >/dev/null 2>&1 || { fail installer.git_required 'option=--source=git'; return 1; }
        locale_message installer.downloading
        git clone --depth 1 "$REPO_URL" "$TEMP_DIR/claude-ads" >/dev/null 2>&1 || { fail installer.git_failed; return 1; }
        SOURCE_DIR="$TEMP_DIR/claude-ads"
    fi
    locale_message installer.source "source=$SOURCE_MODE"

    # Complete source/destination plan. No configured-root mutation occurs until
    # every locale file and document passes the same preflight as core files.
    local PLAN_SOURCES=() PLAN_DESTINATIONS=() PLAN_DIRS=() SOURCE_COUNT=0
    assert_source() {
        local path="$1" current="$1"
        case "$path" in "$SOURCE_DIR"/*|"$TEMP_DIR"/*) ;; *) fail installer.source_escape "path=$path"; return 1 ;; esac
        while [ "$current" != "$SOURCE_DIR" ] && [ "$current" != "$TEMP_DIR" ]; do
            [ ! -L "$current" ] || { fail installer.source_symlink "path=$current"; return 1; }
            current=$(dirname -- "$current")
        done
        case "$path" in *$'\n'*|*$'\r'*|*$'\t'*) fail installer.source_not_file "path=$path"; return 1 ;; esac
    }
    add_directory() {
        local directory="$1" existing
        [ "$directory" != "$SKILL_BASE" ] && [ "$directory" != "$AGENT_DIR" ] || return 0
        case "$directory" in "$SKILL_BASE"/*|"$AGENT_DIR"/*) ;; *) fail installer.destination_escape "path=$directory"; return 1 ;; esac
        for existing in "${PLAN_DIRS[@]+"${PLAN_DIRS[@]}"}"; do [ "$existing" != "$directory" ] || return 0; done
        add_directory "$(dirname -- "$directory")"
        PLAN_DIRS[${#PLAN_DIRS[@]}]="$directory"
    }
    add_file() {
        local source="$1" destination="$2" relative existing
        assert_source "$source"
        if [ "$CLAUDE_ADS_SELECTED_LOCALE" = en ] && [[ "$source" == "$SOURCE_DIR/"*.md ]] && [[ "$source" != "$SOURCE_DIR/claude_ads_core/"* ]]; then
            relative="${source#"$SOURCE_DIR/"}"
            if [ -e "$SOURCE_DIR/claude_ads_core/locales/en/documents/$relative" ] || [ -L "$SOURCE_DIR/claude_ads_core/locales/en/documents/$relative" ]; then
                source="$SOURCE_DIR/claude_ads_core/locales/en/documents/$relative"
                assert_source "$source"
            fi
        fi
        [ -f "$source" ] || { fail installer.source_not_file "path=$source"; return 1; }
        for existing in "${PLAN_DESTINATIONS[@]+"${PLAN_DESTINATIONS[@]}"}"; do
            [ "$existing" != "$destination" ] || { fail installer.duplicate_planned_file "path=$destination"; return 1; }
        done
        add_directory "$(dirname -- "$destination")"
        PLAN_SOURCES[${#PLAN_SOURCES[@]}]="$source"
        PLAN_DESTINATIONS[${#PLAN_DESTINATIONS[@]}]="$destination"
    }
    walk_core() {
        local source="$1" destination="$2" depth="$3" all="$4" child name
        assert_source "$source"
        [ "$depth" -le 16 ] || { fail installer.source_too_deep "path=$source"; return 1; }
        for child in "$source"/* "$source"/.[!.]* "$source"/..?*; do
            [ -e "$child" ] || [ -L "$child" ] || continue
            assert_source "$child"
            name=$(basename -- "$child")
            [ "$name" != __pycache__ ] || continue
            SOURCE_COUNT=$((SOURCE_COUNT + 1))
            [ "$SOURCE_COUNT" -le 10000 ] || { fail installer.source_too_large "path=$source"; return 1; }
            if [ -d "$child" ]; then
                if [ "$name" = locales ]; then walk_core "$child" "$destination/$name" "$((depth + 1))" 1
                else walk_core "$child" "$destination/$name" "$((depth + 1))" "$all"; fi
            elif [ "$all" = 1 ] || [[ "$name" == *.py ]] || [[ "$name" == *.json ]]; then
                add_file "$child" "$destination/$name"
            fi
        done
    }
    add_file "$SOURCE_DIR/ads/SKILL.md" "$SKILL_DIR/SKILL.md"
    for source_file in "$SOURCE_DIR/ads/references/"*.md "$SOURCE_DIR/ads/agents/"*.yaml; do
        [ -e "$source_file" ] || [ -L "$source_file" ] || continue
        add_file "$source_file" "$SKILL_DIR/${source_file#"$SOURCE_DIR/ads/"}"
    done
    for skill_dir in "$SOURCE_DIR/skills"/*; do
        [ -d "$skill_dir" ] || [ -L "$skill_dir" ] || continue
        assert_source "$skill_dir"
        skill_name=$(basename -- "$skill_dir")
        add_file "$skill_dir/SKILL.md" "$SKILL_BASE/$skill_name/SKILL.md"
        for source_file in "$skill_dir/assets/"*.md; do
            [ -e "$source_file" ] || [ -L "$source_file" ] || continue
            add_file "$source_file" "$SKILL_BASE/$skill_name/assets/$(basename -- "$source_file")"
        done
    done
    for source_file in "$SOURCE_DIR/agents/"*.md; do
        [ -e "$source_file" ] || [ -L "$source_file" ] || continue
        add_file "$source_file" "$AGENT_DIR/$(basename -- "$source_file")"
    done
    local SCRIPTS_DIR="$SKILL_DIR/scripts"
    if [ -d "$SOURCE_DIR/scripts" ]; then
        for source_file in "$SOURCE_DIR/scripts/"*.py; do
            [ -e "$source_file" ] || [ -L "$source_file" ] || continue
            add_file "$source_file" "$SCRIPTS_DIR/$(basename -- "$source_file")"
        done
        add_file "$SOURCE_DIR/requirements.txt" "$SKILL_DIR/requirements.txt"
        add_file "$SOURCE_DIR/requirements.lock" "$SKILL_DIR/requirements.lock"
        walk_core "$SOURCE_DIR/claude_ads_core" "$SCRIPTS_DIR/claude_ads_core" 0 0
    fi
    printf '%s\n' "$CLAUDE_ADS_SELECTED_LOCALE" > "$TEMP_DIR/locale"
    add_file "$TEMP_DIR/locale" "$LOCALE_PATH"

    if [ ! -f "$MANIFEST_PATH" ]; then
        local LEGACY_PATHS='' destination
        for destination in "${PLAN_DESTINATIONS[@]+"${PLAN_DESTINATIONS[@]}"}"; do
            if { [ "$destination" = "$SKILL_DIR/SKILL.md" ] || [[ "$destination" == "$AGENT_DIR/"* ]]; } && [ -e "$destination" ]; then
                LEGACY_PATHS="$LEGACY_PATHS    $destination"$'\n'
            fi
        done
        if [ -n "$LEGACY_PATHS" ]; then
            {
                locale_message installer.legacy_detected
                printf '%s' "$LEGACY_PATHS"
                locale_message installer.legacy_explanation
                locale_message installer.legacy_removal "target=$TARGET"
                for destination in "${PLAN_DIRS[@]+"${PLAN_DIRS[@]}"}"; do printf '    %s/\n' "$destination"; done
                printf '    %s\n' "$MANIFEST_PATH"
            } >&2
            return 1
        fi
    fi
    assert_destination_chain() {
        local path="$1" current="$1"
        case "$path" in "$SKILL_BASE"|"$SKILL_BASE"/*|"$AGENT_DIR"|"$AGENT_DIR"/*) ;; *) fail installer.destination_escape "path=$path"; return 1 ;; esac
        while [ "$current" != "$SKILL_BASE" ] && [ "$current" != "$AGENT_DIR" ]; do
            if [ -L "$current" ]; then
                if [ "$current" = "$path" ] && [ ! -d "$current" ]; then fail installer.symlink_file "path=$current"
                else fail installer.symlink_directory "path=$current"; fi
                return 1
            fi
            current=$(dirname -- "$current")
        done
        [ ! -L "$current" ] || { fail installer.symlink_directory "path=$current"; return 1; }
    }
    for directory in "${PLAN_DIRS[@]+"${PLAN_DIRS[@]}"}"; do
        assert_destination_chain "$directory"
        [ ! -e "$directory" ] || [ -d "$directory" ] || { fail installer.destination_not_directory "path=$directory"; return 1; }
    done
    for destination in "${PLAN_DESTINATIONS[@]+"${PLAN_DESTINATIONS[@]}"}"; do
        assert_destination_chain "$destination"
        if [ -e "$destination" ] && { [ ! -f "$destination" ] || ! previously_owned_file "$destination"; }; then
            fail installer.unowned_file "path=$destination"; return 1
        fi
    done
    mkdir -p -- "$SKILL_BASE" "$AGENT_DIR"
    MANIFEST_TMP=$(mktemp "$SKILL_BASE/.claude-ads-manifest.XXXXXX")
    printf 'V\t1\nT\t%s\n' "$TARGET" > "$MANIFEST_TMP"
    # Preserve prior safe ownership entries, including an unchanged managed
    # environment on --no-deps; locale selection does not alter receipt schema.
    if [ -f "$MANIFEST_PATH" ]; then
        while IFS=$'\t' read -r kind path; do
            case "$kind" in
                F|D|R) case "$path" in "$SKILL_BASE"/*|"$AGENT_DIR"/*) printf '%s\t%s\n' "$kind" "$path" >> "$MANIFEST_TMP" ;; esac ;;
            esac
        done < "$MANIFEST_PATH"
    fi
    record_path() {
        local kind="$1" path="$2" previous_kind previous_path
        while IFS=$'\t' read -r previous_kind previous_path; do
            [ "$previous_kind" != "$kind" ] || [ "$previous_path" != "$path" ] || return 0
        done < "$MANIFEST_TMP"
        printf '%s\t%s\n' "$kind" "$path" >> "$MANIFEST_TMP"
    }
    for directory in "${PLAN_DIRS[@]+"${PLAN_DIRS[@]}"}"; do
        assert_destination_chain "$directory"
        if [ ! -d "$directory" ]; then mkdir -- "$directory"; record_path D "$directory"; fi
    done
    install_file() {
        local source="$1" destination="$2"
        assert_source "$source"
        assert_destination_chain "$destination"
        if [ -e "$destination" ] && ! previously_owned_file "$destination"; then fail installer.unowned_file "path=$destination"; return 1; fi
        cp -- "$source" "$destination" || { fail installer.copy_failed "path=$destination"; return 1; }
        # Always derive from the selected source, never the previously installed
        # document. Already generated language directives remain byte-identical.
        if [ "$CLAUDE_ADS_SELECTED_LOCALE" = en ] && [[ "$destination" == */SKILL.md ]] &&
            ! grep -Fq '<!-- claude-ads:operator-language -->' "$source"; then
            printf '\n' >> "$destination"
            locale_template installer.operator_language_rule
            printf '%s' "$LOCALE_TEMPLATE" >> "$destination"
        fi
        record_path F "$destination"
    }
    locale_message installer.install_guarded
    local index
    for ((index=0; index<${#PLAN_SOURCES[@]}; index++)); do
        install_file "${PLAN_SOURCES[$index]}" "${PLAN_DESTINATIONS[$index]}"
    done
    local VENV_DIR="$SKILL_DIR/.venv" RECEIPT_PATH="$SKILL_DIR/managed-runtime-receipt.json"
    if [ "$ALLOW_PIP" = 1 ] && [ "$INSTALL_DEPS" = 1 ]; then
        record_path R "$VENV_DIR"
        record_path F "$RECEIPT_PATH"
    fi
    mv -f -- "$MANIFEST_TMP" "$MANIFEST_PATH"
    MANIFEST_TMP=''
    locale_message installer.manifest_written "path=$MANIFEST_PATH"
    if [ "$ALLOW_PIP" = 1 ] && [ "$INSTALL_DEPS" = 1 ]; then
        rm -f -- "$RECEIPT_PATH" || { fail installer.receipt_invalidate_failed; return 1; }
        locale_message installer.install_dependencies
        if python3 -m venv "$VENV_DIR" \
            && "$VENV_DIR/bin/python" -m pip install -q --ignore-installed --report "$VENV_DIR/install-report.json" --require-hashes --only-binary=:all: -r "$SKILL_DIR/requirements.lock" \
            && SITE_PACKAGES=$("$VENV_DIR/bin/python" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])') \
            && printf '%s\n' "$SCRIPTS_DIR" > "$SITE_PACKAGES/claude-ads-core.pth" \
            && "$VENV_DIR/bin/python" -m pip check \
            && "$VENV_DIR/bin/python" "$SCRIPTS_DIR/write_install_receipt.py" --inventory "$SOURCE_DIR/control-plane/manifests/dependency-inventory.json" --lock "$SKILL_DIR/requirements.lock" --evidence "$SOURCE_DIR/control-plane/dependency-evidence/$DEPENDENCY_TARGET_ID.json" --pip-report "$VENV_DIR/install-report.json" --target-id "$DEPENDENCY_TARGET_ID" --output "$RECEIPT_PATH"; then
            locale_message installer.dependencies_installed "path=$VENV_DIR"
        else
            rm -rf -- "$VENV_DIR"
            rm -f -- "$RECEIPT_PATH"
            fail installer.dependencies_failed; return 1
        fi
    elif [ "$INSTALL_DEPS" = 0 ]; then locale_message installer.skip_dependencies 'option=--no-deps'
    else locale_message installer.host_skip_dependencies "host=$HOST_LABEL"; locale_message installer.python_lock_required; fi
    locale_message installer.image_provider_required
    locale_message installer.installed "host=$HOST_LABEL"
    locale_message installer.skills_path "path=$SKILL_BASE"
    locale_message installer.agents_path "path=$AGENT_DIR"
    locale_message installer.usage
    locale_message installer.start_host
    locale_message installer.run_commands
    locale_message installer.uninstall_command "command=bash uninstall.sh --target=$TARGET --skill-dir=$SKILL_BASE --agent-dir=$AGENT_DIR"
}

main "$@"
