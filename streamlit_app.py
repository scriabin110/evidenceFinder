import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool

import os
from dotenv import load_dotenv

# os.environ["OPENAI_API_KEY"] = st.secrets['openAI_api_id']    #'YOUR_OPENAI_API_KEY'
# os.environ["GOOGLE_CSE_ID"] = st.secrets['cse_id']    #'YOUR_CSE_ID'
# os.environ["GOOGLE_API_KEY"] = st.secrets['Google_api_key']    #'YOUR_GOOGLE_API_KEY'

load_dotenv()

os.environ.get("OPENAI_API_KEY")
os.environ.get("GOOGLE_CSE_ID")
os.environ.get("GOOGLE_API_KEY")

# OpenAIのモデルのインスタンスを作成
llm = ChatOpenAI(model_name="gpt-4", temperature=0.75)

# プロンプトのテンプレート文章を定義
template_1 = """
# 命令書
下記の元原稿の真偽を検証すべく、エビデンスとなるWebページを検索したい。適切な検索キーワードを1組だけ教えて。


# ルール
- 検索キーワードは3単語または4単語とする。
- 下記のコツを活かして検索クエリを生成すること。

## 検索クエリのコツ
- テクニック1．除外検索(-)
- テクニック2．期間指定検索(「before:」、「after:」)
- テクニック3．OR検索 ( OR )
- テクニック4．完全一致検索 ("")
- テクニック5．あいまい検索 ( ＊ )
- テクニック6．リンク元サイト検索 ( link: )
- テクニック7．サイト指定検索 ( site: )
- テクニック8．関連サイト検索 ( related: )
- テクニック9．類義語・同義語を含む検索( ~ ) チルダ
- テクニック10．キーワードの意味を調べる検索 ( define:

\n
#元原稿
「{text}」
"""

# テンプレート文章にあるチェック対象の単語を変数化
prompt_1 = ChatPromptTemplate.from_messages([
    ("system", "あなたはWebコンテンツ編集のプロです。"),
    ("user", template_1)
])

# チャットメッセージを文字列に変換するための出力解析インスタンスを作成
output_parser = StrOutputParser()

# OpenAIのAPIにこのプロンプトを送信するためのチェーンを作成
chain = prompt_1 | llm | output_parser

def remove_quotes(string):
    return string.replace('"', '')

search = GoogleSearchAPIWrapper()

def top5_results(query):
    return search.results(query, 5)

tool = Tool(
    name="Google Search Snippets",
    description="Search Google for recent results.",
    func=top5_results,
)

# プロンプトのテンプレート文章を定義
template_2 = """
# 命令書
エビデンスから鑑みて、元原稿textの正誤を判断せよ。

# ルール
- 理由とともに30~50文字で回答すること。
- 返答は、以下の形式で回答すること。
    - 正しい場合：「元原稿は正しい。エビデンスによると、～ため。」
    - 誤りの場合：「元原稿は誤り。エビデンスによると、～ため。」
    - 判断できない場合：「正誤は判断できない。～について、追加のエビデンスが必要。」
- 「です・ます」調(敬体)としてはならない
\n\n
# 元原稿
「{text}」
\n
# エビデンス
「{snippets}」
"""

# テンプレート文章にあるチェック対象の単語を変数化
prompt_2 = ChatPromptTemplate.from_messages([
    ("system", "あなたは優秀な校正者です。"),
    ("user", template_2)
])

# Streamlit app
def main():
    st.title("エビデンス検証アプリ")

    text_1 = st.text_area("エビデンスチェックしたいテキストを入力してください。")
    st.write("文字数  :", len(text_1))

    # ボタンの状態を決定
    button_disabled = len(text_1) > 200

    if st.button("検証", disabled=button_disabled):
        if text_1:
            with st.spinner("検証中..."):
                query = chain.invoke({"text": text_1})
                query = remove_quotes(query)

                st.write("生成された検索クエリ:", query)

                evidence = top5_results(query)
                snippets_with_links = [f"{result['snippet']} \n(URL: {result['link']})" for result in evidence]

                st.write("検索結果:")
                for i, snippet_with_link in enumerate(snippets_with_links, 1):
                    st.write(f"{i}. {snippet_with_link}")
                    st.write("")  # 空行を追加して見やすくする

                chain_2 = prompt_2 | llm | output_parser
                result = chain_2.invoke({"text": text_1, "snippets": snippets_with_links})

                st.write("検証結果:", result)
        else:
            st.warning("テキストを入力してください。")
    
    if button_disabled:
        st.warning("テキストは200文字以内にしてください。")

if __name__ == "__main__":
    main()