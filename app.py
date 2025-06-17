import streamlit as st
import json
from datetime import datetime, timedelta
import calendar
import os

# --- データファイルのパス ---
DATA_FILE = 'events.json'

# --- データの読み込み・保存 ---
# イベントデータを読み込む関数
def load_events():
    # データファイルが存在しない場合は空の辞書を返す
    if not os.path.exists(DATA_FILE):
        return {}
    
    # ファイルが存在する場合は読み込む
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            # JSONデータを読み込む。ファイルが空の場合や不正な形式の場合は空の辞書を返す
            return json.load(f)
        except json.JSONDecodeError:
            st.error("イベントファイルが破損しています。空のデータで開始します。")
            return {}

# イベントデータを保存する関数
def save_events(events):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        # JSONデータを整形して保存（ensure_ascii=False で日本語をそのまま保存）
        json.dump(events, f, ensure_ascii=False, indent=4)

# --- アプリの初期設定 ---
# ページ全体のレイアウトを広めに設定
st.set_page_config(layout="wide")
st.title("シンプルなスケジュールアプリ")

# --- イベントデータのロード ---
# アプリ起動時に既存のイベントデータを読み込む
events = load_events()

# --- カレンダー表示と日付選択 ---
# アプリのレイアウトを2つのカラムに分割
col1, col2 = st.columns([1, 2]) # 左側のカラムを狭く（カレンダー）、右側を広く（イベント管理）

with col1: # 左側のカラム（カレンダー表示）
    st.header("カレンダー")

    # セッションステートに現在の年月を保持（ページ再読み込み後も状態を維持するため）
    if 'current_year' not in st.session_state:
        st.session_state.current_year = datetime.now().year
    if 'current_month' not in st.session_state:
        st.session_state.current_month = datetime.now().month

    # 年月のナビゲーションボタンと表示
    year_month_col1, year_month_col2, year_month_col3 = st.columns([1, 2, 1])
    with year_month_col1:
        # 「前月」ボタン
        if st.button("前月", key="prev_month"):
            st.session_state.current_month -= 1 # 月を1減らす
            if st.session_state.current_month < 1: # 1月より前になったら
                st.session_state.current_month = 12 # 12月に戻し
                st.session_state.current_year -= 1 # 年を1減らす
            st.rerun() # 変更を反映するために再実行
    with year_month_col2:
        # 現在の年月を中央寄せで表示
        st.markdown(f"<h3 style='text-align: center;'>{st.session_state.current_year}年 {st.session_state.current_month}月</h3>", unsafe_allow_html=True)
    with year_month_col3:
        # 「翌月」ボタン
        if st.button("翌月", key="next_month"):
            st.session_state.current_month += 1 # 月を1増やす
            if st.session_state.current_month > 12: # 12月より後になったら
                st.session_state.current_month = 1 # 1月に戻し
                st.session_state.current_year += 1 # 年を1増やす
            st.rerun() # 変更を反映するために再実行

    # カレンダーの生成（HTML形式）
    # `calendar.HTMLCalendar` を使用して、日曜日始まりのカレンダーを生成
    cal = calendar.HTMLCalendar(calendar.SUNDAY)
    # 指定された年月のカレンダーをHTML文字列として取得
    cal_html = cal.formatmonth(st.session_state.current_year, st.session_state.current_month, withyear=True)

    # カレンダーのHTMLをStreamlitに表示（直接のインタラクティブ性はない）
    # 注: この方法ではカレンダー上の日付を直接クリックして選択することはできません。
    # そのため、別途`st.date_input`を使用します。
    # st.markdown(cal_html, unsafe_allow_html=True) # ここはコメントアウト（`st.date_input`をメインにするため）


    st.markdown("---") # 区切り線

    # 日付選択ウィジェット
    st.write("イベント管理したい日付を選択してください:")
    # `st.date_input`で日付を選択するUIを提供
    # 初期値は現在の日付、選択可能範囲も設定
    selected_date = st.date_input(
        "日付選択",
        value=datetime.now(), # 初期値は今日
        min_value=datetime(1900, 1, 1), # 選択可能な最小日付
        max_value=datetime(2100, 12, 31), # 選択可能な最大日付
        key="date_picker" # ウィジェットのユニークなキー
    )
    # 選択された日付を文字列形式でセッションステートに保存
    if selected_date:
        st.session_state.selected_date_str = selected_date.strftime("%Y-%m-%d")
    else:
        # 何も選択されていない場合のデフォルト
        st.session_state.selected_date_str = datetime.now().strftime("%Y-%m-%d")

    # 現在選択されている日付を表示
    st.markdown(f"**選択中の日付:** {st.session_state.selected_date_str}")


