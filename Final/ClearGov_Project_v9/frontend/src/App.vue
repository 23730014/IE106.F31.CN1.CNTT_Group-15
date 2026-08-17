<template>
  <!-- ==========================================================
       13. TEMPLATE / GIAO DIỆN
       ========================================================== -->
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <div class="logo" aria-hidden="true">✓</div>
        <div>
          <h1>ClearGov</h1>
          <span>Thủ tục rõ ràng, làm việc dễ dàng</span>
        </div>
      </div>

      <div class="topbar-actions">
        <button
          v-if="!submitted && started && !completed"
          class="help-btn"
          @click="speak(currentQuestion.question)"
          :disabled="isSpeaking"
          :aria-label="isSpeaking ? 'Đang đọc câu hỏi' : 'Đọc to câu hỏi hiện tại'"
        >
          <span aria-hidden="true">🔊</span>
          <span class="label">{{ isSpeaking ? 'Đang đọc...' : 'Đọc câu hỏi' }}</span>
        </button>
        <SupportLink />
      </div>
    </header>

    <main class="container">
      <section class="intro" v-if="!started">
        <div class="intro-icon" aria-hidden="true">📄</div>
        <h2>Cháu sẽ giúp bác điền hồ sơ</h2>
        <p>
          Bác không cần đọc biểu mẫu dài. ClearGov sẽ hỏi từng câu
          bằng ngôn ngữ đơn giản và tự điền thông tin giúp bác.
        </p>

        <div class="procedure-card">
          <div class="procedure-icon" aria-hidden="true">🪪</div>
          <div>
            <strong>Đăng ký thông tin cá nhân</strong>
            <small>Biểu mẫu thử nghiệm ClearGov</small>
          </div>
        </div>

        <AppButton variant="primary" @click="start">
          Bắt đầu làm thủ tục →
        </AppButton>

        <div class="image-upload-card">
          <div class="upload-title">📷 Hoặc lấy thông tin từ hình ảnh</div>
          <p>Chụp/tải ảnh CCCD hoặc giấy tờ có thông tin cá nhân. ClearGov sẽ đọc chữ trong ảnh và tự điền các trường nhận diện được.</p>

          <label class="upload-btn">
            {{ ocrLoading ? '⏳ Đang đọc hình ảnh...' : '📤 Tải hình ảnh lên' }}
            <input
              type="file"
              accept="image/*"
              @change="handleImageUpload"
              :disabled="ocrLoading"
              aria-label="Tải ảnh giấy tờ tùy thân lên để tự động đọc thông tin"
              hidden
            />
          </label>

          <StatusMessage variant="error" :text="uploadError" />

          <div v-if="imagePreview" class="image-preview-wrap">
            <img :src="imagePreview" alt="Ảnh giấy tờ đã tải lên" class="image-preview" />
          </div>

          <StatusMessage variant="info" :text="ocrStatus" />

          <div v-if="Object.keys(imageExtracted).length" class="image-result">
            <strong>Thông tin đọc được:</strong>
            <div v-for="question in questions" :key="question.field" class="image-field">
              <span>{{ question.label }}</span>
              <strong>{{ imageExtracted[question.field] || 'Không nhận diện được' }}</strong>
            </div>
            <AppButton variant="secondary" size="small" @click="startWithImageData">
              Dùng thông tin này →
            </AppButton>
          </div>
        </div>
      </section>

      <section class="chat-page" v-else>
        <ProgressBar
          v-if="!submitted"
          :step="currentIndex + 1"
          :total="questions.length"
          :percent="progress"
        />

        <div
          v-if="!submitted"
          class="chat-window"
          ref="chatWindow"
          role="log"
          aria-live="polite"
          aria-relevant="additions"
        >
          <ChatBubble
            v-for="(message, index) in messages"
            :key="index"
            :role="message.role"
            :text="message.text"
          />
        </div>

        <FieldHint v-if="!completed && currentQuestion.hint" :text="currentQuestion.hint" />

        <div v-if="!completed" class="input-area">
          <AppButton
            variant="back"
            :disabled="currentIndex === 0"
            aria-label="Quay lại câu hỏi trước"
            @click="goBack"
          >
            ← Quay lại
          </AppButton>
          <input
            v-model="input"
            @keyup.enter="send"
            :placeholder="currentQuestion.placeholder"
            aria-label="Nhập câu trả lời"
          />
          <AppButton
            variant="voice"
            icon="🎙️"
            icon-only
            aria-label="Nhập bằng giọng nói"
            title="Nhập bằng giọng nói"
            @click="startVoice"
          />
          <AppButton variant="send" @click="send">Gửi</AppButton>
        </div>

        <div v-if="completed && !submitted" class="summary">
          <div class="success" aria-hidden="true">✓</div>
          <h2>Đã hoàn thành hồ sơ</h2>
          <p>Bác kiểm tra thông tin trước khi xác nhận nhé.</p>

          <div class="edit-hint">
            ✏️ Bác có thể bấm vào từng ô bên dưới để sửa thông tin trước khi xác nhận hồ sơ.
          </div>

          <div class="form-preview editable-form">
            <div v-for="question in questions" :key="question.field" class="field editable-field">
              <label :for="`summary-${question.field}`">{{ question.label }}</label>
              <input
                :id="`summary-${question.field}`"
                v-model="form[question.field]"
                :type="question.field === 'birth_year' ? 'number' : 'text'"
                :placeholder="question.placeholder"
                :inputmode="question.field === 'id_number' || question.field === 'birth_year' ? 'numeric' : 'text'"
                :maxlength="question.field === 'id_number' ? 12 : undefined"
                @input="sanitizeFormField(question.field)"
              />
            </div>
          </div>

          <StatusMessage variant="error" :text="formError" />

          <div class="actions confirm-only-actions">
            <AppButton variant="primary" size="small" @click="confirm">
              ✓ Xác nhận hồ sơ
            </AppButton>
          </div>
        </div>

        <div v-if="submitted" class="summary submitted-summary" role="status">
          <div class="success" aria-hidden="true">✓</div>
          <h2>Hồ sơ đã được nộp thành công</h2>
          <p>Thông tin dưới đây là hồ sơ bác đã xác nhận và nộp.</p>

          <div class="form-preview submitted-form">
            <div v-for="question in questions" :key="question.field" class="field">
              <label>{{ question.label }}</label>
              <div class="submitted-value">{{ submittedForm[question.field] }}</div>
            </div>
          </div>

          <div class="submitted-note">
            🔒 Hồ sơ đã được xác nhận. Bác không thể chỉnh sửa thông tin trên trang này.
          </div>

          <div class="actions">
            <AppButton variant="secondary" @click="reset">
              Làm lại
            </AppButton>
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
// ============================================================
// CLEARGOV - APP.VUE
// FILE CHÍNH CỦA FRONTEND
//
// Luồng chính:
// Trang đầu → Upload ảnh → OCR → Trích xuất thông tin
// → Chỉnh sửa → Xác nhận → Trang hồ sơ đã nộp (read-only)
// → Làm lại → Trang đầu
// ============================================================

