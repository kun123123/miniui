# 发布到 GitHub（与 blog 仓库分离）

本地已在 `code/ui` 初始化 Git 并完成首次提交。博客仓库通过 `.gitignore` 忽略 `code/`，两边不再耦合。

## 1. 在 GitHub 新建空仓库

1. 打开 https://github.com/new
2. Repository name：`miniui`
3. 选 **Public**，不要勾选 README / .gitignore（本地已有）
4. 创建

## 2. 推送本地代码

在 **`code/ui`** 目录（或你复制出去的独立文件夹）执行：

```bash
git branch -M main
git remote add origin https://github.com/kun123123/miniui.git
git push -u origin main
```

若 `remote origin` 已存在：

```bash
git remote set-url origin https://github.com/kun123123/miniui.git
git push -u origin main
```

## 3. 可选：迁出 blog 目录

若不想在 blog 项目里保留 `code/ui` 副本：

```bash
# 在 blog 外克隆一份专门开发
cd f:\code
git clone f:\code\blog\code\ui miniui
# 或 push 后：git clone https://github.com/kun123123/miniui.git
```

然后可删除 `blog/code/ui`（删除前确认已 push 成功）。

## 4. 博客文章链接

博客文内已指向：`https://github.com/kun123123/miniui`
