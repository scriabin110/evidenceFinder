import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool
import os
import requests
from bs4 import BeautifulSoup

os.environ["OPENAI_API_KEY"] = st.secrets['openAI_api_id']    #'YOUR_OPENAI_API_KEY'
os.environ["GOOGLE_CSE_ID"] = st.secrets['cse_id']    #'YOUR_CSE_ID'
os.environ["GOOGLE_API_KEY"] = st.secrets['Google_api_key']    #'YOUR_GOOGLE_API_KEY'

llm = ChatOpenAI(model_name="gpt-4o", max_tokens=None, temperature=0.75)

template_0 = """
# 命令書
与えられた元原稿に予算や相場などの数値情報が含まれているかどうかを判断してください。

# ルール
- 予算、相場、税率、金額、割合などの具体的な数値情報を探してください。
- 判断結果は以下のいずれかで回答してください：
  - 数値情報あり：「エビデンスが必要です」
  - 数値情報なし：「エビデンス不要と判断しました」

# 元原稿
「{text}」
"""

prompt_0 = ChatPromptTemplate.from_messages([
    ("system", "あなたはテキスト分析の専門家です。"),
    ("user", template_0)
])

template_1 = """
# 命令書
下記の元原稿の真偽を検証すべく、エビデンスとなるWebページを検索したい。適切な検索キーワードを5組教えて。

# ルール
- 検索キーワードは2単語または3単語とする。
- 5つの異なる検索クエリを生成し、番号を付けて列挙すること。

#元原稿
「{text}」
"""

prompt_1 = ChatPromptTemplate.from_messages([
    ("system", "あなたはWebコンテンツ編集のプロです。"),
    ("user", template_1)
])

output_parser = StrOutputParser()
chain_0 = prompt_0 | llm | output_parser
chain_1 = prompt_1 | llm | output_parser

def remove_quotes_if_needed(string):
    if string.startswith('"') and string.endswith('"'):
        return string[1:-1]
    return string

search = GoogleSearchAPIWrapper()

def top5_results(query):
    return search.results(query, 5)

tool = Tool(
    name="Google Search Snippets",
    description="Search Google for recent results.",
    func=top5_results,
)

template_2 = """
# 命令書
エビデンスから鑑みて、元原稿textの正誤を判断せよ。

# ルール
- 理由とともに30~50文字で回答すること。
- 返答は、以下の形式で回答すること。
    - 正しい場合：「元原稿は正しい。エビデンスによると、～であるため。」
    - 誤りの場合：「元原稿は誤り。エビデンスによると、～であるため。」
    - 判断できない場合：「正誤は判断できない。～について、追加のエビデンスが必要。」
- 「です・ます」調(敬体)としてはならない

# 元原稿
「{text}」

# エビデンス
「{snippets}」

# h-tagの内容
「{h_tags}」
"""

prompt_2 = ChatPromptTemplate.from_messages([
    ("system", "あなたは優秀な校正者です。"),
    ("user", template_2)
])

def get_h_tags(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        h_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        return [tag.get_text() for tag in h_tags]
    except:
        return []

def get_h_tags_with_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        h_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        return [f"{tag.name}: {tag.get_text()}" for tag in h_tags]
    except:
        return []

template_3 = """
# 命令書
与えられた検証結果と検索結果から、最も重要なエビデンスのURLを1つ選び、そのページのhタグの中から、
最も関連性の高いhタグを特定してください。

# ルール
- 検証結果に最も影響を与えたURLを1つ選択すること。
- 選択したURLのhタグの中から、検証結果に最も関連する情報が含まれていそうなhタグを1つ選ぶこと。
- 回答は以下の形式で行うこと：
  最も重要なURL: [選択したURL]
  最も関連性の高いhタグ: [選択したhタグ]
  理由: [選択した理由を1文で]

# 検証結果
{result}

# 検索結果
{snippets}

# 選択したURLのhタグ
{h_tags}
"""

prompt_3 = ChatPromptTemplate.from_messages([
    ("system", "あなたは優秀なWeb分析者です。"),
    ("user", template_3)
])

def main():
    st.title("エビデンス検証アプリ")

    # セッション状態の初期化
    if 'text_1' not in st.session_state:
        st.session_state.text_1 = ""
    if 'queries' not in st.session_state:
        st.session_state.queries = []
    if 'evidence' not in st.session_state:
        st.session_state.evidence = None
    if 'result' not in st.session_state:
        st.session_state.result = None

    text_1 = st.text_area("エビデンスチェックしたいテキストを入力してください。", value=st.session_state.text_1)
    st.write("文字数  :", len(text_1))

    button_disabled = len(text_1) > 200

    if st.button("検証", disabled=button_disabled):
        if text_1:
            st.session_state.text_1 = text_1
            with st.spinner("テキストを分析中..."):
                evidence_needed = chain_0.invoke({"text": text_1})
                
            if "エビデンスが必要です" in evidence_needed:
                with st.spinner("検証中..."):
                    queries = chain_1.invoke({"text": text_1})
                    queries = queries.split('\n')
                    st.session_state.queries = [remove_quotes_if_needed(q.split('. ')[1]) for q in queries if q]
                    st.session_state.evidence = None  # 新しい検証時に以前の結果をクリア
                    st.session_state.result = None
            else:
                st.write(evidence_needed)
                st.session_state.queries = []
                st.session_state.evidence = None
                st.session_state.result = None

    if st.session_state.queries:
        st.write("生成された検索クエリ:")
        for i, query in enumerate(st.session_state.queries, 1):
            st.write(f"{i}. {query}")

        selected_query = st.selectbox("使用する検索クエリを選択してください:", st.session_state.queries)

        if selected_query != st.session_state.get('last_selected_query'):
            st.session_state.last_selected_query = selected_query
            with st.spinner("検索中..."):
                st.session_state.evidence = top5_results(selected_query)
                st.session_state.result = None  # 新しい検索時に以前の結果をクリア

        if st.session_state.evidence:
            snippets_with_links = [f"{result['snippet']} \n(URL: {result['link']})" for result in st.session_state.evidence]

            st.write("検索結果:")
            for i, snippet_with_link in enumerate(snippets_with_links, 1):
                st.write(f"{i}. {snippet_with_link}")
                st.write("")

            top_url = st.session_state.evidence[0]['link']
            h_tags = get_h_tags(top_url)
            h_tags_str = "\n".join(h_tags)

            if st.session_state.result is None:
                with st.spinner("結果を生成中..."):
                    chain_2 = prompt_2 | llm | output_parser
                    st.session_state.result = chain_2.invoke({"text": text_1, "snippets": snippets_with_links, "h_tags": h_tags_str})

            if st.session_state.result:
                st.write("検証結果:", st.session_state.result)

                # 重要なURLとhタグの分析
                with st.spinner("重要なエビデンスを分析中..."):
                    chain_3 = prompt_3 | llm | output_parser
                    all_h_tags = {result['link']: get_h_tags_with_content(result['link']) for result in st.session_state.evidence}
                    important_evidence = chain_3.invoke({
                        "result": st.session_state.result,
                        "snippets": snippets_with_links,
                        "h_tags": all_h_tags
                    })
                    
                    st.write("重要なエビデンス:")
                    lines = important_evidence.split('\n')
                    for line in lines:
                        if line.strip():
                            key, value = line.split(':', 1)
                            st.write(f"**{key.strip()}:** {value.strip()}")

    if button_disabled:
        st.warning("テキストは200文字以内にしてください。")

if __name__ == "__main__":
    main()