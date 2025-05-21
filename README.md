# pytoys

## 执行

初始化开发环境：
```bash
uv sync
```

执行命令：
```bash
cd src
uv run python -m pytoys.cmd.base
uv run python -m pytoys.cmd.ext
uv run python -m pytoys.cmd.win
```

## 构建

```bash
uv build
```