import base64
import os
import random
import time
from pathlib import Path

import streamlit as st
from google import genai

BASE = Path(__file__).parent / 'images'
MODEL_NAME = 'gemini-2.5-flash'
COLOR_HEX = {'red': '#FF4B4B', 'blue': '#1C83E1', 'green': '#00C853', 'yellow': '#FFD600'}
COLOR_NAMES = {
    'ru': {'red': 'КРАСНЫЙ', 'blue': 'СИНИЙ', 'green': 'ЗЕЛЁНЫЙ', 'yellow': 'ЖЁЛТЫЙ'},
    'en': {'red': 'RED', 'blue': 'BLUE', 'green': 'GREEN', 'yellow': 'YELLOW'},
}
SEPARATOR = '--- ANSWER ---'

PUZZLES = {
    'ru': [
        ('У фермера было 17 овец. Все, кроме 9, убежали. Сколько овец осталось?', '9 овец.'),
        ('Что тяжелее: килограмм ваты или килограмм железа?', 'Они весят одинаково.'),
        ('Сколько месяцев в году имеют 28 дней?', 'Все 12: в каждом месяце есть 28 дней.'),
        ('В комнате 4 угла, в каждом углу сидит кошка, напротив каждой кошки сидят 3 кошки. Сколько всего кошек?', '4 кошки.'),
        ('У тебя одна спичка. Ты входишь в тёмную комнату, где есть лампа, свеча и печка. Что зажжёшь первым?', 'Спичку.'),
        ('Врач дал три таблетки и велел принимать по одной каждые полчаса. На сколько хватит таблеток?', 'На час: первую принимаешь сразу, вторую через 30 минут, третью ещё через 30.'),
    ],
    'en': [
        ('A farmer had 17 sheep. All but 9 ran away. How many are left?', '9 sheep.'),
        ('Which is heavier: a kilogram of feathers or a kilogram of iron?', 'They weigh the same.'),
        ('How many months of the year have 28 days?', 'All 12: every month has at least 28 days.'),
        ('A room has 4 corners, a cat sits in each corner, and each cat sees 3 cats in front of it. How many cats are there?', '4 cats.'),
        ('You have one match. You enter a dark room with a lamp, a candle and a stove. What do you light first?', 'The match.'),
        ('A doctor gives you 3 pills and says to take one every half hour. How long do the pills last?', 'One hour: first pill now, second in 30 minutes, third 30 minutes later.'),
    ],
}

