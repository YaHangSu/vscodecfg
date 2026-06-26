# VSCode / Cursor + Qt + MSVC 环境配置教程

> 原文参考：[CSDN - VSCode+Qt+MSVC环境配置](https://blog.csdn.net/qq_40644520/article/details/143849955)
> 实践项目：`RobotAssist/xMate`
> 环境：Windows 10/11 x64，Qt 5.15.2 + MSVC 2019，代码补全默认使用 **C/C++ 插件 IntelliSense（Tag Parser）**，调试使用 **cppvsdbg（CDB）**；**clangd** 为可选增强方案

本文整理了一套可在 **VSCode 与 Cursor 共用同一份 `.vscode` 配置** 的 Qt + MSVC 开发环境，涵盖安装、环境变量、构建任务、代码补全（IntelliSense / clangd）、调试及 Cursor 适配。

---

## 目录

1. [安装清单](#一-安装清单)
2. [环境变量配置](#二-环境变量配置)
3. [编辑器配置](#三-编辑器配置)
4. [（可选）clangd 与 compile_commands.json](#四可选clangd-与-compile_commandsjson)
5. [构建与运行](#五-构建与运行)
6. [调试器配置](#六-调试器配置)
7. [Cursor 调试适配](#七-cursor-调试适配)
8. [常见错误排查](#八-常见错误排查)

---

## 一、安装清单

| 序号 | 组件                       | 说明                                                                                |
| ---- | -------------------------- | ----------------------------------------------------------------------------------- |
| 1    | **Windows SDK**      | 本机版本`10.0.26100.0`（按实际安装版本调整）                                      |
| 2    | **Qt**               | `Qt 5.15.2` + `MSVC 2019 64-bit`                                                |
| 3    | **Visual Studio**    | VS 2019 / VS 2022（需包含「使用 C++ 的桌面开发」）                                  |
| 4    | **VSCode 或 Cursor** | 二者共用`.vscode` 目录下的配置                                                    |
| 5    | **插件**             | `C/C++`（IntelliSense + 调试）、`Qt Configure`、`Qt tools`；`clangd` 为可选 |
| 6    | **调试器**           | CDB（Windows SDK 自带，通过`cppvsdbg` 调用）                                      |
| 7    | **Python 3**         | 可选，仅在使用 clangd 时需用于生成`compile_commands.json`                         |

> **说明**：代码补全默认由 **C/C++ 插件 IntelliSense（Tag Parser）** 提供，配置简单、无需额外脚本。若需要更精确的语义分析，可选用 **clangd** 作为增强方案（见 [第四章](#四可选clangd-与-compile_commandsjson)）。无论哪种补全方案，调试均依赖 C/C++ 插件的 `cppvsdbg`。

---

## 二、环境变量配置

### 2.1 Qt 环境变量

将以下路径添加到系统 **Path**：

```
C:\Qt\5.15.2\msvc2019_64
C:\Qt\5.15.2\msvc2019_64\bin
C:\Qt\Tools\QtCreator\bin
```

### 2.2 cl 编译器环境变量

#### 创建 INCLUDE 变量

```
C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.29.30133\include
C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\shared
C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\ucrt
C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\um
C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\winrt
```

> `INCLUDE` 和 `LIB` 中的 SDK 版本号必须一致。

#### 添加 cl.exe 到 Path

```
C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.29.30133\bin\Hostx64\x64
```

### 2.3 rc 资源配置

1. 从 SDK 目录复制 `rc.exe`、`rcdll.dll`：

```
   C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64
```

2. 粘贴到 cl.exe 所在目录（与上一节 Path 相同）。

---

## 三、编辑器配置

大部分项目配置文件位于 `.vscode/` 目录，VSCode 与 Cursor 直接共用。

代码补全有两种方案，**二选一**即可：

| 方案                           | 适用场景                               | 对应章节                                                                               |
| ------------------------------ | -------------------------------------- | -------------------------------------------------------------------------------------- |
| **IntelliSense（推荐）** | 快速上手，配置`includePath` 即可补全 | [3.2 节](#32-intellisense-推荐用户-settingsjson)                                          |
| **clangd（可选）**       | 需要更精确的跳转、诊断、clang-tidy     | [3.3 节](#33-clangd-可选用户-settingsjson) + [第四章](#四可选clangd-与-compile_commandsjson) |

> 使用 **IntelliSense** 的用户配置完 [3.2 节](#32-intellisense-推荐用户-settingsjson) 和 [3.4 节](#34-c_cpp_propertiesjson) 后，**可直接跳过第四章**。

### 3.1 项目工作区 settings.json

**文件路径：** `.vscode/settings.json`（随项目提交，VSCode 与 Cursor 共用）

用于项目级编辑器行为：隐藏构建目录、排除无关目录检索等。示例（按项目实际目录调整）：

```json
{
    "search.exclude": {
        "**/xmate/_historic": true,
        "**/xmate/3rdparty": true,
        "**/imolplatform": true,
        "**/build-debug/xmate": true,
        "**/build-release/xmate": true,
        "**/build-debug": true,
        "**/build-release": true
    },
    "files.exclude": {
        "**/xmate/_historic": true,
        "**/build-debug/xmate": true,
        "**/build-release/xmate": true
    }
}
```

> 若选用 **clangd** 方案，可在本文件中追加 `"C_Cpp.errorSquiggles": "disabled"`，避免 C/C++ 插件与 clangd 同时报红波浪线。

### 3.2 IntelliSense（推荐，用户 settings.json）

**文件路径：** 用户级 settings.json，**不是** `.vscode/settings.json`

| 编辑器 | 路径                                    |
| ------ | --------------------------------------- |
| VSCode | `%APPDATA%\Code\User\settings.json`   |
| Cursor | `%APPDATA%\Cursor\User\settings.json` |

对 qmake 这类未原生导出 `compile_commands.json` 的项目，建议将 IntelliSense 引擎设为 **Tag Parser**。它基于符号索引，不依赖完整编译数据库，配置 [3.4 节](#34-c_cpp_propertiesjson) 的 `includePath` 后即可工作，启动更快。

```json
{
    "C_Cpp.intelliSenseEngine": "Tag Parser"
}
```

| 配置项                       | 说明                                                                             |
| ---------------------------- | -------------------------------------------------------------------------------- |
| `C_Cpp.intelliSenseEngine` | 设为`Tag Parser`，适合 qmake 项目；语义精度不如 clangd，但对跳转、补全通常够用 |

> Tag Parser 模式下无需安装 clangd 插件，也无需生成 `compile_commands.json`。

### 3.3 clangd（可选，用户 settings.json）

**文件路径：** 用户级 settings.json，**不是** `.vscode/settings.json`

若需要更精确的代码分析，可安装 **clangd** 插件并追加以下配置。此时应关闭 C/C++ 插件的 IntelliSense，避免重复索引。

```json
{
    "C_Cpp.intelliSenseEngine": "disabled",
    "clangd.arguments": [
        "--compile-commands-dir=${workspaceFolder}",
        "--background-index",
        "--header-insertion=iwyu",
        "--clang-tidy"
    ],
    "clangd.fallbackFlags": [
        "-std=c++17"
    ]
}
```

| 配置项                       | 说明                                                                      |
| ---------------------------- | ------------------------------------------------------------------------- |
| `C_Cpp.intelliSenseEngine` | 设为`disabled`，避免与 clangd 冲突（**仅 clangd 方案需要**）      |
| `clangd.arguments`         | 指定`compile_commands.json` 所在目录、后台索引、clang-tidy 等           |
| `clangd.fallbackFlags`     | 无 compile_commands 时的兜底 C++ 标准，按项目改为`c++14` / `c++20` 等 |

> 选用 clangd 后，还需按 [第四章](#四可选clangd-与-compile_commandsjson) 生成 `compile_commands.json`。若希望某配置仅对单个项目生效，也可写入 `.vscode/settings.json`。

### 3.4 c_cpp_properties.json

> 使用 **IntelliSense（Tag Parser）** 时，此文件的 `includePath`、`defines` 等直接参与代码补全，是 IntelliSense 方案的核心配置。
> 使用 **clangd** 时，此文件主要供 C/C++ 插件调试器参考，代码补全由 clangd + `compile_commands.json` 提供。

```json
{
    "configurations": [
        {
            "name": "windows-msvc-x64",
            "includePath": [
                "${workspaceFolder}/**",
                "C:\\Qt\\5.15.2\\msvc2019_64\\include\\**"
            ],
            "defines": [
                "_DEBUG",
                "UNICODE",
                "_UNICODE"
            ],
            "windowsSdkVersion": "10.0.26100.0",
            "compilerPath": "cl.exe",
            "cStandard": "c17",
            "cppStandard": "c++17",
            "intelliSenseMode": "windows-msvc-x64"
        },
        {
            "name": "windows-gcc-x64",
            "includePath": [
                "${workspaceFolder}/**"
            ],
            "defines": [
                "_DEBUG",
                "UNICODE",
                "_UNICODE"
            ],
            "windowsSdkVersion": "10.0.26100.0",
            "compilerPath": "C:/Program Files/Microsoft Visual Studio/2022/Professional/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64/cl.exe",
            "cStandard": "${default}",
            "cppStandard": "${default}",
            "intelliSenseMode": "windows-msvc-x64",
            "mergeConfigurations": false,
            "recursiveIncludes": {},
            "browse": {
                "limitSymbolsToIncludedHeaders": true
            }
        }
    ],
    "version": 4
}
```

### 3.5 tasks.json

构建目录分为 `build-debug` 和 `build-release`，使用 PowerShell + jom 多线程编译：

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "mkdir",
            "type": "shell",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}"
            },
            "command": "mkdir",
            "args": [
                "-Force",
                "build-debug",
                ",",
                "build-release"
            ]
        },
        {
            "label": "qmake-debug",
            "type": "shell",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}/build-debug"
            },
            "command": "C:\\Qt\\5.15.2\\msvc2019_64\\bin\\qmake.exe",
            "args": [
                "../${workspaceFolderBasename}.pro",
                "-spec",
                "win32-msvc",
                "\"CONFIG+=debug\"",
                "\"CONFIG+=qml_debug\"",
                "\"QMAKE_LFLAGS+=/INCREMENTAL:NO\"",
                "\"QMAKE_LFLAGS_DEBUG+=/DEBUG:FASTLINK\"",
                "\"QMAKE_CXXFLAGS+=/FC\""
            ],
            "dependsOn": [
                "mkdir"
            ]
        },
        {
            "label": "make-debug",
            "type": "shell",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}/build-debug"
            },
            "command": "C:\\Qt\\Tools\\QtCreator\\bin\\jom\\jom.exe",
            "args": [
                "-c",
                "-f",
                "Makefile",
                "-j8"
            ],
            "problemMatcher": {
                "owner": "cpp",
                "fileLocation": [
                    "relative",
                    "${workspaceFolder}"
                ],
                "pattern": {
                    "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            },
            "dependsOn": [
                "qmake-debug"
            ]
        },
        {
            "label": "run-debug",
            "type": "process",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}/build-debug"
            },
            "command": "${workspaceFolder}/build-debug/imolProgram.exe",
            "dependsOn": [
                "make-debug"
            ]
        },
        {
            "label": "run-debug-without-compile",
            "type": "process",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}/build-debug"
            },
            "command": "${workspaceFolder}/build-debug/imolProgram.exe"
        },
        {
            "label": "qmake-release",
            "type": "shell",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}/build-release"
            },
            "command": "C:\\Qt\\5.15.2\\msvc2019_64\\bin\\qmake.exe",
            "args": [
                "../${workspaceFolderBasename}.pro",
                "-spec",
                "win32-msvc",
                "\"CONFIG+=qtquickcompiler\"",
                "\"QMAKE_CXXFLAGS+=/FC\""
            ]
        },
        {
            "label": "make-release",
            "type": "shell",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}/build-release"
            },
            "command": "C:\\Qt\\Tools\\QtCreator\\bin\\jom\\jom.exe",
            "args": [
                "-f",
                "Makefile",
                "-j8"
            ],
            "problemMatcher": {
                "owner": "cpp",
                "fileLocation": [
                    "relative",
                    "${workspaceFolder}"
                ],
                "pattern": {
                    "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            },
            "dependsOn": [
                "qmake-release"
            ]
        },
        {
            "label": "run-release",
            "type": "process",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}/build-release"
            },
            "command": "${workspaceFolder}/build-release/Robot Assist.exe",
            "dependsOn": [
                "make-release"
            ]
        },
        {
            "label": "run-release-without-compile",
            "type": "process",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}/build-release"
            },
            "command": "${workspaceFolder}/build-release/Robot Assist.exe"
        },
        {
            "label": "clean-debug",
            "type": "shell",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}/build-debug"
            },
            "command": "C:\\Qt\\Tools\\QtCreator\\bin\\jom\\jom.exe",
            "args": [
                "clean"
            ]
        },
        {
            "label": "clean-release",
            "type": "shell",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}/build-release"
            },
            "command": "C:\\Qt\\Tools\\QtCreator\\bin\\jom\\jom.exe",
            "args": [
                "clean"
            ]
        },
        {
            "label": "gen-compile-commands",
            "type": "shell",
            "options": {
                "shell": {
                    "executable": "powershell"
                },
                "cwd": "${workspaceFolder}/build-debug"
            },
            "command": "python",
            "args": [
                "command.py"
            ],
            "dependsOn": [
                "make-debug"
            ]
        }
    ]
}
```

**任务说明：**

| 任务标签                                          | 功能                                                                   |
| ------------------------------------------------- | ---------------------------------------------------------------------- |
| `mkdir`                                         | 创建`build-debug`、`build-release` 目录                            |
| `qmake-debug`                                   | Debug 模式运行 qmake                                                   |
| `make-debug`                                    | jom 编译 Debug（`-j8` 八线程）                                       |
| `run-debug`                                     | 编译并运行 Debug 可执行文件                                            |
| `run-debug-without-compile`                     | 跳过编译，直接运行 Debug                                               |
| `qmake-release` / `make-release`              | Release 构建                                                           |
| `run-release` / `run-release-without-compile` | 运行 Release                                                           |
| `clean-debug` / `clean-release`               | 清理构建产物                                                           |
| `gen-compile-commands`                          | （clangd 可选）编译后运行`command.py` 生成 `compile_commands.json` |

---

## 四、（可选）clangd 与 compile_commands.json

> **本章为可选增强方案。** 若已在 [3.2 节](#32-intellisense-推荐用户-settingsjson) 使用 C/C++ 插件 **IntelliSense（Tag Parser）**，**可直接跳过本章**，无需安装 clangd 插件、无需 Python 脚本、无需生成 `compile_commands.json`。
>
> 仅在选用 [3.3 节](#33-clangd-可选用户-settingsjson) 的 **clangd** 方案时，才需要按本章配置。clangd 能提供更精确的语义分析、跳转和 clang-tidy 诊断，但配置成本更高。

qmake 项目默认不生成 `compile_commands.json`，需要通过 Python 脚本从 `Makefile.Debug` 中提取编译参数，供 clangd 索引使用。

### 4.1 工作流程

```
qmake-debug → make-debug → command.py → compile_commands.json → clangd 索引
```

1. 执行 `qmake-debug` + `make-debug`
2. 在 `build-debug/` 目录下运行 `python command.py`
3. 脚本在项目根目录生成 `compile_commands.json`
4. clangd 自动读取该文件，提供准确的代码补全、跳转和诊断

> 每次修改 `.pro` 文件、增删源文件或更改编译选项后，需重新执行 qmake + make + `command.py`。

### 4.2 command.py

脚本放在 `build-debug/command.py`，从 qmake 生成的 `Makefile.Debug` 中解析 `CXXFLAGS`、`DEFINES`、`INCPATH`、`SOURCES`，输出标准 `compile_commands.json`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from pathlib import Path

BUILD_ROOT = Path.cwd()
OUTPUT_FILE = BUILD_ROOT.parent / "compile_commands.json"

entries = []


def read_make_var(text: str, var_name: str):
    """
    读取 qmake 多行变量：

    SOURCES = \
        a.cpp \
        b.cpp
    """
    pattern = re.compile(
        rf"^{re.escape(var_name)}\s*=\s*(.*?)^(?=[A-Za-z0-9_]+\s*=|\Z)",
        re.M | re.S,
    )

    m = pattern.search(text)
    if not m:
        return ""

    value = m.group(1)
    lines = []

    for line in value.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.endswith("\\"):
            line = line[:-1].strip()
        lines.append(line)

    return " ".join(lines)


def split_sources(source_text: str):
    result = []
    for item in source_text.split():
        if re.search(r"\.(cpp|cc|cxx|c)$", item, re.I):
            result.append(item)
    return result


for makefile in BUILD_ROOT.rglob("Makefile.Debug"):
    try:
        text = makefile.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"skip {makefile}: {e}")
        continue

    cxxflags = read_make_var(text, "CXXFLAGS")
    defines = read_make_var(text, "DEFINES")
    incpath = read_make_var(text, "INCPATH")
    sources = read_make_var(text, "SOURCES")

    source_files = split_sources(sources)
    if not source_files:
        continue

    project_dir = makefile.parent
    flags = " ".join(x for x in [cxxflags, defines, incpath] if x)

    for src in source_files:
        src_path = Path(src)
        if not src_path.is_absolute():
            src_path = (project_dir / src).resolve()

        entries.append({
            "directory": str(project_dir.resolve()),
            "file": str(src_path),
            "command": f"cl {flags} {src_path}"
        })

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2, ensure_ascii=False)

print(f"generated {len(entries)} entries")
print(f"output: {OUTPUT_FILE}")
```

