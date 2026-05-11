from __future__ import annotations

import time
from html import escape
from time import monotonic

import streamlit as st

from mock_data import POSTS, SUBTOPICS, get_default_posts, get_theme_posts, search_theme_posts


SHANGHAI_SUBTOPICS = ["全部", "美食", "活动", "景点攻略", "Citywalk", "住宿交通"]

SHANGHAI_POSTS = [
    {
        "post_id": "sh_001",
        "title": "上海三天两晚不绕路路线",
        "cover_text": "外滩 / 武康路 / 迪士尼",
        "tags": ["景点攻略", "Citywalk"],
        "author": "沪上周末计划",
        "view_after_save_count": 12,
        "subtopics": ["景点攻略", "Citywalk"],
    },
    {
        "post_id": "sh_002",
        "title": "第一次来上海必吃本帮菜清单",
        "cover_text": "红烧肉、蟹粉面、排骨年糕",
        "tags": ["美食"],
        "author": "爱吃小笼包",
        "view_after_save_count": 9,
        "subtopics": ["美食"],
    },
    {
        "post_id": "sh_003",
        "title": "武康路到安福路 Citywalk",
        "cover_text": "梧桐树下慢慢逛",
        "tags": ["Citywalk", "景点攻略"],
        "author": "走路去看展",
        "view_after_save_count": 7,
        "subtopics": ["Citywalk", "景点攻略"],
    },
    {
        "post_id": "sh_004",
        "title": "上海近期展览和周末活动合集",
        "cover_text": "展览 / 市集 / Livehouse",
        "tags": ["活动"],
        "author": "周末去哪儿",
        "view_after_save_count": 10,
        "subtopics": ["活动"],
    },
    {
        "post_id": "sh_005",
        "title": "住人民广场还是静安寺更方便",
        "cover_text": "地铁换乘和预算对比",
        "tags": ["住宿交通"],
        "author": "旅行住宿研究员",
        "view_after_save_count": 6,
        "subtopics": ["住宿交通"],
    },
    {
        "post_id": "sh_006",
        "title": "外滩夜景最佳拍照机位",
        "cover_text": "不用人挤人的角度",
        "tags": ["景点攻略"],
        "author": "拍照不排队",
        "view_after_save_count": 8,
        "subtopics": ["景点攻略"],
    },
    {
        "post_id": "sh_007",
        "title": "南京西路咖啡甜品地图",
        "cover_text": "逛街中途补能",
        "tags": ["美食", "Citywalk"],
        "author": "咖啡续命中",
        "view_after_save_count": 5,
        "subtopics": ["美食", "Citywalk"],
    },
    {
        "post_id": "sh_008",
        "title": "迪士尼一天怎么玩不崩溃",
        "cover_text": "预约、排队、烟花攻略",
        "tags": ["景点攻略", "活动"],
        "author": "乐园攻略本",
        "view_after_save_count": 11,
        "subtopics": ["景点攻略", "活动"],
    },
    {
        "post_id": "sh_009",
        "title": "上海地铁沿线住宿避坑",
        "cover_text": "别只看直线距离",
        "tags": ["住宿交通"],
        "author": "不想拖箱子",
        "view_after_save_count": 4,
        "subtopics": ["住宿交通"],
    },
    {
        "post_id": "sh_010",
        "title": "巨鹿路夜晚小酒馆收藏",
        "cover_text": "微醺但不踩雷",
        "tags": ["美食", "活动"],
        "author": "夜上海散步",
        "view_after_save_count": 6,
        "subtopics": ["美食", "活动"],
    },
]

AI_PROMPTS = [
    {
        "theme_id": "rent",
        "count": 37,
        "theme": "租房/小空间改造",
        "title": "小空间改造灵感",
        "description": "要不要帮你整理成一个主题收藏夹？不是帮你多收藏，而是帮你真正用起来。",
    },
    {
        "theme_id": "shanghai",
        "count": 10,
        "theme": "上海旅游",
        "title": "上海旅游灵感",
        "description": "要不要帮你整理成一个主题收藏夹？把路线、美食和活动先归好类，出发前更好查。",
    },
]

BASE_NOTE_COUNT = 486
ALBUM_NOTE_COUNTS = {
    "rent": 37,
    "shanghai": 10,
}
ALBUM_SOURCE_THEMES = {
    "rent": "租房/小空间改造",
    "shanghai": "上海旅游",
}


st.set_page_config(
    page_title="收藏夹大脑 / AI 收藏整理助手",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)