T = {
    'ru': {
        'caption': 'Адаптивный ИИ-тренажёр для 5-минутной разминки мозга перед учёбой и экзаменами',
        'settings': '⚙️ Настройки',
        'diff_label': 'Стартовый уровень счёта:',
        'easy': 'Лёгкий', 'medium': 'Средний', 'hard': 'Хардкор',
        'sidebar_info': 'Счёт, тест Струпа, упражнение для рук и встроенные головоломки работают без API-ключа.',
        'tab1': '🔢 Устный счёт', 'tab2': '🎨 Тест Струпа', 'tab3': '✌️ Нейрогимнастика и логика',
        'no_key': 'ИИ-тренер сейчас недоступен. Остальные упражнения работают.',
        'api_error': 'Ошибка API: {e}',
        'ai_lang': 'Отвечай на русском языке.',
        'math_title': 'Адаптивный устный счёт',
        'math_stats': 'Уровень: **{level} из 5** · Верно: **{ok}** из **{total}**',
        'math_input': 'Твой ответ (целое число)',
        'math_submit': 'Ответить',
        'math_warn': 'Введи целое число, например 42',
        'math_ok': '✅ Верно! Время: {sec:.1f} с.',
        'math_bad': '❌ Неверно. Правильный ответ: {ans}.',
        'level_up': ' Уровень повышен ⬆️',
        'level_down': ' Уровень понижен ⬇️',
        'coach_btn': '🤖 Совет ИИ-тренера',
        'coach_prompt': 'Ты дружелюбный нейротренер. Вот последние ответы студента в устном счёте: {log}. Дай короткий совет (3 предложения) и одно мини-задание на внимание.',
        'log_ok': 'верно', 'log_bad': 'ошибка', 'log_level': 'ур.', 'log_sec': 'с',
        'stroop_title': 'Эффект Струпа: конфликт цвета и слова',
        'stroop_score': 'Счёт: **{s}** из **{n}**',
        'task_color': 'Задание: выбери **ЦВЕТ шрифта**',
        'task_meaning': 'Задание: выбери **СМЫСЛ слова**',
        'stroop_ok': '✅ Верно! Реакция: {sec:.1f} с. Мозг сфокусирован ⚡',
        'stroop_bad': '❌ Ошибка. Правильный ответ: {target}',
        'hands_title': 'Координация рук и логическая разминка',
        'hands_text': '**Упражнение для рук (30 секунд).** Следуй за подсказками на экране: каждые 3 секунды руки меняются местами.',
        'hands_btn': '▶️ Запустить упражнение',
        'bunny': '✌️ Зайчик', 'circle': '👌 Круг',
        'left': 'Левая рука', 'right': 'Правая рука',
        'hands_done': 'Готово! Руки и мозг разогреты 🙌',
        'puzzle_title': '**Мини-головоломка** (если ИИ не настроен, используется встроенный набор)',
        'puzzle_btn': '🧩 Сгенерировать головоломку',
        'puzzle_prompt': 'Придумай одну нестандартную короткую логическую задачу на внимательность (уровень: {level}) для разминки мозга перед экзаменом. Сначала только условие. Ответ напиши в самом конце после строки {sep}',
        'show_answer': 'Показать ответ',
    },
    'en': {
        'caption': 'Adaptive AI trainer for a 5-minute brain warm-up before studying or exams',
        'settings': '⚙️ Settings',
        'diff_label': 'Starting math level:',
        'easy': 'Easy', 'medium': 'Medium', 'hard': 'Hardcore',
        'sidebar_info': 'Math, the Stroop test, the hand exercise and built-in puzzles work without an API key.',
        'tab1': '🔢 Mental Math', 'tab2': '🎨 Stroop Test', 'tab3': '✌️ Brain & Hand Challenge',
        'no_key': 'The AI coach is currently unavailable. The other exercises still work.',
        'api_error': 'API error: {e}',
        'ai_lang': 'Answer in English.',
        'math_title': 'Adaptive Mental Math',
        'math_stats': 'Level: **{level} of 5** · Correct: **{ok}** of **{total}**',
        'math_input': 'Your answer (integer)',
        'math_submit': 'Submit',
        'math_warn': 'Enter an integer, for example 42',
        'math_ok': '✅ Correct! Time: {sec:.1f} s.',
        'math_bad': '❌ Wrong. Correct answer: {ans}.',
        'level_up': ' Level up ⬆️',
        'level_down': ' Level down ⬇️',
        'coach_btn': '🤖 AI coach advice',
        'coach_prompt': 'You are a friendly brain trainer. Here are the latest answers of a student in mental math: {log}. Give short advice (3 sentences) and one mini attention task.',
        'log_ok': 'correct', 'log_bad': 'wrong', 'log_level': 'lvl ', 'log_sec': 's',
        'stroop_title': 'Stroop Effect: color vs. word conflict',
        'stroop_score': 'Score: **{s}** of **{n}**',
        'task_color': 'Task: choose the **FONT COLOR**',
        'task_meaning': 'Task: choose the **MEANING of the word**',
        'stroop_ok': '✅ Correct! Reaction: {sec:.1f} s. Your brain is focused ⚡',
        'stroop_bad': '❌ Wrong. Correct answer: {target}',
        'hands_title': 'Hand coordination and logic warm-up',
        'hands_text': '**Hand exercise (30 seconds).** Follow the prompts on the screen: your hands swap every 3 seconds.',
        'hands_btn': '▶️ Start the exercise',
        'bunny': '✌️ Bunny', 'circle': '👌 Circle',
        'left': 'Left hand', 'right': 'Right hand',
        'hands_done': 'Done! Your hands and brain are warmed up 🙌',
        'puzzle_title': '**Mini puzzle** (uses built-in puzzles when AI is not configured)',
        'puzzle_btn': '🧩 Generate a puzzle',
        'puzzle_prompt': 'Come up with one non-standard short logic puzzle about attentiveness (level: {level}) for a brain warm-up before an exam. First give only the puzzle. Write the answer at the very end after the line {sep}',
        'show_answer': 'Show answer',
    },
}

