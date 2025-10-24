# ============================================================
# 🍱 AI 식단 생성기 (자동 리밸런싱 내장 버전)
#  - AI 추천 + DB 매칭 + 알러지 필터 + 자동 리밸런싱(항상 적용)
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import google.generativeai as genai
import matplotlib.pyplot as plt

# -------------------------------
# ⚙️ 한글 폰트 설정 (macOS)
# -------------------------------
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# -------------------------------
# 🔑 Gemini API 설정
# -------------------------------
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = "AIzaSyA6kFiZlrVEeq4fPwf1kw7NeHCGKYtBNYM"  # 테스트용
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------------------
# 📂 데이터 불러오기
# -------------------------------
@st.cache_data
def load_data():
    food_db = pd.read_csv("/Users/younghun/Desktop/무제 폴더 2/data/20250408_음식DB.csv")
    food_db = food_db.dropna(subset=["식품명"])
    food_db = food_db.replace("-", 0)
    for col in ["에너지(kcal)", "탄수화물(g)", "단백질(g)", "지방(g)", "당류(g)"]:
        food_db[col] = pd.to_numeric(food_db[col], errors="coerce").fillna(0)

    def classify(name):
        if any(k in name for k in ["국", "탕", "찌개"]):
            return "국/찌개"
        elif any(k in name for k in ["밥", "덮밥", "비빔밥"]):
            return "밥"
        elif any(k in name for k in ["볶음", "구이", "조림", "찜", "튀김"]):
            return "메인반찬"
        else:
            return "반찬/기타"

    food_db["분류"] = food_db["식품명"].apply(classify)
    return food_db

food_db = load_data()

# -------------------------------
# 🧠 AI 식단 추천
# -------------------------------
def generate_meal_with_ai(food_db, goal_kcal, carb_ratio, protein_ratio, fat_ratio, avoid_list):
    avoid_text = ", ".join(avoid_list) if avoid_list else "없음"
    prompt = f"""
    당신은 전문 영양사입니다.
    다음 음식 리스트를 참고하여 하루 3끼 식단을 짜주세요.

    조건:
    - 각 끼니는 [밥 1, 국/찌개 1, 메인반찬 1, 반찬/기타 2]
    - 총 칼로리는 약 {goal_kcal} kcal 내외
    - 탄단지 비율: {carb_ratio}% / {protein_ratio}% / {fat_ratio}%
    - 절대 포함하지 말아야 할 음식: {avoid_text}
    - 출력 형식:
      아침: 항목1, 항목2, 항목3, 항목4, 항목5
      • (약 630 kcal / 탄수화물 약 58g, 단백질 약 51g, 지방 약 21g)
      점심: ...
      저녁: ...
    """
    response = model.generate_content(prompt)
    return response.text

# -------------------------------
# 🔎 파싱 & 매칭
# -------------------------------
def parse_ai_result(ai_text):
    pattern = r"(아침|점심|저녁)\s*[:：]\s*(.+)"
    meals = re.findall(pattern, ai_text)
    structured = {}
    for meal, items in meals:
        parts = re.split(r"[,、/]+|\s{2,}", items)
        food_list = [f.strip() for f in parts if len(f.strip()) > 1]
        structured[meal] = food_list[:5]
    return structured

def parse_meal_text_to_dataframe(ai_text):
    rows = []
    pattern = re.compile(
        r"(아침|점심|저녁)\s*[:：]\s*(.+?)\s*"
        r"(?:\n|\r\n)\s*[*•\-]?\s*"
        r"\(\s*약?\s*([\d,]+)\s*kcal\s*/\s*탄수화물\s*약?\s*([\d\.]+)g,\s*단백질\s*약?\s*([\d\.]+)g,\s*지방\s*약?\s*([\d\.]+)g\s*\)",
        flags=re.S
    )

    for m in pattern.finditer(ai_text):
        meal = m.group(1).strip()
        menu = m.group(2).strip().replace("\n", " ").replace("  ", " ")
        kcal = float(m.group(3).replace(",", ""))
        c = float(m.group(4))
        p = float(m.group(5))
        f = float(m.group(6))
        rows.append({
            "구분": meal,
            "메뉴": menu,
            "칼로리(kcal)": kcal,
            "탄수화물(g)": c,
            "단백질(g)": p,
            "지방(g)": f
        })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    total = {
        "구분": "합계",
        "메뉴": "",
        "칼로리(kcal)": df["칼로리(kcal)"].sum(),
        "탄수화물(g)": df["탄수화물(g)"].sum(),
        "단백질(g)": df["단백질(g)"].sum(),
        "지방(g)": df["지방(g)"].sum(),
    }
    df = pd.concat([df, pd.DataFrame([total])], ignore_index=True)
    return df