**手动执行：**

```powershell
cd D:\syh\dev\RobotAssist\build-debug
python command.py
```

**或通过任务执行：** `Ctrl+Shift+P` → `Tasks: Run Task` → `gen-compile-commands`

### 4.3 clangd 验证

生成 `compile_commands.json` 后：

1. 确认项目根目录存在 `compile_commands.json`
2. 打开任意 `.cpp` 文件，等待 clangd 索引完成（状态栏显示 clangd 图标）
3. 测试跳转到定义（`F12`）、自动补全、错误波浪线是否正常

---

## 五、构建与运行

### 仅编译运行

1. `Ctrl + Shift + P` → `Tasks: Run Task`
2. 选择 `run-debug` 或 `run-release`

### 编译 + 更新 clangd 索引（仅 clangd 方案）

选用 clangd 时，修改源码或 `.pro` 后需更新索引：

`Ctrl+Shift+P` → `Tasks: Run Task` → `gen-compile-commands`

该任务会先执行 `make-debug`，再在 `build-debug/` 下运行 `python command.py`。

---

## 六、调试器配置

MSVC 使用 **cppvsdbg**（底层为 CDB 调试器）。`launch.json` 配置如下：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Build && Debug",
            "type": "cppvsdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build-debug/ImolProgram.exe",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}/build-debug",
            "environment": [],
            "console": "integratedTerminal",
            "preLaunchTask": "make-debug",
            "visualizerFile": "C:\\Users\\suyah\\.visualizers\\qt5.natvis"
        },
        {
            "name": "Build && Release",
            "type": "cppvsdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build-release/Robot Assist.exe",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}/build-release",
            "environment": [],
            "console": "integratedTerminal",
            "preLaunchTask": "make-release"
        },
        {
            "name": "Run-Debug",
            "type": "cppvsdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build-debug/ImolProgram.exe",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}/build-debug",
            "environment": [],
            "console": "integratedTerminal",
            "visualizerFile": "C:\\Users\\suyah\\.visualizers\\qt5.natvis"
        },
        {
            "name": "Run-Release",
            "type": "cppvsdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build-release/Robot Assist.exe",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}/build-release",
            "environment": [],
            "console": "integratedTerminal"
        },
        {
            "name": "Attach to Process",
            "type": "cppvsdbg",
            "request": "attach",
            "processId": "${command:pickProcess}",
            "logging": {
                "moduleLoad": true
            },
            "visualizerFile": "C:\\Users\\suyah\\.visualizers\\qt5.natvis"
        },
        {
            "name": "C/C++ Runner: Debug Session",
            "type": "cppdbg",
            "request": "launch",
            "args": [],
            "stopAtEntry": false,
            "externalConsole": true,
            "cwd": "c:/dev/RobotAssist",
            "program": "c:/dev/RobotAssist/build/Debug/outDebug",
            "MIMode": "gdb",
            "miDebuggerPath": "gdb",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ]
        },
        {
            "name": "Qt Debug (LLDB)",
            "type": "lldb",
            "request": "launch",
            "program": "${workspaceFolder}/build-debug/imolProgram.exe",
            "cwd": "${workspaceFolder}/build-debug",
            "args": [],
            "env": {
                "PATH": "C:/Qt/5.15.2/msvc2019_64/bin;${env:PATH}"
            },
            "stopOnEntry": false
        }
    ]
}
```

**配置说明：**

| 配置名                          | 说明                                                        |
| ------------------------------- | ----------------------------------------------------------- |
| `Build && Debug`              | 先编译（`preLaunchTask: make-debug`）再调试，带 Qt natvis |
| `Build && Release`            | Release 编译后调试                                          |
| `Run-Debug` / `Run-Release` | 跳过编译，直接调试已构建的可执行文件                        |
| `Attach to Process`           | 附加到运行中的进程                                          |
| `Qt Debug (LLDB)`             | 备选 LLDB 调试方案(暂不可用)                                |

**Qt 类型可视化：** `visualizerFile` 指向 `qt5.natvis`，调试时可正确显示 `QString`、`QVector` 等 Qt 类型（不配置这项Debug时候无法正确显示变量值）。

### 开始调试（VSCode）

1. 设置断点
2. 左侧 **运行和调试** → 选择 `Build && Debug` → 按 `F5`

---

## 七、Cursor 调试适配

Cursor 基于 VSCode，但默认 **不支持 `cppvsdbg` 调试类型**（C/C++ 插件会校验签名）。按以下步骤修改后，Cursor 可与 VSCode **共用同一份** `tasks.json` 和 `launch.json`。

> 参考：[Make Cursor Work with cppvsdbg](https://gist.github.com/Ouroboros/1a1e0b9c8bcbac2a519516aa5a12a52b)

### 7.1 修改 cpptools 的 package.json

找到 Cursor 扩展目录（版本号以本机为准）：

```
%USERPROFILE%\.cursor\extensions\ms-vscode.cpptools-<version>-win32-x64\package.json
```

将所有 `"when": "workspacePlatform == windows"` 条件移除或改为始终生效。例如将：

```json
"when": "workspacePlatform == windows"
```

改为：

```json
"when1": "workspacePlatform == windows"
```

> 有评论建议将所有表达式中的 `workspacePlatform == windows` 替换为 `1`，确保 cppvsdbg 在 Cursor 中可用。

### 7.2 绕过 vsdbg.dll 签名校验

1. 安装 **Hex Editor** 扩展（Cursor 扩展市场搜索 `ms-vscode.hexeditor`）
2. 打开以下文件（**先备份**）：

```
   %USERPROFILE%\.cursor\extensions\ms-vscode.cpptools-<version>-win32-x64\debugAdapters\vsdbg\bin\vsdbg.dll