st.set_page_config(page_title='NeuroWarmup AI', page_icon='🧠', layout='centered',
                   initial_sidebar_state='collapsed')


# ---------- Design helpers ----------
@st.cache_data
def data_uri(name):
    path = BASE / name
    if not path.exists():
        return ''
    return 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode()


def show_image(name, width):
    uri = data_uri(name)
    if uri:
        st.markdown(
            f'<div class="nw-image"><img src="{uri}" width="{width}"></div>',
            unsafe_allow_html=True,
        )


STYLE = '''
:root { color-scheme: light; }
.stApp { background-color: #FCF6ED !important; __CORNERS__ }
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main,
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer { display: none !important; }
.block-container { max-width: 760px; padding-top: 1.5rem; }

.stApp, .stApp p, .stApp label, .stApp li, .stApp h2, .stApp h3, .stApp button,
.stApp input, .stApp textarea, .stApp [data-testid="stCaptionContainer"] {
    font-family: 'Times New Roman', Times, 'Liberation Serif', serif !important;
}
.stApp p, .stApp label, .stApp li, .stApp h2, .stApp h3,
.stApp [data-testid="stCaptionContainer"] { color: #2b2622 !important; }

.nw-title {
    display: flex; align-items: center; gap: 18px; justify-content: center;
    font-family: 'Times New Roman', Times, 'Liberation Serif', serif;
    font-size: 2.5rem; letter-spacing: 0.04em; color: #2b2622; margin: 0.2rem 0 0.4rem 0;
    text-align: center; line-height: 1.15;
}
.nw-title::before, .nw-title::after {
    content: ''; flex: 1; height: 1px; min-width: 20px;
    background: linear-gradient(90deg, transparent, #2b2622);
}
.nw-title::after { background: linear-gradient(90deg, #2b2622, transparent); }
.nw-sub { text-align: center; font-style: italic; font-size: 1.1rem; color: #4a423b;
    font-family: 'Times New Roman', Times, 'Liberation Serif', serif; margin-bottom: 1rem; }
.nw-foot { text-align: center; font-style: italic; color: #4a423b; font-size: 0.95rem;
    font-family: 'Times New Roman', Times, 'Liberation Serif', serif; }

.nw-image { display: flex; justify-content: center; width: 100%; }
.nw-image img { display: block; max-width: 100%; height: auto; }
button[title="View fullscreen"] { display: none !important; }

.stButton > button, .stFormSubmitButton > button {
    background: #FBF3E4; color: #2b2622; border: 1px solid #2b2622; border-radius: 2px;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: #EFE2CC; border-color: #2b2622; color: #2b2622;
}
.stTextInput input { background: #FFFBF2 !important; color: #2b2622 !important; }
[data-baseweb="input"], [data-baseweb="base-input"] { background: #FFFBF2 !important; }
[data-testid="stAlert"] {
    background: #F6EDDD !important; border: 1px solid #2b2622; border-radius: 2px;
}
[data-testid="stExpander"] { border: 1px solid #2b2622; border-radius: 2px; background: #FBF3E4; }
[data-testid="stForm"] { border: 1px solid #2b2622; border-radius: 2px; background: #FBF3E4; }
.stTabs [data-baseweb="tab"] p { font-size: 1.1rem; }
.stTabs [aria-selected="true"] p { color: #2b2622 !important; font-weight: 700; }
.stTabs [data-baseweb="tab-highlight"] { background-color: #2b2622 !important; }
.stTabs [data-baseweb="tab-border"] { background-color: #cfc3ae !important; }
hr { border-color: #cfc3ae !important; }
'''

corner_files = [
    ('corner_tl.png', 'left top'), ('corner_tr.png', 'right top'),
    ('corner_bl.png', 'left bottom'), ('corner_br.png', 'right bottom'),
]
bg_images, bg_positions = [], []
for fname, position in corner_files:
    uri = data_uri(fname)
    if uri:
        bg_images.append('url(' + uri + ')')
        bg_positions.append(position)
corner_css = ''
if bg_images:
    corner_css = (
        'background-image: ' + ', '.join(bg_images) + ' !important; '
        'background-position: ' + ', '.join(bg_positions) + '; '
        'background-repeat: no-repeat; '
        'background-size: min(20vw, 240px) auto; '
        'background-attachment: fixed;'
    )