// ---------- 1. IMPORT THƯ VIỆN ----------
import { computed, nextTick, ref } from 'vue'
import { createWorker } from 'tesseract.js'
import AppButton from './components/AppButton.vue'
import ProgressBar from './components/ProgressBar.vue'
import ChatBubble from './components/ChatBubble.vue'
import FieldHint from './components/FieldHint.vue'
import StatusMessage from './components/StatusMessage.vue'
import SupportLink from './components/SupportLink.vue'

// ---------- 2. CẤU HÌNH API BACKEND ----------
// API này nhận text OCR và trả về các trường hồ sơ đã trích xuất.
const API_URL = 'http://localhost:8000'

// ---------- 3. CẤU HÌNH CÁC TRƯỜNG HỒ SƠ ----------
// field: tên dữ liệu; label: nhãn hiển thị; question: câu hỏi cho người dùng.
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
    placeholder: 'Nhập 12 số CCCD',
    hint: 'Số CCCD gồm đúng 12 chữ số, in ở mặt trước thẻ Căn cước công dân của bác.'
  },
  {
    field: 'address',
    label: 'Địa chỉ',
    question: 'Hiện bác đang ở địa chỉ nào ạ?',
    placeholder: 'Ví dụ: 25 Nguyễn Trãi, Bình Dương',
    hint: 'Bác ghi số nhà, tên đường, phường/xã và tỉnh/thành nơi bác đang ở.'
  }
]

// ---------- 5. STATE ĐIỀU KHIỂN GIAO DIỆN ----------
// started/completed quyết định màn hình nào đang được hiển thị.
const started = ref(false)
const currentIndex = ref(0)
const input = ref('')
const completed = ref(false)
const messages = ref([])
// ---------- 4. STATE / DỮ LIỆU FORM ----------
// form là dữ liệu có thể chỉnh sửa trước khi xác nhận.
const form = ref({})
const chatWindow = ref(null)
const isSpeaking = ref(false)
let currentAudio = null

