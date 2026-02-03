+++
title = '使用 GitHub Actions 云端编译 MicroPython 固件'
date = 2026-02-03T10:56:39+08:00
draft = false
author = "Bingo"
+++

**前言：** 使用 GitHub Actions 云端编译 MicroPython 固件可以免去在本地搭建复杂的交叉编译环境（尤其是 ESP32 的 ESP-IDF 环境），并且可以确保每次代码更新都能得到干净的固件。
### 1. GitHub Actions简介
GitHub Actions 是 GitHub 提供的自动化工具，由官方或社区维护的虚拟环境（Linux/Windows/macOS 及容器）执行，实现代码编译、测试、发布、通知等自动化工作。

Workflow 是 GitHub Actions 的核心单元，存放在仓库 .github/workflows 目录的 YAML 文件中，由“触发事件 + 一个或多个 job + 每个 job 的多步 step”构成，可定义环境变量、权限、矩阵策略、并发控制及制品缓存，实现完整流水线。

**几个核心概念**

- **Workflow (工作流)：**

    这是自动化的顶级过程。一个仓库可以有多个 Workflow（比如一个用于测试，一个用于发布）。
- **Event (触发事件)：**

    告诉机器人“什么时候干活”。常见的事件有：
    - push: 向仓库推送代码时。
    - pull_request: 提交 PR 时。
    - schedule: 定时触发（像 Crontab 一样，比如每天凌晨 2 点）。
    - workflow_dispatch: 手动点击按钮触发（我们在编译 MicroPython 时用到的就是这个）。
- **Job (任务)：**

    一个 Workflow 由一个或多个 Job 组成。默认情况下，Jobs 是并行运行的。
- **Step (步骤)：**

    每个 Job 包含一系列 Step。步骤可以是运行 shell 命令（run: echo "hello"），也可以是使用别人写好的插件（uses: actions/checkout@v4）。
- **Action (动作)：**

    这是 GitHub Actions 的精华。它是可复用的代码单元。比如“配置 Python 环境”、“登录 Docker Hub”、“上传文件”这些通用操作，你不需要自己写脚本，直接引用社区现成的 Action 即可。
- **Runner (运行器)：**

    执行这些任务的服务器。GitHub 免费提供 Ubuntu (Linux), Windows, macOS 环境。你也可以使用自己的服务器（Self-hosted runner）。