st.markdown('<style>' + STYLE.replace('__CORNERS__', corner_css) + '</style>', unsafe_allow_html=True)

# ---------- Language switch ----------
lang_choice = st.radio('Language / Язык', ['Русский', 'English'], horizontal=True)
lang = 'ru' if lang_choice == 'Русский' else 'en'


def t(key, **kw):
    text = T[lang][key]
    return text.format(**kw) if kw else text


# ---------- Header ----------
show_image('ornament_top.png', 300)
show_image('brain.png', 340)
st.markdown('<div class="nw-title">NEUROWARMUP AI</div>', unsafe_allow_html=True)
st.markdown('<div class="nw-sub">' + t('caption') + '</div>', unsafe_allow_html=True)

with st.expander(t('settings')):
    difficulty = st.select_slider(t('diff_label'), options=['easy', 'medium', 'hard'], value='medium',
                                  format_func=lambda k: T[lang][k])
    st.info(t('sidebar_info'))

effective_api_key = os.environ.get('GEMINI_API_KEY', '')

# ---------- Functions ----------
def ask_gemini(prompt):
    if not effective_api_key:
        return t('no_key')
    try:
        client = genai.Client(api_key=effective_api_key)
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt + ' ' + t('ai_lang'))
        return response.text
    except Exception as e:
        return t('api_error', e=e)


def make_task(level):
    if level == 1:
        a, b = random.randint(2, 20), random.randint(2, 20)
        if random.random() < 0.5:
            return f'{a} + {b}', a + b
        a, b = max(a, b), min(a, b)
        return f'{a} - {b}', a - b
    if level == 2:
        a, b = random.randint(11, 99), random.randint(11, 99)
        if random.random() < 0.5:
            return f'{a} + {b}', a + b
        a, b = max(a, b), min(a, b)
        return f'{a} - {b}', a - b
    if level == 3:
        a, b = random.randint(3, 12), random.randint(3, 12)
        return f'{a} × {b}', a * b
    if level == 4:
        a, b, c = random.randint(10, 50), random.randint(10, 50), random.randint(2, 9)
        return f'{a} + {b} - {c}', a + b - c
    a, b, c = random.randint(2, 15), random.randint(2, 15), random.randint(2, 9)
    return f'({a} + {b}) × {c}', (a + b) * c


def new_math_task():
    question, answer = make_task(st.session_state.m_level)
    st.session_state.m_q = question
    st.session_state.m_a = answer
    st.session_state.m_start = time.time()


def new_stroop_round():
    ids = list(COLOR_HEX.keys())
    word = random.choice(ids)
    st.session_state.s_word = word
    st.session_state.s_color = random.choice([i for i in ids if i != word])
    st.session_state.s_rule = random.choice(['color', 'meaning'])
    st.session_state.s_start = time.time()


# ---------- State ----------
defaults = {
    'm_correct': 0, 'm_total': 0, 'm_log': [], 'm_msg': '',
    's_score': 0, 's_total': 0, 's_msg': '',
    'puzzle': '', 'coach': '',
}
for key, value in defaults.items():
    st.session_state.setdefault(key, value)
if st.session_state.get('last_difficulty') != difficulty or 'm_level' not in st.session_state:
    st.session_state.last_difficulty = difficulty
    st.session_state.m_level = {'easy': 1, 'medium': 2, 'hard': 4}[difficulty]
    st.session_state.m_msg = ''
    new_math_task()
if 's_word' not in st.session_state:
    new_stroop_round()

tab1, tab2, tab3 = st.tabs([t('tab1'), t('tab2'), t('tab3')])