def match_foods_to_db(meal_dict, food_db, avoid_list):
    results = []
    for time, items in meal_dict.items():
        for food in items:
            if any(a for a in avoid_list if a and a in food):
                continue
            key = food[:3] if len(food) >= 3 else food
            match = food_db[food_db["식품명"].str.contains(re.escape(key), case=False, na=False)]
            if len(match) > 0:
                row = match.iloc[0].to_dict()
                row["끼니"] = time
                row["AI추천명"] = food
                results.append(row)
    return pd.DataFrame(results)

# -------------------------------
# 📐 유틸
# -------------------------------
def totals(df):
    if df.empty:
        return {"kcal":0, "C":0, "P":0, "F":0, "ratio": {"탄수화물":0,"단백질":0,"지방":0}}
    Cg = df["탄수화물(g)"].sum()
    Pg = df["단백질(g)"].sum()
    Fg = df["지방(g)"].sum()
    kcal = Cg*4 + Pg*4 + Fg*9
    ratio = {"탄수화물": (Cg*4)/kcal*100, "단백질": (Pg*4)/kcal*100, "지방": (Fg*9)/kcal*100} if kcal else {"탄수화물":0,"단백질":0,"지방":0}
    return {"kcal":kcal, "C":Cg, "P":Pg, "F":Fg, "ratio":ratio}

def l1_ratio_distance(ratio, target):
    return abs(ratio["탄수화물"]-target[0]) + abs(ratio["단백질"]-target[1]) + abs(ratio["지방"]-target[2])

# -------------------------------
# 🔁 자동 리밸런싱
# -------------------------------
def auto_rebalance(food_db, current, goal_kcal, target_ratio, avoid_list,
                   kcal_tol=0.05, max_iters=60, log_cb=None):
    def candidate_pool(selected_names):
        pool = food_db[~food_db["식품명"].isin(selected_names)].copy()
        if avoid_list:
            mask = ~pool["식품명"].apply(lambda x: any(a and a in x for a in avoid_list))
            pool = pool[mask]
        return pool

    def score_after_add(cur_df, cand):
        new_df = pd.concat([cur_df, cand.to_frame().T], ignore_index=True)
        tot = totals(new_df)
        kcal_err = abs(tot["kcal"] - goal_kcal) / max(goal_kcal, 1)
        ratio_err = l1_ratio_distance(tot["ratio"], target_ratio) / 300.0
        return -(kcal_err*0.7 + ratio_err*0.3), tot

    def score_after_remove(cur_df, idx):
        new_df = cur_df.drop(index=idx)
        tot = totals(new_df)
        kcal_err = abs(tot["kcal"] - goal_kcal) / max(goal_kcal, 1)
        ratio_err = l1_ratio_distance(tot["ratio"], target_ratio) / 300.0
        return -(kcal_err*0.7 + ratio_err*0.3), tot

    iters = 0
    while iters < max_iters:
        iters += 1
        cur_tot = totals(current)
        kcal = cur_tot["kcal"]
        kcal_err = (kcal - goal_kcal) / max(goal_kcal, 1)
        ratio_err_abs = l1_ratio_distance(cur_tot["ratio"], target_ratio)
        if log_cb:
            log_cb(f"#{iters} kcal={kcal:.0f} ({kcal_err*100:+.1f}%), ratio_dist={ratio_err_abs:.1f}")
        if abs(kcal_err) <= kcal_tol:
            break
        names = set(current["식품명"]) if not current.empty else set()
        pool = candidate_pool(names)
        if kcal < goal_kcal:
            preferred = pool.copy()
            if goal_kcal - kcal > 250:
                preferred = pd.concat([
                    pool[pool["분류"].isin(["메인반찬","밥"])],
                    pool[~pool["분류"].isin(["메인반찬","밥"])]
                ], ignore_index=True)
            best_score, best_cand = -1e9, None
            for _, cand in preferred.iterrows():
                s, _ = score_after_add(current, cand)
                if s > best_score:
                    best_score, best_cand = s, cand
            if best_cand is None:
                break
            current = pd.concat([current, best_cand.to_frame().T], ignore_index=True)
            if log_cb:
                log_cb(f"  ➕ 추가: {best_cand['식품명']} ({best_cand['에너지(kcal)']:.0f} kcal)")
        else:
            if current.empty:
                break
            best_score, best_idx = -1e9, None
            for idx in current.index:
                s, _ = score_after_remove(current, idx)
                if s > best_score:
                    best_score, best_idx = s, idx
            removed = current.loc[best_idx]
            current = current.drop(index=best_idx).reset_index(drop=True)
            if log_cb:
                log_cb(f"  ➖ 제거: {removed['식품명']} ({removed['에너지(kcal)']:.0f} kcal)")
    return current

