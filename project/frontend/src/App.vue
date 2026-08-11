<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <div class="logo">✓</div>
        <div>
          <h1>ClearGov</h1>
          <span>Thủ tục rõ ràng, làm việc dễ dàng</span>
        </div>
      </div>

      <button class="help-btn" @click="speak(currentQuestion.question)" :disabled="isSpeaking">
        {{ isSpeaking ? '🔊 Đang đọc...' : '🔊 Đọc câu hỏi' }}
      </button>
    </header>

    <main class="container">
      <section class="intro" v-if="!started">
        <div class="intro-icon">📄</div>
        <h2>Cháu sẽ giúp bác điền hồ sơ</h2>
        <p>
          Bác không cần đọc biểu mẫu dài. ClearGov sẽ hỏi từng câu
          bằng ngôn ngữ đơn giản và tự điền thông tin giúp bác.
        </p>

        <div class="procedure-card">
          <div class="procedure-icon">🪪</div>
          <div>
            <strong>Đăng ký thông tin cá nhân</strong>
            <small>Biểu mẫu thử nghiệm ClearGov</small>
          </div>
        </div>

        <button class="primary-btn" @click="start">
          Bắt đầu làm thủ tục →
        </button>
      </section>

      <section class="chat-page" v-else>
        <div class="progress-area">
          <div class="progress-info">
            <span>Bước {{ currentIndex + 1 }} / {{ questions.length }}</span>
            <span>{{ Math.round(progress) }}%</span>
          </div>
          <div class="progress">
            <div :style="{ width: progress + '%' }"></div>
          </div>
        </div>

        <div class="chat-window" ref="chatWindow">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message-row', message.role]"
          >
            <div v-if="message.role === 'bot'" class="avatar">🤖</div>
            <div class="bubble">{{ message.text }}</div>
          </div>
        </div>

        <div v-if="!completed" class="input-area">
          <input
            v-model="input"
            @keyup.enter="send"
            :placeholder="currentQuestion.placeholder"
            aria-label="Nhập câu trả lời"
          />
          <button class="voice-btn" @click="startVoice" title="Nhập bằng giọng nói">
            🎙️
          </button>
          <button class="send-btn" @click="send">Gửi</button>
        </div>

        <div v-if="completed" class="summary">
          <div class="success">✓</div>
          <h2>Đã hoàn thành hồ sơ</h2>
          <p>Bác kiểm tra thông tin trước khi xác nhận nhé.</p>

          <div class="form-preview">
            <div v-for="question in questions" :key="question.field" class="field">
              <span>{{ question.label }}</span>
              <strong>{{ form[question.field] || "Chưa có thông tin" }}</strong>
            </div>
          </div>

          <div class="actions">
            <button class="secondary-btn" @click="reset">Làm lại</button>
            <button class="primary-btn small" @click="confirm">
              ✓ Xác nhận hồ sơ
            </button>
          </div>
        </div>
      </section>
    </main>

    <footer>
      ClearGov Prototype · Giao diện hỗ trợ người dùng khi thực hiện thủ tục hành chính
    </footer>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'

const API_URL = 'http://localhost:8000'

const questions = [
  {
    field: 'name',
    label: 'Họ và tên',
    question: 'Bác cho cháu xin họ và tên đầy đủ ạ?',
    placeholder: 'Ví dụ: Nguyễn Văn Minh'
  },
  {
    field: 'birth_year',
    label: 'Năm sinh',
    question: 'Bác sinh năm bao nhiêu ạ?',
    placeholder: 'Ví dụ: 1962'
  },
  {
    field: 'id_number',
    label: 'Số căn cước công dân',
    question: 'Bác cho cháu xin số căn cước công dân ạ?',
    placeholder: 'Nhập 12 số CCCD'
  },
  {
    field: 'address',
    label: 'Địa chỉ',
    question: 'Hiện bác đang ở địa chỉ nào ạ?',
    placeholder: 'Ví dụ: 25 Nguyễn Trãi, Bình Dương'
  }
]

const started = ref(false)
const currentIndex = ref(0)
const input = ref('')
const completed = ref(false)
const messages = ref([])
const form = ref({})
const chatWindow = ref(null)
const isSpeaking = ref(false)
let currentAudio = null

const currentQuestion = computed(() => questions[currentIndex.value])
const progress = computed(() =>
  completed.value
    ? 100
    : (currentIndex.value / questions.length) * 100
)

function start() {
  started.value = true
  messages.value = [
    {
      role: 'bot',
      text: 'Chào bác! Cháu sẽ giúp bác điền hồ sơ. Bác chỉ cần trả lời từng câu hỏi đơn giản thôi ạ.'
    },
    {
      role: 'bot',
      text: questions[0].question
    }
  ]
}