with col2: # 右側のカラム（イベント管理）
    st.header("イベント管理")

    # 日付が選択されている場合のみ、イベントの追加と表示を行う
    if st.session_state.selected_date_str:
        # 選択された日付から年月（YYYY-MM）と日（DD）を抽出
        selected_year_month = st.session_state.selected_date_str[:7] # 例: "2023-10"
        
        # --- イベント追加フォーム ---
        st.subheader(f"{st.session_state.selected_date_str} のイベント追加")
        # イベントタイトル入力欄
        event_title = st.text_input("イベントタイトル", key=f"title_input_{st.session_state.selected_date_str}")
        # イベント詳細入力欄
        event_description = st.text_area("詳細（任意）", key=f"desc_input_{st.session_state.selected_date_str}")
        
        # イベント追加ボタン
        if st.button("イベントを追加", key=f"add_event_button_{st.session_state.selected_date_str}"):
            if event_title: # タイトルが入力されている場合のみ
                # データ構造: events[年-月][年-月-日] = [イベント1, イベント2, ...]
                # 該当する年-月が存在しない場合は作成
                if selected_year_month not in events:
                    events[selected_year_month] = {}
                # 該当する年-月-日が存在しない場合は作成
                if st.session_state.selected_date_str not in events[selected_year_month]:
                    events[selected_year_month][st.session_state.selected_date_str] = []
                
                # 新しいイベントデータを追加
                events[selected_year_month][st.session_state.selected_date_str].append({
                    "title": event_title,
                    "description": event_description,
                    "timestamp": datetime.now().isoformat() # イベント追加日時を記録
                })
                save_events(events) # データを保存
                st.success("イベントを追加しました！")
                st.rerun() # ページを再読み込みしてイベントリストを更新
            else:
                st.warning("イベントタイトルは必須です。") # タイトルが空の場合の警告

        st.markdown("---") # 区切り線

        # --- 選択された日付のイベント表示 ---
        st.subheader(f"{st.session_state.selected_date_str} のイベント一覧")
        
        # 該当する年-月、日付にイベントが存在するか確認
        if selected_year_month in events and st.session_state.selected_date_str in events[selected_year_month]:
            daily_events = events[selected_year_month][st.session_state.selected_date_str]
            
            if daily_events: # イベントがある場合
                # 各イベントを展開可能なエクパンダーで表示
                for i, event in enumerate(daily_events):
                    with st.expander(f"**{event['title']}**"): # イベントタイトルが見出し
                        st.write(f"**説明:** {event['description']}")
                        # 追加日時を整形して表示
                        added_time = datetime.fromisoformat(event['timestamp']).strftime('%Y-%m-%d %H:%M')
                        st.write(f"**追加日時:** {added_time}")
                        
                        # 削除ボタン（ユニークなキーを設定）
                        if st.button("削除", key=f"delete_event_{st.session_state.selected_date_str}_{i}"):
                            # 該当イベントをリストから削除
                            del events[selected_year_month][st.session_state.selected_date_str][i]
                            
                            # その日付にイベントがなくなった場合、日付のキーも削除
                            if not events[selected_year_month][st.session_state.selected_date_str]:
                                del events[selected_year_month][st.session_state.selected_date_str]
                            
                            # その月にイベントがなくなった場合、月のキーも削除
                            if not events[selected_year_month]:
                                del events[selected_year_month]
                                
                            save_events(events) # 変更を保存
                            st.success("イベントを削除しました。")
                            st.rerun() # ページを再読み込みしてイベントリストを更新
            else: # イベントがない場合
                st.info("この日付にはイベントがありません。")
        else: # 該当する日付のキー自体が存在しない場合
            st.info("この日付にはイベントがありません。")
    else:
        st.info("カレンダーから日付を選択してください。") # 日付が選択されていない場合のメッセージ
