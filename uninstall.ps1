#Requires -Version 5.1
# Use -Help for localized usage. Save this script as UTF-8 with BOM for Windows PowerShell 5.1.

param(
    [string]$Target = 'claude',
    [string]$SkillDir = '',
    [string]$AgentDir = '',
    [string]$Locale = '',
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# BEGIN GENERATED INSTALLER MESSAGES
# Generated from claude_ads_core/locales/{en,zh-CN}/installer.json. Do not edit.
function Get-LocaleTemplate([string]$Key) {
    switch -CaseSensitive ("${script:SelectedLocale}:$Key") {
        'en:installer.agent_count' { return '{count} agents' }
        'en:installer.agent_root_missing' { return 'Agent root not found: {path}' }
        'en:installer.agents_path' { return 'Agents: {path}' }
        'en:installer.authority_not_owned' { return 'Ownership authority is not owned by the current Windows identity: {path}' }
        'en:installer.bash_manifest' { return 'Bash ownership manifest detected: {path}. Continue with install.sh, or uninstall with uninstall.sh before switching installers.' }
        'en:installer.bundled' { return 'Bundled:' }
        'en:installer.cleanup_refused' { return 'Exact hashed dependency installation failed; unsafe managed environment cleanup was refused: {detail}' }
        'en:installer.continue_powershell' { return 'Continue with install.ps1, or uninstall with uninstall.ps1 before switching installers.' }
        'en:installer.copy_failed' { return 'Could not install resource: {path}' }
        'en:installer.dependencies_failed' { return 'Exact hashed dependency installation failed; no moving-range fallback was attempted.' }
        'en:installer.dependencies_installed' { return 'Exact locked Python dependencies installed in {path}' }
        'en:installer.destination_escape' { return 'Install destination escapes configured roots: {path}' }
        'en:installer.destination_not_directory' { return 'Install directory destination is not a directory: {path}' }
        'en:installer.directory_changed' { return 'Owned directory changed type before deletion: {path}' }
        'en:installer.directory_escape' { return 'Install directory escapes configured roots: {path}' }
        'en:installer.directory_is_file' { return 'Owned directory entry is not a directory: {path}' }
        'en:installer.downloading' { return 'Downloading Claude Ads with authenticated Git...' }
        'en:installer.duplicate_manifest_directory' { return 'Duplicate ownership-manifest directory: {path}' }
        'en:installer.duplicate_manifest_file' { return 'Duplicate ownership-manifest file: {path}' }
        'en:installer.duplicate_manifest_path' { return 'Duplicate ownership-manifest path: {path}' }
        'en:installer.duplicate_manifest_recursive' { return 'Duplicate recursive ownership-manifest directory: {path}' }
        'en:installer.duplicate_planned_file' { return 'Duplicate planned install file: {path}' }
        'en:installer.empty_manifest_path' { return 'Invalid empty ownership-manifest path' }
        'en:installer.file_changed' { return 'Owned file changed type before deletion: {path}' }
        'en:installer.file_is_directory' { return 'Owned file entry is a directory: {path}' }
        'en:installer.git_failed' { return 'Git clone failed' }
        'en:installer.git_required' { return 'Git is required for {option}.' }
        'en:installer.help_install_ps' { return 'Claude Ads Installer
Usage: .\install.ps1 [-Target <host>] [-SkillDir <path>] [-AgentDir <path>]
                     [-Source auto|local|git] [-RepoDir <path>] [-NoDeps]
                     [-Locale zh-CN|en] [-Help]
Targets: claude (default, verified); codex, cursor, windsurf, gemini, goose (experimental).
-RepoDir selects a local checkout; -NoDeps skips the managed Python environment.
Language: explicit -Locale > CLAUDE_ADS_LOCALE > prior install > zh-CN.
This changes operator language, not advertising or creative delivery language.
Prefer native installation or a locally inspected, checksum-verified release.
Never pipe remote content to PowerShell.' }
        'en:installer.help_install_sh' { return 'Claude Ads Installer

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
  --skill-dir=<path>   Override the target''s default skill install root
  --agent-dir=<path>   Override the target''s default agent install root
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
  verified SHA-256 checksum. Never pipe a remote installer directly to a shell.' }
        'en:installer.help_uninstall_ps' { return 'Usage: .\uninstall.ps1 [-Target <host>] [-SkillDir <path>] [-AgentDir <path>] [-Locale zh-CN|en] [-Help]
Language: explicit -Locale > CLAUDE_ADS_LOCALE > prior install > zh-CN.
Only ownership-manifest paths are removed; the owned locale preference is removed too.' }
        'en:installer.help_uninstall_sh' { return 'Usage: bash uninstall.sh [--target=<host>] [--skill-dir=<path>] [--agent-dir=<path>] [--locale=<zh-CN|en>]
Language: explicit flag > CLAUDE_ADS_LOCALE > prior install > zh-CN.
Only ownership-manifest paths are removed; the owned locale preference is removed too.' }
        'en:installer.home_unknown' { return 'Cannot determine the current user''s home directory.' }
        'en:installer.host_skip_dependencies' { return 'Skipping Python dependencies - {host} host runtime may not execute Python skills directly.' }
        'en:installer.image_provider_required' { return 'Image generation requires an explicitly configured eligible provider/model with capability evidence; Claude Ads does not probe or recommend a default.' }
        'en:installer.install_agents' { return 'Installing subagents...' }
        'en:installer.install_dependencies' { return 'Installing exact hashed Python dependencies into a managed virtual environment...' }
        'en:installer.install_guarded' { return 'Installing guarded skill, sub-skill, agent, and runtime files...' }
        'en:installer.install_parent_not_directory' { return 'Install path parent is not a directory: {path}' }
        'en:installer.install_scripts' { return 'Installing Python scripts and locale resources...' }
        'en:installer.install_skills' { return 'Installing skill files...' }
        'en:installer.install_subskills' { return 'Installing sub-skills...' }
        'en:installer.installed' { return 'Claude Ads installed successfully for {host}!' }
        'en:installer.installed_paths' { return 'Installed to:' }
        'en:installer.invalid_distribution' { return 'Local source is not a Claude Ads distribution: {path}' }
        'en:installer.invalid_locale' { return 'Unsupported locale: {locale}. Use zh-CN or en.' }
        'en:installer.invalid_manifest' { return 'Invalid ownership manifest: {path}' }
        'en:installer.invalid_manifest_entry' { return 'Invalid ownership-manifest entry in {property}: {path}' }
        'en:installer.invalid_manifest_path' { return 'Invalid ownership manifest path: {path}' }
        'en:installer.invalid_path_option' { return 'Invalid {option}: contains forbidden characters or traversal' }
        'en:installer.invalid_repository_path' { return 'Invalid local repository path' }
        'en:installer.invalid_source' { return 'Invalid source: {value}. Use auto, local, or git.' }
        'en:installer.io_failed' { return 'Filesystem operation failed; no further changes were attempted.' }
        'en:installer.legacy_detected' { return 'Existing Claude Ads files without an ownership manifest detected:' }
        'en:installer.legacy_explanation' { return 'Installs older than v2.0.0 wrote no ownership manifest, so this installer cannot verify what it may overwrite.' }
        'en:installer.legacy_manifest_missing' { return 'Installs older than v2.0.0 wrote no ownership manifest.' }
        'en:installer.legacy_removal' { return 'Remove the old install manually, then re-run. Paths this installer would own for target {target}:' }
        'en:installer.locale_file_invalid' { return 'Invalid locale preference data: {path}. Expected exactly en or zh-CN followed by one newline.' }
        'en:installer.locale_file_unsafe' { return 'Locale preference is not a safe, owned regular file: {path}' }
        'en:installer.main_count' { return '1 main skill (ads orchestrator)' }
        'en:installer.manifest_array' { return 'Ownership manifest property must be an array: {property}' }
        'en:installer.manifest_changed' { return 'Ownership manifest changed before deletion: {path}' }
        'en:installer.manifest_missing' { return 'Ownership manifest not found: {path}' }
        'en:installer.manifest_missing_unsafe' { return 'Ownership manifest not found or unsafe: {path}. Refusing namespace-based deletion.' }
        'en:installer.manifest_not_owned' { return 'Ownership manifest is not owned by the current principal: {path}' }
        'en:installer.manifest_owns_root' { return 'Ownership manifest cannot own a configured root: {path}' }
        'en:installer.manifest_written' { return 'Ownership manifest: {path}' }
        'en:installer.mismatched_manifest' { return 'Invalid or mismatched ownership manifest: {path}' }
        'en:installer.musl_unsupported' { return 'Managed dependencies require glibc >=2.17; musl Linux is unsupported. Re-run with --no-deps.' }
        'en:installer.noncanonical_manifest_path' { return 'Non-canonical ownership-manifest path: {path}' }
        'en:installer.operator_language_rule' { return '<!-- claude-ads:operator-language -->
## Operator language

Use English for operator-facing explanations, questions, summaries, help, and reports unless the operator explicitly requests another language. This preference must not change campaign targeting, advertising language, creative copy language, locale identifiers, machine-readable keys, or account data. Ask for the advertising delivery language separately when it is not specified.
' }
        'en:installer.powershell_manifest' { return 'PowerShell ownership manifest detected: {path}' }
        'en:installer.python_lock_required' { return 'Python helpers require the packaged exact-hash lock on a supported CPython wheel target.' }
        'en:installer.python_missing' { return '{command} not found. Re-run with {option} to install without Python helpers.' }
        'en:installer.receipt_invalidate_failed' { return 'Could not invalidate the prior managed runtime receipt.' }
        'en:installer.recursive_not_directory' { return 'Managed recursive path is not a directory: {path}' }
        'en:installer.recursive_reparse' { return 'Refusing reparse point inside managed recursive directory: {path}' }
        'en:installer.reference_count' { return '{count} reference files' }
        'en:installer.refuse_namespace' { return 'Refusing namespace-based deletion. Remove a legacy install manually after reviewing its files.' }
        'en:installer.reparse_install' { return 'Refusing reparse-point install path: {path}' }
        'en:installer.reparse_uninstall' { return 'Refusing reparse-point uninstall path: {path}' }
        'en:installer.repository_missing' { return 'Local repository does not exist: {path}' }
        'en:installer.requires_value' { return '{option} requires a value' }
        'en:installer.root_not_directory' { return 'Configured install root is not a directory: {path}' }
        'en:installer.roots_overlap' { return 'Skill and agent install roots must not overlap: {skills} ; {agents}' }
        'en:installer.run_commands' { return '2. Run commands: /ads audit; /ads plan saas; /ads google' }
        'en:installer.run_help' { return 'Run: {command}' }
        'en:installer.selected_locale' { return 'Operator language: {locale}. Advertising delivery language is unchanged.' }
        'en:installer.skill_root_missing' { return 'Skill root not found: {path}' }
        'en:installer.skills_path' { return 'Skills: {path}' }
        'en:installer.skip_dependencies' { return 'Skipping Python dependencies ({option}).' }
        'en:installer.source' { return 'Distribution source: {source}' }
        'en:installer.source_escape' { return 'Source path is outside its declared base: {path}' }
        'en:installer.source_not_file' { return 'Distribution resource is not a regular file: {path}' }
        'en:installer.source_symlink' { return 'Refusing symlink or reparse point in distribution resources: {path}' }
        'en:installer.source_too_deep' { return 'Distribution resource tree exceeds the maximum depth: {path}' }
        'en:installer.source_too_large' { return 'Distribution resource tree exceeds the file limit: {path}' }
        'en:installer.start_host' { return '1. Start your host CLI' }
        'en:installer.subskill_count' { return '{count} sub-skills (platform + lifecycle + functional + creative)' }
        'en:installer.symlink_directory' { return 'Refusing symlinked install directory: {path}' }
        'en:installer.symlink_file' { return 'Refusing symlinked install file: {path}' }
        'en:installer.target' { return 'Target: {host}' }
        'en:installer.template_count' { return '{count} industry templates' }
        'en:installer.title' { return 'Claude Ads Installer' }
        'en:installer.uninstall_command' { return 'To uninstall: {command}' }
        'en:installer.uninstall_parent_not_directory' { return 'Uninstall path parent is not a directory: {path}' }
        'en:installer.uninstall_recursive_not_directory' { return 'Recursive ownership entry is not a directory: {path}' }
        'en:installer.uninstall_recursive_reparse' { return 'Refusing reparse point inside recursive ownership directory: {path}' }
        'en:installer.uninstalled' { return 'Claude Ads uninstalled.' }
        'en:installer.uninstalling' { return 'Uninstalling Claude Ads from {skills} and {agents}...' }
        'en:installer.unknown_argument' { return 'Unknown argument: {value}' }
        'en:installer.unknown_manifest_record' { return 'Unknown ownership-manifest record: {kind}' }
        'en:installer.unknown_target' { return 'Unknown target: {value}' }
        'en:installer.unowned_environment' { return 'Refusing to reuse unowned managed environment: {path}' }
        'en:installer.unowned_file' { return 'Refusing to overwrite unowned file: {path}' }
        'en:installer.unsafe_manifest_path' { return 'Unsafe ownership-manifest path: {path}' }
        'en:installer.unsupported_lock' { return 'No verified dependency lock target for {target}. Re-run with {option}; moving-range fallback is disabled.' }
        'en:installer.usage' { return 'Usage:' }
        'en:installer.valid_targets' { return 'Valid targets: claude, codex, cursor, windsurf, gemini, goose' }
        'en:installer.windows_python' { return 'install.sh does not manage Windows Python dependencies. Use install.ps1 -Source local.' }
        'zh-CN:installer.agent_count' { return '{count} 个代理' }
        'zh-CN:installer.agent_root_missing' { return '未找到代理根目录：{path}' }
        'zh-CN:installer.agents_path' { return '代理：{path}' }
        'zh-CN:installer.authority_not_owned' { return '所有权凭据不属于当前 Windows 身份：{path}' }
        'zh-CN:installer.bash_manifest' { return '检测到 Bash 所有权清单：{path}。请继续使用 install.sh，或先运行 uninstall.sh 卸载，再切换安装器。' }
        'zh-CN:installer.bundled' { return '已包含：' }
        'zh-CN:installer.cleanup_refused' { return '精确哈希依赖安装失败；已拒绝不安全的托管环境清理：{detail}' }
        'zh-CN:installer.continue_powershell' { return '请继续使用 install.ps1，或先运行 uninstall.ps1 卸载，再切换安装器。' }
        'zh-CN:installer.copy_failed' { return '无法安装资源：{path}' }
        'zh-CN:installer.dependencies_failed' { return '精确哈希依赖安装失败；未尝试回退到浮动版本范围。' }
        'zh-CN:installer.dependencies_installed' { return '已在 {path} 安装精确锁定的 Python 依赖' }
        'zh-CN:installer.destination_escape' { return '安装目标超出配置的根目录：{path}' }
        'zh-CN:installer.destination_not_directory' { return '安装目录的目标不是目录：{path}' }
        'zh-CN:installer.directory_changed' { return '已拥有的目录在删除前改变了类型：{path}' }
        'zh-CN:installer.directory_escape' { return '安装目录超出配置的根目录：{path}' }
        'zh-CN:installer.directory_is_file' { return '已拥有的目录条目实际不是目录：{path}' }
        'zh-CN:installer.downloading' { return '正在通过已认证的 Git 下载 Claude Ads...' }
        'zh-CN:installer.duplicate_manifest_directory' { return '重复的所有权清单目录：{path}' }
        'zh-CN:installer.duplicate_manifest_file' { return '重复的所有权清单文件：{path}' }
        'zh-CN:installer.duplicate_manifest_path' { return '重复的所有权清单路径：{path}' }
        'zh-CN:installer.duplicate_manifest_recursive' { return '重复的递归所有权清单目录：{path}' }
        'zh-CN:installer.duplicate_planned_file' { return '重复的计划安装文件：{path}' }
        'zh-CN:installer.empty_manifest_path' { return '所有权清单路径为空，无效' }
        'zh-CN:installer.file_changed' { return '已拥有的文件在删除前改变了类型：{path}' }
        'zh-CN:installer.file_is_directory' { return '已拥有的文件条目实际是目录：{path}' }
        'zh-CN:installer.git_failed' { return 'Git 克隆失败' }
        'zh-CN:installer.git_required' { return '{option} 需要 Git。' }
        'zh-CN:installer.help_install_ps' { return 'Claude Ads 安装器
用法：.\install.ps1 [-Target <host>] [-SkillDir <path>] [-AgentDir <path>]
                     [-Source auto|local|git] [-RepoDir <path>] [-NoDeps]
                     [-Locale zh-CN|en] [-Help]
目标宿主：claude（默认，已验证）；codex、cursor、windsurf、gemini、goose（实验性）。
-RepoDir 选择本地源码；-NoDeps 跳过托管 Python 环境。
语言优先级：明确 -Locale 参数 > CLAUDE_ADS_LOCALE > 上次安装选择 > zh-CN。
此选项改变操作语言，不改变广告投放语言或创意文案语言。
优先使用原生安装，或已在本地审查并验证校验和的发行包。
绝不可通过管道将远程内容传给 PowerShell 执行。' }
        'zh-CN:installer.help_install_sh' { return 'Claude Ads 安装器

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
  绝不可通过管道将远程安装器直接传给 Shell 执行。' }
        'zh-CN:installer.help_uninstall_ps' { return '用法：.\uninstall.ps1 [-Target <host>] [-SkillDir <path>] [-AgentDir <path>] [-Locale zh-CN|en] [-Help]
语言优先级：明确 -Locale 参数 > CLAUDE_ADS_LOCALE > 上次安装选择 > zh-CN。
仅删除所有权清单记录的路径；已拥有的语言选择文件也会删除。' }
        'zh-CN:installer.help_uninstall_sh' { return '用法：bash uninstall.sh [--target=<host>] [--skill-dir=<path>] [--agent-dir=<path>] [--locale=<zh-CN|en>]
语言优先级：明确参数 > CLAUDE_ADS_LOCALE > 上次安装选择 > zh-CN。
仅删除所有权清单记录的路径；已拥有的语言选择文件也会删除。' }
        'zh-CN:installer.home_unknown' { return '无法确定当前用户的主目录。' }
        'zh-CN:installer.host_skip_dependencies' { return '已跳过 Python 依赖——{host} 宿主运行时可能无法直接执行 Python 技能。' }
        'zh-CN:installer.image_provider_required' { return '图像生成需要明确配置符合条件的服务商和模型，并提供能力证据；Claude Ads 不会探测或推荐默认选项。' }
        'zh-CN:installer.install_agents' { return '正在安装子代理...' }
        'zh-CN:installer.install_dependencies' { return '正在托管虚拟环境中安装经过精确哈希校验的 Python 依赖...' }
        'zh-CN:installer.install_guarded' { return '正在安装经过安全检查的技能、子技能、代理和运行时文件...' }
        'zh-CN:installer.install_parent_not_directory' { return '安装路径的父级不是目录：{path}' }
        'zh-CN:installer.install_scripts' { return '正在安装 Python 脚本和语言资源...' }
        'zh-CN:installer.install_skills' { return '正在安装主技能文件...' }
        'zh-CN:installer.install_subskills' { return '正在安装子技能...' }
        'zh-CN:installer.installed' { return '已成功为 {host} 安装 Claude Ads！' }
        'zh-CN:installer.installed_paths' { return '安装位置：' }
        'zh-CN:installer.invalid_distribution' { return '本地来源不是 Claude Ads 发行包：{path}' }
        'zh-CN:installer.invalid_locale' { return '不支持的语言：{locale}。请使用 zh-CN 或 en。' }
        'zh-CN:installer.invalid_manifest' { return '无效的所有权清单：{path}' }
        'zh-CN:installer.invalid_manifest_entry' { return '{property} 中的所有权清单条目无效：{path}' }
        'zh-CN:installer.invalid_manifest_path' { return '无效的所有权清单路径：{path}' }
        'zh-CN:installer.invalid_path_option' { return '无效的 {option}：包含禁止字符或路径穿越' }
        'zh-CN:installer.invalid_repository_path' { return '无效的本地源码路径' }
        'zh-CN:installer.invalid_source' { return '无效的安装来源：{value}。请使用 auto、local 或 git。' }
        'zh-CN:installer.io_failed' { return '文件系统操作失败；未继续进行更改。' }
        'zh-CN:installer.legacy_detected' { return '检测到没有所有权清单的现有 Claude Ads 文件：' }
        'zh-CN:installer.legacy_explanation' { return 'v2.0.0 之前的安装不会写入所有权清单，因此本安装器无法确认哪些文件可以覆盖。' }
        'zh-CN:installer.legacy_manifest_missing' { return 'v2.0.0 之前的安装不会写入所有权清单。' }
        'zh-CN:installer.legacy_removal' { return '请手动删除旧版安装，再重新运行。目标 {target} 下本安装器将拥有的路径：' }
        'zh-CN:installer.locale_file_invalid' { return '语言选择文件数据无效：{path}。必须仅包含 en 或 zh-CN，并以一个换行符结尾。' }
        'zh-CN:installer.locale_file_unsafe' { return '语言选择文件不是安全且已拥有的普通文件：{path}' }
        'zh-CN:installer.main_count' { return '1 个主技能（ads 编排器）' }
        'zh-CN:installer.manifest_array' { return '所有权清单属性必须是数组：{property}' }
        'zh-CN:installer.manifest_changed' { return '所有权清单在删除前发生了变化：{path}' }
        'zh-CN:installer.manifest_missing' { return '未找到所有权清单：{path}' }
        'zh-CN:installer.manifest_missing_unsafe' { return '未找到所有权清单或其不安全：{path}。拒绝按命名空间删除。' }
        'zh-CN:installer.manifest_not_owned' { return '所有权清单不属于当前用户主体：{path}' }
        'zh-CN:installer.manifest_owns_root' { return '所有权清单不能拥有配置的根目录：{path}' }
        'zh-CN:installer.manifest_written' { return '所有权清单：{path}' }
        'zh-CN:installer.mismatched_manifest' { return '所有权清单无效或不匹配：{path}' }
        'zh-CN:installer.musl_unsupported' { return '托管依赖要求 glibc >=2.17；不支持 musl Linux。请加上 --no-deps 重新运行。' }
        'zh-CN:installer.noncanonical_manifest_path' { return '所有权清单路径不规范：{path}' }
        'zh-CN:installer.operator_language_rule' { return '<!-- claude-ads:operator-language -->
## 操作语言

除非操作者明确要求其他语言，否则面向操作者的解释、问题、摘要、帮助和报告均使用简体中文。此偏好不得改变广告定向、广告投放语言、创意文案语言、语言标识符、机器可读键名或账户数据。未指定广告投放语言时，应单独询问。
' }
        'zh-CN:installer.powershell_manifest' { return '检测到 PowerShell 所有权清单：{path}' }
        'zh-CN:installer.python_lock_required' { return 'Python 辅助工具要求受支持的 CPython wheel 目标及发行包内的精确哈希锁定文件。' }
        'zh-CN:installer.python_missing' { return '未找到 {command}。请加上 {option} 重新运行，以跳过 Python 辅助工具的依赖安装。' }
        'zh-CN:installer.receipt_invalidate_failed' { return '无法使之前的托管运行时凭据失效。' }
        'zh-CN:installer.recursive_not_directory' { return '托管递归路径不是目录：{path}' }
        'zh-CN:installer.recursive_reparse' { return '拒绝托管递归目录内的重解析点：{path}' }
        'zh-CN:installer.reference_count' { return '{count} 个参考文件' }
        'zh-CN:installer.refuse_namespace' { return '拒绝按命名空间删除。请先审查旧版安装的文件，再手动删除。' }
        'zh-CN:installer.reparse_install' { return '拒绝使用重解析点安装路径：{path}' }
        'zh-CN:installer.reparse_uninstall' { return '拒绝使用重解析点卸载路径：{path}' }
        'zh-CN:installer.repository_missing' { return '本地源码目录不存在：{path}' }
        'zh-CN:installer.requires_value' { return '{option} 必须指定值' }
        'zh-CN:installer.root_not_directory' { return '配置的安装根路径不是目录：{path}' }
        'zh-CN:installer.roots_overlap' { return '技能和代理的安装根目录不能重叠：{skills}；{agents}' }
        'zh-CN:installer.run_commands' { return '2. 运行命令：/ads audit；/ads plan saas；/ads google' }
        'zh-CN:installer.run_help' { return '运行：{command}' }
        'zh-CN:installer.selected_locale' { return '操作语言：{locale}。广告投放语言保持不变。' }
        'zh-CN:installer.skill_root_missing' { return '未找到技能根目录：{path}' }
        'zh-CN:installer.skills_path' { return '技能：{path}' }
        'zh-CN:installer.skip_dependencies' { return '已跳过 Python 依赖（{option}）。' }
        'zh-CN:installer.source' { return '发行包来源：{source}' }
        'zh-CN:installer.source_escape' { return '来源路径超出其声明的根目录：{path}' }
        'zh-CN:installer.source_not_file' { return '发行包资源不是普通文件：{path}' }
        'zh-CN:installer.source_symlink' { return '拒绝发行包资源中的符号链接或重解析点：{path}' }
        'zh-CN:installer.source_too_deep' { return '发行包资源树超过最大深度：{path}' }
        'zh-CN:installer.source_too_large' { return '发行包资源树超过文件数量限制：{path}' }
        'zh-CN:installer.start_host' { return '1. 启动宿主 CLI' }
        'zh-CN:installer.subskill_count' { return '{count} 个子技能（平台、生命周期、功能与创意）' }
        'zh-CN:installer.symlink_directory' { return '拒绝使用符号链接安装目录：{path}' }
        'zh-CN:installer.symlink_file' { return '拒绝使用符号链接安装文件：{path}' }
        'zh-CN:installer.target' { return '目标宿主：{host}' }
        'zh-CN:installer.template_count' { return '{count} 个行业模板' }
        'zh-CN:installer.title' { return 'Claude Ads 安装器' }
        'zh-CN:installer.uninstall_command' { return '卸载命令：{command}' }
        'zh-CN:installer.uninstall_parent_not_directory' { return '卸载路径的父级不是目录：{path}' }
        'zh-CN:installer.uninstall_recursive_not_directory' { return '递归所有权条目不是目录：{path}' }
        'zh-CN:installer.uninstall_recursive_reparse' { return '拒绝递归所有权目录内的重解析点：{path}' }
        'zh-CN:installer.uninstalled' { return 'Claude Ads 已卸载。' }
        'zh-CN:installer.uninstalling' { return '正在从 {skills} 和 {agents} 卸载 Claude Ads...' }
        'zh-CN:installer.unknown_argument' { return '未知参数：{value}' }
        'zh-CN:installer.unknown_manifest_record' { return '未知的所有权清单记录：{kind}' }
        'zh-CN:installer.unknown_target' { return '未知目标宿主：{value}' }
        'zh-CN:installer.unowned_environment' { return '拒绝复用无所有权的托管环境：{path}' }
        'zh-CN:installer.unowned_file' { return '拒绝覆盖无所有权的文件：{path}' }
        'zh-CN:installer.unsafe_manifest_path' { return '不安全的所有权清单路径：{path}' }
        'zh-CN:installer.unsupported_lock' { return '{target} 没有已验证的依赖锁定目标。请加上 {option} 重新运行；禁止回退到浮动版本范围。' }
        'zh-CN:installer.usage' { return '用法：' }
        'zh-CN:installer.valid_targets' { return '有效目标宿主：claude、codex、cursor、windsurf、gemini、goose' }
        'zh-CN:installer.windows_python' { return 'install.sh 不管理 Windows Python 依赖。请使用 install.ps1 -Source local。' }
        default { throw ('installer.unknown_key: ' + $Key) }
    }
}
# END GENERATED INSTALLER MESSAGES

# UTF-8 BOM preserves Chinese literals in Windows PowerShell 5.1. Explicit
# encodings also avoid the host's ANSI defaults when reading localized docs.
$script:SelectedLocale = 'zh-CN'
$script:LocaleExplicit = $false
$script:Utf8 = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $script:Utf8
$OutputEncoding = $script:Utf8

function Format-LocaleMessage([string]$Key, [hashtable]$Values = @{}) {
    $Text = Get-LocaleTemplate $Key
    $Builder = New-Object System.Text.StringBuilder
    $Offset = 0
    foreach ($Match in [regex]::Matches($Text, '\{([a-z_]+)\}')) {
        [void]$Builder.Append($Text.Substring($Offset, $Match.Index - $Offset))
        $Name = $Match.Groups[1].Value
        if (-not $Values.ContainsKey($Name)) { throw ('installer.missing_placeholder: ' + $Name) }
        [void]$Builder.Append([string]$Values[$Name])
        $Offset = $Match.Index + $Match.Length
    }
    [void]$Builder.Append($Text.Substring($Offset))
    return $Builder.ToString()
}
function Select-InitialLocale {
    $Requested = 'zh-CN'
    if (-not [string]::IsNullOrEmpty($env:CLAUDE_ADS_LOCALE)) {
        $Requested = $env:CLAUDE_ADS_LOCALE
        $script:LocaleExplicit = $true
    }
    if ($script:HasLocaleParameter) {
        $Requested = $Locale
        $script:LocaleExplicit = $true
    }
    if ($Requested -cnotin @('en', 'zh-CN')) {
        throw (Format-LocaleMessage 'installer.invalid_locale' @{ locale = $Requested })
    }
    $script:SelectedLocale = $Requested
}
function Read-PriorLocale([string]$LocalePath, [string]$ManifestPath) {
    $Item = Get-Item -LiteralPath $LocalePath -Force -ErrorAction SilentlyContinue
    if ($null -eq $Item) { return }
    # Validate every existing ancestor without following a reparse point. The
    # language file is data, and never confers ownership or mutation authority.
    $Current = [IO.Path]::GetFullPath($LocalePath)
    while ($Current) {
        $Ancestor = Get-Item -LiteralPath $Current -Force -ErrorAction SilentlyContinue
        if ($null -ne $Ancestor -and (($Ancestor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw (Format-LocaleMessage 'installer.locale_file_unsafe' @{ path = $LocalePath })
        }
        $Parent = [IO.Path]::GetDirectoryName($Current)
        if ($Parent -eq $Current) { break }
        $Current = $Parent
    }
    if ($Item.PSIsContainer -or $Item.Length -notin @(3,6)) {
        throw (Format-LocaleMessage 'installer.locale_file_invalid' @{ path = $LocalePath })
    }
    $ManifestItem = Get-Item -LiteralPath $ManifestPath -Force -ErrorAction SilentlyContinue
    if ($null -eq $ManifestItem -or $ManifestItem.PSIsContainer -or
        (($ManifestItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw (Format-LocaleMessage 'installer.locale_file_unsafe' @{ path = $LocalePath })
    }
    # Windows owner check is shared with the existing manifest contract. It is
    # available in Main's dynamic scope before this function is called.
    Assert-CurrentUserOwnedFile $ManifestPath
    Assert-CurrentUserOwnedFile $LocalePath
    try { $Prior = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json } catch {
        throw (Format-LocaleMessage 'installer.locale_file_unsafe' @{ path = $LocalePath })
    }
    if (-not ($Prior.files -is [System.Array]) -or $LocalePath -cnotin $Prior.files) {
        throw (Format-LocaleMessage 'installer.locale_file_unsafe' @{ path = $LocalePath })
    }
    $Value = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($LocalePath))
    if ($Value -cnotin @("en`n", "zh-CN`n")) {
        throw (Format-LocaleMessage 'installer.locale_file_invalid' @{ path = $LocalePath })
    }
    if (-not $script:LocaleExplicit) { $script:SelectedLocale = $Value.TrimEnd([char]10) }
}
$script:HasLocaleParameter = $PSBoundParameters.ContainsKey('Locale')
$script:ExtraArguments = @($args)
Select-InitialLocale


function Get-ClaudeAdsUserHome {
    if (-not [string]::IsNullOrWhiteSpace($env:USERPROFILE)) { return $env:USERPROFILE }
    if (-not [string]::IsNullOrWhiteSpace($HOME)) { return $HOME }
    $ProfileHome = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
    if (-not [string]::IsNullOrWhiteSpace($ProfileHome)) { return $ProfileHome }
    throw (Format-LocaleMessage 'installer.home_unknown')
}

function Resolve-TargetPaths {
    param([string]$T)
    $UserHome = Get-ClaudeAdsUserHome
    switch ($T) {
        'claude'   { return @{ SkillBase = Join-Path $UserHome ".claude\skills";                                AgentDir = Join-Path $UserHome ".claude\agents" } }
        'codex'    { return @{ SkillBase = Join-Path $UserHome ".codex\skills";                                 AgentDir = Join-Path $UserHome ".codex\agents" } }
        'cursor'   { return @{ SkillBase = Join-Path $UserHome ".cursor\extensions\claude-ads\skills";          AgentDir = Join-Path $UserHome ".cursor\extensions\claude-ads\agents" } }
        'windsurf' { return @{ SkillBase = Join-Path $UserHome ".windsurf\skills";                              AgentDir = Join-Path $UserHome ".windsurf\agents" } }
        'gemini'   { return @{ SkillBase = Join-Path $UserHome ".gemini\extensions\claude-ads\skills";          AgentDir = Join-Path $UserHome ".gemini\extensions\claude-ads\agents" } }
        'goose'    { return @{ SkillBase = Join-Path $UserHome ".config\goose\skills";                          AgentDir = Join-Path $UserHome ".config\goose\agents" } }
        default    { throw (Format-LocaleMessage 'installer.unknown_target' @{ value = $T }) }
    }
}

function Get-NormalizedInstallRoot([string]$Path) {
    $FullPath = [IO.Path]::GetFullPath($Path)
    $PathRoot = [IO.Path]::GetPathRoot($FullPath)
    $Comparison = if ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) {
        [StringComparison]::OrdinalIgnoreCase
    } else {
        [StringComparison]::Ordinal
    }
    if ($FullPath.Equals($PathRoot, $Comparison)) { return $FullPath }
    $Separators = [char[]]@([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    return $FullPath.TrimEnd($Separators)
}

function Main {
    $paths = Resolve-TargetPaths -T $Target
    $Separators = [char[]]@([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $Boundary = [string][IO.Path]::DirectorySeparatorChar
    $PathComparison = if ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) {
        [StringComparison]::OrdinalIgnoreCase
    } else {
        [StringComparison]::Ordinal
    }
    $StringComparer = if ($PathComparison -eq [StringComparison]::OrdinalIgnoreCase) {
        [StringComparer]::OrdinalIgnoreCase
    } else {
        [StringComparer]::Ordinal
    }
    $SkillBase = if ($SkillDir) { $SkillDir } else { $paths.SkillBase }
    $AgentDirResolved = if ($AgentDir) { $AgentDir } else { $paths.AgentDir }
    $SkillBase = Get-NormalizedInstallRoot $SkillBase
    $AgentDirResolved = Get-NormalizedInstallRoot $AgentDirResolved

    function Get-RootPrefix([string]$Root) {
        if ($Root.EndsWith($Boundary, $PathComparison)) { return $Root }
        return $Root + $Boundary
    }

    $SkillRootPrefix = Get-RootPrefix $SkillBase
    $AgentRootPrefix = Get-RootPrefix $AgentDirResolved
    if ($SkillBase.Equals($AgentDirResolved, $PathComparison) -or
        $SkillBase.StartsWith($AgentRootPrefix, $PathComparison) -or
        $AgentDirResolved.StartsWith($SkillRootPrefix, $PathComparison)) {
        throw (Format-LocaleMessage 'installer.roots_overlap' @{ skills = $SkillBase; agents = $AgentDirResolved })
    }
    $ManifestPath = [IO.Path]::GetFullPath((Join-Path $SkillBase ".claude-ads-$Target.manifest.json"))

    function Get-ContainingRoot([string]$Path) {
        $FullPath = [IO.Path]::GetFullPath($Path)
        if ($FullPath.StartsWith($SkillRootPrefix, $PathComparison)) { return $SkillBase }
        if ($FullPath.StartsWith($AgentRootPrefix, $PathComparison)) { return $AgentDirResolved }
        throw (Format-LocaleMessage 'installer.unsafe_manifest_path' @{ path = $Path })
    }

    function Assert-CanonicalOwnedPath([string]$Path) {
        if ([string]::IsNullOrWhiteSpace($Path)) { throw (Format-LocaleMessage 'installer.empty_manifest_path') }
        $FullPath = [IO.Path]::GetFullPath($Path)
        if (-not $Path.Equals($FullPath, $PathComparison)) {
            throw (Format-LocaleMessage 'installer.noncanonical_manifest_path' @{ path = $Path })
        }
        try { $null = Get-ContainingRoot $FullPath } catch {
            throw (Format-LocaleMessage 'installer.unsafe_manifest_path' @{ path = $Path })
        }
        return $FullPath
    }

    function Assert-NoReparseChain([string]$Path, [string]$StopAt = '') {
        $FullPath = [IO.Path]::GetFullPath($Path)
        $StopPath = if ($StopAt) { [IO.Path]::GetFullPath($StopAt) } else { '' }
        $Current = $FullPath
        while ($true) {
            $Item = Get-Item -LiteralPath $Current -Force -ErrorAction SilentlyContinue
            if ($null -ne $Item) {
                if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                    throw (Format-LocaleMessage 'installer.reparse_uninstall' @{ path = $Current })
                }
                if (-not $Current.Equals($FullPath, $PathComparison) -and -not $Item.PSIsContainer) {
                    throw (Format-LocaleMessage 'installer.uninstall_parent_not_directory' @{ path = $Current })
                }
            }
            if ($StopPath -and $Current.Equals($StopPath, $PathComparison)) { break }
            $Parent = [IO.Path]::GetDirectoryName($Current)
            if ([string]::IsNullOrEmpty($Parent) -or $Parent.Equals($Current, $PathComparison)) { break }
            $Current = $Parent
        }
        return $FullPath
    }

    function Assert-SafeRecursiveTree([string]$Path) {
        $Root = Get-ContainingRoot $Path
        [void](Assert-NoReparseChain $Path $Root)
        $Item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
        if ($null -eq $Item) { return }
        if (-not $Item.PSIsContainer) { throw (Format-LocaleMessage 'installer.uninstall_recursive_not_directory' @{ path = $Path }) }
        $Pending = [System.Collections.Generic.Stack[string]]::new()
        $Pending.Push([IO.Path]::GetFullPath($Path))
        while ($Pending.Count -gt 0) {
            $Directory = $Pending.Pop()
            [void](Assert-NoReparseChain $Directory $Root)
            foreach ($Child in @(Get-ChildItem -LiteralPath $Directory -Force)) {
                if (($Child.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                    throw (Format-LocaleMessage 'installer.uninstall_recursive_reparse' @{ path = $Child.FullName })
                }
                if ($Child.PSIsContainer) { $Pending.Push($Child.FullName) }
            }
        }
    }

    function Assert-CurrentUserOwnedFile([string]$Path) {
        if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { return }
        $Identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
        $Sections = [System.Security.AccessControl.AccessControlSections]::Owner
        if ($PSVersionTable.PSEdition -eq 'Core') {
            $FileInfo = [System.IO.FileInfo]::new($Path)
            $FileSecurity = [System.IO.FileSystemAclExtensions]::GetAccessControl($FileInfo, $Sections)
        } else {
            $FileSecurity = [System.IO.File]::GetAccessControl($Path, $Sections)
        }
        $OwnerSid = $FileSecurity.GetOwner([System.Security.Principal.SecurityIdentifier])
        $CallerSids = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        if ($null -ne $Identity.User) { [void]$CallerSids.Add($Identity.User.Value) }
        foreach ($Group in @($Identity.Groups)) { [void]$CallerSids.Add($Group.Value) }
        if ($null -eq $OwnerSid -or -not $CallerSids.Contains($OwnerSid.Value)) {
            throw (Format-LocaleMessage 'installer.manifest_not_owned' @{ path = $Path })
        }
    }

    $LocalePath = [IO.Path]::GetFullPath((Join-Path $SkillBase ".claude-ads-$Target.locale"))
    Read-PriorLocale $LocalePath $ManifestPath
    if ($script:ExtraArguments.Count -gt 0) { throw (Format-LocaleMessage 'installer.unknown_argument' @{ value = $script:ExtraArguments[0] }) }
    if ($Help) { Write-Host (Format-LocaleMessage 'installer.help_uninstall_ps'); return }

    [void](Assert-NoReparseChain $SkillBase)
    [void](Assert-NoReparseChain $AgentDirResolved)
    [void](Assert-NoReparseChain $ManifestPath $SkillBase)
    $ManifestItem = Get-Item -LiteralPath $ManifestPath -Force -ErrorAction SilentlyContinue
    if ($null -eq $ManifestItem -or $ManifestItem.PSIsContainer -or
        (($ManifestItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw (Format-LocaleMessage 'installer.manifest_missing_unsafe' @{ path = $ManifestPath })
    }
    Assert-CurrentUserOwnedFile $ManifestPath
    try { $Manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json } catch {
        throw (Format-LocaleMessage 'installer.invalid_manifest' @{ path = $ManifestPath })
    }
    $ExpectedProperties = @('version','target','files','directories','recursive_directories')
    $ActualProperties = @($Manifest.PSObject.Properties.Name)
    $VersionType = if ($null -eq $Manifest.version) { $null } else { $Manifest.version.GetType() }
    if (@(Compare-Object $ExpectedProperties $ActualProperties).Count -ne 0 -or
        $VersionType -notin @([int], [long]) -or $Manifest.version -ne 1 -or
        -not ($Manifest.target -is [string]) -or $Manifest.target -cne $Target) {
        throw (Format-LocaleMessage 'installer.mismatched_manifest' @{ path = $ManifestPath })
    }

    $AllPaths = [System.Collections.Generic.HashSet[string]]::new($StringComparer)
    $Validated = @{}
    foreach ($PropertyName in @('files','directories','recursive_directories')) {
        if (-not ($Manifest.$PropertyName -is [System.Array])) {
            throw (Format-LocaleMessage 'installer.manifest_array' @{ property = $PropertyName })
        }
        $Paths = [System.Collections.Generic.List[string]]::new()
        foreach ($OwnedPath in @($Manifest.$PropertyName)) {
            if (-not ($OwnedPath -is [string])) {
                throw (Format-LocaleMessage 'installer.invalid_manifest_entry' @{ property = $PropertyName; path = $ManifestPath })
            }
            $FullPath = Assert-CanonicalOwnedPath $OwnedPath
            if (-not $AllPaths.Add($FullPath)) { throw (Format-LocaleMessage 'installer.duplicate_manifest_path' @{ path = $FullPath }) }
            [void](Assert-NoReparseChain $FullPath (Get-ContainingRoot $FullPath))
            $Item = Get-Item -LiteralPath $FullPath -Force -ErrorAction SilentlyContinue
            if ($null -ne $Item) {
                if ($PropertyName -eq 'files' -and $Item.PSIsContainer) {
                    throw (Format-LocaleMessage 'installer.file_is_directory' @{ path = $FullPath })
                }
                if ($PropertyName -ne 'files' -and -not $Item.PSIsContainer) {
                    throw (Format-LocaleMessage 'installer.directory_is_file' @{ path = $FullPath })
                }
            }
            [void]$Paths.Add($FullPath)
        }
        $Validated[$PropertyName] = $Paths
    }
    foreach ($RecursivePath in $Validated.recursive_directories) { Assert-SafeRecursiveTree $RecursivePath }

    Write-Host (Format-LocaleMessage 'installer.uninstalling' @{ skills = $SkillBase; agents = $AgentDirResolved })

    foreach ($FullPath in $Validated.files) {
        [void](Assert-NoReparseChain $FullPath (Get-ContainingRoot $FullPath))
        $Item = Get-Item -LiteralPath $FullPath -Force -ErrorAction SilentlyContinue
        if ($null -ne $Item) {
            if ($Item.PSIsContainer -or (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
                throw (Format-LocaleMessage 'installer.file_changed' @{ path = $FullPath })
            }
            Remove-Item -LiteralPath $FullPath -Force
        }
    }

    foreach ($FullPath in $Validated.recursive_directories) {
        Assert-SafeRecursiveTree $FullPath
        $Item = Get-Item -LiteralPath $FullPath -Force -ErrorAction SilentlyContinue
        if ($null -ne $Item) { Remove-Item -LiteralPath $FullPath -Recurse -Force }
    }

    foreach ($FullPath in @($Validated.directories | Sort-Object Length -Descending)) {
        [void](Assert-NoReparseChain $FullPath (Get-ContainingRoot $FullPath))
        $Item = Get-Item -LiteralPath $FullPath -Force -ErrorAction SilentlyContinue
        if ($null -ne $Item) {
            if (-not $Item.PSIsContainer -or (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
                throw (Format-LocaleMessage 'installer.directory_changed' @{ path = $FullPath })
            }
            $Children = @(Get-ChildItem -LiteralPath $FullPath -Force -ErrorAction SilentlyContinue)
            if ($Children.Count -eq 0) {
                Remove-Item -LiteralPath $FullPath -Force -Confirm:$false
            }
        }
    }

    [void](Assert-NoReparseChain $ManifestPath $SkillBase)
    $ManifestItem = Get-Item -LiteralPath $ManifestPath -Force -ErrorAction SilentlyContinue
    if ($null -eq $ManifestItem -or $ManifestItem.PSIsContainer -or
        (($ManifestItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw (Format-LocaleMessage 'installer.manifest_changed' @{ path = $ManifestPath })
    }
    Remove-Item -LiteralPath $ManifestPath -Force

    Write-Host (Format-LocaleMessage 'installer.uninstalled') -ForegroundColor Green
}

Main