```

3. `Ctrl + F` → 开启 **Search in Binary Mode** → 搜索十六进制：`488D159E4B0600`
4. 在匹配位置稍下方找到字节序列 `74 15`
5. `Ctrl + Shift + P` → `Hex Editor: Switch Edit Mode` 进入编辑模式
6. 将 `15` 改为 `00`（即 `74 15` → `74 00`）
7. 保存

**版本差异：** 不同 cpptools 版本的偏移不同。例如 `1.27.7` 版本在文件偏移 `0x6B4F6` 处将 `15` 改为 `00`。若搜不到 `488D159E4B0600`，可用 IDA / x64dbg 搜索 `signature` 字符串定位校验逻辑。

### 7.3 禁用扩展自动更新

每次 cpptools 扩展更新后，上述 patch 会被覆盖。建议在 Cursor 扩展设置中对 `ms-vscode.cpptools` **关闭自动更新**，或更新后重新 patch。

### 7.4 验证

1. 用 Cursor 打开项目根目录（与 VSCode 相同的 workspace）
2. 确认 `.vscode/launch.json` 中 `Build && Debug` 配置可见
3. 设置断点 → `F5` 启动调试
4. 应能正常命中断点，Qt 变量通过 natvis 正确显示

配置完成后，**编译（tasks.json）和调试（launch.json）在 VSCode 与 Cursor 中完全一致**，无需维护两套配置。

---

## 八、常见错误排查

### 错误 1：`'cl' 不是内部或外部命令`

**原因**：cl 环境变量未配置。

**解决**：检查 [2.2 节](#22-cl-编译器环境变量) 的 `Path` 和 `INCLUDE`。

---

### 错误 2：`iostream: 不包括路径集`

**原因**：同上，MSVC 头文件路径未找到。

**解决**：补全 `INCLUDE` 环境变量；确认 `c_cpp_properties.json` 中 `compilerPath` 正确。

---

### 错误 3：`无法运行 "rc.exe"`

**原因**：cl 找不到资源编译器。

**解决**：按 [2.3 节](#23-rc-资源配置) 复制 `rc.exe` 到 cl 目录。

---

### 错误 4：clangd 无补全 / 跳转失败（仅 clangd 方案）

**原因**：`compile_commands.json` 不存在或过期。

**解决**：

1. 先执行 `make-debug` 确保 `Makefile.Debug` 已生成
2. 运行 `python build-debug/command.py`
3. 确认项目根目录有 `compile_commands.json`
4. `Ctrl + Shift + P` → `clangd: Restart language server`

---

### 错误 5：Cursor 提示「只能与 Visual Studio Code 一起使用」

**原因**：`vsdbg.dll` 签名校验未绕过。

**解决**：按 [第七章](#七cursor-调试适配) 完成 package.json 修改和 vsdbg.dll patch。

---

## 附录：路径速查

| 组件                      | 路径                                                                    |
| ------------------------- | ----------------------------------------------------------------------- |
| 项目根目录                | `D:\syh\dev\RobotAssist`                                              |
| Debug 构建目录            | `D:\syh\dev\RobotAssist\build-debug`                                  |
| Release 构建目录          | `D:\syh\dev\RobotAssist\build-release`                                |
| compile_commands 生成脚本 | `D:\syh\dev\RobotAssist\build-debug\command.py`（仅 clangd 方案需要） |
| Qt 5.15.2 MSVC            | `C:\Qt\5.15.2\msvc2019_64`                                            |
| qmake                     | `C:\Qt\5.15.2\msvc2019_64\bin\qmake.exe`                              |
| jom                       | `C:\Qt\Tools\QtCreator\bin\jom\jom.exe`                               |
| Qt natvis                 | `C:\Users\suyah\.visualizers\qt5.natvis`                              |
| Win SDK                   | `C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0`         |

---

*Ember*
