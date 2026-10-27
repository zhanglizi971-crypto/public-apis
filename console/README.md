# API Console 构建说明

`public-apis` 控制台（根目录 `index.html` + `data.json`）由本目录的脚本从上游 `README.md` 解析生成。

## 用法

```powershell
python console/build.py
```

重新生成根目录下的 `data.json`（51 个分类、约 2190 条 API 的结构化数据）。

## 流程

1. 同步上游数据：`git fetch upstream && git rebase upstream/master`
2. 重新解析：`python console/build.py`（输出会打印分类统计，总数异常时断言失败）
3. 本地预览：`python -m http.server 8123` 后访问 `http://127.0.0.1:8123/`
4. 提交推送：`git add README.md data.json index.html && git commit && git push origin master`
5. GitHub Pages 约 1 分钟后自动更新

## 解析规则

- 分类：`### CategoryName` 标题
- 条目：`| [Name](url) | Description | Auth | HTTPS | CORS |` 表格行
- 容错：链接内嵌套括号（如维基百科 URL）、Auth 空值按 `No` 处理

## 本地状态（不写入仓库）

收藏 / 隐藏记录保存在浏览器 localStorage（键 `apiconsole.fav.v1` / `apiconsole.hide.v1`），仅本机生效。