CSS = """
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC",
        "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

* {
    box-sizing: border-box;
}

.stApp {
    background:
        radial-gradient(circle at 50% -10%, rgba(255, 255, 255, 0.92), transparent 34%),
        #d9dde4;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    min-height: 100vh;
    overflow: hidden;
}

[data-testid="stMain"] {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px 0;
}

.block-container {
    width: min(390px, calc(100vw - 48px), calc(46.21vh - 22.18px)) !important;
    height: min(844px, calc(100vh - 48px), calc(216.41vw - 103.88px));
    max-width: none !important;
    min-height: 0;
    margin: 0 auto !important;
    padding: 0 !important;
    aspect-ratio: 390 / 844;
    background: #ffffff;
    color: #222222;
    border: 10px solid #111318;
    border-radius: 42px;
    box-shadow: 0 28px 80px rgba(20, 26, 36, 0.28);
    position: relative;
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: none;
}

.block-container::-webkit-scrollbar {
    display: none;
}

.block-container::before {
    content: "";
    position: sticky;
    top: 8px;
    left: 50%;
    transform: translateX(-50%);
    display: block;
    width: 118px;
    height: 27px;
    margin: 0 auto -27px;
    border-radius: 0 0 18px 18px;
    background: #111318;
    z-index: 60;
    pointer-events: none;
}

@media (max-width: 430px) {
    .block-container {
        width: 100vw !important;
        height: 100vh;
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
        border: 0;
        border-radius: 0;
        box-shadow: none;
    }

    .block-container::before {
        display: none;
    }
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeader"],
#MainMenu,
footer {
    display: none !important;
}

/* The phone-shell is always narrower than Streamlit's 640px column-stack */
/* breakpoint, so we force every column to keep its requested flex basis */
/* without min-width stacking. */
.block-container [data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap;
}

.block-container [data-testid="stColumn"] {
    min-width: 0 !important;
}

.phone-shell {
    display: contents;
}

.phone-shell::-webkit-scrollbar {
    display: none;
}

.phone-shell::before {
    display: none;
}

.safe-top {
    height: 28px;
    background: #ffffff;
}

.topbar {
    position: sticky;
    top: 0;
    z-index: 20;
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid #f1f1f1;
    padding: 14px 20px 12px;
}

/* collection-tabs is an empty anchor div produced via st.markdown. */
/* Streamlit emits each markdown / widget as a sibling stElementContainer, */
/* so we use :has() to find the anchor's container and select its next */
/* sibling — which is the stLayoutWrapper that holds the actual tab columns. */
.collection-tabs {
    height: 0;
    overflow: hidden;
}

[data-testid="stElementContainer"]:has(> div > div > div > .collection-tabs) + [data-testid="stLayoutWrapper"] {
    border-bottom: 1px solid #eeeeee;
    background: #ffffff;
    padding: 0 20px;
    margin: 0 0 4px;
}

[data-testid="stElementContainer"]:has(> div > div > div > .collection-tabs) + [data-testid="stLayoutWrapper"] [data-testid="stHorizontalBlock"] {
    gap: 0;
    flex-wrap: nowrap;
}

[data-testid="stElementContainer"]:has(> div > div > div > .collection-tabs) + [data-testid="stLayoutWrapper"] [data-testid="stColumn"] {
    display: flex;
    justify-content: center;
    align-items: center;
    min-width: 0 !important;
    flex: 1 1 50% !important;
}

.tab-label {
    padding: 10px 0 8px;
    text-align: center;
    font-size: 14px;
    font-weight: 750;
    color: #222222;
}

.tab-label::after {
    content: "";
    display: block;
    width: 28px;
    height: 3px;
    margin: 7px auto 0;
    border-radius: 999px;
    background: #ff2d55;
}

[data-testid="stElementContainer"]:has(> div > div > div > .collection-tabs) + [data-testid="stLayoutWrapper"] div.stButton > button {
    width: auto;
    min-height: 36px;
    padding: 10px 0 8px;
    border: 0 !important;
    background: transparent !important;
    color: #8f8f8f;
    font-size: 14px;
    font-weight: 750;
    box-shadow: none !important;
}

[data-testid="stElementContainer"]:has(> div > div > div > .collection-tabs) + [data-testid="stLayoutWrapper"] div.stButton > button:hover {
    color: #222222;
}

.profile-row {
    display: flex;
    align-items: center;
    gap: 10px;
}

.avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6b7a, #ffd7dd);
    display: grid;
    place-items: center;
    color: white;
    font-weight: 800;
    font-size: 15px;
}

.title-block h1 {
    margin: 0;
    font-size: 20px;
    line-height: 1.2;
    letter-spacing: 0;
}

.title-block p,
.muted {
    margin: 3px 0 0;
    color: #8b8b8b;
    font-size: 12px;
}

.back-row {
    display: flex;
    align-items: center;
    gap: 8px;
}

.back-symbol {
    width: 30px;
    height: 30px;
    border-radius: 999px;
    display: grid;
    place-items: center;
    background: #f7f7f7;
    color: #333333;
    font-size: 20px;
}

.theme-back [data-testid="stHorizontalBlock"] {
    gap: 8px;
}

.theme-back div.stButton > button {
    width: 28px;
    min-width: 28px;
    height: 28px;
    min-height: 28px;
    padding: 0;
    border-radius: 999px;
    border: 0;
    background: #f7f7f7;
    color: #333333;
    font-size: 18px;
    line-height: 1;
}

.theme-back div.stButton > button:hover {
    border: 0;
    background: #eeeeee;
    color: #333333;
}

.content {
    padding: 0 20px 28px;
}

.notes-count {
    margin: 6px 20px 8px;
    color: #8b8b8b;
    font-size: 10px;
    line-height: 1.2;
}

.value-banner-wrap {
    margin: 4px 0 14px;
    position: relative;
}

.value-banner {
    position: relative;
    border-radius: 14px;
    padding: 12px 38px 12px 46px;
    background:
        radial-gradient(circle at 88% -10%, rgba(255, 215, 221, 0.95), transparent 55%),
        linear-gradient(135deg, #fff4f6 0%, #ffffff 78%);
    border: 1px solid #ffe0e4;
    box-shadow: 0 6px 16px rgba(255, 45, 85, 0.06);
    overflow: hidden;
}

.value-banner::before {
    content: "✨";
    position: absolute;
    left: 14px;
    top: 13px;
    width: 22px;
    height: 22px;
    display: grid;
    place-items: center;
    border-radius: 8px;
    background: #ff2d55;
    color: #ffffff;
    font-size: 12px;
    line-height: 1;
}

.value-banner h4 {
    margin: 0 0 3px;
    font-size: 13px;
    font-weight: 800;
    color: #1f1f24;
    line-height: 1.3;
}

.value-banner p {
    margin: 0;
    font-size: 11px;
    color: #777777;
    line-height: 1.45;
}

/* The dismiss button is its own sibling stElementContainer; pull it up */
/* and overlay it on the banner's top-right via :has() + negative margin. */
.value-banner-close {
    height: 0;
    overflow: hidden;
}

[data-testid="stElementContainer"]:has(> div > div > div > .value-banner-close) + [data-testid="stElementContainer"] {
    position: relative;
    width: 28px;
    margin-left: auto;
    margin-right: 6px;
    margin-top: -92px;
    margin-bottom: 64px;
    z-index: 5;
}

[data-testid="stElementContainer"]:has(> div > div > div > .value-banner-close) + [data-testid="stElementContainer"] div.stButton > button {
    width: 24px;
    min-width: 24px;
    height: 24px;
    min-height: 24px;
    padding: 0;
    border-radius: 999px;
    border: 0 !important;
    background: transparent !important;
    color: #b0b0b0;
    font-size: 14px;
    line-height: 1;
    box-shadow: none !important;
}

[data-testid="stElementContainer"]:has(> div > div > div > .value-banner-close) + [data-testid="stElementContainer"] div.stButton > button:hover {
    background: rgba(255, 45, 85, 0.08) !important;
    color: #ff2d55;
    border: 0 !important;
}

.album-rail-wrap {
    margin: -2px 0 12px;
}

.album-rail-head {
    margin: 0;
    line-height: 1.2;
}

.album-rail-head h5 {
    margin: 0 0 2px;
    font-size: 13px;
    font-weight: 800;
    color: #1f1f24;
    letter-spacing: 0;
}

.album-rail-head span {
    font-size: 10px;
    color: #999999;
}

.album-rail-scroll {
    margin: 0 -20px;
    padding: 2px 20px 4px;
    overflow-x: auto;
    scrollbar-width: none;
}

.album-rail-scroll::-webkit-scrollbar {
    display: none;
}

.album-rail {
    display: flex;
    gap: 8px;
    width: max-content;
}

.album-rail-card {
    flex: 0 0 auto;
    width: 138px;
    border-radius: 12px;
    border: 1px solid #ffe0e4;
    background:
        radial-gradient(circle at 86% -4%, rgba(255, 215, 221, 0.7), transparent 50%),
        linear-gradient(135deg, #fff7f8 0%, #ffffff 70%);
    padding: 10px 12px 11px;
    position: relative;
    overflow: hidden;
}

.album-rail-card::before {
    content: "◈";
    position: absolute;
    top: 9px;
    right: 11px;
    font-size: 11px;
    color: #ff2d55;
    opacity: 0.65;
}

.album-rail-card .rail-tag {
    display: inline-block;
    font-size: 9px;
    font-weight: 700;
    color: #ff2d55;
    background: rgba(255, 45, 85, 0.10);
    padding: 2px 6px;
    border-radius: 999px;
    margin-bottom: 7px;
    letter-spacing: 0.3px;
}

.album-rail-card .rail-title {
    font-size: 13px;
    font-weight: 800;
    color: #222222;
    line-height: 1.25;
    margin-bottom: 4px;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.album-rail-card .rail-meta {
    font-size: 10px;
    color: #888888;
    line-height: 1.2;
}

.album-rail-head .rail-cta div.stButton > button {
    min-height: 22px;
    padding: 2px 10px;
    font-size: 10px;
    font-weight: 700;
    border-radius: 999px;
    border: 1px solid #ffe0e4;
    background: #ffffff;
    color: #ff2d55;
}

.album-rail-head .rail-cta div.stButton > button:hover {
    border-color: #ff2d55;
    background: #ff2d55;
    color: #ffffff;
}

.album-list {
    display: grid;
    gap: 10px;
}

.album-create,
.album-card {
    display: block;
    text-decoration: none;
    color: inherit;
    background: #ffffff;
    border: 1px solid #eeeeee;
    border-radius: 12px;
    padding: 14px;
}

.album-create {
    display: flex;
    align-items: center;
    gap: 12px;
}

.album-create-icon {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    background: #e7f5ff;
    color: #58b8ff;
    font-size: 24px;
    font-weight: 900;
}

.album-create-title {
    flex: 1;
    font-size: 17px;
    font-weight: 800;
}

.album-chevron {
    color: #aaaaaa;
    font-size: 28px;
}

.album-head {
    display: flex;
    align-items: start;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 14px;
}

.album-title {
    margin: 0 0 5px;
    font-size: 18px;
    font-weight: 850;
    line-height: 1.25;
}

.album-count {
    margin: 0;
    color: #8e8e8e;
    font-size: 14px;
}

.album-preview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
}

.album-thumb {
    min-height: 72px;
    border-radius: 8px;
    padding: 7px;
    display: flex;
    align-items: end;
    color: rgba(43, 43, 43, 0.86);
    font-size: 9px;
    line-height: 1.15;
    font-weight: 850;
    overflow: hidden;
    background:
        radial-gradient(circle at 20% 18%, rgba(255, 45, 85, 0.18), transparent 30%),
        linear-gradient(135deg, #fff0f2, #f8f8f8);
}

.album-thumb.alt-1 { background: linear-gradient(135deg, #f8f1e9, #fff9f2); }
.album-thumb.alt-2 { background: linear-gradient(135deg, #eef7f5, #fbfffd); }
.album-thumb.alt-3 { background: linear-gradient(135deg, #f2f0ff, #ffffff); }

.album-open-hitbox {
    position: relative;
    z-index: 8;
    height: 154px;
    margin-top: -154px;
    margin-bottom: 10px;
}

.album-open-hitbox div.stButton > button {
    width: 100%;
    height: 154px;
    min-height: 154px;
    padding: 0;
    border: 0;
    background: transparent !important;
    color: transparent !important;
    box-shadow: none !important;
    cursor: pointer;
}

.album-open-hitbox div.stButton > button:hover,
.album-open-hitbox div.stButton > button:focus,
.album-open-hitbox div.stButton > button:active {
    border: 0;
    background: transparent !important;
    color: transparent !important;
    box-shadow: none !important;
}

.value-line {
    margin: 2px 0 12px;
    color: #666666;
    font-size: 13px;
}

.ai-card {
    border: 1px solid #ffe0e4;
    border-radius: 18px;
    padding: 16px;
    background: linear-gradient(135deg, #fff7f8 0%, #ffffff 70%);
    box-shadow: 0 8px 22px rgba(255, 45, 85, 0.08);
    margin-bottom: 0;
    position: relative;
    z-index: 2;
}

.ai-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 9px;
    border-radius: 999px;
    background: #ff2d55;
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
}

.ai-card h2 {
    margin: 11px 0 7px;
    font-size: 18px;
    line-height: 1.28;
    letter-spacing: 0;
}

.ai-card p {
    margin: 0;
    color: #555555;
    line-height: 1.55;
    font-size: 13px;
}

.ai-stack {
    position: relative;
    margin-bottom: 14px;
}

.ai-stack.has-next::before,
.ai-stack.has-next::after {
    content: "";
    position: absolute;
    left: 14px;
    right: 14px;
    height: 100%;
    border: 1px solid #ffe8eb;
    border-radius: 18px;
    background: #ffffff;
    box-shadow: 0 8px 18px rgba(255, 45, 85, 0.05);
}

.ai-stack.has-next::before {
    top: 9px;
    z-index: 1;
    transform: rotate(-1.2deg);
}

.ai-stack.has-next::after {
    top: 17px;
    left: 28px;
    right: 28px;
    z-index: 0;
    opacity: 0.72;
    transform: rotate(1.1deg);
}

.ai-card-actions {
    position: relative;
    z-index: 3;
    margin-top: -1px;
    padding: 12px 0 0;
    background: #ffffff;
    border: 1px solid #ffe0e4;
    border-top: 0;
    border-radius: 0 0 18px 18px;
}

.ai-button-row {
    margin-top: -15px;
    margin-bottom: 14px;
    padding: 12px 0 0;
    position: relative;
    z-index: 4;
}

.ai-button-row [data-testid="stHorizontalBlock"] {
    gap: 8px;
}

.metrics-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 12px 0;
}

.success-card-wrap {
    position: relative;
}

.success-card-actions {
    height: 0;
    overflow: hidden;
}

/* Overlay the dismiss button onto the success card's top-right via */
/* the same sibling-overlap technique used for the value-banner close. */
[data-testid="stElementContainer"]:has(> div > div > div > .success-card-actions) + [data-testid="stElementContainer"] {
    position: relative;
    width: 30px;
    margin-left: auto;
    margin-right: 6px;
    margin-top: 8px;
    margin-bottom: -38px;
    z-index: 5;
}

[data-testid="stElementContainer"]:has(> div > div > div > .success-card-actions) + [data-testid="stElementContainer"] div.stButton > button {
    width: 26px;
    min-width: 26px;
    height: 26px;
    min-height: 26px;
    padding: 0;
    border-radius: 999px;
    border: 1px solid #eeeeee !important;
    background: #ffffff !important;
    color: #999999;
    font-size: 13px;
    box-shadow: none !important;
}

[data-testid="stElementContainer"]:has(> div > div > div > .success-card-actions) + [data-testid="stElementContainer"] div.stButton > button:hover {
    border-color: #ff2d55 !important;
    color: #ff2d55;
    background: #ffffff !important;
}

.metric {
    background: #fafafa;
    border: 1px solid #eeeeee;
    border-radius: 14px;
    padding: 12px;
}

.metric strong {
    display: block;
    font-size: 22px;
    color: #ff2d55;
    line-height: 1;
}

.metric span {
    color: #777777;
    font-size: 12px;
}

.section-title {
    display: flex;
    align-items: end;
    justify-content: space-between;
    margin: 16px 2px 10px;
}

.section-title h3 {
    margin: 0;
    font-size: 15px;
}

.section-title span {
    color: #999999;
    font-size: 12px;
}

.masonry {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px 7px;
}

.note-card {
    display: block;
    width: 100%;
    border-radius: 8px;
    overflow: hidden;
    background: #ffffff;
    border: 1px solid #f0f0f0;
    box-shadow: none;
    line-height: normal;
}

.cover {
    min-height: 128px;
    padding: 10px;
    display: flex;
    align-items: end;
    color: rgba(43, 43, 43, 0.88);
    font-weight: 900;
    line-height: 1.18;
    font-size: 14px;
    text-shadow: 0 1px 0 rgba(255, 255, 255, 0.48);
    background:
        radial-gradient(circle at 18% 16%, rgba(255, 45, 85, 0.22), transparent 30%),
        radial-gradient(circle at 82% 18%, rgba(255, 190, 95, 0.22), transparent 28%),
        linear-gradient(135deg, #ffe5eb 0%, #fff7f8 48%, #f7f7f7 100%);
}

.note-card:nth-child(3n + 1) .cover { min-height: 148px; }
.note-card:nth-child(3n + 2) .cover { min-height: 116px; }
.note-card:nth-child(3n) .cover { min-height: 168px; }

.cover.alt-1 {
    background:
        radial-gradient(circle at 74% 24%, rgba(160, 105, 60, 0.20), transparent 26%),
        linear-gradient(135deg, #f7eadc, #fff8ef);
}
.cover.alt-2 {
    background:
        radial-gradient(circle at 26% 26%, rgba(76, 170, 140, 0.20), transparent 30%),
        linear-gradient(135deg, #e7f6f3, #fbfffd);
}
.cover.alt-3 {
    background:
        radial-gradient(circle at 78% 30%, rgba(120, 105, 210, 0.18), transparent 30%),
        linear-gradient(135deg, #eeeaff, #ffffff);
}
.cover.alt-4 {
    background:
        radial-gradient(circle at 24% 26%, rgba(255, 120, 92, 0.18), transparent 30%),
        linear-gradient(135deg, #fff0ea, #fffaf0);
}

.note-body {
    padding: 8px 8px 9px;
}

.note-title {
    margin: 0 0 8px;
    font-size: 13px;
    line-height: 1.34;
    font-weight: 800;
    color: #303030;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.note-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #8e8e8e;
    font-size: 11px;
    white-space: nowrap;
}

.author-avatar {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    flex: 0 0 auto;
    display: grid;
    place-items: center;
    color: #ffffff;
    font-size: 10px;
    font-weight: 800;
    background: linear-gradient(135deg, #ff758c, #9b7cff);
}

.author-name {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
}

.like-count {
    flex: 0 0 auto;
    color: #737373;
    font-size: 12px;
}

.like-count::before {
    content: "♡";
    margin-right: 3px;
    color: #ff2d55;
    font-size: 14px;
    line-height: 1;
}

.summary-card {
    border-radius: 18px;
    border: 1px solid #eeeeee;
    background: #ffffff;
    padding: 15px;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
}

.summary-card h3 {
    margin: 0 0 8px;
    font-size: 15px;
}

.summary-card ul,
.summary-card ol {
    margin: 7px 0 10px 20px;
    padding: 0;
    color: #555555;
    font-size: 13px;
    line-height: 1.52;
}

.summary-card p {
    color: #555555;
    font-size: 13px;
    line-height: 1.55;
    margin: 0 0 8px;
}

.chip-scroll {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding: 2px 0 12px;
    scrollbar-width: none;
    white-space: nowrap;
}

.chip-scroll::-webkit-scrollbar {
    display: none;
}

.chip-strip {
    margin: 4px 0 12px;
    display: flex;
    gap: 6px;
    overflow-x: auto;
    scrollbar-width: none;
}

.chip-strip::-webkit-scrollbar {
    display: none;
}

.topic-chip {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    min-height: 26px;
    padding: 0 9px;
    border-radius: 999px;
    border: 1px solid #eeeeee;
    background: #ffffff;
    color: #333333;
    font-size: 10px;
    line-height: 1;
    font-weight: 700;
    text-decoration: none;
    white-space: nowrap;
}

.topic-chip.active {
    background: #ff2d55;
    border-color: #ff2d55;
    color: #ffffff;
}

[data-testid="stPills"] {
    margin: 4px 0 12px;
    overflow-x: auto;
    scrollbar-width: none;
}

[data-testid="stPills"]::-webkit-scrollbar {
    display: none;
}

[data-testid="stPills"] [role="group"] {
    flex-wrap: nowrap;
    width: max-content;
    min-width: 100%;
}

[data-testid="stPills"] button {
    min-height: 26px;
    padding: 0 9px;
    font-size: 10px;
    font-weight: 700;
    white-space: nowrap;
}

div.stButton > button {
    border-radius: 999px;
    border: 1px solid #eeeeee;
    background: #ffffff;
    color: #333333;
    min-height: 32px;
    font-weight: 700;
    font-size: 11px;
    box-shadow: none;
}

div.stButton > button:hover {
    border-color: #ff2d55;
    color: #ff2d55;
}

div.stButton > button[kind="primary"] {
    background: #ff2d55;
    color: #ffffff;
    border-color: #ff2d55;
}

div.stButton > button[kind="primary"]:hover {
    color: #ffffff;
}

.primary-action div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    background: #ff2d55;
    color: #ffffff;
    border-color: #ff2d55;
    width: 100%;
}

div[data-testid="stFormSubmitButton"] > button:hover {
    color: #ffffff;
}

.active-chip {
    display: inline-flex;
    padding: 8px 12px;
    border-radius: 999px;
    background: #ff2d55;
    color: #ffffff;
    font-size: 13px;
    font-weight: 750;
    margin: 0 0 10px;
}

.search-box {
    margin: 10px 0 14px;
}

.search-box [data-testid="stHorizontalBlock"] {
    gap: 6px;
    align-items: center;
}

[data-testid="stTextInput"] input {
    border-radius: 999px;
    border-color: #eeeeee;
    background: #ffffff;
    font-size: 11px;
    min-height: 32px;
}

.search-box div.stButton > button {
    width: 32px;
    min-width: 32px;
    height: 32px;
    min-height: 32px;
    padding: 0;
    font-size: 14px;
    border-color: #ff2d55;
    background: #ff2d55;
    color: #ffffff;
}

.search-box div.stButton > button:hover {
    color: #ffffff;
    border-color: #ff2d55;
}

.search-suggest {
    margin: -6px 0 12px;
}

.search-suggest-label {
    margin: 0 0 6px;
    font-size: 10px;
    color: #999999;
    line-height: 1;
}

.search-suggest [data-testid="stHorizontalBlock"] {
    gap: 6px;
}

.search-suggest div.stButton > button {
    width: 100%;
    min-height: 26px;
    padding: 4px 9px;
    font-size: 10px;
    font-weight: 600;
    color: #555555;
    background: #fafafa;
    border: 1px solid #eeeeee;
    border-radius: 999px;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.search-suggest div.stButton > button:hover {
    background: #fff7f8;
    border-color: #ffb8c4;
    color: #ff2d55;
}

.reason {
    border-left: 3px solid #ff2d55;
    background: #fff7f8;
    padding: 10px 12px;
    border-radius: 12px;
    color: #555555;
    font-size: 12px;
    line-height: 1.5;
    margin: 10px 0 12px;
}

.loading-wrap {
    width: 100%;
    min-height: calc(100% - 86px);
    background: #ffffff;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
    padding: 48px 32px 32px;
}

.loading-wrap::before {
    display: none;
}

.loading-logo {
    width: 54px;
    height: 54px;
    border-radius: 18px;
    background: #ff2d55;
    color: #ffffff;
    display: grid;
    place-items: center;
    font-size: 24px;
    font-weight: 900;
    margin-bottom: 18px;
}

.loading-step {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 0;
    font-size: 14px;
    color: #444444;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #ff2d55;
    box-shadow: 0 0 0 5px rgba(255, 45, 85, 0.12);
}

.bottom-nav {
    position: sticky;
    bottom: 0;
    width: 100%;
    max-width: 100%;
    height: 64px;
    background: rgba(255, 255, 255, 0.98);
    border-top: 1px solid #eeeeee;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    align-items: center;
    z-index: 30;
}

.nav-item {
    text-align: center;
    font-size: 11px;
    color: #999999;
}

.nav-item b {
    display: block;
    font-size: 20px;
    line-height: 1.2;
    color: #b7b7b7;
}

.nav-item.active {
    color: #ff2d55;
    font-weight: 800;
}

.nav-item.active b {
    color: #ff2d55;
}

@media (max-width: 430px) {
    [data-testid="stMain"] {
        padding: 0;
    }

    .block-container {
        width: 100vw !important;
        height: 100vh;
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
        border: 0;
        border-radius: 0;
        box-shadow: none;
    }

    .phone-shell,
    .loading-wrap {
        width: 100vw;
        border: 0;
        border-radius: 0;
        box-shadow: none;
    }

    .phone-shell::before,
    .loading-wrap::before {
        display: none;
    }

    .safe-top {
        height: 14px;
    }
}
</style>
"""


