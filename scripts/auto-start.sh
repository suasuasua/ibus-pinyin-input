#!/bin/bash
# IBus 输入法自动启动脚本
# 用于在用户登录时自动启动 IBus 输入法
# 适用于：GNOME 桌面环境
# 
# 使用方法：
#   1. 将此脚本复制到 ~/.config/autostart/
#   2. 设置执行权限：chmod +x ~/.config/autostart/ibus-autostart.desktop
#   3. 或者使用 systemd 用户服务

# 检测桌面环境
if [ -d /usr/share/applications/gnome-shell.desktop ]; then
    DESKTOP_ENV=gnome
elif [ -d /usr/share/applications/xfce.desktop ]; then
    DESKTOP_ENV=xfce
else
    echo "未检测到支持的桌面环境"
    exit 1
fi

# 创建 IBus 自动启动配置
create_autostart_config() {
    local username=$(whoami)
    local autostart_dir="$HOME/.config/autostart"
    
    # 创建 autostart 目录（如不存在）
    mkdir -p "$autostart_dir"
    
    # 生成 .desktop 文件
    cat > "$autostart_dir/ibus-autostart.desktop" << EOF
[Desktop Entry]
Type=Application
Name=IBus Input Method
Comment=自动启动 IBus 输入法框架
Exec=/usr/bin/ibus-daemon -dx
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
Terminal=false
EOF
    
    echo "IBus 自动启动配置已创建：$autostart_dir/ibus-autostart.desktop"
}

# 创建 systemd 用户服务（可选）
create_systemd_user_service() {
    local service_file="$HOME/.config/systemd/user/ibus-daemon.service"
    
    # 创建 systemd 用户服务目录（如不存在）
    mkdir -p "$HOME/.config/systemd/user"
    
    cat > "$service_file" << 'EOF'
[Unit]
Description=IBus Input Method Daemon
After=network.target

[Service]
Type=exec
ExecStart=/usr/bin/ibus-daemon -dx
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF
    
    echo "IBus systemd 用户服务已创建：$service_file"
    echo "启用服务：systemctl --user enable ibus-daemon.service"
    echo "启动服务：systemctl --user start ibus-daemon.service"
}

# 设置环境变量
set_environment() {
    local xdg_config="$HOME/.config"
    
    # 确保 IBus 配置目录存在
    mkdir -p "$xdg_config/ibus"
    mkdir -p "$xdg_config/ibus/prefs"
    
    echo "IBus 配置目录已设置：$xdg_config/ibus"
}

# 主函数
main() {
    echo "=== IBus 自动启动配置 ==="
    
    # 检查 IBus 是否已安装
    if command -v ibus-daemon &> /dev/null; then
        echo "✓ IBus 已安装"
    else
        echo "✗ IBus 未安装，请先安装 IBus"
        exit 1
    fi
    
    # 创建各种配置
    set_environment
    create_autostart_config
    create_systemd_user_service
    
    echo ""
    echo "=== 配置完成 ==="
    echo ""
    echo "提示："
    echo "1. 对于 GNOME 桌面，上述配置将自动启动 IBus"
    echo "2. 使用 'systemctl --user status ibus-daemon.service' 检查服务状态"
    echo "3. 使用 'ibus engine' 查看可用输入法引擎"
    echo "4. 使用 'ibus reset' 重置 IBus 配置"
}

# 执行主函数
main