const ocrLoading = ref(false)
const ocrStatus = ref('')
const uploadError = ref('')
const imagePreview = ref('')
const imageExtracted = ref({})
const ocrRawText = ref('')
const formError = ref('')
const submitted = ref(false)
const submittedForm = ref({})

const currentQuestion = computed(() => questions[currentIndex.value])
const progress = computed(() =>
  completed.value
    ? 100
    : (currentIndex.value / questions.length) * 100
)

// ---------- 6. UPLOAD ẢNH + OCR ----------
// Nhận ảnh → Tesseract.js đọc chữ → gọi /api/extract →
// lấy Họ tên, Năm sinh, CCCD và Địa chỉ.
async function handleImageUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return

  uploadError.value = ''

  if (!file.type.startsWith('image/')) {
    uploadError.value = 'Tệp bác chọn chưa phải là hình ảnh. Bác chọn lại giúp cháu ảnh CCCD hoặc giấy tờ nhé.'
    event.target.value = ''
    return
  }

  imagePreview.value = URL.createObjectURL(file)
  imageExtracted.value = {}
  ocrRawText.value = ''
  ocrLoading.value = true
  ocrStatus.value = 'Đang chuẩn bị hình ảnh...'

  let worker = null

  try {
    // Tăng kích thước + chuyển grayscale để OCR đọc ảnh chữ rõ hơn.
    const processedImage = await preprocessImage(file)

    worker = await createWorker('vie+eng', 1, {
      logger: message => {
        if (message.status === 'recognizing text' && typeof message.progress === 'number') {
          ocrStatus.value = `Đang đọc chữ trong ảnh: ${Math.round(message.progress * 100)}%`
        } else if (message.status) {
          ocrStatus.value = message.status
        }
      }
    })

    const { data } = await worker.recognize(processedImage)
    ocrRawText.value = data.text || ''

    if (!ocrRawText.value.trim()) {
      throw new Error('Không đọc được chữ trong hình ảnh.')
    }

    ocrStatus.value = 'Đã đọc ảnh. Đang nhận diện Họ tên, năm sinh, CCCD và địa chỉ...'

    // Trích xuất trực tiếp từ OCR trước, không phụ thuộc hoàn toàn vào API.
    const localFields = extractDocumentFields(ocrRawText.value)

    // Gọi backend để có thêm lớp NLP; kết quả backend sẽ được ưu tiên.
    let serverFields = {}
    try {
      const response = await fetch(`${API_URL}/api/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: ocrRawText.value })
      })

      if (response.ok) {
        const result = await response.json()
        serverFields = result.fields || {}
      }
    } catch (apiError) {
      console.warn('Backend extract unavailable; using local OCR parser.', apiError)
    }

    const extracted = {
      ...localFields,
      ...serverFields
    }

    // Chuẩn hóa lại CCCD để luôn đúng 12 chữ số.
    if (extracted.id_number) {
      const digits = String(extracted.id_number).replace(/\D/g, '')
      extracted.id_number = digits.length === 12 ? digits : null
    }

    // Chuẩn hóa năm sinh thành số.
    if (extracted.birth_year) {
      const year = Number(extracted.birth_year)
      extracted.birth_year = year >= 1900 && year <= new Date().getFullYear() ? year : null
    }

    imageExtracted.value = Object.fromEntries(
      Object.entries(extracted).filter(([, value]) => value !== null && value !== undefined && String(value).trim() !== '')
    )

    const count = Object.keys(imageExtracted.value).length
    ocrStatus.value = count === 4
      ? '✓ Đã nhận diện đủ 4 thông tin.'
      : `✓ Đã nhận diện ${count}/4 thông tin. Bác kiểm tra và bổ sung phần còn thiếu.`
  } catch (error) {
    console.error(error)
    ocrStatus.value = ''
    uploadError.value = 'Cháu chưa đọc được hình ảnh này. Bác thử chụp lại ảnh rõ nét, đủ sáng và thẳng giấy tờ nhé.'
  } finally {
    if (worker) await worker.terminate()
    ocrLoading.value = false
  }
}

async function preprocessImage(file) {
  const sourceUrl = URL.createObjectURL(file)

  try {
    const image = await new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = reject
      img.src = sourceUrl
    })

    const scale = 2.5
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(image.naturalWidth * scale)
    canvas.height = Math.round(image.naturalHeight * scale)

    const ctx = canvas.getContext('2d', { willReadFrequently: true })
    ctx.drawImage(image, 0, 0, canvas.width, canvas.height)

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    const pixels = imageData.data

    // Grayscale + contrast. Giữ ngưỡng vừa phải để không làm mất dấu tiếng Việt.
    for (let i = 0; i < pixels.length; i += 4) {
      const gray = Math.round(
        0.299 * pixels[i] +
        0.587 * pixels[i + 1] +
        0.114 * pixels[i + 2]
      )
      const contrast = Math.max(0, Math.min(255, (gray - 128) * 1.35 + 128))
      pixels[i] = contrast
      pixels[i + 1] = contrast
      pixels[i + 2] = contrast
    }

    ctx.putImageData(imageData, 0, 0)

    return await new Promise((resolve, reject) => {
      canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error('Không tạo được ảnh OCR')), 'image/png')
    })
  } finally {
    URL.revokeObjectURL(sourceUrl)
  }
}

function cleanOcrValue(value) {
  return value
    .replace(/\s+/g, ' ')
    .replace(/^[\s:;,.\-]+|[\s:;,.\-]+$/g, '')
    .trim()
}

function extractDocumentFields(text) {
  const fields = {}
  const normalized = text.replace(/\r/g, '').replace(/[|]/g, ':')

  // CCCD: "SCCCD: 237300140015", "CCCD - 237300140015"
  const idLabel = normalized.match(
    /(?:SCCCD|CCCD|SỐ\s*CCCD|SỐ\s*CĂN\s*CƯỚC)\s*[:\-]?\s*((?:\d[\s-]*){12})(?!\d)/iu
  )
  if (idLabel) {
    const digits = idLabel[1].replace(/\D/g, '')
    if (digits.length === 12) fields.id_number = digits
  }

  if (!fields.id_number) {
    const standaloneId = normalized.match(/(?<!\d)\d{12}(?!\d)/)
    if (standaloneId) fields.id_number = standaloneId[0]
  }

  // Năm sinh: "Năm sinh: 2000" / OCR không dấu "Nam sinh: 2000"
  const yearMatch = normalized.match(
    /(?:NĂM\s*SINH|NAM\s*SINH|SINH\s*NĂM|SINH)\s*[:\-]?\s*(19\d{2}|20\d{2})\b/iu
  )
  if (yearMatch) fields.birth_year = Number(yearMatch[1])

  if (!fields.birth_year) {
    const anyYear = normalized.match(/\b((?:19|20)\d{2})\b/)
    if (anyYear) fields.birth_year = Number(anyYear[1])
  }

  // Họ tên: label-based để không phụ thuộc câu nói của người dùng.
  const nameMatch = normalized.match(
    /(?:HỌ\s*TÊN|HỌ\s*VÀ\s*TÊN|HO\s*TEN|HO\s*VA\s*TEN)\s*[:\-]?\s*([^\n]+)/iu
  )
  if (nameMatch) {
    const name = cleanOcrValue(nameMatch[1])
      .replace(/\s+(?:NĂM\s*SINH|NAM\s*SINH|ĐỊA\s*CHỈ|DIA\s*CHI|SCCCD|CCCD)\s*[:\-]?.*$/iu, '')
    if (name.split(/\s+/).length >= 2) fields.name = name
  }

  // Địa chỉ: lấy toàn bộ phần sau label trên cùng một dòng.
  const addressMatch = normalized.match(
    /(?:ĐỊA\s*CHỈ|DIA\s*CHI)\s*[:\-]?\s*([^\n]+)/iu
  )
  if (addressMatch) {
    const address = cleanOcrValue(addressMatch[1])
      .replace(/\s+(?:SCCCD|CCCD|HỌ\s*TÊN|HỌ\s*VÀ\s*TÊN|NĂM\s*SINH|NAM\s*SINH)\s*[:\-]?.*$/iu, '')
    if (address.length >= 5) fields.address = address
  }

  return fields
}

function sanitizeFormField(field) {
  formError.value = ''

  if (field === 'id_number') {
    form.value.id_number = String(form.value.id_number || '').replace(/\D/g, '').slice(0, 12)
  }

  if (field === 'birth_year') {
    const value = String(form.value.birth_year || '').replace(/\D/g, '').slice(0, 4)
    form.value.birth_year = value
  }
}

function validateForm() {
  const name = String(form.value.name || '').trim()
  const year = Number(form.value.birth_year)
  const idNumber = String(form.value.id_number || '').replace(/\D/g, '')
  const address = String(form.value.address || '').trim()
  const currentYear = new Date().getFullYear()

  if (!name) {
    formError.value = 'Vui lòng nhập Họ và tên.'
    return false
  }

  if (!/^\d{4}$/.test(String(form.value.birth_year || '')) || year < 1900 || year > currentYear) {
    formError.value = `Năm sinh phải có 4 chữ số và nằm trong khoảng 1900-${currentYear}.`
    return false
  }

  if (!/^\d{12}$/.test(idNumber)) {
    formError.value = 'Số căn cước công dân phải gồm đúng 12 chữ số.'
    return false
  }

  if (!address) {
    formError.value = 'Vui lòng nhập Địa chỉ.'
    return false
  }

  form.value.id_number = idNumber
  form.value.name = name
  form.value.address = address
  formError.value = ''
  return true
}

// ---------- 7. ĐƯA KẾT QUẢ OCR VÀO FORM ----------
// Sau OCR, dữ liệu được đưa vào form để người dùng kiểm tra
// và chỉnh sửa trước khi xác nhận.
function startWithImageData() {
  const extracted = imageExtracted.value

  form.value = {
    ...form.value,
    ...extracted
  }

  started.value = true
  currentIndex.value = 0
  completed.value = false

  messages.value = [{
    role: 'bot',
    text: 'Cháu đã đọc thông tin từ hình ảnh. Cháu sẽ kiểm tra từng mục để bác xác nhận lại nhé.'
  }]

  const firstMissingIndex = questions.findIndex(
    question => !form.value[question.field]
  )

  if (firstMissingIndex === -1) {
    completed.value = true
    messages.value.push({
      role: 'bot',
      text: 'Dạ, cháu đã nhận đủ thông tin từ hình ảnh. Bác kiểm tra hồ sơ bên dưới nhé.'
    })
  } else {
    currentIndex.value = firstMissingIndex
    messages.value.push({
      role: 'bot',
      text: `Cháu đã nhận diện được một số thông tin. ${questions[firstMissingIndex].question}`
    })
    setTimeout(() => speak(questions[firstMissingIndex].question), 200)
  }

  scrollChat()
}

// ---------- 8. BẮT ĐẦU / RESET HỒ SƠ ----------
// Mở quy trình khai hồ sơ và reset các trạng thái cần thiết.
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

function goBack() {
  if (currentIndex.value === 0 || completed.value) return

  currentIndex.value--
  const field = questions[currentIndex.value].field
  input.value = form.value[field] != null ? String(form.value[field]) : ''

  messages.value.push({
    role: 'bot',
    text: `Dạ, bác muốn sửa lại câu này: ${questions[currentIndex.value].question}`
  })

  setTimeout(() => speak(questions[currentIndex.value].question), 200)
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
    messages.value.push({
      role: 'bot',
      text: 'Trình duyệt này chưa hỗ trợ nhập bằng giọng nói. Bác gõ câu trả lời vào ô bên dưới giúp cháu nhé.'
    })
    scrollChat()
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

// ---------- 12. HÀM TIỆN ÍCH: TEXT-TO-SPEECH ----------
// Gọi backend TTS để đọc câu hỏi bằng tiếng Việt.
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
      messages.value.push({
        role: 'bot',
        text: 'Cháu không phát được giọng đọc lúc này. Bác đọc câu hỏi trên màn hình giúp cháu nhé.'
      })
      scrollChat()
    }

    await currentAudio.play()
  } catch (error) {
    console.error(error)
    isSpeaking.value = false

    messages.value.push({
      role: 'bot',
      text: 'Cháu không kết nối được hệ thống đọc giọng nói. Bác đọc câu hỏi trên màn hình hoặc bấm ☎ Gọi hỗ trợ giúp cháu nhé.'
    })
    scrollChat()
  }
}

function reset() {
  formError.value = ''
  submitted.value = false
  submittedForm.value = {}
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
  imagePreview.value = ''
  imageExtracted.value = {}
  ocrRawText.value = ''
  ocrStatus.value = ''
  uploadError.value = ''
}

function confirm() {
  if (!validateForm()) return

  // Lưu một bản sao tại thời điểm xác nhận để trang hồ sơ đã nộp không thể chỉnh sửa.
  submittedForm.value = { ...form.value }

  // Chuyển sang trang hồ sơ đã nộp; trang đó tự hiển thị xác nhận thành công,
  // không cần alert() chặn luồng thao tác.
  submitted.value = true
  completed.value = true
}

// ---------- 11. HÀM TIỆN ÍCH: SCROLL ----------
function scrollChat() {
  nextTick(() => {
    if (chatWindow.value) {
      chatWindow.value.scrollTop = chatWindow.value.scrollHeight
    }
  })
}
</script>
