(() => {
  const story = document.querySelector('[data-story]')
  const caps = [...document.querySelectorAll('[data-cap]')]
  const stepButtons = [...document.querySelectorAll('[data-goto]')]
  const count = document.querySelector('[data-count]')
  const bar = document.querySelector('[data-bar]')

  // 每个阶段在叙事区滚动进度中的起点
  const STAGE_STARTS = [0, 0.14, 0.34, 0.56, 0.78]
  const BASE_COUNT = 127
  let stage = -1

  function progress() {
    const rect = story.getBoundingClientRect()
    const travel = story.offsetHeight - window.innerHeight
    return travel > 0 ? Math.min(1, Math.max(0, -rect.top / travel)) : 0
  }

  function setStage(next) {
    if (next === stage) return
    const previous = stage
    stage = next
    for (let i = 1; i < STAGE_STARTS.length; i++) story.classList.toggle(`r${i}`, stage >= i)
    caps.forEach((cap, i) => {
      cap.classList.toggle('is-on', i === stage)
      cap.classList.toggle('is-past', i < stage)
      cap.setAttribute('aria-hidden', i === stage ? 'false' : 'true')
    })
    stepButtons.forEach((button) => {
      const target = Number(button.dataset.goto)
      button.classList.toggle('is-reached', target <= stage)
      button.classList.toggle('is-current', target === stage)
    })
    const finished = stage >= 4
    const value = String(BASE_COUNT + (finished ? 1 : 0))
    if (count.textContent !== value) {
      count.textContent = value
      if (finished && previous !== -1) {
        count.classList.remove('is-bump')
        void count.offsetWidth
        count.classList.add('is-bump')
      }
    }
  }

  function update() {
    const p = progress()
    let next = 0
    STAGE_STARTS.forEach((start, i) => { if (p >= start) next = i })
    setStage(next)
    bar.classList.toggle('is-solid', window.scrollY > story.offsetHeight - window.innerHeight * 1.2)
  }

  let queued = false
  window.addEventListener('scroll', () => {
    if (queued) return
    queued = true
    requestAnimationFrame(() => { queued = false; update() })
  }, { passive: true })
  window.addEventListener('resize', update)
  update()

  stepButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const i = Number(button.dataset.goto)
      const travel = story.offsetHeight - window.innerHeight
      const start = STAGE_STARTS[i]
      const end = STAGE_STARTS[i + 1] ?? 1
      window.scrollTo({ top: story.offsetTop + travel * (start + (end - start) * 0.35) })
    })
  })

  // 小程序码未放入时，显示品牌标志作为占位
  const qr = document.querySelector('[data-qr]')
  const qrImg = document.querySelector('[data-qr-img]')
  const markMissing = () => {
    qr.classList.add('is-missing')
    qr.querySelector('.qr__cap').textContent = '微信小程序 · 语境自修'
  }
  if (qrImg.complete && qrImg.naturalWidth === 0) markMissing()
  qrImg.addEventListener('error', markMissing)

  // 复制小程序名称
  const toast = document.querySelector('[data-toast]')
  document.querySelectorAll('[data-copy]').forEach((button) => {
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(button.dataset.copy)
        toast.textContent = '已复制「语境自修」，打开微信搜索即可。'
      } catch {
        toast.textContent = '复制没有成功，请在微信中手动搜索「语境自修」。'
      }
    })
  })
})()
