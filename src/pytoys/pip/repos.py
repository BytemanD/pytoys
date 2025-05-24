from pytoys.common import user_input

repos = [
    ("官方", "https://pypi.org/simple"),
    ("清华大学", "https://pypi.tuna.tsinghua.edu.cn/simple"),
    ("中国科技大学", "https://pypi.mirrors.ustc.edu.cn/simple"),
    ("阿里云", "https://mirrors.aliyun.com/pypi/simple"),
    ("腾讯", "http://mirrors.cloud.tencent.com/pypi/simple"),
    ("豆瓣", "http://pypi.douban.com/simple"),
]


def select_repos() -> str:
    item = user_input.select_items(
        [{"名称": v1, "地址": v2} for v1, v2 in repos],
        ["名称", "地址"],
    )
    return item.get("地址") if item else ""