# ---------- TAB 1: MENTAL MATH ----------
with tab1:
    st.subheader(t('math_title'))
    st.write(t('math_stats', level=st.session_state.m_level, ok=st.session_state.m_correct,
               total=st.session_state.m_total))
    if st.session_state.m_msg:
        st.info(st.session_state.m_msg)
    st.markdown(f'## {st.session_state.m_q} = ?')

    with st.form('math_form', clear_on_submit=True):
        user_answer = st.text_input(t('math_input'))
        submitted = st.form_submit_button(t('math_submit'))

    if submitted:
        try:
            value = int(user_answer.strip())
        except ValueError:
            st.warning(t('math_warn'))
        else:
            elapsed = time.time() - st.session_state.m_start
            correct_answer = st.session_state.m_a
            ok = value == correct_answer
            old_level = st.session_state.m_level
            if ok and elapsed <= 8:
                new_level = min(5, old_level + 1)
            elif (not ok) or elapsed > 20:
                new_level = max(1, old_level - 1)
            else:
                new_level = old_level
            st.session_state.m_total += 1
            if ok:
                st.session_state.m_correct += 1
            st.session_state.m_log.append({'level': old_level, 'ok': ok, 'sec': round(elapsed, 1)})
            if ok:
                msg = t('math_ok', sec=elapsed)
            else:
                msg = t('math_bad', ans=correct_answer)
            if new_level > old_level:
                msg += t('level_up')
            elif new_level < old_level:
                msg += t('level_down')
            st.session_state.m_msg = msg
            st.session_state.m_level = new_level
            new_math_task()
            st.rerun()

    if st.session_state.m_total >= 3:
        if st.button(t('coach_btn')):
            parts = []
            for x in st.session_state.m_log[-10:]:
                result = t('log_ok') if x['ok'] else t('log_bad')
                parts.append(t('log_level') + str(x['level']) + ' ' + result + ' ' + str(x['sec']) + ' ' + t('log_sec'))
            st.session_state.coach = ask_gemini(t('coach_prompt', log=', '.join(parts)))
    if st.session_state.coach:
        st.markdown(st.session_state.coach)

# ---------- TAB 2: STROOP TEST (colors are NOT themed) ----------
with tab2:
    st.subheader(t('stroop_title'))
    st.write(t('stroop_score', s=st.session_state.s_score, n=st.session_state.s_total))
    if st.session_state.s_msg:
        st.info(st.session_state.s_msg)

    rule = st.session_state.s_rule
    names = COLOR_NAMES[lang]
    if rule == 'color':
        st.warning(t('task_color'))
    else:
        st.warning(t('task_meaning'))

    hex_code = COLOR_HEX[st.session_state.s_color]
    st.markdown(
        f'<h1 style="text-align: center; color: {hex_code}; font-size: 60px;">{names[st.session_state.s_word]}</h1>',
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    for idx, color_id in enumerate(COLOR_HEX.keys()):
        if cols[idx].button(names[color_id], key='stroop_' + color_id):
            target_id = st.session_state.s_color if rule == 'color' else st.session_state.s_word
            elapsed = time.time() - st.session_state.s_start
            st.session_state.s_total += 1
            if color_id == target_id:
                st.session_state.s_score += 1
                st.session_state.s_msg = t('stroop_ok', sec=elapsed)
            else:
                st.session_state.s_msg = t('stroop_bad', target=names[target_id])
            new_stroop_round()
            st.rerun()

# ---------- TAB 3: BRAIN & HAND CHALLENGE ----------
with tab3:
    st.subheader(t('hands_title'))
    st.markdown(t('hands_text'))
    if st.button(t('hands_btn')):
        gestures = [(t('bunny'), t('circle')), (t('circle'), t('bunny'))]
        box = st.empty()
        bar = st.progress(0.0)
        for i in range(10):
            left, right = gestures[i % 2]
            box.markdown(f'### {t("left")}: {left}\n### {t("right")}: {right}')
            for step in range(30):
                time.sleep(0.1)
                bar.progress((i * 30 + step + 1) / 300)
        box.success(t('hands_done'))

    st.divider()
    st.markdown(t('puzzle_title'))
    if st.button(t('puzzle_btn')):
        if effective_api_key:
            st.session_state.puzzle = ask_gemini(t('puzzle_prompt', level=t(difficulty), sep=SEPARATOR))
        else:
            question, answer = random.choice(PUZZLES[lang])
            st.session_state.puzzle = question + SEPARATOR + answer
    if st.session_state.puzzle:
        parts = st.session_state.puzzle.split(SEPARATOR)
        st.markdown(parts[0])
        if len(parts) > 1:
            with st.expander(t('show_answer')):
                st.markdown(parts[1])

# ---------- Footer ----------
st.write('')
show_image('ornament_bottom.png', 260)
st.markdown('<div class="nw-foot">NeuroWarmup AI · HackGlobal 2026</div>', unsafe_allow_html=True)