# -------------------------------
# 🌿 Streamlit UI
# -------------------------------
st.title("🍱 AI 식단 자동 생성기")

goal_kcal = st.number_input("🎯 목표 칼로리 (kcal)", 1000, 5000, 2500, step=50)
col1, col2, col3 = st.columns(3)
with col1: carb_ratio = st.slider("🍚 탄수화물 (%)", 10, 80, 50)
with col2: protein_ratio = st.slider("🍗 단백질 (%)", 10, 50, 30)
with col3: fat_ratio = st.slider("🥑 지방 (%)", 10, 50, 20)
avoid_input = st.text_input("🚫 피해야 할 음식 (쉼표로 구분)", "우유, 땅콩, 새우")

if st.button("AI 식단 생성하기 🚀"):
    avoid_list = [a.strip() for a in avoid_input.split(",") if a.strip()]

    with st.spinner("AI가 식단을 구성 중입니다... 🍽️"):
        ai_text = generate_meal_with_ai(food_db, goal_kcal, carb_ratio, protein_ratio, fat_ratio, avoid_list)

    st.subheader("🤖 AI 추천 식단 (원문)")
    
    st.markdown(ai_text)
    meal_dict = parse_ai_result(ai_text)
    matched = match_foods_to_db(meal_dict, food_db, avoid_list)
    if matched.empty:
        st.error("❌ DB 매칭 결과가 없습니다.")
        st.stop()

    st.success("✅ DB 매칭 완료")
    st.dataframe(matched[["끼니","AI추천명","식품명","분류","에너지(kcal)","탄수화물(g)","단백질(g)","지방(g)"]])

    # 리밸런싱 자동 적용
    logs = []
    t_before = totals(matched)
    def log_cb(msg): logs.append(msg)
    final_df = auto_rebalance(food_db, matched.copy(), goal_kcal,
                              (carb_ratio, protein_ratio, fat_ratio),
                              avoid_list, kcal_tol=0.05, max_iters=60, log_cb=log_cb)

    with st.expander("🔎 리밸런싱 로그 보기"):
        for line in logs:
            st.write(line)

    # 전/후 비교 시각화
    t_after = totals(final_df)
    ratio_before, ratio_after = t_before["ratio"], t_after["ratio"]
    err_before = (t_before["kcal"] - goal_kcal) / goal_kcal * 100
    err_after = (t_after["kcal"] - goal_kcal) / goal_kcal * 100

    st.subheader("📈 리밸런싱 전후 비교")
    st.markdown(f"**리밸런싱 전:** {t_before['kcal']:.0f} kcal ({err_before:+.1f}%) | 탄 {ratio_before['탄수화물']:.1f}% 단 {ratio_before['단백질']:.1f}% 지 {ratio_before['지방']:.1f}%")
    st.markdown(f"**리밸런싱 후:** {t_after['kcal']:.0f} kcal ({err_after:+.1f}%) | 탄 {ratio_after['탄수화물']:.1f}% 단 {ratio_after['단백질']:.1f}% 지 {ratio_after['지방']:.1f}%")

    fig, ax = plt.subplots()
    labels = ["탄수화물", "단백질", "지방"]
    before = [ratio_before["탄수화물"], ratio_before["단백질"], ratio_before["지방"]]
    after = [ratio_after["탄수화물"], ratio_after["단백질"], ratio_after["지방"]]
    x = np.arange(len(labels)); width = 0.35
    ax.bar(x - width/2, before, width, label="리밸런싱 전")
    ax.bar(x + width/2, after, width, label="리밸런싱 후")
    ax.set_ylabel("비율 (%)")
    ax.set_title("영양비율 변화 (전 vs 후)")
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.legend()
    st.pyplot(fig)

    st.subheader("🍽️ 최종 식단 결과")
    st.dataframe(final_df[["끼니","AI추천명","식품명","분류","에너지(kcal)","탄수화물(g)","단백질(g)","지방(g)"]])
