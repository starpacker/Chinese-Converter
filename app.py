import streamlit as st
from final import EnhancedPinyinConverter  # 确保final.py中有EnhancedPinyinConverter类
import re

# 初始化模型（仅执行一次）
if "model_initialized" not in st.session_state:
    EnhancedPinyinConverter.initialize_model(model_path="D:/qwen_0.6b")
    st.session_state.model_initialized = True

# 初始化 session_state
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "result" not in st.session_state:
    st.session_state.result = ""
if "context" not in st.session_state:
    st.session_state.context = ""  # 用于展示上下文内容（可编辑）

# 自定义样式
st.markdown("""
    <style>
        .main { background-color: #f5f5f5; padding: 20px; border-radius: 10px; }
        .result { font-size: 20px; color: #2c3e50; margin-top: 20px; border-left: 5px solid #3498db; padding-left: 10px; }
        .context-display { font-size: 16px; color: #555; margin-top: 10px; background-color: #eef2f3; padding: 10px; border-radius: 5px; }
        .error { color: red; margin-top: 10px; }
        .title { font-size: 28px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 页面标题
st.markdown('<div class="title">智能拼音转换器 v0.1.0</div>', unsafe_allow_html=True)

# 上下文输入框（用户手动输入）
context_input = st.text_area(
    "请输入上下文（帮助模型理解语境）",
    value=st.session_state.context,
    height=100
)

# 如果用户修改了上下文，则同步到 session_state 和 EnhancedPinyinConverter._context
if context_input != st.session_state.context:
    st.session_state.context = context_input
    EnhancedPinyinConverter._context = context_input

# 输入框
st.session_state.input_text = st.text_input(
    "请输入拼音字符串（仅限字母）",
    value=st.session_state.input_text
)

# 转换按钮
if st.button("转换为中文"):
    if not st.session_state.input_text:
        st.markdown('<div class="error">❌ 输入不能为空！</div>', unsafe_allow_html=True)
    elif not re.match(r"^[a-zA-Z]+$", st.session_state.input_text):
        st.markdown('<div class="error">❌ 输入包含非法字符！只接受字母</div>', unsafe_allow_html=True)
    else:
        with st.spinner("⏳ 正在转换中，请稍候..."):
            result = EnhancedPinyinConverter.convert(st.session_state.input_text)
            st.session_state.result = result
            st.session_state.context = st.session_state.context + result

# 显示结果
if st.session_state.result:
    st.markdown(f'<div class="result">✅ 转换结果：{st.session_state.result}</div>', unsafe_allow_html=True)

# 展示当前生效的上下文（来自 final.py 的 _context）
if st.session_state.context:
    st.markdown(f'<div class="context-display">📌 当前上下文：{st.session_state.context}</div>', unsafe_allow_html=True)

# 清空按钮分列布局
col1, col2 = st.columns(2)

with col1:
    if st.button("清空输入输出"):
        st.session_state.input_text = ""
        st.session_state.result = ""

with col2:
    if st.button("清空上下文"):
        st.session_state.context = ""
        EnhancedPinyinConverter._context = ""