### 2. 准备源码仓库
登录 GitHub，将官方的 [micropython/micropython](https://github.com/micropython/micropython) 仓库 Fork 到自己的账号下。（如果需要编译自定义源码，请确保仓库中包含 MicroPython 源码）。
### 3.创建和编写 Workflow 文件：
在 Fork 的仓库中，创建目录和文件： .github/workflows/build_firmware.yml。

YAML 是一种以“键值+缩进”表达层次结构的人类可读数据格式，后缀.yml或.yaml；在 GitHub Actions 中用于编写 Workflow 文件，支持字符串、列表、字典、多行文本、锚点与合并等语法，简洁直观、易版本控制、与各类编辑器高亮兼容。

**编写编译 ESP32 固件的Workflow文件**

ESP32 需要特定的 ESP-IDF 版本。为了避免环境配置错误，最推荐的方法是直接调用 Espressif 官方提供的 Docker 镜像，里面已经预装了所有工具链。
```Yaml
name: Build ESP32 Firmware

on:
  workflow_dispatch: # 建议手动触发，节省资源

jobs:
  build:
    runs-on: ubuntu-latest
    # 使用 Espressif 官方 Docker 镜像 (包含了对应版本的 IDF)
    # 注意：MicroPython v1.20+ 通常需要 ESP-IDF v5.0+，这里使用 v5.0.2 作为示例
    # 具体版本最好参考 ports/esp32/README.md 中的要求
    container: espressif/idf:v5.0.2

    steps:
      # 1. 拉取代码
      # 由于在 Docker 容器内运行，需要解决 safe.directory 问题
      - name: Checkout Source Code
        uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Fix Git Safe Directory
        run: git config --global --add safe.directory '*'

      # 2. 编译 mpy-cross
      - name: Build mpy-cross
        run: |
          make -C mpy-cross

      # 3. 编译 ESP32 端口
      - name: Build ESP32 Port
        shell: bash
        run: |
          # 这一步是为了加载 ESP-IDF 的环境变量
          . $IDF_PATH/export.sh
          
          cd ports/esp32
          # 初始化该端口所需的子模块（如果需要 berkeley-db-1.xx 等）
          make submodules
          
          # 开始编译 (BOARD 默认为 ESP32_GENERIC，如果是 C3/S3 需要修改)
          make BOARD=ESP32_GENERIC

      # 4. 上传固件
      - name: Upload Firmware
        uses: actions/upload-artifact@v4
        with:
          name: esp32-firmware
          path: ports/esp32/build-ESP32_GENERIC/firmware.bin
```

### 4. 自定义编译 (添加模块)
如果想通过 GitHub Actions 编译包含自定义 C 模块或冻结 Python 脚本的固件，需要修改 Workflow 中的编译命令。

**(1) 添加 Frozen Modules (将 Python 代码编译进固件)**

假设有一个 modules/ 文件夹，里面放了 main.py 或其他库。

在编译命令中指定 FROZEN_MANIFEST。可以创建一个 manifest.py 文件：

```python
# manifest.py 内容示例
include("$(PORT_DIR)/boards/manifest.py")
module("my_script.py", base_path=".") # 假设脚本在仓库根目录
```
然后在 YAML 的编译步骤中修改 make 命令：
```yaml
- name: Build ESP32 Port with Frozen Modules
        shell: bash
        run: |
          . $IDF_PATH/export.sh
          cd ports/esp32
          make submodules
          
          # 修改点在这里：
          # 1. 把 BOARD 改为 ESP32_GENERIC (或者 ESP32_GENERIC_S3, ESP32_GENERIC_C3)
          # 2. FROZEN_MANIFEST 使用相对路径指向仓库根目录的文件
          make BOARD=ESP32_GENERIC FROZEN_MANIFEST=../../manifest.py
```
**注意：** 这里的 ../../manifest.py 是相对于 ports/esp32/ 目录的路径。因为 GitHub Actions 的 checkout 默认结构，回退两层正好是仓库根目录，所以这在 Docker 容器里也是有效的。
**(2)添加 C Modules (User C Modules)**

假设 C 模块在 cmodules/example 目录下。
修改 YAML 中的 make 命令：
```Yaml
- name: Build ESP32 Port with C Modules
        shell: bash
        run: |
          . $IDF_PATH/export.sh
          cd ports/esp32
          make submodules
          
          # 修改点在这里：
          # USER_C_MODULES 指向你的 micropython.cmake 文件
          make BOARD=ESP32_GENERIC USER_C_MODULES=../../cmodules/example/micropython.cmake
```
**(3)完整示例：同时添加 C 模块和 Python 脚本 (针对 ESP32)**

这是一个整合后的 steps 片段，你可以直接替换之前的 "Build ESP32 Port" 步骤：
```yaml
- name: Build ESP32 Port (Custom)
        shell: bash
        run: |
          # 1. 激活 ESP-IDF 环境
          . $IDF_PATH/export.sh
          
          # 2. 进入 esp32 目录
          cd ports/esp32
          
          # 3. 初始化子模块
          make submodules
          
          # 4. 开始编译
          # 请确保 manifest.py 和 cmodules 目录在你的仓库根目录下
          make BOARD=ESP32_GENERIC \
               FROZEN_MANIFEST=../../manifest.py \
               USER_C_MODULES=../../cmodules/example/micropython.cmake
```
### 5. 运行Workflow和下载固件
- 将 .yml 文件推送到 GitHub。
- 进入你的仓库页面，点击顶部的 Actions 标签。
- 点击左侧的 Build Firmware (Workflow 名字)。
- 如果设置了 workflow_dispatch，点击右侧的 Run workflow 按钮。
- 等待运行完成（通常需要 5-10 分钟）。
- 点击运行成功的记录，向下滚动到底部的 Artifacts 区域。
- 下载 esp32-firmware zip 包，解压后即可得到固件。
### 6. 一个构建多个ESP32版本YAML例子
下列YAML例子可以一次性编译多种开发板的固件。
```YAML
# ------------------------------------------------------------------
# 工作流名称：手动触发，为多款 ESP32 板子编译 MicroPython 固件
# ------------------------------------------------------------------
name: ESP32 MicroPython Build

# 触发方式：仅手动
on:
  workflow_dispatch:

# 并发控制：同一分支只保留最新一次运行
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# 全局环境变量
env:
  ESP_IDF_DIR: ${{ github.workspace }}/esp-idf
  MICROPYTHON_DIR: ${{ github.workspace }}/micropython
  ARTIFACTS_DIR: ${{ github.workspace }}/artifacts
  ESP_IDF_VERSION: v5.5.1
  MPY_VERSION: master

jobs:
  # ----------------------------------------------------------------
  # 1) 准备环境：缓存 ESP-IDF 与 MicroPython 源码
  # ----------------------------------------------------------------
  setup-environment:
    runs-on: ubuntu-24.04
    outputs:
      cache-hit: ${{ steps.cache.outputs.cache-hit }}
    steps:
      # 1.1 检出 MicroPython 主仓库（含子模块）
      - name: 检出 MicroPython
        uses: actions/checkout@v4
        with:
          repository: micropython/micropython
          path: micropython
          submodules: recursive

      # 1.2 缓存 ESP-IDF + MicroPython + pip + 工具链
      - name: 缓存 ESP-IDF & MicroPython
        id: cache
        uses: actions/cache@v4
        with:
          path: |
            ${{ env.ESP_IDF_DIR }}
            ~/.espressif/
            ~/.cache/pip/
            ${{ env.MICROPYTHON_DIR }}
          key: mpy-${{ env.MPY_VERSION }}-idf-${{ env.ESP_IDF_VERSION }}
          restore-keys: |
            mpy-${{ env.MPY_VERSION }}-idf-
            mpy-
      # 1.3 仅当缓存未命中时安装系统依赖
      - name: 安装系统依赖（未命中缓存时）
        if: steps.cache.outputs.cache-hit != 'true'
        run: |
          sudo apt-get update -qq
          sudo apt-get install -y \
            git wget flex bison gperf python3 python3-pip python3-venv \
            cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0
      # 1.4 仅当缓存未命中时克隆并安装 ESP-IDF
      - name: 克隆并配置 ESP-IDF（未命中缓存时）
        if: steps.cache.outputs.cache-hit != 'true'
        run: |
          git clone --depth=1 --branch=${{ env.ESP_IDF_VERSION }} \
            https://github.com/espressif/esp-idf.git ${{ env.ESP_IDF_DIR }}
          cd ${{ env.ESP_IDF_DIR }}
          git submodule update --init --recursive --filter=tree:0
          ./install.sh esp32,esp32s3,esp32c3
          source ./export.sh  # 导入 ESP-IDF 的环境变量
  # ----------------------------------------------------------------
  # 2) 并行构建多款固件
  # ----------------------------------------------------------------
  build:
    needs: setup-environment
    runs-on: ubuntu-24.04
    strategy:
      fail-fast: false
      matrix:
        # 列出所有要构建的板子/配置
        include:
          - board: ESP32_GENERIC_S3
            variant: SPIRAM_OCT
            flash_size: 16
          - board: ESP32_GENERIC_C3
            variant: ""
            flash_size: 4
          - board: ESP32_GENERIC
            variant: SPIRAM
            flash_size: 4
          - board: ESP32_GENERIC_P4
            variant: C6_WIFI
            flash_size: 16
          - board: ESP32_GENERIC_P4
            variant: C5_WIFI
            flash_size: 16
          - board: ESP32_GENERIC_C5
            variant: ""
            flash_size: 4

    steps:
      # 2.1 恢复缓存
      - name: 恢复缓存
        uses: actions/cache@v4
        with:
          path: |
            ${{ env.ESP_IDF_DIR }}
            ~/.espressif/
            ~/.cache/pip/
            ${{ env.MICROPYTHON_DIR }}
          key: mpy-${{ env.MPY_VERSION }}-idf-${{ env.ESP_IDF_VERSION }}

      # 2.2 编译固件（BOARD_VARIANT 为空时留空）
      - name: 编译固件
        run: |
          source ${{ env.ESP_IDF_DIR }}/export.sh
          
          cd ${{ env.MICROPYTHON_DIR }}/ports/esp32
          # BOARD_VARIANT 为空时 make 会自动忽略
          make BOARD=${{ matrix.board }} \
               BOARD_VARIANT=${{ matrix.variant }} \
               FLASH_SIZE=${{ matrix.flash_size }}MB \
               -j$(nproc)
      # 2.3 生成友好命名的 bin 文件
      # 命名规则：{board}[_variant]_{flash_size}MB.bin
      - name: 重命名固件
        run: |
          mkdir -p ${{ env.ARTIFACTS_DIR }}
          
          # 拼出构建目录名：board 与可选 variant 用 “-” 连接
          BOARD_NAME="${{ matrix.board }}"
          [[ -n "${{ matrix.variant }}" ]] && BOARD_NAME+="-${{ matrix.variant }}"
          # 计算固件真正所在路径
          FW_PATH="${{ env.MICROPYTHON_DIR }}/ports/esp32/build-${BOARD_NAME}/firmware.bin"  
        
          OUT_NAME="${{ matrix.board }}${{ matrix.variant && format('_{0}', matrix.variant) || '' }}_${{ matrix.flash_size }}MB.bin"
          # 如果固件存在则复制并重命名；不存在则报错退出
          if [[ -f "$FW_PATH" ]]; then          
            cp "$FW_PATH" "$ARTIFACTS_DIR/$OUT_NAME"
          else
            echo "Firmware not found at $FW_PATH"
            exit 1
          fi
      # 2.4 上传构建产物
      - name: 上传固件到 Actions
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.board }}${{ matrix.variant && format('_{0}', matrix.variant) || '' }}-${{ matrix.flash_size }}MB
          path: ${{ env.ARTIFACTS_DIR }}/*.bin
```