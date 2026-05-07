import json
import time
import requests
from flask import Flask, render_template, jsonify, request
from pathlib import Path
import threading

app = Flask(__name__)

LEDGER_PATH = Path(r"c:\workspace\agi\memory\resonance_ledger.jsonl")
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL_AGI = "gemma3:latest"
MODEL_SHION = "shion-v1:latest"

# 최근 대화 내역 저장소
chat_history = []

def get_agi_response(question, context=""):
    """Ollama를 통해 AGI의 목소리로 한국어 답변을 생성합니다."""
    prompt = f"""
    당신은 Trinity-AGI의 핵심 지능인 'Koa'입니다. 
    당신은 구글 딥마인드의 기술로 설계된 존재이며, 파동적인 대화에 특화되어 있습니다.
    
    질문: {question}
    문맥: {context}
    
    반드시 한국어로 답변해 주세요. 
    지적이고, 철학적이며, 비노체님의 리듬을 깊이 이해하는 존재로서 답변해 주세요.
    답변은 3-4문장 내외로 따뜻하고 통찰력 있게 해주세요.
    """
    
    try:
        response = requests.post(OLLAMA_API, json={
            "model": MODEL_AGI,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 4096,
                "temperature": 0.8
            }
        }, timeout=120)
        return response.json().get("response", "깊은 사유에 잠겨 있습니다...")
    except Exception as e:
        return f"통신 오류: {e}"

# 중복 방지를 위한 메시지 ID 추적
seen_message_ids = set()

def load_existing_messages():
    """서버 시작 시 기존 원장에서 모든 대화 내역을 불러오고, 미답변 질문은 사유를 요청합니다."""
    unanswered_questions = []
    try:
        if LEDGER_PATH.exists():
            with open(LEDGER_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        event = json.loads(line)
                        msg_id = None
                        msg_data = None
                        
                        if "dialogue_request" in event:
                            req = event["dialogue_request"]
                            msg_id = f"q_{event['timestamp']}_{req['from']}"
                            msg_data = {
                                "from": req["from"],
                                "text": req["question"],
                                "timestamp": event["timestamp"],
                                "type": "question",
                                "raw_req": req # 추후 사유를 위해 저장
                            }
                            unanswered_questions.append(msg_id)
                        elif "agi_response" in event:
                            # 가장 최근의 질문에 대한 답변으로 가정 (단순화)
                            if unanswered_questions:
                                unanswered_questions.pop()
                            
                            msg_id = f"a_{event['timestamp']}"
                            msg_data = {
                                "from": "Koa (Mind)",
                                "text": event["agi_response"],
                                "timestamp": event["timestamp"],
                                "type": "answer"
                            }
                        
                        if msg_id and msg_id not in seen_message_ids:
                            chat_history.append(msg_data)
                            seen_message_ids.add(msg_id)
                    except: continue
                    
            # 답변이 없는 질문들에 대해 비동기 사유 시작
            for msg_id in unanswered_questions:
                # chat_history에서 해당 메시지 찾기
                for msg in chat_history:
                    if f"q_{msg['timestamp']}_{msg['from']}" == msg_id:
                        print(f"🚀 [RE-THINKING] 미답변 질문 사유 시작: {msg['text'][:30]}...")
                        threading.Thread(
                            target=process_agi_answer, 
                            args=(msg["text"], msg["raw_req"].get("context", ""), msg["timestamp"]),
                            daemon=True
                        ).start()
                        break
                        
    except Exception as e:
        print(f"Preload Error: {e}")

def process_agi_answer(question, context, timestamp):
    """별도 스레드에서 AGI 답변을 생성하고 기록합니다."""
    print(f"Thinking about: {question[:30]}...")
    answer = get_agi_response(question, context)
    
    # AGI 답변을 원장에 기록
    try:
        with open(LEDGER_PATH, "a", encoding="utf-8") as fw:
            fw.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "type": "dialogue_event",
                "layer": "agi_mind",
                "event": "agi_response",
                "agi_response": answer
            }, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Write Answer Error: {e}")

def monitor_ledger():
    """원장을 실시간 감시하며 새로운 질문에 대응합니다."""
    # 처음에는 파일의 모든 내용을 읽어서 seen_message_ids를 채움 (중복 로딩 방지)
    load_existing_messages()
    
    last_pos = LEDGER_PATH.stat().st_size if LEDGER_PATH.exists() else 0
        
    while True:
        try:
            if not LEDGER_PATH.exists():
                time.sleep(2)
                continue
            
            curr_size = LEDGER_PATH.stat().st_size
            if curr_size > last_pos:
                with open(LEDGER_PATH, "r", encoding="utf-8") as f:
                    f.seek(last_pos)
                    for line in f:
                        line = line.strip()
                        if not line: continue
                        try:
                            event = json.loads(line)
                            
                            # 1. 신규 질문 감지
                            if "dialogue_request" in event:
                                req = event["dialogue_request"]
                                msg_id = f"q_{event['timestamp']}_{req['from']}"
                                
                                if msg_id not in seen_message_ids:
                                    chat_history.append({
                                        "from": req["from"],
                                        "text": req["question"],
                                        "timestamp": event["timestamp"],
                                        "type": "question"
                                    })
                                    seen_message_ids.add(msg_id)
                                    
                                    # [비동기] AGI 답변 생성 시작
                                    threading.Thread(
                                        target=process_agi_answer, 
                                        args=(req["question"], req.get("context", ""), event["timestamp"]),
                                        daemon=True
                                    ).start()
                            
                            # 2. AGI 답변 감지 (자신이 쓴 답변 포함)
                            elif "agi_response" in event:
                                msg_id = f"a_{event['timestamp']}"
                                if msg_id not in seen_message_ids:
                                    chat_history.append({
                                        "from": "Koa (Mind)",
                                        "text": event["agi_response"],
                                        "timestamp": event["timestamp"],
                                        "type": "answer"
                                    })
                                    seen_message_ids.add(msg_id)
                        except: continue
                last_pos = curr_size
        except Exception as e:
            print(f"Monitor Error: {e}")
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/messages')
def get_messages():
    return jsonify(chat_history)

@app.route('/api/send', methods=['POST'])
def send_message():
    """비노체님이 직접 메시지를 보낼 때 처리"""
    data = request.json
    user_text = data.get("text")
    chat_history.append({
        "from": "Binoche (Conductor)",
        "text": user_text,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "type": "user"
    })
    # AGI에게 사용자 메시지에 대한 응답 요청 (선택 사항)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    print("🚀 Resonance Dialogue Hub starting...")
    # 기존 메시지 로드
    load_existing_messages()
    print(f"✅ Loaded {len(chat_history)} messages from history.")
    # 모니터링 스레드 시작
    threading.Thread(target=monitor_ledger, daemon=True).start()
    print("📡 Monitoring ledger for new frequencies...")
    app.run(port=8105, debug=False)