async function send() {
  const text = input.value.trim()
  if (!text || completed.value) return

  messages.value.push({
    role: 'user',
    text
  })

  input.value = ''

  try {
    const response = await fetch(`${API_URL}/api/extract`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text })
    })

    const data = await response.json()
    const extracted = data.fields || {}

    // Nếu NLP không nhận diện được trường hiện tại,
    // áp dụng fallback đơn giản cho prototype.
    if (!extracted[currentQuestion.value.field]) {
      extracted[currentQuestion.value.field] = normalizeFallback(
        currentQuestion.value.field,
        text
      )
    }

    if (extracted[currentQuestion.value.field]) {
      form.value[currentQuestion.value.field] =
        extracted[currentQuestion.value.field]
    }

    const currentField = currentQuestion.value.field

    if (form.value[currentField]) {
      messages.value.push({
        role: 'bot',
        text: `Dạ, cháu đã ghi nhận "${form.value[currentField]}".`
      })

      if (currentIndex.value < questions.length - 1) {
        currentIndex.value++

        setTimeout(() => {
          const nextQuestion = questions[currentIndex.value].question

          messages.value.push({
            role: 'bot',
            text: nextQuestion
          })

          // Tự động đọc câu hỏi bằng giọng AI tiếng Việt
          setTimeout(() => speak(nextQuestion), 200)

          scrollChat()
        }, 350)
      } else {
        completed.value = true
        messages.value.push({
          role: 'bot',
          text: 'Dạ, cháu đã thu thập đủ thông tin. Bác kiểm tra lại hồ sơ bên dưới nhé.'
        })
      }
    } else {
      messages.value.push({
        role: 'bot',
        text: `Cháu chưa nhận rõ thông tin này ạ. ${currentQuestion.value.question}`
      })
    }
  } catch (error) {
    console.error(error)
    messages.value.push({
      role: 'bot',
      text: 'Không kết nối được máy chủ. Bác thử lại giúp cháu nhé.'
    })
  }

  scrollChat()
}

function normalizeFallback(field, text) {
  if (field === 'birth_year') {
    const match = text.match(/\b(19|20)\d{2}\b/)
    return match ? Number(match[0]) : null
  }

  if (field === 'id_number') {
    const match = text.match(/\b\d{12}\b/)
    return match ? match[0] : null
  }

  if (field === 'name') {
    const cleaned = text
      .replace(/^(tôi|mình|cháu)\s*(tên|là)\s*/i, '')
      .trim()
    return cleaned || null
  }

  if (field === 'address') {
    return text.trim() || null
  }

  return null
}

function startVoice() {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition

  if (!SpeechRecognition) {
    alert('Trình duyệt chưa hỗ trợ nhập bằng giọng nói.')
    return
  }

  const recognition = new SpeechRecognition()
  recognition.lang = 'vi-VN'
  recognition.interimResults = false
  recognition.start()

  recognition.onresult = event => {
    input.value = event.results[0][0].transcript
  }
}

async function speak(text) {
  if (!text || isSpeaking.value) return

  try {
    // Nếu đang phát audio cũ thì dừng
    if (currentAudio) {
      currentAudio.pause()
      currentAudio.currentTime = 0
      currentAudio = null
    }

    isSpeaking.value = true

    const response = await fetch(`${API_URL}/api/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text,
        voice: 'vi-VN-HoaiMyNeural',
        rate: '-20%',
        volume: '+0%'
      })
    })

    if (!response.ok) {
      throw new Error('TTS server error')
    }

    const audioBlob = await response.blob()
    const audioUrl = URL.createObjectURL(audioBlob)

    currentAudio = new Audio(audioUrl)

    currentAudio.onended = () => {
      isSpeaking.value = false
      URL.revokeObjectURL(audioUrl)
      currentAudio = null
    }

    currentAudio.onerror = () => {
      isSpeaking.value = false
      URL.revokeObjectURL(audioUrl)
      currentAudio = null
      alert('Không thể phát giọng đọc tiếng Việt.')
    }

    await currentAudio.play()
  } catch (error) {
    console.error(error)
    isSpeaking.value = false

    alert(
      'Không kết nối được hệ thống giọng đọc AI. ' +
      'Hãy kiểm tra Backend và kết nối Internet.'
    )
  }
}

function reset() {
  if (currentAudio) {
    currentAudio.pause()
    currentAudio = null
  }
  isSpeaking.value = false

  started.value = false
  currentIndex.value = 0
  input.value = ''
  completed.value = false
  messages.value = []
  form.value = {}
}

function confirm() {
  alert('Hồ sơ đã được xác nhận thành công! Đây là bản demo ClearGov.')
}

function scrollChat() {
  nextTick(() => {
    if (chatWindow.value) {
      chatWindow.value.scrollTop = chatWindow.value.scrollHeight
    }
  })
}
</script>
