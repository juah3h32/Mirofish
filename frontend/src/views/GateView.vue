<template>
  <div class="gate">
    <div class="gate-card">
      <div class="gate-logo">
        <svg viewBox="0 0 20 20" width="32" height="32"><polygon points="10,0 20,10 10,20 0,10" fill="#2A5A1A"/></svg>
        <span class="gate-brand">MIROFISH</span>
      </div>
      <p class="gate-label">Ingresa la clave de acceso</p>
      <form @submit.prevent="submit">
        <div class="gate-input-wrap" :class="{ 'gate-input-wrap--error': error }">
          <input
            ref="inputRef"
            v-model="key"
            :type="showKey ? 'text' : 'password'"
            placeholder="••••••"
            autocomplete="off"
            class="gate-input"
            maxlength="20"
          />
          <button type="button" class="gate-eye" @click="showKey = !showKey" tabindex="-1">
            <svg v-if="!showKey" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
              <line x1="1" y1="1" x2="23" y2="23"/>
            </svg>
          </button>
        </div>
        <p class="gate-error" v-if="error">Clave incorrecta. Inténtalo de nuevo.</p>
        <button type="submit" class="gate-submit" :disabled="!key">
          Entrar
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const key = ref('')
const error = ref(false)
const showKey = ref(false)
const inputRef = ref(null)

const ACCESS_KEY = '171215'
const STORAGE_KEY = 'mf_access'

onMounted(() => {
  inputRef.value?.focus()
})

const submit = () => {
  if (key.value === ACCESS_KEY) {
    sessionStorage.setItem(STORAGE_KEY, '1')
    const redirect = route.query.redirect || '/'
    router.replace(redirect)
  } else {
    error.value = true
    key.value = ''
    setTimeout(() => { error.value = false }, 2000)
  }
}
</script>

<style scoped>
.gate {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #111114;
}

.gate-card {
  background: #1A1A1E;
  border: 1px solid #2C2C32;
  border-radius: 14px;
  padding: 48px 44px;
  width: 340px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

.gate-logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.gate-brand {
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.2em;
  color: #CCC;
  font-family: -apple-system, sans-serif;
}

.gate-label {
  margin: 0;
  font-size: 13px;
  color: #888;
  font-family: -apple-system, sans-serif;
  text-align: center;
}

form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.gate-input-wrap {
  display: flex;
  align-items: center;
  background: #111;
  border: 1px solid #333;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.15s;
}

.gate-input-wrap:focus-within {
  border-color: #2A5A1A;
}

.gate-input-wrap--error {
  border-color: #8B2C14 !important;
  animation: shake 0.3s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-6px); }
  75% { transform: translateX(6px); }
}

.gate-input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 12px 14px;
  font-size: 18px;
  color: #EEE;
  letter-spacing: 0.15em;
  font-family: -apple-system, monospace;
  outline: none;
}

.gate-input::placeholder {
  color: #444;
  letter-spacing: 0.1em;
}

.gate-eye {
  background: transparent;
  border: none;
  padding: 0 12px;
  cursor: pointer;
  color: #555;
  display: flex;
  align-items: center;
}
.gate-eye:hover { color: #888; }

.gate-error {
  margin: 0;
  font-size: 11px;
  color: #C0392B;
  text-align: center;
  font-family: -apple-system, sans-serif;
  min-height: 16px;
}

.gate-submit {
  background: #1C3B1A;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.04em;
  cursor: pointer;
  font-family: -apple-system, sans-serif;
  transition: background 0.15s;
}
.gate-submit:hover:not(:disabled) { background: #2A5A1A; }
.gate-submit:disabled { opacity: 0.35; cursor: not-allowed; }
</style>
