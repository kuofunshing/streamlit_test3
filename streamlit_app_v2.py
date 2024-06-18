import streamlit as st
import replicate
import os
import sqlite3
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# 初始化數據庫
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()

def main():
    st.sidebar.title("導航")
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['remaining_uses'] = 0

    if st.session_state['logged_in']:
        st.write(f"歡迎，{st.session_state['username']}！")
        st.write("這是受保護的內容。")
        st.write(f"剩餘服務次數: {st.session_state['remaining_uses']}")
        if st.sidebar.button("登出"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ""
            st.session_state['remaining_uses'] = 0
            st.experimental_rerun()
        
        # 顯示多頁面導航
        pages = {
            "API頁面": api_key_page,
            "圖片處理": data_page,
            "yt頁面": yt_page,
            "充值頁面": recharge_page,
            "Llama2 Chatbot": llama2_chatbot_page,
        }
    else:
        pages = {
            "登入與註冊": login_signup_page
        }

    selection = st.sidebar.radio("前往", list(pages.keys()))
    page = pages[selection]
    page()

def login_signup_page():
    menu = ["登入", "註冊"]
    choice = st.selectbox("選擇操作", menu)

    if choice == "登入":
        login()
    elif choice == "註冊":
        signup()

def login():
    st.subheader("請登入")
    
    username = st.text_input("用戶名")
    password = st.text_input("密碼", type="password")

    if st.button("登入"):
        user = validate_login(username, password)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['remaining_uses'] = 10  # 初始化服務次數
            st.success("登入成功！")
            st.experimental_rerun()
        else:
            st.error("用戶名或密碼錯誤。")

def signup():
    st.subheader("註冊新帳戶")
    
    new_username = st.text_input("新用戶名")
    new_password = st.text_input("新密碼", type="password")

    if st.button("註冊"):
        if not validate_signup(new_username):
            create_user(new_username, new_password)
            st.success("註冊成功，請登入！")
        else:
            st.error("用戶名已存在，請選擇其他用戶名。")

def validate_login(username, password):
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return c.fetchone()

def validate_signup(username):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    return c.fetchone()

def create_user(username, password):
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()

def api_key_page():
    st.title("API KEY 取得頁面")

    if st.session_state['remaining_uses'] <= 0:
        st.warning("剩餘服務次數不足，請充值。")
        return

    uploaded_file = st.file_uploader("選擇一個文件", type=["txt"])

    if uploaded_file is not None:
        st.session_state['remaining_uses'] -= 1
        content = str(uploaded_file.read(), "utf-8")
        st.session_state['api_key'] = content
        st.success("API KEY 文件已上傳並保存。")
    else:
        st.write("請上傳一個API KEY文件。")

    if 'show_image' not in st.session_state:
        st.session_state['show_image'] = True

    if st.button('顯示/隱藏圖片'):
        st.session_state['show_image'] = not st.session_state['show_image']
        st.session_state['remaining_uses'] -= 1

    if st.session_state['show_image']:
        st.image('https://i.ibb.co/N3M78qc/image.jpg', caption='API 圖片')

    if 'show_text' not in st.session_state:
        st.session_state['show_text'] = False

    if st.button('顯示/隱藏 KEY'):
        st.session_state['show_text'] = not st.session_state['show_text']
        st.session_state['remaining_uses'] -= 10

    if st.session_state['show_text']:
        if 'api_key' in st.session_state:
            st.write(st.session_state['api_key'])
        else:
            st.error("請上傳API KEY文件。")

# 圖片處理頁面
def data_page():
    st.header("圖片處理")
    st.write("這是圖片處理頁面。")
  
    if st.session_state['remaining_uses'] <= 0:
        st.warning("剩餘服務次數不足，請充值。")
        return

    uploaded_file = st.file_uploader("選擇一個圖片文件", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        filter_type = st.selectbox("選擇一個濾鏡", [
            'BLUR', 'CONTOUR', 'DETAIL', 'SHARPEN', 
            'EDGE_ENHANCE', 'EMBOSS', 'FIND_EDGES', 'SMOOTH',
            'BRIGHTNESS', 'CONTRAST', 'COLOR', 'INVERT', 'GRAYSCALE'
        ])
        processed_image = process_image(image, filter_type)
        st.session_state['remaining_uses'] -= 1
        st.image(processed_image, caption='處理後的圖片', use_column_width=True)
        if st.button("確認處理"):
            st.session_state['remaining_uses'] -= 1
    else:
        st.write("請上傳一個圖片文件。")

@st.cache_data
def process_image(_image, filter_type):
    if filter_type == 'BLUR':
        return _image.filter(ImageFilter.BLUR)
    elif filter_type == 'CONTOUR':
        return _image.filter(ImageFilter.CONTOUR)
    elif filter_type == 'DETAIL':
        return _image.filter(ImageFilter.DETAIL)
    elif filter_type == 'SHARPEN':
        return _image.filter(ImageFilter.SHARPEN)
    elif filter_type == 'EDGE_ENHANCE':
        return _image.filter(ImageFilter.EDGE_ENHANCE)
    elif filter_type == 'EMBOSS':
        return _image.filter(ImageFilter.EMBOSS)
    elif filter_type == 'FIND_EDGES':
        return _image.filter(ImageFilter.FIND_EDGES)
    elif filter_type == 'SMOOTH':
        return _image.filter(ImageFilter.SMOOTH)
    elif filter_type == 'BRIGHTNESS':
        enhancer = ImageEnhance.Brightness(_image)
        return enhancer.enhance(1.5)  # 1.5是亮度增強的係數
    elif filter_type == 'CONTRAST':
        enhancer = ImageEnhance.Contrast(_image)
        return enhancer.enhance(1.5)  # 1.5是對比度增強的係數
    elif filter_type == 'COLOR':
        enhancer = ImageEnhance.Color(_image)
        return enhancer.enhance(1.5)  # 1.5是顏色增強的係數
    elif filter_type == 'INVERT':
        return ImageOps.invert(_image.convert("RGB"))
    elif filter_type == 'GRAYSCALE':
        return _image.convert("L")
    else:
        return _image

def recharge_page():
    st.header("充值頁面")
    st.write("這是充值頁面。")
    
    card_number = st.text_input("卡號")
    name = st.text_input("姓名")
    email = st.text_input("Email")
    birth_date = st.date_input("出生年月日")
    
    if st.button("充值"):
        if card_number and name and email and birth_date:
            st.session_state['remaining_uses'] += 10
            st.success("充值成功！剩餘服務次數已增加。")
        else:
            st.error("請填寫所有必填欄位。")

# yt頁面
def yt_page():
    st.header("yt頁面")
    st.write("這是yt頁面。")

    st.title("顯示 YouTube 影片選項")

    if st.session_state['remaining_uses'] <= 0:
        st.warning("剩餘服務次數不足，請充值。")
        return

    video_options =    video_options = {
        "影片 1": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=74s&pp=ygUXbmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXA%3D",
        "影片 2": "https://www.youtube.com/watch?v=tJuJ0Dls1hI&ab_channel=%E9%88%BE%E9%88%A6%E4%BA%BA%E6%AF%92%E6%B0%A3%E9%81%8E%E5%BA%A6%E9%9C%80%E8%A6%81",
        "影片 3": "https://www.youtube.com/watch?v=shRV-LIbsO8&ab_channel=GundamInfo",
        "影片 4": "https://www.youtube.com/watch?v=CnUIs6aLjic&ab_channel=GundamInfo",
        "影片 5": "https://www.youtube.com/watch?v=CI41ouIbu2I&ab_channel=GundamInfo",
        "影片 6": "https://www.youtube.com/watch?v=7HZfuTxBhV8&ab_channel=GundamInfo",
        "影片 7": "https://www.youtube.com/watch?v=Yqr9OIgcrrA&pp=ygUPb25seSBteSByYWlsZ3Vu",
        "影片 8": "https://www.youtube.com/watch?v=08yTIIdyUpc&t=206s",
        "影片 9": "https://www.youtube.com/watch?v=FDd4jekq93A&ab_channel=VelikiyKutere",
        "影片 10": "https://www.youtube.com/watch?v=mdSXKdnLX9I&pp=ygUP57SF6JOu44Gu5byT55-i"
    }
    
    selected_video = st.selectbox("選擇一個影片", list(video_options.keys()))

    if st.button("播放"):
        st.session_state['remaining_uses'] -= 1
        st.video(video_options[selected_video])

def llama2_chatbot_page():
    st.title("🦙💬 Llama 2 Chatbot")

    if st.session_state['remaining_uses'] <= 0:
        st.warning("剩餘服務次數不足，請充值。")
        return

    # Replicate Credentials
    with st.sidebar:
        st.title('🦙💬 Llama 2 Chatbot')
        if 'REPLICATE_API_TOKEN' in st.secrets:
            st.success('API key already provided!', icon='✅')
            replicate_api = st.secrets['REPLICATE_API_TOKEN']
        else:
            replicate_api = st.text_input('Enter Replicate API token:', type='password')
            if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
                st.warning('Please enter your credentials!', icon='⚠️')
            else:
                st.success('Proceed to entering your prompt message!', icon='👉')

        # Refactored from https://github.com/a16z-infra/llama2-chatbot
        st.subheader('Models and parameters')
        selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B', 'Llama2-70B'], key='selected_model')
        if selected_model == 'Llama2-7B':
            llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
        elif selected_model == 'Llama2-13B':
            llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
        else:
            llm = 'replicate/llama70b-v2-chat:e951f18578850b652510200860fc4ea62b3b16fac280f83ff32282f87bbd2e48'
        
        temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
        top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
        max_length = st.sidebar.slider('max_length', min_value=64, max_value=4096, value=512, step=8)
        
        st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    # Store LLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

    # Function for generating LLaMA2 response
    def generate_llama2_response(prompt_input):
        string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
        for dict_message in st.session_state.messages:
            if dict_message["role"] == "user":
                string_dialogue += "User: " + dict_message["content"] + "\n\n"
            else:
                string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
        output = replicate.run(llm, 
                               input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                      "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
        return output

    # User-provided prompt
    if prompt := st.chat_input(disabled=not replicate_api):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_llama2_response(prompt)
                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
        st.session_state['remaining_uses'] -= 5  # 每次對話減少5次次數


if __name__ == "__main__":
    main()


 
