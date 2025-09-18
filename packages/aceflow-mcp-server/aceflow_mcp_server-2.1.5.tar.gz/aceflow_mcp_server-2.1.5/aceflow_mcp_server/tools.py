"""AceFlow MCP Tools implementation."""

from typing import Dict, Any, Optional, List
import json
import os
import sys
from pathlib import Path
import shutil
import datetime

# Import core functionality
from .core import ProjectManager, WorkflowEngine, TemplateManager

# Import existing AceFlow functionality
current_dir = Path(__file__).parent
aceflow_scripts_dir = current_dir.parent.parent / "aceflow" / "scripts"
sys.path.insert(0, str(aceflow_scripts_dir))

try:
    from utils.platform_compatibility import PlatformUtils, SafeFileOperations, EnhancedErrorHandler
except ImportError:
    # Fallback implementations if utils are not available
    class PlatformUtils:
        @staticmethod
        def get_os_type(): return "unknown"
    
    class SafeFileOperations:
        @staticmethod
        def write_text_file(path, content, encoding="utf-8"):
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
    
    class EnhancedErrorHandler:
        @staticmethod
        def handle_file_error(error, context=""): return str(error)


class AceFlowTools:
    """AceFlow MCP Tools collection."""
    
    def __init__(self, working_directory: Optional[str] = None):
        """Initialize tools with necessary dependencies."""
        self.platform_utils = PlatformUtils()
        self.file_ops = SafeFileOperations()
        self.error_handler = EnhancedErrorHandler()
        self.project_manager = ProjectManager()
        self.workflow_engine = WorkflowEngine()
        self.template_manager = TemplateManager()
        
        # Store initial working directory for fallback, but don't use it as fixed
        self.fallback_working_directory = working_directory
        
        # Debug logging
        print(f"[DEBUG] AceFlowTools initialized with fallback_directory: {self.fallback_working_directory}", file=sys.stderr)
    
    def _get_dynamic_working_directory(self, provided_directory: Optional[str] = None) -> str:
        """Dynamically detect the current working directory for IDE integration.
        
        This method is called on each tool invocation to get the current working directory,
        supporting IDE environment variables and cross-platform compatibility.
        Windows IDEs often launch MCP servers from their installation directories,
        so we prioritize environment variables over os.getcwd().
        
        Args:
            provided_directory: Optional directory provided by user
            
        Returns:
            Current working directory path
            
        Raises:
            ValueError: If directory cannot be determined
        """
        if provided_directory:
            if provided_directory in [".", "./"]:
                # Handle relative current directory references
                # On Windows, this might still be IDE installation path
                current_cwd = os.getcwd()
                if not self._is_ide_installation_path(current_cwd):
                    print(f"[DEBUG] Resolved '.' to: {current_cwd}", file=sys.stderr)
                    return current_cwd
                else:
                    print(f"[DEBUG] '.' resolved to IDE path {current_cwd}, trying alternatives", file=sys.stderr)
                    # Fall through to environment variable detection
            else:
                return os.path.abspath(provided_directory)
        
        # Priority order for dynamic working directory detection
        candidates = []
        
        # 1. IDE-specific environment variables (HIGHEST priority for Windows)
        ide_env_vars = [
            # VS Code working directory variables
            'VSCODE_CWD',           # VS Code current working directory
            'VSCODE_FILE_CWD',      # VS Code file directory  
            'VSCODE_WORKSPACE',     # VS Code workspace
            
            # Cursor (VS Code fork)
            'CURSOR_CWD',           # Cursor current working directory
            'CURSOR_WORKSPACE',     # Cursor workspace
            
            # CodeBuddy IDE
            'CODEBUDDY_CWD',        # CodeBuddy current working directory
            'CODEBUDDY_WORKSPACE',  # CodeBuddy workspace
            
            # JetBrains IDEs
            'PROJECT_DIR',          # JetBrains project directory
            'IDEA_INITIAL_DIRECTORY', # IntelliJ IDEA
            'WORKSPACE_DIR',        # General workspace directory
            
            # Eclipse
            'PROJECT_LOC',          # Eclipse project location
            'WORKSPACE_LOC',        # Eclipse workspace location
            
            # Generic IDE variables
            'IDE_PROJECT_DIR',      # Generic IDE project directory
            'IDE_WORKSPACE',        # Generic IDE workspace
            'WORKSPACE_ROOT',       # Workspace root directory
            
            # MCP/Client specific
            'MCP_PROJECT_DIR',      # MCP-specific project directory
            'CLIENT_CWD',           # Client current working directory
            'MCP_CWD',              # MCP current working directory
            'MCP_WORKSPACE',        # MCP workspace directory
        ]
        
        for env_var in ide_env_vars:
            env_path = os.environ.get(env_var)
            if env_path and os.path.exists(env_path) and not self._is_ide_installation_path(env_path):
                candidates.append((env_var, env_path))
        
        # 2. Current working directory (lower priority on Windows)
        current_cwd = os.getcwd()
        if not self._is_ide_installation_path(current_cwd):
            candidates.append(("current_cwd", current_cwd))
        else:
            print(f"[DEBUG] Skipping IDE installation path: {current_cwd}", file=sys.stderr)
        
        # 3. System environment variables (Unix-like)
        system_vars = [
            'PWD',                  # Present working directory (Unix)
            'OLDPWD',               # Previous working directory (Unix)
        ]
        
        for env_var in system_vars:
            env_path = os.environ.get(env_var)
            if env_path and os.path.exists(env_path) and not self._is_ide_installation_path(env_path):
                candidates.append((env_var, env_path))
        
        # 4. Windows-specific environment variables
        if os.name == 'nt':
            windows_vars = [
                'CD',               # Current directory (Windows)
                'USERPROFILE',      # User profile directory (fallback)
            ]
            for env_var in windows_vars:
                env_path = os.environ.get(env_var)
                if env_path and os.path.exists(env_path) and not self._is_ide_installation_path(env_path):
                    candidates.append((env_var, env_path))
        
        # Debug logging
        print(f"[DEBUG] Working directory candidates: {candidates}", file=sys.stderr)
        print(f"[DEBUG] Current os.getcwd(): {current_cwd}", file=sys.stderr)
        print(f"[DEBUG] IDE installation path check: {self._is_ide_installation_path(current_cwd)}", file=sys.stderr)
        
        # Select the best candidate (prioritize IDE environment variables)
        for source, path in candidates:
            if self._is_valid_working_directory(path):
                print(f"[DEBUG] Selected working directory from {source}: {path}", file=sys.stderr)
                return path
        
        # Fallback to provided directory during initialization
        if self.fallback_working_directory:
            fallback_path = os.path.abspath(self.fallback_working_directory)
            if self._is_valid_working_directory(fallback_path) and not self._is_ide_installation_path(fallback_path):
                print(f"[DEBUG] Using fallback working directory: {fallback_path}", file=sys.stderr)
                return fallback_path
        
        # If all fails, require user input
        error_msg = (
            "⚠️  无法自动检测项目工作目录\n\n"
            "为确保AceFlow文件创建在正确位置，请在调用工具时明确指定 'directory' 参数：\n\n"
            "📁 示例用法：\n"
            "  • Windows: {\"directory\": \"C:\\\\Users\\\\YourName\\\\your-project\"}\n"
            "  • Linux/Mac: {\"directory\": \"/path/to/your/project\"}\n"
            "  • 当前目录: {\"directory\": \".\"} (仅在确认当前目录正确时使用)\n\n"
            "🤖 如果您使用Cline等AI助手：\n"
            "请要求AI助手提供当前打开项目的完整路径作为directory参数\n\n"
            f"🔍 调试信息：\n"
            f"  检测到的目录: {current_cwd}\n"
            f"  候选目录: {[path for _, path in candidates] if candidates else '无'}"
        )
        raise ValueError(error_msg)
    
    def _is_ide_installation_path(self, path: str) -> bool:
        """Check if path looks like an IDE installation directory."""
        path_lower = path.lower()
        
        # Common IDE installation path patterns (expanded for better detection)
        ide_patterns = [
            # VS Code patterns
            'microsoft vs code',
            'visual studio code',
            'code.exe',
            'vscode',
            '\\vscode\\',
            '/vscode/',
            
            # Cursor patterns  
            'cursor',
            '\\cursor\\',
            '/cursor/',
            
            # CodeBuddy patterns
            'codebuddy',
            '\\codebuddy\\',
            '/codebuddy/',
            
            # JetBrains patterns
            'jetbrains',
            'intellij',
            'pycharm',
            'webstorm',
            'phpstorm',
            
            # General IDE patterns
            'program files',
            'programme',
            'applications',
            'appdata\\local',
            'appdata\\roaming',
            
            # Other editors
            'notepad++',
            'sublime text',
            'atom',
            
            # Development tool patterns
            '.vscode-server',
            'code-server',
            
            # Common installation directories
            '/opt/',
            '/usr/share/',
            '/snap/',
            'c:\\program files',
            'c:\\program files (x86)',
        ]
        
        return any(pattern in path_lower for pattern in ide_patterns)
    
    def _is_valid_working_directory(self, path: str) -> bool:
        """Check if a path is a valid working directory.
        
        Args:
            path: Directory path to validate
            
        Returns:
            True if path is valid and accessible
        """
        try:
            return os.path.exists(path) and os.path.isdir(path) and os.access(path, os.R_OK | os.W_OK)
        except (OSError, PermissionError):
            return False
    
    def aceflow_init(
        self,
        mode: str,
        project_name: Optional[str] = None,
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initialize AceFlow project with specified mode.
        
        Args:
            mode: Workflow mode (minimal, standard, complete, smart)
            project_name: Optional project name
            directory: 项目目录的完整路径。强烈建议明确指定以确保文件创建在正确位置。
                      示例: "C:\\Users\\YourName\\your-project" 或 "/path/to/your/project"
                      提示：如果使用Cline等AI助手，请确保提供当前打开项目的完整路径
        
        Returns:
            Dict with success status, message, and project info
        """
        try:
            # Validate mode
            valid_modes = ["minimal", "standard", "complete", "smart"]
            if mode not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid mode '{mode}'. Valid modes: {', '.join(valid_modes)}",
                    "message": "Mode validation failed"
                }
            
            # Determine target directory using dynamic detection
            working_dir = self._get_dynamic_working_directory(directory)
            target_dir = Path(working_dir).resolve()
            
            # Debug logging for troubleshooting
            print(f"[DEBUG] Dynamic working directory detection:", file=sys.stderr)
            print(f"[DEBUG] Selected working_directory: {working_dir}", file=sys.stderr)
            print(f"[DEBUG] Final target_dir: {target_dir}", file=sys.stderr)
            
            # Create directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Set project name
            if not project_name:
                project_name = target_dir.name
            
            # Check if already initialized (unless forced)
            aceflow_dir = target_dir / ".aceflow"
            clinerules_file = target_dir / ".clinerules"
            
            if aceflow_dir.exists() or clinerules_file.exists():
                return {
                    "success": False,
                    "error": "Directory already contains AceFlow configuration",
                    "message": f"Directory '{target_dir}' is already initialized. Use force=true to overwrite."
                }
            
            # Initialize project structure
            result = self._initialize_project_structure(target_dir, project_name, mode)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Project '{project_name}' initialized successfully in {mode} mode",
                    "project_info": {
                        "name": project_name,
                        "mode": mode,
                        "directory": str(target_dir),
                        "created_files": result.get("created_files", []),
                        "debug_info": {
                            "detected_working_dir": str(target_dir),
                            "original_cwd": os.getcwd(),
                            "pwd_env": os.environ.get('PWD'),
                            "cwd_env": os.environ.get('CWD')
                        }
                    }
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize project",
                "debug_info": {
                    "exception_type": type(e).__name__,
                    "working_directory": os.getcwd(),
                    "target_directory": str(target_dir) if 'target_dir' in locals() else "unknown"
                }
            }
    
    def _initialize_project_structure(self, target_dir: Path, project_name: str, mode: str) -> Dict[str, Any]:
        """Initialize the complete project structure."""
        created_files = []
        
        try:
            # Create .aceflow directory
            aceflow_dir = target_dir / ".aceflow"
            aceflow_dir.mkdir(exist_ok=True)
            created_files.append(".aceflow/")
            
            # Create aceflow_result directory
            result_dir = target_dir / "aceflow_result"
            result_dir.mkdir(exist_ok=True)
            created_files.append("aceflow_result/")
            
            # Create project state file
            state_data = {
                "project": {
                    "name": project_name,
                    "mode": mode.upper(),
                    "created_at": datetime.datetime.now().isoformat(),
                    "version": "3.0"
                },
                "flow": {
                    "current_stage": "user_stories" if mode != "minimal" else "implementation",
                    "completed_stages": [],
                    "progress_percentage": 0
                },
                "metadata": {
                    "total_stages": self._get_stage_count(mode),
                    "last_updated": datetime.datetime.now().isoformat()
                }
            }
            
            state_file = aceflow_dir / "current_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            created_files.append(".aceflow/current_state.json")
            
            # Create .clinerules file
            clinerules_content = self._generate_clinerules(project_name, mode)
            clinerules_file = target_dir / ".clinerules"
            with open(clinerules_file, 'w', encoding='utf-8') as f:
                f.write(clinerules_content)
            created_files.append(".clinerules")
            
            # Create template.yaml
            template_content = self._generate_template_yaml(mode)
            template_file = aceflow_dir / "template.yaml"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            created_files.append(".aceflow/template.yaml")
            
            # Note: In MCP environment, we don't copy Python scripts
            # All operations are handled through MCP tools
            
            # Create README
            readme_content = self._generate_readme(project_name, mode)
            readme_file = target_dir / "README_ACEFLOW.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            created_files.append("README_ACEFLOW.md")
            
            return {
                "success": True,
                "created_files": created_files
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create project structure"
            }
    
    def _get_stage_count(self, mode: str) -> int:
        """Get the number of stages for the given mode."""
        stage_counts = {
            "minimal": 3,
            "standard": 8,
            "complete": 12,
            "smart": 10
        }
        return stage_counts.get(mode, 8)
    
    def _generate_clinerules(self, project_name: str, mode: str) -> str:
        """Generate .clinerules content."""
        return f"""# AceFlow v3.0 - AI Agent 集成配置
# 项目: {project_name}
# 模式: {mode}
# 初始化时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 工作模式配置
AceFlow模式: {mode}
输出目录: aceflow_result/
配置目录: .aceflow/
项目名称: {project_name}

## 核心工作原则  
1. 所有项目文档和代码必须输出到 aceflow_result/ 目录
2. 严格按照 .aceflow/template.yaml 中定义的流程执行
3. 每个阶段完成后更新项目状态文件
4. 保持跨对话的工作记忆和上下文连续性
5. 遵循AceFlow v3.0规范进行标准化输出

## 质量标准
- 代码质量: 遵循项目编码规范，注释完整
- 文档质量: 结构清晰，内容完整，格式统一
- 测试覆盖: 根据模式要求执行相应测试策略
- 交付标准: 符合 aceflow-spec_v3.0.md 规范

## 工具集成命令
- python aceflow-validate.py: 验证项目状态和合规性
- python aceflow-stage.py: 管理项目阶段和进度
- python aceflow-templates.py: 管理模板配置

记住: AceFlow是AI Agent的增强层，通过规范化输出和状态管理，实现跨对话的工作连续性。
"""
    
    def _generate_template_yaml(self, mode: str) -> str:
        """Generate template.yaml content based on mode."""
        templates = {
            "minimal": """# AceFlow Minimal模式配置
name: "Minimal Workflow"
version: "3.0"
description: "快速原型和概念验证工作流"

stages:
  - name: "implementation"
    description: "快速实现核心功能"
    required: true
  - name: "test"
    description: "基础功能测试"
    required: true
  - name: "demo"
    description: "功能演示"
    required: true

quality_gates:
  - stage: "implementation"
    criteria: ["核心功能完成", "基本可运行"]
  - stage: "test"
    criteria: ["主要功能测试通过"]""",
            
            "standard": """# AceFlow Standard模式配置
name: "Standard Workflow"
version: "3.0"
description: "标准软件开发工作流"

stages:
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "task_breakdown"
    description: "任务分解"
    required: true
  - name: "test_design"
    description: "测试用例设计"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "unit_test"
    description: "单元测试"
    required: true
  - name: "integration_test"
    description: "集成测试"
    required: true
  - name: "code_review"
    description: "代码审查"
    required: true
  - name: "demo"
    description: "功能演示"
    required: true

quality_gates:
  - stage: "user_stories"
    criteria: ["用户故事完整", "验收标准明确"]
  - stage: "implementation"
    criteria: ["代码质量合格", "功能完整"]
  - stage: "unit_test"
    criteria: ["测试覆盖率 > 80%", "所有测试通过"]""",
            
            "complete": """# AceFlow Complete模式配置  
name: "Complete Workflow"
version: "3.0"
description: "完整企业级开发工作流"

stages:
  - name: "requirement_analysis"
    description: "需求分析"
    required: true
  - name: "architecture_design"
    description: "架构设计"
    required: true
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "task_breakdown"
    description: "任务分解"
    required: true
  - name: "test_design"
    description: "测试用例设计"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "unit_test"
    description: "单元测试"
    required: true
  - name: "integration_test"
    description: "集成测试"
    required: true
  - name: "performance_test"
    description: "性能测试"
    required: true
  - name: "security_review"
    description: "安全审查"
    required: true
  - name: "code_review"
    description: "代码审查"
    required: true
  - name: "demo"
    description: "功能演示"
    required: true

quality_gates:
  - stage: "architecture_design"
    criteria: ["架构设计完整", "技术选型合理"]
  - stage: "implementation"
    criteria: ["代码质量优秀", "性能满足要求"]
  - stage: "security_review"
    criteria: ["安全检查通过", "无重大漏洞"]""",
            
            "smart": """# AceFlow Smart模式配置
name: "Smart Adaptive Workflow"  
version: "3.0"
description: "AI增强的自适应工作流"

stages:
  - name: "project_analysis"
    description: "AI项目复杂度分析"
    required: true
  - name: "adaptive_planning"
    description: "自适应规划"
    required: true
  - name: "user_stories"
    description: "用户故事分析"
    required: true
  - name: "smart_breakdown"
    description: "智能任务分解"
    required: true
  - name: "test_generation"
    description: "AI测试用例生成"
    required: true
  - name: "implementation"
    description: "功能实现"
    required: true
  - name: "automated_test"
    description: "自动化测试"
    required: true
  - name: "quality_assessment"
    description: "AI质量评估"
    required: true
  - name: "optimization"
    description: "性能优化"
    required: true
  - name: "demo"
    description: "智能演示"
    required: true

ai_features:
  - "复杂度智能评估"
  - "动态流程调整"
  - "自动化测试生成"
  - "质量智能分析"

quality_gates:
  - stage: "project_analysis"
    criteria: ["复杂度评估完成", "技术栈确定"]
  - stage: "implementation"
    criteria: ["AI代码质量检查通过", "性能指标达标"]"""
        }
        
        return templates.get(mode, templates["standard"])
    
    def _generate_readme(self, project_name: str, mode: str) -> str:
        """Generate README content."""
        return f"""# {project_name}

## AceFlow项目说明

本项目使用AceFlow v3.0工作流管理系统，采用 **{mode.upper()}** 模式。

### 项目信息
- **项目名称**: {project_name}
- **工作流模式**: {mode.upper()}
- **初始化时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **AceFlow版本**: 3.0

### 目录结构
```
{project_name}/
├── .aceflow/           # AceFlow配置目录
│   ├── current_state.json    # 项目状态文件
│   └── template.yaml         # 工作流模板
├── aceflow_result/     # 项目输出目录
├── .clinerules         # AI Agent工作配置
└── README_ACEFLOW.md   # 本文件
```

### MCP工具使用指南

本项目支持通过MCP (Model Context Protocol) 工具进行管理。在支持MCP的AI客户端（如Cline、Claude Desktop等）中，可以使用以下工具：

#### 1. 查看当前阶段状态
使用 `aceflow_stage` 工具查看项目当前状态：
```
工具: aceflow_stage
参数:
  action: "status"
```

#### 2. 验证项目配置
使用 `aceflow_validate` 工具验证项目合规性：
```
工具: aceflow_validate
参数:
  mode: "basic"
  fix: false
  report: true
```

#### 3. 推进到下一阶段
使用 `aceflow_stage` 工具推进工作流：
```
工具: aceflow_stage
参数:
  action: "next"
```

#### 4. 查看所有阶段列表
```
工具: aceflow_stage
参数:
  action: "list"
```

#### 5. 重置项目状态
```
工具: aceflow_stage
参数:
  action: "reset"
```

### 工作流程

根据{mode}模式，项目将按以下阶段进行：

{self._get_stage_description(mode)}

### MCP客户端集成说明

#### 在Cline中使用
1. 确保AceFlow MCP服务器已启动
2. 在Cline设置中配置MCP服务器连接
3. 直接使用上述MCP工具命令进行项目管理

#### 在Claude Desktop中使用
1. 在MCP服务器配置中添加aceflow-mcp-server
2. 重启Claude Desktop
3. 在对话中直接调用MCP工具

#### 通过HTTP API使用
如果使用HTTP模式的MCP服务器：
```bash
# 查看项目状态
curl -X POST http://localhost:8000/mcp \\
  -H "Content-Type: application/json" \\
  -d '{{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/call",
    "params": {{
      "name": "aceflow_stage",
      "arguments": {{"action": "status"}}
    }}
  }}'
```

### 注意事项

- 所有项目文档和代码请输出到 `aceflow_result/` 目录
- 使用AI助手时，确保AceFlow MCP工具已正确加载
- 每个阶段完成后，使用 `aceflow_stage` 工具更新状态
- 定期使用 `aceflow_validate` 工具检查项目合规性
- 所有操作都通过MCP工具接口进行，无需直接运行Python脚本

### 帮助和支持

如需帮助，请参考：
- AceFlow MCP工具列表：使用任意MCP客户端查看可用工具
- 项目状态文件: `.aceflow/current_state.json`
- 工作流配置: `.aceflow/template.yaml`
- MCP服务器文档: 查看aceflow-mcp-server相关文档

### 故障排除

1. **MCP工具无法使用**
   - 确认MCP服务器正在运行
   - 检查客户端MCP配置是否正确

2. **工作目录不正确**
   - 确保在正确的项目目录中操作
   - 检查.aceflow目录是否存在

3. **阶段推进失败**
   - 使用 `aceflow_validate` 检查项目状态
   - 查看 `.aceflow/current_state.json` 文件

---
*Generated by AceFlow v3.0 MCP Server*"""
    
    def _get_stage_description(self, mode: str) -> str:
        """Get stage descriptions for the mode."""
        descriptions = {
            "minimal": """1. **Implementation** - 快速实现核心功能
2. **Test** - 基础功能测试  
3. **Demo** - 功能演示""",
            
            "standard": """1. **User Stories** - 用户故事分析
2. **Task Breakdown** - 任务分解
3. **Test Design** - 测试用例设计
4. **Implementation** - 功能实现
5. **Unit Test** - 单元测试
6. **Integration Test** - 集成测试
7. **Code Review** - 代码审查
8. **Demo** - 功能演示""",
            
            "complete": """1. **Requirement Analysis** - 需求分析
2. **Architecture Design** - 架构设计
3. **User Stories** - 用户故事分析
4. **Task Breakdown** - 任务分解
5. **Test Design** - 测试用例设计
6. **Implementation** - 功能实现
7. **Unit Test** - 单元测试
8. **Integration Test** - 集成测试
9. **Performance Test** - 性能测试
10. **Security Review** - 安全审查
11. **Code Review** - 代码审查
12. **Demo** - 功能演示""",
            
            "smart": """1. **Project Analysis** - AI项目复杂度分析
2. **Adaptive Planning** - 自适应规划
3. **User Stories** - 用户故事分析
4. **Smart Breakdown** - 智能任务分解
5. **Test Generation** - AI测试用例生成
6. **Implementation** - 功能实现
7. **Automated Test** - 自动化测试
8. **Quality Assessment** - AI质量评估
9. **Optimization** - 性能优化
10. **Demo** - 智能演示"""
        }
        
        return descriptions.get(mode, descriptions["standard"])
    
    def aceflow_stage(
        self,
        action: str,
        stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manage project stages and workflow.
        
        Args:
            action: Stage management action (status, next, list, reset)
            stage: Optional target stage name
            
        Returns:
            Dict with success status and stage information
        """
        try:
            if action == "status":
                result = self.workflow_engine.get_current_status()
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            elif action == "next":
                result = self.workflow_engine.advance_to_next_stage()
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            elif action == "list":
                stages = self.workflow_engine.list_all_stages()
                return {
                    "success": True,
                    "action": action,
                    "result": {
                        "stages": stages
                    }
                }
            elif action == "reset":
                result = self.workflow_engine.reset_project()
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'. Valid actions: status, next, list, reset",
                    "message": "Action not supported"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute stage action: {action}"
            }
    
    def aceflow_validate(
        self,
        mode: str = "basic",
        fix: bool = False,
        report: bool = False
    ) -> Dict[str, Any]:
        """Validate project compliance and quality.
        
        Args:
            mode: Validation mode (basic, complete)
            fix: Auto-fix issues if possible
            report: Generate detailed report
            
        Returns:
            Dict with validation results
        """
        try:
            validator = self.project_manager.get_validator()
            validation_result = validator.validate(mode=mode, auto_fix=fix, generate_report=report)
            
            return {
                "success": True,
                "validation_result": {
                    "status": validation_result["status"],
                    "checks_total": validation_result["checks"]["total"],
                    "checks_passed": validation_result["checks"]["passed"],
                    "checks_failed": validation_result["checks"]["failed"],
                    "mode": mode,
                    "auto_fix_enabled": fix,
                    "report_generated": report
                },
                "message": f"Validation completed in {mode} mode"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Validation failed"
            }
    
    def aceflow_template(
        self,
        action: str,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manage workflow templates.
        
        Args:
            action: Template action (list, apply, validate)
            template: Optional template name
            
        Returns:
            Dict with template operation results
        """
        try:
            if action == "list":
                result = self.template_manager.list_templates()
                return {
                    "success": True,
                    "action": action,
                    "result": {
                        "available_templates": result["available"],
                        "current_template": result["current"]
                    }
                }
            elif action == "apply":
                if not template:
                    return {
                        "success": False,
                        "error": "Template name is required for apply action",
                        "message": "Please specify a template name"
                    }
                result = self.template_manager.apply_template(template)
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            elif action == "validate":
                result = self.template_manager.validate_current_template()
                return {
                    "success": True,
                    "action": action,
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": f"Invalid action '{action}'. Valid actions: list, apply, validate",
                    "message": "Action not supported"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Template action failed: {action}"
            }