st.markdown(CSS, unsafe_allow_html=True)


def init_state() -> None:
    defaults = {
        "page": "default",
        "selected_subtopic": "全部",
        "search_query": "",
        "last_search": "",
        "ai_prompt_index": 0,
        "target_theme": "rent",
        "main_tab": "notes",
        "generated_albums": [],
        "theme_success_shown_at": None,
        "theme_success_theme": None,
        "theme_success_dismissed": False,
        "value_banner_dismissed": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def note_card_html(post: dict, index: int = 0) -> str:
    cover_text = escape(post["cover_text"])
    title = escape(post["title"])
    author = escape(post["author"])
    avatar_text = escape(author[:1] or "作")
    like_count = post["view_after_save_count"] * 357 + index * 86
    likes = f"{like_count / 10000:.1f}万".replace(".0", "") if like_count >= 10000 else str(like_count)
    return (
        f'<article class="note-card">'
        f'<div class="cover alt-{index % 5}">{cover_text}</div>'
        f'<div class="note-body">'
        f'<p class="note-title">{title}</p>'
        f'<div class="note-meta">'
        f'<span class="author-avatar">{avatar_text}</span>'
        f'<span class="author-name">{author}</span>'
        f'<span class="like-count">{likes}</span>'
        f'</div>'
        f'</div>'
        f'</article>'
    )


def note_grid(posts: list[dict]) -> None:
    cards = "".join(note_card_html(post, index) for index, post in enumerate(posts))
    st.markdown(f'<div class="masonry">{cards}</div>', unsafe_allow_html=True)


def album_ids() -> list[str]:
    ids = st.session_state.generated_albums
    return [theme_id for theme_id in ids if theme_id in {"rent", "shanghai"}]


def add_generated_album(theme_id: str) -> None:
    albums = list(st.session_state.generated_albums)
    if theme_id not in albums:
        albums.append(theme_id)
    st.session_state.generated_albums = albums


def unclassified_note_count() -> int:
    organized_count = sum(ALBUM_NOTE_COUNTS.get(theme_id, 0) for theme_id in album_ids())
    return max(BASE_NOTE_COUNT - organized_count, 0)


def get_unclassified_default_posts() -> list[dict]:
    excluded_themes = {
        ALBUM_SOURCE_THEMES[theme_id]
        for theme_id in album_ids()
        if theme_id in ALBUM_SOURCE_THEMES
    }
    return [
        post
        for post in get_default_posts()
        if post.get("theme") not in excluded_themes
    ]


def theme_config_for(theme_id: str) -> dict:
    previous = st.session_state.target_theme
    st.session_state.target_theme = theme_id
    config = current_theme_config()
    st.session_state.target_theme = previous
    return config


def render_collection_tabs() -> None:
    active = st.session_state.main_tab
    st.markdown('<div class="collection-tabs">', unsafe_allow_html=True)
    notes_col, albums_col = st.columns(2)
    with notes_col:
        if active == "notes":
            st.markdown('<div class="tab-label">笔记</div>', unsafe_allow_html=True)
        elif st.button("笔记", key="tab_notes", use_container_width=True):
            st.session_state.main_tab = "notes"
            st.rerun()
    with albums_col:
        if active == "albums":
            st.markdown('<div class="tab-label">专辑</div>', unsafe_allow_html=True)
        elif st.button("专辑", key="tab_albums", use_container_width=True):
            st.session_state.main_tab = "albums"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def album_card_html(theme_id: str) -> str:
    config = theme_config_for(theme_id)
    thumbs = "".join(
        f'<div class="album-thumb alt-{index % 4}">{escape(post["cover_text"])}</div>'
        for index, post in enumerate(config["posts"][:4])
    )
    return (
        f'<div class="album-card">'
        f'<div class="album-head">'
        f'<div><p class="album-title">{escape(config["title"])}</p>'
        f'<p class="album-count">笔记 · {config["count"]}</p></div>'
        f'</div>'
        f'<div class="album-preview">{thumbs}</div>'
        f'</div>'
    )


def render_albums_page() -> None:
    ids = album_ids()
    if not ids:
        st.markdown(
            '<div class="summary-card"><h3>还没有创建专辑</h3>'
            '<p>回到「笔记」页点击“帮我整理”生成专辑再回来看看吧。</p></div>',
            unsafe_allow_html=True,
        )
        return

    for theme_id in ids:
        st.markdown(album_card_html(theme_id), unsafe_allow_html=True)
        st.markdown('<div class="album-open-hitbox">', unsafe_allow_html=True)
        if st.button("打开专辑", key=f"open_album_{theme_id}", use_container_width=True):
            st.session_state.target_theme = theme_id
            st.session_state.page = "theme"
            st.session_state.selected_subtopic = "全部"
            st.session_state.last_search = ""
            st.session_state.search_query = ""
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def current_theme_config() -> dict:
    if st.session_state.target_theme == "shanghai":
        return {
            "theme_id": "shanghai",
            "title": "上海旅游灵感",
            "subtitle": "10 篇笔记 · AI 已整理",
            "created_title": "已为你创建主题收藏夹：上海旅游灵感",
            "done_text": "AI 已帮你识别路线、美食、活动和住宿交通，并生成可筛选标签。",
            "count": 10,
            "subtopic_count": 5,
            "subtopics": SHANGHAI_SUBTOPICS,
            "posts": SHANGHAI_POSTS,
            "summary_html": """
                <div class="summary-card">
                    <h3>笔记内容总结</h3>
                    <p>你收藏的内容主要集中在：</p>
                    <ul>
                        <li>上海经典景点路线</li>
                        <li>本帮菜、咖啡甜品和夜晚小酒馆</li>
                        <li>周末展览、市集和乐园活动</li>
                        <li>住宿区域和地铁换乘避坑</li>
                    </ul>
                    <p>综合来看，你更偏向“少绕路、好拍照、能顺手吃喝”的上海旅行方案。</p>
                    <h3>接下来</h3>
                    <p>如果你准备出发，可以先从：</p>
                    <ol>
                        <li>确定住宿区域</li>
                        <li>按 Citywalk 路线合并景点和咖啡店</li>
                        <li>提前预约展览或迪士尼项目</li>
                    </ol>
                </div>
            """,
        }
    return {
        "theme_id": "rent",
        "title": "小空间改造灵感",
        "subtitle": "37 篇笔记 · AI 已整理",
        "created_title": "已为你创建主题收藏夹：小空间改造灵感",
        "done_text": "AI 已帮你识别主题、总结重点，并生成可筛选标签。",
        "count": 37,
        "subtopic_count": 6,
        "subtopics": SUBTOPICS,
        "posts": get_theme_posts(),
        "summary_html": """
            <div class="summary-card">
                <h3>笔记内容总结</h3>
                <p>你收藏的内容主要集中在：</p>
                <ul>
                    <li>小户型空间利用</li>
                    <li>不打孔收纳</li>
                    <li>床底/墙面/洗衣机上方空间改造</li>
                    <li>低预算软装</li>
                    <li>提升出租屋生活感</li>
                </ul>
                <p>综合来看，你更偏向“低成本、可复原、不伤墙、提升生活感”的改造方案。</p>
                <h3>接下来</h3>
                <p>如果你想真正开始改造，可以先从：</p>
                <ol>
                    <li>床底收纳</li>
                    <li>洗衣机上方置物</li>
                    <li>折叠桌/移动小推车</li>
                </ol>
            </div>
        """,
    }


def render_album_rail() -> None:
    """笔记 tab 顶部的主题专辑轮播，使 AI 生成的价值持续可见。

    仅在已生成至少一个专辑时展示，避免空状态占位。
    点击“查看全部”跳转到专辑 tab，同时轮播卡本身作为体现 AI 成果的静态展示，
    避免复杂点击跳转逻辑与 Streamlit 布局抵触。
    """
    ids = album_ids()
    if not ids:
        return

    total = sum(ALBUM_NOTE_COUNTS.get(theme_id, 0) for theme_id in ids)

    st.markdown('<div class="album-rail-wrap">', unsafe_allow_html=True)
    head_left, head_right = st.columns([0.68, 0.32], vertical_alignment="center")
    with head_left:
        st.markdown(
            f'<div class="album-rail-head">'
            f'<h5>AI 整理的主题专辑</h5>'
            f'<span>{len(ids)} 个专辑 · {total} 篇笔记</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with head_right:
        st.markdown('<div class="rail-cta">', unsafe_allow_html=True)
        if st.button("查看全部 ›", key="album_rail_view_all", use_container_width=True):
            st.session_state.main_tab = "albums"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    cards = []
    for theme_id in ids:
        config = theme_config_for(theme_id)
        cards.append(
            f'<div class="album-rail-card">'
            f'<span class="rail-tag">AI 整理</span>'
            f'<div class="rail-title">{escape(config["title"])}</div>'
            f'<div class="rail-meta">{config["count"]} 篇 · {config["subtopic_count"]} 个子主题</div>'
            f'</div>'
        )
    st.markdown(
        f'<div class="album-rail-scroll"><div class="album-rail">{"".join(cards)}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_value_banner() -> None:
    """首页价值许诺型 banner，向面试官（首次进入的用户）传达产品核心价值。

    设计考量：
    - 使用价值许诺型文案，避免处于空收藏夹场景下讲“堆积”反而不合理
    - 仅在笔记 tab 且未关闭过时展示，不污染主体路径
    - 提供关闭按钮，体现对用户控制感的尊重。
    """
    if st.session_state.value_banner_dismissed:
        return

    st.markdown('<div class="value-banner-wrap">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="value-banner">
            <h4>让你的收藏变成能上手的方案</h4>
            <p>AI 帮你把杂乱的笔记整理成可执行的主题灵感库</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="value-banner-close">', unsafe_allow_html=True)
    if st.button("×", key="dismiss_value_banner"):
        st.session_state.value_banner_dismissed = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_ai_prompt() -> None:
    prompt_index = st.session_state.ai_prompt_index
    if prompt_index >= len(AI_PROMPTS):
        return

    prompt = AI_PROMPTS[prompt_index]
    stack_class = "ai-stack has-next" if prompt_index < len(AI_PROMPTS) - 1 else "ai-stack"
    st.markdown(
        f"""
        <div class="{stack_class}">
        <div class="ai-card">
            <span class="ai-pill">AI 收藏整理助手</span>
            <h2>我发现你最近收藏了 {prompt["count"]} 篇与「{prompt["theme"]}」相关的笔记</h2>
            <p>{prompt["description"]}</p>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="ai-button-row">', unsafe_allow_html=True)
    organize_col, dismiss_col = st.columns(2)
    with organize_col:
        if st.button("帮我整理", key=f'organize_{prompt["theme_id"]}', use_container_width=True, type="primary"):
            st.session_state.target_theme = prompt["theme_id"]
            st.session_state.page = "loading"
            st.session_state.ai_prompt_index += 1
            st.session_state.selected_subtopic = "全部"
            st.session_state.last_search = ""
            st.session_state.search_query = ""
            st.rerun()
    with dismiss_col:
        if st.button("不用了", key=f'dismiss_{prompt["theme_id"]}', use_container_width=True):
            st.session_state.ai_prompt_index += 1
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def bottom_nav() -> None:
    st.markdown(
        """
        <div class="bottom-nav">
            <div class="nav-item"><b>⌂</b>首页</div>
            <div class="nav-item active"><b>♡</b>收藏</div>
            <div class="nav-item"><b>◦</b>我的</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_default_page() -> None:
    default_posts = get_unclassified_default_posts()
    section_title = "未归类笔记" if album_ids() else "最近收藏"
    section_meta = f"展示 {len(default_posts)} 篇样例" if album_ids() else f"混合展示 {len(POSTS)} 篇样例"

    st.markdown('<div class="phone-shell"><div class="safe-top"></div>', unsafe_allow_html=True)
    render_collection_tabs()
    if st.session_state.main_tab == "notes":
        st.markdown(
            f'<p class="notes-count">你已收藏 {unclassified_note_count()} 篇笔记</p>',
            unsafe_allow_html=True,
        )
    st.markdown('<div class="content">', unsafe_allow_html=True)

    if st.session_state.main_tab == "albums":
        render_albums_page()
    else:
        render_value_banner()
        render_album_rail()
        render_ai_prompt()

        st.markdown(
            f"""
            <div class="section-title">
                <h3>{section_title}</h3>
                <span>{section_meta}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        note_grid(default_posts)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_loading_page() -> None:
    theme_label = "上海旅游" if st.session_state.target_theme == "shanghai" else "租房/小空间改造"
    st.markdown(
        f"""
        <div class="loading-wrap">
            <div class="loading-logo">AI</div>
            <div class="title-block">
                <h1>正在整理收藏夹</h1>
                <p>把「{theme_label}」相关收藏整理成可复用主题</p>
            </div>
            <div style="height: 18px"></div>
            <div class="loading-step"><span class="dot"></span>AI 正在识别收藏内容……</div>
            <div class="loading-step"><span class="dot"></span>正在聚类相似笔记……</div>
            <div class="loading-step"><span class="dot"></span>正在生成主题收藏夹……</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(1.6)
    add_generated_album(st.session_state.target_theme)
    st.session_state.theme_success_shown_at = monotonic()
    st.session_state.theme_success_theme = st.session_state.target_theme
    st.session_state.theme_success_dismissed = False
    st.session_state.page = "theme"
    st.rerun()


def set_subtopic(subtopic: str) -> None:
    st.session_state.selected_subtopic = subtopic
    st.session_state.last_search = ""
    st.session_state.search_query = ""


def render_chips(subtopics: list[str]) -> None:
    active = st.session_state.selected_subtopic
    if active not in subtopics:
        active = "全部"
        st.session_state.selected_subtopic = active

    selected = st.pills(
        "子主题标签",
        subtopics,
        selection_mode="single",
        default=active,
        key=f"subtopic_pills_{'_'.join(subtopics)}",
        label_visibility="collapsed",
        width="stretch",
    )
    if selected and selected != st.session_state.selected_subtopic:
        set_subtopic(selected)


def filtered_by_subtopic(posts: list[dict]) -> list[dict]:
    active = st.session_state.selected_subtopic
    if active == "全部":
        return posts
    return [post for post in posts if active in post["subtopics"]]


SEARCH_SUGGESTIONS = [
    "洗衣机上面怎么利用？",
    "不打孔上墙有什么办法",
    "小空间工位怎么布置",
]


def render_search() -> list[dict] | None:
    """主题页搜索区。

    除输入框外提供 3 个推荐问句 chip，点击后直接填充并触发搜索。
    设计考量：
    - 推荐问句为 AI 预测的“用户可能想问”，增强产品智能感
    - 避免面试官随手输入不及模糊匹配范围的 query 导致空结果
    - chip 底色差于主色，默认灰调，hover 才点亮品牌色，不与主 CTA 争夺注意力
    """
    pending_query = st.session_state.pop("_pending_search", None)
    if pending_query is not None:
        st.session_state.last_search = pending_query
        st.session_state.search_query = pending_query

    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    with st.form("search_form", clear_on_submit=False, border=False):
        input_col, button_col = st.columns([0.86, 0.14])
        with input_col:
            query = st.text_input(
                "搜索",
                key="search_query",
                label_visibility="collapsed",
                placeholder="试试搜索：洗衣机上怎么利用？",
            )
        with button_col:
            submitted = st.form_submit_button("⌕", use_container_width=True)
        if submitted:
            st.session_state.last_search = query
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="search-suggest">'
        '<p class="search-suggest-label">你可能想问</p>',
        unsafe_allow_html=True,
    )
    suggest_cols = st.columns(len(SEARCH_SUGGESTIONS))
    for idx, suggestion in enumerate(SEARCH_SUGGESTIONS):
        with suggest_cols[idx]:
            if st.button(suggestion, key=f"suggest_{idx}", use_container_width=True):
                st.session_state._pending_search = suggestion
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.last_search.strip():
        return search_theme_posts(st.session_state.last_search)
    return None


def render_theme_page() -> None:
    theme = current_theme_config()
    theme_posts = theme["posts"]

    st.markdown('<div class="phone-shell"><div class="safe-top"></div>', unsafe_allow_html=True)
    st.markdown('<div class="topbar theme-back">', unsafe_allow_html=True)
    back_col, title_col = st.columns([0.13, 0.87])
    with back_col:
        if st.button("‹", key="theme_back_btn"):
            st.session_state.page = "default"
            st.session_state.main_tab = "albums"
            st.session_state.selected_subtopic = "全部"
            st.session_state.last_search = ""
            st.session_state.search_query = ""
            st.rerun()
    with title_col:
        st.markdown(
            f"""
            <div class="title-block">
                <h1>{theme["title"]}</h1>
                <p>{theme["subtitle"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        """
        </div>
        <div class="content">
        """,
        unsafe_allow_html=True,
    )

    success_started = st.session_state.theme_success_shown_at
    is_current_success = st.session_state.theme_success_theme == theme["theme_id"]
    should_show_success = (
        is_current_success
        and success_started is not None
        and not st.session_state.theme_success_dismissed
        and monotonic() - success_started < 3
    )
    if should_show_success:
        st.markdown('<div class="success-card-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="success-card-actions">', unsafe_allow_html=True)
        if st.button("×", key=f'dismiss_success_button_{theme["theme_id"]}'):
            st.session_state.theme_success_dismissed = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ai-card">
                <span class="ai-pill">整理完成</span>
                <h2>{theme["created_title"]}</h2>
                <p>{theme["done_text"]}</p>
            </div>
            <div class="metrics-row">
                <div class="metric"><strong>{theme["count"]}</strong><span>已整理相关笔记</span></div>
                <div class="metric"><strong>{theme["subtopic_count"]}</strong><span>AI 子主题标签</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(theme["summary_html"], unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-title">
            <h3>子主题标签</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_chips(theme["subtopics"])

    search_results = render_search() if theme["theme_id"] == "rent" else None
    if search_results is not None and theme["theme_id"] == "rent":
        st.markdown(
            """
            <div class="reason">
                我优先找到了和「洗衣机上方空间」「洞洞板」「置物架」「护肤台」相关的笔记。
            </div>
            """,
            unsafe_allow_html=True,
        )
        posts_to_show = search_results
        section_label = f"搜索结果 · {len(posts_to_show)} 篇"
    else:
        posts_to_show = filtered_by_subtopic(theme_posts)
        section_label = f"{st.session_state.selected_subtopic} · {len(posts_to_show)} 篇"

    st.markdown(
        f"""
        <div class="section-title">
            <h3>相关笔记</h3>
            <span>{section_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    note_grid(posts_to_show)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    init_state()

    if st.session_state.page == "default":
        render_default_page()
    elif st.session_state.page == "loading":
        render_loading_page()
    else:
        render_theme_page()


if __name__ == "__main__":
    main()
