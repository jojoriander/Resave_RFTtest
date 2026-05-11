# 收藏夹大脑 / AI 收藏整理助手

一个面向小红书收藏场景的 Streamlit 产品 Demo。Demo 使用 mock data 和 scripted AI response，展示 AI 如何把默认收藏夹里的碎片内容整理成「小空间改造灵感」主题收藏夹，并生成总结、子主题标签、行动建议和收藏夹内模糊搜索结果。

## 功能

- 默认收藏夹页：展示混杂收藏笔记和 AI 发现提示
- 一键整理：模拟 AI 识别、聚类、生成主题收藏夹
- 主题收藏夹：展示 37 篇租房/小空间改造相关笔记
- AI 总结：自动总结收藏主题和可执行改造建议
- 子主题标签：床底收纳、不打孔上墙、小空间工位、洗衣机上方、低预算软装、出租屋避坑
- 模糊搜索：可搜索「洗衣机上面怎么利用？」并显示 AI 匹配原因
- 移动端 App 原型风格：390px 宽度、白底、轻量红色点缀、卡片式瀑布流

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

启动后浏览器会打开本地地址，通常是：

```text
http://localhost:8501
```

## 文件结构

```text
.
├── app.py
├── mock_data.py
├── requirements.txt
└── README.md
```

## 部署到 Streamlit Cloud

1. 将本项目上传到 GitHub 仓库。
2. 打开 Streamlit Cloud。
3. 选择该仓库和分支。
4. Main file path 填写：

```text
app.py
```

5. 确认 `requirements.txt` 位于仓库根目录。
6. 点击 Deploy。

## 说明

本 Demo 不接入真实小红书数据，也不调用真实大模型 API。所有收藏笔记、AI 总结、主题标签和搜索匹配原因均为原型演示数据。
